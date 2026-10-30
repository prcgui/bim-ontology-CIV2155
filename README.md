# bim-ontology-CIV2155

Projeto acadêmico desenvolvido no âmbito da disciplina CIV2155, dedicado à organização e à representação semântica de informações BIM por meio de ontologias.

## Notebook 1 v10 · aprimoramento orientado pela literatura

[Notebook 1 v10](notebooks/01_Conversao_Arquitetura_IFC_LBD_v10.ipynb) · [Análise minuciosa e ensaios](resultados/aprimoramento_n1_v10/) · [Código](consultas/aprimoramento_n1_v10/) · [Literatura, decisões e fontes](referencias/aprimoramento_n1_v10/).

O acervo inicial de 73 PDFs contém 63 conteúdos distintos: seis pranchas e 57 documentos bibliográficos/técnicos. A triagem de todo o acervo e a leitura dirigida das propostas prioritárias orientaram a recuperação controlada de BRep, o preparo de aberturas por suas próprias faces, a normalização planar rastreada, a partição de áreas, as tentativas de confirmação volumétrica e os contratos SHACL. O relatório registra a decisão sobre cada documento e sete análises aprofundadas. Não se afirma reprodução de todos os experimentos publicados.

**A associação passou de 29 para 38 dos 41 espaços**, com três inconclusivos. Todos os 457 recortes de parede foram preparados. Os 29 BReps aceitos anteriormente permanecem idênticos por hash e os 74 pares ambiente–esquadria anteriores foram preservados; a v10 registra 101 pares e 66 esquadrias distintas. Pares não equivalem a peças físicas.

Na mesma amostra documental de 14 ambientes, os positivos confirmados passaram de **35/43 (81,4%) para 39/43 (90,7%)**, incluindo os não recuperados por preparo no denominador. Permanecem uma omissão após execução, três positivos sem resultado por preparo e JA-09 indeterminada. Nos negativos avaliados, houve 37 exclusões corretas e nenhuma associação indevida; dois negativos ficaram não avaliáveis. A amostra é intencional, assistida por IA e usada no desenvolvimento, sem avaliação cega ou externa.

**106 controles aprovados**, além da reexecução dos lotes, ablação sem normalização planar, ensaio 2D, auditorias e validação SHACL do grafo completo. O ensaio 2D encontrou contornos nos 41 espaços, mas somente 33 positivos, e não substituiu o núcleo 3D. A v10 preserva o grafo v09 e registra separadamente regiões concorrentes, contenções inconclusivas e candidatos com folga.

Infantil 1, Infantil 5 e Amamentação continuam inconclusivos. A JA-04 da Administração permanece omissão primária, com candidato projetado a aproximadamente 10 mm da face do espaço. Há 23 pares de espaços sobrepostos e hospedeiros concorrentes em 28 espaços. Esses diagnósticos não foram apagados nem corrigidos silenciosamente no IFC. Os resultados não comprovam completude de todas as associações/interfaces ou ganho geral de velocidade. Referências, adaptações e licenças permanecem explícitas no Notebook 1.

## Notebook 1 v09 · aplicação aos 41 ambientes

[Notebook 1 v09](notebooks/01_Conversao_Arquitetura_IFC_LBD_v09.ipynb) · [Cobertura, relatório e resultados](resultados/multiambientes_v01/) · [Código generalizado](consultas/multiambientes_v01/) · [Amostra documental e fontes](referencias/multiambientes_v01/).

O núcleo IFC2SB parcial + Kiavarz foi aplicado aos 41 IfcSpace do IFC original, com parâmetros comuns e preparo compartilhado das paredes. **29 espaços chegaram à associação e 12 ficaram inconclusivos no preparo.** Dos 29, vinte não tiveram pendências registradas nesse recorte e nove tiveram pendências de faces/recortes. Isso descreve execução, não aprovação arquitetônica completa.

Foram registrados 74 pares ambiente–esquadria, envolvendo 57 esquadrias distintas. A mesma porta pode delimitar dois cômodos; os pares não são quantitativos de peças. O grafo completo v08 foi preservado e recebeu os estados e evidências da v09, incluindo os inconclusivos sem contagem falsa de zero.

A conferência documental abrange 14 ambientes, sendo 13 além da cozinha: despensa, copa, vestiários, sanitários PCD, sala de atendimento, sala de professores, lactário, Infantil 2/3, Administração, Infantil 1 e Lavanderia/Rouparia. Na parte processada, houve 35 associações e 33 exclusões corretas, sem associação indevida ou omissão após associação nos casos determinados. **Oito referências positivas não foram recuperadas** por causa do preparo inconclusivo dos três últimos ambientes. A JA-09 da cozinha permanece indeterminada. A amostra é intencional e assistida por IA, sem revisão cega por especialista.

Há evidência de funcionamento em dez novos cômodos processados da amostra. Não se afirma cobertura completa do edifício: além dos 12 espaços inconclusivos, quatro recortes de parede não foram concluídos pelo módulo parcial e foram encontradas sobreposições em 12 pares de espaços aceitos. Os diagnósticos novos usam OCP; CGAL/Krijnen da cozinha não foi transplantado e o fluxo integral de Lilis não foi executado. Referências, atribuição, licenças e o papel de cada etapa permanecem explícitos no notebook.

## Notebook 1 v08 · rotina consolidada e conferência documental da cozinha

[Notebook 1 v08 executado](notebooks/01_Conversao_Arquitetura_IFC_LBD_v08.ipynb) · [Resultados e relatório](resultados/consolidacao_hibrido_v01/) · [Rotina única](consultas/consolidacao_hibrido_v01/) · [Pranchas oficiais e referência caso a caso](referencias/consolidacao_hibrido_v01/).

A rotina reexecuta os recortes IFC2SB parciais e as interfaces adaptadas de Kiavarz, mantendo as avaliações CGAL como entradas verificadas. Lilis permanece comparação opcional. O complemento é ligado por GUID às identidades do grafo completo anterior, que permanece preservado. O perfil está restrito à cozinha FNDE ARQ-DTV R03.

Na conferência das pranchas 02, 24, 25 e 26, oito esquadrias têm referência positiva e seis objetos vizinhos têm referência negativa. O híbrido acertou esses 14 casos, com zero associações indevidas e zero omissões. A JA-09 ficou indeterminada por divergência entre a planta geral e as ampliações. A conferência é documental, assistida por IA, sem revisão cega por especialista.

| Procedimento no mesmo recorte | Associações corretas | Indevidas | Omissões |
|---|---:|---:|---:|
| Listagem v03 por parede, se usada como hipótese de pertencimento | 4 | 2 | 4 |
| IFC2SB parcial v04 | 8 | 0 | 0 |
| Híbrido consolidado v08 | 8 | 0 | 0 |

A v03 já advertia que a cadeia parede–abertura–preenchimento **não prova pertencimento ao cômodo**. A primeira linha avalia essa listagem como hipótese exploratória; não transforma a advertência da v03 em uma alegação de classificação arquitetônica. O ganho demonstrado é frente à utilização da listagem por parede para essa pergunta. Frente ao IFC2SB parcial, o híbrido mantém os acertos e acrescenta organização por interface, proveniência e integração ao grafo principal.

A saída distingue nove esquadrias geometricamente associadas (incluindo a JA-09 pendente), outro preenchimento IfcWall AL25, dez elementos internos candidatos e três componentes sem FillsVoids candidatos. Esses conjuntos têm significados diferentes e não são somados como nove ou vinte e três “portas e janelas”. A validação exaustiva de superfícies, demais categorias e outros cômodos permanece pendente. As versões v03–v07 continuam preservadas como histórico.

## Ensaio parcial de Lilis · Notebook 1 v07

[Notebook 1 v07](notebooks/01_Conversao_Arquitetura_IFC_LBD_v07.ipynb) · [Notebook 9 independente](notebooks/09_Lilis_Hibrido_Cozinha_v01.ipynb) · [Resultados e limites](resultados/lilis_hibrido_v01/).

As oito células novas foram executadas com 20 controles aprovados e aplicam operadores de projeção e subtração de Lilis et al. (2026) ao piloto da cozinha. As dez aberturas distintas do híbrido anterior foram mantidas. São 12 recortes locais candidatos: 11 com apoio no volume 3D e um adicional de 0,062 m² por projeção, mantido para conferência. O RDF conserva todas as 2.559 triplas anteriores e passa a 3.244. A contribuição observada é a comparação de recortes e o cálculo rastreável dos resíduos; não foi demonstrado ganho de acurácia arquitetônica. Alpha wrap e o método completo não foram implementados.

## Interfaces híbridas da cozinha · Notebook 1 v06

O [Notebook 1 v06](notebooks/01_Conversao_Arquitetura_IFC_LBD_v06.ipynb) e o [Notebook 8 independente](notebooks/08_Interfaces_Hibridas_Cozinha_v01.ipynb) combinam recortes da adaptação parcial IFC2SB, sinais do ensaio Krijnen/CGAL e operações geométricas adaptadas de Kiavarz et al. (2023). As oito células novas foram executadas; as etapas anteriores do Notebook 1 são preservadas sem reexecução.

Foram produzidas 14 interfaces qualificadas geometricamente no critério experimental, em dez paredes, e 11 recortes locais associados a dez das 24 aberturas examinadas. O RDF preserva as 1.946 triplas anteriores e contém 2.559 triplas, com coordenadas, proveniência e avaliações negativas. Os 17 controles analíticos foram aprovados. As contagens coincidem com o piloto anterior; a contribuição é a combinação operacional e rastreável, sem demonstração de maior acurácia arquitetônica.

[Resultados e limitações](resultados/interfaces_hibridas_v01/) · [Código](consultas/interfaces_hibridas_v01/) · [Artigos e adaptações](referencias/interfaces_hibridas_v01/) · [Figura consultada do RDF](resultados/interfaces_hibridas_v01/Grafo_RDF_Recorte_Interface.png).

Na revisão 06, Lilis et al. (2026) foi usado somente na triagem de pré-condições. A revisão 07 acima acrescenta a adaptação parcial dos operadores de geração. Volumes compostos e interseções entre espaços permanecem registrados, sem reparação global. A validação arquitetônica independente e a expansão aos demais ambientes continuam pendentes.

## Avaliação geométrica complementar · Krijnen / CGAL

O [ensaio parcial de Krijnen et al. (2020)](resultados/krijnen_cgal_v01/) acrescenta ao fluxo uma avaliação por operações CGAL/Nef, com parâmetros de tolerância e proveniência no RDF. A preparação por componentes fechados permitiu concluir 68 testes das 34 paredes candidatas da cozinha, com 14 controles analíticos aprovados. O novo grafo preserva as 676 triplas anteriores e contém 1.946 triplas, incluindo 68 avaliações. Os sinais distinguem contato, interseção volumétrica e inconclusão; não confirmam automaticamente paredes delimitadoras.

A implementação reutiliza operações do [código dos autores citado no artigo](https://doi.org/10.5281/zenodo.3633653) e explicita as diferenças de interpretação IFC e de preparação geométrica. [Fontes e PDF](referencias/krijnen_cgal_v01/) · [Código do ensaio](consultas/krijnen_cgal_v01/) · [Comparação por parede](resultados/krijnen_cgal_v01/Comparacao_Paredes_IFC2SB_CGAL_v01.csv). A reprodução integral do programa de 2020 e a delimitação semântica completa não são declaradas como concluídas.

O [Notebook 1, revisão 05](notebooks/01_Conversao_Arquitetura_IFC_LBD_v05.ipynb) incorpora as avaliações ao RDF. O [Notebook 7](notebooks/07_Auditoria_Krijnen_CGAL_v01.ipynb) reúne a auditoria executada dos registros e a opção de reexecução do motor em Linux. As etapas anteriores do Notebook 1 são preservadas como registro e não foram reexecutadas nessa revisão.

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
| [notebooks/](notebooks/) | Procedimentos executáveis, referências e registros de execução. |

## Revisão do Notebook 1 a partir da literatura

### Questões de competência e modelo conceitual de referência

A [especificação consolidada em PDF](docs/modelo_conceitual_v01/CIV2155_Questoes_de_Competencia_Modelo_Conceitual_v01.pdf) define três questões arquitetônicas: paredes delimitadoras, aberturas/preenchimentos associados às interfaces e localização de elementos no volume do ambiente. Mantém também CQ1, de controle dos ambientes, e CQ3, relativa às condições da integração com SMT. Para cada questão são registrados significado da relação, resposta esperada, informação necessária e critérios de aceitação, rejeição delimitada e inconclusão.

O modelo distingue declaração IFC, evidência geométrica e decisão arquitetônica independente. A [tabela editável de questões e critérios](docs/modelo_conceitual_v01/Questoes_de_Competencia_e_Criterios_v01.csv), o [esquema conceitual](docs/modelo_conceitual_v01/Modelo_Conceitual_Referencia_v01.svg) e a [especificação estruturada](docs/modelo_conceitual_v01/Especificacao_Questoes_Modelo_Conceitual_v01.json) relacionam as perguntas à matriz existente e ao programa da disciplina. R10 formaliza a localização de elementos, preservando os nove identificadores anteriores; sua inclusão não representa nova verificação geométrica.

As [referências e seus localizadores](referencias/modelo_conceitual_v01/Fontes_e_Localizadores.txt) incluem Noy e McGuinness (2001), a especificação BOT e o OWL 2 Primer. Os PDFs de Noy e McGuinness e do OWL 2 Primer e a cópia do vocabulário BOT consultado estão disponíveis em [referências](referencias/modelo_conceitual_v01/). A consolidação é um modelo-alvo de avaliação; não acrescenta instâncias ou relações arquitetônicas confirmadas ao RDF.

### Adaptação parcial do IFC2SB para Python — revisão 04

O [Notebook 1, revisão 04](notebooks/01_Conversao_Arquitetura_IFC_LBD_v04.ipynb) acrescenta um [módulo geométrico executado em seis células](notebooks/01_Modulo_Geometrico_IFC2SB_Python_v01.ipynb). São adaptadas rotinas do [IFC2SB dos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), associado a [Fichter et al. (2021)](https://doi.org/10.26868/25222708.2021.30156), utilizando OpenCascade por meio de OCP. O [mapa de funções e diferenças](consultas/ifc2sb_python_v01/) distingue as rotinas portadas da extensão experimental de comparação ambiente–face. As células e saídas anteriores da revisão 03 são preservadas, sem nova execução da conversão nesta revisão.

No piloto da cozinha, as 457 paredes foram examinadas no pré-filtro e 34 permaneceram candidatas. Foram avaliadas 24 aberturas: seis com coincidência geométrica sem interpenetração detectada no critério, quatro com coincidência e interpenetração parede–ambiente, onze sem interseção de face no critério e três separadas por bbox. Dez aberturas distintas geraram onze recortes coincidentes; os quatro casos em conflito estão incluídos nesse total e permanecem sinalizados.

O [RDF e as consultas executadas](resultados/ifc2sb_python_v01/) registram a cadeia **ambiente → superfície bruta candidata → recorte de abertura → abertura → preenchimento**, com coordenadas XYZ, referencial do projeto, unidade metro, GUIDs e estados. Os 17 controles foram aprovados; nove confrontam os resultados Python com corpos C++ originais efetivamente compilados e executados. Isso não demonstra equivalência ao IFC2SB completo nem validação arquitetônica de todos os ambientes. O IFC original é preservado por SHA-256 e os conflitos não são corrigidos.

### Ensaio com implementação publicada: IFC2SB

**Conferência posterior do piloto:** o [Notebook 6](notebooks/06_Conferencia_Geometrica_Piloto_IFC2SB_v01.ipynb), com seis células executadas e quatro controles analíticos, distingue o volume global da parede da região de cada abertura e compara geometrias com e sem subtração dos vazios. Os quatro casos sinalizados anteriormente são janelas da mesma parede W06; a sobreposição dessa parede com a cozinha permanece após a subtração, mas o sinal global não demonstra quatro conflitos locais independentes.

Os 24 preenchimentos incluem cinco IfcDoor, oito IfcWindow e onze IfcWall. Nenhum foi aceito como um único sólido fechado pelo procedimento conservador para estimar sua fração dentro do ambiente; os valores ficam indisponíveis, com motivo registrado. O [relatório, a galeria dos 24 casos e as condições de aceitação](resultados/conferencia_ifc2sb_v01/) distinguem limites da entrada, do critério e da interpretação. Trata-se de conferência interna da mesma fonte, sem validação arquitetônica independente e sem alteração do IFC ou do RDF anterior.

O [Notebook 5](notebooks/05_IFC2SB_Controle_e_Creche_v01.ipynb) documenta a auditoria da execução do programa C++ [IFC2SB dos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), associado a [Fichter et al. (2021)](https://doi.org/10.26868/25222708.2021.30156). O [relatório, os logs e os ajustes de compilação](resultados/ifc2sb_controle_v01/) distinguem o funcionamento do motor da adequação das relações ao problema de pesquisa.

No controle FZK-Haus, foram produzidos quatro espaços interiores e 1.095 limites, mas os sete ambientes da entrada não foram conservados individualmente. Na creche integral, o limite operacional predefinido de 600 segundos foi atingido sem arquivo IFC de saída auditável. Esse resultado não demonstra impossibilidade do método. O IFC original foi preservado; a arquitetura completa e a integração entre disciplinas permanecem sem demonstração. O [PDF do artigo e o código dos autores](referencias/geometria_relacoes/) estão identificados nas referências.

### Experimento auxiliar com geometria em Python

A implementação geométrica Python da revisão 03 é uma adaptação específica deste estudo de critérios encontrados na literatura. **Não executa o GRC original de Lilis nem o IFC2SB.** Seus testes analíticos verificam operações e casos definidos, sem demonstrar completude arquitetônica ou equivalência à implementação publicada.

O [Notebook 1, revisão 03, executado](notebooks/01_Conversao_Arquitetura_IFC_LBD_v03.ipynb) acrescenta geometria XYZ ao RDF e investiga as relações entre os 41 ambientes e as paredes, distinguindo dados declarados, adjacências calculadas e casos não qualificados. A revisão se apoia em Huitzil et al. (2024), Lilis et al. (2025), Zhang et al. (2018), Wang et al. (2024) e Jäkel et al. (2025), com [fontes, PDFs e natureza das adaptações](referencias/notebook1_v03/).

Os [resultados e testes](resultados/notebook1_v03/) registram 2109 produtos com malha no RDF, 3 falhas de geometria e 12 testes geométricos analíticos aprovados. O IFC original permanece preservado. A revisão não demonstra completude arquitetônica nem resolve a integração com a estrutura; as limitações permanecem objeto de análise. O código de harmonização JSON de propriedades não foi aplicado.

## Procedimento metodológico

### Conferência da cozinha e rastreabilidade v02

O [Notebook 4](notebooks/04_Conferencia_Cozinha_IFC_RDF_v01.ipynb) confronta as cadeias do RDF com IfcRelVoidsElement/IfcRelFillsElement e examina sua localização na geometria do IFC. As 14 linhas da consulta coincidem com as relações das paredes selecionadas, mas duas aberturas estão separadas da cozinha. A conferência evidencia que preservar a cadeia parede–abertura–preenchimento não demonstra que cada preenchimento atenda ao ambiente.

O [relatório com figuras, consultas e limitações](resultados/conferencia_cozinha_v01/) e a [matriz v02](resultados/matriz_rastreabilidade_v02/) distinguem fidelidade da conversão, localização geométrica e significado arquitetônico. O IFC e o RDF de origem foram preservados; a completude arquitetônica e a integração entre disciplinas não são declaradas como concluídas.

### Inspeção de portas, aberturas e elementos hospedeiros

O [notebook 3](notebooks/03_Inspecao_Portas_IFC_RDF_CQ2_v01.ipynb) documenta a análise-piloto da CQ2 em 11 etapas executáveis, com finalidade, critérios e referências junto a cada consulta. A seleção utiliza a classe `IfcDoor`, percorre `IfcRelFillsElement` e `IfcRelVoidsElement` e confere os pares hospedeiro-porta no RDF por `GlobalId`.

Foram identificadas 53 portas: 45 com hospedeiro `IfcWall` e oito com hospedeiro `IfcFurniture`, descrito no IFC como divisória de granito. Os 53 pares têm aresta direta `bot:hasSubElement` no RDF. O resultado 45/53 corresponde à cobertura do filtro `IfcWall`; a exclusão dos oito casos não demonstra perda na conversão. A associação dos elementos aos ambientes permanece sem demonstração neste teste.

Os [resultados, as entradas e o relatório detalhado](resultados/notebook3/) permitem reproduzir a inspeção. As rotinas são adaptações específicas deste estudo das APIs do IfcOpenShell e RDFLib e das relações definidas pela buildingSMART e pela BOT, conforme as [fontes técnicas](referencias/Referencias_Notebook3_CQ2.txt). O código das bibliotecas está disponível nos repositórios [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) e [RDFLib](https://github.com/RDFLib/rdflib).

### Incremento exploratório: arquitetura e estrutura

O [notebook 2](notebooks/02_integracao_arquitetura_estrutura.ipynb) amplia a inspeção para os elementos do modelo arquitetônico e para o arquivo estrutural **SMT**, da mesma revisão do FNDE. A etapa repete as conversões e verificações em blocos separados e registra as dificuldades de estabelecer correspondências entre os modelos. O [IFC estrutural selecionado](dados/fnde/estrutura/) e os [resultados do diagnóstico](resultados/notebook2/) documentam o recorte. A integração semântica permanece pendente; esta versão não aplica soluções aos problemas novos encontrados.

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

### Correção textual e comparação entre execuções

A [célula 8](consultas/08_correcao_textual_conversor.py) documenta duas intervenções locais no código do IFCtoLBD 2.49.0: a decodificação dos caracteres Unicode isolados e a preservação de apóstrofos internos nos textos. A interpretação dos caracteres se fundamenta na orientação [IFC String Encoding, da buildingSMART](https://technical.buildingsmart.org/resources/ifcimplementationguidance/string-encoding/), e sua representação em Java na [seção 3.3 da especificação Java SE 21, da Oracle](https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.3). O tratamento dos apóstrofos decorre da análise das funções `IfcSpfParser` e `RDFWriter.filterExtras` do código-fonte dos autores. As funções, o commit e as alterações estão identificados na célula. A implementação específica constitui uma adaptação deste estudo; as fontes técnicas fundamentam as decisões, mas não publicam essa mesma correção.

Somente as duas classes de tratamento textual são recompiladas. A intervenção é examinada com dez testes independentes e com a verificação das interfaces públicas antes da nova conversão. O mesmo IFC e os mesmos parâmetros de conversão são utilizados, com geração de uma saída separada. A [célula 9](consultas/09_comparacao_apos_correcao.py) compara as duas execuções com o IFC por igualdade textual exata e repete a verificação dos pavimentos e das regras SHACL. Os resultados originais são preservados; a avaliação não utiliza substituição de palavras nem preenchimento dos valores esperados no grafo. As fontes técnicas estão em [referências](referencias/#codificação-de-caracteres-e-intervenção-local).

Na execução avaliada, as divergências em `LongName` e `Category` passaram de 13 para zero em cada campo, com os 41 identificadores e vínculos com pavimentos preservados. A [comparação consolidada e os registros da intervenção](resultados/#efeito-da-correção-de-leitura-textual) delimitam o resultado aos campos e às regras examinados.

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

## Referências metodológicas

KIAVARZ, Hamid; JADIDI, Mojgan; RAJABIFARD, Abbas; SOHN, Gunho. An Automated Space-Based Graph Generation Framework for Building Energy Consumption Estimation. **Buildings**, v. 13, n. 2, 350, 2023. DOI: [10.3390/buildings13020350](https://doi.org/10.3390/buildings13020350).

**Contribuição nesta etapa:** adaptação dos procedimentos de faces, raios, projeção e interseção dos §§4.2.2–4.4 e Tabelas 4–5. O pseudocódigo publicado não é apresentado como programa executável completo. As alterações de API e de critérios estão registradas. [PDF e fontes](referencias/interfaces_hibridas_v01/) · [Página dos autores](https://www.ausmlab.com/publications/an-automated-space-based-graph-generation-framewor) · [Biblioteca Shapely usada no artigo e nesta adaptação](https://github.com/shapely/shapely).

LILIS, Georgios Nektarios et al. Automated generation of building energy model geometry from BIM-derived space and opening volumes. **Automation in Construction**, v. 185, 106840, 2026. DOI: [10.1016/j.autcon.2026.106840](https://doi.org/10.1016/j.autcon.2026.106840).

**Contribuição atual (revisão 07):** além da triagem anterior do §6, foram adaptados e executados parcialmente os operadores IP/IPS, PSS, pares entre espaços e maxA/recortes de abertura (Alg. 1–3 e 5). Os 20 controles passaram; o piloto manteve dez aberturas associadas, com 12 recortes candidatos, dos quais 11 têm apoio no volume 3D. O recorte adicional de 0,062 m² permanece candidato. Alpha wrap/Alg. 4 e o método completo não foram implementados. A contribuição observada é geométrica e comparativa, sem ganho de acurácia arquitetônica demonstrado. [Notebook 9 executado](notebooks/09_Lilis_Hibrido_Cozinha_v01.ipynb) · [Notebook 1 v07](notebooks/01_Conversao_Arquitetura_IFC_LBD_v07.ipynb) · [Resultados](resultados/lilis_hibrido_v01/) · [PDF, fontes e adaptações](referencias/lilis_hibrido_v01/).

BONDUEL, Mathias; ORASKARI, Jyrki; PAUWELS, Pieter; VERGAUWEN, Maarten; KLEIN, Ralf. The IFC to Linked Building Data Converter: Current Status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018, Londres. **Proceedings [...]**. CEUR Workshop Proceedings, v. 2159, 2018. p. 34–43. Disponível em: <https://ceur-ws.org/Vol-2159/04paper.pdf>. Acesso em: 27 out. 2026.

**Contribuição no estudo:** fundamentação da transformação IFC-LBD e reutilização do conversor dos autores. [PDF](referencias/Bonduel_et_al_2018_IFCtoLBD.pdf) · [Código dos autores](https://github.com/jyrkioraskari/IFCtoLBD).

JÄKEL, Jan-Iwo; HEINLEIN, Eva; VON CZERNITZKY, Constantin; MACKENBACH, Sven; KLEMT-ALBERT, Katharina. Ontology for a Knowledge-Based Deconstruction of Buildings Based on BIM Models and Linked Data Principles. **Buildings**, v. 15, n. 5, 720, 2025. DOI: [10.3390/buildings15050720](https://doi.org/10.3390/buildings15050720). Acesso em: 27 out. 2026.

**Contribuição no estudo:** referência para a estratégia de consultas SPARQL e validação SHACL adaptada nas células 6 e 7. Os exemplos originais constam da seção 5.2 e das tabelas 3 a 5. [PDF](referencias/Jaekel_et_al_2025_DCO.pdf) · [Ontologia dos autores](https://github.com/janiwojaekel/dcoOntology).

ORASKARI, Jyrki; KIRNER, Lukas; ZÖCKLEIN, Marit; BRELL-COKCAN, Sigrid. A Method to Unify Custom Properties in IFC to Linked Building Data Conversion. In: **LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP**, 2024. Disponível em: <https://linkedbuildingdata.net/ldac2024/files/papers/LDAC2024_Camera_20.pdf>. Acesso em: 27 out. 2026.

**Contribuição no estudo:** referência para a discussão da correspondência e harmonização de propriedades IFC-LBD. O mapeamento JSON apresentado pelos autores não foi aplicado ao grafo desta etapa. [PDF](referencias/Oraskari_et_al_2024_Propriedades_IFC_LBD.pdf) · [Exemplo de código dos autores: Example13.java](https://github.com/jyrkioraskari/IFCtoLBD/blob/master/IFCtoLBD/src/main/java/examples/Example13.java).
