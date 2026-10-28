# 7. Validação explícita dos ambientes com SHACL
#
# REFERÊNCIA CIENTÍFICA
# JÄKEL, J.-I. et al. Buildings, v. 15, n. 5, 720, 2025.
# https://doi.org/10.3390/buildings15050720
# Seção 5.2.2 e tabelas 3 a 5 (PDF, p. 18): exemplos de regras SHACL.
# PDF: referencias/Jaekel_et_al_2025_DCO.pdf (também no Drive).
# Ontologia dos autores: https://github.com/janiwojaekel/dcoOntology
# As regras originais estão no artigo; esse repositório publica a ontologia.
# Código desta adaptação:
# https://github.com/prcgui/bim-ontology-CIV2155/blob/main/consultas/07_validacao_shacl.py
#
# ADAPTAÇÃO E FONTES TÉCNICAS
# Regras elaboradas para este estudo com assistência de inteligência artificial,
# adaptando a estrutura sh:NodeShape/sh:property ao recorte da creche.
# Examinam presença, multiplicidade e tipos; a igualdade IFC-LBD está nas células 5 e 6.
# Estas regras não são as verificações de desconstrução do artigo.
# SHACL: https://www.w3.org/TR/shacl/ (minCount, maxCount, inversePath e class).
# Motor utilizado: pySHACL 0.30.1. Exemplo oficial de validate():
# https://github.com/RDFLib/pySHACL#python-module-use
# Acesso às fontes: 27 out. 2026.

import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "-q", "install",
                       "pyshacl==0.30.1", "rdflib==7.1.4"])
from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import SH

regras_ambientes = Graph().parse(data="""
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix bot: <https://w3id.org/bot#> .
@prefix props: <http://lbd.arch.rwth-aachen.de/props#> .
@prefix estudo: <https://github.com/prcgui/bim-ontology-CIV2155/regras/> .

estudo:AmbienteShape a sh:NodeShape ;
  sh:targetClass bot:Space ;
  sh:property [ sh:path props:globalIdIfcRoot_attribute_simple ;
                sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ] ;
  sh:property [ sh:path rdfs:label ;
                sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ] ;
  sh:property [ sh:path [ sh:inversePath bot:hasSpace ] ;
                sh:minCount 1 ; sh:maxCount 1 ; sh:class bot:Storey ] .

estudo:CategoriaShape a sh:NodeShape ;
  sh:property [ sh:path props:category_property_simple ;
                sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ] .
""", format="turtle")
ESTUDO = Namespace("https://github.com/prcgui/bim-ontology-CIV2155/regras/")
# A categoria é exigida somente para ambientes correspondentes cujo IFC a informa.
for ambiente in ambientes_ifc:
    recurso = recursos_por_guid.get(ambiente.GlobalId)
    if recurso is not None and elemento_ifc.get_pset(
        ambiente, "Pset_SpaceCommon", "Category", should_inherit=False
    ) is not None:
        regras_ambientes.add((ESTUDO.CategoriaShape, SH.targetNode, recurso))

conforme_shacl, relatorio_shacl, texto_shacl = validate(
    data_graph=grafo_lbd, shacl_graph=regras_ambientes,
    inference="none", meta_shacl=True, inplace=False,
)
regras_ambientes.serialize(pasta_resultados / "regras_ambientes.ttl", format="turtle")
relatorio_shacl.serialize(pasta_resultados / "relatorio_shacl.ttl", format="turtle")
(pasta_resultados / "relatorio_shacl.txt").write_text(texto_shacl, encoding="utf-8")
print("Conformidade com as regras estruturais:", conforme_shacl)
print("Ambientes IFC com recurso correspondente:", len(guids_ifc & guids_lbd), "/", len(ambientes_ifc))
print("Ausências de ambientes são registradas na comparação da célula 5.")
print("Conformidade SHACL não comprova igualdade textual nem preservação integral do IFC.")
print(texto_shacl)
