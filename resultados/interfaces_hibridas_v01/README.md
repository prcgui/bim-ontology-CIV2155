# Interfaces híbridas da cozinha

O procedimento combina efetivamente três entradas: recortes de abertura da adaptação parcial IFC2SB, avaliações CGAL do ensaio Krijnen e geometria do IFC original. A projeção/interseção de faces e a verificação por raios se apoiam em Kiavarz et al. (2023), §§4.2.2–4.4 e Tabelas 4–5. O resultado é um grafo de interfaces e recortes **qualificados geometricamente no critério experimental**, com validação arquitetônica independente pendente.

## Resultado executado

- 17 controles analíticos aprovados.
- 14 interfaces, em dez paredes, apoiadas pelo critério de sondas e raios. Todas mantiveram a qualificação nas sondas de 0,1, 1 e 2 mm.
- 11 recortes locais associados a dez aberturas das 24 examinadas. Os preenchimentos são três IfcDoor, seis IfcWindow e um IfcWall; o papel de preenchimento não altera a classe IFC.
- Nenhuma divergência de contorno parental nos recortes associados; 11 faces ficaram fora do critério de arestas retas.
- RDF com **2.559 triplas**, preservando as 1.946 anteriores. As 24 avaliações, inclusive negativas, permanecem.

As contagens de recortes/aberturas coincidem com o piloto anterior. A contribuição demonstrada é a combinação operacional, a conferência dos contornos e a organização rastreável por interface; não se demonstrou ganho de acurácia arquitetônica. Os números não representam a totalidade dos elementos da cozinha ou dos 41 ambientes.

## Lógica da combinação

1. Ler o mesmo IFC, com GlobalId e coordenadas de projeto em metros.
2. Examinar as 34 paredes candidatas e recortar suas faces contra as faces do IfcSpace em uma base planar local, usando Shapely.
3. Conferir a orientação com raios e sondas locais, mantendo o caso inconclusivo quando o critério não for sustentado.
4. Consumir os **recortes produzidos pelo IFC2SB**, conferir o contorno parental e intersectá-los com a interface daquele cômodo. Uma abertura não é atribuída ao cômodo apenas por compartilhar a parede.
5. Vincular os sinais **CGAL da parede inteira**, sem transformar o sinal global em conflito localizado em cada abertura.
6. Gravar a cadeia ambiente → interface → recorte de abertura → abertura IFC → preenchimento; a interface aponta para sua parede hospedeira. Preservar coordenadas, fontes e avaliações negativas.

As superfícies são brutas, com recortes de aberturas registrados separadamente; não somar áreas como se fossem área líquida arquitetônica ou área de vidro. Nenhuma nova adjacência BOT foi certificada. O IFC original não foi regravado.

## Fontes reais e natureza da implementação

**Kiavarz et al. (2023):** [artigo](https://doi.org/10.3390/buildings13020350) e [PDF](../../referencias/interfaces_hibridas_v01/An%20Automated%20Space-Based%20Graph%20Generation%20Framework%20for%20Building%20Energy%20Consumption%20Estimation.pdf). A Tabela 5 é pseudocódigo e contém chamadas incompatíveis com a API. A adaptação usa [intersection](https://shapely.readthedocs.io/en/stable/reference/shapely.intersection.html), preservando [a distinção de intersects](https://shapely.readthedocs.io/en/stable/reference/shapely.intersects.html). O [código da biblioteca Shapely 2.2.0](https://github.com/shapely/shapely/blob/2.2.0/src/shapely/set_operations.py) está arquivado com licença. A implementação completa do artigo em repositório específico não foi confirmada. [Página dos autores](https://www.ausmlab.com/publications/an-automated-space-based-graph-generation-framewor) · [GitHub do laboratório, sem equivalência afirmada com o código do artigo](https://github.com/ausmlab).

**Fichter et al. (2021):** [código dos autores IFC2SB](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad). São reutilizados os resultados e o módulo parcial anteriormente testado, não o programa completo.

**Krijnen et al. (2020):** [código citado no artigo](https://doi.org/10.5281/zenodo.3633653). Os resultados CGAL existentes são incorporados sem reiniciar o motor.

As diferenças de seleção de faces, normais, pseudocódigo e substituição de BoundedBy estão em [Fontes e adaptações](../../referencias/interfaces_hibridas_v01/Fontes_e_Adaptacoes_v01.json). Não são correções atribuídas aos autores nem reprodução integral do framework energético.

## Lilis (2026): etapa separada

A [triagem de pré-condições](Triagem_Precondicoes_Lilis_2026_v01.json), baseada no §6 do [artigo](https://doi.org/10.1016/j.autcon.2026.106840), examinou os 41 espaços e as 24 aberturas do recorte. O critério conservador Sewing/MakeSolid aceitou 29 espaços como um único sólido fechado; os demais não são declarados inválidos. Entre esses 29, foram examinados 406 pares e encontrados 12 com volume comum acima do limiar experimental.

As 24 aberturas já possuem sólidos BRep individualmente válidos, embora apenas uma tenha sido aceita pelo critério monocomponente. Isso evidencia uma limitação dessa preparação, não ausência de geometria ou falha do método de Lilis. Não foi feita união/reparação de entradas nesta triagem. **O algoritmo de geração de 2LSB de Lilis ainda não foi implementado.**

## Arquivos

[Relatório e tabelas](Relatorio_Interfaces_Hibridas_v01.html) · [RDF](Cozinha_Interfaces_Hibridas_IFC2SB_Krijnen_Kiavarz_v01.ttl) · [Consulta SPARQL](Consultar_Cozinha_Interfaces_Aberturas.rq) · [Figura gerada a partir do RDF](Grafo_RDF_Recorte_Interface.png) · [Código](../../consultas/interfaces_hibridas_v01/).
