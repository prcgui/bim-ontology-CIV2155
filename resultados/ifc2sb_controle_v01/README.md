# IFC2SB: controle e creche integral · v01

O ensaio utiliza o programa C++ [IFC2SB dos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), associado ao [artigo de Fichter et al. (2021)](https://doi.org/10.26868/25222708.2021.30156), com ajustes de compilação registrados. A versão do executável é 0.9 (2022); não se presume identidade com a versão do benchmark do artigo.

- [Relatório em PDF](Relatorio_IFC2SB_Controle_Creche_v01.pdf).
- [Notebook 5 executado: auditoria dos arquivos e registros](../../notebooks/05_IFC2SB_Controle_e_Creche_v01.ipynb).
- [Registros completos: entradas do controle, saída IFC, logs, CSVs e diffs](CIV2155_IFC2SB_Controle_Creche_v01_Registros.zip).
- [Código de supervisão, auditoria e preparação](../../consultas/ifc2sb_controle_v01/) · [pacote](CIV2155_IFC2SB_v01_Codigo.zip) · [instruções](LEIA_ME_IFC2SB_v01.txt).
- [PDF do artigo e fontes publicadas](../../referencias/geometria_relacoes/).

## Resultados e interpretação

| Caso | Resultado observado | Limite de interpretação |
| --- | --- | --- |
| Controle FZK-Haus | 4 espaços interiores; 131 limites de primeiro nível e 964 de segundo nível; execução de aproximadamente 90 s. | A entrada tinha 7 espaços: quatro ambientes aparecem reunidos em um. Não houve validação arquitetônica independente. |
| Creche integral FNDE ARQ-DTV R03 | Limite operacional predefinido de 600 s atingido, sem IFC de saída auditável. | Não comprova impossibilidade do método nem identifica a causa isolada do impedimento. |

Os dois casos utilizaram o mesmo executável, o filtro original de classes e `-j2 --graph`. O controle contém 81 limites genéricos na entrada; a auditoria verifica classes, GUIDs e espaços relacionados para não confundir sua preservação com geração de novos limites.

O IFC FNDE original permaneceu inalterado. Há 631 IfcCovering fora do filtro original do motor, nenhum IfcSlab e nenhum IfcRelSpaceBoundary declarado. Essa diferença de cobertura é uma hipótese a investigar; não foi demonstrada como causa única. Os avisos de geometria do motor também estão preservados.

A geração geométrica ocorre no C++ publicado. As rotinas Python de supervisão e auditoria são específicas deste estudo e consultam a [API oficial IfcOpenShell](https://docs.ifcopenshell.org/ifcopenshell-python/code_examples.html), versão 0.8.4. Os ajustes de compatibilidade estão registrados em nove diffs; OCCT 7.6.3 difere do ambiente original. Não se declara reprodução exata de benchmark.

A adaptação geométrica Python da revisão 03 permanece como experimento auxiliar, distinto do IFC2SB e do GRC original de Lilis. A geração arquitetônica completa da creche e a integração com a estrutura permanecem sem demonstração. Nenhum vínculo novo foi promovido ao RDF como resultado desta execução.
