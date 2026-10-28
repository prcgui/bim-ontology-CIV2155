# 9. Avaliação do efeito da correção textual
#
# FINALIDADE E CRITÉRIO
# Comparar o IFC com as duas saídas: conversor original e conversor com correção.
# Os ambientes são pareados por GlobalId; Name, LongName e Category são examinados
# por igualdade textual exata. Nenhum resultado é preenchido ou normalizado.
# Reconfere também a relação com o pavimento e as mesmas regras SHACL da célula 7.
#
# REFERÊNCIAS E AUTORIA
# Mantém o critério das células 5 e 6 e a estratégia de validação de Jäkel et al.
# (2025), seção 5.2: https://doi.org/10.3390/buildings15050720
# Consulta RDF: https://rdflib.readthedocs.io/en/latest/intro_to_graphs/
# Execução SHACL: https://github.com/RDFLib/pySHACL#python-module-use
# A implementação da comparação é uma adaptação deste estudo apoiada nessas
# interfaces; o artigo não fornece este código nem a correção dos caracteres.
# As correções locais e suas fontes estão descritas na célula 8.

from rdflib import RDF, RDFS
import pandas as pd
import json

mapa_campos = {
    "Name": RDFS.label,
    "LongName": PROPS.longNameIfcSpatialElement_attribute_simple,
    "Category": PROPS.category_property_simple,
}
linhas_correcao = []
recursos_corrigidos = {}
for etapa, grafo in [("Original", grafo_lbd), ("Com correcao", grafo_corrigido)]:
    por_guid = {}
    for recurso in grafo.subjects(RDF.type, BOT.Space):
        guid = grafo.value(recurso, PROPS.globalIdIfcRoot_attribute_simple, any=False)
        if guid is None or str(guid) in por_guid:
            raise ValueError("Identificador ausente ou duplicado: " + etapa)
        por_guid[str(guid)] = recurso
    if set(por_guid) != guids_ifc:
        raise ValueError("Os identificadores dos ambientes diferem do IFC: " + etapa)
    if etapa == "Com correcao":
        recursos_corrigidos = por_guid
    for ambiente in ambientes_ifc:
        recurso = por_guid[ambiente.GlobalId]
        for campo, propriedade in mapa_campos.items():
            origem = (elemento_ifc.get_pset(ambiente, "Pset_SpaceCommon", "Category",
                                          should_inherit=False)
                      if campo == "Category" else getattr(ambiente, campo))
            valor = grafo.value(recurso, propriedade, any=False)
            convertido = None if valor is None else str(valor)
            linhas_correcao.append({
                "Execucao": etapa, "GlobalId": ambiente.GlobalId, "Campo": campo,
                "IFC": origem, "LBD": convertido,
                "Resultado": "preservado" if origem == convertido else "divergente",
            })

comparacao_correcao = pd.DataFrame(linhas_correcao)
resumo_correcao = comparacao_correcao.groupby(
    ["Execucao", "Campo", "Resultado"]
).size().unstack(fill_value=0)
display(resumo_correcao)
divergencias_corrigidas = comparacao_correcao[
    (comparacao_correcao["Execucao"] == "Com correcao")
    & (comparacao_correcao["Resultado"] == "divergente")
]
print("Divergências após a correção:", len(divergencias_corrigidas))
display(divergencias_corrigidas)

# A relação espacial é novamente comparada pela identidade do pavimento no IFC.
pavimentos_preservados = 0
for ambiente in ambientes_ifc:
    esperado = {r.RelatingObject.GlobalId for r in ambiente.Decomposes
                if r.is_a("IfcRelAggregates") and r.RelatingObject.is_a("IfcBuildingStorey")}
    obtido = {
        str(grafo_corrigido.value(p, PROPS.globalIdIfcRoot_attribute_simple, any=False))
        for p in grafo_corrigido.subjects(BOT.hasSpace, recursos_corrigidos[ambiente.GlobalId])
    }
    pavimentos_preservados += esperado == obtido
conforme_corrigido, relatorio_corrigido, texto_corrigido = validate(
    grafo_corrigido, shacl_graph=regras_ambientes, inference="none",
    meta_shacl=True, inplace=False,
)
print("Relações com pavimentos preservadas:", pavimentos_preservados, "/", len(ambientes_ifc))
print("Conformidade com as mesmas regras SHACL:", conforme_corrigido)
comparacao_correcao.to_csv(pasta_resultados_corrigidos / "comparacao_antes_depois.csv",
                          index=False, encoding="utf-8-sig")
resumo_correcao.to_csv(pasta_resultados_corrigidos / "resumo_antes_depois.csv", encoding="utf-8-sig")
relatorio_corrigido.serialize(pasta_resultados_corrigidos / "relatorio_shacl_corrigido.ttl",
                            format="turtle")
avaliacao_correcao = {
    "ambientes": len(ambientes_ifc), "divergencias_textuais_corrigidas": len(divergencias_corrigidas),
    "pavimentos_preservados": pavimentos_preservados, "conforme_shacl": bool(conforme_corrigido),
    "criterio": "igualdade textual exata; sem normalizacao dos valores",
}
(pasta_resultados_corrigidos / "avaliacao_correcao.json").write_text(
    json.dumps(avaliacao_correcao, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Avaliação antes/depois salva em:", pasta_resultados_corrigidos)
