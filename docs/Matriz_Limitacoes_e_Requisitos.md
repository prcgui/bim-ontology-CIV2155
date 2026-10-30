# Limitações evidências e requisitos de informação

O objetivo do artigo é analisar limitações da transformação IFC para RDF e da articulação entre arquitetura e estrutura, relacionando-as às informações e representações exigidas pela finalidade de uso. A matriz organiza resultados já obtidos; as recomendações não comprovam que uma remodelagem resolveria os problemas.

**Base examinada:** FNDE Tipo 2 R03; resultados dos notebooks 1, 2 e 3 no commit `cb7e422d6a8b56e147884ceef397e52385db8b20`. A conferência adicional dos IFCs registra zero `IfcRelSpaceBoundary` na arquitetura e nenhuma interseção de GUIDs entre os três conjuntos de produtos.

**Leitura dos estatutos:** D significa observado ou demonstrado no recorte indicado. I significa interpretação fundamentada, sem causa isolada. R significa recomendação cujo benefício ainda precisa ser testado. As propostas R01 a R10 são requisitos para a finalidade deste estudo, não obrigações universais de todo modelo IFC.

| Caso | Evidência observada | Origem ou alcance | Requisito proposto e situação |
|---|---|---|---|
| L01 Vínculos entre espaços e elementos | O IFC arquitetônico contém 41 IfcSpace e zero IfcRelSpaceBoundary. A rotina calcula associações a partir da geometria. | Conteúdo do IFC entregue | R01 Definir, para a finalidade de consulta, como recuperar o vínculo espaço-elemento: relação declarada ou cálculo identificado, com origem e geometria acessíveis. R: recomenda-se uma entrega que explicite os vínculos necessários; o ganho de uma reexportação não foi medido. |
| L02 Preparo geométrico dos espaços | A rotina concluiu a associação em 38 dos 41 espaços. Infantil 1, Infantil 5 e Amamentação permaneceram inconclusivos; nove espaços haviam sido recuperados pelo preparo controlado. | Compatibilidade entre representação de entrada e pré-condições do método | R02 Declarar a representação geométrica exigida pelo uso e verificar suas condições de aceitação antes de calcular relações. Quando o método exigir sólido, conferir fechamento e validade. D: preparo controlado ampliou a execução de 29 para 38 espaços. R: benefício de remodelagem ou reexportação permanece não testado. |
| L03 Associação próxima do limite geométrico | JA-04 da Administração não foi associada. A investigação registrada aponta afastamento aproximado de 10 mm, superior aos 0,1 mm admitidos pelo critério de contato. | Critério geométrico e geometria representada | R03 Documentar precisão, tolerâncias e significado da associação, verificando a compatibilidade entre limites dos espaços e representações dos elementos. R: conferir compatibilidade geométrica e avaliar sensibilidade; não foi demonstrado que mover o elemento ou aumentar a tolerância resolva o problema de forma geral. |
| L04 Divergência entre referências documentais | JA-09 da cozinha permaneceu indeterminada porque a prancha 02 diverge das pranchas 24/25. Das nove associações da cozinha, oito têm confirmação positiva na referência adotada. | Documentação e definição da referência de avaliação | R04 Vincular modelo, documentos e revisão; registrar qual referência sustenta cada julgamento e manter divergências como pendências. R: compatibilizar e conferir as referências antes de avaliar o resultado; a resolução do conflito não foi demonstrada. |
| L05 Contexto das propriedades no RDF | Na V137, quatro quantidades aparecem sob o mesmo predicado direto na extração L1. O IFC conserva seus conjuntos, descrições, tipos e unidades; o N3 recuperou nove conjuntos e 34 propriedades simples. | Representação selecionada na conversão | R05 Conservar conjunto, nome original, tipo nominal, valor, unidade e identificador ao mapear propriedades necessárias à consulta. D: recuperação de contexto demonstrada na V137. R: generalização para outros produtos, herança e valores complexos não foi testada. |
| L06 Unidades e referência espacial entre modelos | ARQ, SMT e SCO usam metro, milímetro e centímetro para comprimento. O N2 aplicou os placements e normalizou a geometria para metros; não há MapConversion declarada nem conferência externa de alinhamento. | Interpretação dos arquivos e coordenação entre disciplinas | R06 Documentar unidade por grandeza, cadeia de posicionamentos e referência espacial comum. Validar o alinhamento com pontos ou elementos de controle independentes. D: unidades e placements tratados. R: alinhamento independente e melhoria de uma entrega coordenada permanecem não testados. |
| L07 Identidade e correspondência entre disciplinas | Foram preservadas 26.601 identidades de produtos. Os conjuntos de GUIDs de ARQ, SMT e SCO não têm interseção entre si; as URIs mantêm a origem do modelo. | Identidades dos arquivos e decisão de integração | R07 Preservar identificadores e origem; estabelecer critérios verificáveis quando uma aplicação precisar reconhecer correspondência física entre modelos. D: identidade por fonte preservada. R: correspondência física entre modelos não foi estabelecida ou avaliada. |
| L08 Relação geométrica e significado construtivo | O N2 registrou 1.652 pares positivos segundo seus critérios: 863 interseções parciais, 198 contenções e 591 contatos por face, envolvendo 1.333 elementos estruturais distintos. | Alcance da interpretação dos vínculos calculados | R08 Distinguir relação geométrica calculada de relação funcional declarada ou validada, conservando critério, medida e origem da evidência. D: relações espaciais registradas. R: uso para conclusões funcionais exige informação e validação adicionais. |
| L09 Cobertura das categorias analisadas | A avaliação geométrica selecionou 5.329 elementos. As 17.755 armaduras SCO, 1.365 montagens SMT e 27 elementos de vazios SMT permaneceram na extração semântica, sem teste geométrico individual nesse recorte. | Recorte do procedimento | R09 Definir categorias, granularidade e exclusões conforme as perguntas de competência, tornando explícita a cobertura de cada avaliação. D: cobertura registrada. R: ampliação do procedimento para outras categorias não foi avaliada. |
| L10 Alcance da validação | A amostra documental contém 14 ambientes: 39 positivos recuperados em 43 esperados, uma omissão após execução e três positivos sem resultado por preparo. O contrato SHACL do N3 foi conforme na projeção de 200.962 triplas e detectou 12 defeitos controlados. | Desenho da avaliação e contrato de dados | R10 Associar cada requisito a uma verificação, declarar alvos e informação ausente, e separar conformidade de dados da validação de significado e de projeto. D: contrato e casos controlados avaliados. R: validação independente e generalização permanecem pendentes. |

## Rastreabilidade por caso

### L01 Vínculos entre espaços e elementos

**Demonstrado:** Ausência dessa relação explícita no arquivo examinado e necessidade de uma estratégia complementar na rotina selecionada.

**Limite da conclusão:** Não foi identificado se a ausência decorre da autoria do modelo, do exportador ou da configuração de entrega. Não comprova invalidade do IFC.

**Requisito proposto:** R01 Definir, para a finalidade de consulta, como recuperar o vínculo espaço-elemento: relação declarada ou cálculo identificado, com origem e geometria acessíveis. R: recomenda-se uma entrega que explicite os vínculos necessários; o ganho de uma reexportação não foi medido.

**Tipo de requisito:** Requisito de informação e exportação. **Relação com a disciplina:** Finalidade da informação e interoperabilidade OpenBIM.

**Evidência do caso:** [TIPO2-ARQ-DTV_R03.ifc.zip](../dados/TIPO2-ARQ-DTV_R03.ifc.zip) · [rotina_multiambientes.py](../codigo/rotina_multiambientes.py) · [Esquadrias_Por_Ambiente.csv](../resultados/Esquadrias_Por_Ambiente.csv).

**Fundamentação:** [Noy e McGuinness (2001), p. 4-5](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf); [Rasmussen et al. (2021), §§3.2-3.5](https://doi.org/10.3233/SW-200385); [Kiavarz et al. (2023), §§4.2.2-4.4](https://doi.org/10.3390/buildings13020350); [buildingSMART, IFC4, IfcRelSpaceBoundary](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm).

**Verificação futura necessária:** Comparar o arquivo original com uma exportação documentada que inclua limites de espaços, mantendo o mesmo projeto e o mesmo critério de avaliação.

### L02 Preparo geométrico dos espaços

**Demonstrado:** O preparo empregado não obteve os sólidos exigidos para os três casos. Contagens desses ambientes permanecem ausentes.

**Limite da conclusão:** Falha de preparo não equivale a ausência de elementos, erro de projeto ou invalidade de qualquer representação IFC. Os arquivos de origem não foram remodelados.

**Requisito proposto:** R02 Declarar a representação geométrica exigida pelo uso e verificar suas condições de aceitação antes de calcular relações. Quando o método exigir sólido, conferir fechamento e validade. D: preparo controlado ampliou a execução de 29 para 38 espaços. R: benefício de remodelagem ou reexportação permanece não testado.

**Tipo de requisito:** Requisito de representação geométrica e verificação. **Relação com a disciplina:** Modelagem da informação e adequação ao uso.

**Evidência do caso:** [Ambientes.csv](../resultados/Ambientes.csv) · [Resumo.json](../resultados/Resumo.json) · [Metodo_e_Alcance.md](../docs/Metodo_e_Alcance.md).

**Fundamentação:** [Fichter et al. (2021), geração de limites](https://doi.org/10.26868/25222708.2021.30156); [Lilis et al. (2025), §§3.1-3.4](https://doi.org/10.1016/j.autcon.2025.106081); [buildingSMART, IFC4, IfcRelSpaceBoundary](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm); [Ying e Lee (2021), §§3.1 e 4.3](https://doi.org/10.1016/j.autcon.2021.103659); [Lilis et al. (2026), §§4-5](https://doi.org/10.1016/j.jobe.2026.115667).

**Verificação futura necessária:** Inspecionar os três casos e comparar representações alternativas em cópias controladas, com teste de preservação da geometria e avaliação independente.

### L03 Associação próxima do limite geométrico

**Demonstrado:** Uma omissão no caso documental examinado; não se ampliou a tolerância para obter a associação esperada.

**Limite da conclusão:** O diagnóstico não identifica sozinho erro de modelagem nem estabelece a tolerância ideal. O afastamento não foi medido novamente nesta matriz.

**Requisito proposto:** R03 Documentar precisão, tolerâncias e significado da associação, verificando a compatibilidade entre limites dos espaços e representações dos elementos. R: conferir compatibilidade geométrica e avaliar sensibilidade; não foi demonstrado que mover o elemento ou aumentar a tolerância resolva o problema de forma geral.

**Tipo de requisito:** Requisito de geometria e procedimento de análise. **Relação com a disciplina:** Compatibilização e critérios de coordenação.

**Evidência do caso:** [Analise_dos_Resultados.md](../docs/Analise_dos_Resultados.md) · [Analise_Documental_14_Ambientes.csv](../resultados/Analise_Documental_14_Ambientes.csv).

**Fundamentação:** [Kiavarz et al. (2023), §§4.2.2-4.4](https://doi.org/10.3390/buildings13020350); [Lilis et al. (2025), §§3.1-3.4](https://doi.org/10.1016/j.autcon.2025.106081); [Lilis et al. (2026), §§4-5](https://doi.org/10.1016/j.jobe.2026.115667).

**Verificação futura necessária:** Avaliar tolerâncias predefinidas contra referência independente, incluindo positivos e negativos, antes de recomendar alteração do modelo.

### L04 Divergência entre referências documentais

**Demonstrado:** A documentação examinada não forneceu uma classificação inequívoca desse caso; ele não foi contado como acerto ou erro.

**Limite da conclusão:** O caso não permite responsabilizar o conversor ou declarar incorreta a esquadria. A referência documental foi usada no desenvolvimento.

**Requisito proposto:** R04 Vincular modelo, documentos e revisão; registrar qual referência sustenta cada julgamento e manter divergências como pendências. R: compatibilizar e conferir as referências antes de avaliar o resultado; a resolução do conflito não foi demonstrada.

**Tipo de requisito:** Requisito de coordenação da informação. **Relação com a disciplina:** Coordenação BIM e gestão da informação.

**Evidência do caso:** [Origem.json](../dados/Origem.json) · [Analise_dos_Resultados.md](../docs/Analise_dos_Resultados.md) · [Analise_Documental_14_Ambientes.csv](../resultados/Analise_Documental_14_Ambientes.csv).

**Fundamentação:** [Noy e McGuinness (2001), p. 4-5](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf); [Ziegler e Dittrich (2007), integração estrutural e semântica](https://doi.org/10.1007/978-3-540-72677-7_3); [FNDE, Projeto Tipo 2, revisão R03](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2).

**Verificação futura necessária:** Realizar conferência por especialista, com fonte e revisão explicitadas, sem ajustar a referência para concordar com a saída.

### L05 Contexto das propriedades no RDF

**Demonstrado:** A POC preservou os valores 0,140544 m³, 1,87392 m², 4,26151 kg e 2,04999 kg com seus contextos. Os cinco grafos do N2 permaneceram inalterados.

**Limite da conclusão:** A informação contextual já existia no IFC. Não cabe atribuir essa dificuldade à falta de modelagem desses dados. A POC cobre somente um elemento e valores simples diretamente associados.

**Requisito proposto:** R05 Conservar conjunto, nome original, tipo nominal, valor, unidade e identificador ao mapear propriedades necessárias à consulta. D: recuperação de contexto demonstrada na V137. R: generalização para outros produtos, herança e valores complexos não foi testada.

**Tipo de requisito:** Requisito de representação semântica e conversão. **Relação com a disciplina:** Modelagem da informação e interoperabilidade.

**Evidência do caso:** [Propriedades_V137.json](../resultados/organizacao/Propriedades_V137.json) · [Propriedades_V137.nt](../resultados/organizacao/Propriedades_V137.nt) · [organizar_dataset.py](../codigo/organizar_dataset.py) · [Resumo_Organizacao.json](../resultados/organizacao/Resumo_Organizacao.json).

**Fundamentação:** [Bonduel et al. (2018), §§1.3 e 2.1](https://ceur-ws.org/Vol-2159/04paper.pdf); [buildingSMART, IFC4, IfcPropertySingleValue](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcpropertyresource/lexical/ifcpropertysinglevalue.htm).

**Verificação futura necessária:** Aplicar o mapeamento a uma amostra planejada de outros tipos e modelos, incluindo unidades explícitas e propriedades herdadas.

### L06 Unidades e referência espacial entre modelos

**Demonstrado:** Tratamento das unidades e posicionamentos declarados. O deslocamento do terreno SCO, de -40 m em X, foi considerado uma vez na cadeia de placements.

**Limite da conclusão:** Unidades diferentes são representações válidas. Ausência de MapConversion não impede toda coordenação local nem prova desalinhamento; o alinhamento físico não foi validado independentemente.

**Requisito proposto:** R06 Documentar unidade por grandeza, cadeia de posicionamentos e referência espacial comum. Validar o alinhamento com pontos ou elementos de controle independentes. D: unidades e placements tratados. R: alinhamento independente e melhoria de uma entrega coordenada permanecem não testados.

**Tipo de requisito:** Requisito de coordenação e interpretação geométrica. **Relação com a disciplina:** Interface arquitetura e estrutura e coordenação BIM.

**Evidência do caso:** [Fontes_e_Referenciais.json](../resultados/integracao/Fontes_e_Referenciais.json) · [Resumo_Geometrico.json](../resultados/integracao/Resumo_Geometrico.json) · [Modelos_Integracao.json](../dados/Modelos_Integracao.json).

**Fundamentação:** [Lilis et al. (2025), §§3.1-3.4](https://doi.org/10.1016/j.autcon.2025.106081); [buildingSMART, IFC4, IfcRelSpaceBoundary](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm); [buildingSMART, IFC4, IfcPropertySingleValue](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcpropertyresource/lexical/ifcpropertysinglevalue.htm); [Ziegler e Dittrich (2007), integração estrutural e semântica](https://doi.org/10.1007/978-3-540-72677-7_3).

**Verificação futura necessária:** Conferir pontos de controle de referência conhecida e quantificar desvios, registrando a procedência de qualquer transformação.

### L07 Identidade e correspondência entre disciplinas

**Demonstrado:** Identificação dos produtos dentro de cada arquivo e separação das fontes, sem inferência de owl:sameAs.

**Limite da conclusão:** GUIDs distintos não constituem erro e não provam que os modelos descrevam objetos físicos diferentes. Nomes iguais também não demonstram identidade.

**Requisito proposto:** R07 Preservar identificadores e origem; estabelecer critérios verificáveis quando uma aplicação precisar reconhecer correspondência física entre modelos. D: identidade por fonte preservada. R: correspondência física entre modelos não foi estabelecida ou avaliada.

**Tipo de requisito:** Requisito de identidade e integração semântica. **Relação com a disciplina:** Interoperabilidade e interface entre disciplinas.

**Evidência do caso:** [Identidades_Modelos.csv](../resultados/integracao/Identidades_Modelos.csv) · [Resumo_Integracao.json](../resultados/integracao/Resumo_Integracao.json).

**Fundamentação:** [Rasmussen et al. (2021), §§3.2-3.5](https://doi.org/10.3233/SW-200385); [Ziegler e Dittrich (2007), integração estrutural e semântica](https://doi.org/10.1007/978-3-540-72677-7_3).

**Verificação futura necessária:** Construir uma referência de correspondências validada por especialista e avaliar regras de pareamento antes de afirmar equivalência.

### L08 Relação geométrica e significado construtivo

**Demonstrado:** Registro e consulta das relações no referencial adotado. Cozinha e V137 têm contato por face de 0,4674837228519026 m² segundo a operação executada.

**Limite da conclusão:** Não há referência independente para classificar os 1.652 vínculos. Contato ou interseção não demonstra apoio, ligação, capacidade resistente ou adequação estrutural.

**Requisito proposto:** R08 Distinguir relação geométrica calculada de relação funcional declarada ou validada, conservando critério, medida e origem da evidência. D: relações espaciais registradas. R: uso para conclusões funcionais exige informação e validação adicionais.

**Tipo de requisito:** Requisito de significado e rastreabilidade. **Relação com a disciplina:** Interface arquitetura e estrutura e finalidade da informação.

**Evidência do caso:** [Relacoes_Espaciais.csv](../resultados/integracao/Relacoes_Espaciais.csv) · [Resumo_Integracao.json](../resultados/integracao/Resumo_Integracao.json) · [03_cozinha_v137.csv](../resultados/organizacao/03_cozinha_v137.csv).

**Fundamentação:** [Rasmussen et al. (2021), §§3.2-3.5](https://doi.org/10.3233/SW-200385); [Lilis et al. (2025), §§3.1-3.4](https://doi.org/10.1016/j.autcon.2025.106081).

**Verificação futura necessária:** Selecionar relações funcionais relevantes e confrontá-las com documentos e avaliação de domínio independentes.

### L09 Cobertura das categorias analisadas

**Demonstrado:** Distinção entre elementos representados semanticamente e elementos submetidos à análise geométrica.

**Limite da conclusão:** Ausência de vínculo calculado fora do recorte não demonstra ausência física ou perda do objeto na conversão.

**Requisito proposto:** R09 Definir categorias, granularidade e exclusões conforme as perguntas de competência, tornando explícita a cobertura de cada avaliação. D: cobertura registrada. R: ampliação do procedimento para outras categorias não foi avaliada.

**Tipo de requisito:** Requisito de escopo e nível de informação. **Relação com a disciplina:** Requisitos de informação e planejamento da modelagem.

**Evidência do caso:** [Resumo_Geometrico.json](../resultados/integracao/Resumo_Geometrico.json) · [07_armaduras_sem_avaliacao_geometrica.csv](../resultados/organizacao/07_armaduras_sem_avaliacao_geometrica.csv).

**Fundamentação:** [Noy e McGuinness (2001), p. 4-5](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf); [Lilis et al. (2025), §§3.1-3.4](https://doi.org/10.1016/j.autcon.2025.106081).

**Verificação futura necessária:** Priorizar outra categoria a partir de uma pergunta concreta e definir sua referência de avaliação antes de ampliar o código.

### L10 Alcance da validação

**Demonstrado:** Resultados nessa amostra e nas condições expressas pelo contrato. Os alvos incluem 26.601 produtos, três modelos, 1.652 registros e 41 resultados por ambiente.

**Limite da conclusão:** A referência foi construída com leitura assistida por IA e usada no desenvolvimento. Não houve avaliação cega, segundo edifício ou certificação global da semântica. As mutações não estimam precisão geral.

**Requisito proposto:** R10 Associar cada requisito a uma verificação, declarar alvos e informação ausente, e separar conformidade de dados da validação de significado e de projeto. D: contrato e casos controlados avaliados. R: validação independente e generalização permanecem pendentes.

**Tipo de requisito:** Requisito de verificação e avaliação. **Relação com a disciplina:** Qualidade da informação e verificação de requisitos.

**Evidência do caso:** [Analise_Documental_14_Ambientes.csv](../resultados/Analise_Documental_14_Ambientes.csv) · [Resumo_SHACL.json](../resultados/organizacao/Resumo_SHACL.json) · [Restricoes_Organizacao.ttl](../codigo/Restricoes_Organizacao.ttl) · [Analise_dos_Resultados.md](../docs/Analise_dos_Resultados.md).

**Fundamentação:** [Noy e McGuinness (2001), p. 4-5](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf); [W3C (2017), SHACL, alvos e restrições](https://www.w3.org/TR/shacl/).

**Verificação futura necessária:** Realizar avaliação independente com amostra e critérios previamente definidos, incluindo casos ausentes e negativos.

## Limites comuns da interpretação

Ausência de uma relação no IFC entregue não identifica sozinha uma falha no modelo autoral. É necessário examinar também exportação, configuração e requisitos de entrega. Unidades diferentes e GUIDs distintos entre disciplinas não são erros por si. Uma contagem ausente por falha de preparo não equivale a zero. Contato geométrico não comprova função estrutural.

A amostra documental foi usada no desenvolvimento e não teve validação independente. A POC de propriedades cobre apenas a V137. Não houve comparação controlada com um IFC remodelado. A classificação de cada caso impede atribuir essas limitações genericamente a uma modelagem inadequada.

O explorador auxilia a inspeção dos resultados. Sua existência não mede usabilidade ou qualidade ontológica global. O registro técnico de conferência e os ensaios permanecem no Google Drive; esta página apresenta a análise selecionada.

## Referências

**F01.** NOY, Natalya F.; MCGUINNESS, Deborah L. Ontology development 101: a guide to creating your first ontology. Stanford: Stanford University, 2001. Disponível em: https://protege.stanford.edu/publications/ontology_development/ontology101.pdf. Acesso em: 30 out. 2026.

**F02.** BONDUEL, Mathias et al. The IFC to Linked Building Data converter: current status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018, Londres. Proceedings [...]. CEUR Workshop Proceedings, v. 2159, p. 34-43, 2018. Disponível em: https://ceur-ws.org/Vol-2159/04paper.pdf. Acesso em: 30 out. 2026.

**F03.** RASMUSSEN, Mads Holten; LEFRANÇOIS, Maxime; SCHNEIDER, Georg Ferdinand; PAUWELS, Pieter. BOT: the building topology ontology of the W3C linked building data group. Semantic Web, v. 12, n. 1, p. 143-161, 2021. DOI: https://doi.org/10.3233/SW-200385.

**F04.** FICHTER, Eric; RICHTER, Veronika; FRISCH, Jérôme; VAN TREECK, Christoph. Automatic generation of second level space boundary geometry from IFC models. In: BUILDING SIMULATION, 17., 2021, Bruges. Proceedings [...]. IBPSA, 2021. p. 1083-1090. DOI: https://doi.org/10.26868/25222708.2021.30156.

**F05.** KIAVARZ, Hamid et al. An automated space-based graph generation framework for building energy consumption estimation. Buildings, v. 13, n. 2, art. 350, 2023. DOI: https://doi.org/10.3390/buildings13020350.

**F06.** LILIS, Georgios Nektarios et al. BIM-based semantic enrichment and knowledge graph generation via geometric relation checking. Automation in Construction, v. 173, art. 106081, 2025. DOI: https://doi.org/10.1016/j.autcon.2025.106081.

**F07.** BUILDINGSMART INTERNATIONAL. IFC4: IfcRelSpaceBoundary. [S. l.], [s. d.]. Disponível em: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcrelspaceboundary.htm. Acesso em: 30 out. 2026.

**F08.** BUILDINGSMART INTERNATIONAL. IFC4: IfcPropertySingleValue. [S. l.], [s. d.]. Disponível em: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcpropertyresource/lexical/ifcpropertysinglevalue.htm. Acesso em: 30 out. 2026.

**F09.** ZIEGLER, Patrick; DITTRICH, Klaus R. Data integration: problems, approaches, and perspectives. In: KROGSTIE, John; OPDAHL, Andreas L.; BRINKKEMPER, Sjaak (ed.). Conceptual modelling in information systems engineering. Berlin; Heidelberg: Springer, 2007. p. 39-58. DOI: https://doi.org/10.1007/978-3-540-72677-7_3.

**F10.** W3C. Shapes Constraint Language SHACL. W3C Recommendation, 20 jul. 2017. Disponível em: https://www.w3.org/TR/shacl/. Acesso em: 30 out. 2026.

**F11.** FUNDO NACIONAL DE DESENVOLVIMENTO DA EDUCAÇÃO. Creche Pré-Escola Tipo 2. Brasília, DF: FNDE, [s. d.]. Disponível em: https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2. Acesso em: 30 out. 2026.

**F12.** YING, Huaquan; LEE, Sanghoon. Generating second-level space boundaries from large-scale IFC-compliant building information models using multiple geometry representations. Automation in Construction, v. 126, art. 103659, 2021. DOI: https://doi.org/10.1016/j.autcon.2021.103659.

**F13.** LILIS, Georgios Nektarios; WANG, Meng; KATSIGARAKIS, Kyriakos; ROVAS, Dimitrios. BIM geometric error detection for building energy model generation. Journal of Building Engineering, v. 122, art. 115667, 2026. DOI: https://doi.org/10.1016/j.jobe.2026.115667.
