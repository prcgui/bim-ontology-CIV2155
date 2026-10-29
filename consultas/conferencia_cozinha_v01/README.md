# Código da conferência da cozinha

Rotinas carregadas por SHA-256 no [Notebook 4](../../notebooks/04_Conferencia_Cozinha_IFC_RDF_v01.ipynb).

- `conferir_cozinha.py`: leitura IFC/RDF, tuplas por GUID, localização tridimensional, diagnóstico e extrato RDF sem novas triplas.
- `plotar_conferencia.py`: corte horizontal e projeção das malhas para inspeção.

Reutiliza `geometria_relacoes.py` e `pipeline_arquitetura.py` do Notebook 1 v03, fixados no commit a2302cd. Os artigos, versões, diferenças de implementação e limites estão junto às células e no [relatório](../../resultados/conferencia_cozinha_v01/). Os cortes 2D não classificam relações arquitetônicas.
