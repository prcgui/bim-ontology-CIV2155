"""Prepara um ensaio parcial de Krijnen et al. (2020), seção 3.3.

Origem científica: https://doi.org/10.46421/2706-6568.37.2020.paper008
Código citado no artigo: https://doi.org/10.5281/zenodo.3633653
Leitura IFC por IfcOpenShell 0.8.4/OpenCascade; NÃO usa o conversor CGAL
de 2020. A mudança de interpretação geométrica é uma diferença experimental.
As 34 paredes são a seleção do piloto anterior, não todos os possíveis limites.
"""
from pathlib import Path
import json,hashlib,sys,time,collections,zipfile
import numpy as np
import ifcopenshell,ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
from ifc2sb_faces import read_brep,closed_space_solid,common,shapes,volume,TopAbs_SOLID

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parents[1]
DESK=Path.home()/'OneDrive/Área de Trabalho/artigo bim CIV2155'
IFC=DESK/'02_Dados_BIM/Arquitetura/TIPO2-ARQ-DTV_R03.ifc'
SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
GUID='3UFjAT4k55zg_Pqo6VMw5l'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')

def off(path,v,f):
    path.write_text('OFF\n'+f'{len(v)} {len(f)} 0\n'+'\n'.join(' '.join(format(float(x),'.17g') for x in p) for p in v)+'\n'+'\n'.join('3 '+' '.join(str(int(x)) for x in t) for t in f)+'\n',encoding='ascii')

def run():
    t=time.perf_counter();assert sha(IFC)==SHA
    out=ROOT/'entrada';out.mkdir(exist_ok=True)
    baseline_path=WORK/'bim-ontology-CIV2155/resultados/ifc2sb_python_v01/Resultado_Piloto.json'
    baseline=json.loads(baseline_path.read_text(encoding='utf8'))
    assert baseline['sha256_IFC']==SHA
    model=ifcopenshell.open(str(IFC))
    s=ifcopenshell.geom.settings();s.set('use-world-coords',True)
    s.set('convert-back-units',False);s.set('disable-opening-subtractions',True)
    s.set('weld-vertices',True)
    bs=ifcopenshell.geom.settings();bs.set('use-world-coords',True)
    bs.set('convert-back-units',False);bs.set('disable-opening-subtractions',True)
    bs.set('iterator-output',W.SERIALIZED)
    def brep(e):
        holder=ifcopenshell.geom.create_shape(bs,e)
        return read_brep(holder.geometry.brep_data)
    room,topo=closed_space_solid(brep(model.by_guid(GUID)))
    records=[]
    for i,e in enumerate([model.by_guid(GUID)]+[model.by_guid(w['parede']) for w in baseline['paredes']]):
        h=ifcopenshell.geom.create_shape(s,e)
        v=np.asarray(h.geometry.verts).reshape(-1,3)
        f=np.asarray(h.geometry.faces).reshape(-1,3)
        code='S00' if i==0 else f'W{i:02d}'
        path=out/(code+'.off');off(path,v,f)
        edges=collections.Counter(tuple(sorted((int(a),int(b)))) for tri in f for a,b in zip(tri,np.roll(tri,-1)))
        r={'codigo':code,'guid':e.GlobalId,'nome':e.Name,'classe':e.is_a(),'arquivo':path.name,
           'sha256_off':sha(path),'vertices':len(v),'triangulos':len(f),
           'arestas_sem_duas_faces':sum(n!=2 for n in edges.values()),
           'min_xyz_m':v.min(0).tolist(),'max_xyz_m':v.max(0).tolist()}
        if i:
            w=baseline['paredes'][i-1]
            ws=brep(e);inter=common(room,ws)
            r['volume_comum_ocp_bruto_m3']=sum(abs(volume(a)) for a in shapes(inter,TopAbs_SOLID))
            r['area_coincidente_piloto_m2']=w['area_contato_bruta_m2']
            r['chaves_registro_piloto']=list(w.keys()) if i==1 else None
        records.append(r)
    data={'artigo':'https://doi.org/10.46421/2706-6568.37.2020.paper008','codigo_depositado':'https://doi.org/10.5281/zenodo.3633653',
      'ifc_original':IFC.name,'sha256_ifc':SHA,'original_preservado':sha(IFC)==SHA,
      'ifcopenshell':ifcopenshell.version,'interpretacao_ifc':'IfcOpenShell/OpenCascade atual; malha triangular em coordenadas de projeto e metros',
      'escopo':'Cozinha e as mesmas 34 paredes candidatas do piloto IFC2SB parcial. Não cobre lajes, revestimentos nem a totalidade da edificação.',
      'desvio_da_fonte':'Entrada OFF triangulada no lugar da interpretação IFC/CGAL de 2020. Sólidos completos com padding, conforme trecho executável preservado; não se presume fronteira oca nem limite semântico.',
      'baseline':{'arquivo':baseline_path.name,'sha256':sha(baseline_path)},'topologia_room_ocp':topo,
      'subtracao_aberturas':False,'observacao_comparacao':'O piloto anterior subtraiu aberturas sem preenchimento. A nova comparação OCP usa os mesmos sólidos brutos deste ensaio; não atribuir diferenças de entrada ao CGAL.',
      'objetos':records,'segundos_preparacao':time.perf_counter()-t}
    save(out/'Registro_Entrada.json',data)
    with zipfile.ZipFile(ROOT/'Entrada_Krijnen_v01.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in out.iterdir():z.write(p,p.name)
    print(json.dumps({'objetos':len(records),'abertos_ou_nao_manifold_pela_contagem':[(r['codigo'],r['arestas_sem_duas_faces']) for r in records if r['arestas_sem_duas_faces']], 'chaves_piloto':records[1]['chaves_registro_piloto'],'segundos':data['segundos_preparacao']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
