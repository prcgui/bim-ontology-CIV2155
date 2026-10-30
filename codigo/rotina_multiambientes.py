"""Generaliza o núcleo IFC2SB parcial + Kiavarz para todos os IfcSpace.

Fichter (2021), DOI 10.26868/25222708.2021.30156: recortes/ancestralidade.
Kiavarz (2023), DOI 10.3390/buildings13020350: faces, projeção e sondas.
Sem alterar tolerâncias por cômodo; sem usar a referência documental na previsão.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,csv,time
import numpy as np
from shapely.ops import unary_union
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_OUT,TopAbs_ON
from OCP.gp import gp_Pnt
from ifc2sb_faces import read_brep
from faces_kiavarz import PlaneFace,clipped_interface,probe_interface,polygon_parts,polygon_xyz,polygon3_wkt,AREA_MIN,GAP_M,NORMAL_TOL
from preparar_geometria import SHA,sha,save

PARAMS={'desvio_max_projecao_planar_m':1e-4,'distancia_planos_m':GAP_M,'area_min_m2':AREA_MIN,'tol_normal':NORMAL_TOL,
 'sonda_principal_m':.001,'tolerancia_classificacao_m':1e-7,'tolerancia_contorno_parental_m2':1e-7,
 'tolerancia_internos_m':1e-5,'distancia_componente_m':.25,'margem_componente_m':.02}

def near(a,b,margin=1e-4):return all(a[i]<=b[i+3]+margin and b[i]<=a[i+3]+margin for i in range(3))
def frame(d):return PlaneFace.from_wkt(d['id'],d['wkt'],d['normal'])
def classify(solid,point,tol=1e-7):
    state=BRepClass3d_SolidClassifier(solid,gp_Pnt(*map(float,point)),tol).State()
    return 'IN' if state==TopAbs_IN else 'OUT' if state==TopAbs_OUT else 'ON' if state==TopAbs_ON else 'UNKNOWN'
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)

class RotinaMultiambientes:
    def __init__(self,cache):
        self.cache=Path(cache);self.data=json.loads((self.cache/'Catalogo_Geometria.json').read_text(encoding='utf8'))
        if self.data['ifc_sha256']!=SHA:raise ValueError('Cache de outro IFC.')
        self.rooms={r['guid']:r for r in self.data['espacos']};self.walls={};self.frames={}
        self.products={r['guid']:r for r in self.data['produtos']}
        self.openings={r['guid']:r for r in self.data['aberturas']}
        for r in self.data['paredes']:
            if sha(self.cache/r['arquivo'])!=r['sha256']:raise ValueError('Cache de parede alterado: '+r['guid'])
    def wall(self,guid):
        if guid not in self.walls:
            d=next(r for r in self.data['paredes'] if r['guid']==guid)
            r=json.loads((self.cache/d['arquivo']).read_text(encoding='utf8'));self.walls[guid]=r
            parent_frames={};patches=[];issues=[dict(x) for x in r.get('diagnosticos_recorte',[]) if x.get('estado') in ['abertura_inconclusiva_sem_aproximacao','ramo_fallback_nao_portado']]
            for parent in r['faces_parentais']:
                try:parent_frames[parent['indice']]=frame(parent)
                except ValueError as exc:issues.append({'face':parent['indice'],'motivo':str(exc)})
            for patch in r['recortes']:
                try:
                    p=frame(patch);parent=parent_frames.get(patch['indice_parental'])
                    if parent is None or not patch['check_parent']['ok']:raise ValueError('ancestralidade_nao_aceita')
                    outside=parent.projected(p).difference(parent.polygon).area
                    if outside>PARAMS['tolerancia_contorno_parental_m2']:raise ValueError('recorte_fora_contorno_parental')
                    patches.append((patch,p))
                except ValueError as exc:issues.append({'recorte':patch['id'],'motivo':str(exc)})
            self.frames[guid]=(parent_frames,patches,issues)
        return self.walls[guid],self.frames[guid]
    def executar_ambiente(self,guid,out):
        if guid not in self.rooms:raise ValueError('GUID não identifica um IfcSpace do IFC preparado.')
        started=time.perf_counter();room=self.rooms[guid];out=Path(out);out.mkdir(parents=True,exist_ok=True)
        d={'ambiente':guid,'nome':room['nome'],'ifc_sha256':SHA,'parametros':PARAMS,
          'preparacao_geometrica':room.get('preparacao'),'sha256_brep':room.get('sha256_brep'),
          'estado':'inconclusivo_preparacao_espaco','interfaces':[],'recortes_aberturas':[],
          'esquadrias_associadas':[],'outros_preenchimentos':[],'elementos_internos_candidatos':[],
          'componentes_sem_FillsVoids_candidatos':[],'problemas':[]}
        if not room['estado'].startswith('volume_'):
            d['motivo']=room.get('motivo',room['estado']);d['segundos']=time.perf_counter()-started
            d['resumo']={'interfaces':None,'esquadrias':None,'internos':None,'componentes':None}
            save(out/'Resultado_Ambiente.json',d);return d
        if sha(self.cache/room['arquivo_brep'])!=room['sha256_brep']:raise ValueError('BRep de espaço alterado.')
        solid=read_brep((self.cache/room['arquivo_brep']).read_bytes());room_faces=[]
        for r in room['faces']:
            try:room_faces.append(frame(r))
            except ValueError as exc:d['problemas'].append({'face_espaco':r['id'],'motivo':str(exc)})
        d['problemas'].extend(room.get('faces_nao_cobertas',[]))
        candidates=[w for w in self.data['paredes'] if w.get('bbox') and near(room['bbox'],w['bbox'])]
        d['paredes_prefiltradas']=len(candidates)
        d['paredes_globais_sem_geometria']=[w['guid'] for w in self.data['paredes'] if not w.get('bbox')]
        runtime={};wall_runtime={}
        for wall_entry in candidates:
            wall,(parents,patches,issues)=self.wall(wall_entry['guid']);wall_runtime[wall['guid']]=(parents,patches)
            if wall['estado']!='recorte_preparado':
                d['problemas'].append({'parede':wall['guid'],'motivo':wall.get('motivo',wall['estado'])});continue
            for issue in issues:d['problemas'].append({'parede':wall['guid'],**issue})
            for i,pf in parents.items():
                for rf in room_faces:
                    clipped,info=clipped_interface(rf,pf)
                    if clipped is None:continue
                    for k,p in enumerate(polygon_parts(clipped)):
                        iid=f'{wall["guid"]}_F{i:03d}_{rf.id}_P{k}'
                        probe=probe_interface(rf,p,pf.normal,room_faces,lambda q:classify(solid,q))
                        sensitivity=[probe_interface(rf,p,pf.normal,room_faces,lambda q:classify(solid,q),step=st)['qualificada_no_criterio'] for st in [.0001,.001,.002]]
                        r={**info,'id':iid,'parede':wall['guid'],'nome_parede':wall['nome'],'face_parede':i,'face_ambiente':rf.id,
                           'area_m2':float(p.area),'wkt':polygon3_wkt(polygon_xyz(rf,p)),
                           'normal_ambiente':rf.normal.tolist(),'qualificada_no_criterio':probe['qualificada_no_criterio'],
                           'sondas':probe,'sondas_estaveis':len(set(sensitivity))==1}
                        d['interfaces'].append(r);runtime[iid]=(rf,p,r)
        grouped=defaultdict(list)
        for interface in d['interfaces']:
            rf,poly,_=runtime[interface['id']]
            _,patches=wall_runtime[interface['parede']]
            for patch,pf in patches:
                if patch['indice_parental']!=interface['face_parede']:continue
                overlap=rf.projected(pf).intersection(poly)
                if overlap.area>AREA_MIN:grouped[(interface['id'],patch['abertura'],patch['preenchimento'])].append(overlap)
        for (iid,opening,fill),polys in grouped.items():
            f,_,interface=runtime[iid];p=unary_union(polys);product=self.products[fill]
            for k,part in enumerate(polygon_parts(p)):
                d['recortes_aberturas'].append({'id':f'A{len(d["recortes_aberturas"])+1:03d}','interface':iid,
                  'parede':interface['parede'],'abertura':opening,'preenchimento':fill,'classe':product['classe'],'nome':product['nome'],
                  'area_m2':float(part.area),'wkt':polygon3_wkt(polygon_xyz(f,part)),
                  'qualificada_no_criterio':interface['qualificada_no_criterio']})
        associated=defaultdict(list)
        for r in d['recortes_aberturas']:
            if r['qualificada_no_criterio']:associated[r['preenchimento']].append(r)
        for fill,patches in associated.items():
            p=self.products[fill];record={'guid':fill,'nome':p['nome'],'classe':p['classe'],
                'interfaces':sorted({r['interface'] for r in patches}),'aberturas':sorted({r['abertura'] for r in patches})}
            (d['esquadrias_associadas'] if p['classe'] in ['IfcDoor','IfcWindow'] else d['outros_preenchimentos']).append(record)
        # Critério candidato de localização compartilhado no lote; não prova contenção.
        for product in self.products.values():
            if product.get('estado_geometria')!='disponivel' or not near(room['bbox'],product['bbox'],.6):continue
            if product['classe']=='IfcWall' and product['aberturas_declaradas']:
                states=[classify(solid,p,tol=PARAMS['tolerancia_internos_m']) for p in product['vertices_xyz_m']]
                if states and all(s in ['IN','ON'] for s in states) and 'IN' in states:
                    d['elementos_internos_candidatos'].append({'guid':product['guid'],'nome':product['nome'],'estados_vertices':dict(Counter(states))})
            if product['classe'] in ['IfcDoor','IfcWindow'] and not product['aberturas_declaradas']:
                matches=[];a=np.asarray(product['bbox'][:3]);b=np.asarray(product['bbox'][3:])
                for fill in d['esquadrias_associadas']:
                    target=self.products[fill['guid']];c=np.asarray(target['bbox'][:3]);e=np.asarray(target['bbox'][3:])
                    gap=float(np.linalg.norm(np.maximum(np.maximum(a-e,c-b),0)))
                    thin=int(np.argmin(e-c));axes=[i for i in range(3) if i!=thin];center=(a+b)/2
                    if gap<=.25 and all(c[i]-.02<=center[i]<=e[i]+.02 for i in axes):matches.append(fill['guid'])
                if matches:d['componentes_sem_FillsVoids_candidatos'].append({'guid':product['guid'],'nome':product['nome'],'preenchimentos_alvo':matches})
        d['estado']='associacao_executada_com_pendencias' if d['problemas'] or room.get('faces_nao_cobertas') else 'associacao_executada'
        d['resumo']={'interfaces':len(d['interfaces']),'interfaces_qualificadas':sum(i['qualificada_no_criterio'] for i in d['interfaces']),
          'paredes_com_interface':len({i['parede'] for i in d['interfaces']}),'esquadrias':len(d['esquadrias_associadas']),
          'outros_preenchimentos':len(d['outros_preenchimentos']),'internos':len(d['elementos_internos_candidatos']),
          'componentes':len(d['componentes_sem_FillsVoids_candidatos']),'problemas':len(d['problemas'])}
        d['segundos']=time.perf_counter()-started;save(out/'Resultado_Ambiente.json',d);return d

def executar_lote(ifc_path,cache,out):
    started=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if sha(ifc_path)!=SHA:raise ValueError('IFC não corresponde à fonte fixada do cache.')
    routine=RotinaMultiambientes(cache);results=[]
    for i,room in enumerate(routine.data['espacos']):
        r=routine.executar_ambiente(room['guid'],out/'ambientes'/room['guid']);results.append(r)
        print('AMBIENTE',i+1,'/',len(routine.rooms),r['nome'],r['estado'],r['resumo'],flush=True)
    rows=[{'ambiente':r['ambiente'],'nome':r['nome'],'estado':r['estado'],'motivo':r.get('motivo',''),**r['resumo']} for r in results]
    write_csv(out/'Cobertura_Ambientes.csv',rows)
    prediction_rows=[{'ambiente':r['ambiente'],'nome_ambiente':r['nome'],**e} for r in results for e in r['esquadrias_associadas']]
    write_csv(out/'Esquadrias_Por_Ambiente.csv',prediction_rows)
    summary={'ifc_sha256':SHA,'parametros_comuns':PARAMS,'estados':dict(Counter(r['estado'] for r in results)),
       'espacos_solicitados':len(results),'espacos_com_associacao_executada':sum(r['estado'].startswith('associacao_') for r in results),
       'espacos_inconclusivos':sum(r['estado'].startswith('inconclusivo_') for r in results),
       'pares_ambiente_esquadria':len(prediction_rows),'esquadrias_distintas_associadas':len({r['guid'] for r in prediction_rows}),
       'cache_catalogo_sha256':sha(Path(cache)/'Catalogo_Geometria.json'),'preparo_global':routine.data['resumo'],
       'limite':'Aplicação geométrica em 41 espaços; não confundir execução com validação documental de todos os casos.',
       'ifc_original_preservado':sha(ifc_path)==SHA,'segundos_associacao':time.perf_counter()-started}
    save(out/'Resumo_Lote.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True);return summary

if __name__=='__main__':
    import sys
    executar_lote(sys.argv[1],sys.argv[2],sys.argv[3])
