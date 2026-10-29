"""Inventário por classes e tipos declarados; não infere limites espaciais.
Fonte da API: https://docs.ifcopenshell.org/ifcopenshell-python/code_examples.html
Filtro: Graph.cpp dos autores IFC2SB, commit 96a89cdff65f13279c0c3ce67e729ad9f9f5adad.
"""
from pathlib import Path
from collections import Counter
import json,csv,sys,hashlib
import ifcopenshell
FILTRO=['IfcBeam','IfcColumn','IfcCurtainWall','IfcDoor','IfcMember','IfcPlate','IfcRoof','IfcSlab','IfcWall','IfcWindow']

def inventariar(entrada,pasta):
    entrada=Path(entrada);pasta=Path(pasta);pasta.mkdir(exist_ok=True,parents=True)
    m=ifcopenshell.open(str(entrada))
    cobertura=[]
    for e in m.by_type('IfcCovering'):
        tipos=[rel.RelatingType for rel in e.IsTypedBy]
        cobertura.append({'guid':e.GlobalId,'nome':e.Name,'predefined_type_instancia':e.PredefinedType,
          'tipo_nome':' | '.join(str(t.Name) for t in tipos),'predefined_type_tipo':' | '.join(str(t.PredefinedType) for t in tipos)})
    with (pasta/'Revestimentos_Declarados.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['guid','nome','predefined_type_instancia','tipo_nome','predefined_type_tipo']);w.writeheader();w.writerows(cobertura)
    r={'entrada':entrada.name,'sha256':hashlib.sha256(entrada.read_bytes()).hexdigest(),
       'schema':m.schema,'filtro_classes_autores':FILTRO,
       'contagens':{c:len(m.by_type(c)) for c in FILTRO+['IfcSpace','IfcCovering','IfcRelSpaceBoundary','IfcOpeningElement','IfcRelVoidsElement','IfcRelFillsElement']},
       'covering_tipo_instancia':dict(Counter(str(e.PredefinedType) for e in m.by_type('IfcCovering'))),
       'covering_tipo_do_tipo':dict(Counter(row['predefined_type_tipo'] for row in cobertura)),
       'advertencia':'A ausência de IfcCovering no filtro foi verificada no código-fonte. O inventário não demonstra que isso, isoladamente, explique o comportamento do programa.'}
    (pasta/'Inventario_Entrada_FNDE.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(r,ensure_ascii=False,indent=2));return r

if __name__=='__main__':inventariar(*sys.argv[1:3])
