# Consultas

Perguntas de competência e consultas sobre as informações representadas na ontologia. As respostas consolidadas integram a seção de [resultados](../resultados/).

| Código | Finalidade | Referência |
| --- | --- | --- |
| [Célula 6](06_verificacao_espacial_classificacao.py) | Comparar pavimentos e categorias funcionais entre IFC e LBD e inventariar as classificações formais do IFC. | Jäkel et al. (2025), seção 5.2.1. |
| [Célula 7](07_validacao_shacl.py) | Verificar presença, multiplicidade e tipos dos identificadores, nomes, pavimentos e categorias no grafo. | Jäkel et al. (2025), seção 5.2.2; SHACL/W3C; pySHACL. |
| [Célula 8](08_correcao_textual_conversor.py) | Preparar e testar as correções locais de Unicode e apóstrofos e repetir a conversão em uma saída separada. | Código-fonte fixado do IFCtoLBD 2.49.0; orientação de codificação IFC da buildingSMART. |
| [Célula 9](09_comparacao_apos_correcao.py) | Comparar os textos antes e depois da intervenção e repetir as verificações espacial e SHACL. | Critérios das células 5 a 7; Jäkel et al. (2025); RDFLib e pySHACL. |

Os arquivos correspondem ao conteúdo das células de mesmo número do [notebook do estudo](https://colab.research.google.com/drive/1qmajVMEY4S-4RKymkpQa2cx2eHtwuWmq) e dependem das variáveis criadas nas células anteriores. A implementação e as regras específicas da creche são adaptações deste estudo, com assistência de inteligência artificial. As fontes e o código dos autores estão identificados em [referências](../referencias/).

A [rotina de visualização](10_visualizacao_grafo.py) é executada separadamente sobre o Turtle corrigido. Gera figuras PNG e SVG da organização espacial e de um ambiente, com leitura das triplas pelo RDFLib e desenho pelo Matplotlib. Os critérios, as fontes técnicas e os arquivos de entrada estão nos [resultados da visualização](../resultados/visualizacao_grafo/).
