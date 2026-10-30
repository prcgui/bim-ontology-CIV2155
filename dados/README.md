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

## Entradas adicionais do Notebook 2

| Entrada | Utilização |
|---|---|
| `TIPO2-SMT-MOD_R03.ifc.zip` | Modelo de estrutura metálica R03, 5.256 produtos, comprimento em milímetros. |
| `TIPO2-SCO-MOD_R03.IFC.zip` | Modelo de estrutura de concreto R03, 19.229 produtos, comprimento em centímetros. |
| `Modelos_Integracao.json` | URLs de origem FNDE, nomes de arquivo, hashes IFC/ZIP, fatores de comprimento e namespaces dos três modelos. |

Os IFCs estruturais vêm do pacote oficial FNDE `Projeto_Estrutural.rar`, indicado no JSON, e permanecem sem alteração. Os ZIPs são embalagens do estudo. O deslocamento de −40 m em X do terreno SCO é declarado na fonte e aplicado pela cadeia de placements. A geometria dos três modelos é expressa em metros na checagem; as outras propriedades permanecem em seus contextos. [Recorte geométrico e limitações](../docs/Integracao_Arquitetura_Estrutura.md).
