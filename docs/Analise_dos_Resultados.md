# O que foi analisado e o que se concluiu

A rotina geométrica foi executada nos 41 espaços do modelo arquitetônico R03. A conferência documental de 04/11/2026 também abrange os 41 espaços, incluindo circulações, playgrounds e áreas técnicas. A comparação usa os CSV da execução real do Colab encerrada às 17:35 UTC. Esses CSV coincidem, como conjuntos de linhas, com as tabelas publicadas. A ampliação da referência não alterou o algoritmo ou suas tolerâncias.

| Questão analisada | Resultado | Alcance da conclusão |
|---|---|---|
| A geometria pôde ser processada em todos os espaços? | 38 processados e três inconclusivos; 32 sem pendências e seis com pendências registradas. | Processamento não equivale a concordância com a planta. |
| Quantas relações eram esperadas na documentação? | 122 relações positivas de fronteira principal nos 41 espaços. | Referência visual preliminar, sem revisão independente. |
| Quantas foram recuperadas? | 100; outras 15 ficaram ausentes nos processados e sete indisponíveis nos inconclusivos. | Recuperação global: 100/122 = 82,0%; nos processados: 100/115 = 87,0%. |
| As associações produzidas foram confirmadas? | Das 101, 100 concordam com a referência e uma é indeterminada. Nenhuma associação contrariou os casos documentais decididos. | Precisão de 100/100 nos casos decididos desta referência; não é acurácia externa nem garantia de ausência de erros. |
| Há espaços sem esquadria principal esperada? | Dois playgrounds, pátio coberto/refeitório e castelo d'água. | Os quatro não aumentam a recuperação de relações positivas. O acesso técnico do reservatório não foi presumido como IfcDoor. |

## Como foi feita a conferência

Cada espaço foi identificado por GUID, nome e posição no IFC. Isso distingue as quatro circulações e os dois playgrounds. Em seguida, o perímetro foi lido na planta geral 02 e confrontado com ampliações, vistas e mapas de esquadrias das pranchas 12 a 15 e 19 a 36 efetivamente citadas na [referência](../dados/Referencia_Documental_41_Ambientes.json). Os arquivos têm uma página cada; o número identifica a prancha no conjunto 02/36, por exemplo.

O rótulo esperado foi transcrito da documentação. Posição e altura no inventário IFC ajudaram a identificar instâncias repetidas; a associação calculada pelo N1 não foi usada como regra de rotulagem. Porém, os resultados anteriores já eram conhecidos: a avaliação é assistida por IA e não cega. Não houve revisão por especialista independente.

A relação avaliada é uma esquadria principal na fronteira do espaço, inclusive quando compartilhada. Portões PF1/PF2 e portas técnicas PA5 entram no escopo. Oito PM5 de cabines internas e cinco telas V02 acessórias ficam fora dele, com justificativa. O universo contém 79 esquadrias principais. Os demais pares desse universo são negativos do perímetro lido; sua quantidade não é apresentada como acurácia global. A referência foi congelada antes do cálculo desta comparação.

## Onde a rotina deixou relações passar

| Ambiente | Relações positivas ausentes após processamento | Evidência documental |
|---|---|---|
| Administração | Uma JA04 | 02 e 14 |
| Casa de bombas | Duas PA5 e duas JA14 | 02, 13 e 15; JA14 em duas alturas |
| Circulação de 4,37 m² | PM1 compartilhada com sala de atendimento | 02 e 23 |
| Circulação pedagógica de 70,09 m² | PA3 do recesso lateral | 02, 12 e 13 |
| Hall de entrada | JA09 do sanitário PCD feminino | 02 e 14 |
| Solário 2 | PA4 compartilhada com Infantil 2/3 | 02 e 30 |
| Solário 3 | PA4 compartilhada com Infantil 4 | 02 e 30 |
| Varanda de serviço/DML | PA1 e PA2 da cozinha, PA2 da copa e duas JA06 da divisa oeste | 02, 22 e 26 |

São 15 pares ausentes em oito espaços. Os PF2 dos solários foram recuperados. A mesma esquadria pode ter sido recuperada de um lado e omitida do outro; são relações distintas. O registro identifica a ausência, mas não atribui automaticamente a causa ao modelo, à exportação ou a um parâmetro sem investigação específica.

**Falhas de preparo.** Infantil 1, Infantil 5 e Amamentação têm, respectivamente, três, três e uma relações positivas esperadas. As sete ficam separadas das omissões em espaços processados. Ausência de resultado não significa exclusão correta.

**Divergência entre documentos.** A JA09 da cozinha aparece nas pranchas 02 e 22, mas não na planta 24 nem na vista 02 da prancha 25. As relações com cozinha e varanda permanecem indeterminadas. O N1 a associa à cozinha e não à varanda; nenhuma dessas decisões foi convertida em acerto ou erro documental.

**Cozinha.** Mantêm-se nove associações, oito confirmadas pela referência e uma indeterminada. As 14 interfaces candidatas da cozinha são segmentos geométricos, não 14 paredes físicas.

## O que os números permitem discutir

A leitura dos 41 espaços evidenciou omissões que a amostra anterior de 14 ambientes não cobria. Por isso, a recuperação global de 82,0% não deve ser comparada diretamente aos 90,7% daquela amostra como se houvesse piora do código: os conjuntos avaliados são diferentes. Os ensaios históricos e a tabela anterior permanecem no [arquivo técnico do Drive](https://drive.google.com/drive/u/0/folders/1kVGXvERWXieeMeURrJF07tuLaADdrJ_O).

A cobertura completa deste modelo não torna a referência independente. Não houve outro edifício, revisão cega, revisão por especialista ou comparação controlada com um IFC remodelado. O resultado fundamenta a discussão sobre representação dos espaços, relações compartilhadas e consistência documental. Melhorar esses requisitos é uma recomendação; o ganho decorrente de remodelar o IFC ainda não foi medido.

O N1 contém a função de comparação e recalcula a avaliação a partir das tabelas que acabou de produzir. A leitura arquitetônica continua sendo uma referência explícita, não uma interpretação automática dos PDFs a cada execução. O código recusa IFC, inventário ou esquadrias desconhecidos e distingue omissão, indisponibilidade, indeterminação e previsão fora de escopo.

[Comparação dos 41 ambientes](../resultados/Comparacao_Documental_41_Ambientes.csv) · [Síntese calculada](../resultados/Resumo_Comparacao_Documental_41_Ambientes.json) · [Referência documental](../dados/Referencia_Documental_41_Ambientes.json) · [Associações produzidas](../resultados/Esquadrias_Por_Ambiente.csv).
