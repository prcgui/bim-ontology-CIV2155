# Geometria e relações espaciais

**Situação dos ensaios:** os testes históricos IFC2SB da revisão 02 não comprovaram uma delimitação válida da cozinha. A [revisão 03 executada](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v03.ipynb) reutiliza o padrão geométrico BimSPARQL e investiga contatos das malhas originais; não executa o IFC2SB nem apresenta a geração de limites espaciais como etapa concluída.

Fontes para a revisão espacial do Notebook 1. A disponibilidade de um código não comprova sua execução ou a adequação dos resultados ao modelo da creche. O registro da execução deve identificar a versão, as opções, as adaptações e os resultados obtidos.

| Fonte | Artigo | Código dos autores | Papel no procedimento |
|---|---|---|---|
| Fichter et al. (2021) | [PDF](Fichter_et_al_2021_Geracao_Limites_Espaciais.pdf) · [DOI](https://doi.org/10.26868/25222708.2021.30156) | [IFC2SB](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad) | Geração de limites espaciais. O ensaio utiliza a opção de primeiro nível; o artigo também trata do segundo nível. |
| Zhang, Beetz e De Vries (2018) | [Manuscrito aceito](Zhang_et_al_2018_BimSPARQL_Manuscrito_Aceito.pdf) · [DOI](https://doi.org/10.3233/SW-180297) | [BimSPARQL: GeometryConverter.java](https://github.com/BenzclyZhang/BimSPARQL/blob/dd7872ac7aab85e98e2d0177d80c878abb88a71e/src/main/java/nl/tue/ddss/bimsparql/geometry/convert/GeometryConverter.java) | Padrão produto–geometria–TIN e agrupamento dos índices em triângulos, adaptados à API Python. A classe Java original não é executada. |
| Krijnen et al. (2020) | [PDF](Krijnen_et_al_2020_Validacao_Inferencia_Geometrica.pdf) · [DOI](https://doi.org/10.46421/2706-6568.37.2020.paper008) | [IfcOpenShell, ramo dos autores](https://github.com/tudelft3d/IfcOpenShell/tree/2adb098cdb0a3f072af4fcead29c2a427e6498e5) | Discussão da validação geométrica. O algoritmo CGAL/Nef/Minkowski não foi executado nesta revisão. |

As versões consultadas dos códigos estão preservadas no [pacote de fontes](Codigos_Publicados_Geometria_Relacoes_v01.zip), com identificação dos commits. O [registro das fontes](Registro_das_Fontes_v01.json) conserva os hashes dos materiais inicialmente consultados.

O [registro complementar de integridade](Registro_das_Fontes_v02.json) inclui as licenças e o [vocabulário geom.ttl dos autores do BimSPARQL](https://github.com/BenzclyZhang/BimSPARQL/blob/dd7872ac7aab85e98e2d0177d80c878abb88a71e/Vocabularies/geom.ttl), utilizado na escolha dos termos `geom:Geometry`, `geom:hasGeometry` e `geom:asBody`.

FICHTER, Eric; RICHTER, Veronika; FRISCH, Jérôme; VAN TREECK, Christoph. **Automatic generation of second level space boundary geometry from IFC models**. In: Building Simulation 2021. p. 1083–1090, 2021. DOI: [10.26868/25222708.2021.30156](https://doi.org/10.26868/25222708.2021.30156).

ZHANG, Chi; BEETZ, Jakob; DE VRIES, Bauke. **BimSPARQL: Domain-specific functional SPARQL extensions for querying RDF building data**. *Semantic Web*, v. 9, n. 6, p. 829–855, 2018. DOI: [10.3233/SW-180297](https://doi.org/10.3233/SW-180297).

KRIJNEN, Thomas; NOARDO, Francesca; OHORI, Ken Arroyo; LEDOUX, Hugo; STOTER, Jantien. **Validation and Inference of Geometrical Relationships in IFC**. In: CIB W78 2020. p. 98–111, 2020. DOI: [10.46421/2706-6568.37.2020.paper008](https://doi.org/10.46421/2706-6568.37.2020.paper008).

O ajuste de compatibilidade do IfcOpenShell antigo com OCCT 7.6 utiliza a API oficial: [Poly_Triangulation](https://dev.opencascade.org/doc/refman/html/class_poly___triangulation.html), [BRepAdaptor_CompCurve em OCCT 7.6](https://github.com/Open-Cascade-SAS/OCCT/blob/V7_6_0/src/BRepAdaptor/BRepAdaptor_CompCurve.hxx) e [Approx_Curve3d](https://github.com/Open-Cascade-SAS/OCCT/blob/V7_6_0/src/Approx/Approx_Curve3d.hxx). Os diffs devem acompanhar o registro da compilação.

Documentação técnica complementar: [IfcOpenShell: geometria](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html), [RDFLib: SPARQL](https://rdflib.readthedocs.io/en/latest/intro_to_sparql/) e [BOT](https://w3c-lbd-cg.github.io/bot/). A ligação de URIs, a proveniência, as consultas e os testes constituem adaptações específicas do estudo.
