"""Organização incremental do N2, sem nova inferência geométrica.

Bonduel et al. (2018), §§1.3 e 2.1: recursos e contexto de propriedades.
buildingSMART IFC4 IfcPropertySingleValue: unidade explícita ou unidade de projeto
correspondente ao tipo da medida. Não elevar a unidade linear ao quadrado/cubo.
W3C SHACL (2017) e PROV-O (2013): contrato próprio e proveniência de execução.
O perfil não implementa gUFO, gOCED, GoDa nem harmonização global de propriedades.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import csv, json, zipfile, hashlib, time
from rdflib import Dataset, Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD, BNode
from rdflib.compare import to_isomorphic

BASE = 'https://github.com/prcgui/bim-ontology-CIV2155/'
C = Namespace(BASE+'vocab/analise#')
N = Namespace(BASE+'vocab/integracao#')
CTX = Namespace(BASE+'vocab/contexto#')
B = Namespace(BASE+'id/integracao/')
BOT = Namespace('https://w3id.org/bot#')
PROV = Namespace('http://www.w3.org/ns/prov#')
P = Namespace('http://lbd.arch.rwth-aachen.de/props#')
GRAPHS = {k: URIRef(BASE+'grafo/'+k) for k in
          ['arquitetura','smt','sco','relacoes','proveniencia','perfil','bot-referencia','propriedades-contextuais','execucao-n3']}
V137 = '0EVSuIeKOHxuDHo7zKqQBn'
EXPECTED_SOURCE = '8fb829827ec1ad3b02285b0f24d8d8329c7c999bf3904c50533c37e3294f5959'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def salvar(p, obj, compacto=False):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=None if compacto else 2,
                           separators=(',',':') if compacto else None),encoding='utf8')

def carregar(raiz):
    raiz=Path(raiz)
    source=raiz/'resultados/integracao/Integracao_Arquitetura_Estrutura.zip'
    if sha(source)!=EXPECTED_SOURCE: raise ValueError('O N3 exige o resultado validado do N2 indicado no notebook.')
    ds=Dataset(default_union=True)
    with zipfile.ZipFile(source) as z:
        ds.parse(data=z.read('Integracao_Arquitetura_Estrutura.nq'),format='nquads')
    identities=list(csv.DictReader((raiz/'resultados/integracao/Identidades_Modelos.csv').open(encoding='utf-8-sig')))
    signatures={k:str(to_isomorphic(ds.graph(GRAPHS[k])).graph_digest()) for k in list(GRAPHS)[:5]}
    if len(identities)!=26601 or sum(len(ds.graph(GRAPHS[k])) for k in signatures)!=415175:
        raise ValueError('Contagens de entrada inesperadas.')
    return ds,identities,signatures

def contextualizar_v137(ds, identities, arquivo_ifc, hash_ifc):
    """POC delimitada: Psets diretamente associados, IfcPropertySingleValue.

    Mantém nomes originais, tipos nominais, valor e unidade nativa. IfcReal não
    recebe unidade por suposição. Não inclui propriedades herdadas de tipo,
    IfcElementQuantity nem outros subtipos de IfcProperty.
    """
    import ifcopenshell
    from ifcopenshell.util.unit import get_property_unit
    if sha(arquivo_ifc)!=hash_ifc: raise ValueError('IFC SCO diferente da fonte integrada.')
    model=ifcopenshell.open(arquivo_ifc); entity=model.by_guid(V137)
    row=next(r for r in identities if r['modelo']=='sco' and r['guid']==V137)
    product=URIRef(row['uri']); graph=ds.graph(GRAPHS['propriedades-contextuais'])
    ns=Namespace(BASE+'id/contexto/'+hash_ifc[:12]+'/')
    processed=[]; unsupported=[]
    for rel in sorted(entity.IsDefinedBy,key=lambda r:r.id()):
        if not rel.is_a('IfcRelDefinesByProperties'): continue
        pset=rel.RelatingPropertyDefinition
        if not pset.is_a('IfcPropertySet'):
            unsupported.append({'step':pset.id(),'tipo':pset.is_a()}); continue
        pn=ns['pset/'+pset.GlobalId]
        for p,o in [(RDF.type,CTX.ConjuntoPropriedadesIFC),(RDFS.label,Literal(pset.Name or '')),
                    (CTX.globalIdPset,Literal(pset.GlobalId)),(CTX.stepIFC,Literal(pset.id())),
                    (CTX.produto,product),(PROV.wasDerivedFrom,B['modelo/sco'])]: graph.add((pn,p,o))
        graph.add((product,CTX.conjuntoPropriedades,pn))
        for prop in pset.HasProperties:
            if not prop.is_a('IfcPropertySingleValue') or prop.NominalValue is None:
                unsupported.append({'step':prop.id(),'tipo':prop.is_a()}); continue
            node=ns['propriedade/'+pset.GlobalId+'/'+str(prop.id())]
            typ=prop.NominalValue.is_a(); value=prop.NominalValue.wrappedValue
            # The nominal IFC type remains explicit even when RDF scalar datatypes coincide.
            literal=Literal(value)
            unit=get_property_unit(prop,model)
            origin='explicita' if prop.Unit is not None else ('unidades_do_projeto_por_tipo_da_medida' if unit else 'nao_declarada_ou_nao_dimensional')
            graph.add((pn,CTX.propriedade,node))
            for p,o in [(RDF.type,CTX.OcorrenciaPropriedadeIFC),(RDFS.label,Literal(prop.Name)),
                        (CTX.stepIFC,Literal(prop.id())),(CTX.tipoValorIFC,Literal(typ)),
                        (RDF.value,literal),(CTX.conjuntoFonte,pn),(CTX.origemUnidade,Literal(origin)),
                        (PROV.wasDerivedFrom,B['modelo/sco'])]: graph.add((node,p,o))
            unit_info=None
            if unit:
                un=ns['unidade/'+str(unit.id())]; graph.add((node,CTX.unidade,un))
                unit_info={'step':unit.id(),'tipo':unit.is_a(),'tipo_unidade':str(getattr(unit,'UnitType','')),
                           'nome':str(getattr(unit,'Name','')),'prefixo':str(getattr(unit,'Prefix',None) or '')}
                for p,o in [(RDF.type,CTX.UnidadeIFC),(CTX.stepIFC,Literal(unit.id())),
                            (CTX.tipoIFC,Literal(unit_info['tipo'])),(CTX.tipoUnidade,Literal(unit_info['tipo_unidade'])),
                            (CTX.nomeUnidade,Literal(unit_info['nome'])),(CTX.prefixoUnidade,Literal(unit_info['prefixo'])),
                            (PROV.wasDerivedFrom,B['modelo/sco'])]: graph.add((un,p,o))
            processed.append({'uri':str(node),'pset':pset.Name,'pset_guid':pset.GlobalId,
                              'nome':prop.Name,'step':prop.id(),'tipo_valor_ifc':typ,
                              'valor':value,'valor_lexical_rdf':str(literal),'datatype':str(literal.datatype or XSD.string),
                              'unidade':unit_info,'origem_unidade':origin})
    return {'produto_uri':str(product),'guid':V137,'nome':entity.Name,'step':entity.id(),
            'sha256_ifc':hash_ifc,'conjuntos':len(set(r['pset_guid'] for r in processed)),
            'propriedades':len(processed),'itens':processed,'nao_tratados':unsupported,
            'alcance':'Somente V137; Psets diretamente associados e valores simples; unidades nativas, sem harmonização ou cálculo estrutural.'}

def projecao_validacao(ds, identities):
    """Projeção verificável dos campos do contrato; não valida toda a semântica IFC/OWL."""
    g=Graph()
    for row in identities:
        s=URIRef(row['uri']); g.add((s,RDF.type,CTX.ProdutoIndexado))
        for p in [RDF.type,P.globalIdIfcRoot_attribute_simple,PROV.wasDerivedFrom]:
            for o in ds.objects(s,p): g.add((s,p,o))
    for typ in [N.ModeloIFC,N.RelacaoEspacial,C.ResultadoPorAmbiente,
                CTX.ConjuntoPropriedadesIFC,CTX.OcorrenciaPropriedadeIFC,CTX.UnidadeIFC]:
        for s in ds.subjects(RDF.type,typ):
            for t in ds.triples((s,None,None)): g.add(t)
    for predicate in [BOT.containsElement,BOT.intersectingElement,BOT.adjacentElement]:
        for t in ds.triples((None,predicate,None)): g.add(t)
    for t in ds.triples((B.estudo,None,None)): g.add(t)
    return g

def validar(ds, identities, raiz, saida):
    from pyshacl import validate
    g=projecao_validacao(ds,identities)
    t=time.perf_counter()
    conform,report,report_text=validate(g,shacl_graph=str(Path(raiz)/'codigo/Restricoes_Organizacao.ttl'),
                                       inference='none',advanced=False,inplace=False)
    out=Path(saida);out.mkdir(parents=True,exist_ok=True)
    if not isinstance(report,Graph): raise ValueError('Falha na especificação SHACL: '+str(report))
    report.serialize(out/'Validacao_SHACL.ttl',format='turtle')
    summary={'conforme':bool(conform),'inferencia':'none','triplas_da_projecao':len(g),
             'duracao_s':round(time.perf_counter()-t,3),
             'alvos':{str(typ):len(set(g.subjects(RDF.type,typ))) for typ in
                      [CTX.ProdutoIndexado,N.ModeloIFC,N.RelacaoEspacial,C.ResultadoPorAmbiente,
                       CTX.ConjuntoPropriedadesIFC,CTX.OcorrenciaPropriedadeIFC]},
             'alcance':'Contrato de identidade, proveniência, resultados, vínculos e POC de propriedades. Não certifica qualidade estrutural, alinhamento, completude IFC nem consistência OWL global.'}
    salvar(out/'Resumo_SHACL.json',summary)
    if not conform: raise ValueError(report_text[:8000])
    return summary

def consultar(ds, raiz, saida):
    """Consultas publicadas e executáveis, com resultados efetivos em JSON/CSV."""
    results=[]; out=Path(saida)
    for path in sorted((Path(raiz)/'codigo/consultas_exploracao').glob('*.rq')):
        print('CONSULTA',path.stem,flush=True)
        text=path.read_text(encoding='utf8'); result=ds.query(text)
        fields=[str(v) for v in result.vars]
        rows=[{k:str(v) if v is not None else None for k,v in zip(fields,row)} for row in result]
        with (out/(path.stem+'.csv')).open('w',encoding='utf-8-sig',newline='') as fp:
            w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows(rows)
        results.append({'id':path.stem,'consulta':text,'linhas':len(rows),'colunas':fields,'resultados':rows})
    salvar(out/'Consultas_Executadas.json',results)
    return results

def criar_indice(ds, identities, raiz, saida, poc, queries):
    """Índice de consulta visual, não substituto nem cópia integral do Dataset.

    Inclui os produtos e suas triplas diretas (exceto literais >4k caracteres),
    os registros N1/N2 e a extensão de propriedades. Termos RDF ficam tipados.
    Valores geométricos extensos continuam no Dataset integral disponibilizado.
    """
    terms=[];lookup={};quads=[];omitted=Counter()
    def term(t):
        if isinstance(t,URIRef): v=('u',str(t))
        elif isinstance(t,BNode): v=('b',str(t))
        else: v=('l',str(t),str(t.datatype or ''),str(t.language or ''))
        if v not in lookup:lookup[v]=len(terms);terms.append(v)
        return lookup[v]
    selected={URIRef(r['uri']) for r in identities}
    for typ in [N.ModeloIFC,N.RelacaoEspacial,C.ResultadoPorAmbiente,CTX.ConjuntoPropriedadesIFC,
                CTX.OcorrenciaPropriedadeIFC,CTX.UnidadeIFC]:selected.update(ds.subjects(RDF.type,typ))
    for s,p,o,c in ds.quads():
        if s not in selected: continue
        if isinstance(o,Literal) and len(str(o))>4000:
            omitted[str(p)]+=1;continue
        quads.append([term(s),term(p),term(o),term(c)])
    products=[{**r,'t':term(URIRef(r['uri']))} for r in identities]
    rooms=[]
    spatial=list(csv.DictReader((Path(raiz)/'resultados/integracao/Integracao_Por_Ambiente.csv').open(encoding='utf-8-sig')))
    spatial={r['ambiente']:r for r in spatial}
    for r in identities:
        if r['classe_ifc']!='IfcSpace' or r['modelo']!='arquitetura':continue
        s=URIRef(r['uri']);rec=next(ds.subjects(C.ambiente,s)); status=str(ds.value(rec,C.estado))
        rooms.append({'t':term(s),'guid':r['guid'],'nome':str(ds.value(rec,C.nome)),
                      'estado_n1':status,'esquadrias':int(ds.value(rec,C.quantidadeEsquadrias)) if ds.value(rec,C.quantidadeEsquadrias) is not None else None,
                      'estrutura':spatial[r['guid']]})
    # Full schema is separately inspectable, with its named-graph source.
    schema=[]
    for key in ['perfil','bot-referencia']:
        for s,p,o in ds.graph(GRAPHS[key]):
            if p in [RDF.type,RDFS.label,RDFS.subClassOf,RDFS.domain,RDFS.range]:
                schema.append([term(s),term(p),term(o),term(GRAPHS[key])])
    data={'versao':1,'produtos':products,'ambientes':rooms,'termos':terms,'quadruplas':quads,
          'esquema':schema,'poc':poc,'consultas':queries,
          'resumo':{'produtos':len(products),'ambientes':len(rooms),'quadruplas_no_indice':len(quads),
                    'literais_extensos_omitidos_por_predicado':dict(omitted),'sha256_n2':EXPECTED_SOURCE,
                    'escopo':'Triplas diretas dos produtos e registros selecionados. Geometria extensa e recursos auxiliares permanecem no Dataset integral.'}}
    target=Path(raiz)/'docs/dados/exploracao.json';salvar(target,data,True)
    salvar(Path(saida)/'Resumo_Indice.json',{**data['resumo'],'bytes':target.stat().st_size})
    return data['resumo']

def finalizar(ds, signatures, raiz, saida, inicio, resumo):
    """Confere os cinco grafos originais antes e depois da gravação N-Quads."""
    root=Path(raiz);out=Path(saida)
    for k,digest in signatures.items():
        if str(to_isomorphic(ds.graph(GRAPHS[k])).graph_digest())!=digest:
            raise ValueError('Grafo original alterado: '+k)
    run=URIRef(BASE+'id/execucao/n3/'+inicio.replace(':','').replace('+','_'))
    g=ds.graph(GRAPHS['execucao-n3'])
    for p,o in [(RDF.type,PROV.Activity),(PROV.startedAtTime,Literal(inicio,datatype=XSD.dateTime)),
                (PROV.endedAtTime,Literal(datetime.now(timezone.utc).isoformat(),datatype=XSD.dateTime)),
                (PROV.used,URIRef(BASE+'blob/main/resultados/integracao/Integracao_Arquitetura_Estrutura.zip')),
                (CTX.sha256Entrada,Literal(EXPECTED_SOURCE)),(CTX.sha256Codigo,Literal(sha(Path(__file__))))]:g.add((run,p,o))
    for graph in ['perfil','bot-referencia','propriedades-contextuais']:
        g.add((GRAPHS[graph],PROV.wasGeneratedBy,run))
    raw=out/'Dataset_Organizado.nq';ds.serialize(raw,format='nquads')
    reopened=Dataset(default_union=True)
    reopened.parse(raw,format='nquads')
    for k in GRAPHS:
        if str(to_isomorphic(ds.graph(GRAPHS[k])).graph_digest())!=str(to_isomorphic(reopened.graph(GRAPHS[k])).graph_digest()):
            raise ValueError('Serialização alterou termos do grafo '+k)
    with zipfile.ZipFile(out/'Dataset_Organizado.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(raw,raw.name)
    raw.unlink()
    summary={**resumo,'grafos':{k:len(ds.graph(v)) for k,v in GRAPHS.items()},
             'quadruplas':sum(len(ds.graph(v)) for v in GRAPHS.values()),
             'cinco_grafos_n2_inalterados':True,'reabertura_sem_alteracao_de_termos':True,
             'sha256_entrada_n2':EXPECTED_SOURCE,'sha256_saida':sha(out/'Dataset_Organizado.zip'),
             'inicio_utc':inicio,'fim_utc':datetime.now(timezone.utc).isoformat()}
    if sha(root/'resultados/integracao/Integracao_Arquitetura_Estrutura.zip')!=EXPECTED_SOURCE:
        raise ValueError('Arquivo original foi alterado.')
    salvar(out/'Resumo_Organizacao.json',summary)
    return summary
