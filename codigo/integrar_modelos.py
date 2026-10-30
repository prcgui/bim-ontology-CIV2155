"""Integra extrações do mesmo motor em um RDF Dataset com origem preservada.

Bonduel et al. (2018): IFCtoLBD (motor compartilhado com o Notebook 1).
Rasmussen et al. (2021), DOI 10.3233/SW-200385: vocabulário BOT.
W3C RDF 1.1 Concepts, §§1.6 e 4: conjuntos de grafos nomeados.
Nenhuma equivalência owl:sameAs é criada a partir de nomes ou cotas.
"""
from pathlib import Path
from collections import Counter
import csv,json,zipfile,hashlib,gc
from urllib.request import urlretrieve
import ifcopenshell
import ifcopenshell.util.unit as units
import ifcopenshell.util.element as element_util
import ifcopenshell.util.placement as placement
from rdflib import Graph,Dataset,Namespace,URIRef,Literal,RDF,RDFS,XSD
from rdflib.compare import isomorphic,to_isomorphic
from converter_ifc import converter

BASE='https://github.com/prcgui/bim-ontology-CIV2155/'
N=Namespace(BASE+'vocab/integracao#');B=Namespace(BASE+'id/integracao/')
P=Namespace('http://lbd.arch.rwth-aachen.de/props#');BOT=Namespace('https://w3id.org/bot#')
PROV=Namespace('http://www.w3.org/ns/prov#')
GRAPH_IRIS={k:URIRef(BASE+'grafo/'+k) for k in ['arquitetura','smt','sco','relacoes','proveniencia']}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def write_csv(path,rows,fields=None):
    if not rows and not fields:return
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows(rows)

def extrair_entradas(raiz,trabalho,config):
    raiz=Path(raiz);trabalho=Path(trabalho);trabalho.mkdir(parents=True,exist_ok=True);paths={}
    for key,entry in config['modelos'].items():
        source=raiz/entry['zip'];target=trabalho/entry['arquivo']
        if sha(source)!=entry['sha256_zip']:raise ValueError('ZIP diferente da fonte: '+key)
        with zipfile.ZipFile(source) as z:target.write_bytes(z.read(entry['arquivo']))
        if sha(target)!=entry['sha256_ifc']:raise ValueError('IFC diferente da fonte: '+key)
        paths[key]=target
    return paths

def extrair_modelos(paths,config,trabalho,reconverter=True):
    """Arquitetura e estruturas passam pela mesma função converter do N1."""
    trabalho=Path(trabalho);files={}
    for key,path in paths.items():
        entry=config['modelos'][key];folder=trabalho/key;folder.mkdir(parents=True,exist_ok=True)
        target=folder/'modelo.ttl';record=folder/'Registro_Extracao.json'
        expected={'ifc_sha256':entry['sha256_ifc'],'namespace':entry['namespace'],
                  'extrator_sha256':sha(Path(__file__).with_name('converter_ifc.py'))}
        previous=json.loads(record.read_text(encoding='utf8')) if record.exists() else {}
        reuse=(not reconverter and target.exists() and all(previous.get(k)==v for k,v in expected.items())
               and previous.get('rdf_sha256')==sha(target))
        if not reuse:
            converter(path,target,folder/'motor_preparado',ifc_sha256=entry['sha256_ifc'],base_uri=entry['namespace'],java_heap='3g')
            save(record,{**expected,'rdf_sha256':sha(target)})
        files[key]=target;print('EXTRAÇÃO',key,'reutilizada:',reuse,flush=True)
    return files

def caracterizar(modelo,path,grafo):
    model=ifcopenshell.open(path);products=model.by_type('IfcProduct');index={}
    for s,o in grafo.subject_objects(P.globalIdIfcRoot_attribute_simple):index.setdefault(str(o),set()).add(s)
    absent=[];ambiguous=[];divergent=[];rows=[];identities={}
    for e in products:
        matches=index.get(e.GlobalId,set())
        if not matches:absent.append(e.GlobalId);continue
        if len(matches)!=1:ambiguous.append(e.GlobalId);continue
        uri=next(iter(matches));identities[e.GlobalId]=uri
        if e.Name is not None and str(grafo.value(uri,RDFS.label))!=e.Name:divergent.append(e.GlobalId)
        container=element_util.get_container(e,ifc_class='IfcBuildingStorey')
        rows.append({'modelo':modelo,'guid':e.GlobalId,'classe_ifc':e.is_a(),'nome':e.Name,
                     'uri':str(uri),'pavimento_ifc':container.GlobalId if container else ''})
    if absent or ambiguous or divergent or len(identities)!=len(products):
        raise ValueError(f'Extração {modelo} não preservou identidades/textos: ausentes={len(absent)}, ambíguos={len(ambiguous)}, nomes={len(divergent)}')
    contexts=[]
    for c in model.by_type('IfcGeometricRepresentationContext',include_subtypes=False):
        contexts.append({'tipo':c.ContextType,'precisao_unidade_projeto':c.Precision,
                         'wcs':placement.get_axis2placement(c.WorldCoordinateSystem).tolist(),
                         'norte':list(c.TrueNorth.DirectionRatios) if c.TrueNorth else None})
    locations=[]
    scale=units.calculate_unit_scale(model)
    for cls in ['IfcSite','IfcBuilding','IfcBuildingStorey']:
        for e in model.by_type(cls):
            matrix=placement.get_local_placement(e.ObjectPlacement) if e.ObjectPlacement else None
            origin=[float(x)*scale for x in matrix[:3,3]] if matrix is not None else None
            locations.append({'classe':cls,'guid':e.GlobalId,'nome':e.Name,'origem_m':origin,
                'elevacao_declarada_m':float(e.Elevation)*scale if getattr(e,'Elevation',None) is not None else None})
    info={'modelo':modelo,'arquivo':Path(path).name,'sha256_ifc':sha(path),'produtos_ifc':len(products),
          'elementos_ifc':len(model.by_type('IfcElement')),'espacos_ifc':len(model.by_type('IfcSpace')),
          'produtos_identificados_no_rdf':len(identities),'triplas':len(grafo),'fator_comprimento_para_m':scale,
          'contextos_geometricos':contexts,'posicionamentos_espaciais':locations,
          'map_conversion_declarada':len(model.by_type('IfcMapConversion')),'classes_ifc':dict(Counter(e.is_a() for e in products))}
    del model;return info,identities,rows

def integrar(grafo_n1,paths,extracoes,relacoes_dir,saida):
    """Mantém o resultado atual do N1 e acrescenta grafos de origem e ligações."""
    out=Path(saida);out.mkdir(parents=True,exist_ok=True);relations=Path(relacoes_dir)
    ds=Dataset();ds.bind('int',N);ds.bind('bot',BOT);ds.bind('prov',PROV)
    arq=ds.graph(GRAPH_IRIS['arquitetura'])
    with zipfile.ZipFile(grafo_n1) as z:arq.parse(data=z.read('Arquitetura_Analisada.ttl'),format='turtle')
    if Literal(sha(paths['arquitetura'])) not in set(arq.objects(None,URIRef(BASE+'vocab/analise#sha256IFC'))):
        raise ValueError('O resultado do N1 não declara o IFC arquitetônico desta execução.')
    # A semântica reextraída deve corresponder exatamente à base que o N1 usou.
    original=Graph().parse(extracoes['arquitetura'],format='turtle')
    if not all(t in arq for t in original):raise ValueError('A reextração arquitetônica não corresponde à base do Notebook 1.')
    del original;gc.collect()
    metas=[];indices={};all_rows=[]
    for key,path in paths.items():
        graph=arq if key=='arquitetura' else ds.graph(GRAPH_IRIS[key]).parse(extracoes[key],format='turtle')
        info,index,rows=caracterizar(key,path,graph);metas.append(info);indices[key]=index;all_rows.extend(rows)
        print('GRAFO',key,info['triplas'],'triplas;',info['produtos_identificados_no_rdf'],'produtos preservados',flush=True)
    keys=list(indices)
    for i,key in enumerate(keys):
        for other in keys[i+1:]:
            if set(indices[key].values()) & set(indices[other].values()):
                raise ValueError('Há colisão de URIs de produtos entre modelos.')
    meta=ds.graph(GRAPH_IRIS['proveniencia']);meta.add((B.estudo,RDF.type,N.EstudoMultimodelos))
    for info in metas:
        key=info['modelo'];source=B['modelo/'+key];meta.add((B.estudo,N.modelo,source))
        for p,o in [(RDF.type,N.ModeloIFC),(N.chave,Literal(key)),(N.grafo,GRAPH_IRIS[key]),
                    (N.sha256IFC,Literal(info['sha256_ifc'])),(N.fatorComprimentoParaMetro,Literal(info['fator_comprimento_para_m']))]:meta.add((source,p,o))
        for guid,uri in indices[key].items():meta.add((uri,PROV.wasDerivedFrom,source))
    links=ds.graph(GRAPH_IRIS['relacoes']);links.parse(Path(__file__).with_name('Vocabulario_Integracao.ttl'),format='turtle')
    records=list(csv.DictReader((relations/'Relacoes_Espaciais.csv').open(encoding='utf-8-sig')))
    for i,r in enumerate(records,1):
        model=r['modelo'];room=indices['arquitetura'][r['ambiente']];element=indices[model][r['elemento']]
        predicate=BOT[r['predicado_bot']];node=B['relacao/'+model+'/'+r['ambiente']+'/'+r['elemento']]
        links.add((room,predicate,element))
        for p,o in [(RDF.type,N.RelacaoEspacial),(N.ambiente,room),(N.elementoEstrutural,element),
                    (N.modelo,B['modelo/'+model]),(N.predicado,predicate),(N.estado,Literal(r['estado'])),
                    (N.volumeIntersecaoM3,Literal(float(r['volume_intersecao_m3']))),
                    (N.volumeElementoM3,Literal(float(r['volume_elemento_m3']))),
                    (N.areaContatoM2,Literal(float(r['area_contato_m2']))),
                    (N.referencial,Literal('Placements dos IFCs aplicados; metros; sem registro espacial inferido.'))]:links.add((node,p,o))
    expected={k:len(ds.graph(uri)) for k,uri in GRAPH_IRIS.items()}
    signatures={k:str(to_isomorphic(ds.graph(uri)).graph_digest()) for k,uri in GRAPH_IRIS.items()}
    # N-Quads/N-Triples conservam os literais tipados completos. O atalho
    # numérico do serializador Turtle/TriG pode arredondar xsd:double.
    artifact=out/'Integracao_Arquitetura_Estrutura.nq';ds.serialize(artifact,format='nquads')
    links.serialize(out/'Relacoes_Interdisciplinares.nt',format='nt')
    write_csv(out/'Identidades_Modelos.csv',all_rows)
    write_csv(out/'Modelos_Integrados.csv',[{k:i[k] for k in ['modelo','arquivo','produtos_ifc','elementos_ifc','espacos_ifc','produtos_identificados_no_rdf','triplas','fator_comprimento_para_m']} for i in metas])
    save(out/'Fontes_e_Referenciais.json',{'modelos':metas,'criterio':'Mesmos IFCs R03; unidades normalizadas na geometria, placements declarados aplicados. Sem equivalência por nome ou translação inferida. Ausência de MapConversion impede declarar georreferenciamento validado.'})
    del graph,arq,links,meta,ds;gc.collect()
    reopened=Dataset();reopened.parse(artifact,format='nquads')
    observed={k:len(reopened.graph(uri)) for k,uri in GRAPH_IRIS.items()}
    if expected!=observed:raise ValueError('O Dataset reaberto não conserva as contagens por grafo.')
    reopened_signatures={k:str(to_isomorphic(reopened.graph(uri)).graph_digest()) for k,uri in GRAPH_IRIS.items()}
    if signatures!=reopened_signatures:raise ValueError('A reabertura alterou termos RDF em algum grafo.')
    queried=[]
    for name,filename in [('03_modelos_integrados.rq','Consulta_Modelos.csv'),('04_relacoes_estrutura_ambientes.rq','Consulta_Relacoes.csv')]:
        result=reopened.query(Path(__file__).with_name(name).read_text(encoding='utf8'))
        names=[str(v) for v in result.vars];rows=[{n:str(v) if v is not None else '' for n,v in zip(names,row)} for row in result]
        write_csv(out/filename,rows,names)
        if name.startswith('04_'):queried=rows
    if len(queried)!=len(records):raise ValueError('Consulta interdisciplinares não reproduz as relações registradas.')
    n1pairs=len(list(reopened.graph(GRAPH_IRIS['arquitetura']).triples((None,URIRef(BASE+'vocab/analise#esquadriaAssociada'),None))))
    if n1pairs!=101:raise ValueError('As associações do N1 não foram preservadas.')
    with zipfile.ZipFile(out/'Integracao_Arquitetura_Estrutura.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(artifact,artifact.name)
    artifact.unlink()
    summary={'grafos_nomeados':observed,'quadruplas':sum(observed.values()),'relacoes_interdisciplinares':len(records),
             'pares_n1_preservados':n1pairs,'origens_preservadas':True,'owl_sameAs_inferido':False,
             'preservacao_semantica_por_grafo':signatures==reopened_signatures,'formato_dataset':'N-Quads',
             'por_modelo':dict(Counter(r['modelo'] for r in records)),'por_relacao':dict(Counter(r['estado'] for r in records)),
             'alcance':'Federação RDF e relações geométricas no referencial dos arquivos. Não certifica coordenação de projeto, função ou adequação estrutural.'}
    save(out/'Resumo_Integracao.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True);return summary
