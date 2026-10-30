# Estrutura do artigo baseada nas limitações observadas

## Recorte e objetivo

Analisar as limitações observadas na transformação de arquivos IFC em RDF e na articulação entre arquitetura e estrutura, relacionando cada achado às informações e representações necessárias à finalidade de consulta.

Pergunta orientadora: quais informações e relações precisam estar disponíveis, preservadas ou verificadas para representar os ambientes e seus vínculos com elementos arquitetônicos e estruturais?

A unidade de análise é a dificuldade documentada no fluxo IFC para RDF e integração. Os notebooks fornecem o procedimento e as evidências. A matriz distingue os achados, sua interpretação e os requisitos recomendados. Não se propõe comprovar superioridade de um novo algoritmo nem atribuir todas as dificuldades à autoria dos modelos.

## Sequência do raciocínio

1. Definir a informação desejada por meio de perguntas de competência.
2. Identificar onde essa informação está ou deveria estar recuperável nos arquivos examinados.
3. Confrontar a entrada com os resultados da transformação e das consultas.
4. Descrever o obstáculo e localizar a etapa em que ele aparece.
5. Explicar o que foi demonstrado, o que permanece indeterminado e qual requisito seria pertinente.
6. Encerrar com recomendações proporcionais ao estudo, indicando como poderiam ser verificadas.

## Organização proposta

| Parte | Função no argumento | Evidências e fontes | Extensão indicativa |
|---|---|---|---|
| Título resumo e abstract | Apresentar problema, caso, procedimento e conclusão delimitada | Resultados atuais, sem prometer integração funcional completa | 0,75 a 1 página |
| 1 Introdução | Partir da informação desejada, delimitar problema e apresentar objetivo | F01, F02, F03 e F09 | 0,5 a 0,75 página |
| 2 Da informação BIM à representação semântica | Explicar relações, contexto e diferença entre fonte e representação | F01, F02, F03, F07 e F08 | 0,5 a 0,75 página |
| 3 Procedimentos da análise | Identificar três IFCs R03, transformação, consultas e critérios de evidência | Notebooks; F04, F05, F06, F10, F11, F12 e F13 | 0,75 a 1 página |
| 4 Resultados e discussão | Examinar limites espaciais, contexto de propriedades, coordenação e alcance da validação | L01 a L10; concentrar a narrativa em L01, L02, L05, L06 e L08 | 2 a 2,5 páginas |
| 5 Considerações finais | Responder ao objetivo e delimitar recomendações e verificações futuras | Síntese dos achados, sem nova evidência | 0,4 a 0,6 página |
| Referências | Permitir conferir as fontes citadas | Somente referências efetivamente citadas no texto | 1 a 1,5 página |

Meta editorial: cerca de 6 a 8 páginas, sujeita à conferência do Word. O limite de 15 páginas é um teto, não uma meta de preenchimento. O exemplo fornecido pela professora orienta a apresentação, com uma coluna, texto corrido, resumo, abstract, seções e referências. Seu assunto e suas fontes não são transferidos para o estudo atual.

## Correspondência entre discussão e matriz

- Limites e relações espaciais: L01, L02 e L03. A retomada deve lembrar a pergunta sobre quais elementos delimitam o ambiente.
- Contexto das propriedades: L05. O caso demonstra uma dificuldade da representação RDF apesar da informação presente no IFC.
- Integração entre disciplinas: L06, L07 e L08. A discussão passa de coordenadas e identidade para o significado dos vínculos.
- Cobertura e evidência: L04, L09 e L10. Essa passagem delimita o que as contagens e verificações permitem concluir.

## Resultados e recomendações

**Demonstrado:** aplicação em 38 de 41 espaços; 101 pares ambiente e esquadria; 39 de 43 positivos documentais recuperados no recorte de desenvolvimento; preservação de 26.601 identidades; 1.652 pares espaciais positivos pelo critério; recuperação de nove Psets e 34 propriedades da V137; conformidade do contrato SHACL declarado.

**Recomendado, sem benefício de remodelagem demonstrado:** entrega orientada à finalidade, vínculos espaço e elemento recuperáveis, geometrias compatíveis com o método, conferência independente do alinhamento e dos documentos, regras verificáveis para correspondências e validação por especialista.

**Não concluir:** que o IFCtoLBD perdeu tudo que não aparece em uma consulta; que os IFCs são inválidos ou foram mal modelados; que as 1.652 relações são corretas fisicamente; que contato significa apoio; que a POC vale para todas as propriedades; ou que o explorador melhora a usabilidade sem avaliação própria.

## Materiais de apoio

A [matriz completa](Matriz_Limitacoes_e_Requisitos.md) mantém fontes e limites por caso. Código, gráficos detalhados e dados ficam nos notebooks e resultados. Auditorias, versões anteriores e revisões editoriais ficam no arquivo técnico do Drive. O Word com revisões é um rascunho assistido, com alterações reais e autoria identificada, para revisão do pesquisador; não representa um histórico de escrita anterior a esta execução.

## Revisão de coesão e retomadas

Cada parágrafo deve desenvolver uma ideia apoiada pelo anterior. Expressões como “essa limitação” precisam indicar o achado a que se referem; “esses resultados” deve retomar um conjunto já delimitado. Conectivos causais só cabem quando houver relação demonstrada. Quando a causa não foi isolada, usar linguagem de interpretação ou recomendação. Evitar encadear parágrafos com fórmulas repetidas, duplicar conclusões ou introduzir assunto novo nas considerações finais. O texto não usa travessões.
