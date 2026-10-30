"""Entrada única para o perfil da cozinha; sem usar a referência documental.

IFC2SB parcial: Fichter et al., DOI 10.26868/25222708.2021.30156.
Faces/interfaces: Kiavarz et al., DOI 10.3390/buildings13020350.
CGAL reaproveitado: Krijnen et al., DOI 10.46421/2706-6568.37.2020.paper008.
Lilis opcional: DOI 10.1016/j.autcon.2026.106840, adaptação parcial.
Orquestração, classificação de saídas e ligações acessórias são do estudo.
"""
from pathlib import Path
import json,hashlib,zipfile,time
import numpy as np
from rdflib import Graph,Namespace,Literal,URIRef,RDF

ROOM='3UFjAT4k55zg_Pqo6VMw5l'
IFC_SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
C=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/consolidado#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/consolidado-v08/')
OLD=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/id/ifc2sb-python-v01/')
P=Namespace('http://www.w3.org/ns/prov#')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def executar_ambiente(ifc_path,ambiente,entradas,saida,comparar_lilis=False,inventario_preparado=None):
    """Reexecuta IFC2SB e Kiavarz; reaproveita CGAL fixado ao mesmo IFC.

    Perfil disponível: cozinha FNDE ARQ-DTV R03. Outros GUIDs exigem novo
    perfil e ensaios; são recusados antes do processamento, sem resultados vazios.
    A referência documental NÃO é argumento nem entrada desta função.
    """
    start=time.perf_counter();ifc_path=Path(ifc_path);entradas=Path(entradas);saida=Path(saida)
    if ambiente!=ROOM:raise ValueError('Perfil validado somente para a cozinha FNDE R03; outro ambiente requer preparação e avaliação próprias.')
    if sha(ifc_path)!=IFC_SHA:raise ValueError('IFC diferente do perfil de entrada; não reutilizar avaliações CGAL.')
    manifest=json.loads((entradas/'Manifesto_Entradas.json').read_text(encoding='utf8'))
    for rel,digest in manifest['arquivos'].items():
        if sha(entradas/rel)!=digest:raise ValueError('Entrada alterada: '+rel)
    saida.mkdir(parents=True,exist_ok=True);logs=[]
    from piloto import run as recortar
    raw=saida/'ifc2sb';print('ETAPA 1: reexecutar recortes IFC2SB no IFC original.',flush=True)
    pilot=recortar(ifc_path,raw)
    if pilot['falhas']:raise RuntimeError('Falhas de processamento IFC2SB; consultar Resultado_Piloto.json.')
    assert pilot['ambiente']==ambiente
    with zipfile.ZipFile(raw/'Geometrias_BRep_e_Controles.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in raw.glob('*.brep'):z.write(p,'geometrias/'+p.name)
    logs.append({'etapa':'IFC2SB parcial','modo':'reexecutado','paredes_examinadas':pilot['paredes_examinadas'],'paredes_candidatas':len(pilot['paredes'])})
    from pipeline_hibrido import run as combinar
    from exportar_hibrido import run as exportar
    core=saida/'interfaces';print('ETAPA 2: interfaces e recortes locais; sinais CGAL reaproveitados.',flush=True)
    result=combinar(ifc_path,raw,entradas/'cgal',core)
    registro=exportar(core/'Resultado_Hibrido_Kiavarz_v01.json',entradas/'Grafo_CGAL_v05.ttl',core)
    logs.append({'etapa':'Kiavarz adaptado','modo':'reexecutado','interfaces':len(result['interfaces'])})
    logs.append({'etapa':'Krijnen/CGAL parcial','modo':'resultados anteriores verificados por hash; motor não reexecutado'})
    from inventariar_projeto import run as inventariar
    inventory_dir=saida/'inventario'
    if inventario_preparado:
        import shutil
        source=Path(inventario_preparado)
        inventory=json.loads((source/'Inventario_Projeto_Cozinha.json').read_text(encoding='utf8'))
        assert inventory['ifc_sha256']==IFC_SHA and inventory['ambiente']==ambiente
        shutil.copytree(source,inventory_dir,dirs_exist_ok=True)
        inventory_mode='inventário desta revisão reaproveitado; mesmo IFC/ambiente'
    else:
        print('ETAPA 3: inventário independente de todas as aberturas e esquadrias.',flush=True)
        inventory=inventariar(ifc_path,ambiente,inventory_dir);inventory_mode='reexecutado'
    if inventory['erros']:raise RuntimeError('Inventário incompleto; consultar erros antes de classificar cobertura.')
    logs.append({'etapa':'Inventário de cobertura','modo':inventory_mode,**inventory['resumo']})
    associated={r['preenchimento']:r for r in result['recortes_aberturas'] if r['qualificada_no_criterio']}
    esquadrias=[dict(r,interfaces=sorted({p['interface'] for p in result['recortes_aberturas'] if p['preenchimento']==guid})) for guid,r in associated.items() if r['classe_preenchimento'] in ['IfcDoor','IfcWindow']]
    auxiliary=[r for r in associated.values() if r['classe_preenchimento'] not in ['IfcDoor','IfcWindow']]
    internals=[r for r in inventory['preenchimentos_proximos'] if r['classe']=='IfcWall' and r.get('todos_vertices_dentro_ou_no_limite') and r.get('algum_vertice_interno')]
    # Componentes sem IfcRelFillsElement não são forçados a ser preenchimentos.
    # Associação alternativa por caixas e distância: candidata, sem certificar função.
    typed={r['guid']:r for r in inventory['esquadrias_ifc']};accessories=[]
    for e in inventory['esquadrias_ifc']:
        if not e['proxima_bbox_60cm'] or e['aberturas_declaradas']:continue
        nearby=[]
        for prediction in esquadrias:
            target=typed[prediction['preenchimento']]
            a,b=np.array(e['min_xyz_m']),np.array(e['max_xyz_m'])
            c,d=np.array(target['min_xyz_m']),np.array(target['max_xyz_m'])
            gap=np.maximum(np.maximum(a-d,c-b),0)
            distance=float(np.linalg.norm(gap))
            # Centro nas duas direções dominantes deve permanecer no contorno
            # da esquadria-alvo; eixo fino da própria esquadria define o plano.
            thin=int(np.argmin(d-c));axes=[i for i in range(3) if i!=thin]
            center=(a+b)/2
            within=all(c[i]-.02<=center[i]<=d[i]+.02 for i in axes)
            if within and distance<=.25:nearby.append({'preenchimento_alvo':target['guid'],'abertura_alvo':prediction['abertura'],'distancia_caixas_m':distance})
        if nearby:accessories.append(dict(e,associacoes_candidatas=nearby,estado='componente_sem_FillsVoids; vinculo_geometrico_candidato; funcao_pendente'))
    final_graph=core/'Cozinha_Interfaces_Hibridas_IFC2SB_Krijnen_Kiavarz_v01.ttl'
    lilis_summary=None
    if comparar_lilis:
        from ensaio_lilis import run as testar_lilis
        from exportar_lilis import run as exportar_lilis
        print('ETAPA OPCIONAL: comparação Lilis; não modifica decisões do núcleo.',flush=True)
        lilis=saida/'comparacao_lilis'
        comparison=testar_lilis(ifc_path,core/'Resultado_Hibrido_Kiavarz_v01.json',entradas/'Triagem_Lilis_v06.json',lilis)
        exportar_lilis(lilis/'Resultado_Lilis_Hibrido_v01.json',final_graph,lilis)
        final_graph=lilis/'Cozinha_Hibrido_Com_Ensaio_Lilis_v01.ttl';lilis_summary=comparison['resumo']
        logs.append({'etapa':'Lilis parcial','modo':'comparação opcional reexecutada; sem alterar esquadrias do núcleo'})
    result_summary={'ambiente':ambiente,'nome':result['nome'],'ifc_sha256':IFC_SHA,'etapas':logs,
       'interfaces_delimitadoras':result['interfaces'],'esquadrias_associadas':esquadrias,
       'outros_preenchimentos_associados':auxiliary,'elementos_internos_candidatos':internals,
       'componentes_sem_FillsVoids_candidatos':accessories,'comparacao_lilis':lilis_summary,
       'resumo':{'interfaces':len(result['interfaces']),'paredes_com_interface':len({i['parede'] for i in result['interfaces']}),
         'esquadrias_distintas':len(esquadrias),'outros_preenchimentos':len(auxiliary),'elementos_internos_candidatos':len(internals),'componentes_sem_FillsVoids':len(accessories)},
       'limites':['Perfil único cozinha; não generalizado aos 41 ambientes.','Vértices e caixas fornecem candidatos, não função ou contenção integral certificada.',
         'A conferência documental é executada depois, sem alimentar o algoritmo.','Classes IFC preservadas; IfcWall não se transforma em porta ou janela.',
         'As relações antigas permanecem históricas; consultar o vocabulário consolidado para a saída atual.'],
       'ifc_original_preservado':sha(ifc_path)==IFC_SHA,'segundos':time.perf_counter()-start}
    g=Graph().parse(final_graph,format='turtle');g.bind('con',C);g.bind('cid',B)
    g.parse(Path(__file__).with_name('Vocabulario_Consolidado.ttl'),format='turtle')
    run_node=B['execucao'];room=OLD[ambiente]
    g.add((run_node,RDF.type,P.Activity));g.add((run_node,C.sha256IFC,Literal(IFC_SHA)))
    g.add((run_node,C.perfil,Literal('cozinha-FNDE-ARQ-DTV-R03')))
    for e in esquadrias:
        g.add((room,C.esquadriaAssociada,OLD[e['preenchimento']]))
        g.add((OLD[e['preenchimento']],C.aberturaFonte,OLD[e['abertura']]))
    for e in auxiliary:g.add((room,C.outroPreenchimentoAssociado,OLD[e['preenchimento']]))
    for e in internals:
        g.add((room,C.elementoInternoCandidato,OLD[e['guid']]))
        g.add((OLD[e['guid']],C.criterioLocalizacao,Literal('Vértices IN/ON, com pelo menos um IN; tolerância 1e-5 m; não certifica contenção integral.')))
    for e in accessories:
        node=OLD[e['guid']];g.add((room,C.componenteSemFillsVoidsCandidato,node))
        g.add((node,C.classeIFC,Literal(e['classe'])));g.add((node,C.nomeIFC,Literal(e['nome'])))
        for target in e['associacoes_candidatas']:g.add((node,C.proximoDePreenchimento,OLD[target['preenchimento_alvo']]))
    target=saida/'Complemento_Hibrido_Consolidado_v08.ttl';g.serialize(target,format='turtle')
    assert set(Graph().parse(target,format='turtle'))==set(g)
    save(saida/'Resultado_Consolidado_Cozinha_v08.json',result_summary)
    print('ROTINA CONCLUÍDA:',json.dumps(result_summary['resumo'],ensure_ascii=False),flush=True)
    return result_summary
