# Código da revisão 03

Módulos carregados pelo [Notebook 1 executado](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v03.ipynb), com SHA-256 conferido antes da importação. [Fontes e natureza das adaptações](../../referencias/notebook1_v03/).

- `geometria_relacoes.py`: contato de faces em 3D e interseção volumétrica; critérios de Lilis et al. adaptados em Python.
- `pipeline_arquitetura.py`: extração geométrica do IFC preservado, relações declaradas, grafos nomeados e geometria TIN Z.
- `validacao_e_consultas.py`: consultas SPARQL e regras SHACL específicas do estudo.
- `testar_geometria.py`: 12 casos analíticos com resultados conhecidos.

O IFC não é escrito por estas rotinas. Relações geométricas não comprovam pertencimento funcional de portas a ambientes. Os parâmetros e limites encontram-se junto às células do notebook.
