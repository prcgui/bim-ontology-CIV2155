"""Recuperação controlada de BRep derivado, sem modificar IFC.

Motivação: Fichter et al. (2021), DOI 10.26868/25222708.2021.30156,
etapa de healing. Implementação específica deste estudo com OCCT ShapeFix;
não é a portabilidade integral do grafo de faces/outer hull dos autores.
Lilis et al. (2026), DOI 10.1016/j.jobe.2026.115667: separar diagnóstico,
correção e pré-condições de cada método. Não usa caixa nem preenche furos.
"""
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.ShapeFix import ShapeFix_Shape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_VERTEX
from ifc2sb_faces import shapes,area,volume,closed_space_solid,TopAbs_FACE,TopAbs_SHELL,TopAbs_SOLID,TopoDS

TOLERANCIAS=(1e-6,1e-5,1e-4)
LIMITE_AREA_REL=1e-6
LIMITE_DESVIO_M=1e-4

def caixa(s):
    b=Bnd_Box();BRepBndLib.Add_s(s,b);return np.array(b.Get())

def pontos(s):
    vs=[]
    for v in shapes(s,TopAbs_VERTEX):
        p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(v));vs.append([p.X(),p.Y(),p.Z()])
    return np.unique(np.round(vs,12),axis=0)

def verificar_derivacao(original,candidato):
    """Guardas conservadoras; não constituem conferência arquitetônica."""
    a=area(original);b=area(candidato);p=pontos(original);q=pontos(candidato)
    if not len(p) or not len(q):raise ValueError('Sem vértices para controlar derivação')
    dist=np.linalg.norm(p[:,None,:]-q[None,:,:],axis=2)
    d={'faces_entrada':len(shapes(original,TopAbs_FACE)),
       'faces_saida':len(shapes(candidato,TopAbs_FACE)),
       'delta_area_rel':abs(a-b)/max(abs(a),1e-12),
       'delta_bbox_max_m':float(np.max(abs(caixa(original)-caixa(candidato)))),
       'hausdorff_vertices_m':float(max(dist.min(axis=0).max(),dist.min(axis=1).max()))}
    d['aceito_guardas']=(d['faces_entrada']==d['faces_saida'] and d['delta_area_rel']<=LIMITE_AREA_REL
       and d['delta_bbox_max_m']<=LIMITE_DESVIO_M and d['hausdorff_vertices_m']<=LIMITE_DESVIO_M)
    return d

def preparar_volume_controlado(raw):
    """Mantém o caminho v09 nos casos aceitos; tenta healing só após falha."""
    try:
        solid,info=closed_space_solid(raw)
        return solid,{**info,'metodo_v10':'caminho_estrito_v09_preservado'}
    except (ValueError,RuntimeError) as exc:initial=str(exc)
    attempts=[]
    for tol in TOLERANCIAS:
        # Cópia profunda a cada tentativa: não acumular mutações/tolerâncias.
        fix=ShapeFix_Shape(BRepBuilderAPI_Copy(raw).Shape())
        fix.SetPrecision(tol);fix.SetMinTolerance(1e-7);fix.SetMaxTolerance(tol);fix.Perform()
        sew=BRepBuilderAPI_Sewing(tol)
        for f in shapes(fix.Shape(),TopAbs_FACE):sew.Add(f)
        sew.Perform();closed=sew.SewedShape();shells=shapes(closed,TopAbs_SHELL)
        rec={'tolerancia_m':tol,'cascas':len(shells),'arestas_livres':sew.NbFreeEdges(),
             'arestas_multiplas':sew.NbMultipleEdges(),'aceito':False}
        if len(shells)==1 and sew.NbFreeEdges()==0 and sew.NbMultipleEdges()==0:
            solid=BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(shells[0])).Solid()
            if volume(solid)<0:solid=TopoDS.Solid_s(solid.Complemented())
            rec.update(valido=BRepCheck_Analyzer(solid).IsValid(),volume_m3=volume(solid))
            rec['guardas']=verificar_derivacao(raw,solid)
            rec['aceito']=rec['valido'] and rec['volume_m3']>1e-8 and rec['guardas']['aceito_guardas']
            if rec['aceito']:
                attempts.append(rec)
                return solid,{'metodo_v10':'ShapeFix_Shape_e_costura_controlada',
                  'falha_inicial':initial,'tentativas':attempts,'volume_m3':rec['volume_m3'],
                  'faces_entrada':rec['guardas']['faces_entrada'],'faces_saida':rec['guardas']['faces_saida'],
                  'limite':'Guardas geométricas não substituem avaliação documental; não foi criado tampão ou caixa.'}
        attempts.append(rec)
    error=ValueError(initial+'; recuperação controlada sem candidato aceito')
    error.tentativas=attempts
    raise error
