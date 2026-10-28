# Diagnóstico da tentativa de integração entre arquitetura e estrutura

Estudo exploratório sobre os modelos `TIPO2-ARQ-DTV_R03.ifc` e `TIPO2-SMT-MOD_R03.ifc`, do Projeto Tipo 2 do FNDE. As conversões são executadas separadamente com o IFCtoLBD 2.49.0, a adaptação textual previamente documentada e a inclusão explícita dos elementos. Os resultados desta etapa não abrangem o modelo SCO.

**Situação:** grafos produzidos e verificados separadamente; correspondências semânticas e divergências de recuperação espacial permanecem pendentes. Não foram aplicadas soluções aos problemas novos encontrados.

## Resultados observados

| Indicador | Arquitetura | Estrutura SMT |
| --- | ---: | ---: |
| Produtos IFC examinados | 2.116 | 5.256 |
| Elementos IFC | 2.071 | 5.253 |
| Elementos representados como `bot:Element` | 2.071 | 5.253 |
| Ambientes IFC e `bot:Space` | 41 | 0 |
| Triplas no grafo | 56.961 | 84.933 |
| Identificadores de produtos ausentes | 0 | 0 |
| Divergências nos textos comparados | 0 | 0 |
| Vínculos com pavimentos não recuperados pelo critério adotado | 184 | 5.253 |

A arquitetura possui 2.110 valores de `Name`, 41 de `LongName` e 41 categorias de ambientes examinados por igualdade exata. Os produtos SMT possuem 5.256 valores de `Name` examinados. Esses valores foram preservados. A ausência de `IfcSpace` no SMT é uma condição da entrada e não constitui, por si, perda de conversão.

## Problemas e decisões pendentes

1. **Recuperação dos vínculos espaciais.** O critério percorre, em sentido inverso, `bot:containsElement`, `bot:hasSpace`, `bot:hasSubElement` e `bot:hasStorey`, buscando recursos `bot:Storey` e seus GUIDs. Não recupera como no IFC os vínculos de 184 `IfcOpeningElement` da arquitetura e dos 5.253 elementos SMT. Esse achado ainda exige examinar a correspondência entre as relações IFC, o mapeamento e o caminho de consulta. Não demonstra, isoladamente, perda do conversor. O critério não foi ampliado para eliminar as divergências.
2. **Identidade entre modelos.** Nenhum `GlobalId` de `IfcProduct` é compartilhado entre arquitetura e SMT. O pareamento direto entre fonte IFC e sua própria saída LBD não fornece, portanto, uma correspondência entre os dois modelos. Não foram criadas equivalências a partir dos nomes.
3. **Unidades e referenciais.** A arquitetura utiliza fator 1 para metro e o SMT fator 0,001. Os pavimentos denominados `COBERTURA` têm GUIDs diferentes e cotas declaradas de 3,26 m e 0,00 m, respectivamente, após expressar as unidades em metros. Essas cotas não são coordenadas globais calculadas; a equivalência dos pavimentos e seus referenciais permanece por verificar. A diferença não comprova erro de projeto ou interferência geométrica.
4. **Limite da verificação SHACL.** Ambos os grafos atendem às regras declaradas de identificador e de vínculo dos ambientes. A regra de ambientes alcança 41 recursos na arquitetura e nenhum no SMT. Esse resultado é compatível com a permanência das divergências dos elementos, pois as regras não verificam a recuperação dos vínculos de todos os elementos com pavimentos. A conformidade não comprova integração completa.

## Evidências e reprodução

- [Notebook 2, com fontes e saídas de execução](../../notebooks/02_integracao_arquitetura_estrutura.ipynb).
- [Resumo dos modelos](resumo_modelos.csv).
- [Quadro de problemas e pendências](problemas_e_pendencias.csv).
- [Pavimentos candidatos de comparação](pavimentos_candidatos.csv).
- [Resultados e quantidade de alvos SHACL](validacao_shacl.json).
- [Manifesto da etapa, fontes e escopo](manifesto_estudo.json).
- [Pacote completo de evidências](02_diagnostico_arquitetura_estrutura.zip): grafos separados, inventários, comparações, vínculos pendentes, logs, comandos, hashes e relatórios.

As saídas foram obtidas em execução local com Java 21 e Python. A geometria não foi processada para detectar interferências; os modelos não tiveram seus referenciais reconciliados. A contribuição desta etapa é o diagnóstico reproduzível dos limites e das decisões necessárias à integração semântica.
