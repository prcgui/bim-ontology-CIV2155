"""Registra no RDF as evidências geométricas do piloto, sem afirmar uso espacial.
Padrão geométrico: Zhang et al. (2018), BimSPARQL, DOI 10.3233/SW-180297.
Navegação: RDFLib, https://rdflib.readthedocs.io/en/stable/intro_to_graphs/.
Vocabulário CIV deste ensaio; não equivale a ontologia arquitetônica validada.
"""
from pathlib import Path
import json,csv,hashlib
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,XSD
C=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/ifc2sb-python#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/ifc2sb-python-v01/')
G=Namespace('http://bimsparql.org/geometry#');P=Namespace('http://www.w3.org/ns/prov#')
def exportar(result_path,out):
    result_path=Path(result_path);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    d=json.loads(result_path.read_text(encoding='utf8'));g=Graph()
    for prefix,ns in [('civ',C),('inst',B),('geom',G),('prov',P)]:g.bind(prefix,ns)
    source=B['fonte-ifc'];run=B['execucao'];room=B[d['ambiente']];frame=B['referencial-projeto-metros']
    g.add((source,C.sha256,Literal(d['sha256_IFC'])))
    g.add((run,RDF.type,P.Activity));g.add((run,P.used,source));g.add((run,P.wasDerivedFrom,URIRef('https://doi.org/10.26868/25222708.2021.30156')))
    g.add((run,RDFS.comment,Literal('Adaptação parcial e extensão ambiente-face. Evidências geométricas; validação arquitetônica independente não realizada.',lang='pt')))
    g.add((room,RDF.type,C.AmbienteIFC));g.add((room,C.globalId,Literal(d['ambiente'])));g.add((room,RDFS.label,Literal(d['nome'])))
    g.add((frame,RDFS.label,Literal('Referencial cartesiano do projeto IFC; coordenadas em metros. Não georreferenciado como CRS84.',lang='pt')))
    def geometry(node,wkt,area=None):
        g.add((node,G.asBody,Literal(wkt)));g.add((node,C.coordinateReference,frame));g.add((node,C.unit,URIRef('http://qudt.org/vocab/unit/M')))
        if area is not None:g.add((node,C.areaM2,Literal(area)))
        g.add((node,P.wasGeneratedBy,run))
    geometry(room,d['wkt_ambiente'])
    g.add((room,C.volumeM3,Literal(d['volume_ambiente_m3'])))
    g.add((room,C.validacaoArquitetonica,Literal('não realizada')))
    indices={}
    for wall in d['paredes']:
        wu=B[wall['parede']];g.add((wu,RDF.type,C.ParedeIFC));g.add((wu,C.globalId,Literal(wall['parede'])));g.add((wu,RDFS.label,Literal(wall['nome'] or wall['parede'])))
        evaluation=B['intersecao-parede/'+wall['parede']]
        g.add((evaluation,C.ambienteExaminado,room));g.add((evaluation,C.paredeExaminada,wu))
        g.add((evaluation,C.volumeIntersecaoM3,Literal(wall['volume_intersecao_ambiente_parede_m3'])))
        for s in wall['superficies_brutas_coincidentes']:
            key=(wall['parede'],s['original_face_index'],s['face_ambiente'])
            u=B['face/'+wall['parede']+'/'+str(s['original_face_index'])+'/'+str(s['face_ambiente'])];indices[key]=u
            g.add((room,C.temSuperficieCandidata,u));g.add((u,RDF.type,C.SuperficieBrutaCandidata));g.add((u,C.faceDeElemento,wu))
            g.add((u,C.originalFaceIndex,Literal(s['original_face_index'])));g.add((u,C.validacaoArquitetonica,Literal('não realizada')))
            if 'wkt' in s:geometry(u,s['wkt'],s['area_m2'])
    estados={r['abertura']:r for r in d['aberturas']}
    for row in d['aberturas']:
        wu=B[row['parede']];op=B[row['abertura']];fill=B[row['preenchimento']]
        g.add((wu,C.possuiAberturaDeclaradaIFC,op));g.add((op,C.possuiPreenchimentoDeclaradoIFC,fill))
        g.add((op,C.globalId,Literal(row['abertura'])));g.add((fill,C.globalId,Literal(row['preenchimento'])))
        g.add((fill,RDFS.label,Literal(row['nome_preenchimento'] or row['preenchimento'])));g.add((fill,C.classeIFC,Literal(row['classe_preenchimento'])))
        assessment=B['avaliacao/'+row['abertura']];g.add((assessment,C.ambienteExaminado,room));g.add((assessment,C.aberturaExaminada,op))
        g.add((assessment,C.estado,Literal(row['estado'])));g.add((assessment,C.areaCoincidenteM2,Literal(row['area_coincidente_cozinha_m2'])))
    recs=0
    for patch in d['faces_recortadas']:
        for s in patch['contatos']:
            parent=indices.get((patch['parede'],patch['original_face_index'],s['face_ambiente']))
            if parent is None:raise ValueError('Recorte sem superfície ancestral candidata')
            u=B['recorte/'+patch['codigo']+'/'+str(s['face_ambiente'])]
            g.add((parent,C.temRecorteGeometricoDeAbertura,u));g.add((u,RDF.type,C.RecorteGeometricoCandidato))
            g.add((u,C.recorteDeAbertura,B[patch['abertura']]))
            g.add((u,C.estado,Literal(estados[patch['abertura']]['estado'])))
            if 'wkt' in s:geometry(u,s['wkt'],s['area_m2'])
            recs+=1
    # Não usa bot:containsElement ou bot:adjacentElement para promover candidatos.
    target=out/'Cozinha_Superficies_Candidatas_IFC2SB_Python.ttl';g.serialize(destination=str(target),format='turtle')
    query='''PREFIX civ: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/ifc2sb-python#>
PREFIX geom: <http://bimsparql.org/geometry#>
SELECT DISTINCT ?ambiente ?superficie ?parede ?abertura ?preenchimento ?estado ?coordenadas
WHERE {
 ?ambiente civ:temSuperficieCandidata ?superficie .
 ?superficie civ:faceDeElemento ?parede ; civ:temRecorteGeometricoDeAbertura ?recorte .
 ?recorte civ:recorteDeAbertura ?abertura ; civ:estado ?estado ; geom:asBody ?coordenadas .
 ?abertura civ:possuiPreenchimentoDeclaradoIFC ?preenchimento .
}'''
    (out/'Consulta_Ambiente_Superficie_Abertura.rq').write_text(query,encoding='utf8')
    values=list(g.query(query));guids={str(r.abertura).rsplit('/',1)[-1] for r in values}
    expected={r['abertura'] for r in d['aberturas'] if r['area_coincidente_cozinha_m2']>1e-8}
    assert guids==expected,{'RDF':guids,'JSON':expected}
    negative={r['abertura'] for r in d['aberturas'] if r['estado']=='fora_do_ambiente_por_separacao_bbox'}
    assert not negative&guids
    with (out/'Consulta_Recortes.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow([str(v) for v in g.query(query).vars]);w.writerows([[str(v) for v in r] for r in values])
    info={'triplas':len(g),'superficies_candidatas':len(indices),'recortes_coincidentes':recs,'aberturas_com_recortes':len(guids),
      'aberturas_separadas_sem_cadeia':len(negative),'consulta_linhas':len(values),'sha256_RDF':hashlib.sha256(target.read_bytes()).hexdigest(),
      'limite':'Grafo de evidências candidatas; não é atribuição arquitetônica validada. Relações declaradas IFC são distintas das superfícies calculadas.'}
    (out/'Registro_RDF.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8');print(info);return info
if __name__=='__main__':
    import sys
    exportar(sys.argv[1],sys.argv[2])
