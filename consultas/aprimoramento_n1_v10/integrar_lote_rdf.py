"""Complemento multiambientes ligado por GUID; preserva integralmente a v09."""
from pathlib import Path
from decimal import Decimal
import json,csv,zipfile,hashlib,gc
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS
from preparar_geometria import SHA,save,sha

M=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/aprimoramento#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/multiambientes-v10/')
G=Namespace('http://bimsparql.org/geometry#');P=Namespace('http://www.w3.org/ns/prov#')

def run(resultados,identidades_csv,base_zip,registro_base,out):
    resultados=Path(resultados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    index={}
    with Path(identidades_csv).open(encoding='utf-8-sig') as fp:
        for r in csv.DictReader(fp):
            if r['GlobalId'] in index:raise ValueError('GlobalId ambíguo no mapa do grafo principal.')
            index[r['GlobalId']]=URIRef(r['uri'])
    source=json.loads(Path(registro_base).read_text(encoding='utf8'))
    batch=json.loads((resultados/'Resumo_Lote_v10.json').read_text(encoding='utf8'))
    audit=json.loads((resultados/'conferencia/Conferencia_Multiambientes_v10.json').read_text(encoding='utf8'))
    document_rows=list(csv.DictReader((resultados/'conferencia/Conferencia_Caso_a_Caso_v10.csv').open(encoding='utf-8-sig')))
    g=Graph()
    for prefix,ns in [('mu',M),('mid',B),('geom',G),('prov',P)]:g.bind(prefix,ns)
    g.parse(Path(__file__).with_name('Vocabulario_Multiambientes.ttl'),format='turtle')
    activity=B['execucao'];frame=B['referencial-projeto-metros']
    g.add((activity,RDF.type,P.Activity));g.add((activity,M.sha256IFC,Literal(SHA)))
    g.add((activity,M.sha256Catalogo,Literal(batch['cache_catalogo_sha256'])))
    g.add((activity,M.sha256ReferenciaDocumental,Literal(audit['referencia_sha256'])))
    for uri in ['https://doi.org/10.26868/25222708.2021.30156','https://doi.org/10.3390/buildings13020350','https://doi.org/10.1016/j.autcon.2021.103659','https://doi.org/10.1016/j.autcon.2021.103724','https://doi.org/10.1016/j.autcon.2025.106081','https://doi.org/10.1016/j.autcon.2024.105293']:
        g.add((activity,P.wasDerivedFrom,URIRef(uri)))
    g.add((frame,RDFS.label,Literal('Coordenadas cartesianas do projeto IFC em metros; não CRS84.',lang='pt')))
    states={};pairs=set();interface_count=0
    def geom(node,wkt):
        g.add((node,G.asBody,Literal(wkt)));g.add((node,M.referencial,frame))
        g.add((node,M.unidade,URIRef('http://qudt.org/vocab/unit/M')))
    for path in sorted((resultados/'ambientes').glob('*/Resultado_Ambiente_v10.json')):
        d=json.loads(path.read_text(encoding='utf8'));guid=d['ambiente'];room=index[guid];node=B['resultado/'+guid]
        states[guid]=d['estado'];g.add((room,M.resultadoV09,node));g.add((node,RDF.type,M.ResultadoPorAmbiente))
        for p,o in [(M.ambiente,room),(M.nome,Literal(d['nome'])),(M.estado,Literal(d['estado'])),(P.wasGeneratedBy,activity)]:g.add((node,p,o))
        if d['estado'].startswith('inconclusivo_'):g.add((node,M.motivo,Literal(d.get('motivo','Indisponível'))))
        else:
            g.add((node,M.quantidadeEsquadrias,Literal(len(d['esquadrias_associadas']))))
            for e in d['esquadrias_associadas']:
                element=index[e['guid']];g.add((node,M.esquadriaAssociada,element));pairs.add((guid,e['guid']))
                for opening in e['aberturas']:g.add((element,M.aberturaFonte,index[opening]))
            for e in d['outros_preenchimentos']:g.add((node,M.outroPreenchimento,index[e['guid']]))
            for e in d['elementos_internos_candidatos']:g.add((node,M.elementoInternoCandidato,index[e['guid']]))
            for e in d['componentes_sem_FillsVoids_candidatos']:
                element=index[e['guid']];g.add((node,M.componenteSemFillsVoidsCandidato,element))
                for target in e['preenchimentos_alvo']:g.add((element,M.proximoDePreenchimento,index[target]))
        if d.get('preparacao_geometrica'):
            g.add((node,M.metodoPreparo,Literal(d['preparacao_geometrica']['metodo_v10'])))
        for i in d['interfaces']:
            surface=B['interface/'+guid+'/'+i['id']];interface_count+=1
            g.add((node,M.interfaceCandidata,surface));g.add((surface,M.paredeHospedeira,index[i['parede']]))
            g.add((surface,M.areaM2,Literal(Decimal(str(i['area_m2'])))))
            g.add((surface,M.qualificadaNoCriterio,Literal(i['qualificada_no_criterio'])))
            g.add((surface,M.sondasEstaveis,Literal(i['sondas_estaveis'])));geom(surface,i['wkt'])
            for key,prop in [('regularizacao_espaco_m',M.projecaoPlanarEspacoM),('regularizacao_parede_m',M.projecaoPlanarParedeM),('distancia_planos_m',M.distanciaPlanosM)]:
                g.add((surface,prop,Literal(Decimal(str(i.get(key,0))))))
        for patch in d['recortes_aberturas']:
            cut=B['recorte/'+guid+'/'+patch['id']]
            g.add((cut,M.interfaceFonte,B['interface/'+guid+'/'+patch['interface']]))
            g.add((cut,M.aberturaFonte,index[patch['abertura']]))
            g.add((cut,M.preenchimento,index[patch['preenchimento']]))
            g.add((cut,M.qualificadaNoCriterio,Literal(patch['qualificada_no_criterio'])));geom(cut,patch['wkt'])
    for r in document_rows:
        record=B['conferencia/'+r['ambiente']+'/'+r['guid']]
        g.add((record,RDF.type,M.ConferenciaDocumental));g.add((record,M.resultadoDoAmbiente,B['resultado/'+r['ambiente']]))
        g.add((record,M.elemento,index[r['guid']]))
        g.add((record,M.referenciaDocumental,Literal(r.get('pertence_ao_ambiente',''))))
        g.add((record,M.resultadoConferencia,Literal(r['resultado_conferencia'])))
    surface_audit=json.loads((resultados/'auditorias/Auditoria_Interfaces_v10.json').read_text(encoding='utf8'))
    for face in surface_audit['faces']:
        guid=face['ambiente'];node=B['resultado/'+guid]
        for atom in face['regioes_particionadas']:
            region=B['regiao/'+guid+'/'+atom['id']]
            g.add((region,RDF.type,M.RegiaoParticionada));g.add((node,M.regiaoParticionada,region))
            g.add((region,M.areaM2,Literal(Decimal(str(atom['area_m2'])))))
            g.add((region,M.classeConcorrencia,Literal(atom['classe'])));geom(region,atom['wkt'])
            for parent in atom['interfaces_fonte']:g.add((region,M.interfaceFonte,B['interface/'+guid+'/'+parent]))
            for wall in atom['paredes_fonte']:g.add((region,M.paredeHospedeira,index[wall]))
    volume_audit=json.loads((resultados/'auditorias/Contencao_Volumetrica_v10.json').read_text(encoding='utf8'))
    for row in volume_audit['pares']:
        auditnode=B['contencao/'+row['ambiente']+'/'+row['elemento']]
        g.add((auditnode,M.resultadoDoAmbiente,B['resultado/'+row['ambiente']]))
        g.add((auditnode,M.elemento,index[row['elemento']]));g.add((auditnode,M.estado,Literal(row['estado'])))
        if row.get('motivo'):g.add((auditnode,M.motivo,Literal(row['motivo'])))
    gaps=json.loads((resultados/'diagnosticos/Candidatos_Com_Folga_v10.json').read_text(encoding='utf8'))
    for row in gaps['candidatos']:
        candidate=B['folga/'+row['ambiente']+'/'+row['elemento']]
        g.add((candidate,RDF.type,M.CandidatoComFolga))
        g.add((candidate,M.resultadoDoAmbiente,B['resultado/'+row['ambiente']]))
        g.add((candidate,M.elemento,index[row['elemento']]))
        g.add((candidate,M.paredeHospedeira,index[row['parede']]))
        g.add((candidate,M.aberturaFonte,index[row['abertura']]))
        g.add((candidate,M.distanciaPlanosM,Literal(Decimal(str(row['distancia_m'])))))
        g.add((candidate,M.estado,Literal(row['estado'])))
    assert len(states)==41 and len(pairs)==batch['pares_ambiente_esquadria']
    assert interface_count==sum(1 for _ in g.objects(None,M.interfaceCandidata))
    addon=out/'Complemento_Multiambientes_v10.ttl';g.serialize(addon,format='turtle')
    assert set(Graph().parse(addon,format='turtle'))==set(g)
    full_path=out/'Notebook1_Arquitetura_Multiambientes_v10.ttl'
    prefix_hash=hashlib.sha256();prefix_bytes=0
    with zipfile.ZipFile(base_zip) as z,z.open('Notebook1_Arquitetura_Multiambientes_v09.ttl') as src,full_path.open('wb') as dest:
        while True:
            chunk=src.read(1024*1024)
            if not chunk:break
            prefix_hash.update(chunk);dest.write(chunk);prefix_bytes+=len(chunk)
        assert prefix_hash.hexdigest()==source['sha256_saida']
        dest.write(b'\n\n# Complemento multiambientes v10; fonte anterior preservada.\n');dest.write(addon.read_bytes())
    del g;gc.collect()
    print('Reabrindo grafo completo v10 para consultar todos os espaços...',flush=True)
    full=Graph().parse(full_path,format='turtle')
    query='''PREFIX mu: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/aprimoramento#>
SELECT ?resultado ?ambiente ?nome ?estado ?quantidade ?esquadria WHERE {
 ?resultado a mu:ResultadoPorAmbiente; mu:ambiente ?ambiente; mu:nome ?nome; mu:estado ?estado .
 OPTIONAL {?resultado mu:quantidadeEsquadrias ?quantidade}
 OPTIONAL {?resultado mu:esquadriaAssociada ?esquadria}
} ORDER BY ?nome ?resultado ?esquadria'''
    rows=list(full.query(query));found_states={};found_pairs=set()
    inverse={str(v):k for k,v in index.items()}
    for r in rows:
        guid=inverse[str(r.ambiente)];found_states[guid]=str(r.estado)
        if str(r.estado).startswith('inconclusivo_'):assert r.quantidade is None and r.esquadria is None
        if r.esquadria is not None:found_pairs.add((guid,inverse[str(r.esquadria)]))
    assert found_states==states and found_pairs==pairs
    (out/'Consultar_Todos_Ambientes_v10.rq').write_text(query,encoding='utf8')
    with (out/'Consulta_Todos_Ambientes_v10.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.writer(fp);w.writerow([str(v) for v in rows[0].labels]);w.writerows([[str(v) if v is not None else '' for v in r] for r in rows])
    report={'triplas_base_v09':source['triplas_uniao_v09'],'triplas_uniao_v10':len(full),'espacos_consultados':len(found_states),
       'pares_ambiente_esquadria_consultados':len(found_pairs),'interfaces_registradas':interface_count,'regioes_particionadas':surface_audit['regioes_particionadas'],
       'inconclusivos_sem_contagem_falsa_zero':sum(s.startswith('inconclusivo_') for s in found_states.values()),
       'base_v09_preservada_bytes':prefix_bytes,'sha256_base_v09':prefix_hash.hexdigest(),'sha256_saida':sha(full_path),
       'grafo_reaberto_e_consultado':True,'limite':'Propriedades mu: identificam o resultado desta revisão; não substituem registros históricos nem certificam completude arquitetônica.'}
    del full;gc.collect()
    save(out/'Registro_RDF_Multiambientes_v10.json',report)
    with zipfile.ZipFile(out/'Notebook1_Grafo_Multiambientes_v10.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(full_path,full_path.name);z.write(addon,addon.name)
    print(json.dumps(report,ensure_ascii=False,indent=2));return report
