# Resultados — adaptação parcial IFC2SB em Python

Execução local em 29 out. 2026, incorporada à revisão 04 do Notebook 1. [Notebook completo](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v04.ipynb) · [módulo executável independente](../../notebooks/01_Modulo_Geometrico_IFC2SB_Python_v01.ipynb) · [código, fontes, funções originais e diferenças](../../consultas/ifc2sb_python_v01/).

## Procedimento

Adaptação parcial do [código IFC2SB de Fichter et al.](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), associado ao [artigo de 2021](https://doi.org/10.26868/25222708.2021.30156). Utiliza operações OpenCascade acessíveis por OCP, preservando a sequência de recorte de faces e a ancestralidade dos fragmentos. A comparação ambiente-face é extensão experimental identificada separadamente, não portabilidade integral do método.

O IFC é lido sem regravação. A cozinha, GUID `3UFjAT4k55zg_Pqo6VMw5l`, chega como conjunto de 23 faces, sem sólido. Sewing e MakeSolid produzem um sólido fechado e válido, com as mesmas 23 faces e zero arestas livres. Volume derivado: 109.524949 m³. Massa sobre faces abertas não é utilizada como volume de interseção.

As 457 paredes são examinadas no pré-filtro; 34 permanecem candidatas por bbox. Em seguida são verificados os recortes de aberturas e suas coincidências com as faces do ambiente. Bbox não prova adjacência. Superfícies coincidentes são brutas; não representam área líquida da parede.

## Resultados observados

| Verificação | Resultado |
|---|---:|
| Controles aprovados | 17 de 17 |
| Casos confrontados com corpos C++ originais executados | 9 |
| Paredes examinadas / candidatas bbox | 457 / 34 |
| Aberturas examinadas nas paredes candidatas | 24 |
| Coincidência sem interpenetração detectada no critério | 6 |
| Coincidência com interpenetração parede–ambiente | 4 |
| Sem interseção de face no critério | 11 |
| Separadas do ambiente por bbox | 3 |
| Exceções de processamento registradas | 0 |
| Superfícies brutas candidatas no RDF | 14 |
| Recortes geométricos / aberturas distintas com recorte | 11 / 10 |
| Triplas RDF | 676 |

As dez aberturas com recorte coincidente incluem os quatro casos em conflito; não são dez relações arquitetônicas aprovadas. Uma abertura pode gerar mais de um recorte, razão pela qual a consulta tem 11 linhas. “Sem interseção no critério” não comprova ausência de relação arquitetônica.

Paredes com interpenetração volumétrica identificada (GUID, volume em m³): `[('3BgFgAEMH1AR1k70kqmmGX', 0.8042500239460195), ('0mwaX7fNvBBAXIeVJZBq96', 0.41638680303484454), ('17V7r$InT5S9X3rf$rlDOY', 0.06142536901864748), ('1VhllNj3XBbvgUNHbDgqWs', 0.04777618451796997), ('17PQAe7i5DsBgg9Rvg7RRm', 0.06142504160972193), ('3MO8KHMKT4ifS0ALbQHueo', 0.04777621392425382), ('1oAmkwqafCWgjoEPq64mYa', 0.06142157386682946), ('1WwizIhz52jQoLkPqpIpsC', 0.08559951893796534), ('0Vw1PHxBfD9Pid8d4aIlJG', 0.06823998000310832), ('3pfXBBd114LP7U8seHQy5V', 0.06824108430550568)]`. Esses casos permanecem registrados, sem correção do modelo e sem promoção a limites validados.

## Arquivos para conferência

- `Resultado_Piloto.json`: critérios, versões, GUIDs, coordenadas do ambiente e das faces, áreas, volumes, estados e diagnósticos.
- `Aberturas_Verificadas.csv`: 24 registros individuais.
- `Cozinha_Superficies_Candidatas_IFC2SB_Python.ttl`: grafo consultável com geometria XYZ, referencial do projeto, unidade metro e proveniência.
- `Consulta_Ambiente_Superficie_Abertura.rq` e `Consulta_Recortes.csv`: consulta SPARQL efetivamente executada e 11 linhas obtidas.
- `Testes_Adaptacao.json`: 17 controles, com resultados C++ e Python. Os nove confrontos não demonstram equivalência fora dos casos ensaiados.
- `Geometrias_BRep_e_Controles.zip`: geometrias derivadas e registros da referência C++; não contém alteração do IFC.
- `Registro_RDF.json`, `Resumo_Execucao.json` e `Manifesto_Arquivos.json`: controles e hashes dos arquivos consolidados.

## Limites

O código não porta fallback por caixas, reconstrução global de espaços ou o motor completo IFC2SB. A interseção ambiente-face cobre planos paralelos, com tolerâncias explicitadas; curvas não são aproximadas silenciosamente. CheckParent verifica ancestralidade compatível, mas não inclusão no contorno: esse limite foi reproduzido em um controle negativo.

O resultado é um **grafo de evidências candidatas**, não uma ontologia arquitetônica completa. O piloto é da cozinha; os 41 ambientes não foram validados por este módulo. A interpretação arquitetônica independente e a expansão controlada a outros ambientes permanecem pendentes. A integração com a estrutura não é realizada nesta etapa.

SHA-256 do IFC original, confirmado antes e depois: `0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a`.
