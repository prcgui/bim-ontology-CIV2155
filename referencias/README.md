# Referências e atribuições

As fontes abaixo fundamentam as operações indicadas. As adaptações e as decisões da implementação são descritas nas células dos notebooks.

| Fonte primária | Aplicação no estudo |
|---|---|
| [Bonduel et al. (2018), The IFC to Linked Building Data Converter](https://ceur-ws.org/Vol-2159/04paper.pdf) · [IFCtoLBD 2.49.0](https://github.com/jyrkioraskari/IFCtoLBD/releases/tag/2.49.0) | Conversão IFC–LBD, entidades e identidades dos modelos. As duas correções textuais utilizadas estão documentadas no N1. |
| [Fichter et al. (2021), IFC2SB](https://doi.org/10.26868/25222708.2021.30156) · [código de origem](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad) | Adaptação parcial de procedimentos de faces e preparo geométrico em Python/OCP. |
| [Kiavarz et al. (2023)](https://doi.org/10.3390/buildings13020350) | Adaptação de orientação, projeção e interseção de faces e busca local de interfaces. |
| [Ying e Lee (2021)](https://doi.org/10.1016/j.autcon.2021.103659) | Representações geométricas e preparação planar controlada. |
| [Lilis et al. (2025), BIM-based semantic enrichment and knowledge graph generation via geometric relation checking](https://doi.org/10.1016/j.autcon.2025.106081) | Fluxo de seleção de candidatos e checagem de relações espaciais; implementação local em OCP. |
| [Rasmussen et al. (2021), BOT](https://doi.org/10.3233/SW-200385) · [especificação BOT](https://w3c-lbd-cg.github.io/bot/) | Tipos e predicados topológicos reutilizados nos grafos. |
| [Noy e McGuinness (2001), Ontology Development 101](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf) | Delimitação do escopo, perguntas e reutilização de termos no N3. |
| [Zhang, Beetz e De Vries (2018), BimSPARQL](https://doi.org/10.3233/SW-180297) | Vocabulário GEOM para a representação geométrica. |
| [Bronsart et al. (2013)](https://doi.org/10.11648/j.ijmea.20130101.11) · [Barequet et al. (1998), RSVP](https://doi.org/10.1109/2945.694983) | Fundamentação complementar do preparo e do controle de alterações geométricas. |
| [FNDE — Projeto Tipo 2](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2) | Modelos originais do estudo de caso. |

As especificações [RDF 1.1](https://www.w3.org/TR/rdf11-concepts/), [N-Quads](https://www.w3.org/TR/n-quads/), [PROV-O](https://www.w3.org/TR/prov-o/) e [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/) fundamentam a representação, os grafos nomeados, a proveniência e as consultas. As adaptações geométricas não reproduzem integralmente os programas publicados; os limiares adotados são parâmetros do estudo.

## Software e licenças

A implementação utiliza [IfcOpenShell](https://docs.ifcopenshell.org/), [Open CASCADE](https://dev.opencascade.org/doc/overview/html/occt_user_guides__shape_healing.html), [Shapely](https://shapely.readthedocs.io/) e [RDFLib](https://rdflib.readthedocs.io/). As consultas externas utilizam o [GraphDB](https://graphdb.ontotext.com/documentation/11.5/).

O código do repositório é acompanhado pela [GNU GPL versão 3](../LICENSE). As adaptações parciais de `Kernel_pre.cpp`, `Kernel_occ.cpp` e `cFace.cpp`, do IFC2SB, preservam o crédito **Copyright 2022 Eric Fichter, GPL-3.0-or-later**, os cabeçalhos nos notebooks e a [licença integral de origem](../codigo/COPYING). Os componentes externos e os artigos conservam suas licenças de origem.
