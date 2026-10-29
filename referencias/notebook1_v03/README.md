# Referências da revisão 03 do Notebook 1

As contribuições aplicadas, os métodos não incorporados e as limitações estão discriminados na [matriz de fontes](matriz_fontes_implementacao.csv). Os caminhos da coluna `pdf` referem-se ao acervo local organizado; esta pasta reúne os quatro PDFs adicionais diretamente relacionados às mudanças da revisão 03.

- Huitzil et al. (2024). *Semantic Building Information Modeling: An empirical evaluation of existing tools*. [DOI](https://doi.org/10.1016/j.jii.2024.100731). Avaliação da preservação e da geometria. O benchmark dos autores não foi reproduzido.
- Lilis et al. (2025). *BIM-based semantic enrichment and knowledge graph generation via geometric relation checking*. [DOI](https://doi.org/10.1016/j.autcon.2025.106081). §§3.2–3.4, Figura 4: critérios de adjacência adaptados em Python. O código GRC C++ dos autores não foi executado. [Registro Zenodo citado no artigo](https://doi.org/10.5281/zenodo.14039972); seu conteúdo não foi confirmado devido a restrição de acesso HTTP 403.
- Wang, Zhang e Yan (2024). *Enhancement and validation of ifcOWL ontology based on Shapes Constraint Language (SHACL)*. [DOI](https://doi.org/10.1016/j.autcon.2024.105293). Estratégia de validação; shapes próprios do presente ensaio, sem reprodução das regras WHERE/EXPRESS.
- Zhu et al. (2024). *BG-LoA: A Benchmarking Framework for BIM-GIS Data Integration Based on Meta-Modelling Theory*. [DOI](https://doi.org/10.5194/isprs-archives-XLVIII-4-2024-591-2024). Delimitação dos níveis de representação; benchmark não executado.

Fontes já utilizadas e código disponível dos autores:

- Bonduel et al. (2018). [Artigo](https://ceur-ws.org/Vol-2159/04paper.pdf); [IFCtoLBD](https://github.com/jyrkioraskari/IFCtoLBD). Motor executado: versão 2.49.0, com adaptação textual documentada.
- Zhang, Beetz e De Vries (2018). [BimSPARQL, DOI](https://doi.org/10.3233/SW-180297); [GeometryConverter.java em commit fixo](https://github.com/BenzclyZhang/BimSPARQL/blob/dd7872ac7aab85e98e2d0177d80c878abb88a71e/src/main/java/nl/tue/ddss/bimsparql/geometry/convert/GeometryConverter.java). Padrão GEOM/TIN Z adaptado; a classe Java não foi executada.
- Jäkel et al. (2025). [Artigo](https://doi.org/10.3390/buildings15050720); [ontologia DCO dos autores](https://github.com/janiwojaekel/dcoOntology). Estratégia de validação; regras de desconstrução não transferidas automaticamente.

Bibliotecas técnicas: [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell), [RDFLib](https://github.com/RDFLib/rdflib), [Shapely](https://github.com/shapely/shapely), [Manifold](https://github.com/elalish/manifold) e [pySHACL](https://github.com/RDFLib/pySHACL). A interseção de sólidos utiliza Manifold/Mesh64 e difere do BSP utilizado por Lilis et al.
