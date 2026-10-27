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
| [docs/](docs/) | Planejamento, referências e texto do trabalho. |
| [dados/](dados/) | Modelo BIM e dados utilizados no estudo. |
| [ontologia/](ontologia/) | Classes, propriedades, relações e arquivo da ontologia. |
| [consultas/](consultas/) | Perguntas e consultas sobre as informações representadas. |
| [resultados/](resultados/) | Respostas obtidas, tabelas e imagens de verificação. |
| [apresentacao/](apresentacao/) | Roteiro e slides da apresentação acadêmica. |

## Etapas de desenvolvimento

1. Obter o pacote arquitetônico do FNDE e registrar os arquivos de origem.
2. Inspecionar o IFC e selecionar os ambientes e informações do recorte.
3. Representar os conceitos e suas relações na ontologia.
4. Elaborar e executar consultas.
5. Registrar os resultados e as limitações.
6. Preparar o texto e a apresentação.
