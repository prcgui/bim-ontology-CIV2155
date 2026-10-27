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

## Referência metodológica

BONDUEL, Mathias; ORASKARI, Jyrki; PAUWELS, Pieter; VERGAUWEN, Maarten; KLEIN, Ralf. The IFC to Linked Building Data Converter: Current Status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018, Londres. **Proceedings [...]**. CEUR Workshop Proceedings, v. 2159, 2018. p. 34–43. Disponível em: <https://ceur-ws.org/Vol-2159/04paper.pdf>. Acesso em: 27 out. 2026.
