# Aprimoramento orientado pela literatura · Notebook 1 v10

[Notebook executado](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v10.ipynb) · [Análise minuciosa, ensaios e catálogo filtrável](Relatorio_Literatura_e_Ensaios_v10.html) · [Código](../../consultas/aprimoramento_n1_v10/) · [Literatura e fontes](../../referencias/aprimoramento_n1_v10/).

## Resultado medido

| Indicador | v09 | v10 |
|---|---:|---:|
| Espaços com associação executada | 29/41 | 38/41 |
| Espaços inconclusivos no preparo | 12 | 3 |
| Paredes com recorte preparado | 453/457 | 457/457 |
| Pares ambiente–esquadria | 74 | 101 |
| Esquadrias distintas | 57 | 66 |
| Positivos documentais confirmados | 35/43 | 39/43 |
| Omissões após execução, na amostra | 0 | 1 |
| Positivos sem resultado por preparo | 8 | 3 |

Todos os **74 pares anteriores foram preservados** e os 29 BReps aceitos anteriormente são idênticos por hash. A cozinha passou em seus cinco controles de regressão. Pares e regiões geométricas não equivalem à quantidade de peças físicas.

A referência documental foi mantida por hash: 14 ambientes, 43 positivos, 39 negativos e JA-09 indeterminada. Nos negativos processados, houve 37 exclusões corretas e nenhuma associação indevida; dois negativos ficaram não avaliáveis por preparo. A recuperação, incluindo os inconclusivos, passou de **81,4% para 90,7%**. A amostra é intencional, assistida por IA e usada no desenvolvimento. Não se afirma acurácia de 100% ou validação de todas as 101 associações.

## Literatura e métodos

O acervo inicial tinha 73 PDFs, 63 conteúdos distintos, incluindo seis pranchas e 57 documentos bibliográficos/técnicos. Houve triagem completa do acervo e leitura dirigida aprofundada das propostas relacionadas aos gargalos. [Decisão sobre cada documento e sete análises aprofundadas](../../referencias/aprimoramento_n1_v10/Revisao_Literatura_v10.json). Não se afirma leitura linear de todas as 1.258 páginas ou reprodução de 57 experimentos.

- **Fichter/IFC2SB + OCCT:** preparo de aberturas por suas próprias faces e recuperação controlada somente após falha estrita, sem caixa/tampão. Nove espaços recuperados; original IFC preservado. ShapeFix e guardas são adaptações do estudo, não portabilidade integral do outer hull.
- **Ying/Lee, representações:** projeção planar limitada a 0,1 mm, com deslocamento efetivo registrado. Distância primária entre planos não foi alargada. AABB/cache já existiam na v09.
- **Ying/Lee, validação:** partição de áreas com proveniência, sem eleger o hospedeiro correto entre concorrentes. Não implementa todas as 38 regras nem certifica fechamento global do recorte de IfcWall.
- **Lilis, diagnóstico/GRC:** estados de falha por etapa e confirmação volumétrica de candidatos somente com operandos adequados. Os 27 candidatos reais permaneceram inconclusivos nessa confirmação.
- **Wang/Zhang/Yan, SHACL:** shapes próprias do resultado v10, com casos válidos e violações deliberadas. Não transplanta regras ifcOWL diretamente ao LBD.
- **Ham/XeoBIM:** ensaio 2D separado e sem prova por bounding box. Encontrou algum contorno nos 41 espaços, mas só 33 dos 43 positivos, contra 39 da v10 3D; não foi adotado como substituto.

CBIP, Lilis por volumes de espaços, Ciria por grafo de paredes, Krijnen/CGAL, navegação, BIM–GIS, instalações e IA têm utilidades/limites separados no relatório. As fontes, as pré-condições e o que foi efetivamente implementado permanecem explícitos. Artigos completos não foram republicados indiscriminadamente; títulos, caminhos relativos, DOI quando disponível e hashes identificam os originais.

## Testes e reprodução

**106 controles aprovados:** 54 de operadores anteriores, cinco da cozinha, seis de generalização, 16 novas contraprovas geométricas, 13 de contratos SHACL e 12 da comparação pareada. Expectativas analíticas incluem formas com dimensões conhecidas, caixa sem face, derivação deslocada, vazios e sala U, na qual todos os vértices internos não bastam para provar contenção.

Onze células foram executadas sem erros em novo kernel. O preparo completo foi executado nesta revisão e reutilizado por hash no notebook, com opção de reexecução. Predição final, ablação sem projeção em processo separado, ensaio 2D, auditorias, conferência, comparação e integração foram reexecutados. A conversão e o grafo semânticos anteriores foram reutilizados explicitamente.

A ablação com healing sem normalização planar deu 38 positivos; a versão selecionada deu 39. [Fonte congelada da ablação](Codigo_Ablacao_Healing_Sem_Projecao.zip) · [Controle](Ablacao_Healing_Controle_v10.json) · [Resultados reexecutados](ablacao_healing/).

[Verificação da entrega](Verificacao_Entrega_v10.json) · [Comparação pareada](controles/comparacao/Comparacao_v09_v10.json) · [Conferência caso a caso](conferencia/Conferencia_Caso_a_Caso_v10.csv) · [Registro de preparo](preparo/Registro_Preparo_v10.json) · [Pilotos de seleção](pilotos/).

## Superfícies e grafo

A v10 registra 3.011 interfaces e 7.666 regiões particionadas em 463 faces auditadas. Hospedeiros concorrentes permanecem em 28 espaços. A soma das áreas é 1.578,923 m² e a união por face é 1.569,694 m²: a diferença de 9,230 m² não é contada repetidamente como área geométrica única. Esses valores não são um quantitativo completo de paredes físicas. [Auditoria](auditorias/Auditoria_Interfaces_v10.json).

O grafo contém **252844 triplas**, preservando integralmente os bytes da base v09 de 137.832 triplas. A união foi reaberta, a consulta recuperou os 41 estados e 101 pares e o SHACL passou sem violações nas shapes declaradas. Candidatos com folga usam classe própria e não associação primária.

[Grafo completo compactado](rdf_principal/Notebook1_Grafo_Multiambientes_v10.zip) · [Complemento](rdf_principal/Complemento_Multiambientes_v10.ttl) · [Consulta](rdf_principal/Consultar_Todos_Ambientes_v10.rq) · [Resposta](rdf_principal/Consulta_Todos_Ambientes_v10.csv) · [Registro RDF](rdf_principal/Registro_RDF_Multiambientes_v10.json) · [Validação SHACL](validacao/Validacao_SHACL_v10.json).

## Limitações mantidas

Infantil 1, Infantil 5 e Amamentação continuam inconclusivos. A JA-04 da Administração permanece omissão após associação; o diagnóstico geral encontrou o candidato com folga de aproximadamente 10 mm, sem promovê-lo a contato. JA-09 continua indeterminada documentalmente. [Candidatos com folga](diagnosticos/Candidatos_Com_Folga_v10.json).

Entre os 38 sólidos aceitos, 23 dos 703 pares apresentaram sobreposição. Há recortes recusados por exceder o contorno parental. Dos 38 espaços, 32 tiveram execução sem pendências registradas nesse recorte e seis com pendências. Esses estados não certificam completude arquitetônica. [Sobreposições](diagnosticos/Sobreposicoes_Entre_Espacos_v10.json).

Não houve revisão independente, outro edifício, validação exaustiva das superfícies/categorias ou comprovação de ganho de velocidade geral. SHACL atesta os contratos declarados e não a verdade geométrica. O IFC e os 73 PDFs originais do inventário inicial mantiveram seus hashes.

[Código/entradas](Pacote_Codigo_Entradas_v10.zip) · [Preparo fixado](Pacote_Preparo_Geometrico_v10.zip) · [Fontes e hashes](../../referencias/aprimoramento_n1_v10/Fontes_e_Adaptacoes_v10.json).
