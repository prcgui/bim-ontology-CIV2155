"""Regras e consultas elaboradas para CIV2155, não copiadas de autores.
Estratégia apoiada em Wang et al.2024 (10.1016/j.autcon.2024.105293),
Jäkel et al.2025 (10.3390/buildings15050720) e Huitzil et al.2024
(10.1016/j.jii.2024.100731). Shapes são específicos de BOT/GEOM/CIV;
não executam a conversão das regras EXPRESS proposta por Wang et al.
"""
from pathlib import Path
import json,csv
from rdflib import Graph,Namespace,RDF,Literal
from pyshacl import validate
from pipeline_arquitetura import CIV,BOT,GEOM,PROPS,save_json,save_csv

PREFIX='''PREFIX bot: <https://w3id.org/bot#>
PREFIX geom: <http://bimsparql.org/geometry#>
PREFIX civ: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/arquitetura#>
PREFIX props: <http://lbd.arch.rwth-aachen.de/props#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
'''
SHAPES=PREFIX+'''
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix civ: <https://github.com/prcgui/bim-ontology-CIV2155/vocab/arquitetura#> .
@prefix geom: <http://bimsparql.org/geometry#> .
@prefix bot: <https://w3id.org/bot#> .
@prefix props: <http://lbd.arch.rwth-aachen.de/props#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
civ:SpaceShape a sh:NodeShape; sh:targetClass bot:Space;
 sh:property [sh:path props:globalIdIfcRoot_attribute_simple;sh:minCount 1;sh:maxCount 1];
 sh:property [sh:path geom:hasGeometry;sh:minCount 1;sh:maxCount 1;sh:class geom:Geometry] .
civ:GeometryShape a sh:NodeShape;sh:targetClass geom:Geometry;
 sh:property [sh:path geom:asBody;sh:minCount 1;sh:maxCount 1;sh:datatype xsd:string;sh:pattern "^TIN Z "];
 sh:property [sh:path civ:unit;sh:hasValue <http://qudt.org/vocab/unit/M>;sh:maxCount 1];
 sh:property [sh:path civ:coordinateReference;sh:minCount 1;sh:maxCount 1];
 sh:property [sh:path civ:triangleCount;sh:minCount 1;sh:minExclusive 0] .
civ:EvidenceShape a sh:NodeShape;sh:targetClass civ:GeometricRelationEvidence;
 sh:property [sh:path rdf:subject;sh:minCount 1;sh:maxCount 1;sh:class bot:Space];
 sh:property [sh:path rdf:object;sh:minCount 1;sh:maxCount 1;sh:class bot:Element];
 sh:property [sh:path prov:wasDerivedFrom;sh:minCount 1];
 sh:property [sh:path prov:wasGeneratedBy;sh:minCount 1];
 sh:property [sh:path rdfs:seeAlso;sh:hasValue <https://doi.org/10.1016/j.autcon.2025.106081>];
 sh:property [sh:path civ:contactGeometry;sh:minCount 1] .
'''
QUERIES={
 '01_Geometria_dos_Ambientes':PREFIX+'''
SELECT ?ambiente ?nome ?geometria ?unidade ?referencial ?vertices ?triangulos
WHERE { ?ambiente a bot:Space; civ:ifcLongName ?nome; geom:hasGeometry ?geometria.
 ?geometria civ:unit ?unidade;civ:coordinateReference ?referencial;
 civ:vertexCount ?vertices;civ:triangleCount ?triangulos. } ORDER BY ?nome
''',
 '02_Cozinha_Paredes_Aberturas_Preenchimentos':PREFIX+'''
SELECT DISTINCT ?ambiente ?parede ?paredeGUID ?abertura ?preenchimento ?classe
WHERE { ?ambiente a bot:Space; rdfs:label "COZINHA";bot:adjacentElement ?parede.
 ?parede props:globalIdIfcRoot_attribute_simple ?paredeGUID.
 OPTIONAL { ?parede civ:hasOpening ?abertura.
 OPTIONAL { ?abertura civ:hasFilling ?preenchimento.?preenchimento civ:ifcClass ?classe. } }
} ORDER BY ?paredeGUID ?abertura
''',
 '03_Justificativa_das_Adjacencias':PREFIX+'''
SELECT ?ambiente ?parede ?area ?volume ?limiar ?fonte
WHERE { ?e a civ:GeometricRelationEvidence;rdf:subject ?ambiente;rdf:predicate bot:adjacentElement;
 rdf:object ?parede;civ:strictContactAreaM2 ?area;civ:intersectionVolumeM3 ?volume;
 civ:distanceThresholdM ?limiar;rdfs:seeAlso ?fonte. } ORDER BY ?ambiente ?parede
''',
 '04_Proximidades_e_Contatos_Nao_Qualificados':PREFIX+'''
SELECT ?ambiente ?parede ?situacao ?distancia ?area
WHERE { ?e a civ:GeometricRelationEvidence;rdf:subject ?ambiente;rdf:predicate civ:nearElement;
 rdf:object ?parede;civ:status ?situacao;civ:maxGapM ?distancia;civ:contactAreaM2 ?area. }
''',
 '05_Paredes_Compartilhadas':PREFIX+'''
SELECT ?parede (COUNT(DISTINCT ?ambiente) AS ?quantidade_ambientes)
WHERE { ?ambiente a bot:Space;bot:adjacentElement ?parede. }
GROUP BY ?parede HAVING(COUNT(DISTINCT ?ambiente)>1)
''',
 '06_Ambientes_sem_Adjacencia_Qualificada':PREFIX+'''
SELECT ?ambiente ?nome WHERE { ?ambiente a bot:Space;civ:ifcLongName ?nome.
FILTER NOT EXISTS { ?ambiente bot:adjacentElement ?parede. } } ORDER BY ?nome
''',
}

def run_queries(ttl_path,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    g=Graph().parse(str(ttl_path),format='turtle');counts={}
    for name,query in QUERIES.items():
        (output/(name+'.rq')).write_text(query,encoding='utf8')
        result=g.query(query);cols=[str(v) for v in result.vars]
        rows=[{key:None if value is None else str(value) for key,value in zip(cols,row)} for row in result]
        save_csv(output/(name+'.csv'),rows,cols);counts[name]=len(rows)
    save_json(output/'registro_consultas.json',{'arquivo_consultado':str(ttl_path),'respostas':counts,
       'nota_cadeia':'A porta preenche uma abertura da parede adjacente. Isso não prova que a porta atende a esse cômodo.'})
    return counts

def validate_graph(ttl_path,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    g=Graph().parse(str(ttl_path),format='turtle')
    # PREFIX SPARQL are accepted by RDFLib's Turtle parser, but use explicit @prefix block.
    shapes=Graph().parse(data=SHAPES[SHAPES.index('@prefix'):],format='turtle')
    shapes.serialize(output/'regras_shacl.ttl',format='turtle')
    conforms,report,text=validate(g,shacl_graph=shapes,inference='none',advanced=True)
    report.serialize(output/'relatorio_shacl.ttl',format='turtle');(output/'relatorio_shacl.txt').write_text(text,encoding='utf8')
    SH=Namespace('http://www.w3.org/ns/shacl#')
    result={'conforme_regras_declaradas':bool(conforms),'violacoes':len(set(report.subjects(RDF.type,SH.ValidationResult))),
      'limite':'Não demonstra completude arquitetônica nem valida todas as restrições IFC/EXPRESS.'}
    # Additional executable controls: every qualified edge must have evidence and numeric guards.
    qualified=list(g.triples((None,BOT.adjacentElement,None)));evidence={}
    for e in g.subjects(RDF.type,CIV.GeometricRelationEvidence):
        if g.value(e,RDF.predicate)==BOT.adjacentElement:
            evidence[(g.value(e,RDF.subject),g.value(e,RDF.object))]=e
            assert float(g.value(e,CIV.intersectionVolumeM3))<=float(g.value(e,CIV.volumeThresholdM3))
            assert float(g.value(e,CIV.strictContactAreaM2))>0
            assert float(g.value(e,CIV.maxGapM))<=float(g.value(e,CIV.distanceThresholdM))
    # The union includes original converter edges. Only generated adjacentElement facts are required here.
    derived_edges={(s,o) for s,o in evidence}
    assert all((s,BOT.adjacentElement,o) in g for s,o in derived_edges)
    result['adjacencias_derivadas_com_evidencia']=len(derived_edges)
    result['adjacencias_totais_incluindo_conversor']=len(qualified)
    # Controlled negative test removes the mesh link of one space: validator must fail.
    room=next(g.subjects(RDF.type,BOT.Space));links=list(g.triples((room,GEOM.hasGeometry,None)))
    for t in links:g.remove(t)
    negative=validate(g,shacl_graph=shapes,inference='none')[0]
    assert not negative,'SHACL não detectou ambiente sem geometria'
    result['controle_negativo_ambiente_sem_geometria_detectado']=True
    save_json(output/'registro_validacao.json',result)
    return result
