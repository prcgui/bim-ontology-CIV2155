"""Triagem de condições de entrada de Lilis et al. (2026), §6.
DOI 10.1016/j.autcon.2026.106840. NÃO implementa geração de 2LSB.
Testa volumes fechados e interseções dos espaços; mantém casos inconclusivos.
Operadores: IfcOpenShell/OpenCascade atuais, não o programa C++ dos autores.
"""
from pathlib import Path
import json,time,hashlib
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from ifc2sb_faces import read_brep,closed_space_solid,shapes,common,volume,TopAbs_SOLID,BRepCheck_Analyzer
SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(ifc_path,pilot_path,out):
    start=time.monotonic();ifc_path=Path(ifc_path);assert sha(ifc_path)==SHA
    f=ifcopenshell.open(str(ifc_path));pilot=json.loads(Path(pilot_path).read_text(encoding='utf8'))
    s=ifcopenshell.geom.settings();s.set('iterator-output',W.SERIALIZED);s.set('use-world-coords',True);s.set('convert-back-units',False)
    records=[];bodies={};boxes={}
    for e in f.by_type('IfcSpace')+[f.by_guid(r['abertura']) for r in pilot['aberturas']]:
        r={'guid':e.GlobalId,'classe':e.is_a(),'nome':e.LongName if e.is_a('IfcSpace') else e.Name}
        try:
            holder=ifcopenshell.geom.create_shape(s,e);raw=read_brep(holder.geometry.brep_data)
            raw_solids=shapes(raw,TopAbs_SOLID)
            r.update(solidos_brep_entrada=len(raw_solids),brep_valido=BRepCheck_Analyzer(raw).IsValid(),
                     solidos_individualmente_validos=all(BRepCheck_Analyzer(x).IsValid() for x in raw_solids))
            solid,info=closed_space_solid(raw);r.update(estado='volume_fechado_aceito',geometria=info)
            if e.is_a('IfcSpace'):
                bodies[e.GlobalId]=solid;b=Bnd_Box();BRepBndLib.Add_s(solid,b);boxes[e.GlobalId]=b.Get()
        except (ValueError,RuntimeError) as ex:r.update(estado='geometria_nao_aceita_no_criterio',motivo=str(ex))
        records.append(r)
    pairs=[];ids=sorted(bodies);total=len(ids)*(len(ids)-1)//2
    for i,a in enumerate(ids):
      for b in ids[i+1:]:
        if time.monotonic()-start>120:
            pairs.append({'a':a,'b':b,'estado':'nao_executado_limite_operacional'});continue
        A,B=boxes[a],boxes[b]
        if not all(min(A[k+3],B[k+3])-max(A[k],B[k])>1e-7 for k in range(3)):
            pairs.append({'a':a,'b':b,'estado':'sem_sobreposicao_interior_bbox_no_criterio'});continue
        try:
            c=common(bodies[a],bodies[b]);cs=shapes(c,TopAbs_SOLID);v=sum(abs(volume(x)) for x in cs)
            pairs.append({'a':a,'b':b,'estado':'volume_comum_acima_limiar' if v>1e-8 else 'sem_volume_comum_acima_limiar','volume_m3':v})
        except RuntimeError as ex:pairs.append({'a':a,'b':b,'estado':'inconclusivo_operador','motivo':str(ex)})
    spaces=[r for r in records if r['classe']=='IfcSpace'];ops=[r for r in records if r['classe']!='IfcSpace']
    result={'artigo':'https://doi.org/10.1016/j.autcon.2026.106840','natureza':'Triagem de pré-condições; não execução do método 2LSB de Lilis.',
      'sha256_ifc':SHA,'ifc_original_preservado':sha(ifc_path)==SHA,'espacos':spaces,'aberturas_do_piloto':ops,'pares_espacos':pairs,
      'resumo':{'espacos_examinados':len(spaces),'espacos_fechados_aceitos':len(bodies),'aberturas_examinadas':len(ops),
       'aberturas_fechadas_aceitas':sum(r['estado']=='volume_fechado_aceito' for r in ops),
       'aberturas_com_solidos_validos_na_entrada':sum(r.get('solidos_brep_entrada',0)>0 and r.get('solidos_individualmente_validos',False) for r in ops),
       'pares_de_espacos_aceitos':total,'pares_com_volume_comum_acima_limiar':sum(r['estado']=='volume_comum_acima_limiar' for r in pairs),
       'pares_inconclusivos_ou_nao_executados':sum(r['estado'] in ['inconclusivo_operador','nao_executado_limite_operacional'] for r in pairs)},
      'limite':'Limiares experimentais, motor OCP e recorte de 24 aberturas. Não certifica conformidade completa com os requisitos dos autores nem fornece seu código completo. Nenhuma inconsistência foi corrigida.',
      'segundos':time.monotonic()-start}
    target=Path(out);target.mkdir(parents=True,exist_ok=True)
    (target/'Triagem_Precondicoes_Lilis_2026_v01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result['resumo'],ensure_ascii=False,indent=2));return result
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ifc');p.add_argument('piloto');p.add_argument('saida');a=p.parse_args();run(a.ifc,a.piloto,a.saida)
