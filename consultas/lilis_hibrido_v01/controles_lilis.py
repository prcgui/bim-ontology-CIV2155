"""Controles geométricos com áreas/distâncias analíticas, não ajuste à creche.
Fonte dos operadores: Lilis et al. (2026), §§2 e 3.3.4.
"""
from pathlib import Path
import json,math
import numpy as np
from faces_kiavarz import PlaneFace
from operadores_lilis import *

def rect(id,x,y0=0,y1=2,z0=0,z1=3,n=1):
    return PlaneFace.create(id,[[[x,y0,z0],[x,y1,z0],[x,y1,z1],[x,y0,z1]]],[n,0,0])

def run(out):
    tests=[]
    def check(name,test):
        assert bool(test),name
        tests.append({'controle':name,'aprovado':True})
    a,b=rect('A',0),rect('B',.2,n=-1)
    p,_=ip_d(a,b,.3)
    check('duas_faces_separadas_20cm_area_6',p is not None and all(abs(g.area-6)<1e-10 for g in p))
    check('limiar_10cm_rejeita_20cm',ip_d(a,b,.1)[0] is None)
    check('limiar_exato_e_rejeitado',ip_d(a,b,.2)[0] is None)
    check('mesmo_sentido_rejeitado',ip_d(a,rect('C',.2),.3)[0] is None)
    p,_=ip_d(a,rect('D',.2,1,3,n=-1),.3)
    check('recorte_parcial_area_3',p and abs(p[0].area-3)<1e-10)
    check('contato_apenas_aresta_nao_produz_superficie',ip_d(a,rect('E',.2,2,4,n=-1),.3)[0] is None)
    # Tilt: B x=0.2+0.02*y, área 6*sqrt(1+.02²); projeções têm áreas distintas.
    tilt=PlaneFace.create('T',[[[.2,0,0],[.24,2,0],[.24,2,3],[.2,0,3]]],[-1,.02,0])
    p,_=ip_d(a,tilt,.3)
    check('projecao_nao_paralela_admitida',p is not None)
    check('planos_distintos_nao_forcam_areas_iguais',p and abs(p[0].area-p[1].area)>1e-6)
    far=PlaneFace.create('F',[[[.1,0,0],[.5,2,0],[.5,2,3],[.1,0,3]]],[-1,.2,0])
    check('todos_vertices_distancia_nao_so_centro',ip_d(a,far,.35)[0] is None)
    small=rect('pequena',.1,.5,1.5,.5,2.5,n=-1)
    cut=fragment(a,opening_on_boundary(a,[small],.3)[0],'abertura')
    remain=pss(a,[cut])
    check('PSS_area_liquida_4',abs(remain.area-4)<1e-10)
    check('PSS_preserva_um_furo',len(remain.interiors)==1)
    check('PSS_nao_subtrai_plano_distante',abs(pss(a,[small]).area-6)<1e-10)
    check('PSS_subtrai_face_invertida_coplanar',abs(pss(a,[reversed_face(cut)]).area-4)<1e-10)
    same=rect('mesmo',.1,.5,1.5,.5,2.5,n=1)
    check('Alg5_inverte_orientacao',abs(opening_on_boundary(a,[same],.3)[0].area-2)<1e-10)
    larger=rect('maior_longe',2,0,3,0,3,n=-1)
    check('maxA_nao_escolhe_face_menor_para_forcar_sucesso',opening_on_boundary(a,[small,larger],.3)[0] is None)
    check('maxA_sem_alinhamento_retorna_none',max_a([a],np.array([0,1,0])) is None)
    check('IPS_sem_pares_duplicados',len(ips_d([a,b],[a,b],.3,same_set=True))==1)
    shift=np.array([1e6,-2e6,3e6])
    tr=lambda f:PlaneFace.create(f.id,[r+shift for r in f.rings],f.normal)
    check('invariancia_translacao',abs(ip_d(tr(a),tr(b),.3)[0][0].area-6)<1e-8)
    angle=.7;rot=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
    rt=lambda f:PlaneFace.create(f.id,[r@rot.T for r in f.rings],f.normal@rot.T)
    check('invariancia_rotacao',abs(ip_d(rt(a),rt(b),.3)[0][0].area-6)<1e-9)
    # Dois recortes sobrepostos: área líquida usa união, não soma duplicada.
    c1=rect('c1',0,0,1.5,0,1);c2=rect('c2',0,.5,2,0,1)
    check('PSS_aberturas_sobrepostas_sem_dupla_subtracao',abs(pss(a,[c1,c2]).area-4)<1e-10)
    result={'fonte':'https://doi.org/10.1016/j.autcon.2026.106840','total':len(tests),'aprovados':len(tests),'controles':tests}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'Controles_Lilis_v01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('Controles Lilis:',len(tests),'aprovados');return result

if __name__=='__main__':
    import sys
    run(sys.argv[1])
