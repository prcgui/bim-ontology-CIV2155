"""Exporta as interfaces e recortes locais para RDF; preserva o grafo v05.
Geometria GEOM: Zhang et al. (2018), DOI 10.3233/SW-180297.
RDFLib: https://rdflib.readthedocs.io/en/stable/intro_to_graphs/.
Vocabulário experimental deste estudo; nenhuma adjacência BOT é certificada.
"""
from pathlib import Path
from decimal import Decimal
import json,hashlib,csv,html
from collections import Counter
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,XSD
H=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/interfaces-hibridas#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/interfaces-hibridas-v01/')
OLD=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/ifc2sb-python-v01/')
K=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/krijnen-piloto#')
GEOM=Namespace('http://bimsparql.org/geometry#');PROV=Namespace('http://www.w3.org/ns/prov#')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def decimal(x):return Literal(Decimal(str(x)))

def run(result_path,rdf_base,out):
    result_path=Path(result_path);rdf_base=Path(rdf_base);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    d=json.loads(result_path.read_text(encoding='utf8'));assert d['ifc_original_preservado']
    base_hash=sha(rdf_base);g=Graph().parse(rdf_base,format='turtle');before=set(g)
    for prefix,ns in [('hiv',H),('hid',B),('geom',GEOM),('prov',PROV)]:g.bind(prefix,ns)
    room=OLD[d['ambiente']];activity=B['execucao'];frame=B['referencial-projeto-metros']
    g.add((activity,RDF.type,PROV.Activity));g.add((activity,H.sha256Resultado,Literal(sha(result_path))))
    for uri in ['https://doi.org/10.3390/buildings13020350','https://doi.org/10.26868/25222708.2021.30156','https://doi.org/10.46421/2706-6568.37.2020.paper008']:
        g.add((activity,PROV.wasDerivedFrom,URIRef(uri)))
    g.add((activity,RDFS.comment,Literal('Adaptação experimental: interfaces do IfcSpace, projeção/interseção Shapely e sondas; recortes derivados do IFC2SB; sinais CGAL globais preservados. Validação arquitetônica independente pendente.',lang='pt')))
    g.add((activity,H.sha256IFC,Literal(d['sha256_ifc'])))
    g.add((frame,RDFS.label,Literal('Referencial cartesiano do projeto IFC; coordenadas em metros; não CRS84.',lang='pt')))
    for cls,description in [('InterfaceGeometricaCandidata','Trecho de contato geométrico com o ambiente, qualificado somente no critério experimental.'),('RecorteLocalDeAbertura','Parte da superfície de abertura recortada na interface do ambiente.'),('AvaliacaoDeAbertura','Registro da avaliação, inclusive quando não houve associação pelo critério.')]:
        g.add((H[cls],RDF.type,RDFS.Class));g.add((H[cls],RDFS.comment,Literal(description,lang='pt')))
    def geom(node,wkt):
        g.add((node,GEOM.asBody,Literal(wkt)));g.add((node,H.coordinateReference,frame))
        g.add((node,H.unit,URIRef('http://qudt.org/vocab/unit/M')))
    cgal_by_wall={}
    for node in list(g.subjects(RDF.type,K.AvaliacaoGeometrica)):
        wall=g.value(node,K.paredeExaminada)
        cgal_by_wall.setdefault(wall,[]).append(node)
    for i in d['interfaces']:
        node=B[i['id']];wall=OLD[i['parede']]
        g.add((room,H.interfaceCandidata,node));g.add((node,RDF.type,H.InterfaceGeometricaCandidata))
        g.add((node,RDFS.label,Literal(i['id'])));g.add((node,H.paredeHospedeira,wall))
        g.add((node,H.areaBrutaM2,decimal(i['area_m2'])));g.add((node,H.distanciaPlanosM,decimal(i['distancia_planos_m'])))
        g.add((node,H.faceFonteParede,Literal(i['face_parede'])));g.add((node,H.faceFonteAmbiente,Literal(i['face_ambiente'])))
        g.add((node,H.qualificadaNoCriterio,Literal(i['qualificada_no_criterio'])))
        g.add((node,H.validacaoArquitetonica,Literal('pendente')));g.add((node,PROV.wasGeneratedBy,activity))
        g.add((node,H.sinalGlobalCGAL,Literal(i['sinal_global_cgal'])))
        g.add((node,H.sondaPositiva,Literal(i['sondas']['sonda_positiva'])));g.add((node,H.sondaNegativa,Literal(i['sondas']['sonda_negativa'])))
        g.add((node,H.sensibilidadeSondasEstavel,Literal(i['sensibilidade_sondas']['estavel'])))
        for s in cgal_by_wall.get(wall,[]):g.add((node,H.avaliacaoCGALDoHospedeiro,s))
        geom(node,i['wkt'])
    for p in d['recortes_aberturas']:
        node=B[p['id']];opening=OLD[p['abertura']];fill=OLD[p['preenchimento']]
        g.add((B[p['interface']],H.recorteAbertura,node));g.add((node,RDF.type,H.RecorteLocalDeAbertura))
        g.add((node,H.abertura,opening));g.add((node,H.preenchimento,fill))
        g.add((node,H.paredeHospedeira,OLD[p['parede']]))
        g.add((node,H.areaRecorteM2,decimal(p['area_recorte_m2'])))
        g.add((node,H.relacaoIfcVoidsGlobalId,Literal(p['relacao_voids'])));g.add((node,H.relacaoIfcFillsGlobalId,Literal(p['relacao_fills'])))
        for source in p['recortes_ifc2sb']:g.add((node,H.recorteFonteIFC2SB,Literal(source)))
        g.add((node,H.qualificadaNoCriterio,Literal(p['qualificada_no_criterio'])))
        g.add((node,PROV.wasGeneratedBy,activity));g.add((node,H.validacaoArquitetonica,Literal('pendente')))
        g.add((fill,H.classeIFC,Literal(p['classe_preenchimento'])));g.add((fill,RDFS.label,Literal(p['nome_preenchimento'] or p['preenchimento'])))
        geom(node,p['wkt'])
    for r in d['avaliacao_aberturas']:
        node=B['avaliacao/'+r['abertura']];g.add((node,RDF.type,H.AvaliacaoDeAbertura))
        g.add((node,H.ambienteExaminado,room));g.add((node,H.abertura,OLD[r['abertura']]))
        g.add((node,H.estado,Literal(r['estado'])));g.add((node,H.recortesEncontrados,Literal(r['recortes_na_interface'])))
        g.add((node,PROV.wasGeneratedBy,activity))
    assert before.issubset(set(g)) and sha(rdf_base)==base_hash
    BOT=Namespace('https://w3id.org/bot#');assert not any(p in [BOT.adjacentElement,BOT.intersectingElement] for s,p,o in set(g)-before)
    target=out/'Cozinha_Interfaces_Hibridas_IFC2SB_Krijnen_Kiavarz_v01.ttl';g.serialize(target,format='turtle')
    restored=Graph().parse(target,format='turtle');assert set(restored)==set(g)
    query='''PREFIX hiv: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/interfaces-hibridas#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?ambiente ?interface ?parede ?qualificada ?recorte ?abertura ?preenchimento ?nome ?classe WHERE {
 ?ambiente hiv:interfaceCandidata ?interface .
 ?interface hiv:paredeHospedeira ?parede; hiv:qualificadaNoCriterio ?qualificada .
 OPTIONAL { ?interface hiv:recorteAbertura ?recorte .
  ?recorte hiv:abertura ?abertura; hiv:preenchimento ?preenchimento .
  ?preenchimento hiv:classeIFC ?classe . OPTIONAL {?preenchimento rdfs:label ?nome}
 }
} ORDER BY ?interface ?recorte'''
    (out/'Consultar_Cozinha_Interfaces_Aberturas.rq').write_text(query,encoding='utf8')
    rows=list(restored.query(query));interfaces=set(restored.objects(room,H.interfaceCandidata))
    recortes=set(restored.subjects(RDF.type,H.RecorteLocalDeAbertura))
    assert len(interfaces)==len(d['interfaces']) and len(recortes)==len(d['recortes_aberturas'])
    assert len(set(restored.subjects(RDF.type,H.AvaliacaoDeAbertura)))==24
    with (out/'Consulta_Cozinha_Interfaces_Aberturas.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        wr=csv.writer(fp);wr.writerow([str(v) for v in rows[0].labels] if rows else []);wr.writerows([[str(v) if v is not None else '' for v in row] for row in rows])
    summary={'triplas_entrada':len(before),'triplas_saida':len(g),'interfaces':len(interfaces),
      'interfaces_qualificadas':sum(i['qualificada_no_criterio'] for i in d['interfaces']),
      'recortes_aberturas':len(recortes),'aberturas_associadas':len({p['abertura'] for p in d['recortes_aberturas']}),
      'classes_dos_10_preenchimentos':dict(Counter({p['preenchimento']:p['classe_preenchimento'] for p in d['recortes_aberturas']}.values())),
      'avaliacoes_aberturas':24,'linhas_consulta':len(rows),'sha256_rdf_entrada':base_hash,'sha256_rdf_saida':sha(target),
      'roundtrip_e_preservacao':True,'novas_adjacencias_bot_certificadas':0,
      'limite':'Relações qualificadas geometricamente no recorte; significado e completude arquitetônica permanecem sem validação independente.'}
    (out/'Registro_RDF_Hibrido_v01.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2));return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resultado');p.add_argument('rdf_base');p.add_argument('saida');a=p.parse_args();run(a.resultado,a.rdf_base,a.saida)
