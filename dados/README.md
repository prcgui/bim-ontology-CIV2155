# Dados de entrada

Os modelos pertencem ao projeto padrão da Creche Tipo 2 do FNDE, revisão R03. A origem pública é a [página oficial do Projeto Tipo 2](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2).

| Arquivo | Modelo | Unidade de comprimento declarada |
|---|---|---|
| [TIPO2-ARQ-DTV_R03.ifc.zip](TIPO2-ARQ-DTV_R03.ifc.zip) | Arquitetura | Metro |
| [TIPO2-SMT-MOD_R03.ifc.zip](TIPO2-SMT-MOD_R03.ifc.zip) | Estrutura metálica | Milímetro |
| [TIPO2-SCO-MOD_R03.IFC.zip](TIPO2-SCO-MOD_R03.IFC.zip) | Estrutura de concreto | Centímetro |

Os IFCs originais são preservados. Os ZIPs são embalagens utilizadas pelo estudo. Os nomes e os hashes dos modelos estão registrados em [Fontes_e_Referenciais.json](../resultados/integracao/Fontes_e_Referenciais.json).

[Conversao_IFCtoLBD.zip](Conversao_IFCtoLBD.zip) fornece a conversão semântica arquitetônica reutilizada pelo N1. [Identidades_IFC_RDF.csv](Identidades_IFC_RDF.csv) relaciona os GlobalIds às URIs utilizadas no RDF. As instruções de leitura e processamento estão nos notebooks.
