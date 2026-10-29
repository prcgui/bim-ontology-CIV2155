"""Auditoria de entidades IFC produzidas pelo IFC2SB; não é algoritmo geométrico.

Leitura e consulta: API oficial IfcOpenShell, by_type(), atributos e inversas.
https://docs.ifcopenshell.org/ifcopenshell-python/code_examples.html
Semântica: buildingSMART IFC4, IfcRelSpaceBoundary2ndLevel e IfcSpace.
https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/link/ifcrelspaceboundary2ndlevel.htm
O método que gera limites é o programa C++ de Fichter et al. (2021).
Este relatório conta relações e compara identificadores; não certifica correção
geométrica nem correspondência arquitetônica das divisões reconstruídas.
"""
from pathlib import Path
from collections import Counter
import json, hashlib, csv, sys
import ifcopenshell

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventario(path):
    m=ifcopenshell.open(str(path))
    rels=m.by_type('IfcRelSpaceBoundary')
    spaces=m.by_type('IfcSpace')
    counts={t:len(m.by_type(t)) for t in ['IfcSpace','IfcExternalSpatialElement','IfcWall','IfcSlab','IfcRoof','IfcCovering','IfcDoor','IfcWindow','IfcRelSpaceBoundary']}
    counts['classes_concretas_limites']=dict(Counter(r.is_a() for r in rels))
    counts['classe_espaco_relacionado']=dict(Counter(r.RelatingSpace.is_a() if r.RelatingSpace else 'AUSENTE' for r in rels))
    counts['classe_elemento_relacionado']=dict(Counter(r.RelatedBuildingElement.is_a() if r.RelatedBuildingElement else 'AUSENTE' for r in rels))
    counts['geometria_conexao_presente']=sum(r.ConnectionGeometry is not None for r in rels)
    counts['tipo_fisico_virtual']=dict(Counter(str(r.PhysicalOrVirtualBoundary) for r in rels))
    counts['tipo_interno_externo']=dict(Counter(str(r.InternalOrExternalBoundary) for r in rels))
    counts['espacos_com_limites']=sum(bool(s.BoundedBy) for s in spaces)
    return m,counts

def analisar(entrada,saida,pasta):
    pasta=Path(pasta);pasta.mkdir(exist_ok=True,parents=True)
    mi,ci=inventario(entrada);mo,co=inventario(saida)
    gi={r.GlobalId for r in mi.by_type('IfcRelSpaceBoundary')}
    go={r.GlobalId for r in mo.by_type('IfcRelSpaceBoundary')}
    si={s.GlobalId for s in mi.by_type('IfcSpace')};so={s.GlobalId for s in mo.by_type('IfcSpace')}
    rows=[]
    for r in mo.by_type('IfcRelSpaceBoundary'):
        s=r.RelatingSpace;e=r.RelatedBuildingElement
        rows.append({'limite_guid':r.GlobalId,'classe_limite':r.is_a(),'guid_ja_existia':r.GlobalId in gi,
          'espaco_guid':getattr(s,'GlobalId',None),'classe_espaco':s.is_a() if s else None,
          'espaco_nome':getattr(s,'Name',None),'espaco_nome_longo':getattr(s,'LongName',None),
          'elemento_guid':getattr(e,'GlobalId',None),'classe_elemento':e.is_a() if e else None,
          'geometria_conexao':bool(r.ConnectionGeometry),'fisico_virtual':r.PhysicalOrVirtualBoundary,
          'interno_externo':r.InternalOrExternalBoundary})
    with (pasta/'Limites_Gerados.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys() if rows else ['limite_guid']);w.writeheader();w.writerows(rows)
    r={'entrada':str(entrada),'sha256_entrada':sha(entrada),'saida':str(saida),'sha256_saida':sha(saida),
       'ifcopenshell_auditoria':ifcopenshell.version,'inventario_entrada':ci,'inventario_saida':co,
       'guids_limites_novos':len(go-gi),'guids_limites_preservados':len(go&gi),
       'guids_espacos_novos':len(so-si),'guids_espacos_preservados':len(so&si),
       'espacos_saida':[{'guid':s.GlobalId,'nome':s.Name,'nome_longo':s.LongName,'limites':len(s.BoundedBy)} for s in mo.by_type('IfcSpace')],
       'criterio_controle':'Existência de IfcSpace com limites e GUIDs de relações novos. Não basta retorno zero; não equivale a validação geométrica independente.',
       'limite_interpretacao':'GUID novo demonstra reescrita, não por si só nova informação. As contagens devem ser lidas com o log de reconstrução e a inspeção das classes.'}
    (pasta/'Inspecao_Entidades_IFC.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(r,ensure_ascii=False,indent=2));return r

if __name__=='__main__':analisar(*sys.argv[1:4])
