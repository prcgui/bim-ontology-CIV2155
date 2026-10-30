# Núcleo multiambientes · Notebook 1 v09

`preparar_geometria.preparar(IFC, cache, workers=2)` extrai os 41 espaços, lê relações e produtos, examina 457 paredes e compartilha os recortes IFC2SB parciais. O preparo original desta revisão já está preservado no pacote, com hashes.

`rotina_multiambientes.executar_lote(IFC, cache, saida)` percorre todos os IfcSpace. `RotinaMultiambientes(cache).executar_ambiente(GUID, saida)` executa um ambiente do mesmo catálogo. Outros GUIDs ou outro IFC são rejeitados; não há associação baseada no nome. Os parâmetros são comuns a todos os ambientes.

`auditar_lote.py`: diagnóstico OCP entre espaços, conferência documental posterior e regressão da cozinha. `testar_generalizacao.py`: cobertura, isolamento, parâmetros e inconclusão. `integrar_lote_rdf.py`: identidades por GUID e complemento versionado ao grafo completo v08. `apresentar_lote.py`: relatório e figuras. `Vocabulario_Multiambientes.ttl`: significado das relações e dos estados.

Helper IFC2SB e testes de origem: Fichter et al. (2021), portabilidade parcial GPL-3.0-or-later; manter atribuição e LICENSE/COPYING. Faces/projeções: adaptação anterior de Kiavarz et al. (2023), com diferenças explícitas. Lilis mantém somente operadores comparativos e controles, sem execução de seu fluxo no lote. CGAL da cozinha não foi reutilizado para os demais pares. As rotinas novas de lote, cache, diagnóstico e avaliação são específicas do estudo.

[Fontes, uso e hashes](../../referencias/multiambientes_v01/Fontes_Multiambientes_v09.json) · [Referência documental](../../referencias/multiambientes_v01/Referencia_Multiambientes_R03.json). Execução não equivale a validação arquitetônica completa.
