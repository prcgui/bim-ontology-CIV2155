# Conferência geométrica do piloto IFC2SB

**Conferência interna da cozinha, com 34 paredes, 24 aberturas/preenchimentos e quatro controles analíticos aprovados.** [Notebook executado](../../notebooks/06_Conferencia_Geometrica_Piloto_IFC2SB_v01.ipynb) · [código e fontes](../../consultas/conferencia_ifc2sb_v01/) · [relatório em PDF](Relatorio_Conferencia_Geometrica_IFC2SB_v01.pdf) · [galeria HTML, com 24 casos](Conferencia_Geometrica_Cozinha.html).

## Evidências e limites

- Os quatro casos C09–C12 são janelas da mesma parede W06. O sinal do piloto era global à parede bruta; não demonstra quatro conflitos locais independentes.
- Em W06, o volume comum com a cozinha cai de 0,804250 para 0,286742 m³ com as aberturas processadas. A sobreposição permanece. Nas regiões das quatro aberturas, não se obtém sólido comum positivo com a parede processada com vazios; isso é esperado após a subtração e não valida a associação arquitetônica.
- Os 24 preenchimentos são cinco IfcDoor, oito IfcWindow e onze IfcWall. Uma das dez aberturas com recortes coincidentes tem preenchimento IfcWall. A classe isolada não determina erro de modelagem: o tipo de RelatedBuildingElement no esquema IFC4 é IfcElement.
- Nenhum dos 24 preenchimentos foi aceito como um único sólido fechado pelo helper conservador. A fração do preenchimento dentro da cozinha fica indisponível, com motivo registrado. Isso não prova que todos tenham geometria aberta ou sejam inválidos; múltiplos componentes também podem ficar fora desse helper.
- A entrada tem zero IfcRelSpaceBoundary. A cozinha, entretanto, possui geometria disponível: 23 faces permitem obter um sólido derivado válido. Ausência de relação declarada não significa ausência de coordenadas.

A conferência usa nova leitura do mesmo IFC e o mesmo ecossistema geométrico. **Não é validação por padrão-ouro arquitetônico independente.** Distância mínima, coincidência de superfície, interseção de volume e função arquitetônica são questões distintas. Não se resolvem conflitos, não se altera o IFC ou o RDF anterior e não se declara completude da arquitetura.

## Arquivos

**Retificação das referências a requisitos:** na primeira linha do quadro de critérios do relatório v01, p. 5, deve constar R03; nas duas linhas seguintes, R04. São corrigidos somente os identificadores de referência à matriz v02. As medições e os arquivos computacionais históricos permanecem inalterados. Consultar a [errata](Errata_Referencias_Requisitos_Conferencia_v01.txt) e o [CSV retificado v02](Criterios_por_Requisito_Retificados_v02.csv). A [consolidação das questões e do modelo conceitual](../../docs/modelo_conceitual_v01/CIV2155_Questoes_de_Competencia_Modelo_Conceitual_v01.pdf) registra o mapeamento e a extensão R10 separadamente.

- `Conferencia_Geometrica_Cozinha.json`: dados, versões/parametrização, GUIDs de relações e objetos, limites XYZ, métricas, valores indisponíveis e motivos.
- `Casos_Arquitetonicos_Cozinha.csv`, `Paredes_Brutas_e_Com_Vazios.csv`, `Preenchimentos_Vs_Cozinha.csv`: dados individuais de 24 casos e 34 paredes.
- `Matriz_Casos_e_Condicoes_de_Aceitacao.csv` e `Criterios_por_Requisito.csv`: condições pendentes vinculadas a R04, R05, R06 e R09; não substituem a matriz v02 nem aprovam automaticamente associações.
- `Controles_Conferencia.json`: quatro controles analíticos executados.
- `figuras/`: 24 cortes ilustrativos e uma comparação global de volumes; todos derivados de geometria, sem desenho manual de vínculos.
- `Geometrias_de_Conferencia.zip`: malhas e BReps derivados para conferência.
- `Manifesto_Arquivos.json` e `Verificacao_Entrega.json`: hashes e verificações finais.

O [artigo de Fichter et al.](https://doi.org/10.26868/25222708.2021.30156) e o [código dos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad) fundamentam o módulo geométrico anterior reutilizado. A comparação e a visualização específicas desta conferência são código do estudo, apoiado nas fontes técnicas indicadas junto às células.
