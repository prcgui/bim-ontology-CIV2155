# Código utilizado

O ponto de entrada é o [Notebook 1](../notebooks/01_Arquitetura_IFC_RDF.ipynb). Seus módulos foram consolidados a partir da rotina já executada no estudo. A seleção de associações e seus parâmetros foram preservados; a exportação foi reduzida aos resultados primários e à base semântica.

| Arquivo | Função no procedimento |
|---|---|
| `converter_ifc.py` | Repete a conversão IFCtoLBD 2.49.0 com as duas correções textuais efetivamente usadas. A execução padrão usa o RDF já convertido. |
| `preparar_geometria.py` | Lê o IFC, prepara espaços e recortes de 457 paredes, preserva relações declaradas e produz dados intermediários. |
| `recuperar_geometria.py` | Exige sólido fechado e válido; tenta ShapeFix e costura controlada nos casos que falham no caminho estrito. |
| `ifc2sb_faces.py` | Adaptação parcial do IFC2SB para faces, recortes de abertura e ancestralidade. |
| `faces_kiavarz.py` | Projeta e intersecta faces, preserva anéis, aplica orientação, raios e sondas locais. |
| `rotina_multiambientes.py` | Repete o mesmo critério para cada IfcSpace e registra associações e inconclusões. |
| `publicar_resultados.py` | Seleciona as tabelas de apresentação, liga resultados às identidades IFC/RDF e entrega o grafo consolidado. |
| `Vocabulario.ttl` | Define as classes e propriedades usadas nos resultados geométricos. |
| `01_ambientes.rq`, `02_esquadrias.rq` | Consultas SPARQL executadas sobre o grafo entregue. |
| `apresentar.py` | Produz a figura de cobertura mostrada no notebook e no repositório. |
| `visualizar_rdf.py` | Lê o grafo entregue e desenha os recortes RDF em caixas: organização espacial, identidade da cozinha e associação com PA2. |

**IFC2SB:** fonte RWTH-E3D/IFC2SB, commit `96a89cdff65f13279c0c3ce67e729ad9f9f5adad`. Foram adaptadas rotinas de `Kernel_pre.cpp`, `Kernel_occ.cpp` e `cFace.cpp`, conforme cabeçalho do módulo. Copyright de Eric Fichter e licença GPL-3.0-or-later preservados em [COPYING](COPYING). A adaptação utiliza OCP em Python e não executa integralmente o programa dos autores, o outer hull ou sua reconstrução completa de limites.

**Kiavarz:** adaptação metodológica do pseudocódigo, com base ortonormal 3D→2D, interseção de polígonos com anéis, tolerância entre planos e sondas no sólido. O IFC não fornece os limites `BoundedBy` exigidos pelo fluxo literal do artigo. A rotina não deve ser apresentada como reprodução integral.

**IFCtoLBD:** o motor é obtido da distribuição oficial 2.49.0, verificada por hash. Duas classes de fontes fixadas recebem as alterações usadas para preservar Unicode e apóstrofos nos textos STEP. Compilam-se as classes modificadas e elas precedem os JARs originais no caminho de execução. As bibliotecas e fontes externas mantêm suas licenças.

Os arquivos intermediários da execução ficam em `.execucao/`, fora do conteúdo versionado. Os dados publicados estão em `resultados/`; as trilhas de auditoria e os ensaios ficam no Drive indicado no README principal.

## Rotina usada no Notebook 2

| Arquivo | Função |
|---|---|
| `integrar_modelos.py` | Repete a extração comum nos três IFCs, confere identidades e nomes, reúne os grafos com proveniência, serializa em N-Quads e executa as consultas. |
| `relacoes_interdisciplinares.py` | Reutiliza o preparo conservador do N1 e verifica contenção, interseção e superfície comum nos pares espaço–estrutura. |
| `apresentar_integracao.py` | Produz o gráfico de contagens e o exemplo RDF da cozinha, conferido no Dataset. |
| `Vocabulario_Integracao.ttl` | Registros qualificados dos vínculos, unidades, identidade dos modelos e proveniência. |
| `03_modelos_integrados.rq`, `04_relacoes_estrutura_ambientes.rq` | Consultas executadas sobre os grafos nomeados. |

`converter_ifc.py` aceita hash de origem, namespace e limite de memória como parâmetros. Os padrões do N1 foram preservados. Para a extensão maiúscula do SCO, usa uma cópia de trabalho byte a byte com extensão `.ifc`, compatível com a CLI do motor. [Fontes e limites das adaptações](../referencias/integracao/README.md).


## Organização e exploração no Notebook 3

`organizar_dataset.py` carrega o resultado validado do N2, preserva suas identidades e grafos, recupera Psets diretamente associados à V137, executa o contrato SHACL e oito consultas e gera o índice e o Dataset organizado. `Perfil_Organizacao.ttl` contém o perfil próprio; `Restricoes_Organizacao.ttl` declara o contrato. Os oito arquivos em `consultas_exploracao/` são as perguntas efetivamente executadas. As dependências adicionais estão em `requirements-exploracao.txt`.

A [explicação metodológica](../docs/Organizacao_e_Exploracao.md) distingue o perfil dos dados originais, a POC da harmonização global e a conformidade SHACL de certificação do projeto. O [código do explorador](../visualizacao/explorador-integrado.html) usa o índice produzido pelo notebook. Ensaios e auditorias permanecem no Drive.
