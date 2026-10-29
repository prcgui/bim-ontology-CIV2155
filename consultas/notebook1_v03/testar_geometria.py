"""Controles positivos/negativos independentes para a adaptação GRC.
Casos analíticos, sem referência ao resultado esperado da creche.
"""
if __name__=='__main__':
    import ambiente
import json,time,math
import numpy as np
import manifold3d as m
from geometria_relacoes import classify_pair,solid,mesh_diagnostics

def arrays(manifold):
    mesh=manifold.to_mesh64()
    return np.asarray(mesh.vert_properties[:,:3]),np.asarray(mesh.tri_verts,dtype=np.int64)

def run_tests():
    cases=[]
    def check(name,fn):
        start=time.perf_counter();fn();cases.append({'teste':name,'aprovado':True,'segundos':time.perf_counter()-start})
    unit=m.Manifold.cube((1,1,1))
    a,fa=arrays(unit)
    def contact():
        b,fb=arrays(unit.translate((1,0,0)));r=classify_pair(a,fa,b,fb)
        assert r['status']=='adjacencia_geometrica_no_limiar_numerico'
        assert abs(r['strict_area_m2']-1)<1e-8 and r['intersection_volume_m3']<1e-12
    check('Face comum: área analítica 1 m² e volume comum zero',contact)
    def near():
        b,fb=arrays(unit.translate((1.001,0,0)));r=classify_pair(a,fa,b,fb)
        assert r['status']=='proximidade_de_superficies' and r['strict_area_m2']==0
    check('Vão de 1 mm: proximidade, sem adjacência materializada',near)
    def gap():
        b,fb=arrays(unit.translate((1.01,0,0)));assert classify_pair(a,fa,b,fb) is None
    check('Vão de 10 mm: nenhuma relação no limiar de 2 mm',gap)
    def edge():
        b,fb=arrays(unit.translate((1,1,0)));assert classify_pair(a,fa,b,fb) is None
    check('Contato só em aresta: não constitui interface com área',edge)
    def point():
        b,fb=arrays(unit.translate((1,1,1)));assert classify_pair(a,fa,b,fb) is None
    check('Contato só em ponto: sem falsa adjacência por face',point)
    def rotation():
        ar,far=arrays(unit.rotate((21,17,33)).translate((5,-7,9)))
        br,fbr=arrays(unit.translate((1,0,0)).rotate((21,17,33)).translate((5,-7,9)))
        r=classify_pair(ar,far,br,fbr)
        assert r['status']=='adjacencia_geometrica_no_limiar_numerico' and abs(r['strict_area_m2']-1)<1e-6
    check('Rotação e translação 3D: contato preservado fora da planta XY',rotation)
    def concave():
        L=m.Manifold.cube((2,1,1))+m.Manifold.cube((1,2,1))
        av,af=arrays(L);bv,bf=arrays(m.Manifold.cube((.5,.5,.5)).translate((1.2,1.2,.2)))
        assert classify_pair(av,af,bv,bf) is None
    check('Sólido em L: sobreposição de caixas sem contato real',concave)
    def hole():
        shape=unit-m.Manifold.cube((.5,.5,2)).translate((.25,.25,-.5))
        av,af=arrays(shape);bv,bf=arrays(unit.translate((0,0,1)))
        r=classify_pair(av,af,bv,bf)
        assert abs(r['strict_area_m2']-.75)<1e-7
    check('Interface com furo: área 0,75 m², sem preencher o vazio',hole)
    def overlap():
        b,fb=arrays(unit.translate((.8,0,0)));r=classify_pair(a,fa,b,fb)
        assert r is None or r['status']!='adjacencia_geometrica_no_limiar_numerico'
        assert abs(float((solid(a,fa)^solid(b,fb)).volume())-.2)<1e-8
    check('Sobreposição volumétrica: não declarar adjacência disjunta',overlap)
    def open_mesh():assert solid(a,fa[:-1]) is None
    check('Malha aberta: recusa da validação volumétrica',open_mesh)
    def reverse():
        sm=solid(a,fa[:,[0,2,1]]);assert sm is not None and abs(sm.volume()-1)<1e-8
    check('Orientação global invertida: normalização só na malha derivada',reverse)
    def nonfinite():
        bad=a.copy();bad[0,0]=np.nan
        try:mesh_diagnostics(bad,fa)
        except ValueError:return
        raise AssertionError('Coordenada não finita aceita')
    check('Coordenada inválida: rejeição explícita',nonfinite)
    return cases

if __name__=='__main__':
    result=run_tests();print(json.dumps(result,ensure_ascii=False,indent=2))
    (ambiente.BASE/'desenvolvimento/revisao_notebook1_v03/testes_geometria.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
