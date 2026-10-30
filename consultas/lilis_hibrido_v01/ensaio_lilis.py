"""Ensaio parcial de Lilis et al. 2026 no IFC original, sem repará-lo.

Implementa IP/IPS (Alg. 1), PSS (Alg. 2), pares de espaços (Alg. 3)
e recortes por maxA (Alg. 5). Integra os recortes às interfaces do
procedimento híbrido anterior. Alg. 4 (alpha wrap) não foi implementado;
por isso os resíduos não são rotulados como superfícies externas 2a.
Não gera BEM completo, gbXML nem IfcRelSpaceBoundary no IFC.
"""
from pathlib import Path
import json,hashlib,time,csv
from collections import defaultdict
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pnt
from ifc2sb_faces import (read_brep,closed_space_solid,shapes,polygon_wkt,normal,
    TopAbs_FACE,TopAbs_SOLID,TopoDS,BRepAdaptor_Surface,GeomAbs_Plane,volume,BRepCheck_Analyzer,common,area)
from faces_kiavarz import PlaneFace,polygon_parts,polygon_xyz,polygon3_wkt,AREA_MIN
from operadores_lilis import *

IFC_SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
ROOM='3UFjAT4k55zg_Pqo6VMw5l'
DISTANCES=[.05,.15,.30,.60]
MAIN_D=.30

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def csv_write(p,rows):
    if not rows:return
    with Path(p).open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader();w.writerows(rows)

def bbox(shape):
    b=Bnd_Box();BRepBndLib.Add_s(shape,b);return list(b.Get())
def nearby(a,b,d):return all(a[k]<=b[k+3]+d and b[k]<=a[k+3]+d for k in range(3))

def polygon_brep(frame,polygon):
    """Validação cruzada do estudo: face planar original -> Common com volume.
    API OCCT BRepBuilderAPI_MakeFace e BRepAlgoAPI_Common; não etapa de Lilis.
    """
    from shapely.geometry.polygon import orient
    polygon=orient(polygon,sign=1)
    def wire(coords):
        make=BRepBuilderAPI_MakePolygon()
        for xyz in frame.xyz(list(coords)[:-1]):make.Add(gp_Pnt(*map(float,xyz)))
        make.Close();return make.Wire()
    make=BRepBuilderAPI_MakeFace(wire(polygon.exterior.coords))
    for hole in polygon.interiors:make.Add(wire(hole.coords))
    if not make.IsDone():raise ValueError('Construção da face de conferência falhou')
    return make.Face()

def as_faces(shape,prefix):
    faces=[];unsupported=[]
    for i,f in enumerate(shapes(shape,TopAbs_FACE)):
        id=f'{prefix}_F{i:03d}'
        try:
            if BRepAdaptor_Surface(f).GetType()!=GeomAbs_Plane:raise ValueError('superficie_curva')
            n=normal(f);faces.append(PlaneFace.from_wkt(id,polygon_wkt(f),[n.X(),n.Y(),n.Z()]))
        except ValueError as e:unsupported.append({'face':id,'motivo':str(e)})
    return faces,unsupported

def run(ifc_path,hybrid_path,triage_path,out):
    started=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    assert sha(ifc_path)==IFC_SHA
    hybrid=json.loads(Path(hybrid_path).read_text(encoding='utf8'))
    triage=json.loads(Path(triage_path).read_text(encoding='utf8'))
    assert hybrid['sha256_ifc']==triage['sha256_ifc']==IFC_SHA
    model=ifcopenshell.open(str(ifc_path));settings=ifcopenshell.geom.settings()
    settings.set('iterator-output',W.SERIALIZED);settings.set('use-world-coords',True)
    settings.set('convert-back-units',False);settings.set('disable-opening-subtractions',True)
    cache={}
    def brep(entity):
        if entity.GlobalId not in cache:
            holder=ifcopenshell.geom.create_shape(settings,entity)
            cache[entity.GlobalId]=read_brep(holder.geometry.brep_data)
        return cache[entity.GlobalId]
    room,room_info=closed_space_solid(brep(model.by_guid(ROOM)))
    room_faces,room_errors=as_faces(room,'COZINHA');box=bbox(room)
    assert len(room_faces)==room_info['faces_saida'] and not room_errors
    old_ids={r['abertura'] for r in hybrid['avaliacao_aberturas']}
    old_by_id={r['abertura']:r for r in hybrid['avaliacao_aberturas']}
    old_interfaces={r['id']:r for r in hybrid['interfaces']}
    frames={id:PlaneFace.from_wkt(id,r['wkt'],r['normal_ambiente']) for id,r in old_interfaces.items()}
    openings=[];all_checks=[]
    # Examina TODOS os 184 IfcOpeningElement: BBox é somente pré-filtro.
    for e in model.by_type('IfcOpeningElement'):
        record={'abertura':e.GlobalId,'no_piloto_anterior':e.GlobalId in old_ids}
        try:
            raw=brep(e);bb=bbox(raw)
            if not nearby(box,bb,max(DISTANCES)):
                all_checks.append(dict(record,estado='fora_do_prefiltro_espacial'));continue
            solids=shapes(raw,TopAbs_SOLID)
            if not solids or not all(BRepCheck_Analyzer(s).IsValid() for s in solids):
                all_checks.append(dict(record,estado='sem_conjunto_de_solidos_validos'));continue
            groups=[];errors=[]
            for j,s in enumerate(solids):
                # A abertura pode ter múltiplos sólidos. Não usa Sewing monocomponente.
                if volume(s)<0:s=s.Complemented()
                fs,err=as_faces(s,f'{e.GlobalId}_C{j:02d}');groups.append(fs);errors.extend(err)
            hosts=[r.RelatingBuildingElement.GlobalId for r in e.VoidsElements]
            fills=[{'guid':r.RelatedBuildingElement.GlobalId,'classe':r.RelatedBuildingElement.is_a(),
                    'nome':r.RelatedBuildingElement.Name,'relacao':r.GlobalId} for r in e.HasFillings]
            r=dict(record,estado='avaliada_no_ensaio',solidos=len(solids),faces_planas=sum(map(len,groups)),
                   faces_nao_cobertas=errors,paredes_hospedeiras=hosts,preenchimentos=fills)
            openings.append((r,groups));all_checks.append(r)
        except (RuntimeError,ValueError) as e2:all_checks.append(dict(record,estado='inconclusivo_geometria',motivo=str(e2)))
    # Alg. 3: somente pares cozinha/outro espaço aceito e sem interseção volumétrica.
    pair_checks=[];internal=[]
    pair_info={frozenset([r['a'],r['b']]):r for r in triage['pares_espacos']}
    for r in triage['espacos']:
        if r['guid']==ROOM:continue
        rec={'cozinha':ROOM,'outro_espaco':r['guid'],'nome':r['nome']}
        if r['estado']!='volume_fechado_aceito':
            pair_checks.append(dict(rec,estado='volume_nao_aceito_na_preparacao_anterior'));continue
        status=pair_info[frozenset([ROOM,r['guid']])]
        if status['estado'] not in ['sem_sobreposicao_interior_bbox_no_criterio','sem_volume_comum_acima_limiar']:
            pair_checks.append(dict(rec,estado='par_nao_aceito_por_sobreposicao_ou_inconclusao',diagnostico=status));continue
        solid,_=closed_space_solid(brep(model.by_guid(r['guid'])))
        if not nearby(box,bbox(solid),max(DISTANCES)):
            pair_checks.append(dict(rec,estado='fora_do_prefiltro_espacial'));continue
        fs,err=as_faces(solid,r['guid']);n_by_d={}
        for d in DISTANCES:
            pairs=ips_d(room_faces,fs,d);n_by_d[str(d)]=len(pairs)
            if d==MAIN_D:
                for fa,fb,(pa,pb),info in pairs:
                    for k,p in enumerate(polygon_parts(pa)):
                        internal.append({'id':f'V{len(internal)+1:03d}','face_cozinha':fa.id,'outro_espaco':r['guid'],
                         'nome_outro_espaco':r['nome'],'face_outro_espaco':fb.id,'wkt_cozinha':polygon3_wkt(polygon_xyz(fa,p)),
                         'normal_cozinha':fa.normal.tolist(),'wkt_outro_espaco':[polygon3_wkt(polygon_xyz(fb,q)) for q in polygon_parts(pb)],
                         'area_cozinha_m2':float(p.area),'medidas':info,'estado':'par_candidato_por_IPS; validacao_arquitetonica_pendente'})
        pair_checks.append(dict(rec,estado='IPS_executado',pares_por_d=n_by_d,faces_nao_cobertas=err))
    # Alg. 5 em faces do espaço; mesma maxA para B/O e B/-O.
    raw_pieces=[];audits=[];sensitivity=[]
    for d in DISTANCES:
        for mode in ['maxA_global_artigo','maxA_por_componente_extensao']:
            total=0;ids=set();masked=[]
            for op,groups in openings:
                sets=[sum(groups,[])] if mode=='maxA_global_artigo' else groups
                for rf in room_faces:
                    parts=[];origins=[]
                    for j,group in enumerate(sets):
                        if not group:continue
                        poly,info=opening_on_boundary(rf,group,d)
                        if d==MAIN_D and mode=='maxA_global_artigo':
                            audits.append({'abertura':op['abertura'],'face_cozinha':rf.id,**info})
                        if poly is not None:parts.append(poly);origins.append(info)
                    if not parts:continue
                    candidate=unary_union(parts)
                    # Associação à parede é contribuição do híbrido, NÃO do método Lilis.
                    associations=[]
                    for iid,frame in frames.items():
                        old=old_interfaces[iid]
                        if old['parede'] not in op['paredes_hospedeiras'] or not coplanar(rf,frame):continue
                        clip=frame.projected(fragment(rf,candidate,'temp')) if isinstance(candidate,Polygon) else None
                        if clip is None:
                            clip=unary_union([frame.projected(fragment(rf,p,'tmp')) for p in polygon_parts(candidate)])
                        clip=clip.intersection(frame.polygon)
                        if clip.area>AREA_MIN:associations.append((iid,clip))
                    if associations:
                        ids.add(op['abertura']);masked.extend((op['abertura'],i,p.area) for i,p in associations)
                    total+=len(polygon_parts(candidate))
                    if d==MAIN_D and mode=='maxA_global_artigo':
                        for p in polygon_parts(candidate):
                            raw_pieces.append({'id':f'O{len(raw_pieces)+1:03d}','abertura':op['abertura'],'face_cozinha':rf.id,
                              'wkt':polygon3_wkt(polygon_xyz(rf,p)),'normal':rf.normal.tolist(),'area_m2':float(p.area),
                              'selecoes_maxA':origins,'interfaces_hospedeiras':[i for i,_ in associations],
                              'paredes_ifc':op['paredes_hospedeiras'],'preenchimentos':op['preenchimentos'],
                              'no_piloto_anterior':op['no_piloto_anterior']})
            sensitivity.append({'d_m':d,'variante':mode,'recortes_brutos':total,'aberturas_com_interface_hospedeira':len(ids),
                                'guids_associados':sorted(ids),'recortes_com_hospedeira':len(masked)})
    # PSS: resíduos no espaço, sem chamar de externos (Alg. 4 não executado).
    residues=[]
    for rf in room_faces:
        cuts=[PlaneFace.from_wkt(r['id'],r['wkt_cozinha'],r['normal_cozinha']) for r in internal if r['face_cozinha']==rf.id]
        remain=pss(rf,cuts)
        residues.append({'face_cozinha':rf.id,'area_bruta_m2':float(rf.polygon.area),'area_residual_m2':float(remain.area),
                         'wkt_residual':[polygon3_wkt(polygon_xyz(rf,p)) for p in polygon_parts(remain)],
                         'estado':'residuo_sem_classificacao_externa; alpha_wrap_nao_executado'})
    # Recorta resultados do Alg. 5 dentro da interface confirmada no híbrido.
    local=[];net=[];geometry_comparison=[]
    for iid,frame in frames.items():
        polys=[];supported_polys=[]
        for op,groups in openings:
            pieces=[]
            for r in raw_pieces:
                if r['abertura']!=op['abertura'] or iid not in r['interfaces_hospedeiras']:continue
                f=PlaneFace.from_wkt(r['id'],r['wkt'],r['normal'])
                pieces.append(frame.polygon.intersection(frame.projected(f)))
            if not pieces:continue
            p=unary_union(pieces)
            if p.area<=AREA_MIN:continue
            polys.append(p)
            old=[r for r in hybrid['recortes_aberturas'] if r['interface']==iid and r['abertura']==op['abertura']]
            old_polys=[frame.projected(PlaneFace.from_wkt(r['id'],r['wkt'],frame.normal)) for r in old]
            ref=unary_union(old_polys)
            agreement=float(p.intersection(ref).area);new=float(p.difference(ref).area)
            # Confere a projeção contra a interseção 3D com o volume REAL da abertura.
            # Distingue recorte apoiado por volume de mera projeção através de um vão.
            direct=common(polygon_brep(frame,frame.polygon),brep(model.by_guid(op['abertura'])))
            direct_area=area(direct)
            direct_polys=[]
            for df in shapes(direct,TopAbs_FACE):
                n=normal(df)
                try:direct_polys.append(frame.projected(PlaneFace.from_wkt('common',polygon_wkt(df),[n.X(),n.Y(),n.Z()])))
                except ValueError:pass
            du=unary_union(direct_polys)
            supported=float(p.intersection(du).area)
            supported_polys.append(p.intersection(du))
            geom_check={'interface':iid,'abertura':op['abertura'],'area_anterior_m2':float(ref.area),'area_lilis_m2':float(p.area),
              'area_intersecao_anterior_m2':agreement,'area_nova_m2':new,'area_anterior_nao_reproduzida_m2':float(ref.difference(p).area),
              'area_diferenca_simetrica_m2':float(ref.symmetric_difference(p).area),'area_common_3D_m2':float(direct_area),
              'area_lilis_apoiada_common_3D_m2':supported,'area_lilis_sem_apoio_common_3D_m2':float(p.difference(du).area)}
            geometry_comparison.append(geom_check)
            for k,part in enumerate(polygon_parts(p)):
                unsupported=float(part.difference(du).area)
                local.append({'id':f'L{len(local)+1:03d}','interface':iid,'abertura':op['abertura'],
                  'parede':old_interfaces[iid]['parede'],'area_m2':float(part.area),'wkt':polygon3_wkt(polygon_xyz(frame,part)),
                  'normal':frame.normal.tolist(),'preenchimentos':op['preenchimentos'],'fontes_brutas':[r['id'] for r in raw_pieces if r['abertura']==op['abertura'] and iid in r['interfaces_hospedeiras']],
                  'area_intersecao_anterior_m2':agreement,'area_nao_coberta_anterior_m2':new,
                  'conferencia_volume_3D':geom_check,
                  'apoio_volume_3D_no_criterio':unsupported<=1e-7,
                  'area_sem_apoio_volume_3D_m2':unsupported,
                  'estado':'candidato_com_hospedeira_IFC; validacao_arquitetonica_pendente'})
        opening_union=unary_union(polys)
        supported_union=unary_union(supported_polys)
        cuts=[fragment(frame,p,f'c{k}') for k,p in enumerate(polygon_parts(opening_union))]
        opaque=pss(frame,cuts)
        conserved=abs(frame.polygon.area-opening_union.area-opaque.area)<1e-7
        assert conserved
        net.append({'interface':iid,'parede':old_interfaces[iid]['parede'],'area_bruta_m2':float(frame.polygon.area),
          'area_uniao_recortes_m2':float(opening_union.area),'area_residual_m2':float(opaque.area),
          'area_uniao_recortes_apoiados_3D_m2':float(supported_union.area),
          'area_residual_apos_recortes_apoiados_3D_m2':float(frame.polygon.difference(supported_union).area),
          'conservacao_area':conserved,'wkt_residual':[polygon3_wkt(polygon_xyz(frame,p)) for p in polygon_parts(opaque)],
          'normal':frame.normal.tolist(),'nota':'Resíduo geométrico; não área certificada de parede opaca ou de vidro.'})
    old_associated={r['abertura'] for r in hybrid['recortes_aberturas']}
    new_associated={r['abertura'] for r in local}
    comparison=[]
    for op,groups in openings:
        guid=op['abertura'];rs=[r for r in local if r['abertura']==guid]
        comparison.append({'abertura':guid,'no_piloto_anterior':guid in old_ids,'associada_antes':guid in old_associated,
          'associada_Lilis_hibrido':guid in new_associated,'nova_associacao_candidata':guid in new_associated-old_associated,
          'area_recortes_novos_m2':sum(r['area_m2'] for r in rs),'faces_do_espaco_com_recorte':len({r['face_cozinha'] for r in raw_pieces if r['abertura']==guid}),
          'paredes_ifc':op['paredes_hospedeiras'],'preenchimentos':op['preenchimentos']})
    result={'fonte':'https://doi.org/10.1016/j.autcon.2026.106840','natureza':'adaptação parcial do procedimento publicado: Alg. 1,2,3,5; não reprodução do código C++',
      'sha256_ifc':IFC_SHA,'entradas':{'hybrid_sha256':sha(hybrid_path),'triagem_sha256':sha(triage_path)},
      'ambiente':ROOM,'parametros':{'d_principal_m':MAIN_D,'d_sensibilidade_m':DISTANCES,'eps_normal':EPS_NORMAL,'tol_plano_PSS_m':PLANE_TOL},
      'preparacao_cozinha':room_info,'pares_espacos':pair_checks,'interfaces_entre_espacos':internal,
      'residuos_faces_espaco':residues,'recortes_brutos_alg5':raw_pieces,'recortes_hibridos':local,'areas_por_interface':net,
      'sensibilidade':sensitivity,'comparacao_aberturas':comparison,'avaliacao_todas_aberturas_ifc':all_checks,'auditoria_maxA':audits,
      'comparacao_geometrica':geometry_comparison,
      'resumo':{'aberturas_ifc_examinadas':len(all_checks),'aberturas_no_ensaio_local':len(openings),'faces_espaco':len(room_faces),
        'pares_faces_espacos_candidatos':len(internal),'recortes_brutos_alg5':len(raw_pieces),'recortes_hibridos':len(local),
        'aberturas_associadas_antes':len(old_associated),'aberturas_associadas_apos':len(new_associated),
        'novas_associacoes_candidatas':sorted(new_associated-old_associated),'associacoes_anteriores_nao_reproduzidas':sorted(old_associated-new_associated),
        'interfaces_com_area_residual':len(net),'area_bruta_interfaces_m2':sum(r['area_bruta_m2'] for r in net),
        'area_recortes_uniao_m2':sum(r['area_uniao_recortes_m2'] for r in net),'area_residual_m2':sum(r['area_residual_m2'] for r in net)},
      'limites':['Alg. 4/alpha wrap não implementado: resíduos não certificados como externos/2b.',
        'Somente cozinha e pares com volumes aceitos e sem sobreposição. Não reconstrói todos os 41 cômodos.',
        'Faces curvas não aproximadas; maxA global não substituído silenciosamente por recortes menores.',
        'Novas associações são candidatas; contagem maior não demonstra maior acurácia.',
        'Alg. 5 aplicado a faces brutas do espaço: substitui a entrada 2LSB filtrada do artigo; sem equivalência integral.',
        'Common 3D é conferência complementar do estudo, não regra de Lilis nem padrão-ouro arquitetônico.',
        'Não demonstradas todas as pré-condições entre volumes de espaços e aberturas neste IFC.',
        'Associação ao hospedeiro e RDF são extensões do estudo; Lilis não gera ontologia parede-porta.'],
      'ifc_original_preservado':sha(ifc_path)==IFC_SHA,'segundos':time.perf_counter()-started}
    result['resumo'].update({
        'recortes_com_apoio_volume_3D':sum(r['apoio_volume_3D_no_criterio'] for r in local),
        'recortes_sem_apoio_volume_3D':sum(not r['apoio_volume_3D_no_criterio'] for r in local),
        'area_uniao_recortes_apoiados_3D_m2':sum(r['area_uniao_recortes_apoiados_3D_m2'] for r in net),
        'area_residual_apos_recortes_apoiados_3D_m2':sum(r['area_residual_apos_recortes_apoiados_3D_m2'] for r in net),
        'tolerancia_area_conferencia_m2':1e-7})
    save(out/'Resultado_Lilis_Hibrido_v01.json',result)
    save(out/'Resumo_Lilis_Hibrido_v01.json',result['resumo'])
    csv_write(out/'Comparacao_Aberturas_Lilis_v01.csv',comparison);csv_write(out/'Sensibilidade_Distancia_Lilis_v01.csv',sensitivity)
    csv_write(out/'Areas_Interfaces_Lilis_v01.csv',[{k:v for k,v in r.items() if k not in ['wkt_residual','normal']} for r in net])
    csv_write(out/'Comparacao_Geometrica_Recortes_v01.csv',geometry_comparison)
    print(json.dumps(result['resumo'],ensure_ascii=False,indent=2));return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ifc');p.add_argument('hibrido');p.add_argument('triagem');p.add_argument('saida')
    a=p.parse_args();run(a.ifc,a.hibrido,a.triagem,a.saida)
