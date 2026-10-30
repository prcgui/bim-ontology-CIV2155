# Organização e exploração da integração

O [Notebook 3](../notebooks/03_Organizacao_e_Exploracao.ipynb) acrescenta organização semântica, propriedades contextualizadas, oito consultas SPARQL, um contrato SHACL e um [explorador integrado](https://prcgui.github.io/bim-ontology-CIV2155/). Utiliza o resultado validado do Notebook 2, sem repetir a geometria. O [explorador original do N1](https://prcgui.github.io/bim-ontology-CIV2155/arquitetura-n1.html) foi preservado integralmente.

## Do esquema ao elemento

A representação separa três planos: os esquemas de classes e propriedades; os produtos identificados nos modelos; os registros que documentam modelos, resultados, propriedades e relações. A classe IFC do catálogo, como `IfcBeam`, é um metadado extraído do arquivo e aparece separada dos tipos RDF realmente declarados. Uma classe não é um produto físico. Um registro sobre uma relação também não é um novo produto.

Os grafos ARQ, SMT, SCO, relações e proveniência continuam semanticamente idênticos aos do N2. Acrescentam-se quatro grafos:

| Grafo | Conteúdo efetivamente acrescentado | Triplas |
|---|---|---:|
| `perfil` | Perfil próprio para registros informacionais, subordinado a `prov:Entity` | 56 |
| `bot-referencia` | Esquema BOT 0.3.2, com versão, autoria e licença preservadas | 957 |
| `propriedades-contextuais` | POC de propriedades diretamente associadas à V137 | 406 |
| `execucao-n3` | Atividade computacional, datas, entrada e hash do código | 9 |

O Dataset organizado possui **416.603 quádruplas em nove grafos**, mantendo os **26.601 produtos**, as **1.652 relações N2** e os **101 pares N1**. O esquema de referência não é apresentado como uma hierarquia que já existisse nos dados do N2. Não foram executados alinhamento de identidades, inferência `owl:sameAs`, gUFO/gOCED ou raciocínio OWL global.

## Propriedades com seu contexto de origem

Na V137, o RDF direto da extração L1 reúne quatro valores sob `props:quantidade_property_simple`. O IFC os distribui em conjuntos próprios, junto das respectivas descrições. A extensão registra **9 Psets e 34 propriedades simples**, mantendo seus nomes, GUIDs dos conjuntos, números STEP, tipos nominais IFC, valores e unidades nativas. O produto físico conserva a mesma URI.

| Propriedade original | Contexto de origem | Tipo IFC | Valor e unidade nativa |
|---|---|---|---:|
| Quantidade_01 | AltoQi_Eberick-Item_01, concreto | IfcVolumeMeasure | 0,140544 m³ |
| Quantidade_02 | AltoQi_Eberick-Item_02, forma | IfcAreaMeasure | 1,87392 m² |
| Quantidade_03 | AltoQi_Eberick-Item_03, aço CA50 | IfcMassMeasure | 4,26151 kg |
| Quantidade_04 | AltoQi_Eberick-Item_04, aço CA60 | IfcMassMeasure | 2,04999 kg |

O IFC SCO declara centímetro para comprimento, mas metro quadrado, metro cúbico e quilograma para as outras medidas da tabela. A rotina consulta a unidade correspondente ao tipo nominal. Não calcula cm² ou cm³ a partir do comprimento. Unidade explícita da propriedade prevalece sobre a unidade do projeto. Valores `IfcReal` sem unidade declarada permanecem sem dimensão atribuída.

Essa extensão é própria, inspirada nos recursos de propriedades discutidos por Bonduel et al. (2018). Não constitui conversão L2 integral, unificação de nomes nem harmonização global. O recorte cobre somente V137, Psets diretamente associados e `IfcPropertySingleValue`; herança de tipos e outros tipos de propriedades não foram generalizados.

## Perguntas e validação

As [oito consultas publicadas](../codigo/consultas_exploracao/) respondem a necessidades do estudo: localizar produtos e fontes; relacionar ambientes às estruturas; examinar a evidência cozinha–V137; identificar os três ambientes inconclusivos; recuperar propriedades com contexto; verificar GUID repetido no mesmo modelo; mostrar armaduras fora da avaliação geométrica; inspecionar hierarquias dos esquemas. O notebook executa as consultas; a aplicação apresenta suas respostas salvas e permite baixá-las.

O [contrato SHACL](../codigo/Restricoes_Organizacao.ttl) foi executado sem inferência em uma projeção de **200.962 triplas**. Ela inclui os campos exigidos de todos os produtos, três modelos, 1.652 registros espaciais, 41 resultados por ambiente e a POC. A projeção e seus alvos são construídos explicitamente pelo código. A validação verificou identidade, proveniência, extremos das relações, tipos de medidas, estados e contexto das propriedades, obtendo conformidade. `ctx:ProdutoIndexado` é somente um alvo local dessa projeção, não uma classificação física adicionada à fonte.

Conformidade nesse contrato não demonstra qualidade estrutural, alinhamento, completude IFC nem consistência OWL global. Os ensaios com defeitos introduzidos em cópias e os registros de execução permanecem no arquivo técnico do Drive. Propriedades multivaloradas da fonte não são genericamente proibidas.

## Explorar e verificar

O explorador oferece visão geral, filtros por origem, classe IFC, tipo RDF e estado da análise; passagem dos tipos aos indivíduos; propriedades tipadas; vizinhança com expansão seletiva; evidências e medidas; histórico de navegação; exportação de um recorte RDF em N-Quads e, por uma ação separada, do estado dos filtros em JSON. As cores identificam fontes, acompanhadas de rótulos textuais.

O índice contém **394.067 quádruplas diretas de produtos e registros selecionados**, mais informações de esquema. Cada quádrupla foi conferida contra o Dataset. Não é uma cópia integral: recursos auxiliares e representações geométricas extensas permanecem no arquivo completo. O recorte exportado inclui o contexto do foco descrito na interface, independentemente dos filtros de exibição. A página não executa um servidor SPARQL ou inferência no navegador.

O N1 já possuía visualização organizada. O avanço demonstrado nesta etapa é a exploração conjunta das fontes, a distinção de níveis e a verificação de contexto, consulta e contrato. Não foi realizado estudo de usabilidade com participantes, nem foi medido ganho de acurácia geométrica.

## Limitações preservadas

Infantil 1, Infantil 5 e Amamentação continuam inconclusivos, sem contagem artificial. Os placements declarados foram aplicados, mas não houve validação independente do alinhamento ou do georreferenciamento. Contato e interseção não comprovam apoio, função ou adequação estrutural. As 17.755 armaduras SCO, montagens e vazios SMT permanecem fora da avaliação geométrica individual indicada no N2. Fonte IFC, disciplina e sistema construtivo não são tratados como conceitos equivalentes. A POC não resolve conflitos globais de propriedades ou identidade entre modelos.

As [referências aplicadas](../referencias/organizacao/README.md) identificam a contribuição original e a adaptação. O inventário interdisciplinar completo, as alternativas avaliadas e as auditorias ficam no [Google Drive do projeto](https://drive.google.com/drive/u/0/folders/1kVGXvERWXieeMeURrJF07tuLaADdrJ_O).
