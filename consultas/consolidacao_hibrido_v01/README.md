# Rotina consolidada do Notebook 1 v08

Entrada única: `executar_ambiente(ifc_path, ambiente, entradas, saida, comparar_lilis=False)`, em `rotina_hibrida.py`. Perfil disponível: cozinha FNDE ARQ-DTV R03, GUID `3UFjAT4k55zg_Pqo6VMw5l`. Outros ambientes e outro IFC são recusados antes de reutilizar avaliações incompatíveis. O código não é apresentado como solução já generalizada.

O núcleo reexecuta a adaptação parcial IFC2SB e as interfaces adaptadas de Kiavarz, conservando as avaliações CGAL anteriores verificadas por hash. A saída distingue esquadrias, outros preenchimentos, candidatos internos e componentes sem FillsVoids. Lilis é comparação opcional e não modifica as decisões do núcleo.

`inventariar_projeto.py` examina todas as aberturas e todas as entidades IfcDoor/IfcWindow, inclusive componentes sem preenchimento declarado. `conferir_documentos.py` recebe a referência documental somente depois da previsão. `integrar_grafo_principal.py` liga os GUIDs às identidades existentes e preserva o grafo completo anterior. `apresentar_consolidacao.py` produz o relatório e as figuras. `Vocabulario_Consolidado.ttl` explica as novas relações candidatas.

Fontes científicas, limites e hashes: [registro completo](../../referencias/consolidacao_hibrido_v01/Fontes_Consolidacao_v08.json). As cópias de módulos anteriores preservam seus cabeçalhos, referências e licenças. O conjunto reutiliza código derivado IFC2SB sob GPL-3.0-or-later; manter atribuição e licença nas redistribuições. A comparação documental e as regras novas são específicas deste estudo.
