# Contribuições verificadas para incorporação ao artigo

Este texto reúne uma contribuição delimitada de método, resultados e limitações. Não substitui o manuscrito completo. Em 30/10/2026, não foi localizado o artigo atual no repositório simplificado, na pasta local `06_Redacao` ou na pasta `06_Texto_Academico` do Google Drive, ambas conferidas vazias. Portanto, não se afirma revisão do manuscrito nem conferência de seu limite de 15 páginas.

## Método

A integração de fontes exige conservar o contexto necessário à interpretação dos dados, além de oferecer uma apresentação comum (ZIEGLER; DITTRICH, 2007). Neste estudo, o resultado arquitetônico do primeiro notebook e as extrações estruturais foram reunidos em grafos nomeados, com identidades e proveniência preservadas. Sobre esse resultado, foi desenvolvida uma extensão incremental para distinguir produtos físicos de registros sobre modelos, propriedades e evidências. Os esquemas e os acréscimos foram mantidos em grafos separados, permitindo comparar os resultados com a base previamente validada.

A exploração foi organizada a partir de perguntas sobre origem, relações, propriedades e informações ausentes. Essa escolha dialoga com a orientação a objetivos de Liu e Yoon (2024), sem reproduzir seu sistema de integração automática. A interface permite selecionar produtos por fonte, classe IFC e tipo RDF, examinar vizinhanças e acessar detalhes e evidências. Visão geral, filtros, histórico e extração foram adaptados das tarefas de busca visual discutidas por Shneiderman (1996). A aplicação complementa os notebooks executáveis e não substitui a interpretação dos resultados.

Uma prova de conceito recuperou conjuntos de propriedades diretamente associados à viga V137. A distinção entre literais diretos e recursos para propriedades, discutida por Bonduel et al. (2018), orientou a preservação de nomes originais, conjuntos, identificadores STEP, tipos de valores e unidades. A unidade explícita da propriedade, quando existente, prevalece; nos demais casos, consulta-se a unidade declarada pelo projeto para o tipo nominal de medida, conforme a especificação IFC4 (BUILDINGSMART INTERNATIONAL, s.d.). Não foram atribuídas dimensões a valores cuja fonte não as declarava.

Um contrato próprio foi expresso em SHACL e executado sem inferência em uma projeção documentada dos dados. O contrato verifica identidade, proveniência, extremos das relações, medidas, estados dos resultados e contexto das propriedades selecionadas (W3C, 2017). A proveniência da execução computacional utiliza PROV-O (W3C, 2013). Essas verificações são delimitadas pelas condições declaradas e não equivalem à certificação global da ontologia ou do projeto.

## Resultados e discussão

O Dataset organizado contém 416.603 quádruplas em nove grafos. Os cinco grafos originais do segundo notebook permaneceram semanticamente idênticos, incluindo 26.601 produtos, 1.652 relações espaciais interdisciplinares e os 101 pares ambiente–esquadria do primeiro notebook. A extensão acrescentou dois esquemas, um grafo de propriedades contextualizadas e um registro de execução. O aumento no número de afirmações descreve a extensão; não constitui, isoladamente, uma medida de qualidade.

Na V137, foram recuperados nove conjuntos e 34 propriedades simples. Quatro valores anteriormente apresentados sob um mesmo predicado de quantidade passaram a conservar seus respectivos contextos: 0,140544 m³ de concreto, 1,87392 m² de forma, 4,26151 kg de aço CA50 e 2,04999 kg de aço CA60. Os valores e as relações originais foram preservados. O caso evidencia que a unidade de comprimento do projeto não deve ser automaticamente elevada ao quadrado ou ao cubo para interpretar outras medidas.

As oito consultas permitem recuperar fontes, vínculos e lacunas, incluindo três ambientes inconclusivos e 17.755 armaduras SCO sem avaliação geométrica individual. O contrato SHACL foi satisfeito na projeção de 200.962 triplas. O ganho demonstrado consiste na recuperação de contexto, na organização explícita dos níveis e na possibilidade de verificar consultas e condições. Não foi realizado estudo com participantes que permita afirmar melhora mensurada de usabilidade.

## Limitações

A reorganização não resolve a ausência de validação independente do alinhamento dos IFCs. Contato e interseção geométrica não demonstram apoio, função ou adequação estrutural. Infantil 1, Infantil 5 e Amamentação permanecem inconclusivos, sem atribuição de zero. A recuperação de contexto foi testada em um elemento, sem generalização para todos os tipos de propriedades, herança de tipos ou harmonização global. A navegação por fonte não equivale a uma classificação de sistemas construtivos, e não foram inferidas identidades físicas entre modelos.

## Inserção no manuscrito

Priorizar uma subseção curta de método, um parágrafo de resultados e a limitação da POC. A tabela das quatro quantidades pode substituir uma figura redundante. Manter código, inventário, matriz integral e auditorias fora das 15 páginas do artigo. A extensão proposta preserva a pergunta sobre representação e integração BIM; mineração de processos, causalidade e aprendizado de máquina exigiriam outra pergunta e novas bases, não tendo sido incorporados. A paginação final depende do manuscrito e do modelo da disciplina, que não estavam disponíveis.

## Referências em formato ABNT

BONDUEL, Mathias et al. The IFC to Linked Building Data converter: current status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018. *Proceedings [...]*. CEUR Workshop Proceedings, v. 2159, p. 34–43, 2018. Disponível em: <https://ceur-ws.org/Vol-2159/04paper.pdf>. Acesso em: 30 out. 2026.

BUILDINGSMART INTERNATIONAL. *IFC4: IfcPropertySingleValue*. [S. l.], [s. d.]. Disponível em: <https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcpropertyresource/lexical/ifcpropertysinglevalue.htm>. Acesso em: 30 out. 2026.

LIU, Dapeng; YOON, Victoria Y. Developing a goal-driven data integration framework for effective data analytics. *Decision Support Systems*, v. 180, art. 114197, 2024. DOI: <https://doi.org/10.1016/j.dss.2024.114197>.

SHNEIDERMAN, Ben. The eyes have it: a task by data type taxonomy for information visualizations. In: IEEE SYMPOSIUM ON VISUAL LANGUAGES, 1996. *Proceedings [...]*. IEEE, 1996. p. 336–343. DOI: <https://doi.org/10.1109/VL.1996.545307>.

W3C. *PROV-O: the PROV ontology*. W3C Recommendation, 30 abr. 2013. Disponível em: <https://www.w3.org/TR/prov-o/>. Acesso em: 30 out. 2026.

W3C. *Shapes Constraint Language SHACL*. W3C Recommendation, 20 jul. 2017. Disponível em: <https://www.w3.org/TR/shacl/>. Acesso em: 30 out. 2026.

ZIEGLER, Patrick; DITTRICH, Klaus R. Data integration: problems, approaches, and perspectives. In: KROGSTIE, John; OPDAHL, Andreas L.; BRINKKEMPER, Sjaak (ed.). *Conceptual modelling in information systems engineering*. Berlin; Heidelberg: Springer, 2007. p. 39–58. DOI: <https://doi.org/10.1007/978-3-540-72677-7_3>.
