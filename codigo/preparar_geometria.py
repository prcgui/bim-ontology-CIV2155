"""Preparo global, sem alterar o IFC: IFC2SB parcial + geometrias de espaços.

Fichter et al. (2021), DOI 10.26868/25222708.2021.30156: helper parcial
GPL-3.0-or-later, atribuição preservada. Compartilhar o recorte de cada
parede entre ambientes é reorganização de execução deste estudo.
IfcOpenShell/OCP atuais; não execução integral do programa dos autores.
"""
from pathlib import Path
import json,hashlib,time,os
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.TopAbs import TopAbs_VERTEX
from OCP.BRep import BRep_Tool
from ifc2sb_faces import (read_brep,write_brep,closed_space_solid,shapes,cut_openings,
    check_parent,polygon_wkt,normal,TopAbs_FACE,TopoDS,BRepAdaptor_Surface,GeomAbs_Plane)

SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
VERSION='aprimoramento-1.0'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def bbox(shape):
    b=Bnd_Box();BRepBndLib.Add_s(shape,b);return list(b.Get())
def vertices(shape):
    rows=[]
    for v in shapes(shape,TopAbs_VERTEX):
        p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(v));rows.append([p.X(),p.Y(),p.Z()])
    return np.unique(np.round(np.asarray(rows),12),axis=0).tolist() if rows else []
def planar_record(face,id):
    if BRepAdaptor_Surface(face).GetType()!=GeomAbs_Plane:raise ValueError('superficie_curva')
    n=normal(face);return {'id':id,'wkt':polygon_wkt(face),'normal':[n.X(),n.Y(),n.Z()]}

def init_worker(ifc_path):
    global MODEL,SETTINGS,LOCAL_CACHE
    MODEL=ifcopenshell.open(str(ifc_path));LOCAL_CACHE={}
    SETTINGS=ifcopenshell.geom.settings();SETTINGS.set('iterator-output',W.SERIALIZED)
    SETTINGS.set('use-world-coords',True);SETTINGS.set('convert-back-units',False)
    SETTINGS.set('disable-opening-subtractions',True)
def brep(entity):
    if entity.GlobalId not in LOCAL_CACHE:
        holder=ifcopenshell.geom.create_shape(SETTINGS,entity)
        LOCAL_CACHE[entity.GlobalId]=read_brep(holder.geometry.brep_data)
    return LOCAL_CACHE[entity.GlobalId]

def process_wall(task):
    guid,folder=task;out=Path(folder)/'paredes'/f'{guid}.json';wall=MODEL.by_guid(guid)
    result={'guid':guid,'nome':wall.Name,'ifc_sha256':SHA,'versao_preparo':VERSION,'estado':'inconclusivo',
       'faces_parentais':[],'recortes':[],'aberturas':[],'faces_nao_cobertas':[]}
    started=time.perf_counter()
    try:
        raw=brep(wall);result['bbox']=bbox(raw);result['vertices_xyz_m']=vertices(raw)
        openings=[]
        for rel in wall.HasOpenings:
            op=rel.RelatedOpeningElement;fills=list(op.HasFillings)
            record={'guid':op.GlobalId,'preenchimentos':[r.RelatedBuildingElement.GlobalId for r in fills]}
            result['aberturas'].append(record)
            if not fills:
                cut=BRepAlgoAPI_Cut(raw,brep(op));assert cut.IsDone();raw=cut.Shape()
            elif len(fills)==1:openings.append((op.GlobalId,fills[0].RelatedBuildingElement.GlobalId,brep(op)))
            else:record['estado']='multiplos_preenchimentos_nao_cobertos'
        pieces,parents,diagnostics=cut_openings(raw,guid,openings)
        result['diagnosticos_recorte']=diagnostics
        for i,parent in enumerate(parents):
            try:result['faces_parentais'].append(dict(planar_record(parent.shape,f'F{i:03d}'),indice=i))
            except ValueError as exc:result['faces_nao_cobertas'].append({'face':i,'motivo':str(exc)})
        for i,piece in enumerate(pieces):
            check=check_parent(piece,parents[piece.original_index])
            try:result['recortes'].append(dict(planar_record(piece.shape,f'P{i:03d}'),
                indice_parental=piece.original_index,abertura=piece.opening,preenchimento=piece.filling,check_parent=check))
            except ValueError as exc:result['faces_nao_cobertas'].append({'recorte':i,'motivo':str(exc)})
        result['estado']='recorte_preparado'
    except Exception as exc:result.update(estado='inconclusivo_geometria',motivo=type(exc).__name__+': '+str(exc))
    result['segundos']=time.perf_counter()-started;save(out,result)
    return {'guid':guid,'estado':result['estado'],'bbox':result.get('bbox'),'arquivo':'paredes/'+out.name,
      'sha256':sha(out),'faces_parentais':len(result['faces_parentais']),'recortes':len(result['recortes']),
      'faces_nao_cobertas':len(result['faces_nao_cobertas']),'motivo':result.get('motivo')}

def preparar(ifc_path,out,workers=2):
    ifc_path=Path(ifc_path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name in ['paredes','espacos']: (out/name).mkdir(exist_ok=True)
    assert sha(ifc_path)==SHA
    started=time.perf_counter();init_worker(ifc_path);rooms=[];products={};openings=[]
    # Cada espaço é examinado, inclusive os que não passam no sólido fechado.
    for e in MODEL.by_type('IfcSpace'):
        rec={'guid':e.GlobalId,'nome':e.LongName or e.Name,'nome_curto':e.Name,'estado':'inconclusivo'}
        try:
            raw=brep(e);rec['bbox']=bbox(raw);rec['vertices_xyz_m']=vertices(raw)
            from recuperar_geometria import preparar_volume_controlado
            solid,info=preparar_volume_controlado(raw)
            write_brep(solid,out/'espacos'/f'{e.GlobalId}.brep')
            rec.update(estado='volume_fechado_aceito',preparacao=info,faces=[])
            for i,face in enumerate(shapes(solid,TopAbs_FACE)):
                try:rec['faces'].append(planar_record(face,f'R{i:02d}'))
                except ValueError as exc:
                    rec.setdefault('faces_nao_cobertas',[]).append({'face':i,'motivo':str(exc)})
            if rec.get('faces_nao_cobertas'):rec['estado']='volume_aceito_com_faces_nao_cobertas'
            rec['arquivo_brep']='espacos/'+e.GlobalId+'.brep';rec['sha256_brep']=sha(out/rec['arquivo_brep'])
        except (RuntimeError,ValueError) as exc:
            rec.update(estado='inconclusivo_preparacao_espaco',motivo=str(exc))
            if hasattr(exc,'tentativas'):rec['tentativas_recuperacao']=exc.tentativas
        rooms.append(rec);print('ESPAÇO',len(rooms),rec['nome'],rec['estado'],flush=True)
    # Leitura das relações declaradas e dos preenchimentos, sem previsão espacial.
    targets={e.GlobalId:e for e in MODEL.by_type('IfcDoor')+MODEL.by_type('IfcWindow')}
    for op in MODEL.by_type('IfcOpeningElement'):
        fills=[r.RelatedBuildingElement for r in op.HasFillings]
        openings.append({'guid':op.GlobalId,'hospedeiros':[r.RelatingBuildingElement.GlobalId for r in op.VoidsElements],
          'preenchimentos':[e.GlobalId for e in fills]})
        targets.update({e.GlobalId:e for e in fills})
    for e in targets.values():
        r={'guid':e.GlobalId,'classe':e.is_a(),'nome':e.Name,
           'aberturas_declaradas':[r.RelatingOpeningElement.GlobalId for r in getattr(e,'FillsVoids',[])]}
        try:
            shape=brep(e);r.update(bbox=bbox(shape),vertices_xyz_m=vertices(shape),estado_geometria='disponivel')
        except (RuntimeError,ValueError) as exc:r.update(estado_geometria='inconclusivo',motivo=str(exc))
        products[e.GlobalId]=r
    print('PREPARO: espaços e',len(products),'produtos de preenchimento/componentes lidos.',flush=True)
    wall_ids=[w.GlobalId for w in MODEL.by_type('IfcWall')]
    wall_results=[]
    with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(str(ifc_path),)) as pool:
        futures=[pool.submit(process_wall,(guid,str(out))) for guid in wall_ids]
        for future in as_completed(futures):
            wall_results.append(future.result())
            if len(wall_results)%25==0:print('PAREDES PREPARADAS',len(wall_results),'/',len(wall_ids),flush=True)
    import OCP
    result={'ifc_sha256':SHA,'versao_preparo':VERSION,'ifcopenshell':ifcopenshell.version,'OCP':OCP.__version__,
      'espacos':rooms,'paredes':sorted(wall_results,key=lambda r:r['guid']),'produtos':list(products.values()),'aberturas':openings,
      'resumo':{'espacos':len(rooms),'espacos_com_volume_aceito':sum(r['estado'].startswith('volume_') for r in rooms),
       'paredes':len(wall_ids),'paredes_preparadas':sum(r['estado']=='recorte_preparado' for r in wall_results),
       'paredes_inconclusivas':sum(r['estado']!='recorte_preparado' for r in wall_results),'aberturas_ifc':len(openings),
       'produtos_examinados':len(products)},'segundos':time.perf_counter()-started,'ifc_preservado':sha(ifc_path)==SHA}
    save(out/'Catalogo_Geometria.json',result)
    print('PREPARO CONCLUÍDO',json.dumps(result['resumo'],ensure_ascii=False),flush=True);return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('ifc');p.add_argument('saida');p.add_argument('--workers',type=int,default=2)
    a=p.parse_args();preparar(a.ifc,a.saida,a.workers)
