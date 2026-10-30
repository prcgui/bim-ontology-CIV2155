# Resultados de organização e exploração

Resultados primários produzidos pela execução completa do [Notebook 3](../../notebooks/03_Organizacao_e_Exploracao.ipynb), em 30/10/2026. Consulte o [método, referências e limitações](../../docs/Organizacao_e_Exploracao.md).

| Resultado | Evidência disponibilizada |
|---|---|
| 416.603 quádruplas, nove grafos; cinco grafos N2 preservados | [Dataset N-Quads ZIP](Dataset_Organizado.zip) · [Resumo](Resumo_Organizacao.json) |
| 9 Psets e 34 propriedades simples da V137 | [Registros e unidades JSON](Propriedades_V137.json) · [Grafo N-Triples](Propriedades_V137.nt) |
| Oito perguntas respondidas em SPARQL | [Consultas e respostas JSON](Consultas_Executadas.json) · CSVs nesta pasta · [código das consultas](../../codigo/consultas_exploracao/) |
| Contrato SHACL conforme na projeção documentada | [Resumo e alcance](Resumo_SHACL.json) · [Resultado de conformidade](Validacao_SHACL.ttl) |
| 26.601 produtos disponíveis para explorar; 394.067 quádruplas diretas no índice | [Aplicação publicada](https://prcgui.github.io/bim-ontology-CIV2155/) · [Resumo do índice](Resumo_Indice.json) |

As três salas inconclusivas continuam sem contagem, e a avaliação geométrica não foi ampliada. Os testes de regressão, mutações controladas, erros de desenvolvimento e demais auditorias ficam somente no Google Drive. O resultado SHACL acima é o resultado primário do contrato implementado, sem certificar a semântica global ou o projeto estrutural.
