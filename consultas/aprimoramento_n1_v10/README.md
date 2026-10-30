# Aprimoramento do Notebook 1 v10

Preparação ampliada e associação em 38 dos 41 espaços, com os parâmetros e limites explícitos. O código é uma adaptação do estudo, assistida por IA; os autores dos artigos não são apresentados como autores deste pacote completo.

- `recuperar_geometria.py`: recuperação controlada somente depois da falha estrita; guardas de faces, área, vértices e caixa.
- `ifc2sb_faces.py`: fonte derivada IFC2SB com licença/atribuição preservadas; aberturas sem sólido são constituídas de suas próprias faces. Sem caixa como prova.
- `faces_kiavarz.py`: interfaces adaptadas, com projeção planar micrométrica registrada e limitada a 0,1 mm.
- `auditar_interfaces.py`: partição da união e proveniência das regiões; mantém hospedeiros concorrentes.
- `auditar_contencao.py`: confirmação volumétrica ou inconclusão explícita, sem certificar contenção só por vértices.
- `ensaio_cortes_2d.py`: comparação experimental separada, inspirada no XeoBIM; não entra nas associações primárias.
- `diagnosticar_folgas.py`: candidatos projetados separados por até 20 mm, com estado distinto. A faixa exploratória não é tolerância primária.
- `validar_resultados.py` e `Validacao_Resultados_v10.ttl`: contratos SHACL próprios e contraprovas.
- `comparar_revisoes.py`: comparação pareada com a v09 e a referência documental congelada.

Não é portabilidade integral do IFC2SB, GRC, CBIP ou dos demais métodos científicos. O grafo anterior, o IFC original e as pranchas são preservados. As atribuições detalhadas constam das docstrings e de `referencias/aprimoramento_n1_v10` no repositório.
