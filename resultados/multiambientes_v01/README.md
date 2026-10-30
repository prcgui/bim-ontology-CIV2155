# Aplicação multiambientes · Notebook 1 v09

[Notebook executado](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v09.ipynb) · [Relatório com cobertura e casos](Relatorio_Multiambientes_v09.html) · [Código](../../consultas/multiambientes_v01/) · [Referência documental e fontes](../../referencias/multiambientes_v01/).

## Conclusão

O núcleo IFC2SB parcial + Kiavarz foi aplicado aos **41 IfcSpace**, incluindo os 40 além da cozinha. **29 espaços chegaram à associação e 12 ficaram inconclusivos no preparo.** Dos 29, vinte chegaram sem pendências registradas nesse recorte e nove com pendências. Esses estados descrevem a execução, sem certificar completude arquitetônica.

Foram registrados **74 pares ambiente–esquadria e 57 esquadrias distintas**. Uma porta compartilhada pode aparecer em dois espaços; pares não são quantitativos de peças. A quantidade de interfaces depende da segmentação do IFC e não equivale à quantidade de paredes físicas.

## Conferência além da cozinha

Amostra intencional de 14 ambientes, 13 novos: despensa, copa, dois vestiários, dois sanitários PCD, sala de atendimento, sala de professores, lactário, Infantil 2/3, Administração, Infantil 1 e Lavanderia/Rouparia, além da cozinha de controle. Pranchas oficiais R03 02, 20, 24–27; leitura assistida por IA, sem avaliação cega ou revisão independente de especialista.

| Resultado documental | Pares ambiente–esquadria |
|---|---:|
| Associações corretas em espaços processados | 35 |
| Exclusões corretas em espaços processados | 33 |
| Associações indevidas detectadas nesses casos | 0 |
| Omissões após associação nesses casos | 0 |
| Positivos não recuperados por preparo inconclusivo | 8 |
| Negativos não avaliáveis por preparo inconclusivo | 6 |
| Indeterminado documental: JA-09 da cozinha | 1 |

Há evidência de funcionamento em **dez novos cômodos processados da amostra**, além do controle da cozinha. Administração, Infantil 1 e Lavanderia/Rouparia permanecem no balanço e concentram oito positivos não recuperados. Incluindo esses casos, a recuperação é 35/43 = 81,4% nesta amostra intencional; não é estimativa estatística para todos os espaços ou outros edifícios. Ausência de resultado não foi contada como exclusão correta.

[Tabela por ambiente](conferencia/Conferencia_Por_Ambiente_v09.csv) · [Casos e justificativas](conferencia/Conferencia_Caso_a_Caso_v09.csv) · [Referência documental](../../referencias/multiambientes_v01/Referencia_Multiambientes_R03.json). Os outros espaços do lote não recebem aprovação documental por extrapolação.

## Diagnósticos e limitações

O preparo compartilhado examinou 457 paredes: 453 tiveram recorte preparado e quatro ficaram inconclusivas no módulo parcial. O fallback por caixa do original não foi portado. [Motivos dos quatro recortes e dos 12 espaços](preparo/Diagnostico_Preparo_Global_v09.json). Não se conclui que o IFC seja inválido ou que esses espaços não tenham geometria.

Foram examinados 406 pares entre os 29 espaços aceitos e encontrados 12 com volume comum acima do limiar. São medições **OCP atuais**, não CGAL/Nef. As sobreposições permanecem registradas e não vetam automaticamente toda abertura. [Diagnóstico](diagnosticos/Sobreposicoes_Entre_Espacos_v09.json).

CGAL/Krijnen da cozinha não foi transplantado aos novos pares; o fluxo integral de Lilis não foi aplicado no lote. Suas referências e controles comparativos foram mantidos. A generalização desta revisão é do núcleo de recortes/interfaces. Não foi feita reparação global nem validação exaustiva das 1.950 interfaces, de todas as paredes ou categorias.

## Execução e grafo principal

Oito células executadas sem erros, em novo kernel. **65 controles aprovados:** 54 de operadores, cinco de regressão da cozinha e seis da generalização. A cozinha preservou suas nove esquadrias, 14 interfaces, dez internos e três componentes. [Regressão](Regressao_Cozinha_v08_v09.json).

O preparo global foi efetivamente executado nesta revisão e preservado no pacote, com hashes. O notebook reutiliza esse preparo e reexecuta associação dos 41 espaços, diagnóstico OCP, conferência, controles e integração. Pode regenerar o preparo diretamente do IFC com o código incluído. A conversão semântica anterior permanece reutilizada por hash.

O grafo v09 contém **137832 triplas**, preservando integralmente a base v08 de 120191 triplas. A união foi reaberta e a consulta recuperou os 41 estados e 74 pares. Nos 12 inconclusivos, a quantidade permanece ausente em vez de zero.

[Grafo completo compactado](rdf_principal/Notebook1_Grafo_Multiambientes_v09.zip) · [Complemento v09](rdf_principal/Complemento_Multiambientes_v09.ttl) · [Consulta](rdf_principal/Consultar_Todos_Ambientes_v09.rq) · [Resposta](rdf_principal/Consulta_Todos_Ambientes_v09.csv) · [Registro RDF](rdf_principal/Registro_RDF_Multiambientes_v09.json).

## Reprodução e fontes

[Código e entradas](Pacote_Codigo_Entradas_Multiambientes_v09.zip) · [Preparo geométrico fixado](Pacote_Preparo_Geometrico_v09.zip) · [Verificação de entrega](Verificacao_Entrega_v09.json) · [Papel de cada fonte e hashes](../../referencias/multiambientes_v01/Fontes_Multiambientes_v09.json).

Fichter/IFC2SB fundamenta os recortes e a ancestralidade; Kiavarz fundamenta as interfaces adaptadas; Zhang/GEOM orienta a geometria no RDF; Bonduel/IFCtoLBD fundamenta a conversão anterior preservada. Krijnen e Lilis permanecem referências e diagnósticos/alternativas anteriores com limites explícitos. Orquestração em lote, cache compartilhado, diagnóstico OCP e avaliação são rotinas do estudo. Atribuição e licenças derivadas IFC2SB preservadas.
