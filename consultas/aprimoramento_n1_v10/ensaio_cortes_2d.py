"""Ensaio comparativo inspirado em XeoBIM/Ham (2026), §§3.2–3.4,
DOI 10.3390/buildings16153086, e nas representações de Ying/Lee (2021).
Usa seções de malhas e IfcOpeningElement ligado a Door/Window; não reproduz
o visualizador inteiro. Buffer de 1 mm no lugar da expansão radial do XeoBIM.
Sem fallback AABB, sem promover o resultado 2D à associação primária 3D.
"""
from pathlib import Path
import json
import numpy as np
import ifcopenshell,ifcopenshell.geom
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union,polygonize_full
from preparar_geometria import save,sha,SHA

ALTURAS_M=(.5,1.2,2.0)
QUANTIZACAO_M=1e-5
EXPANSAO_M=.001
PERIMETRO_MIN_M=1.0

def secao(vertices,triangles,z):
    segments=[]
    for tri in vertices[triangles]:
        dz=tri[:,2]-z
        if np.min(dz)>1e-10 or np.max(dz)<-1e-10 or np.max(abs(dz))<1e-10:continue
        pts=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            a,b=tri[i],tri[j];da,db=dz[i],dz[j]
            if abs(da)<1e-10:pts.append(a[:2])
            if da*db<0:pts.append((a+(b-a)*(-da/(db-da)))[:2])
        if len(pts)<2:continue
        pts=np.unique(np.round(np.asarray(pts)/QUANTIZACAO_M)*QUANTIZACAO_M,axis=0)
        if len(pts)==2 and np.linalg.norm(pts[0]-pts[1])>QUANTIZACAO_M/2:segments.append(LineString(pts))
    if not segments:return None,{'estado':'sem_segmentos_no_corte'}
    polygons,cuts,dangles,invalid=polygonize_full(unary_union(segments))
    parts=[p for p in polygons.geoms if p.area>1e-8]
    if not parts:return None,{'estado':'sem_contorno_fechado','segmentos':len(segments),'linhas_soltas_m':float(cuts.length+dangles.length)}
    # Não unir as faces das cavidades: isso apagaria anéis internos.
    p=max(parts,key=lambda p:p.area)
    return p,{'estado':'contorno_fechado_2d','area_m2':float(p.area),'poligonos_encontrados':len(parts),
      'segmentos':len(segments),'linhas_soltas_m':float(cuts.length+dangles.length),'wkt':p.wkt,
      'limite':'Maior polígono fechado do corte, preservando seus anéis. Pode representar somente parte de espaço desconectado.'}

def associar(room,opening):
    if room is None or opening is None:return False
    overlap=room.buffer(EXPANSAO_M,join_style=2).intersection(opening)
    return overlap.area>1e-8 and overlap.length>=PERIMETRO_MIN_M

def run(ifc,out,reference=None):
    ifc=Path(ifc);out=Path(out);out.mkdir(parents=True,exist_ok=True);assert sha(ifc)==SHA
    model=ifcopenshell.open(str(ifc));settings=ifcopenshell.geom.settings()
    settings.set('use-world-coords',True);settings.set('convert-back-units',False)
    settings.set('disable-opening-subtractions',True)
    memo={}
    def mesh(e):
        if e.GlobalId not in memo:
            holder=ifcopenshell.geom.create_shape(settings,e);s=holder.geometry
            memo[e.GlobalId]=(np.asarray(s.verts).reshape(-1,3).copy(),np.asarray(s.faces,dtype=int).reshape(-1,3).copy())
        return memo[e.GlobalId]
    openings=[]
    for op in model.by_type('IfcOpeningElement'):
        targets=[r.RelatedBuildingElement for r in op.HasFillings if r.RelatedBuildingElement.is_a() in ['IfcDoor','IfcWindow']]
        if targets:
            try:
                v,f=mesh(op);openings.append((op.GlobalId,[e.GlobalId for e in targets],v,f))
            except (ValueError,RuntimeError):pass
    cached_sections={};rows=[]
    for e in model.by_type('IfcSpace'):
        rec={'ambiente':e.GlobalId,'nome':e.LongName or e.Name,'cortes':[],'previstos_uniao_alturas':[]}
        try:
            vertices,tri=mesh(e);zmin=float(vertices[:,2].min());zmax=float(vertices[:,2].max());pred=set()
            for h in ALTURAS_M:
                z=zmin+h
                if z>=zmax-1e-6:continue
                p,info=secao(vertices,tri,z);local=set()
                if p is not None:
                    for oguid,targets,v,f in openings:
                        if z<float(v[:,2].min()) or z>float(v[:,2].max()):continue
                        b=p.bounds;lo=v[:,:2].min(axis=0);hi=v[:,:2].max(axis=0)
                        if b[0]>hi[0]+EXPANSAO_M or b[1]>hi[1]+EXPANSAO_M or b[2]<lo[0]-EXPANSAO_M or b[3]<lo[1]-EXPANSAO_M:continue
                        key=(oguid,round(z,7))
                        if key not in cached_sections:cached_sections[key]=secao(v,f,z)[0]
                        if associar(p,cached_sections[key]):local.update(targets)
                pred.update(local);rec['cortes'].append({'altura_relativa_m':h,'z_m':z,**info,'previstos':sorted(local)})
            rec['previstos_uniao_alturas']=sorted(pred)
        except (ValueError,RuntimeError) as exc:rec['motivo']=str(exc)
        rows.append(rec)
    result={'metodo':'Ensaio 2D inspirado em XeoBIM; união de três alturas; sem AABB como prova',
      'parametros':{'alturas_m':ALTURAS_M,'quantizacao_m':QUANTIZACAO_M,'expansao_m':EXPANSAO_M,'perimetro_min_m':PERIMETRO_MIN_M},
      'ambientes':rows,'ambientes_com_algum_contorno':sum(any(c.get('estado')=='contorno_fechado_2d' for c in r['cortes']) for r in rows),
      'limite':'Ensaio separado. Relação 2D não valida sólido, limite 3D, hospedeiro ou acessibilidade. Parâmetros congelados antes da conferência.'}
    # Referência consultada exclusivamente depois de concluir todas as previsões.
    if reference:
        ref=json.loads(Path(reference).read_text(encoding='utf8'));byid={r['ambiente']:r for r in rows};cases=[];tot={k:0 for k in ['TP','FP','FN','TN','indeterminados','positivos_sem_contorno','negativos_sem_contorno']}
        for room in ref['ambientes']:
            r=byid[room['guid']];available=any(c.get('estado')=='contorno_fechado_2d' for c in r['cortes']);pred=set(r['previstos_uniao_alturas'])
            for case in room['casos']:
                truth=case['pertence_ao_ambiente'];found=case['guid'] in pred
                key='indeterminados' if truth=='indeterminado' else ('positivos_sem_contorno' if truth=='sim' else 'negativos_sem_contorno') if not available else 'TP' if truth=='sim' and found else 'FN' if truth=='sim' else 'FP' if found else 'TN'
                tot[key]+=1;cases.append({'ambiente':room['guid'],'elemento':case['guid'],'resultado':key})
        result['conferencia_14_ambientes']={'totais':tot,'casos':cases,'limite':ref['limites']}
    save(out/'Ensaio_Cortes_2D_v10.json',result);print('Ensaio 2D:',result['ambientes_com_algum_contorno'],result.get('conferencia_14_ambientes',{}).get('totais'),flush=True);return result
