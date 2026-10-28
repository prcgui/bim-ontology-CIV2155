# Referências

## Conversão IFC para Linked Building Data

BONDUEL, Mathias; ORASKARI, Jyrki; PAUWELS, Pieter; VERGAUWEN, Maarten; KLEIN, Ralf. The IFC to Linked Building Data Converter: Current Status. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 6., 2018, Londres. **Proceedings [...]**. CEUR Workshop Proceedings, v. 2159, 2018. p. 34–43. Disponível em: <https://ceur-ws.org/Vol-2159/04paper.pdf>. Acesso em: 27 out. 2026.

- [Artigo completo em PDF](Bonduel_et_al_2018_IFCtoLBD.pdf).
- [Publicação original](https://ceur-ws.org/Vol-2159/04paper.pdf).
- [Código-fonte do IFCtoLBD](https://github.com/jyrkioraskari/IFCtoLBD).

O artigo fundamenta a utilização de um conversor publicado para transformar dados IFC em grafos RDF com vocabulários de Linked Building Data. A seção 2.1, página 37, identifica a implementação em Java e o repositório do software.

O PDF é reproduzido integralmente, com atribuição aos autores e à publicação de origem. Os [anais do volume 2159](https://ceur-ws.org/Vol-2159/) autorizam cópia para fins privados e acadêmicos.

## Consulta aos dados do grafo com RDFLib

RDFLIB. **Navigating Graphs**. Documentação oficial. Seção *Basic Triple Matching*. [S. d.]. Disponível em: <https://rdflib.readthedocs.io/en/latest/intro_to_graphs/#basic-triple-matching>. Acesso em: 27 out. 2026.

- [Trechos selecionados e aplicação na célula 5 (PDF)](RDFLib_Navigating_Graphs_trechos.pdf).
- [Documentação original](https://rdflib.readthedocs.io/en/latest/intro_to_graphs/#basic-triple-matching).

A documentação fundamenta o uso de `subjects()` para selecionar recursos por tipo e de `value(..., any=False)` para consultar atributos com controle de multiplicidade. O PDF reúne recortes dos exemplos originais e explica sua aplicação na leitura dos ambientes do grafo. Trata-se de uma referência técnica; o pareamento por `GlobalId` e a comparação textual são procedimentos elaborados para o estudo com assistência de inteligência artificial.

## Verificação do modelo convertido com SPARQL e SHACL

JÄKEL, Jan-Iwo; HEINLEIN, Eva; VON CZERNITZKY, Constantin; MACKENBACH, Sven; KLEMT-ALBERT, Katharina. **Ontology for a Knowledge-Based Deconstruction of Buildings Based on BIM Models and Linked Data Principles**. *Buildings*, v. 15, n. 5, 720, 2025. DOI: [10.3390/buildings15050720](https://doi.org/10.3390/buildings15050720). Acesso em: 27 out. 2026.

- [Artigo completo em PDF, 26 páginas](Jaekel_et_al_2025_DCO.pdf).
- [Publicação e exemplos de validação, seção 5.2](https://www.mdpi.com/2075-5309/15/5/720#sec5dot2-buildings-15-00720).
- [Repositório da ontologia DCO dos autores](https://github.com/janiwojaekel/dcoOntology).
- [Arquivo publicado da ontologia, versão consultada](https://github.com/janiwojaekel/dcoOntology/blob/ae73fee5d6d488fa78f78e55624f7b507b906746/docs/dco.ttl).
- [Código adaptado da célula 6: consulta e comparação](../consultas/06_verificacao_espacial_classificacao.py).
- [Código adaptado da célula 7: validação SHACL](../consultas/07_validacao_shacl.py).

A seção 5.2.1 apresenta a avaliação do modelo por consultas SPARQL. A seção 5.2.2 apresenta três regras SHACL, com os exemplos de código nas tabelas 3 a 5, página 18 do PDF. Essas regras tratam de componentes em um cenário de desconstrução. O repositório dos autores disponibiliza a ontologia DCO; os exemplos de regras utilizados como referência estão no artigo.

As células 6 e 7 adaptam a estratégia de consulta e validação aos ambientes da creche. A implementação em Python, a consulta de pavimentos e categorias e as regras de presença, multiplicidade e tipo foram elaboradas para este estudo com assistência de inteligência artificial. A comparação funcional utiliza `Pset_SpaceCommon.Category`; as associações formais `IfcRelAssociatesClassification` são inventariadas separadamente. Os textos originais são mantidos. A conformidade SHACL caracteriza o atendimento às regras declaradas e é examinada em conjunto com a comparação IFC-LBD.

Fontes técnicas: [consulta SPARQL no RDFLib](https://rdflib.readthedocs.io/en/latest/intro_to_sparql/), [leitura de propriedades com IfcOpenShell](https://docs.ifcopenshell.org/autoapi/ifcopenshell/util/element/index.html), [recomendação SHACL do W3C](https://www.w3.org/TR/shacl/) e [exemplo de uso do pySHACL](https://github.com/RDFLib/pySHACL#python-module-use). Versões executadas: IfcOpenShell 0.8.4, RDFLib 7.1.4 e pySHACL 0.30.1.

O artigo é distribuído pelos autores sob licença **CC BY 4.0**, indicada no PDF. A cópia disponibilizada preserva o documento original e a atribuição.

## Harmonização de propriedades IFC-LBD

ORASKARI, Jyrki; KIRNER, Lukas; ZÖCKLEIN, Marit; BRELL-COKCAN, Sigrid. **A Method to Unify Custom Properties in IFC to Linked Building Data Conversion**. In: LINKED DATA IN ARCHITECTURE AND CONSTRUCTION WORKSHOP, 2024. Acesso em: 27 out. 2026.

- [Artigo completo em PDF, 10 páginas](Oraskari_et_al_2024_Propriedades_IFC_LBD.pdf).
- [PDF publicado no site do LDAC 2024](https://linkedbuildingdata.net/ldac2024/files/papers/LDAC2024_Camera_20.pdf).
- [Example13.java: exemplo de código indicado na seção 5 do artigo](https://github.com/jyrkioraskari/IFCtoLBD/blob/master/IFCtoLBD/src/main/java/examples/Example13.java).
- [Modelos e dados de demonstração dos autores](https://github.com/jyrkioraskari/props_demo).

O trabalho apresenta o mapeamento de propriedades específicas de programas para definições compartilhadas. A seção 5 indica o exemplo Java, e a seção 6 discute a harmonização dos nomes e suas limitações. Essa contribuição fundamenta a discussão sobre correspondências entre propriedades; a substituição de identificadores de propriedades por regras JSON não foi aplicada ao grafo desta etapa. O PDF é distribuído sob licença **CC BY 4.0**, indicada na primeira página.

## Codificação de caracteres e intervenção local

BUILDINGSMART INTERNATIONAL. **IFC String Encoding**. Orientação técnica sobre codificação e decodificação de caracteres no formato IFC-SPF. Disponível em: <https://technical.buildingsmart.org/resources/ifcimplementationguidance/string-encoding/>. Acesso em: 27 out. 2026.

IFCtoLBD, colaboradores. **StringOperations.java** e **RDFWriter.java**. Código-fonte do projeto IFCtoLBD, commit `ca7811b7132a843b85beee748d255f9b5b709e07`. GitHub. Acesso em: 27 out. 2026.

- [StringOperations.java: função handleUnicode](https://github.com/jyrkioraskari/IFCtoLBD/blob/ca7811b7132a843b85beee748d255f9b5b709e07/IFCtoLBD/src/main/java/org/linkedbuildingdata/ifc2lbd/core/utils/StringOperations.java).
- [RDFWriter.java: função filterExtras](https://github.com/jyrkioraskari/IFCtoLBD/blob/ca7811b7132a843b85beee748d255f9b5b709e07/IFCtoRDF/src/main/java/be/ugent/RDFWriter.java).
- [Célula 8: preparação, testes e execução da correção local](../consultas/08_correcao_textual_conversor.py).
- [Célula 9: avaliação antes e depois](../consultas/09_comparacao_apos_correcao.py).

A intervenção local tem duas finalidades: utilizar os códigos Unicode indicados nas sequências IFC em lugar de substituições textuais corrompidas e preservar os apóstrofos internos dos tokens de texto. A leitura dos textos é examinada em dez testes independentes, antes da conversão completa. A alteração foi elaborada para este estudo com assistência de inteligência artificial. O procedimento registra as diferenças em relação aos fontes originais e os hashes dos arquivos, sem modificar os JARs da distribuição dos autores. A referência metodológica da conversão permanece Bonduel et al. (2018).
