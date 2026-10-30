# Fontes analisadas

**Projeto:** FNDE Proinfância Tipo 2, arquitetura, revisão R03. [Página oficial do projeto](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2).

| Entrada | Utilização |
|---|---|
| `TIPO2-ARQ-DTV_R03.ifc.zip` | Modelo arquitetônico original, sem alteração. O notebook descompacta e verifica o hash antes de processar. |
| `Conversao_IFCtoLBD.zip` | Resultado da conversão semântica efetivamente executada: 56.961 triplas, sem os antigos complementos geométricos. |
| `Identidades_IFC_RDF.csv` | Correspondência entre GlobalId e URI dos produtos, usada na integração dos resultados. |
| `pranchas/` | Seis PDFs oficiais R03 empregados na leitura documental: pranchas 02, 20 e 24–27. |
| `Origem.json` | Identificação da fonte, hashes e informação da conversão reutilizada. |

O modelo contém 41 IfcSpace e 457 IfcWall. O preparo examina também 184 aberturas e 188 produtos de preenchimento/componentes. Isso não equivale a analisar todas as categorias arquitetônicas ou todos os elementos do projeto.

As pranchas sustentam a análise de uma amostra de 14 ambientes. O quadro agregado está em [Análise documental](../resultados/Analise_Documental_14_Ambientes.csv); as leituras caso a caso e seus registros estão no arquivo técnico do Drive.

O namespace das identidades RDF mantém `notebook1-v03` para preservar as URIs já usadas. O notebook atual usa apenas os arquivos desta estrutura; não depende dos antigos notebooks.
