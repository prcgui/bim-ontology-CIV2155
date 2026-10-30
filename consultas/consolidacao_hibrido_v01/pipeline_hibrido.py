"""Combina recortes IFC2SB, operações geométricas de Kiavarz e sinais CGAL.

Kiavarz et al. (2023), DOI 10.3390/buildings13020350, §§4.2.2-4.4,
Tabelas 4-5: plano, orientação, raio e interseção poligonal.
Fichter et al. (2021), DOI 10.26868/25222708.2021.30156: recortes de
aberturas já produzidos pela adaptação parcial IFC2SB deste estudo.
Krijnen et al. (2020), DOI 10.46421/2706-6568.37.2020.paper008:
avaliações CGAL do mesmo conjunto, reutilizadas sem nova execução do motor.

Extensão específica do estudo: candidatos substituem BoundedBy ausente;
IfcSpace limita o recorte; validação do contorno parental; sondas locais;
associação ao fragmento do ambiente, sem inferir a função arquitetônica.
Não regrava o IFC e não corrige conflitos do modelo.
"""
from pathlib import Path
import json,hashlib,time,csv,zipfile,math
from collections import Counter,defaultdict
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_OUT,TopAbs_ON
from OCP.gp import gp_Pnt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from ifc2sb_faces import (read_brep,closed_space_solid,shapes,polygon_wkt,normal,
 BRepAdaptor_Surface,GeomAbs_Plane,TopAbs_FACE,TopAbs_SHELL,volume,BRepGProp,GProp_GProps,TopoDS)
from faces_kiavarz import *

IFC_SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',encoding='utf-8-sig',newline='') as fp:
        wr=csv.DictWriter(fp,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));wr.writeheader();wr.writerows(rows)

def run(ifc_path,pilot_folder,cgal_folder,out):
    t=time.perf_counter();ifc_path=Path(ifc_path);pilot_folder=Path(pilot_folder);cgal_folder=Path(cgal_folder);out=Path(out)
    out.mkdir(parents=True,exist_ok=True);assert sha(ifc_path)==IFC_SHA
    pilot_path=pilot_folder/'Resultado_Piloto.json';pilot=json.loads(pilot_path.read_text(encoding='utf8'))
    cgal_path=cgal_folder/'Comparacao_Paredes_IFC2SB_CGAL_v01.json';cgal={r['guid']:r for r in json.loads(cgal_path.read_text(encoding='utf8'))}
    assert pilot['sha256_IFC']==IFC_SHA and len(pilot['paredes'])==34
    archive=pilot_folder/'Geometrias_BRep_e_Controles.zip'
    with zipfile.ZipFile(archive) as z:z.extractall(out/'entrada_ifc2sb')
    geometry_dir=out/'entrada_ifc2sb/geometrias'
    model=ifcopenshell.open(str(ifc_path));s=ifcopenshell.geom.settings()
    s.set('iterator-output',W.SERIALIZED);s.set('use-world-coords',True)
    s.set('convert-back-units',False);s.set('disable-opening-subtractions',True)
    cache={}
    def brep(guid):
        if guid not in cache:
            holder=ifcopenshell.geom.create_shape(s,model.by_guid(guid));cache[guid]=read_brep(holder.geometry.brep_data)
        return cache[guid]
    def face_data(shape,id):
        shape=TopoDS.Face_s(shape)
        if BRepAdaptor_Surface(shape).GetType()!=GeomAbs_Plane:raise ValueError('Superfície curva não coberta')
        n=normal(shape)
        return PlaneFace.from_wkt(id,polygon_wkt(shape),[n.X(),n.Y(),n.Z()])
    room,topology=closed_space_solid(brep(pilot['ambiente']))
    rf=[face_data(f,f'R{i:02d}') for i,f in enumerate(shapes(room,TopAbs_FACE))]
    props=GProp_GProps();BRepGProp.VolumeProperties_s(room,props);cp=props.CentreOfMass();room_center=[cp.X(),cp.Y(),cp.Z()]
    def classify(point):
        result=BRepClass3d_SolidClassifier(room,gp_Pnt(*map(float,point)),1e-7).State()
        return 'IN' if result==TopAbs_IN else 'OUT' if result==TopAbs_OUT else 'ON' if result==TopAbs_ON else 'UNKNOWN'
    interfaces=[];runtime={};parents={};diagnostics=[];unsupported=[]
    for w in pilot['paredes']:
        wall=brep(w['parede'])
        # Mesma preparação da entrada parental usada no piloto IFC2SB.
        for rel in model.by_guid(w['parede']).HasOpenings:
            op=rel.RelatedOpeningElement
            if not op.HasFillings:
                cut=BRepAlgoAPI_Cut(wall,brep(op.GlobalId))
                if not cut.IsDone():raise ValueError('Subtração de abertura não preenchida falhou')
                wall=cut.Shape()
        index=0;shells=shapes(wall,TopAbs_SHELL)
        if not shells:unsupported.append({'parede':w['parede'],'estado':'sem_shell_parental'})
        for si,shell in enumerate(shells):
            current=[]
            for f in shapes(shell,TopAbs_FACE):
                i=index;index+=1
                try:pf=face_data(f,f"{w['codigo']}_F{i:03d}")
                except ValueError as e:unsupported.append({'parede':w['parede'],'face':i,'estado':str(e)});continue
                current.append(pf);parents[(w['parede'],i)]=pf
                for room_face in rf:
                    clipped,info=clipped_interface(room_face,pf)
                    if clipped is None:continue
                    for k,part in enumerate(polygon_parts(clipped)):
                        id=f"I_{pf.id}_{room_face.id}_P{k}"
                        probe=probe_interface(room_face,part,pf.normal,rf,classify)
                        # Testa a dependência da sonda sem trocar a decisão por conveniência.
                        sensitivity=[probe_interface(room_face,part,pf.normal,rf,classify,step=st)['qualificada_no_criterio'] for st in [1e-4,1e-3,2e-3]]
                        rings=polygon_xyz(room_face,part)
                        record=dict(info,id=id,parede=w['parede'],codigo_parede=w['codigo'],nome_parede=w['nome'],
                          face_parede=i,componente_parede=si,face_ambiente=room_face.id,area_m2=float(part.area),
                          area_face_inteira_parede_m2=float(pf.polygon.area),wkt=polygon3_wkt(rings),
                          normal_parede=pf.normal.tolist(),normal_ambiente=room_face.normal.tolist(),
                          sondas=probe,qualificada_no_criterio=probe['qualificada_no_criterio'],
                          sensibilidade_sondas={'passos_m':[1e-4,1e-3,2e-3],'qualificacoes':sensitivity,'estavel':len(set(sensitivity))==1},
                          sinal_global_cgal=cgal[w['parede']]['interpretacao'],
                          validacao_arquitetonica='pendente; qualificação geométrica experimental')
                        interfaces.append(record);runtime[id]=(room_face,part,pf)
            diagnostics.append(dict(face_pair_diagnostic(current,room_center),parede=w['parede'],componente=si))
    # Usa o recorte de abertura do IFC2SB como entrada real da etapa seguinte.
    by_parent=defaultdict(list)
    for i in interfaces:by_parent[(i['parede'],i['face_parede'])].append(i)
    pieces=defaultdict(list);source_errors=[];checks=[];read_cache={}
    for p in pilot['faces_recortadas']:
        key=(p['parede'],p['original_face_index'])
        if key not in by_parent:continue
        parent_path=geometry_dir/(p['codigo']+'_Parent.brep');patch_path=geometry_dir/(p['codigo']+'.brep')
        try:
            parent=face_data(read_brep(parent_path.read_bytes()),p['codigo']+'_parent')
            child=face_data(read_brep(patch_path.read_bytes()),p['codigo'])
            current=parents[key]
            parent_gap=max(float(np.max(abs((r-current.origin)@current.normal))) for r in parent.rings)
            pa=current.projected(parent)
            agreement=pa.intersection(current.polygon).area
            consistent=parent_gap<=GAP_M and abs(agreement-current.polygon.area)<=max(1e-7,current.polygon.area*1e-8) and abs(pa.area-current.polygon.area)<=max(1e-7,current.polygon.area*1e-8)
            # CheckParent da etapa anterior não verificava inclusão do contorno.
            pc=parent.projected(child)
            child_inside=pc.intersection(parent.polygon).area>=pc.area-max(1e-8,pc.area*1e-8)
            check={'recorte_ifc2sb':p['codigo'],'parent_atual_consistente':consistent,'filha_no_contorno_parental':child_inside}
            checks.append(check)
            if not consistent or not child_inside:
                source_errors.append(dict(check,estado='ancestralidade_geometrica_nao_confirmada'));continue
            for interface in by_parent[key]:
                frame,part,_=runtime[interface['id']]
                dot=float(frame.normal@child.normal)
                gap=max(float(np.max(abs((r-frame.origin)@frame.normal))) for r in child.rings)
                if dot>-1+NORMAL_TOL or gap>GAP_M:continue
                candidate=part.intersection(frame.projected(child))
                if candidate.area>AREA_MIN:pieces[(interface['id'],p['abertura'],p['preenchimento'])].append((candidate,p['codigo']))
        except (ValueError,RuntimeError) as e:source_errors.append({'recorte_ifc2sb':p['codigo'],'estado':str(e)})
    from shapely.ops import unary_union
    opening_pieces=[];interfaces_by_id={i['id']:i for i in interfaces}
    for (iid,opening,filling),parts in sorted(pieces.items()):
        geom=unary_union([p[0] for p in parts]);frame,_,_=runtime[iid];i=interfaces_by_id[iid]
        op=model.by_guid(opening);fill=model.by_guid(filling)
        voids=[r.GlobalId for r in op.VoidsElements if r.RelatingBuildingElement.GlobalId==i['parede']]
        fills=[r.GlobalId for r in op.HasFillings if r.RelatedBuildingElement.GlobalId==filling]
        assert len(voids)==len(fills)==1
        for k,part in enumerate(polygon_parts(geom)):
            opening_pieces.append({'id':f'A{len(opening_pieces)+1:03d}','interface':iid,'parede':i['parede'],
              'abertura':opening,'preenchimento':filling,'classe_preenchimento':fill.is_a(),'nome_preenchimento':fill.Name,
              'relacao_voids':voids[0],'relacao_fills':fills[0],'recortes_ifc2sb':sorted(set(p[1] for p in parts)),
              'area_recorte_m2':float(part.area),'wkt':polygon3_wkt(polygon_xyz(frame,part)),
              'qualificada_no_criterio':i['qualificada_no_criterio'],'validacao_arquitetonica':'pendente'})
    assessed=[]
    for op in pilot['aberturas']:
        associated=[p for p in opening_pieces if p['abertura']==op['abertura']]
        assessed.append({'abertura':op['abertura'],'parede':op['parede'],'preenchimento':op['preenchimento'],
          'classe':op['classe_preenchimento'],'nome':op['nome_preenchimento'],'estado_anterior':op['estado'],
          'recortes_na_interface':len(associated),'recortes_qualificados':sum(p['qualificada_no_criterio'] for p in associated),
          'estado':'associacao_geometrica_ao_recorte' if associated else 'sem_associacao_pelo_criterio',
          'area_total_recortes_m2':sum(p['area_recorte_m2'] for p in associated),
          'nota':'Soma sobre interfaces examinadas; não é área líquida arquitetônica ou de vidro.'})
    result={'procedimento':'adaptação híbrida experimental; não reprodução integral de Kiavarz, IFC2SB ou Krijnen',
      'sha256_ifc':IFC_SHA,'ifc_original_preservado':sha(ifc_path)==IFC_SHA,'ambiente':pilot['ambiente'],'nome':pilot['nome'],
      'entradas':{'piloto_sha256':sha(pilot_path),'geometrias_ifc2sb_sha256':sha(archive),'comparacao_cgal_sha256':sha(cgal_path)},
      'topologia_ambiente':topology,'centro_volume_ambiente_xyz_m':room_center,
      'parametros':{'distancia_planos_m':GAP_M,'area_min_m2':AREA_MIN,'tolerancia_produto_normal':NORMAL_TOL,'sonda_principal_m':1e-3},
      'interfaces':interfaces,'recortes_aberturas':opening_pieces,'avaliacao_aberturas':assessed,
      'diagnostico_selecao_faces':diagnostics,'conferencia_ancestralidade':checks,
      'faces_nao_cobertas':unsupported,'recortes_nao_aceitos':source_errors,
      'limites_declarados_ifc':len(model.by_type('IfcRelSpaceBoundary')),
      'resumo':{'paredes_candidatas':34,'interfaces':len(interfaces),'interfaces_qualificadas':sum(i['qualificada_no_criterio'] for i in interfaces),
       'paredes_com_interface':len({i['parede'] for i in interfaces}),'recortes_aberturas':len(opening_pieces),
       'aberturas_associadas':sum(r['recortes_na_interface']>0 for r in assessed),'aberturas_examinadas':len(assessed),
       'interfaces_sensibilidade_sondas':sum(not i['sensibilidade_sondas']['estavel'] for i in interfaces),
       'recortes_com_problema_parental':len(source_errors),'faces_nao_cobertas':len(unsupported)},
      'limite':'Mesmo IFC e motores derivados; sem padrão-ouro arquitetônico. Krijnen é sinal global da parede, não conflito localizado em cada abertura. Os casos negativos e inconclusivos permanecem.',
      'segundos':time.perf_counter()-t}
    save(out/'Resultado_Hibrido_Kiavarz_v01.json',result)
    write_csv(out/'Interfaces_Por_Ambiente.csv',[{k:v for k,v in i.items() if k not in ['wkt','sondas','sensibilidade_sondas']} for i in interfaces])
    write_csv(out/'Aberturas_Por_Interface.csv',[{k:v for k,v in p.items() if k!='wkt'} for p in opening_pieces])
    write_csv(out/'Todas_Aberturas_Avaliadas.csv',assessed)
    assert len(assessed)==24 and result['ifc_original_preservado']
    print(json.dumps(result['resumo'],ensure_ascii=False,indent=2));return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ifc');p.add_argument('piloto');p.add_argument('cgal');p.add_argument('saida')
    a=p.parse_args();run(a.ifc,a.piloto,a.cgal,a.saida)
