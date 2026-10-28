# bim-ontology-CIV2155

Projeto acadêmico desenvolvido no âmbito da disciplina CIV2155, dedicado à organização e à representação semântica de informações BIM por meio de ontologias.

## Tema

**Transformação de dados BIM em OWL: estudo do projeto padrão de uma creche do FNDE.**

## Pergunta de pesquisa

Quais informações de identificação, organização espacial e classificação dos ambientes são preservadas na transformação do modelo IFC dessa creche em uma representação OWL baseada na Building Topology Ontology (BOT)?

## Objetivo

Documentar o procedimento de transformação de um recorte do modelo arquitetônico IFC em uma representação semântica baseada em BOT e comparar os dados de origem com a representação obtida.

## Universo de dados

O universo documental será a página oficial do FNDE [Creche Pré-Escola Tipo 2](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2), identificada como **Revisão 2025 – R03**. Acesso em: 27 out. 2026.

A base de dados selecionada é o pacote **Projeto Arquitetônico**, disponibilizado na seção **Revisão 2025 – R03** dessa página. A identificação da fonte está em [dados/fnde/arquitetura/](dados/fnde/arquitetura/).

O estudo se concentrará nos identificadores, nomes, classificação dos ambientes e relações de organização espacial efetivamente presentes no modelo. As propriedades disponíveis serão inventariadas antes da definição das consultas. O caso representa um projeto padrão institucional, sem pressupor uma creche construída em um município específico.

### Escopo da análise

1. Caracterização dos ambientes e da estrutura espacial representados no modelo IFC arquitetônico.
2. Mapeamento das informações selecionadas para uma representação OWL baseada nos conceitos da BOT.
3. Verificação da preservação dos identificadores, nomes, classificações e relações após a transformação.
4. Identificação de simplificações, divergências e ausências, distinguindo lacunas dos dados de origem de perdas decorrentes da transformação.

O recorte compreende a arquitetura e a organização dos ambientes. A comparação entre os dados de entrada e saída será realizada sobre um conjunto delimitado e explicitamente selecionado de objetos.

## Estrutura do repositório

| Pasta | Conteúdo |
| --- | --- |
| [docs/](docs/) | Texto acadêmico e fundamentação teórica. |
| [referencias/](referencias/) | Artigos científicos e referências bibliográficas. |
| [dados/](dados/) | Modelo BIM e dados utilizados no estudo. |
| [ontologia/](ontologia/) | Classes, propriedades, relações e arquivo da ontologia. |
| [consultas/](consultas/) | Perguntas e consultas sobre as informações representadas. |
| [resultados/](resultados/) | Resultados consolidados, tabelas e evidências da análise. |
| [apresentacao/](apresentacao/) | Slides da apresentação. |

## Procedimento metodológico

### Transformação do modelo IFC

A transformação será realizada com o **IFCtoLBD**, software associado ao método apresentado por Bonduel et al. (2018). O conversor extrai informações do modelo IFC e produz um grafo RDF com vocabulários de Linked Building Data, incluindo a **Building Topology Ontology (BOT)** para a organização topológica do edifício.

- **Código-fonte dos autores:** [jyrkioraskari/IFCtoLBD](https://github.com/jyrkioraskari/IFCtoLBD).
- **Artigo de referência:** [The IFC to Linked Building Data Converter: Current Status — PDF](referencias/Bonduel_et_al_2018_IFCtoLBD.pdf).
- **Publicação original:** [anais do LDAC 2018, CEUR Workshop Proceedings, v. 2159](https://ceur-ws.org/Vol-2159/).

O procedimento compreenderá as seguintes etapas:

1. **Inspeção da entrada:** leitura do arquivo `TIPO2-ARQ-DTV_R03.ifc` e identificação dos ambientes, identificadores, classificações e relações espaciais do recorte.
2. **Configuração da conversão:** definição dos módulos e parâmetros do IFCtoLBD pertinentes ao recorte, com registro da versão do software e das opções utilizadas.
3. **Transformação semântica:** execução do conversor e preservação da saída RDF em Turtle (`.ttl`), com os conceitos e relações definidos pelos vocabulários adotados.
4. **Consulta dos dados:** elaboração de consultas para recuperar as informações dos ambientes e sua organização espacial.
5. **Avaliação da preservação:** comparação dos registros selecionados no IFC com os resultados das consultas, identificando correspondências, simplificações, divergências e ausências.

A representação OWL será examinada por meio dos conceitos e axiomas da BOT e dos indivíduos e relações expressos no grafo RDF. Turtle é o formato de serialização dos dados; sua utilização não implica a tradução integral do esquema IFC para ifcOWL.

O motor de conversão será reutilizado do repositório dos autores. As rotinas de execução, consulta e comparação desenvolvidas para o estudo serão identificadas como adaptações de apoio. A versão efetivamente utilizada será referenciada separadamente do artigo de 2018, considerando a evolução do software desde sua publicação.

### Verificação da organização espacial e das categorias

A verificação do grafo incorpora a estratégia de consultas SPARQL e regras SHACL apresentada por [Jäkel et al. (2025), seção 5.2](https://doi.org/10.3390/buildings15050720). A [célula 6](consultas/06_verificacao_espacial_classificacao.py) compara os pavimentos pelo `GlobalId` e as categorias funcionais por `Pset_SpaceCommon.Category`. As classificações formais associadas por `IfcRelAssociatesClassification` são inventariadas separadamente. A [célula 7](consultas/07_validacao_shacl.py) verifica condições explícitas de presença, multiplicidade e tipo no grafo.

Essas rotinas e as regras específicas da creche são adaptações elaboradas para este estudo com assistência de inteligência artificial. Os exemplos SHACL originais do artigo tratam de desconstrução e estão nas tabelas 3 a 5. O [PDF completo](referencias/Jaekel_et_al_2025_DCO.pdf), o [repositório da ontologia dos autores](https://github.com/janiwojaekel/dcoOntology) e o [exemplo Java de harmonização de propriedades de Oraskari et al. (2024)](https://github.com/jyrkioraskari/IFCtoLBD/blob/master/IFCtoLBD/src/main/java/examples/Example13.java) estão documentados em [referências](referencias/).

### Fundamentação científica e repercussão do artigo

O artigo de **Bonduel et al. (2018)** foi apresentado no **6th Linked Data in Architecture and Construction Workshop (LDAC 2018)**, realizado em Londres entre 19 e 21 de junho de 2018, e publicado nos [anais do evento, CEUR Workshop Proceedings, v. 2159, p. 34–43](https://ceur-ws.org/Vol-2159/). Apresenta o conversor aberto IFCtoLBD e o procedimento de transformação de modelos IFC em grafos RDF organizados pelos vocabulários BOT, PRODUCT e PROPS.

Sua relevância para este estudo está na disponibilização de uma implementação reutilizável e na explicitação dos mapeamentos entre entidades, relações espaciais e atributos IFC. No caso **Duplex House**, os autores demonstram redução de aproximadamente **83% no número de triplas** em relação à representação ifcOWL, com os três módulos e PROPS L3, além de consultas mais curtas. Esse resultado se refere à configuração avaliada no artigo, cuja representação LBD exclui os dados geométricos. [Fonte: seções 2.2 e 2.3 do artigo](https://ceur-ws.org/Vol-2159/04paper.pdf#page=8).

Na consulta realizada em **27 out. 2026**, a [página do artigo no ResearchGate](https://www.researchgate.net/publication/327262321_The_IFC_to_Linked_Building_Data_Converter-Current_Status) exibia **112 citações**. O indicador registra a repercussão rastreada pela plataforma e pode variar entre bases e datas. O campo **“References (7)”** corresponde às referências bibliográficas vinculadas ao artigo pelo ResearchGate, e não a sete citações adicionais recebidas.

Entre as publicações recentes que citam o trabalho, destacam-se os seguintes exemplos, selecionados por sua proximidade temática:

| Ano | Publicação citante | Relação com o tema |
| --- | --- | --- |
| 2024 | Oraskari et al. — [A Method to Unify Custom Properties in IFC to Linked Building Data Conversion](https://linkedbuildingdata.net/ldac2024/files/papers/LDAC2024_Camera_20.pdf), LDAC 2024. | Discute a harmonização de propriedades e utiliza o IFCtoLBD na conversão dos modelos. |
| 2025 | Jäkel et al. — [Ontology for a Knowledge-Based Deconstruction of Buildings Based on BIM Models and Linked Data Principles](https://doi.org/10.3390/buildings15050720), *Buildings*. | Emprega o IFCtoLBD para associar modelos BIM a uma ontologia de desconstrução. |
| 2026 | Menegotto — [Ontologia BIM da Taxonomia Sustentável Brasileira](https://doi.org/10.56238/arev8n3-151), *ARACÊ*. | Inclui Bonduel et al. (2018) entre as referências da discussão sobre ontologias e BIM. |
| 2026 | Zentgraf, Hagedorn e König — [A BIM-based framework for automated building code extraction and compliance checking](https://doi.org/10.1016/j.aei.2026.104735), *Advanced Engineering Informatics*. | Cita o trabalho ao tratar da representação semântica de dados BIM para verificação de requisitos. |

A presença de citações entre 2024 e 2026 indica continuidade de uso e discussão da abordagem. A escolha metodológica neste estudo se apoia nessa pertinência temática e no acesso ao artigo e ao código dos autores; a contagem de citações é um indicador complementar de repercussão.

## Referência metodológica

BONDUEL, Mathias; ORASKARI, Jyrki; PAUWELS, Pieter; VERGAUWEN, Maarten; KLEIN, Ralf. The IFC to Linked Building Data Converter: Current Status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018, Londres. **Proceedings [...]**. CEUR Workshop Proceedings, v. 2159, 2018. p. 34–43. Disponível em: <https://ceur-ws.org/Vol-2159/04paper.pdf>. Acesso em: 27 out. 2026.
