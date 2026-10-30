"""Integra o complemento ao grafo completo do Notebook 1 por GUID único.

Conversão preservada: Bonduel et al. (2018), IFCtoLBD 2.49.0, com a
correção textual já documentada. Não reexecuta Java nem apaga relações antigas.
"""
from pathlib import Path
import json,zipfile,hashlib,shutil,csv,gc
from collections import defaultdict
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS
from rotina_hibrida import C,B,OLD

PROPS=Namespace('http://lbd.arch.rwth-aachen.de/props#')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(pacote_original,complemento,conferencia,resultado,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    archive=zipfile.ZipFile(pacote_original)
    # A conversão menor fornece as identidades; o grafo completo é copiado
    # por fluxo, evitando manter duas cópias das malhas grandes em memória.
    converted=Graph().parse(data=archive.read('arquitetura_ifctolbd.ttl'),format='turtle')
    idx=defaultdict(set)
    for s,o in converted.subject_objects(PROPS.globalIdIfcRoot_attribute_simple):idx[str(o)].add(s)
    if any(len(v)!=1 for v in idx.values()):raise ValueError('Identidade ambígua por GlobalId no grafo principal.')
    addon=Graph().parse(complemento,format='turtle');mapped=Graph()
    for prefix,ns in addon.namespaces():mapped.bind(prefix,ns)
    mapped.bind('con',C);mappings={}
    def canonical(term):
        if isinstance(term,URIRef) and str(term).startswith(str(OLD)):
            guid=str(term)[len(str(OLD)):]
            if guid in idx:
                target=next(iter(idx[guid]));mappings[guid]=str(target);return target
        return term
    for s,p,o in addon:mapped.add((canonical(s),p,canonical(o)))
    d=json.loads(Path(resultado).read_text(encoding='utf8'))
    audit=json.loads(Path(conferencia).read_text(encoding='utf8'))
    room=next(iter(idx[d['ambiente']]))
    for r in audit['casos_documentais_indeterminados']:
        node=next(iter(idx[r['guid']]))
        mapped.add((node,C.statusDocumental,Literal('indeterminado; divergência entre pranchas 02 e 24/25')))
        mapped.add((node,C.justificativaDocumental,Literal(r['justificativa'],lang='pt')))
    mapped.add((B['execucao'],C.sha256ReferenciaDocumental,Literal(audit['sha256_referencia'])))
    mapped.add((B['execucao'],C.modoConversaoPrincipal,Literal('Resultados v03 reutilizados por hash; conversor não reexecutado nesta revisão.')))
    mapped.add((room,C.resultadoAtual,B['execucao']))
    for r in d['esquadrias_associadas']:
        assert r['preenchimento'] in mappings and r['abertura'] in mappings
    compact=out/'Complemento_Com_Identidades_N1_v08.ttl';mapped.serialize(compact,format='turtle')
    assert set(Graph().parse(compact,format='turtle'))==set(mapped)
    target=out/'Notebook1_Arquitetura_Com_Hibrido_v08.ttl'
    expected='7694e6bc327485ae320de14e51cc3229f43b0574e922a84454129428387af9db'
    prefix_hash=hashlib.sha256();prefix_bytes=0
    with archive.open('rdf/arquitetura_enriquecida.ttl') as src,target.open('wb') as dest:
        while True:
            chunk=src.read(1024*1024)
            if not chunk:break
            dest.write(chunk);prefix_hash.update(chunk);prefix_bytes+=len(chunk)
        assert prefix_hash.hexdigest()==expected
        dest.write(b'\n\n# Complemento consolidado v08. Relacoes anteriores preservadas.\n')
        dest.write(compact.read_bytes())
    with target.open('rb') as fp:
        digest=hashlib.sha256();remaining=prefix_bytes
        while remaining:
            chunk=fp.read(min(1024*1024,remaining));digest.update(chunk);remaining-=len(chunk)
    assert digest.hexdigest()==expected
    del converted,addon;gc.collect()
    # Reabre a união efetivamente salva para verificar a consulta principal.
    print('Reabrindo o grafo completo do Notebook 1 para consulta...',flush=True)
    full=Graph().parse(target,format='turtle')
    query='''PREFIX con: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/consolidado#>
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ambiente ?elemento ?guid ?nome ?abertura ?statusDocumental WHERE {
 ?ambiente props:globalIdIfcRoot_attribute_simple ?guidAmbiente; con:esquadriaAssociada ?elemento .
 FILTER(STR(?guidAmbiente) = "3UFjAT4k55zg_Pqo6VMw5l")
 ?elemento props:globalIdIfcRoot_attribute_simple ?guid; con:aberturaFonte ?abertura .
 OPTIONAL { ?elemento rdfs:label ?nome }
 OPTIONAL { ?elemento con:statusDocumental ?statusDocumental }
} ORDER BY ?guid'''
    (out/'Consultar_Cozinha_Atual_v08.rq').write_text(query,encoding='utf8')
    rows=list(full.query(query))
    expected_set={r['preenchimento'] for r in d['esquadrias_associadas']}
    assert {str(r.guid) for r in rows}==expected_set
    assert len(set(full.objects(room,C.esquadriaAssociada)))==9
    assert len(set(full.objects(room,C.elementoInternoCandidato)))==10
    assert len(set(full.objects(room,C.componenteSemFillsVoidsCandidato)))==3
    with (out/'Consulta_Cozinha_Atual_v08.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.writer(fp);w.writerow([str(v) for v in rows[0].labels]);w.writerows([[str(v) if v is not None else '' for v in r] for r in rows])
    record={'triplas_base_historica':117591,'triplas_uniao_atual':len(full),'triplas_complemento':len(mapped),
        'produtos_mapeados_por_GUID':len(mappings),'esquadrias_consulta_distintas':len(expected_set),
        'linhas_consulta_com_labels':len(rows),'prefixo_base_preservado_bytes':prefix_bytes,
        'sha256_prefixo_base':expected,'sha256_saida':sha(target),'consulta_reaberta_aprovada':True,
        'limite':'Preserva o grafo anterior e seus diagnósticos; a consulta atual usa con:esquadriaAssociada, sem transitividade via parede.'}
    (out/'Registro_Integracao_N1_v08.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'Mapa_GUID_Para_URI_N1.json').write_text(json.dumps(mappings,ensure_ascii=False,indent=2),encoding='utf8')
    del full;gc.collect()
    # O TTL grande é distribuído compactado para respeitar o limite do GitHub.
    with zipfile.ZipFile(out/'Notebook1_Grafo_Completo_v08.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(target,target.name);z.write(compact,compact.name)
    print(json.dumps(record,ensure_ascii=False,indent=2));return record
