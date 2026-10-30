"""Controles analíticos da adaptação; não validação arquitetônica da creche.
Expectativas provêm das dimensões fornecidas, não das saídas do piloto.
Kiavarz et al. (2023), §§4.2.2-4.4 e Tabela 5; diferenças no manifesto.
"""
from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,Point
from faces_kiavarz import *

def rect(id,x0,x1,y,z0,z1,n):
    return PlaneFace.create(id,[[[x0,y,z0],[x1,y,z0],[x1,y,z1],[x0,y,z1]]],n)

def prism_faces(outline,z0=0,z1=3):
    out=[]
    for k,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
        dx,dy=b[0]-a[0],b[1]-a[1]
        out.append(PlaneFace.create(f'side{k}',[[[*a,z0],[*b,z0],[*b,z1],[*a,z1]]],[dy,-dx,0]))
    out.extend([PlaneFace.create('floor',[[[x,y,z0] for x,y in outline]],[0,0,-1]),
                PlaneFace.create('ceiling',[[[x,y,z1] for x,y in outline]],[0,0,1])])
    return out

def run(out):
    rows=[]
    def add(name,ok,obtained,expected):rows.append({'teste':name,'aprovado':bool(ok),'obtido':obtained,'esperado':expected})
    r=rect('room',1,3,0,0,3,[0,-1,0]);w=rect('wall',0,4,0,0,3,[0,1,0])
    cut,rec=clipped_interface(r,w);add('recorte_vertical_xyz',abs(cut.area-6)<1e-9,cut.area,6)
    rot=np.array([[math.cos(.6),-math.sin(.6),0],[math.sin(.6),math.cos(.6),0],[0,0,1]])
    rr=PlaneFace.create('rot-r',[a@rot.T for a in r.rings],rot@r.normal)
    ww=PlaneFace.create('rot-w',[a@rot.T for a in w.rings],rot@w.normal)
    x,_=clipped_interface(rr,ww);add('invariancia_rotacao_3d',abs(x.area-6)<1e-9,x.area,6)
    tr=np.array([1e6,2e6,0])
    rt=PlaneFace.create('tr-r',[a+tr for a in r.rings],r.normal);wt=PlaneFace.create('tr-w',[a+tr for a in w.rings],w.normal)
    x,_=clipped_interface(rt,wt);add('referencial_transladado',abs(x.area-6)<1e-7,x.area,6)
    x,d=clipped_interface(r,rect('far',0,4,.2,0,3,[0,1,0]));add('projecao_distante_recusada',x is None,d['estado'],'planos_separados')
    x,d=clipped_interface(r,rect('same',0,4,0,0,3,[0,-1,0]));add('normal_mesmo_sentido_recusada',x is None,d['estado'],'normais_nao_opostas')
    x,d=clipped_interface(r,rect('edge',3,4,0,0,3,[0,1,0]));add('contato_so_em_aresta_sem_area',x is None,d['estado'],'sem_area_comum')
    hf=PlaneFace.create('hole',[[[0,0,0],[4,0,0],[4,0,3],[0,0,3]],[[1,0,1],[2,0,1],[2,0,2],[1,0,2]]],[0,-1,0])
    x,_=clipped_interface(hf,w);add('anel_interior_preservado',abs(x.area-11)<1e-9,x.area,11)
    x,_=clipped_interface(hf,rect('in-hole',1,2,0,1,2,[0,1,0]));add('abertura_no_vazio_nao_vira_parede',x is None,x is None,True)
    outline=[[0,0],[4,0],[4,1],[1,1],[1,4],[0,4]];faces=prism_faces(outline)
    lp=Polygon(outline);add('centroide_sala_concava_pode_ficar_fora',not lp.covers(lp.centroid),list(lp.centroid.coords)[0],'fora do polígono L')
    def classify_l(p):
        x,y,z=p
        if 0<x<4 and 0<y<4 and (x<1 or y<1) and 0<z<3:return 'IN'
        return 'OUT'
    left=next(f for f in faces if np.allclose(f.normal,[-1,0,0]));wall_left=PlaneFace.create('leftwall',left.rings,[1,0,0])
    clip,_=clipped_interface(left,wall_left);probe=probe_interface(left,clip,wall_left.normal,faces,classify_l)
    add('raio_e_sondas_sala_concava',probe['qualificada_no_criterio'],probe['qualificacao_local'],'apoiada_pelas_sondas_e_raio')
    add('raio_apontado_para_fora',len(ray_hits([0,2,1.5],[-1,0,0],faces))==0,len(ray_hits([0,2,1.5],[-1,0,0],faces)),0)
    floor=faces[-2];square=PlaneFace.create('square',[[[0,0,0],[4,0,0],[4,4,0],[0,4,0]]],[0,0,1])
    x,_=clipped_interface(floor,square);add('recorte_poligono_concavo',abs(x.area-7)<1e-9,x.area,7)
    # Parede comprida e porta exclusiva de uma das regiões. GUID do hospedeiro
    # sozinho não resolve a relação: as áreas esperadas são 1 e 0 m².
    a=rect('roomA',0,2,0,0,3,[0,-1,0]);b=rect('roomB',2,4,0,0,3,[0,-1,0]);door=rect('door',.5,1.5,0,.5,1.5,[0,1,0])
    aa,_=clipped_interface(a,door);bb,_=clipped_interface(b,door)
    add('hospedeiro_compartilhado_porta_localizada',abs(aa.area-1)<1e-9 and bb is None,[aa.area,0 if bb is None else bb.area],[1,0])
    # Demonstrações das ambiguidades do texto, sem atribuir correção aos autores.
    cube_faces=prism_faces([[0,0],[4,0],[4,.2],[0,.2]])
    diag=face_pair_diagnostic(cube_faces,[2,2,1.5]);small=diag['literal_ordem_crescente']['areas_m2'];big=diag['adaptacao_ordem_decrescente']['areas_m2']
    add('ordem_crescente_nao_seleciona_faces_principais_da_parede',max(small)<min(big),[small,big],[[.6,.6],[12,12]])
    add('produto_escalar_zero_e_perpendicularidade',float(np.dot([1,0,0],[0,1,0]))==0 and np.linalg.norm(np.cross([1,0,0],[0,1,0]))==1,[0,1],'normais perpendiculares; não paralelas')
    try:Polygon([(0,0),(1,0),(1,1),(0,1)]).intersects(Polygon([(0,0),(1,0),(1,1),(0,1)])).area;error=False
    except AttributeError:error=True
    add('tabela5_intersects_area_incompativel_com_api',error,error,'AttributeError esperado; usar intersection(...).area')
    try:PlaneFace.create('invalid',[[[0,0,0],[1,0,1],[0,0,1],[1,0,0]]],[0,1,0]);refused=False
    except ValueError:refused=True
    add('poligono_invalido_nao_reparado_silenciosamente',refused,refused,True)
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    result={'total':len(rows),'aprovados':sum(r['aprovado'] for r in rows),'testes':rows,
      'alcance':'Controles de dimensões conhecidas e API; não validação independente da arquitetura da creche.'}
    (p/'Controles_Kiavarz_v01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    assert result['aprovados']==result['total'],[r for r in rows if not r['aprovado']]
    print('CONTROLES',result['aprovados'],'/',result['total']);return result
if __name__=='__main__':run(Path(__file__).resolve().parent/'controles')
