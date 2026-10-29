"""Controles analíticos e comparação com corpos C++ extraídos do IFC2SB.
Expectativas geométricas calculadas por dimensões das formas de controle.
Não demonstra equivalência geral nem acurácia arquitetônica na creche.
"""
from pathlib import Path
import json,math
from ifc2sb_faces import *
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pnt

def rectangle(x,y,z,w,h):
    p=BRepBuilderAPI_MakePolygon()
    for a in [(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)]:p.Add(gp_Pnt(*a))
    p.Close();return BRepBuilderAPI_MakeFace(p.Wire()).Face()

def run(reference,out):
    reference=Path(reference);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    cpp=json.loads(reference.read_text(encoding='utf8'));observed={};tests=[]
    def test(name,condition,detail):
        tests.append({'teste':name,'aprovado':bool(condition),'evidencia':detail})
    wall=BRepPrimAPI_MakeBox(4,.2,3).Shape()
    o1=BRepPrimAPI_MakeBox(gp_Pnt(1,-.1,.5),1,.4,1.5).Shape()
    o2=BRepPrimAPI_MakeBox(gp_Pnt(3,-.1,.5),.5,.4,1.5).Shape()
    for n in [1,2]:
        fs,ps,ds=cut_openings(wall,'W',[('O1','D1',o1)]+([('O2','D2',o2)] if n==2 else []))
        values=sorted(area(f.shape) for f in fs);expected=[1.5,1.5] if n==1 else [.75,.75,1.5,1.5]
        observed['cut_'+str(n)]=values
        test('recorte_'+str(n),len(values)==len(expected) and all(abs(a-b)<1e-9 for a,b in zip(values,expected)),{'Python':values,'analitico':expected,'CPP':cpp['cut_'+str(n)]})
        test('CPP_recorte_'+str(n),len(values)==len(cpp['cut_'+str(n)]) and all(abs(a-b)<1e-9 for a,b in zip(values,cpp['cut_'+str(n)])),values)
    par=Face(rectangle(0,0,0,4,3),'W',0);ch=Face(rectangle(1,0,.5,1,1.5),'W',1)
    sequence=[check_parent(ch,par)['ok']]
    ch.product='OUTRA';sequence.append(check_parent(ch,par)['ok']);ch.product='W'
    sequence.append(check_parent(Face(rectangle(1,.01,.5,1,1.5),'W',2),par)['ok'])
    sequence.append(check_parent(Face(rectangle(0,0,0,5,4),'W',3),par)['ok'])
    sequence.append(check_parent(Face(TopoDS.Face_s(ch.shape.Reversed()),'W',4),par)['ok'])
    sequence.append(check_parent(ch,ch)['ok'])
    outside=Face(rectangle(6,0,0,1,1),'W',5);sequence.append(check_parent(outside,par)['ok'])
    observed['parent']=sequence
    expected=[True,False,False,False,False,False,True]
    for i,(a,b,c) in enumerate(zip(sequence,expected,cpp['parent'])):test('parent_CPP_'+str(i),a==b==c,{'Python':a,'CPP':c,'esperado':b})
    # Contraexemplo: CheckParent não testa inclusão no contorno.
    test('parent_nao_certifica_contencao',sequence[-1] and area(common(outside.shape,par.shape))<1e-10,'Face coplanar externa é aceita pelo critério original; Common tem área zero.')
    room=BRepPrimAPI_MakeBox(gp_Pnt(0,.2,0),2.5,3,3).Shape()
    fs,_,_=cut_openings(wall,'W',[('O1','D1',o1),('O2','D2',o2)])
    sums={o:sum((room_face_common(r,p.shape)[1].get('area_m2',0)) for r in shapes(room,TopAbs_FACE) for p in fs if p.opening==o) for o in ['O1','O2']}
    test('abertura_atende_trecho_geometrico',abs(sums['O1']-1.5)<1e-9,sums)
    test('abertura_mesma_parede_fora_ambiente',sums['O2']<1e-10,sums)
    # Cinco faces de uma caixa não constituem sólido fechado, mas GProp pode
    # devolver massa não nula. Volume só é interpretado em componentes sólidas.
    f=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(f)
    for face in shapes(BRepPrimAPI_MakeBox(1,1,1).Shape(),TopAbs_FACE)[1:]:builder.Add(f,face)
    test('massa_de_faces_nao_e_volume_solido',not shapes(f,TopAbs_SOLID) and abs(volume(f))>1e-6,{'massa_assinada_faces':volume(f),'numero_solidos':0})
    try:closed_space_solid(f);rejected=False
    except ValueError:rejected=True
    test('rejeita_casca_aberta',rejected,'Caixa com uma face removida não aceita para volume.')
    closed=TopoDS_Compound();builder.MakeCompound(closed)
    for face in shapes(BRepPrimAPI_MakeBox(1,2,3).Shape(),TopAbs_FACE):builder.Add(closed,face)
    solid,info=closed_space_solid(closed)
    test('forma_solido_sem_descartar_faces',len(shapes(solid,TopAbs_SOLID))==1 and abs(volume(solid)-6)<1e-9 and info['faces_entrada']==info['faces_saida'],info)
    result={'controles':tests,'total':len(tests),'aprovados':sum(t['aprovado'] for t in tests),'observado_python':observed,
      'CPP':cpp,'limite':'Referência C++ usa corpos originais em adaptador isolado e OCCT 7.6.3; Python usa OCP/OCCT 7.8.1. Não demonstra equivalência fora dos casos ensaiados.'}
    (out/'Testes_Adaptacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    assert result['aprovados']==result['total'],result
    print('CONTROLES',result['aprovados'],'/',result['total']);return result
if __name__=='__main__':
    H=Path(__file__).resolve().parent;run(H/'referencia_cpp/Resultado_CPP.json',H/'controles')
