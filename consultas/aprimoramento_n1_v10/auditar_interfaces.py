"""Validação de superfícies inspirada em Ying e Lee (2021),
DOI 10.1016/j.autcon.2021.103724, §§4.3–4.4; partição é implementação
do estudo. Não declara conformidade a todas as 38 regras nem produz
fechamento 3D: o recorte atual contém interfaces de IfcWall.
"""
from pathlib import Path
from collections import defaultdict
import json
from shapely.ops import unary_union,polygonize
from shapely import wkt
from faces_kiavarz import PlaneFace,polygon_xyz,polygon3_wkt
from preparar_geometria import save
from rotina_multiambientes import write_csv

def particionar(poligonos):
    """Entradas: [(id, parede_guid, Polygon)]. Preserva concorrência sem escolher parede."""
    if not poligonos:return [],{'soma_m2':0.,'uniao_m2':0.,'particao_m2':0.,'excesso_m2':0.,'erro_balanco_m2':0.}
    union=unary_union([p for _,_,p in poligonos]);regions=[]
    lines=unary_union([p.boundary for _,_,p in poligonos])
    for atom in polygonize(lines):
        if atom.area<=1e-8 or not union.covers(atom.representative_point()):continue
        sources=[(id,wall) for id,wall,p in poligonos if p.covers(atom.representative_point())]
        if not sources:raise ValueError('Região sem proveniência')
        walls=sorted({wall for _,wall in sources})
        regions.append({'polygon':atom,'interfaces_fonte':sorted({id for id,_ in sources}),
          'paredes_fonte':walls,'classe':'hospedeiros_concorrentes' if len(walls)>1 else 'mesmo_hospedeiro_com_segmentos_sobrepostos' if len(sources)>1 else 'uma_interface'})
    s=sum(p.area for _,_,p in poligonos);part=sum(a['polygon'].area for a in regions)
    d={'soma_m2':s,'uniao_m2':float(union.area),'particao_m2':part,
       'excesso_m2':max(0.,s-union.area),'erro_balanco_m2':abs(part-union.area)}
    if d['erro_balanco_m2']>max(1e-6,union.area*1e-7):raise ValueError('Partição não conservou área da união')
    return regions,d

def run(cache,resultados,out):
    cache=Path(cache);resultados=Path(resultados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cat=json.loads((cache/'Catalogo_Geometria_v10.json').read_text(encoding='utf8'));rooms={r['guid']:r for r in cat['espacos']}
    rows=[];details=[];atoms_count=0
    for p in sorted((resultados/'ambientes').glob('*/Resultado_Ambiente_v10.json')):
        d=json.loads(p.read_text(encoding='utf8'))
        if not d['estado'].startswith('associacao_'):continue
        wanted={i['face_ambiente'] for i in d['interfaces'] if i['qualificada_no_criterio']}
        frames={f['id']:PlaneFace.from_wkt(f['id'],f['wkt'],f['normal']) for f in rooms[d['ambiente']]['faces'] if f['id'] in wanted}
        groups=defaultdict(list)
        for i in d['interfaces']:
            if not i['qualificada_no_criterio']:continue
            rf=frames[i['face_ambiente']];poly=wkt.loads(i['wkt'])
            pf=PlaneFace.create(i['id'],[list(poly.exterior.coords)]+[list(r.coords) for r in poly.interiors],rf.normal)
            groups[rf.id].append((i['id'],i['parede'],rf.projected(pf)))
        for fid,polys in groups.items():
            rf=frames[fid];atoms,balance=particionar(polys);serialized=[]
            for k,a in enumerate(atoms):
                geom=a.pop('polygon');serialized.append({**a,'id':f'{fid}_A{k:04d}',
                    'area_m2':float(geom.area),'wkt':polygon3_wkt(polygon_xyz(rf,geom))})
            atoms_count+=len(atoms)
            row={'ambiente':d['ambiente'],'nome':d['nome'],'face_ambiente':fid,**balance,
                 'regioes':len(atoms),'regioes_com_hospedeiros_concorrentes':sum(len(a['paredes_fonte'])>1 for a in atoms)}
            details.append({**row,'regioes_particionadas':serialized});rows.append(row)
    result={'fonte_metodologica':'Ying e Lee (2021), DOI 10.1016/j.autcon.2021.103724; partição e balanço adaptados pelo estudo',
       'escopo':'Interfaces qualificadas da mesma face. Área de união separada da soma. Mantém proveniência e ambiguidades; não escolhe automaticamente o hospedeiro correto.',
       'faces_auditadas':len(rows),'regioes_particionadas':atoms_count,
       'ambientes_com_excesso_soma':len({r['ambiente'] for r in rows if r['excesso_m2']>1e-6}),
       'ambientes_com_hospedeiros_concorrentes':len({r['ambiente'] for r in rows if r['regioes_com_hospedeiros_concorrentes']}),
       'maior_erro_balanco_m2':max((r['erro_balanco_m2'] for r in rows),default=0),
       'soma_areas_m2':sum(r['soma_m2'] for r in rows),'area_uniao_m2':sum(r['uniao_m2'] for r in rows),'faces':details,
       'limite':'Não avalia fechamento global nem todos os elementos físicos/virtuais. Sobreposição geométrica não prova por si associação arquitetônica indevida.'}
    save(out/'Auditoria_Interfaces_v10.json',result);write_csv(out/'Balanco_Areas_por_Face_v10.csv',rows)
    print('Auditoria interfaces:',{k:result[k] for k in ['faces_auditadas','regioes_particionadas','ambientes_com_excesso_soma','maior_erro_balanco_m2']},flush=True)
    return result
