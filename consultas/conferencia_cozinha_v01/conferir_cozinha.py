"""Conferência da CQ2, cozinha: dados IFC, cadeias RDF e localização 3D.

Código específico de inspeção. Métodos reutilizados do Notebook 1 v03:
Lilis et al. (2025), §§3.2–3.4/Fig.4, DOI 10.1016/j.autcon.2025.106081;
Huitzil et al. (2024), DOI 10.1016/j.jii.2024.100731; geometria GEOM
conforme Zhang et al. (2018), DOI 10.3233/SW-180297.
IfcRelVoidsElement/IfcRelFillsElement são relações declaradas (IFC4).
O corte horizontal é somente visualização das malhas, não classificador.
Não modifica IFC/RDF, corrige polígonos ou cria associação porta–cômodo.
"""
from pathlib import Path
import json,csv,hashlib,os,sys
from collections import Counter
import numpy as np
import ifcopenshell
import ifcopenshell.util.element
from shapely.errors import GEOSException
from rdflib import Graph,RDF
from pipeline_arquitetura import BOT,CIV,GEOM,PROPS,EXPECTED_IFC,save_json,save_csv
from geometria_relacoes import aabb_candidate,surfaces,solid,classify_pair,NEAR_M,VOLUME_EPS_M3

KITCHEN='3UFjAT4k55zg_Pqo6VMw5l'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inspect(ifc_path,results_path,cache_path,out):
    ifc_path=Path(ifc_path);results_path=Path(results_path);cache_path=Path(cache_path);out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    assert sha(ifc_path)==EXPECTED_IFC,'IFC não corresponde à fonte selecionada'
    metadata=json.loads((results_path/'rdf/registro_rdf.json').read_text(encoding='utf8'))
    ttl=results_path/'rdf/arquitetura_enriquecida.ttl';original_rdf_hash=sha(ttl)
    assert original_rdf_hash==metadata['sha256_ttl'],'RDF diferente do resultado registrado'
    cache=json.loads((cache_path/'inventario_geometria.json').read_text(encoding='utf8'))
    assert cache['sha256_ifc']==EXPECTED_IFC
    records={r['guid']:r for r in cache['entidades']}
    model=ifcopenshell.open(str(ifc_path));g=Graph().parse(str(ttl),format='turtle')
    guid_to_uri={str(o):s for s,o in g.subject_objects(PROPS.globalIdIfcRoot_attribute_simple)}
    uri_to_guid={s:guid for guid,s in guid_to_uri.items()}
    room=model.by_guid(KITCHEN);ru=guid_to_uri[KITCHEN]
    qualified=sorted({uri_to_guid[o] for o in g.objects(ru,BOT.adjacentElement)})
    n1=json.loads((results_path/'relacoes/relacoes_geometricas.json').read_text(encoding='utf8'))
    saved_pairs={r['parede']:r for r in n1['pares'] if r['ambiente']==KITCHEN}
    save_json(out/'relacoes_origem_cozinha.json',[r for r in n1['pares'] if r['ambiente']==KITCHEN])
    assert set(qualified)=={k for k,r in saved_pairs.items() if r['status']=='adjacencia_geometrica_no_limiar_numerico'}
    loaded={}
    def mesh(guid):
        if guid not in loaded:
            r=records[guid];path=cache_path/r['cache'];assert sha(path)==r['sha256_npz']
            z=np.load(path);v=z['vertices'];f=z['faces']
            if r['orientacao_consistente'] and r['volume_assinado_m3']<0:f=f[:,[0,2,1]]
            loaded[guid]=(v,f,surfaces(v,f),solid(v,f))
        return loaded[guid]
    vr,fr,sr,mr=mesh(KITCHEN)
    def relation_to_room(guid):
        r=records.get(guid)
        if not r or 'cache' not in r:return {'teste_3d':'sem_malha','volume_comum_m3':None,'area_contato_m2':None}
        path=cache_path/r['cache'];assert sha(path)==r['sha256_npz'],'Cache alterado: '+guid
        z=np.load(path);v=z['vertices'];f=z['faces']
        gap=np.maximum(0,np.maximum(vr.min(0),v.min(0))-np.minimum(vr.max(0),v.max(0)))
        if not aabb_candidate(vr,v):
            return {'teste_3d':'fora_do_filtro_espacial_2mm','volume_comum_m3':0.,'area_contato_m2':0.,
                    'separacao_caixas_XYZ_m':gap.tolist()}
        try:
            va,fa,sa,ma=mesh(guid)
            volume=None
            if mr is not None and ma is not None:
                common=mr^ma
                if str(common.status()).endswith('NoError'):volume=max(0.,float(common.volume()))
            contact=classify_pair(vr,fr,va,fa,sr,sa,mr,ma)
            return {'teste_3d':contact['status'] if contact else 'sem_contato_de_faces_no_criterio',
                    'volume_comum_m3':volume,'area_contato_m2':contact['strict_area_m2'] if contact else 0.,
                    'intersecao_volumetrica_acima_limiar':None if volume is None else volume>VOLUME_EPS_M3,
                    'separacao_caixas_XYZ_m':gap.tolist()}
        except (ValueError,GEOSException) as ex:
            # Falha registrada, sem completar a relação por inferência.
            return {'teste_3d':'indeterminado_por_falha_geometrica','volume_comum_m3':None,'area_contato_m2':None,'erro':str(ex)}

    wall_codes={guid:'P'+str(i+1).zfill(2) for i,guid in enumerate(qualified)}
    # Percurso de relações declaradas no IFC: nenhuma busca por palavras no nome.
    voids={};fills={}
    for rel in model.by_type('IfcRelVoidsElement'):voids.setdefault(rel.RelatingBuildingElement.GlobalId,[]).append(rel)
    for rel in model.by_type('IfcRelFillsElement'):fills.setdefault(rel.RelatingOpeningElement.GlobalId,[]).append(rel)
    chains=[];tuples_ifc=set()
    for wall_guid in qualified:
        rels=sorted(voids.get(wall_guid,[]),key=lambda r:r.RelatedOpeningElement.GlobalId)
        if not rels:tuples_ifc.add((wall_guid,None,None))
        for rel in rels:
            opening=rel.RelatedOpeningElement
            fs=fills.get(opening.GlobalId,[])
            for fill in fs or [None]:
                item=fill.RelatedBuildingElement if fill else None
                tuples_ifc.add((wall_guid,opening.GlobalId,item.GlobalId if item else None))
                chain={'parede_codigo':wall_codes[wall_guid],'parede_guid':wall_guid,'parede_step':rel.RelatingBuildingElement.id(),
                       'abertura_guid':opening.GlobalId,'abertura_step':opening.id(),'rel_voids_step':rel.id(),
                       'preenchimento_guid':item.GlobalId if item else None,'preenchimento_step':item.id() if item else None,
                       'classe_preenchimento':item.is_a() if item else None,'nome_preenchimento':item.Name if item else None,
                       'rel_fills_step':fill.id() if fill else None,'atribuicao_arquitetonica_ao_ambiente':'não demonstrada por esta cadeia'}
                chain['abertura_vs_cozinha']=relation_to_room(opening.GlobalId)
                if item:chain['preenchimento_vs_cozinha']=relation_to_room(item.GlobalId)
                chains.append(chain)
    for i,r in enumerate(chains):r['codigo']='A'+str(i+1).zfill(2)
    query='''PREFIX bot: <https://w3id.org/bot#>
PREFIX civ: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/arquitetura#>
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
SELECT DISTINCT ?paredeGUID ?aberturaGUID ?preenchimentoGUID WHERE {
 ?ambiente props:globalIdIfcRoot_attribute_simple "3UFjAT4k55zg_Pqo6VMw5l";bot:adjacentElement ?parede.
 ?parede props:globalIdIfcRoot_attribute_simple ?paredeGUID.
 OPTIONAL { ?parede civ:hasOpening ?abertura.?abertura props:globalIdIfcRoot_attribute_simple ?aberturaGUID.
 OPTIONAL { ?abertura civ:hasFilling ?preenchimento.?preenchimento props:globalIdIfcRoot_attribute_simple ?preenchimentoGUID. } }
} ORDER BY ?paredeGUID ?aberturaGUID'''
    (out/'consulta_conferencia_cozinha.rq').write_text(query,encoding='utf8')
    rdf_rows=[tuple(str(v) if v is not None else None for v in r) for r in g.query(query)]
    tuples_rdf=set(rdf_rows)
    assert tuples_rdf==tuples_ifc,{'so_IFC':list(tuples_ifc-tuples_rdf),'so_RDF':list(tuples_rdf-tuples_ifc)}
    save_csv(out/'cadeias_IFC_RDF.csv',[{'parede_guid':a,'abertura_guid':b,'preenchimento_guid':c} for a,b,c in rdf_rows],['parede_guid','abertura_guid','preenchimento_guid'])
    # Examina todas as aberturas para identificar possíveis omissões do filtro de paredes.
    all_openings=[]
    for opening in model.by_type('IfcOpeningElement'):
        rel=relation_to_room(opening.GlobalId)
        if rel['teste_3d']=='fora_do_filtro_espacial_2mm':continue
        host=next((r.RelatingBuildingElement for r in opening.VoidsElements),None)
        all_openings.append({'abertura_guid':opening.GlobalId,'abertura_STEP':opening.id(),'hospedeiro_guid':host.GlobalId if host else None,
            'classe_hospedeiro':host.is_a() if host else None,'hospedeiro_na_lista_dez_paredes':bool(host and host.GlobalId in qualified),**rel})
        all_openings[-1]['preenchimentos_IFC']=[{'guid':r.RelatedBuildingElement.GlobalId,'classe':r.RelatedBuildingElement.is_a(),'nome':r.RelatedBuildingElement.Name} for r in fills.get(opening.GlobalId,[])]
    wall_rows=[]
    for wall in model.by_type('IfcWall'):
        r=records.get(wall.GlobalId)
        if not r or 'cache' not in r:continue
        if np.any(np.minimum(r['bbox_max'],vr.max(0))+NEAR_M<np.maximum(r['bbox_min'],vr.min(0))):continue
        p=saved_pairs.get(wall.GlobalId,{})
        others=sorted({records[uri_to_guid[s]].get('long_name') or uri_to_guid[s] for s in g.subjects(BOT.adjacentElement,guid_to_uri[wall.GlobalId]) if s!=ru})
        wall_rows.append({'codigo':wall_codes.get(wall.GlobalId,'C'+str(len(wall_rows)+1).zfill(2)),'guid':wall.GlobalId,'step':wall.id(),'nome':wall.Name,
            'situacao_N1':p.get('status','sem_contato_de_faces_no_criterio'),'area_estrita_m2':p.get('strict_area_m2'),
            'volume_intersecao_m3':p.get('intersection_volume_m3'),'outros_ambientes_com_aresta_RDF':'; '.join(others),
            'aberturas_declaradas_no_IFC':len(voids.get(wall.GlobalId,[]))})
    # Recorte por cópia de triplas existentes; não acrescenta fatos ao grafo.
    selected={ru}|{guid_to_uri[r['guid']] for r in wall_rows}
    for r in all_openings:
        for guid in [r['abertura_guid'],r['hospedeiro_guid']]+[i['guid'] for i in r['preenchimentos_IFC']]:
            if guid in guid_to_uri:selected.add(guid_to_uri[guid])
    for r in chains:
        for guid in [r['abertura_guid'],r['preenchimento_guid']]:
            if guid in guid_to_uri:selected.add(guid_to_uri[guid])
    for subject in list(selected):selected.update(g.objects(subject,GEOM.hasGeometry))
    for e in g.subjects(RDF.type,CIV.GeometricRelationEvidence):
        if g.value(e,RDF.subject)==ru:
            selected.add(e);selected.update(g.objects(e,CIV.contactGeometry))
    cut=Graph()
    for prefix,uri in g.namespaces():cut.bind(prefix,uri)
    for subject in selected:
        for triple in g.triples((subject,None,None)):cut.add(triple)
    assert all(t in g for t in cut)
    cut.serialize(out/'cozinha_extrato_RDF_existente.ttl',format='turtle')
    save_csv(out/'paredes_candidatas_cozinha.csv',wall_rows)
    flat=[]
    for row in chains:
        flat.append({k:v for k,v in row.items() if k not in ['abertura_vs_cozinha','preenchimento_vs_cozinha']}|{
          'abertura_teste_3d':row['abertura_vs_cozinha']['teste_3d'],
          'abertura_volume_comum_m3':row['abertura_vs_cozinha']['volume_comum_m3'],
          'abertura_area_contato_m2':row['abertura_vs_cozinha']['area_contato_m2'],
          'preenchimento_teste_3d':row.get('preenchimento_vs_cozinha',{}).get('teste_3d')})
    save_csv(out/'aberturas_e_preenchimentos_conferencia.csv',flat)
    save_csv(out/'todas_aberturas_preselecionadas.csv',[{k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items()} for r in all_openings])
    summary={'cozinha_GUID':KITCHEN,'cozinha_STEP':room.id(),'cozinha_nome':room.LongName,'sha256_IFC':EXPECTED_IFC,
        'sha256_RDF':original_rdf_hash,'paredes_preselecionadas':len(wall_rows),'paredes_no_RDF':len(qualified),
        'linhas_consulta_com_optional':len(tuples_rdf),'linhas_com_abertura':len(chains),
        'preenchimentos_por_classe':dict(Counter(r['classe_preenchimento'] for r in chains)),
        'cadeias_IFC_RDF_identicas':tuples_ifc==tuples_rdf,
        'aberturas_das_cadeias_fora_filtro_espacial':sum(r['abertura_vs_cozinha']['teste_3d']=='fora_do_filtro_espacial_2mm' for r in chains),
        'todas_aberturas_preselecionadas':len(all_openings),
        'aberturas_preselecionadas_sem_parede_qualificada':sum(not r['hospedeiro_na_lista_dez_paredes'] for r in all_openings),
        'aberturas_vs_cozinha':dict(Counter(r['abertura_vs_cozinha']['teste_3d'] for r in chains)),
        'aberturas_das_cadeias_com_intersecao_volumetrica':sum((r['abertura_vs_cozinha']['volume_comum_m3'] or 0)>VOLUME_EPS_M3 for r in chains),
        'extrato_RDF_triplas':len(cut),'extrato_sem_triplas_novas':True,
        'limites':['Conferência interna e visualização das malhas; não existe planta ou classificação independente como padrão-ouro neste ensaio.',
                  'Não demonstra completude de paredes ou associação funcional de portas/janelas ao ambiente.',
                  'Contato e volume referem-se a malhas trianguladas e aos limiares do Notebook 1; não são limites IFC de segundo nível.',
                  'A pré-seleção por caixas só exclui candidatos; a sobreposição das caixas não confirma relação.',
                  'Não altera o IFC, o RDF ou o código do Notebook 1.']}
    save_json(out/'conferencia_cozinha_dados.json',{'resumo':summary,'paredes':wall_rows,'cadeias':chains,'aberturas_preselecionadas':all_openings})
    assert sha(ifc_path)==EXPECTED_IFC and sha(ttl)==original_rdf_hash
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return model,records,summary,wall_rows,chains,all_openings

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--ifc',required=True);p.add_argument('--resultados',required=True);p.add_argument('--cache',required=True);p.add_argument('--saida',required=True)
    a=p.parse_args();inspect(a.ifc,a.resultados,a.cache,a.saida)
