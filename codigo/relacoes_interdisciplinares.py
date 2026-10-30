"""Relações espaço-elemento entre modelos, com geometrias em metros.

Lilis et al. (2025), DOI 10.1016/j.autcon.2025.106081, §§3.1–3.4:
checagem cruzada, pré-filtro AABB, operação geométrica e registro em grafo.
Adaptação própria com OCP; não é o executável GRC/BSP dos autores.
Rasmussen et al. (2021), DOI 10.3233/SW-200385, §3.4: distinguir
contenção, interseção e adjacência. A junção não transforma nomes em identidade.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,time
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.unit as units
import ifcopenshell.util.placement as placement
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.TopAbs import TopAbs_SOLID
from ifc2sb_faces import read_brep,write_brep,shapes,volume,area,TopAbs_FACE
from recuperar_geometria import preparar_volume_controlado
from preparar_geometria import bbox

CLASSES_ESTRUTURAIS={'IfcBeam','IfcColumn','IfcFooting','IfcPile','IfcSlab','IfcMember','IfcWall','IfcPlate','IfcRoof'}
PARAMETROS={'margem_aabb_m':1e-4,'volume_min_m3':1e-9,'volume_relativo_min':1e-8,
            'area_comum_min_m2':1e-6,'distancia_busca_contato_m':1e-4,'tolerancia_contencao_rel':1e-7}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def csv_write(path,rows,fields=None):
    if not rows and fields is None:return
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',encoding='utf-8-sig',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader();writer.writerows(rows)
def candidatos(a,b,margin=PARAMETROS['margem_aabb_m']):
    return all(a[i]<=b[i+3]+margin and b[i]<=a[i+3]+margin for i in range(3))
def settings_brep():
    s=ifcopenshell.geom.settings();s.set('iterator-output',W.SERIALIZED)
    s.set('use-world-coords',True);s.set('convert-back-units',False)
    s.set('disable-opening-subtractions',True);return s
def extrair_brep(settings,element):
    # Manter o holder vivo enquanto o conteúdo SERIALIZED é lido (IfcOpenShell).
    holder=ifcopenshell.geom.create_shape(settings,element)
    return read_brep(holder.geometry.brep_data)
def contorno_solido(solid):
    result=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(result)
    for face in shapes(solid,TopAbs_FACE):builder.Add(result,face)
    return result
def common(a,b):
    op=BRepAlgoAPI_Common(a,b)
    if not op.IsDone():raise ValueError('Operação Common não concluída.')
    result=op.Shape()
    if not BRepCheck_Analyzer(result).IsValid():raise ValueError('Resultado Common inválido.')
    return result

def verificar_solido(raw):
    """Reutiliza o preparo conservador do N1; nunca substitui o corpo por caixa."""
    solid,info=preparar_volume_controlado(raw)
    if len(shapes(solid,TopAbs_SOLID))!=1 or not BRepCheck_Analyzer(solid).IsValid():
        raise ValueError('Não foi obtido um único sólido válido.')
    v=volume(solid)
    if not np.isfinite(v) or v<=0:raise ValueError('Volume não positivo.')
    return solid,info

def avaliar_par(space,element):
    """Operação em sólidos já preparados; resultados não são equivalência de objetos."""
    vs,ve=volume(space),volume(element)
    if vs<=0 or ve<=0 or not shapes(space,TopAbs_SOLID) or not shapes(element,TopAbs_SOLID):
        raise ValueError('O par exige dois sólidos com volume positivo.')
    if not BRepCheck_Analyzer(space).IsValid() or not BRepCheck_Analyzer(element).IsValid():
        raise ValueError('O par contém BRep inválido.')
    intersection=common(space,element);vi=max(0.,volume(intersection))
    eps=max(PARAMETROS['volume_min_m3'],min(vs,ve)*PARAMETROS['volume_relativo_min'])
    if vi>min(vs,ve)+max(eps,min(vs,ve)*1e-6):raise ValueError('Volume de interseção excede os operandos.')
    result={'volume_elemento_m3':ve,'volume_intersecao_m3':vi,'area_contato_m2':0.,
            'fracao_elemento_no_espaco':vi/ve,'limiar_volume_m3':eps,'estado':'sem_relacao_no_criterio',
            'predicado_bot':'','distancia_minima_m':None}
    if vi>eps:
        contained=abs(ve-vi)<=max(eps,ve*PARAMETROS['tolerancia_contencao_rel'])
        result.update(estado='contido' if contained else 'intersecciona',
                      predicado_bot='containsElement' if contained else 'intersectingElement')
        return result
    distance=BRepExtrema_DistShapeShape(space,element)
    if not distance.IsDone():raise ValueError('Distância entre operandos indisponível.')
    result['distancia_minima_m']=float(distance.Value())
    if distance.Value()>PARAMETROS['distancia_busca_contato_m']:return result
    boundary=common(contorno_solido(space),contorno_solido(element));shared=max(0.,area(boundary))
    result['area_contato_m2']=shared
    if shared>PARAMETROS['area_comum_min_m2']:result.update(estado='adjacente',predicado_bot='adjacentElement')
    elif distance.Value()<=PARAMETROS['distancia_busca_contato_m']:result['estado']='proximo_sem_superficie_comum'
    return result

def preparar_espacos(ifc,cache):
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True);model=ifcopenshell.open(ifc);settings=settings_brep();rows=[]
    for entity in model.by_type('IfcSpace'):
        row={'guid':entity.GlobalId,'nome':entity.LongName or entity.Name,'estado':'inconclusivo_preparo'}
        try:
            raw=extrair_brep(settings,entity);solid,info=verificar_solido(raw)
            filename=entity.GlobalId+'.brep';write_brep(solid,cache/filename)
            row.update(estado='solido_aceito',arquivo=filename,sha256_brep=sha(cache/filename),bbox=bbox(solid),
                       volume_m3=volume(solid),metodo_preparo=info['metodo_v10'])
        except (ValueError,RuntimeError) as exc:row['motivo']=str(exc)
        rows.append(row)
    save(cache/'Espacos.json',{'ifc_sha256':sha(ifc),'espacos':rows});return rows

def preparar_caixas(ifc,modelo,cache):
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    model=ifcopenshell.open(ifc)
    elements=model.by_type('IfcElement')
    selected=[e for e in elements if e.is_a() in CLASSES_ESTRUTURAIS and not any(getattr(r,'RelatedObjects',()) for r in e.IsDecomposedBy)]
    targets=[e for e in selected if e.Representation]
    selected_ids={e.id() for e in selected}
    settings=ifcopenshell.geom.settings();settings.set('use-world-coords',True);settings.set('convert-back-units',False)
    iterator=ifcopenshell.geom.iterator(settings,model,2,include=targets);rows=[]
    if iterator.initialize():
        while True:
            shape=iterator.get();vertices=np.asarray(shape.geometry.verts).reshape(-1,3);entity=model.by_guid(shape.guid)
            if len(vertices):rows.append({'modelo':modelo,'guid':entity.GlobalId,'classe':entity.is_a(),'nome':entity.Name,
                'bbox':[float(x) for x in [*vertices.min(axis=0),*vertices.max(axis=0)]]})
            if not iterator.next():break
    seen={r['guid'] for r in rows}
    for e in selected:
        if e.GlobalId not in seen:rows.append({'modelo':modelo,'guid':e.GlobalId,'classe':e.is_a(),'nome':e.Name,'bbox':None,'motivo':'geometria_indisponivel'})
    record={'modelo':modelo,'ifc_sha256':sha(ifc),'fator_unidade_para_m':units.calculate_unit_scale(model),
            'elementos_ifc':len(elements),'alvos_geometricos':len(selected),'com_caixa':len(seen),
            'classes_fora_do_recorte':dict(Counter(e.is_a() for e in elements if e.id() not in selected_ids)),
            'elementos':rows}
    save(cache/'Caixas.json',record);return record

def executar_relacoes(arquitetura,estruturas,cache,saida):
    """estruturas é um mapa {chave: caminho IFC}; não aplica registro espacial inferido."""
    cache=Path(cache);out=Path(saida);cache.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    rooms=preparar_espacos(arquitetura,cache/'espacos')
    accepted=[r for r in rooms if r['estado']=='solido_aceito'];raw_rows=[];positives=[];summaries=[]
    room_shapes={r['guid']:read_brep((cache/'espacos'/r['arquivo']).read_bytes()) for r in accepted}
    per_room={r['guid']:{'ambiente':r['guid'],'nome':r['nome'],'estado_preparo':r['estado'],'motivo':r.get('motivo','')} for r in rooms}
    for key,ifc in estruturas.items():
        record=preparar_caixas(ifc,key,cache/key);model=ifcopenshell.open(ifc);settings=settings_brep()
        by_element=defaultdict(list)
        for element in record['elementos']:
            if element['bbox']:
                for room in accepted:
                    if candidatos(room['bbox'],element['bbox']):by_element[element['guid']].append(room)
        index={e['guid']:e for e in record['elementos']};local=[];bad_geometries=0;preparations=Counter()
        trace=cache/key/'Pares_Examinados.jsonl'
        with trace.open('w',encoding='utf8') as fp:
            for i,(guid,candidate_rooms) in enumerate(by_element.items(),1):
                element=index[guid];solid=None;problem=None
                try:
                    raw=extrair_brep(settings,model.by_guid(guid));solid,info=verificar_solido(raw)
                    preparations[info['metodo_v10']]+=1
                except (ValueError,RuntimeError) as exc:problem=str(exc);bad_geometries+=1
                for room in candidate_rooms:
                    row={'modelo':key,'ambiente':room['guid'],'nome_ambiente':room['nome'],'elemento':guid,
                         'classe_ifc':element['classe'],'nome_elemento':element['nome'],'estado':'inconclusivo_geometria_elemento' if problem else 'inconclusivo_operacao'}
                    if problem:row['motivo']=problem
                    else:
                        try:row.update(avaliar_par(room_shapes[room['guid']],solid))
                        except (ValueError,RuntimeError) as exc:row['motivo']=str(exc)
                    fp.write(json.dumps(row,ensure_ascii=False)+'\n');fp.flush();local.append(row)
                    if row.get('predicado_bot'):positives.append(row)
                if i%100==0:print('PARES',key,i,'/',len(by_element),'elementos;',len(local),'pares',flush=True)
        for room in rooms:
            subset=[r for r in local if r['ambiente']==room['guid']];ok=[r for r in subset if r.get('predicado_bot')]
            per_room[room['guid']].update({key+'_pares_candidatos':len(subset) if room['estado']=='solido_aceito' else None,
                key+'_relacoes':len(ok) if room['estado']=='solido_aceito' else None,
                key+'_inconclusivos':sum(r['estado'].startswith('inconclusivo') for r in subset) if room['estado']=='solido_aceito' else None})
        summaries.append({'modelo':key,'elementos_ifc':record['elementos_ifc'],'alvos_geometricos':record['alvos_geometricos'],
            'caixas_disponiveis':record['com_caixa'],'elementos_com_candidatos':len(by_element),
            'elementos_com_preparo_inconclusivo':bad_geometries,'pares_examinados':len(local),
            'estados':dict(Counter(r['estado'] for r in local)), 'metodos_preparo':dict(preparations),
            'classes_fora_do_recorte':record['classes_fora_do_recorte']})
        raw_rows.extend(local);del model
    fields=['modelo','ambiente','nome_ambiente','elemento','classe_ifc','nome_elemento','estado','predicado_bot',
            'volume_elemento_m3','volume_intersecao_m3','fracao_elemento_no_espaco','area_contato_m2','distancia_minima_m','limiar_volume_m3']
    csv_write(out/'Relacoes_Espaciais.csv',[{k:r.get(k,'') for k in fields} for r in positives],fields)
    csv_write(out/'Integracao_Por_Ambiente.csv',list(per_room.values()))
    summary={'parametros':PARAMETROS,'ambientes':len(rooms),'ambientes_com_solido':len(accepted),
             'ambientes_inconclusivos':len(rooms)-len(accepted),'por_modelo':summaries,'relacoes_positivas':len(positives),
             'pares':len(raw_rows),'referencial':'Coordenadas de engenharia dos IFCs, com placements aplicados e comprimentos em metros; sem transformação inferida entre modelos.'}
    save(out/'Resumo_Geometrico.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return summary
