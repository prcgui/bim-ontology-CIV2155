"""Adaptação dos critérios de Lilis et al. (2025), §§3.2–3.4, Fig.4.
DOI 10.1016/j.autcon.2025.106081. Não executa o GRC C++ dos autores.
Adjacência: normais opostas + distância máxima plano-ponto + interseção
positiva das projeções dos polígonos em um plano 3D. Não usa planta XY.
O controle de interseção volumétrica usa Manifold3D, não o BSP do GRC.
Suporte técnico: github.com/elalish/manifold; shapely.readthedocs.io.
Limiares numéricos são parâmetros explícitos deste ensaio, não constantes
atribuídas ao artigo. Nenhum arquivo IFC é escrito.
"""
from dataclasses import dataclass
from collections import Counter,defaultdict
import math
import numpy as np
from shapely.geometry import Polygon,MultiPolygon,GeometryCollection
from shapely.ops import unary_union
import manifold3d

STRICT_M=1e-5
NEAR_M=0.002
ANGLE_DEG=0.1
MIN_AREA_M2=1e-6
VOLUME_EPS_M3=1e-8

@dataclass
class Surface:
    normal:np.ndarray
    origin:np.ndarray
    u:np.ndarray
    v:np.ndarray
    polygon:object
    points:np.ndarray

def polygons(g):
    if isinstance(g,Polygon):return [g]
    if hasattr(g,'geoms'):return [p for child in g.geoms for p in polygons(child)]
    return []

def mesh_diagnostics(vertices,faces):
    v=np.asarray(vertices,dtype=np.float64);f=np.asarray(faces,dtype=np.int64)
    if v.ndim!=2 or v.shape[1]!=3 or f.ndim!=2 or f.shape[1]!=3 or not len(f):
        raise ValueError('Malha sem vértices XYZ ou índices triangulares')
    if not np.isfinite(v).all() or np.min(f)<0 or np.max(f)>=len(v):
        raise ValueError('Coordenadas não finitas ou índices inválidos')
    edges=Counter();directions=Counter()
    for a,b,c in f:
        for x,y in [(a,b),(b,c),(c,a)]:
            edges[tuple(sorted((int(x),int(y))))]+=1
            directions[(int(x),int(y))]+=1
    closed=bool(edges) and all(n==2 for n in edges.values())
    oriented=closed and all(directions[(a,b)]==directions[(b,a)]==1 for a,b in edges)
    centered=v-v.mean(axis=0)
    signed=float(np.sum(np.einsum('ij,ij->i',centered[f[:,0]],np.cross(centered[f[:,1]],centered[f[:,2]])))/6)
    degenerate=int(np.sum(np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)<1e-12))
    return {'vertices':len(v),'triangulos':len(f),'fechada_por_arestas':closed,
      'orientacao_consistente':oriented,'volume_assinado_m3':signed,'triangulos_degenerados':degenerate,
      'bbox_min':v.min(axis=0).tolist(),'bbox_max':v.max(axis=0).tolist()}

def surfaces(vertices,faces):
    """Agrupa somente triângulos coplanares; preserva furos pelo union real."""
    vertices=np.asarray(vertices,dtype=np.float64);faces=np.asarray(faces,dtype=np.int64)
    groups=defaultdict(list)
    for tri in faces:
        xyz=vertices[tri];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);length=np.linalg.norm(n)
        if length<1e-12:continue
        n/=length;d=float(n@xyz[0]);key=tuple(np.round(n,7))+(round(d,7),)
        groups[key].append(tri)
    result=[]
    for key,tris in groups.items():
        xyz=vertices[np.asarray(tris)];n=np.asarray(key[:3]);n/=np.linalg.norm(n)
        origin=xyz[0,0].copy();axis=np.eye(3)[np.argmin(np.abs(n))]
        u=np.cross(n,axis);u/=np.linalg.norm(u);w=np.cross(n,u)
        ps=[Polygon(np.column_stack(((t-origin)@u,(t-origin)@w))) for t in xyz]
        merged=unary_union(ps)
        if not merged.is_valid:raise ValueError('Polígono coplanar inválido; não corrigido automaticamente')
        for p in polygons(merged):
            # Points from the source group are kept for conservative max-distance.
            result.append(Surface(n,origin,u,w,p,xyz.reshape(-1,3)))
    return result

def reproject(surface,target):
    def ring(coords):
        q=np.asarray(coords);world=surface.origin+q[:,0,None]*surface.u+q[:,1,None]*surface.v
        return np.column_stack(((world-target.origin)@target.u,(world-target.origin)@target.v))
    return Polygon(ring(surface.polygon.exterior.coords),[ring(r.coords) for r in surface.polygon.interiors])

def aabb_candidate(a,b,tolerance=NEAR_M):
    return bool(np.all(np.minimum(a.max(axis=0),b.max(axis=0))+tolerance>=np.maximum(a.min(axis=0),b.min(axis=0))))

def surface_contacts(sa,sb,distance_m=NEAR_M,angle_deg=ANGLE_DEG,min_area=MIN_AREA_M2):
    out=[];cos=math.cos(math.radians(angle_deg))
    for i,a in enumerate(sa):
        pieces=[]
        for b in sb:
            if float(a.normal@b.normal)>-cos:continue
            distance=max(float(np.max(np.abs((b.points-a.origin)@a.normal))),
                         float(np.max(np.abs((a.points-b.origin)@b.normal))))
            if distance>distance_m:continue
            projected=reproject(b,a)
            if not projected.is_valid:raise ValueError('Projeção inválida')
            intersection=a.polygon.intersection(projected)
            for p in polygons(intersection):
                if p.area>min_area:pieces.append((p,distance))
        if pieces:
            # Union prevents the same contact area being counted twice.
            total=unary_union([p for p,d in pieces])
            strict=unary_union([p for p,d in pieces if d<=STRICT_M])
            out.append({'surface_index':i,'area_m2':float(total.area),
              'strict_area_m2':float(strict.area),'max_gap_m':max(d for p,d in pieces),
              'max_strict_gap_m':max((d for p,d in pieces if d<=STRICT_M),default=0.0),
              'polygon':total,'strict_polygon':strict,'surface':a})
    return out

def solid(vertices,faces,diagnostic=None):
    d=diagnostic or mesh_diagnostics(vertices,faces)
    if not d['orientacao_consistente'] or abs(d['volume_assinado_m3'])<=VOLUME_EPS_M3:return None
    faces=np.asarray(faces,dtype=np.uint64)
    if d['volume_assinado_m3']<0:faces=faces[:,[0,2,1]]
    # nanobind requires writable buffers; to_mesh64 may expose read-only arrays.
    m=manifold3d.Manifold(manifold3d.Mesh64(np.array(vertices,dtype=np.float64,order='C',copy=True),np.array(faces,dtype=np.uint64,order='C',copy=True)))
    if m.status()!=manifold3d.Error.NoError or m.is_empty():return None
    return m

def classify_pair(va,fa,vb,fb,sa=None,sb=None,solid_a=None,solid_b=None):
    if not aabb_candidate(va,vb):return None
    contacts=surface_contacts(sa or surfaces(va,fa),sb or surfaces(vb,fb))
    if not contacts:return None
    ma=solid_a if solid_a is not None else solid(va,fa)
    mb=solid_b if solid_b is not None else solid(vb,fb)
    intersection_volume=None
    if ma is not None and mb is not None:
        result=ma^mb
        if result.status()==manifold3d.Error.NoError:intersection_volume=max(0.0,float(result.volume()))
    strict_area=sum(c['strict_area_m2'] for c in contacts)
    if intersection_volume is None:status='contato_sem_validacao_volumetrica'
    elif intersection_volume>VOLUME_EPS_M3:status='contato_com_intersecao_volumetrica'
    elif strict_area>MIN_AREA_M2:status='adjacencia_geometrica_no_limiar_numerico'
    else:status='proximidade_de_superficies'
    return {'status':status,'area_m2':sum(c['area_m2'] for c in contacts),
      'strict_area_m2':strict_area,'intersection_volume_m3':intersection_volume,
      'max_gap_m':max(c['max_gap_m'] for c in contacts),
      'max_strict_gap_m':max(c['max_strict_gap_m'] for c in contacts),'contacts':contacts}

def surface_wkt(contact,strict=False):
    """Interseção calculada, reconduzida ao plano XYZ da face; não é bbox."""
    a=contact['surface'];g=contact['strict_polygon'] if strict else contact['polygon']
    def ring(coords):
        q=np.asarray(coords);world=a.origin+q[:,0,None]*a.u+q[:,1,None]*a.v
        return '('+', '.join(' '.join(format(float(v),'.17g') for v in p) for p in world)+')'
    parts=[]
    for p in polygons(g):parts.append('('+', '.join([ring(p.exterior.coords)]+[ring(r.coords) for r in p.interiors])+')')
    return 'MULTIPOLYGON Z ('+', '.join(parts)+')' if parts else 'MULTIPOLYGON Z EMPTY'
