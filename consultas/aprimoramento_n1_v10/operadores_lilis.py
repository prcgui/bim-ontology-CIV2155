"""Adaptação em Python de Lilis et al. (2026), §§2.1-2.2 e §3.3.4.

DOI: 10.1016/j.autcon.2026.106840. IP_d, IPS_d, PSS e maxA são
reimplementados a partir das equações/pseudocódigos publicados; não são
o código C++ dos autores. Shapely substitui Clipper. PlaneFace (base local
e anéis) vem da etapa Kiavarz deste estudo. Não implementa alpha wrap.

Na Eq. 1 os nomes dos conjuntos de saída são ambíguos no texto: aqui
o primeiro resultado fica no plano A; o segundo, no plano B. Projeção
ortogonal utiliza a normal do plano de destino, conforme a definição.
"""
import numpy as np
from shapely.ops import unary_union
from shapely.geometry import Polygon
from faces_kiavarz import PlaneFace, polygon_parts, polygon_xyz, AREA_MIN

EPS_NORMAL = 1e-3  # §4: valor prático usado pelos autores.
PLANE_TOL = 1e-7   # m; escolha numérica deste estudo para PSS.

def reversed_face(f):
    return PlaneFace.create(f.id+'~', [r[::-1] for r in f.rings], -f.normal)

def gap_to_plane(a,b):
    return max(float(np.max(abs((r-b.origin)@b.normal))) for r in a.rings)

def ip_d(a,b,d,eps=EPS_NORMAL):
    """§2.1.1/Eq. 1: projeções ortogonais bilaterais e recorte.
    Rejeita se QUALQUER vértice de qualquer lado exceder d.
    Não exige paralelismo: o artigo admite normais com dot < -eps.
    Os resultados preservam o plano e a normal de cada face original.
    """
    if d<=0:raise ValueError('d deve ser positivo')
    dot=float(a.normal@b.normal)
    ga,gb=gap_to_plane(a,b),gap_to_plane(b,a)
    meta={'produto_normal':dot,'max_A_plano_B_m':ga,'max_B_plano_A_m':gb,'d_m':d}
    if dot>=-eps:return None,dict(meta,estado='orientacao_nao_oposta')
    # < d é o critério explícito no Algoritmo 1; limite exato é rejeitado.
    if ga>=d or gb>=d:return None,dict(meta,estado='fora_do_limiar')
    pa,pb=a.projected(b),b.projected(a)
    if not pa.is_valid or not pb.is_valid:return None,dict(meta,estado='projecao_invalida')
    aa,bb=a.polygon.intersection(pa),b.polygon.intersection(pb)
    if aa.area<=AREA_MIN or bb.area<=AREA_MIN:return None,dict(meta,estado='sem_area_bilateral')
    return (aa,bb),dict(meta,estado='recorte_bilateral',area_no_plano_A_m2=float(aa.area),area_no_plano_B_m2=float(bb.area))

def ips_d(a,b,d,same_set=False):
    """Algoritmo 1: conserva pares, sem testar a si próprio nem duplicar i,j."""
    out=[]
    for i,fa in enumerate(a):
        for j,fb in enumerate(b):
            if same_set and j<=i:continue
            pair,info=ip_d(fa,fb,d)
            if pair:out.append((fa,fb,pair,info))
    return out

def coplanar(a,b,eps=EPS_NORMAL,tol=PLANE_TOL):
    # §2.2/Alg. 2; tolerância angular §4 e distância bilateral deste estudo.
    return abs(float(a.normal@b.normal))>1-eps and max(gap_to_plane(a,b),gap_to_plane(b,a))<=tol

def pss(a,subtract):
    """Alg. 2: diferença com polígonos coplanares, preservando furos.
    Retorna polígonos no plano A; não faz conserto por buffer(0).
    """
    eligible=[a.projected(b) for b in subtract if coplanar(a,b)]
    return a.polygon.difference(unary_union(eligible)) if eligible else a.polygon

def max_a(faces,n,eps=EPS_NORMAL):
    """§3.3.4/Eq. 5: UMA face de maior área alinhada à normal n.
    Empates: ordem estável das faces de entrada, decisão deste estudo.
    Não une componentes nem troca para uma face menor se a maior falhar.
    """
    eligible=[f for f in faces if abs(float(f.normal@n))>1-eps]
    return max(eligible,key=lambda f:f.polygon.area) if eligible else None

def opening_on_boundary(boundary,opening_faces,d):
    """Alg. 5: maxA, IP(B,O), IP(B,-O); retém somente recorte no plano B.
    A face escolhida é a mesma nas duas orientações, conforme o artigo.
    """
    face=max_a(opening_faces,boundary.normal)
    if face is None:return None,{'estado':'sem_face_alinhada'}
    parts=[];trials=[]
    for candidate in [face,reversed_face(face)]:
        pair,info=ip_d(boundary,candidate,d);trials.append(info)
        if pair:parts.append(pair[0])
    out=unary_union(parts) if parts else None
    return out,{'estado':'recorte_por_maxA' if out is not None else 'sem_recorte_por_maxA',
                'face_maxA':face.id,'area_face_maxA_m2':float(face.polygon.area),'tentativas':trials}

def fragment(frame,polygon,id):
    return PlaneFace.create(id,polygon_xyz(frame,polygon),frame.normal)
