"""Distingue zero de volume não mensurável na representação BRep de entrada."""
from pathlib import Path
import json
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from ifc2sb_faces import read_brep,shapes,TopAbs_SOLID,closed_space_solid
R=Path(__file__).resolve().parent
cfg=json.loads((R/'entrada/Registro_Entrada.json').read_text(encoding='utf8'))
f=ifcopenshell.open(str(Path.home()/'OneDrive/Área de Trabalho/artigo bim CIV2155/02_Dados_BIM/Arquitetura'/cfg['ifc_original']))
s=ifcopenshell.geom.settings();s.set('use-world-coords',True);s.set('iterator-output',W.SERIALIZED);s.set('disable-opening-subtractions',True)
rows=[]
for obj in cfg['objetos'][1:]:
    holder=ifcopenshell.geom.create_shape(s,f.by_guid(obj['guid']));body=read_brep(holder.geometry.brep_data)
    rows.append({'codigo':obj['codigo'],'guid':obj['guid'],'solidos_brep_entrada':len(shapes(body,TopAbs_SOLID)),
                 'volume_ocp_registrado_m3':obj['volume_comum_ocp_bruto_m3'],
                 'criterio':'Sem TopAbs_SOLID na entrada, a soma vazia de volumes do Common não demonstra volume comum zero.'})
(R/'Diagnostico_Solidos_OCP.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print([(r['codigo'],r['solidos_brep_entrada']) for r in rows])
