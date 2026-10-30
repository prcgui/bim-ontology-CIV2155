"""Extensão RDF do estudo: evidências alternativas, sem certificar adjacências.

Fonte geométrica: Lilis et al. (2026), DOI 10.1016/j.autcon.2026.106840.
Serialização GEOM: Zhang et al. (2018), DOI 10.3233/SW-180297.
RDFLib: https://rdflib.readthedocs.io/en/stable/intro_to_graphs/.
"""
from pathlib import Path
from decimal import Decimal
import json, hashlib, csv
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

L=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/lilis-piloto#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/lilis-piloto-v01/')
OLD=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/ifc2sb-python-v01/')
HI=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/interfaces-hibridas-v01/')
P=Namespace('http://www.w3.org/ns/prov#')
G=Namespace('http://bimsparql.org/geometry#')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def number(v):return Literal(Decimal(str(v)))

def run(result_path,base_rdf,out):
    result_path=Path(result_path);base_rdf=Path(base_rdf);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    d=json.loads(result_path.read_text(encoding='utf8'))
    assert d['ifc_original_preservado']
    base_sha=sha(base_rdf);g=Graph().parse(base_rdf,format='turtle');before=set(g)
    for prefix,ns in [('lil',L),('lid',B),('prov',P),('geom',G)]:g.bind(prefix,ns)
    activity=B['ensaio'];frame=B['referencial-projeto-metros'];room=OLD[d['ambiente']]
    g.add((activity,RDF.type,P.Activity));g.add((activity,P.wasDerivedFrom,URIRef(d['fonte'])))
    g.add((activity,L.sha256IFC,Literal(d['sha256_ifc'])))
    g.add((activity,L.sha256Resultado,Literal(sha(result_path))))
    g.add((activity,L.sha256RDFBase,Literal(base_sha)))
    g.add((activity,L.distanciaPrincipalM,number(d['parametros']['d_principal_m'])))
    g.add((activity,L.alphaWrapExecutado,Literal(False)))
    g.add((activity,RDFS.comment,Literal('Adaptação parcial de operadores; associação à parede, RDF e conferência Common 3D são extensões do estudo. Não equivale ao método completo nem à validação arquitetônica.',lang='pt')))
    g.add((frame,RDFS.label,Literal('Referencial cartesiano do projeto IFC em metros; não CRS84.',lang='pt')))
    for cls,description in [
        ('RecorteCandidato','Projeção de abertura sobre uma interface; não certifica uma relação arquitetônica.'),
        ('BalancoDeArea','Área bruta, união dos recortes e resíduo; alternativas não são somáveis entre si.'),
        ('ParEntreEspacosCandidato','Par projetado entre cozinha e outro espaço, sem validação arquitetônica independente.'),
        ('ResiduoSemClassificacaoExterna','Resíduo geométrico; alpha wrap e classificação externa não executados.')]:
        g.add((L[cls],RDF.type,RDFS.Class));g.add((L[cls],RDFS.comment,Literal(description,lang='pt')))
    def geometry(node,wkt):
        g.add((node,G.asBody,Literal(wkt)));g.add((node,L.referencial,frame))
        g.add((node,L.unidade,URIRef('http://qudt.org/vocab/unit/M')))
    for r in d['recortes_hibridos']:
        node=B['recorte/'+r['id']]
        g.add((node,RDF.type,L.RecorteCandidato));g.add((room,L.recorteCandidato,node))
        g.add((node,L.interfaceAnterior,HI[r['interface']]))
        g.add((node,L.paredeHospedeira,OLD[r['parede']]))
        g.add((node,L.abertura,OLD[r['abertura']]))
        g.add((node,L.areaM2,number(r['area_m2'])))
        g.add((node,L.apoioVolume3DNoCriterio,Literal(r['apoio_volume_3D_no_criterio'])))
        g.add((node,L.areaSemApoioVolume3DM2,number(r['area_sem_apoio_volume_3D_m2'])))
        g.add((node,L.validacaoArquitetonica,Literal('pendente')))
        g.add((node,P.wasGeneratedBy,activity));geometry(node,r['wkt'])
        for f in r['preenchimentos']:
            fill=OLD[f['guid']];g.add((node,L.preenchimento,fill))
            g.add((fill,L.classeIFC,Literal(f['classe'])))
            if f['nome']:g.add((fill,RDFS.label,Literal(f['nome'])))
    for r in d['areas_por_interface']:
        node=B['balanco/'+r['interface']]
        g.add((node,RDF.type,L.BalancoDeArea));g.add((node,L.interfaceAnterior,HI[r['interface']]))
        g.add((node,P.wasGeneratedBy,activity))
        for field in ['area_bruta_m2','area_uniao_recortes_m2','area_residual_m2','area_uniao_recortes_apoiados_3D_m2','area_residual_apos_recortes_apoiados_3D_m2']:
            g.add((node,L[field],number(r[field])))
        g.add((node,L.conservacaoArea,Literal(r['conservacao_area'])))
        for i,wkt in enumerate(r['wkt_residual']):
            geom=B['residuo-interface/'+r['interface']+'/'+str(i)]
            g.add((node,L.geometriaResidual,geom));geometry(geom,wkt)
    for r in d['interfaces_entre_espacos']:
        node=B['par/'+r['id']];g.add((node,RDF.type,L.ParEntreEspacosCandidato))
        g.add((node,L.espacoA,room));g.add((node,L.espacoB,OLD[r['outro_espaco']]))
        g.add((node,L.areaNoPlanoAM2,number(r['area_cozinha_m2'])))
        g.add((node,P.wasGeneratedBy,activity));geometry(node,r['wkt_cozinha'])
        for i,wkt in enumerate(r['wkt_outro_espaco']):
            other=B['par/'+r['id']+'/plano-B/'+str(i)]
            g.add((node,L.geometriaNoPlanoB,other));geometry(other,wkt)
    for r in d['residuos_faces_espaco']:
        node=B['residuo-espaco/'+r['face_cozinha']]
        g.add((node,RDF.type,L.ResiduoSemClassificacaoExterna))
        g.add((room,L.residuoCandidato,node));g.add((node,P.wasGeneratedBy,activity))
        g.add((node,L.areaM2,number(r['area_residual_m2'])))
        for i,wkt in enumerate(r['wkt_residual']):
            geom=B['residuo-espaco/'+r['face_cozinha']+'/'+str(i)]
            g.add((node,L.geometriaResidual,geom));geometry(geom,wkt)
    target=out/'Cozinha_Hibrido_Com_Ensaio_Lilis_v01.ttl';g.serialize(target,format='turtle')
    reread=Graph().parse(target,format='turtle')
    assert set(g)==set(reread) and before.issubset(set(reread)) and sha(base_rdf)==base_sha
    BOT=Namespace('https://w3id.org/bot#')
    assert not any(p in [BOT.adjacentElement,BOT.intersectingElement,BOT.adjacentZone] for s,p,o in set(g)-before)
    query='''PREFIX lil: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/lilis-piloto#>
SELECT ?recorte ?interface ?abertura ?area ?apoio3D ?areaSemApoio WHERE {
 ?recorte a lil:RecorteCandidato; lil:interfaceAnterior ?interface;
 lil:abertura ?abertura; lil:areaM2 ?area;
 lil:apoioVolume3DNoCriterio ?apoio3D; lil:areaSemApoioVolume3DM2 ?areaSemApoio .
} ORDER BY ?recorte'''
    (out/'Consultar_Recortes_Lilis.rq').write_text(query,encoding='utf8')
    rows=list(reread.query(query));assert len(rows)==len(d['recortes_hibridos'])
    with (out/'Consulta_Recortes_Lilis.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        writer=csv.writer(fp);writer.writerow([str(v) for v in rows[0].labels] if rows else [])
        writer.writerows([[str(v) for v in row] for row in rows])
    summary={'triplas_entrada':len(before),'triplas_saida':len(g),'linhas_consulta':len(rows),
        'triplas_anteriores_preservadas':True,'roundtrip_sem_alteracao':True,
        'sha256_rdf_entrada':base_sha,'sha256_rdf_saida':sha(target),
        'novas_adjacencias_BOT_certificadas':0,'validacao_arquitetonica':'pendente'}
    (out/'Registro_RDF_Lilis_v01.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2));return summary
