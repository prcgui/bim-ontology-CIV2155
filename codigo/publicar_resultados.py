"""Publica resultados primários e integra a conversão semântica à geometria.

Seleção de colunas de apresentação; não executa ensaios ou auditorias.
A base semântica é preservada integralmente como conjunto de triplas.
O padrão geom:asBody de BimSPARQL é usado para os polígonos WKT 3D.
"""
from pathlib import Path
import csv,json,zipfile
from collections import Counter
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,XSD
from preparar_geometria import SHA,sha,save
from rotina_multiambientes import write_csv

NS='https://github.com/prcgui/bim-ontology-CIV2155/'
M=Namespace(NS+'vocab/analise#');B=Namespace(NS+'id/analise/')
GEOM=Namespace('http://bimsparql.org/geometry#');PROV=Namespace('http://www.w3.org/ns/prov#')

def publicar(brutos,base_ttl,identidades,out):
    brutos=Path(brutos);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with Path(identidades).open(encoding='utf-8-sig') as fp:
        records=list(csv.DictReader(fp))
    ids={r['GlobalId']:URIRef(r['uri']) for r in records}
    if len(ids)!=len(records):raise ValueError('GUID duplicado no mapa de identidades.')
    g=Graph().parse(base_ttl,format='turtle');base_count=len(g)
    g.parse(Path(__file__).with_name('Vocabulario.ttl'),format='turtle')
    for p,ns in [('civ',M),('analise',B),('geom',GEOM),('prov',PROV)]:g.bind(p,ns)
    activity=B.execucao;g.add((activity,RDF.type,PROV.Activity));g.add((activity,M.sha256IFC,Literal(SHA)))
    g.add((activity,M.sha256BaseSemantica,Literal(sha(base_ttl))))
    frame=B['referencial-projeto-metros']
    g.add((frame,RDFS.label,Literal('Coordenadas cartesianas do projeto IFC em metros; não CRS84.',lang='pt')))
    rooms=[];pairs=[];interfaces=[];cuts=[]
    for file in sorted((brutos/'ambientes').glob('*/Resultado_Ambiente.json')):
        d=json.loads(file.read_text(encoding='utf8'));guid=d['ambiente'];room=ids[guid];node=B['resultado/'+guid]
        row={'ambiente':guid,'nome':d['nome'],'estado':d['estado'],
             'esquadrias':d['resumo']['esquadrias'],'interfaces':d['resumo']['interfaces'],
             'interfaces_qualificadas':d['resumo'].get('interfaces_qualificadas'),
             'pendencias':len(d['problemas']),'motivo':d.get('motivo','')}
        rooms.append(row)
        for p,o in [(RDF.type,M.ResultadoPorAmbiente),(M.ambiente,room),(M.nome,Literal(d['nome'])),
                    (M.estado,Literal(d['estado'])),(PROV.wasGeneratedBy,activity)]:g.add((node,p,o))
        g.add((room,M.resultado,node))
        if d['estado'].startswith('inconclusivo_'):
            g.add((node,M.motivo,Literal(d.get('motivo','Geometria indisponível'))))
        else:
            g.add((node,M.quantidadeEsquadrias,Literal(len(d['esquadrias_associadas']))))
            for e in d['esquadrias_associadas']:
                product=ids[e['guid']];g.add((node,M.esquadriaAssociada,product))
                pairs.append({'ambiente':guid,'nome_ambiente':d['nome'],'esquadria':e['guid'],
                    'nome_esquadria':e['nome'],'classe':e['classe'],
                    'aberturas':';'.join(e['aberturas']),'interfaces':';'.join(e['interfaces'])})
        for i in d['interfaces']:
            rec={'ambiente':guid,'interface':i['id'],'parede':i['parede'],
                 'face_ambiente':i['face_ambiente'],'face_parede':i['face_parede'],
                 'area_m2':i['area_m2'],'qualificada':i['qualificada_no_criterio'],
                 'distancia_planos_m':i['distancia_planos_m'],'wkt':i['wkt']}
            interfaces.append(rec);surface=B['interface/'+guid+'/'+i['id']]
            for p,o in [(RDF.type,M.Interface),(M.paredeHospedeira,ids[i['parede']]),
                        (M.areaM2,Literal(i['area_m2'])),(M.qualificada,Literal(i['qualificada_no_criterio'])),
                        (GEOM.asBody,Literal(i['wkt'])),(M.referencial,frame)]:g.add((surface,p,o))
            g.add((node,M.interface,surface))
        for i in d['recortes_aberturas']:
            rec={k:i[k] for k in ['id','interface','parede','abertura','preenchimento','classe','nome','area_m2','wkt','qualificada_no_criterio']}
            cuts.append({'ambiente':guid,**rec});patch=B['recorte/'+guid+'/'+i['id']]
            for p,o in [(RDF.type,M.RecorteAbertura),(M.interfaceFonte,B['interface/'+guid+'/'+i['interface']]),
                        (M.aberturaFonte,ids[i['abertura']]),(M.preenchimento,ids[i['preenchimento']]),
                        (M.areaM2,Literal(i['area_m2'])),(M.qualificada,Literal(i['qualificada_no_criterio'])),
                        (GEOM.asBody,Literal(i['wkt'])),(M.referencial,frame)]:g.add((patch,p,o))
    write_csv(out/'Ambientes.csv',rooms);write_csv(out/'Esquadrias_Por_Ambiente.csv',pairs)
    write_csv(out/'Interfaces.csv',interfaces);write_csv(out/'Recortes_Aberturas.csv',cuts)
    ttl=out/'Arquitetura_Analisada.ttl';g.serialize(ttl,format='turtle')
    # Reabrir e consultar o artefato que será efetivamente disponibilizado.
    reopened=Graph().parse(ttl,format='turtle')
    query=lambda name:list(reopened.query(Path(__file__).with_name(name).read_text(encoding='utf8')))
    for source,target in [('01_ambientes.rq','Consulta_Ambientes.csv'),('02_esquadrias.rq','Consulta_Esquadrias.csv')]:
        result=reopened.query(Path(__file__).with_name(source).read_text(encoding='utf8'))
        names=[str(v) for v in result.vars]
        write_csv(out/target,[{name:str(value) if value is not None else '' for name,value in zip(names,row)} for row in result])
    graph_pairs=query('02_esquadrias.rq')
    if len(graph_pairs)!=len(pairs) or len(query('01_ambientes.rq'))!=len(rooms):
        raise ValueError('Consultas ao grafo não reproduzem as tabelas de resultado.')
    with zipfile.ZipFile(out/'Arquitetura_Analisada.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(ttl,ttl.name)
    ttl.unlink()  # Apenas a cópia intermediária; o resultado publicado está no ZIP.
    summary={'ifc_sha256':SHA,'espacos_solicitados':len(rooms),
             'espacos_com_associacao':sum(r['estado'].startswith('associacao_') for r in rooms),
             'espacos_inconclusivos':sum(r['estado'].startswith('inconclusivo_') for r in rooms),
             'estados':dict(Counter(r['estado'] for r in rooms)),
             'pares_ambiente_esquadria':len(pairs),'esquadrias_distintas':len({r['esquadria'] for r in pairs}),
             'interfaces_candidatas':len(interfaces),'recortes_aberturas':len(cuts),
             'triplas_base_semantica':base_count,'triplas_grafo_entregue':len(reopened),
             'coordenadas':'Referencial cartesiano do IFC; metros; não CRS84.',
             'alcance':'Associação geométrica no mesmo IFC; conferência documental em 14 ambientes. Não certifica completude arquitetônica.'}
    save(out/'Resumo.json',summary);return summary
