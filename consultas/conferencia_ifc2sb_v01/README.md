# Conferência geométrica do piloto IFC2SB — v01

[Notebook 6 executado](../../notebooks/06_Conferencia_Geometrica_Piloto_IFC2SB_v01.ipynb) · [resultados, relatório e figuras](../../resultados/conferencia_ifc2sb_v01/).

`conferir.py` reabre o IFC, verifica as relações declaradas e distingue interseção global e local nas geometrias com e sem subtração das aberturas. `visualizar.py` gera cortes ilustrativos e uma galeria dos 24 casos. São rotinas de diagnóstico específicas deste estudo, não um novo algoritmo publicado nem validação arquitetônica independente.

`ifc2sb_faces.py` é cópia byte a byte do helper da revisão 04, com licença GPL e atribuição preservadas. Reutiliza-se o subconjunto de operações geométricas adaptado do [IFC2SB dos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), associado a [Fichter et al. (2021)](https://doi.org/10.26868/25222708.2021.30156). O motor completo não é executado aqui.

As funções de leitura e os parâmetros derivam diretamente dos exemplos e da documentação do IfcOpenShell: [processamento geométrico](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html) e [subtração de aberturas](https://docs.ifcopenshell.org/ifcopenshell/geometry_settings.html#disable-opening-subtractions). [Fontes, versões e natureza das contribuições](Fontes_Conferencia_Geometrica.txt).

O Notebook 6 prepara fontes por hash, verifica entradas e quatro controles, executa a conferência, examina preenchimentos/esquema IFC4, gera figuras e confere a integridade. Os cortes 2D não classificam relações; as métricas são 3D. BRep válido não implica um único sólido fechado. Valores volumétricos indisponíveis não são substituídos por zero. Nenhum resultado é promovido automaticamente a relação BOT validada.

Os critérios e condições de aceitação são organizados nos CSVs dos resultados. A matriz v02 anterior é preservada; os novos registros complementam R04, R05, R06 e R09 sem alterar o estado de validação arquitetônica.
