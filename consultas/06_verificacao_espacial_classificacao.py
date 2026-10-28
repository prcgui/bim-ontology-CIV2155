# 6. Verificação da organização espacial e da categoria dos ambientes
#
# REFERÊNCIA CIENTÍFICA
# JÄKEL, J.-I. et al. Ontology for a Knowledge-Based Deconstruction of
# Buildings Based on BIM Models and Linked Data Principles. Buildings,
# v. 15, n. 5, 720, 2025. DOI: https://doi.org/10.3390/buildings15050720
# Seção 5.2.1: verificação do modelo convertido por consultas SPARQL.
# Artigo: https://www.mdpi.com/2075-5309/15/5/720#sec5dot2-buildings-15-00720
# PDF: referencias/Jaekel_et_al_2025_DCO.pdf (também no Drive).
# Ontologia publicada: https://github.com/janiwojaekel/dcoOntology
# Código desta adaptação:
# https://github.com/prcgui/bim-ontology-CIV2155/blob/main/consultas/06_verificacao_espacial_classificacao.py
#
# AUTORIA E RECORTE DA ADAPTAÇÃO
# Rotina elaborada para este estudo com assistência de inteligência artificial.
# A consulta dos autores examina componentes para desconstrução; aqui se
# adapta a estratégia aos pavimentos e às categorias dos ambientes da creche.
# Categoria funcional = Pset_SpaceCommon.Category. As associações formais
# IfcRelAssociatesClassification são inventariadas separadamente.
# Os valores são comparados exatamente, sem normalização ou correção.
# Fontes técnicas (acesso em 27 out. 2026):
# https://rdflib.readthedocs.io/en/latest/intro_to_sparql/
# https://docs.ifcopenshell.org/autoapi/ifcopenshell/util/element/index.html

import json
import pandas as pd
import ifcopenshell.util.element as elemento_ifc
from IPython.display import display

# Dependências das células anteriores: ambientes_ifc, grafo_lbd,
# recursos_por_guid e pasta_resultados.
consulta_espacial = """
PREFIX bot: <https://w3id.org/bot#>
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
SELECT ?espaco ?guid ?pavimento ?pavimento_guid ?categoria WHERE {
  ?espaco a bot:Space .
  OPTIONAL { ?espaco props:globalIdIfcRoot_attribute_simple ?guid . }
  OPTIONAL {
    ?pavimento bot:hasSpace ?espaco .
    OPTIONAL { ?pavimento props:globalIdIfcRoot_attribute_simple ?pavimento_guid . }
  }
  OPTIONAL { ?espaco props:category_property_simple ?categoria . }
}
"""
consulta_rdf = list(grafo_lbd.query(consulta_espacial))
tabela_consulta = pd.DataFrame(
    [[None if v is None else str(v) for v in linha] for linha in consulta_rdf],
    columns=["Recurso", "GlobalId", "Pavimento_recurso", "Pavimento_GlobalId", "Categoria"],
)

def valores_consulta(recurso, campo):
    return {str(getattr(linha, campo)) for linha in consulta_rdf
            if linha.espaco == recurso and getattr(linha, campo) is not None}

def comparar_conjuntos(origem, saida, recurso):
    if recurso is None:
        return "ambiente ausente no grafo"
    if not origem:
        return "ausente nas duas fontes" if not saida else "adicionado no grafo"
    if not saida:
        return "ausente no grafo"
    return "preservado" if origem == saida else "divergente"

registros_espaciais, classificacoes_formais = [], []
for ambiente in ambientes_ifc:
    recurso = recursos_por_guid.get(ambiente.GlobalId)
    pavimentos_ifc = {r.RelatingObject.GlobalId for r in ambiente.Decomposes
                     if r.is_a("IfcRelAggregates")
                     and r.RelatingObject.is_a("IfcBuildingStorey")}
    categoria = elemento_ifc.get_pset(
        ambiente, "Pset_SpaceCommon", "Category", should_inherit=False
    )
    categorias_ifc = set() if categoria is None else {str(categoria)}
    verificacoes = [
        ("Pavimento (GlobalId)", pavimentos_ifc, valores_consulta(recurso, "pavimento_guid")),
        ("Categoria funcional", categorias_ifc, valores_consulta(recurso, "categoria")),
    ]
    for campo, origem, saida in verificacoes:
        registros_espaciais.append({
            "GlobalId": ambiente.GlobalId, "Verificacao": campo,
            "IFC": json.dumps(sorted(origem), ensure_ascii=False),
            "LBD": json.dumps(sorted(saida), ensure_ascii=False),
            "Resultado": comparar_conjuntos(origem, saida, recurso),
        })
    for relacao in ambiente.HasAssociations:
        if relacao.is_a("IfcRelAssociatesClassification"):
            referencia = relacao.RelatingClassification
            sistema = referencia
            while sistema is not None and sistema.is_a("IfcClassificationReference"):
                sistema = sistema.ReferencedSource
            classificacoes_formais.append({
                "GlobalId": ambiente.GlobalId,
                "Sistema": None if sistema is None else sistema.Name,
                "Codigo": getattr(referencia, "Identification", None),
                "Nome": getattr(referencia, "Name", None),
            })

comparacao_espacial = pd.DataFrame(registros_espaciais)
inventario_classificacoes = pd.DataFrame(
    classificacoes_formais, columns=["GlobalId", "Sistema", "Codigo", "Nome"]
)
resumo_espacial = comparacao_espacial.groupby(
    ["Verificacao", "Resultado"]
).size().unstack(fill_value=0)
print("Ambientes consultados no grafo:", tabela_consulta["Recurso"].nunique())
display(resumo_espacial)
display(comparacao_espacial[comparacao_espacial["Resultado"] != "preservado"])
print("Associações formais de classificação no IFC:", len(inventario_classificacoes))
print("A comparação de Category não comprova preservação da classificação formal.")
display(inventario_classificacoes[["Sistema", "Codigo", "Nome"]].drop_duplicates())

for nome, tabela in [
    ("consulta_espacos_pavimentos_categorias.csv", tabela_consulta),
    ("comparacao_espacial_classificacao.csv", comparacao_espacial),
    ("inventario_classificacoes_ifc.csv", inventario_classificacoes),
]:
    tabela.to_csv(pasta_resultados / nome, index=False, encoding="utf-8-sig")
(pasta_resultados / "consulta_espacial.sparql").write_text(consulta_espacial, encoding="utf-8")
print("Consulta e tabelas salvas em:", pasta_resultados)
