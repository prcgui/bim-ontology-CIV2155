"""Controles adversariais/analíticos das extensões selecionadas da literatura."""
from pathlib import Path
import json,numpy as np
from shapely.geometry import box,Polygon
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt,gp_Trsf,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from ifc2sb_faces import shapes,TopAbs_FACE,TopAbs_SOLID,volume,unify,cut_openings
from recuperar_geometria import preparar_volume_controlado,verificar_derivacao,TOLERANCIAS
from faces_kiavarz import PlaneFace
from auditar_interfaces import particionar
from auditar_contencao import conter
from ensaio_cortes_2d import secao,associar
from rotina_multiambientes import classify
from preparar_geometria import save

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    tests=[]
    def check(name,ok,detail=None):
        assert ok,(name,detail);tests.append({'controle':name,'aprovado':True,'evidencia':detail})
    def compound(fs):
        s=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(s)
        for f in fs:b.Add(s,f)
        return s
    cube=BRepPrimAPI_MakeBox(1,2,3).Shape();faces=shapes(cube,TopAbs_FACE)
    closed=compound(faces);s,info=preparar_volume_controlado(closed)
    check('geometria_valida_mantem_caminho_estrito',info['metodo_v10']=='caminho_estrito_v09_preservado' and abs(volume(s)-6)<1e-9)
    opening=unify(closed)
    check('abertura_de_faces_vira_solido_sem_caixa',len(shapes(closed,TopAbs_SOLID))==0 and len(shapes(opening,TopAbs_SOLID))==1 and abs(volume(opening)-6)<1e-9)
    opened=compound(faces[1:]);refused=False
    try:preparar_volume_controlado(opened)
    except ValueError:refused=True
    check('healing_nao_inventa_face_ausente',refused)
    check('limiar_healing_limitado_a_um_decimo_de_milimetro',max(TOLERANCIAS)==1e-4)
    tr=gp_Trsf();tr.SetTranslation(gp_Vec(.01,0,0));moved=BRepBuilderAPI_Transform(cube,tr,True).Shape()
    guard=verificar_derivacao(cube,moved)
    check('guardas_rejeitam_corpo_deslocado',not guard['aceito_guardas'],guard)
    p=PlaneFace.create('numeric',[[[0,0,0],[1,0,1e-5],[1,1,0],[0,1,0]]],[0,0,1])
    check('projecao_micrometrica_rastreada',abs(p.polygon.area-1)<1e-12 and abs(p.regularizacao_max_m-1e-5)<1e-12)
    refused=False
    try:PlaneFace.create('warped',[[[0,0,0],[1,0,.001],[1,1,0],[0,1,0]]],[0,0,1])
    except ValueError:refused=True
    check('deformacao_de_um_milimetro_nao_e_planaridade_numerica',refused)
    wall=BRepPrimAPI_MakeBox(4,.2,3).Shape();op=BRepPrimAPI_MakeBox(gp_Pnt(1,-.1,.5),1,.4,1.5).Shape()
    bad=compound(shapes(op,TopAbs_FACE)[1:])
    cuts,parents,diags=cut_openings(wall,'W',[('O_valida','D1',op),('O_aberta','D2',bad)])
    check('falha_isolada_nao_apaga_faces_hospedeiras',len(parents)==6 and len(cuts)==2 and {c.opening for c in cuts}=={'O_valida'} and any(d.get('abertura')=='O_aberta' and d['estado']=='abertura_inconclusiva_sem_aproximacao' for d in diags))
    atoms,b=particionar([('a','W1',box(0,0,2,1)),('b','W2',box(1,0,3,1))])
    check('particao_conserva_uniao_sem_somar_sobreposicao',abs(b['soma_m2']-4)<1e-12 and abs(b['uniao_m2']-3)<1e-12 and abs(b['particao_m2']-3)<1e-12,b)
    check('particao_preserva_hospedeiros_concorrentes',sum(a['polygon'].area for a in atoms if len(a['paredes_fonte'])==2)==1)
    hole=Polygon([(0,0),(4,0),(4,4),(0,4)],[[(1,1),(3,1),(3,3),(1,3)]])
    atoms,b=particionar([('a','W',hole)])
    check('particao_nao_preenche_vazio',abs(b['particao_m2']-12)<1e-12,b)
    a=BRepPrimAPI_MakeBox(1,3,3).Shape();b=BRepPrimAPI_MakeBox(gp_Pnt(2,0,0),1,3,3).Shape();base=BRepPrimAPI_MakeBox(3,1,3).Shape()
    u=BRepAlgoAPI_Fuse(BRepAlgoAPI_Fuse(a,b).Shape(),base).Shape()
    bridge=BRepPrimAPI_MakeBox(gp_Pnt(.5,2,.5),2,.5,1).Shape()
    coords=[[x,y,z] for x in [.5,2.5] for y in [2,2.5] for z in [.5,1.5]]
    vertex_test=all(classify(u,p) in ['IN','ON'] for p in coords);strict=conter(bridge,u)
    check('todos_vertices_internos_nao_provam_contencao_em_sala_concava',vertex_test and not strict['contencao_confirmada'] and abs(strict['volume_fora_m3']-.5)<1e-8,strict)
    inner=BRepPrimAPI_MakeBox(gp_Pnt(.2,.2,.2),.5,.5,.5).Shape();strict=conter(inner,cube)
    check('contencao_volumetrica_corpo_interno',strict['contencao_confirmada'] and strict['volume_fora_m3']<1e-9,strict)
    refused=False
    try:conter(opened,cube)
    except ValueError:refused=True
    check('contencao_sem_solido_fica_inconclusiva',refused)
    vertices=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],float)
    triangles=np.array([[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    p,d=secao(vertices,triangles,.5)
    check('secao_2d_de_dimensoes_conhecidas',p is not None and abs(p.area-1)<1e-9,d)
    p,d=secao(vertices,triangles,2)
    check('ausencia_contorno_nao_vira_caixa',p is None and not associar(p,box(0,0,1,1)),d)
    result={'total':len(tests),'aprovados':len(tests),'controles':tests,'limite':'Controles analíticos/adversariais; avaliação documental é outro conjunto de evidências.'}
    save(Path(out)/'Controles_Aprimoramentos_v10.json',result);print('Aprimoramentos:',len(tests),'controles aprovados',flush=True);return result
