# Código do ensaio CGAL/Nef

Fonte científica, diferenças e resultados: [relatório do ensaio](../../resultados/krijnen_cgal_v01/).

`ensaio_nef.cpp`: variante com entrada composta. `ensaio_nef_componentes.cpp`: preparação por união dos componentes, explicitamente identificada como extensão do estudo. `nef_extraido.h`: corpo extraído do código arquivado dos autores, com namespace adaptado. Licenças originais preservadas.

`executar_componentes_colab.py` compila com clang++ e CGAL 5.6, executa 14 controles e testa as 34 paredes em duas configurações. Limites operacionais: 45 s/par e 600 s no supervisor. Os tempos não são benchmark comparável ao artigo. O pacote de entrada deve estar ao lado do supervisor. Em Linux: `python executar_componentes_colab.py`.

`preparar.py` e `preparar_componentes.py` documentam a origem IFC e a preparação dos arquivos OFF. O primeiro utiliza os caminhos organizados do projeto e o módulo `ifc2sb_faces.py` da etapa anterior; as entradas exatas estão preservadas no pacote para auditoria independente desses caminhos.

`consolidar.py EXECUCAO RDF_BASE SAIDA` acrescenta avaliações ao RDF e verifica hashes, preservação das triplas, roundtrip e consultas. Usa RDFLib 7.1.4. Não executa inferência de adjacência BOT.

Autores: [IfcOpenShell v0.7.0-validation](https://github.com/aothms/IfcOpenShell/tree/v0.7.0-validation). Depósito citado: [Zenodo 3633653](https://doi.org/10.5281/zenodo.3633653). Base técnica da extensão de união: [CGAL 5.6, Nef_3](https://doc.cgal.org/5.6/Nef_3/index.html).
