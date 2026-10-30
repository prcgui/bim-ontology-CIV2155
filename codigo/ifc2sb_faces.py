"""Adaptação parcial C++ -> Python do IFC2SB (GPL-3.0-or-later).

Copyright 2022 Eric Fichter (rotinas de origem). Adaptação CIV2155, 2026.
Fichter et al. (2021), DOI 10.26868/25222708.2021.30156.
Fonte fixada: RWTH-E3D/IFC2SB, commit 96a89cdff65f13279c0c3ce67e729ad9f9f5adad.
Kernel_pre.cpp: cvfcipw_* e create_void_filling_cuts_in_products_worker.
Kernel_occ.cpp: face_normal, face_center, unify_shape.
cFace.cpp: CheckParent. NÃO é portabilidade integral do IFC2SB.

OCP expõe OpenCascade ao Python. Não substitui as operações por malhas.
As diferenças e a extensão ambiente-face estão explicitadas em codigo/README.md.
"""
from dataclasses import dataclass
import io,math
from OCP.TopoDS import TopoDS,TopoDS_Shape,TopoDS_Compound
from OCP.TopAbs import TopAbs_FACE,TopAbs_SHELL,TopAbs_SOLID,TopAbs_REVERSED,TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopTools import TopTools_ListOfShape
from OCP.BRep import BRep_Builder,BRep_Tool
from OCP.BRepTools import BRepTools,BRepTools_WireExplorer
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Fuse
from OCP.BOPAlgo import BOPAlgo_CellsBuilder
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GeomAbs import GeomAbs_Plane,GeomAbs_Line
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.gp import gp_Vec,gp_Trsf,gp_Pln

def shapes(s,kind):
    ex=TopExp_Explorer(s,kind);out=[]
    while ex.More():
        a=ex.Current();out.append(TopoDS.Face_s(a) if kind==TopAbs_FACE else a);ex.Next()
    return out
def lst(items):
    out=TopTools_ListOfShape()
    for s in items:out.Append(s)
    return out
def area(s):
    p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);return p.Mass()
def volume(s):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return p.Mass()
def center(face):
    p=GProp_GProps();BRepGProp.SurfaceProperties_s(face,p);return p.CentreOfMass()
def normal(face):
    u0,u1,v0,v1=BRepTools.UVBounds_s(face)
    n=BRepLProp_SLProps(BRepAdaptor_Surface(face),u0,v0,1,1e-3).Normal()
    return n.Reversed() if face.Orientation()==TopAbs_REVERSED else n
def read_brep(data):
    s=TopoDS_Shape();BRepTools.Read_s(s,io.BytesIO(data.encode() if isinstance(data,str) else data),BRep_Builder())
    if s.IsNull():raise ValueError('BRep vazio')
    return s
def write_brep(s,path):BRepTools.Write_s(s,str(path))
def closed_space_solid(shape):
    """Subconjunto de ShapeHealing::get_outer_hull_of_component e
    Kernel::create_shapes_of_IfcSpaces: Sewing -> MakeSolid -> orientar.
    Não porta seleção de face externa, remoção de faces ou reparação global.
    Só aceita componente única, fechada, sem faces descartadas e válida.
    """
    fs=shapes(shape,TopAbs_FACE);sew=BRepBuilderAPI_Sewing()
    for f in fs:sew.Add(f)
    sew.Perform();closed=sew.SewedShape();shells=shapes(closed,TopAbs_SHELL)
    if len(shells)!=1 or sew.NbFreeEdges()!=0:raise ValueError('Ambiente não forma uma única casca fechada; sem reparação automática')
    if len(shapes(closed,TopAbs_FACE))!=len(fs):raise ValueError('Sewing mudou a contagem de faces; caso não aceito')
    s=BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(shells[0])).Solid()
    if volume(s)<0:s=TopoDS.Solid_s(s.Complemented())
    if not BRepCheck_Analyzer(s).IsValid():raise ValueError('Sólido do ambiente inválido')
    return s,{'faces_entrada':len(fs),'faces_saida':len(shapes(s,TopAbs_FACE)),'arestas_livres':sew.NbFreeEdges(),
      'solidos_entrada':len(shapes(shape,TopAbs_SOLID)),'solidos_saida':1,'volume_m3':volume(s),
      'procedimento':'subconjunto Sewing/MakeSolid do IFC2SB; sem remoção de faces nem reparação global'}
def polygon_wkt(shape):
    """Serialização de faces planas com arestas retas, sem triangulação.
    Não aproxima arcos; nesses casos o BRep preservado é a referência.
    """
    parts=[]
    for f in shapes(shape,TopAbs_FACE):
        outer=BRepTools.OuterWire_s(f);wires=[outer]+[TopoDS.Wire_s(w) for w in shapes(f,TopAbs_WIRE) if not w.IsSame(outer)]
        rings=[]
        for wire in wires:
            ex=BRepTools_WireExplorer(wire);points=[]
            while ex.More():
                if BRepAdaptor_Curve(ex.Current()).GetType()!=GeomAbs_Line:raise ValueError('Aresta curva: WKT poligonal não produzido')
                p=BRep_Tool.Pnt_s(ex.CurrentVertex());points.append((p.X(),p.Y(),p.Z()));ex.Next()
            if len(points)<3:raise ValueError('Anel com menos de três vértices')
            points.append(points[0]);rings.append('('+', '.join(' '.join(format(x,'.17g') for x in p) for p in points)+')')
        parts.append('('+', '.join(rings)+')')
    return 'MULTIPOLYGON Z ('+', '.join(parts)+')'
def common(a,b):
    op=BRepAlgoAPI_Common(a,b)
    if not op.IsDone():raise ValueError('OpenCascade Common falhou')
    return op.Shape()
def unify(s):
    solids=shapes(s,TopAbs_SOLID)
    if len(solids)>1:
        op=BRepAlgoAPI_Fuse();op.SetArguments(lst(solids[:1]));op.SetTools(lst(solids[1:]));op.SetFuzzyValue(1e-5);op.SetToFillHistory(False);op.Build()
        if not op.IsDone():raise ValueError('Unificação de múltiplos sólidos falhou')
        u=ShapeUpgrade_UnifySameDomain(op.Shape(),True,True,False);u.Build();return u.Shape()
    if not solids:
        # Extensão v10: reconstrução estrita da casca original, sem caixa.
        solid,info=closed_space_solid(s)
        return solid
    return s

@dataclass
class Face:
    shape:object
    product:str
    original_index:int
    opening:str|None=None
    filling:str|None=None

def check_parent(child,parent,tol_dist=1e-4,tol_angle=.001):
    """Porta os critérios de cFace::CheckParent, não testa contenção poligonal.
    A referência a si mesmo é representada por identidade de objeto Face.
    A correspondência do produto usa GUID (C++ usa ponteiro Product).
    """
    if parent is None:return {'ok':True,'motivo':'sem_parent_neste_teste'}
    if child is parent:return {'ok':False,'motivo':'auto_referencia'}
    p1=center(child.shape);p2=center(parent.shape)
    dist=abs(gp_Pln(p1,normal(child.shape)).Distance(p2))
    angle=abs(normal(child.shape).Angle(normal(parent.shape)))
    a1=area(child.shape);a2=area(parent.shape)
    ok=child.product==parent.product and dist<=tol_dist and angle<=tol_angle and a1-a2<=1e-7
    return {'ok':ok,'distancia_plano_m':dist,'angulo_rad':angle,'area_filha_m2':a1,'area_parent_m2':a2}

def cut_openings(wall,wall_guid,openings):
    """Recorte por shell usando BOPAlgo_CellsBuilder e histórico Modified.

    openings: lista de (GUID abertura, GUID preenchimento ou None, BRep).
    Porta o ramo de aberturas preenchidas com volume comum >=0.001 m3.
    O fallback por caixas do original NÃO é aplicado: retorna inconclusivo.
    Objetos BRep são derivados em memória; não escreve o IFC original.
    """
    result=[];diagnostics=[];parents=[]
    shells=shapes(wall,TopAbs_SHELL)
    if not shells:return [],[],[{'estado':'hospedeiro_sem_shell'}]
    eligible=[]
    for guid,fill,shape in openings:
        sem_solido=not shapes(shape,TopAbs_SOLID)
        try:shape=unify(shape)
        except (ValueError,RuntimeError) as exc:
            diagnostics.append({'abertura':guid,'estado':'abertura_inconclusiva_sem_aproximacao','motivo':str(exc)});continue
        if sem_solido:diagnostics.append({'abertura':guid,'estado':'solido_reconstruido_da_casca_original_sem_caixa'})
        v=volume(common(wall,shape))
        if v<.001:
            diagnostics.append({'abertura':guid,'estado':'ramo_fallback_nao_portado','volume_comum_m3':v});continue
        eligible.append((guid,fill,shape))
    for shell_index,shell in enumerate(shells):
        originals=shapes(shell,TopAbs_FACE)
        offset=len(parents)
        parents.extend(Face(f,wall_guid,offset+i) for i,f in enumerate(originals))
        if not eligible:continue
        compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
        for f in originals:builder.Add(compound,f)
        cb=BOPAlgo_CellsBuilder();cb.SetArguments(lst([compound]+[o[2] for o in eligible]));cb.Perform()
        if cb.HasErrors():raise ValueError('CellsBuilder encontrou erro no recorte')
        diagnostics.append({'shell':shell_index,'estado':'recorte_executado','avisos_occt':cb.HasWarnings()})
        cb.AddToResult(lst([compound]),lst([o[2] for o in eligible]))
        ids=set()
        # Conforme cvfcipw_cut_openings_from_wall_faces, preserva ancestralidade.
        cut=[]
        for i,orig in enumerate(originals):
            modified=list(cb.Modified(orig))
            for f in (modified or [orig]):
                f=TopoDS.Face_s(f);ids.add(hash(f));cut.append(Face(f,wall_guid,offset+i))
        for index,(guid,fill,opening) in enumerate(eligible):
            cb.RemoveAllFromResult();cb.AddToResult(lst([compound,opening]),lst([o[2] for o in eligible[:index]]))
            for i,orig in enumerate(originals):
                for f in cb.Modified(orig):
                    f=TopoDS.Face_s(f)
                    if normal(f).Angle(normal(orig))>.1:f=TopoDS.Face_s(f.Complemented())
                    if hash(f) not in ids:
                        result.append(Face(f,wall_guid,offset+i,guid,fill))
    return result,parents,diagnostics

def room_face_common(room_face,patch,tol_dist=1e-4):
    """Extensão deste estudo, NÃO função pronta dos autores.

    Inspira-se na comparação de faces de get_virtual_faces_worker: normais
    opostas, distância <=1e-4 m e interseção projetada. Usa Common OCCT em
    planos paralelos em lugar do Clipper. Exige paralelismo mais estrito
    (1e-7 rad) e recusa faces curvas. Não gera limite arquitetônico validado.
    """
    a=BRepAdaptor_Surface(room_face);b=BRepAdaptor_Surface(patch)
    if a.GetType()!=GeomAbs_Plane or b.GetType()!=GeomAbs_Plane:return None,{'estado':'face_curva_nao_coberta'}
    nr=normal(room_face);np=normal(patch);angle=nr.Angle(np)
    if angle<3.14:return None,{'estado':'normais_nao_opostas','angulo_rad':angle}
    if abs(math.pi-angle)>1e-7:return None,{'estado':'planos_nao_paralelos_no_recorte','angulo_rad':angle}
    cr=center(room_face);cp=center(patch);plane=gp_Pln(cr,nr)
    dist=plane.Distance(cp)
    if dist>tol_dist:return None,{'estado':'planos_separados','distancia_m':dist}
    # Projeção por translação é equivalente somente para os planos paralelos.
    delta=gp_Vec(cr,cp).Dot(gp_Vec(nr));tr=gp_Trsf();tr.SetTranslation(gp_Vec(nr).Multiplied(-delta))
    projected=BRepBuilderAPI_Transform(patch,tr,True).Shape()
    contact=common(room_face,projected);a_contact=area(contact)
    return contact,{'estado':'intersecao_de_superficies' if a_contact>1e-8 else 'sem_area_comum',
      'area_m2':a_contact,'distancia_planos_m':dist,'angulo_rad':angle}
