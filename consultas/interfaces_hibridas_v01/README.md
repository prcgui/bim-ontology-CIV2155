# Código da combinação de interfaces

`faces_kiavarz.py`: operações planares e raios adaptados do procedimento publicado; diferenças explícitas. `pipeline_hibrido.py`: lê o IFC, consome os recortes IFC2SB e sinais CGAL e qualifica as interfaces do recorte. `exportar_hibrido.py`: conserva o RDF anterior e acrescenta relações locais. `testar_faces.py`: controles analíticos. `triagem_lilis_2026.py`: verifica condições de entrada; não gera 2LSB.

Fontes científicas, licenças e alcance: [resultados](../../resultados/interfaces_hibridas_v01/) e [referências](../../referencias/interfaces_hibridas_v01/). O helper `ifc2sb_faces.py` é cópia sem alterações da adaptação parcial anterior, com origem e licença GPL-3.0-or-later preservadas. As rotinas do estudo não são apresentadas como um repositório executável completo dos autores de Kiavarz.

O pacote de reprodução contém código, entradas geométricas intermediárias, hashes e controles. O notebook baixa o IFC original separadamente e verifica seu SHA-256. Ambientes e bibliotecas testados são registrados junto aos resultados.
