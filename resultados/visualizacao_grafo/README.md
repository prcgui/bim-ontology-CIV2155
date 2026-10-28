# Visualização do grafo IFC–LBD

Figuras elaboradas a partir do arquivo corrigido `creche_tipo2_lbd_corrigido.ttl`, com **411 triplas**. Os textos e as relações são obtidos diretamente desse arquivo. A visualização seleciona relações e propriedades; não acrescenta fatos ao grafo.

| Figura | Conteúdo | Arquivos |
| --- | --- | --- |
| Organização espacial | Terreno, edificação, dois pavimentos e os 41 ambientes vinculados ao térreo. As caixas dos ambientes exibem `Name` e `LongName`. | [PNG, 3240 × 3060 pixels](grafo_organizacao_espacial.png) · [SVG vetorial](grafo_organizacao_espacial.svg) |
| Detalhe da cozinha | Cadeia terreno–edificação–pavimento–ambiente e cinco propriedades do ambiente COZINHA. | [PNG, 2880 × 1620 pixels](grafo_detalhe_cozinha.png) · [SVG vetorial](grafo_detalhe_cozinha.svg) |

![Detalhe do ambiente COZINHA](grafo_detalhe_cozinha.png)

## Leitura das figuras

As setas `bot:hasBuilding`, `bot:hasStorey` e `bot:hasSpace` representam, respectivamente, os vínculos entre terreno e edificação, edificação e pavimento, e pavimento e ambiente. As linhas de distribuição da visão geral compartilham a origem no térreo; suas junções gráficas não são novos recursos RDF. A posição e a distância entre as caixas não expressam a geometria do edifício.

No detalhe, os rótulos abaixo foram simplificados para facilitar a leitura. `props:` corresponde a `http://lbd.arch.rwth-aachen.de/props#`.

| Rótulo da seta | Propriedade RDF |
| --- | --- |
| tipo (`rdf:type`) | `http://www.w3.org/1999/02/22-rdf-syntax-ns#type` |
| nome | `rdfs:label` |
| nome descritivo | `props:longNameIfcSpatialElement_attribute_simple` |
| categoria | `props:category_property_simple` |
| GlobalId | `props:globalIdIfcRoot_attribute_simple` |

A categoria é funcional e não equivale às associações formais de classificação do IFC. A cobertura apresenta zero relações `bot:hasSpace` neste resultado. Nomes repetidos correspondem a recursos distintos e não foram fundidos.

## Dados e reprodução

- [Grafo corrigido utilizado como entrada, 411 triplas](creche_tipo2_lbd_corrigido.ttl).
- [Recorte da organização espacial, 175 triplas](recorte_organizacao_espacial.ttl).
- [Recorte da cozinha, 17 triplas](recorte_cozinha.ttl). Esse arquivo conserva também propriedades não exibidas na figura.
- [Registro de contagens, versões e hash da entrada](registro_visualizacao.json).
- [Rotina de geração das figuras](../../consultas/10_visualizacao_grafo.py).

As figuras foram produzidas com **RDFLib 7.1.4** para ler e selecionar as triplas e **Matplotlib 3.10.7** para desenhar caixas, textos e setas. A rotina verifica que todas as triplas dos recortes pertencem ao grafo de origem. O arranjo gráfico é uma elaboração deste estudo, apoiada na documentação técnica das bibliotecas.

Fontes técnicas: [RDFLib — Navigating Graphs](https://rdflib.readthedocs.io/en/latest/intro_to_graphs/) e [Matplotlib — Annotations](https://matplotlib.org/3.10.7/users/explain/text/annotations.html). Acesso em: 27 out. 2026.

Para reprodução, instalar `rdflib==7.1.4` e `matplotlib==3.10.7` e executar, a partir da raiz do repositório:

```text
python consultas/10_visualizacao_grafo.py resultados/visualizacao_grafo/creche_tipo2_lbd_corrigido.ttl
```
