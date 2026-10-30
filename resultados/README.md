# Resultados da rotina selecionada

| Resultado | Arquivo |
|---|---|
| Síntese da execução e do grafo entregue | [Resumo.json](Resumo.json) |
| Estado e quantidade de associações dos 41 espaços | [Ambientes.csv](Ambientes.csv) |
| 101 pares ambiente–esquadria | [Esquadrias_Por_Ambiente.csv](Esquadrias_Por_Ambiente.csv) |
| Interfaces candidatas e qualificação geométrica | [Interfaces.csv](Interfaces.csv) |
| Recortes locais com abertura e preenchimento declarados | [Recortes_Aberturas.csv](Recortes_Aberturas.csv) |
| Grafo RDF consolidado, em Turtle compactado | [Arquitetura_Analisada.zip](Arquitetura_Analisada.zip) |
| Respostas das consultas SPARQL executadas no grafo | [Ambientes](Consulta_Ambientes.csv) · [Esquadrias](Consulta_Esquadrias.csv) |
| Resultado agregado da análise documental realizada | [14 ambientes](Analise_Documental_14_Ambientes.csv) |
| Cobertura de execução | [Figura](Cobertura.png) |

**Leitura dos números:** 38 ambientes com associação executada, três inconclusivos; 101 pares e 66 esquadrias distintas. Das 3.011 interfaces candidatas, nem todas são qualificadas. A tabela inclui a coluna de qualificação. Interfaces/recortes são segmentos geométricos e não devem ser somados como quantitativo de peças.

Contagens vazias nos inconclusivos significam ausência de resultado. Zero em ambiente processado significa nenhuma associação no critério. As coordenadas WKT estão em metros no referencial cartesiano do IFC, sem declaração de CRS84.

O grafo preserva as 56.961 triplas da conversão semântica e acrescenta somente o vocabulário e os resultados primários da rotina selecionada. Os complementos históricos de testes e auditorias não fazem parte deste artefato. Por isso, a quantidade de triplas entregue difere da dos antigos grafos de desenvolvimento.

O notebook refaz o preparo e as associações, exporta o grafo, reabre-o e executa as duas consultas. A tabela documental registra uma análise já realizada, com referência às pranchas; o notebook a apresenta sem refazer a leitura arquitetônica. Consulte a [interpretação e suas limitações](../docs/Analise_dos_Resultados.md).
