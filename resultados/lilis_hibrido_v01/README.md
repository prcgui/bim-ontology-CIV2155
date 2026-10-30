# Ensaio parcial de Lilis no híbrido da cozinha

O código passou da triagem de entradas para a adaptação e execução parcial de operadores geométricos do [artigo de Lilis et al. (2026)](https://doi.org/10.1016/j.autcon.2026.106840). O objetivo é testar sua contribuição à geração de superfícies e recortes no código híbrido. Não foi executado o método completo.

## Resultado observado

- 20 controles analíticos aprovados.
- 184 aberturas do IFC examinadas; 26 próximas com geometria avaliadas.
- 23 faces da cozinha; 11 pares candidatos de faces com outros espaços, d = 30 cm.
- 33 recortes brutos; 12 recortes locais candidatos em 14 interfaces existentes.
- As mesmas dez aberturas distintas do piloto anterior; nenhuma abertura nova associada.
- Onze recortes com apoio no volume 3D; um recorte adicional de 0,062 m² obtido por projeção, sem apoio no Common 3D no critério. Ele permanece candidato.
- 3244 triplas RDF, preservando as 2559 anteriores; 12 linhas recuperadas por SPARQL, sem novas adjacências BOT certificadas.

**Contribuição demonstrada:** estratégia alternativa de projeção das aberturas e cálculo rastreável de resíduos por subtração da união dos polígonos. Não foi demonstrado ganho de acurácia arquitetônica. O Common 3D é uma conferência adicional do estudo; exigir contato volumétrico não é uma regra do método de Lilis.

## Áreas e parâmetros

As 14 interfaces somam 91.982787 m² brutos. A união dos recortes candidatos soma 11.936844 m² e deixa 80.045943 m². Usando somente a parte apoiada no volume 3D, os valores são 11.874844 m² e 80.107943 m². São alternativas, não resultados a somar. Não representam área certificada de vidro ou parede opaca.

O teste de distância associou três aberturas em 5 cm e dez em 15, 30 e 60 cm. A quantidade de recortes brutos cresce com a distância; estabilidade de contagem não certifica geometrias iguais ou relações corretas. A variante maxA por componente é extensão separada.

## Alcance e diferenças do artigo

IP/IPS e PSS vêm dos §§2.1–2.2/Alg. 1–2; pares entre espaços do Alg. 3; recortes de abertura da Eq. 5/Alg. 5. A associação à parede é do híbrido. O Alg. 5 recebe faces brutas do IfcSpace neste ensaio, enquanto o fluxo integral do artigo recebe superfícies previamente classificadas. Shapely substitui Clipper. Alpha wrap/Alg. 4, classificação externa, geração integral nos 41 ambientes e BEM não foram implementados. As pré-condições completas não foram demonstradas para todo o IFC. Validação arquitetônica independente permanece pendente.

## Arquivos

[Notebook 9 executado](../../notebooks/09_Lilis_Hibrido_Cozinha_v01.ipynb) · [Notebook 1 v07](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v07.ipynb) · [Relatório](Relatorio_Lilis_Hibrido_v01.html) · [Figura](Comparacao_Lilis_v01.png) · [RDF](Cozinha_Hibrido_Com_Ensaio_Lilis_v01.ttl) · [Consulta](Consultar_Recortes_Lilis.rq) · [Código](../../consultas/lilis_hibrido_v01/) · [Fontes e PDF](../../referencias/lilis_hibrido_v01/).
