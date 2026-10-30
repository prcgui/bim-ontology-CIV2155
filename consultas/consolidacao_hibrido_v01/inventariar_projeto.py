"""Leitura independente das previsões: todas as aberturas e esquadrias do IFC.

Fonte técnica: IfcOpenShell geometry_processing, coordenadas globais e metros.
A classificação por vértices é somente evidência de localização do estudo.
Não usa a lista de acertos nem as decisões da conferência documental.
"""
from pathlib import Path
import json,csv,hashlib
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_ON,TopAbs_OUT
from OCP.gp import gp_Pnt
from ifc2sb_faces import read_brep,closed_space_solid

def run(ifc_path,room_guid,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'malhas').mkdir(exist_ok=True)
    before=hashlib.sha256(Path(ifc_path).read_bytes()).hexdigest()
    model=ifcopenshell.open(str(ifc_path));settings=ifcopenshell.geom.settings()
    settings.set('use-world-coords',True);settings.set('convert-back-units',False)
    settings.set('disable-opening-subtractions',False)
    cache={};errors=[]
    def mesh(entity):
        if entity.GlobalId not in cache:
            holder=ifcopenshell.geom.create_shape(settings,entity)
            v=np.asarray(holder.geometry.verts,dtype=float).reshape(-1,3)
            f=np.asarray(holder.geometry.faces,dtype=int).reshape(-1,3)
            cache[entity.GlobalId]=(v,f)
        return cache[entity.GlobalId]
    room_entity=model.by_guid(room_guid);rv,rf=mesh(room_entity)
    rs=ifcopenshell.geom.settings();rs.set('use-world-coords',True);rs.set('convert-back-units',False);rs.set('iterator-output',W.SERIALIZED)
    holder=ifcopenshell.geom.create_shape(rs,room_entity);room,_=closed_space_solid(read_brep(holder.geometry.brep_data))
    low,high=rv.min(0),rv.max(0)
    def nearby(v,padding=.6):return bool(np.all(v.min(0)<=high+padding) and np.all(v.max(0)>=low-padding))
    def record(e):
        v,f=mesh(e);a,b=v.min(0),v.max(0)
        return {'guid':e.GlobalId,'classe':e.is_a(),'nome':e.Name,'step':e.id(),
          'min_xyz_m':a.tolist(),'max_xyz_m':b.tolist(),'centro_bbox_xyz_m':((a+b)/2).tolist(),
          'proxima_bbox_60cm':nearby(v)}
    openings=[];fills={}
    for op in model.by_type('IfcOpeningElement'):
        r={'guid':op.GlobalId,'nome':op.Name,'hospedeiros':[rel.RelatingBuildingElement.GlobalId for rel in op.VoidsElements],
          'preenchimentos':[rel.RelatedBuildingElement.GlobalId for rel in op.HasFillings]}
        try:
            r.update(record(op));r['estado_geometria']='disponivel'
            if r['proxima_bbox_60cm']:
                for rel in op.HasFillings:
                    fill=rel.RelatedBuildingElement;fr=record(fill)
                    fr['abertura']=op.GlobalId;fr['hospedeiros']=r['hospedeiros']
                    if fill.is_a('IfcWall'):
                        v,f=mesh(fill);states=[]
                        for point in np.unique(v,axis=0):
                            state=BRepClass3d_SolidClassifier(room,gp_Pnt(*map(float,point)),1e-5).State()
                            states.append('IN' if state==TopAbs_IN else 'ON' if state==TopAbs_ON else 'OUT' if state==TopAbs_OUT else 'UNKNOWN')
                        fr['vertices_por_estado']={state:states.count(state) for state in set(states)}
                        fr['todos_vertices_dentro_ou_no_limite']=all(s in ['IN','ON'] for s in states)
                        fr['algum_vertice_interno']=any(s=='IN' for s in states)
                    fills[fill.GlobalId]=fr
        except (ValueError,RuntimeError) as exc:
            r['estado_geometria']='inconclusivo';r['motivo']=str(exc);errors.append({'guid':op.GlobalId,'motivo':str(exc)})
        openings.append(r)
    fenestration=[]
    for e in model.by_type('IfcDoor')+model.by_type('IfcWindow'):
        try:
            fr=record(e)
            fr['aberturas_declaradas']=[rel.RelatingOpeningElement.GlobalId for rel in e.FillsVoids]
            fenestration.append(fr)
        except (ValueError,RuntimeError) as exc:errors.append({'guid':e.GlobalId,'motivo':str(exc)})
    for guid,(v,f) in cache.items():
        if guid==room_guid or nearby(v):np.savez_compressed(out/'malhas'/f'{guid}.npz',vertices=v,faces=f)
    result={'ifc_sha256':before,'ambiente':room_guid,'nome':room_entity.LongName,'aberturas_ifc':openings,
       'preenchimentos_proximos':list(fills.values()),'esquadrias_ifc':fenestration,'erros':errors,
       'resumo':{'aberturas_ifc':len(openings),'aberturas_proximas':sum(r.get('proxima_bbox_60cm',False) for r in openings),
          'portas_e_janelas_ifc':len(fenestration),'portas_e_janelas_proximas':sum(r['proxima_bbox_60cm'] for r in fenestration)},
       'limite':'Caixa somente pré-filtro. Vértices internos não certificam contenção integral de formas côncavas nem função arquitetônica.'}
    assert hashlib.sha256(Path(ifc_path).read_bytes()).hexdigest()==before
    (out/'Inventario_Projeto_Cozinha.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result['resumo'],ensure_ascii=False));return result

if __name__=='__main__':
    import sys
    run(sys.argv[1],sys.argv[2],sys.argv[3])
