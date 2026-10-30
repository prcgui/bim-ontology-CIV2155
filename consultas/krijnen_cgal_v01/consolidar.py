"""Integra evidências do ensaio CGAL ao RDF e compara com o piloto anterior.

Krijnen et al. (2020), §3.3: Nef/Minkowski/interseção (não limites completos).
Zhang et al. (2018), DOI 10.3233/SW-180297: padrão GEOM para geometria RDF.
RDFLib: https://rdflib.readthedocs.io/en/stable/intro_to_graphs/
Predicados de avaliação e critérios de comparação são específicos deste estudo.
Não converte interseção de volumes expandidos em adjacência BOT confirmada.
"""
from pathlib import Path
from decimal import Decimal
import json,csv,hashlib,collections,html,math
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,XSD
C=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/krijnen-piloto#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/krijnen-piloto-v01/')
OLD=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/ifc2sb-python-v01/')
G=Namespace('http://bimsparql.org/geometry#');P=Namespace('http://www.w3.org/ns/prov#')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def off_wkt(path):
    words=Path(path).read_text().split();assert words[0]=='OFF'
    nv,nf=int(words[1]),int(words[2]);i=4
    vertices=[tuple(map(float,words[i+3*k:i+3*k+3])) for k in range(nv)];i+=3*nv
    assert all(math.isfinite(x) for v in vertices for x in v)
    polys=[]
    for _ in range(nf):
        n=int(words[i]);i+=1;indices=list(map(int,words[i:i+n]));i+=n
        points=[vertices[k] for k in indices];points.append(points[0])
        polys.append('(('+', '.join(' '.join(format(x,'.17g') for x in v) for v in points)+'))')
    return 'MULTIPOLYGON Z ('+', '.join(polys)+')'
def consolidate(execution_root,base_rdf,out):
    er=Path(execution_root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    ex=json.loads((er/'Execucao.json').read_text(encoding='utf8'));cfg=json.loads((er/'entrada/Registro_Entrada.json').read_text(encoding='utf8'))
    control=json.loads((er/'Controles.json').read_text(encoding='utf8'))
    expected_controls=14 if ex.get('preparacao_componentes') else 12
    assert control['aprovados']==control['total']==expected_controls
    B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/krijnen-piloto-'+('v02/' if expected_controls==14 else 'v01/'))
    assert ex['estado']=='concluido' and len(ex['casos'])==68 and ex['entradas_off_preservadas']
    assert sha(er/'entrada/Registro_Entrada.json')==ex['sha256_entrada']
    for obj in cfg['objetos']:assert sha(er/'entrada'/obj['arquivo'])==obj['sha256_off']
    original_hash=sha(base_rdf);g=Graph().parse(base_rdf,format='turtle');base=set(g)
    for prefix,ns in [('kr',C),('krid',B),('geom',G),('prov',P)]:g.bind(prefix,ns)
    frame=B['referencial-projeto-metros'];activity=B['ensaio'];room=OLD[cfg['objetos'][0]['guid']]
    g.add((activity,RDF.type,P.Activity));g.add((activity,P.wasDerivedFrom,URIRef(ex['artigo'])))
    g.add((activity,P.used,URIRef(ex['fonte'])));g.add((activity,C.sha256Entrada,Literal(ex['sha256_entrada'])))
    g.add((activity,RDFS.comment,Literal(ex['natureza'],lang='pt')))
    g.add((frame,RDFS.label,Literal('Referencial cartesiano do projeto IFC em metros; não CRS84.',lang='pt')))
    def geometry(node,path,role):
        g.add((node,G.asBody,Literal(off_wkt(path))));g.add((node,C.coordinateReference,frame))
        g.add((node,C.unit,URIRef('http://qudt.org/vocab/unit/M')));g.add((node,C.papelGeometria,Literal(role)))
        g.add((node,C.sha256,Literal(sha(path))))
    for obj in cfg['objetos']:
        node=OLD[obj['guid']];rep=B['malha/'+obj['codigo']]
        g.add((node,C.geometriaDoEnsaio,rep));g.add((node,C.globalId,Literal(obj['guid'])))
        g.add((node,RDFS.label,Literal(obj['nome'] or obj['guid'])))
        geometry(rep,er/'entrada'/obj['arquivo'],'malha triangular da entrada; aberturas não subtraídas')
    measurements={(c['codigo'],c['eps_m']):c for c in ex['casos']};rows=[]
    diag_path=er/'Diagnostico_Solidos_OCP.json'
    diag={r['guid']:r for r in json.loads(diag_path.read_text(encoding='utf8'))} if diag_path.exists() else {}
    for obj in cfg['objetos'][1:]:
        r={'codigo':obj['codigo'],'guid':obj['guid'],'nome':obj['nome'],
          'area_coincidente_piloto_m2':obj['area_coincidente_piloto_m2'],
          'volume_ocp_bruto_m3':obj['volume_comum_ocp_bruto_m3']}
        for eps,label in [(0.,'e0'),(1e-5,'e1e5')]:
            m=measurements[(obj['codigo'],eps)];x=m.get('resultado');node=B['avaliacao/'+obj['codigo']+'/'+label]
            g.add((node,RDF.type,C.AvaliacaoGeometrica));g.add((node,C.ambienteExaminado,room))
            g.add((node,C.paredeExaminada,OLD[obj['guid']]));g.add((node,C.paddingMeiaArestaM,Literal(Decimal(str(eps)))))
            g.add((node,C.estadoExecucao,Literal(m['estado'])));g.add((node,P.wasGeneratedBy,activity))
            g.add((node,C.decisaoArquitetonica,Literal('pendente; sinal geométrico não confirma delimitação')))
            r['estado_'+label]=m['estado'];r['nao_vazio_'+label]=x['nao_vazio'] if x else None
            r['volume_3d_'+label]=x['volume_3d_presente'] if x else None
            r['volume_m3_'+label]=x['volume_m3'] if x else None
            r['segundos_'+label]=m.get('segundos')
            if x:
                g.add((node,C.intersecaoNaoVazia,Literal(x['nao_vazio'])));g.add((node,C.volume3dPresente,Literal(x['volume_3d_presente'])))
                # Decimal preserva os dígitos do JSON: Turtle do RDFLib arredonda
                # doubles em notação curta. Não altera precisão da medição CGAL.
                if x['volume_m3'] is not None:g.add((node,C.volumeComumM3,Literal(Decimal(str(x['volume_m3'])))))
                part=er/'intersecoes'/(obj['codigo']+'_'+label+'.off')
                if part.exists():
                    shape=B['intersecao/'+obj['codigo']+'/'+label];g.add((node,C.geometriaResultado,shape))
                    geometry(shape,part,'interseção dos volumes expandidos' if eps else 'interseção dos sólidos triangulados sem expansão')
            elif m.get('motivo'):g.add((node,C.motivo,Literal(m['motivo'])))
        r['valor_ocp_original_registrado_m3']=r['volume_ocp_bruto_m3']
        r['solidos_brep_entrada']=diag.get(obj['guid'],{}).get('solidos_brep_entrada')
        if r['solidos_brep_entrada']==0:r['volume_ocp_bruto_m3']=None
        if r['estado_e0']!='concluido' or r['estado_e1e5']!='concluido':status='inconclusivo_motor_ou_entrada'
        elif (r['volume_m3_e0'] or 0)>1e-8:status='intersecao_volumetrica_sem_padding'
        elif r['volume_3d_e0'] and r['volume_m3_e0'] is None:status='intersecao_3d_nao_quantificada'
        elif r['nao_vazio_e1e5']:status='candidato_por_contato_ou_tolerancia'
        else:status='sem_intersecao_neste_criterio'
        r['interpretacao']=status;r['sem_confirmacao_arquitetonica']=True
        r['novo_sinal_vs_superficie_piloto']=r['area_coincidente_piloto_m2']<=1e-8 and r['nao_vazio_e1e5'] is True
        r['diferenca_volume_nef_ocp_m3']=r['volume_m3_e0']-r['volume_ocp_bruto_m3'] if r['volume_m3_e0'] is not None and r['volume_ocp_bruto_m3'] is not None else None
        rows.append(r)
    assert base.issubset(set(g)) and sha(base_rdf)==original_hash
    rdf=out/'Cozinha_IFC2SB_Com_Avaliacoes_CGAL_v01.ttl';g.serialize(rdf,format='turtle')
    reread=Graph().parse(rdf,format='turtle')
    assert set(reread)==set(g),'Roundtrip RDF mudou termos'
    assessments=set(reread.subjects(RDF.type,C.AvaliacaoGeometrica));assert len(assessments)==68
    for a in assessments:
        assert len(list(reread.objects(a,C.ambienteExaminado)))==1
        assert len(list(reread.objects(a,C.paredeExaminada)))==1
    BOT=Namespace('https://w3id.org/bot#')
    assert not any(p in [BOT.adjacentElement,BOT.intersectingElement] for s,p,o in set(g)-base)
    with (out/'Comparacao_Paredes_IFC2SB_CGAL_v01.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'paredes':len(rows),'ensaios':len(ex['casos']),'controles':expected_controls,
      'estados_execucao':dict(collections.Counter(c['estado'] for c in ex['casos'])),
      'interpretacoes':dict(collections.Counter(r['interpretacao'] for r in rows)),
      'novos_sinais_vs_superficies_piloto':[r['codigo'] for r in rows if r['novo_sinal_vs_superficie_piloto']],
      'intersecoes_sem_padding':sum(r['nao_vazio_e0'] is True for r in rows),
      'intersecoes_com_padding':sum(r['nao_vazio_e1e5'] is True for r in rows),
      'paredes_com_superficie_coincidente_piloto':sum(r['area_coincidente_piloto_m2']>1e-8 for r in rows),
      'volume_ocp_indisponivel_sem_solidos':[r['codigo'] for r in rows if r['solidos_brep_entrada']==0],
      'maior_diferenca_volume_nef_ocp_m3':max((abs(r['diferenca_volume_nef_ocp_m3']) for r in rows if r['diferenca_volume_nef_ocp_m3'] is not None),default=None),
      'triplas_entrada':len(base),'triplas_saida':len(g),'avaliacoes_rdf':68,'rdf_entrada_preservado':sha(base_rdf)==original_hash,
      'sha256_rdf_entrada':original_hash,'sha256_rdf_saida':sha(rdf),'sha256_ifc_original':cfg['sha256_ifc'],
      'comparacao':'Sinais geométricos de natureza distinta; maior contagem não demonstra maior precisão. Sem padrão-ouro arquitetônico.',
      'contribuicao':'Módulo opcional de avaliação geométrica com tolerância e coordenadas integrado ao RDF do piloto; não gera limites semânticos automaticamente.',
      'nao_implementado':'IfcConvert/CGAL de 2020 completo, achatamento de superfícies, portas/janelas pelo método de 2020, lajes/revestimentos e generalização aos 41 espaços.'}
    save(out/'Resumo_Comparacao_Krijnen_v01.json',summary)
    save(out/'Comparacao_Paredes_IFC2SB_CGAL_v01.json',rows)
    query='''PREFIX kr: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/krijnen-piloto#>
SELECT ?parede ?eps ?naoVazio ?volume ?estado WHERE {
 ?a a kr:AvaliacaoGeometrica; kr:paredeExaminada ?parede;
    kr:paddingMeiaArestaM ?eps; kr:estadoExecucao ?estado .
 OPTIONAL { ?a kr:intersecaoNaoVazia ?naoVazio }
 OPTIONAL { ?a kr:volumeComumM3 ?volume }
} ORDER BY ?parede ?eps'''
    (out/'Consultar_Avaliacoes_CGAL.rq').write_text(query,encoding='utf8')
    assert len(list(reread.query(query)))==68
    save(out/'Verificacao_Integracao_RDF.json',{'controles_aprovados':expected_controls,'avaliacoes_consultadas':68,'roundtrip_rdf':True,'triplas_anteriores_preservadas':True,'novas_adjacencias_bot_confirmadas':0})
    print(json.dumps(summary,ensure_ascii=False,indent=2));return summary
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('execucao');p.add_argument('rdf_base');p.add_argument('saida')
    a=p.parse_args();consolidate(a.execucao,a.rdf_base,a.saida)
