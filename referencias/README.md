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
