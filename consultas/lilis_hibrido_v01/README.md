# Adaptação parcial de Lilis: código e reprodução

`operadores_lilis.py`: IP/IPS/PSS/maxA e recortes. `ensaio_lilis.py`: piloto no IFC original, sensibilidade e conferência Common 3D. `controles_lilis.py`: 20 casos analíticos. `exportar_lilis.py`: evidências candidatas no RDF, sem novas adjacências BOT certificadas. `apresentar_lilis.py`: relatório e figura das medições.

As rotinas reimplementam parte das equações e pseudocódigos de Lilis et al. (2026), DOI https://doi.org/10.1016/j.autcon.2026.106840. Não são o código C++ dos autores. [Rastreabilidade, parâmetros e limites](../../referencias/lilis_hibrido_v01/Fontes_e_Adaptacoes_Lilis_v01.json).

`faces_kiavarz.py` é uma cópia da adaptação anterior do estudo, baseada em Kiavarz et al. (2023). `ifc2sb_faces.py` é cópia da adaptação parcial IFC2SB, com atribuição a Eric Fichter e licença GPL-3.0-or-later preservadas em `COPYING`. O conjunto reutiliza código GPL; manter atribuição e licença nas redistribuições. O PDF de Lilis tem licença própria CC BY 4.0.

O Notebook 9 baixa um pacote com código e entradas fixadas, verifica os hashes e executa os controles e a geometria do IFC. Avaliações CGAL e interfaces anteriores são entradas reaproveitadas; seus motores não são reexecutados nesse notebook.
