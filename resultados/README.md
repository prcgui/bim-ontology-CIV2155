# Resultados da rotina selecionada

[Ver o RDF em caixas, como na apresentação](grafo_rdf/README.md) · [Explorar os dados na aplicação](https://prcgui.github.io/bim-ontology-CIV2155/).

| Resultado | Arquivo |
|---|---|
| Síntese da execução e do grafo entregue | [Resumo.json](Resumo.json) |
| Estado e quantidade de associações dos 41 espaços | [Ambientes.csv](Ambientes.csv) |
| 101 pares ambiente–esquadria | [Esquadrias_Por_Ambiente.csv](Esquadrias_Por_Ambiente.csv) |
| Interfaces candidatas e qualificação geométrica | [Interfaces.csv](Interfaces.csv) |
| Recortes locais com abertura e preenchimento declarados | [Recortes_Aberturas.csv](Recortes_Aberturas.csv) |
| Grafo RDF consolidado, em Turtle compactado | [Arquitetura_Analisada.zip](Arquitetura_Analisada.zip) |
| Respostas das consultas SPARQL executadas no grafo | [Ambientes](Consulta_Ambientes.csv) · [Esquadrias](Consulta_Esquadrias.csv) |
| Comparação documental recalculada nos 41 ambientes | [Por ambiente](Comparacao_Documental_41_Ambientes.csv) · [Síntese](Resumo_Comparacao_Documental_41_Ambientes.json) |
| Recuperação documental por ambiente | [Figura dos 41 espaços](Comparacao_Documental_41_Ambientes.png) |
| Cobertura de execução | [Figura](Cobertura.png) |

**Leitura dos números:** 38 ambientes com associação executada, três inconclusivos; 101 pares e 66 esquadrias distintas. Das 3.011 interfaces candidatas, nem todas são qualificadas. A tabela inclui a coluna de qualificação. Interfaces/recortes são segmentos geométricos e não devem ser somados como quantitativo de peças.

Contagens vazias nos inconclusivos significam ausência de resultado. Zero em ambiente processado significa nenhuma associação no critério. As coordenadas WKT estão em metros no referencial cartesiano do IFC, sem declaração de CRS84.

O grafo preserva as 56.961 triplas da conversão semântica e acrescenta somente o vocabulário e os resultados primários da rotina selecionada. Os complementos históricos de testes e auditorias não fazem parte deste artefato. Por isso, a quantidade de triplas entregue difere da dos antigos grafos de desenvolvimento.

O notebook refaz o preparo e as associações, exporta o grafo, reabre-o e executa as duas consultas. A etapa 8 recalcula a comparação contra a referência documental explícita dos 41 espaços. A referência vem de leitura visual assistida por IA, sem revisão independente. O notebook não relê os PDFs automaticamente. A síntese publicada de 04/11 foi calculada sobre os CSV reais do Colab, sem refazer a geometria. Consulte a [interpretação e suas limitações](../docs/Analise_dos_Resultados.md).
