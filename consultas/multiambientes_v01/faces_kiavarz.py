"""Adaptação de procedimentos geométricos de Kiavarz et al. (2023).

DOI 10.3390/buildings13020350, §§4.2.2, 4.3-4.4, Tabelas 4-5.
Não é código executável completo dos autores. A Tabela 5 é pseudocódigo.
Shapely.intersects retorna bool; a área exige intersection(...).area:
https://shapely.readthedocs.io/en/stable/reference/shapely.intersection.html
https://shapely.readthedocs.io/en/stable/reference/shapely.intersects.html

Extensões do estudo: base ortonormal 3D->2D, suporte a anéis interiores,
distância máxima entre planos, amostra interna do recorte e sondas locais.
O artigo é voltado a grafos energéticos, não fornece uma ontologia RDF pronta.
"""
from dataclasses import dataclass
import math
import numpy as np
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely import wkt

AREA_MIN=1.e-8
GAP_M=1.e-4
NORMAL_TOL=1.e-10

@dataclass
class PlaneFace:
    id:str
    origin:np.ndarray
    normal:np.ndarray
    u:np.ndarray
    v:np.ndarray
    polygon:object
    rings:list

    @classmethod
    def create(cls,id,rings,normal):
        rings=[np.asarray(r,dtype=float) for r in rings]
        if not rings or any(r.ndim!=2 or r.shape[1]!=3 or len(r)<3 for r in rings):raise ValueError('Anel 3D incompleto')
        if not all(np.isfinite(r).all() for r in rings):raise ValueError('Coordenada não finita')
        n=np.asarray(normal,dtype=float);length=np.linalg.norm(n)
        if length<1e-14:raise ValueError('Normal nula')
        n=n/length;o=rings[0][0]
        if max(np.max(np.abs((r-o)@n)) for r in rings)>1e-7:raise ValueError('Face não planar no critério')
        axis=np.eye(3)[int(np.argmin(abs(n)))];u=np.cross(n,axis);u/=np.linalg.norm(u);v=np.cross(n,u)
        to2=lambda r:np.column_stack(((r-o)@u,(r-o)@v))
        p=Polygon(to2(rings[0]),[to2(r) for r in rings[1:]])
        if not p.is_valid or p.area<=AREA_MIN:raise ValueError('Polígono inválido ou área insuficiente; sem reparação automática')
        return cls(id,o,n,u,v,p,rings)

    @classmethod
    def from_wkt(cls,id,text,normal):
        geom=wkt.loads(text)
        polys=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
        if len(polys)!=1:raise ValueError('Esperada uma face por registro')
        p=polys[0]
        return cls.create(id,[list(p.exterior.coords)]+[list(r.coords) for r in p.interiors],normal)

    def xy(self,points):
        a=np.asarray(points,dtype=float)-self.origin
        return np.column_stack((a@self.u,a@self.v))

    def xyz(self,points):
        a=np.asarray(points,dtype=float)
        return self.origin+a[...,0,None]*self.u+a[...,1,None]*self.v

    def projected(self,other):
        return Polygon(self.xy(other.rings[0]),[self.xy(r) for r in other.rings[1:]])

def polygon_parts(geometry):
    if geometry.is_empty:return []
    if isinstance(geometry,Polygon):return [geometry] if geometry.area>AREA_MIN else []
    return [p for g in getattr(geometry,'geoms',[]) for p in polygon_parts(g)]

def clipped_interface(room_face,wall_face,gap=GAP_M):
    """Projeção e interseção do §4.4/Tabela 5, com filtros explícitos.
    A área é calculada no plano local da face, nunca no XY global.
    Normais opostas seguem a descrição do §4.3; o texto e a Tabela 4
    usam sinais divergentes. A escolha fica registrada, não é reprodução literal.
    """
    dot=float(room_face.normal@wall_face.normal)
    if dot>-1+NORMAL_TOL:return None,{'estado':'normais_nao_opostas','produto_escalar':dot}
    dist=max(float(np.max(abs((r-room_face.origin)@room_face.normal))) for r in wall_face.rings)
    if dist>gap:return None,{'estado':'planos_separados','distancia_planos_m':dist}
    other=room_face.projected(wall_face)
    if not other.is_valid:return None,{'estado':'projecao_invalida'}
    # Tabela 5 corrigida segundo a API: intersection produz geometria;
    # intersects é somente o predicado booleano.
    result=room_face.polygon.intersection(other)
    if result.area<=AREA_MIN:return None,{'estado':'sem_area_comum','area_m2':float(result.area)}
    return result,{'estado':'recorte_geometrico_candidato','area_m2':float(result.area),
                   'distancia_planos_m':dist,'produto_escalar':dot}

def ray_hits(point,direction,faces,eps=1e-7):
    """Ray/plane + point in polygon, adaptação do §4.2.2, Step II.
    Só t positivo; origem/self-hit são excluídos. Não prova função arquitetônica.
    """
    p=np.asarray(point,dtype=float);d=np.asarray(direction,dtype=float);d=d/np.linalg.norm(d)
    hits=[]
    for f in faces:
        denom=float(f.normal@d)
        if abs(denom)<1e-12:continue
        t=float(f.normal@(f.origin-p)/denom)
        if t<=eps:continue
        q=p+t*d;xy=f.xy([q])[0]
        if f.polygon.covers(Point(xy)):
            hits.append({'face':f.id,'distancia_m':t,'xyz_m':q.tolist()})
    return sorted(hits,key=lambda r:(r['distancia_m'],r['face']))

def probe_interface(frame,polygon,wall_normal,room_faces,classify,step=1e-3):
    """Extensão explícita: ponto interno ao recorte e sondas ±step.
    O centroide pode cair fora de polígono côncavo ou dentro de um vazio.
    Sem confirmação local, um raio que alcança outra parte da sala não basta.
    """
    uv=polygon.representative_point();p=frame.xyz([[uv.x,uv.y]])[0]
    n=np.asarray(wall_normal,dtype=float);n/=np.linalg.norm(n)
    plus=classify(p+step*n);minus=classify(p-step*n)
    hits=ray_hits(p,n,room_faces)
    qualified=plus=='IN' and minus=='OUT' and len(hits)>0
    return {'ponto_amostra_xyz_m':p.tolist(),'sonda_positiva':plus,'sonda_negativa':minus,
            'passo_sonda_m':step,'intersecoes_raio_positivo':hits,
            'qualificacao_local':'apoiada_pelas_sondas_e_raio' if qualified else 'inconclusiva_nas_sondas',
            'qualificada_no_criterio':qualified}

def polygon_xyz(frame,polygon):
    rings=[frame.xyz(list(polygon.exterior.coords)).tolist()]
    rings += [frame.xyz(list(r.coords)).tolist() for r in polygon.interiors]
    return rings

def polygon3_wkt(rings):
    return 'POLYGON Z ('+', '.join('('+', '.join(' '.join(format(float(x),'.17g') for x in p) for p in r)+')' for r in rings)+')'

def face_pair_diagnostic(faces,room_center):
    """Compara leitura literal (áreas crescentes) e adaptação (decrescentes).
    Nenhuma das seleções elimina as outras faces na execução híbrida.
    """
    if len(faces)<2:return {'estado':'menos_de_duas_faces'}
    a=sorted(faces,key=lambda f:(f.polygon.area,f.id))
    def choose(fs):
        ds=[abs(float((np.asarray(room_center)-f.origin)@f.normal)) for f in fs]
        return {'faces':[f.id for f in fs],'areas_m2':[float(f.polygon.area) for f in fs],
                'distancias_centro_planos_m':ds,'face_mais_proxima_do_centro':fs[int(np.argmin(ds))].id}
    return {'literal_ordem_crescente':choose(a[:2]),'adaptacao_ordem_decrescente':choose(list(reversed(a))[:2]),
            'uso':'diagnóstico apenas; recortes e sondas qualificam todas as faces elegíveis'}
