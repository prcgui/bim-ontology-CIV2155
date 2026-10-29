"""Ensaio da adaptação parcial do IFC2SB; nunca escreve o IFC de entrada.
Relação ambiente-face é extensão experimental explicitamente identificada.
"""
from pathlib import Path
import json,csv,hashlib,time,sys,io
from collections import Counter
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
import OCP
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from ifc2sb_faces import *
KITCHEN='3UFjAT4k55zg_Pqo6VMw5l'
IFC_SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bbox(s):
    b=Bnd_Box();BRepBndLib.Add_s(s,b);return b.Get()
def bbox_candidate(a,b,tol=1e-4):return all(min(a[i+3],b[i+3])+tol>=max(a[i],b[i]) for i in range(3))
def run(ifc,out,only_wall=None):
    start=time.perf_counter();ifc=Path(ifc);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    assert sha(ifc)==IFC_SHA
    model=ifcopenshell.open(str(ifc));settings=ifcopenshell.geom.settings()
    settings.set('iterator-output',W.SERIALIZED);settings.set('use-world-coords',True)
    settings.set('convert-back-units',False);settings.set('disable-opening-subtractions',True)
    cache={};failures=[]
    def brep(e):
        if e.GlobalId not in cache:
            shape=ifcopenshell.geom.create_shape(settings,e)
            cache[e.GlobalId]=read_brep(shape.geometry.brep_data)
        return cache[e.GlobalId]
    room=model.by_guid(KITCHEN);raw_room=brep(room)
    write_brep(raw_room,out/'Cozinha_Original.brep')
    rs,space_topology=closed_space_solid(raw_room)
    write_brep(rs,out/'Cozinha_Solido_Verificado.brep')
    rfaces=shapes(rs,TopAbs_FACE);rb=bbox(rs)
    walls=[model.by_guid(only_wall)] if only_wall else model.by_type('IfcWall')
    rows=[];patch_info=[];wall_info=[];count_candidates=0
    for wi,wall in enumerate(walls):
        try:
            ws=brep(wall)
            if not bbox_candidate(rb,bbox(ws)):continue
            count_candidates+=1
            openings=[];rels=[]
            for rel in wall.HasOpenings:
                op=rel.RelatedOpeningElement;fillings=list(op.HasFillings)
                fill=fillings[0].RelatedBuildingElement if len(fillings)==1 else None
                os=brep(op)
                if not fillings:
                    cut=BRepAlgoAPI_Cut(ws,os)
                    if not cut.IsDone():raise ValueError('Subtração de abertura não preenchida falhou')
                    ws=cut.Shape()
                elif len(fillings)==1:
                    openings.append((op.GlobalId,fill.GlobalId,os))
                    rels.append({'abertura':op.GlobalId,'preenchimento':fill.GlobalId,'classe':fill.is_a(),'nome':fill.Name})
                else:failures.append({'guid':op.GlobalId,'erro':'múltiplos preenchimentos; caso não promovido'})
            opening_faces,parents,diag=cut_openings(ws,wall.GlobalId,openings)
            wall_id=f'W{count_candidates:02d}'
            totalwall=0.;wall_surfaces=[]
            for pi,p in enumerate(parents):
                for ri,rf in enumerate(rfaces):
                    contact,status=room_face_common(rf,p.shape)
                    if contact is not None and status.get('area_m2',0)>1e-8:
                        totalwall+=status['area_m2']
                        r=dict(status,original_face_index=pi,face_ambiente=ri)
                        try:r['wkt']=polygon_wkt(contact)
                        except ValueError as exc:r['wkt_indisponivel']=str(exc)
                        write_brep(contact,out/f'{wall_id}_Parede_F{pi:03d}_R{ri:02d}.brep')
                        wall_surfaces.append(r)
            overlap_shape=common(rs,ws)
            overlap_solids=shapes(overlap_shape,TopAbs_SOLID)
            # Extensão: GProp em faces abertas pode dar massa assinada não nula.
            # Só volumes de componentes sólidas contam como interpenetração.
            signed_overlap=volume(overlap_shape)
            wall_overlap=sum(abs(volume(s)) for s in overlap_solids)
            wall_valid=BRepCheck_Analyzer(ws).IsValid()
            wall_info.append({'parede':wall.GlobalId,'nome':wall.Name,'codigo':wall_id,'area_contato_bruta_m2':totalwall,
                'volume_intersecao_ambiente_parede_m3':wall_overlap,
                'massa_assinada_resultado_common':signed_overlap,'solidos_no_common':len(overlap_solids),
                'superficies_brutas_coincidentes':wall_surfaces,
                'faces_abertura':len(opening_faces),'diagnosticos':diag,'brep_valido':BRepCheck_Analyzer(ws).IsValid()})
            for oi,(og,fg,os) in enumerate(openings):
                matching=[f for f in opening_faces if f.opening==og]
                row={'parede':wall.GlobalId,'abertura':og,'preenchimento':fg,
                  'classe_preenchimento':model.by_guid(fg).is_a(),'nome_preenchimento':model.by_guid(fg).Name,
                  'faces_recortadas':len(matching),'faces_com_parent_aprovado':0,'area_coincidente_cozinha_m2':0.,
                  'fora_bbox_cozinha':not bbox_candidate(rb,bbox(os)),'estado':'sem_intersecao_de_face_no_criterio',
                  'validacao_arquitetonica':'não realizada','avisos':[]}
                row['volume_intersecao_ambiente_parede_m3']=wall_overlap
                row['brep_parede_valido']=wall_valid
                if not matching:row['estado']='sem_face_de_abertura_recortada'
                for j,p in enumerate(matching):
                    parent=parents[p.original_index];check=check_parent(p,parent)
                    if check['ok']:row['faces_com_parent_aprovado']+=1
                    name=f'{wall_id}_O{oi+1:02d}_F{j+1:02d}';write_brep(p.shape,out/(name+'.brep'))
                    write_brep(parent.shape,out/(name+'_Parent.brep'))
                    rec={'codigo':name,'parede':wall.GlobalId,'abertura':og,'preenchimento':fg,
                      'original_face_index':p.original_index,'area_face_m2':area(p.shape),'parent_check':check,'contatos':[]}
                    if check['ok']:
                        for ri,rf in enumerate(rfaces):
                            contact,status=room_face_common(rf,p.shape)
                            if contact is not None and status.get('area_m2',0)>1e-8:
                                item=dict(status,face_ambiente=ri)
                                try:item['wkt']=polygon_wkt(contact)
                                except ValueError as exc:item['wkt_indisponivel']=str(exc)
                                rec['contatos'].append(item)
                                row['area_coincidente_cozinha_m2']+=status['area_m2']
                                write_brep(contact,out/(name+f'_Contato_R{ri:02d}.brep'))
                    patch_info.append(rec)
                if row['area_coincidente_cozinha_m2']>1e-8:row['estado']='evidencia_geometrica_de_coincidencia'
                if wall_overlap>1e-8 and row['area_coincidente_cozinha_m2']>1e-8:row['estado']='coincidencia_com_interpenetracao_parede_ambiente'
                if not wall_valid:row['avisos'].append('BRep do hospedeiro inválido; não certifica relação arquitetônica')
                if row['fora_bbox_cozinha']:row['estado']='fora_do_ambiente_por_separacao_bbox'
                rows.append(row)
            print(wall_id,wall.GlobalId,'aberturas',len(openings),'faces',len(opening_faces),'contato_bruto',totalwall,flush=True)
        except Exception as exc:
            failures.append({'guid':wall.GlobalId,'erro':type(exc).__name__+': '+str(exc)})
    summary={'procedimento':'adaptação parcial IFC2SB C++ -> Python/OCP; extensão ambiente-face separada',
      'sha256_IFC':sha(ifc),'original_preservado':sha(ifc)==IFC_SHA,'ambiente':KITCHEN,'nome':room.LongName,
      'ifcopenshell':ifcopenshell.version,'OCP':OCP.__version__,'volume_ambiente_m3':volume(rs),
      'topologia_ambiente':space_topology,'wkt_ambiente':polygon_wkt(rs),
      'brep_ambiente_valido':BRepCheck_Analyzer(rs).IsValid(),'paredes_examinadas':len(walls),'paredes_candidatas_bbox':count_candidates,
      'paredes':wall_info,'aberturas':rows,'faces_recortadas':patch_info,'falhas':failures,'segundos':time.perf_counter()-start,
      'limite':'Coincidência geométrica não certifica atribuição arquitetônica. Não cobre fallback por caixas, superfícies curvas ou reconstrução global de espaços.'}
    (out/'Resultado_Piloto.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    if rows:
        with (out/'Aberturas_Verificadas.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print('RESUMO',Counter(r['estado'] for r in rows),'FALHAS',failures,flush=True)
    return summary
if __name__=='__main__':run(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
