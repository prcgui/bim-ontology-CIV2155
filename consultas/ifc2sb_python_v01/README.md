# Adaptação parcial do IFC2SB para Python · v01

**Origem científica:** Fichter et al., *Automatic generation of second level space boundary geometry from IFC models*, Building Simulation 2021, p. 1083–1090. [Artigo](https://doi.org/10.26868/25222708.2021.30156) · [PDF neste repositório](../../referencias/geometria_relacoes/Fichter_et_al_2021_Geracao_Limites_Espaciais.pdf).

**Código dos autores:** [RWTH-E3D/IFC2SB](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad), commit `96a89cdff65f13279c0c3ce67e729ad9f9f5adad`. Rotinas derivadas distribuídas sob GPL-3.0-or-later, com licença e atribuição preservadas. A implementação constitui portabilidade parcial, não execução integral do IFC2SB nem equivalência demonstrada do algoritmo completo.

## Rastreabilidade das rotinas

| Origem publicada | Implementação Python | Natureza |
|---|---|---|
| [Kernel_pre.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/Kernel_pre.cpp): `cvfcipw_compound_from_orig_faces`, `cvfcipw_perform_fuse`, `cvfcipw_cut_openings_from_wall_faces`, `cvfcipw_commons_between_opening_and_wall_faces` | `cut_openings` | Adaptação da sequência CellsBuilder e do histórico Modified. Processamento por shell; ancestralidade preservada. |
| [Kernel_occ.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/Kernel_occ.cpp): `face_normal`, `face_center`, `area`, `volume`, `unify_shape` | `normal`, `center`, `area`, `volume`, `unify` | Operações OpenCascade expostas por OCP. |
| [cFace.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/cFace.cpp): `CheckParent` | `check_parent` | Mesmos critérios de produto, plano, normal e área; identidade do produto representada por GUID. Não testa inclusão no contorno. |
| [ShapeHealing.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/ShapeHealing.cpp): `get_outer_hull_of_component`; [Kernel_pre.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/Kernel_pre.cpp): `create_shapes_of_IfcSpaces` | `closed_space_solid` | Subconjunto Sewing → MakeSolid → orientação; exige uma casca fechada, validade e mesmo número de faces. Não porta a reconstrução global. |
| [Kernel_pre.cpp](https://github.com/RWTH-E3D/IFC2SB/blob/96a89cdff65f13279c0c3ce67e729ad9f9f5adad/src/Kernel_pre.cpp): `get_virtual_faces_worker` | `room_face_common` | **Extensão experimental deste estudo**, inspirada na comparação de faces. Common do OCCT substitui Clipper somente em planos paralelos; exige paralelismo mais estrito. Não é uma função pronta nem algoritmo integral dos autores. |
| [Zhang, Beetz e de Vries (2018), BimSPARQL](https://doi.org/10.3233/SW-180297) | `polygon_wkt`, `exportar_rdf.py` | Serialização de coordenadas XYZ e consulta RDF específicas deste estudo; não reutilizam o motor Java do artigo. |

**Fontes técnicas complementares:** [OCP, bindings do OpenCascade](https://github.com/CadQuery/OCP); [IfcOpenShell, processamento geométrico](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html); [RDFLib, grafos](https://rdflib.readthedocs.io/en/stable/intro_to_graphs/). As bibliotecas não substituem a referência científica nem publicam esta adaptação específica.

## Procedimento e controles

1. Confirmar SHA-256 do IFC original; obter BRep com coordenadas globais do projeto e metros. O objeto de retorno de `create_shape` é mantido vivo durante a leitura da geometria.
2. A cozinha chega como 23 faces, sem sólido. Costurar as faces e aceitar somente sólido fechado e válido, sem descarte de faces. Massa de GProp sobre faces abertas **não é interpretada como volume fechado**.
3. Examinar as 457 paredes; usar bbox apenas como pré-filtro, nunca como prova de adjacência.
4. Recortar aberturas e comparar os fragmentos com as superfícies do ambiente. Preservar GUIDs e histórico de faces; registrar áreas e coordenadas.
5. Testar interpenetração apenas sobre componentes SOLID do resultado booleano. Registrar conflitos sem corrigi-los.
6. Gravar grafo de evidências candidatas e consultar a cadeia ambiente → superfície → abertura → preenchimento. Relações declaradas IFC são distintas das calculadas.

`testar_adaptacao.py` contém 17 controles. Nove confrontam Python com resultados de corpos C++ originais extraídos e efetivamente compilados (duas situações de recorte e sete de CheckParent). Os demais verificam casos analíticos, rejeição de casca aberta, formação de sólido e o contraexemplo de CheckParent. A referência C++ foi executada com OCCT 7.6.3; Python utiliza OCP/OCCT 7.8.1. Igualdade nos controles não prova equivalência em todos os modelos.

`Extracao_Corpos_CPP.json` registra os hashes dos corpos extraídos; `Referencia_IFC2SB_Extraida.cpp` contém o adaptador de teste. Compilação, execução e resultados C++ estão em `referencia_cpp/`. O adaptador fornece apenas estruturas mínimas e exemplos de controle, sem executar o IFC2SB completo.

## Limites assumidos

- Não porta fallback por caixas para hospedeiro já perfurado, reconstrução global de espaços, seleção de face exterior ou reparação global.
- Faces curvas e planos não paralelos ficam fora do critério de contato. WKT é produzido somente para faces com arestas retas; BRep preserva a geometria derivada.
- Lista ordenada de aberturas substitui o unordered_map C++; aberturas sobrepostas exigem investigação própria.
- Superfícies de parede são **brutas**, antes de descontar os vazios. Recortes são registrados separadamente; áreas não devem ser somadas como área líquida.
- Coincidência geométrica não comprova pertencimento funcional nem certifica limite arquitetônico. A validação arquitetônica independente permanece pendente.
- O piloto é da cozinha. O pré-filtro percorre todas as paredes, mas não se demonstrou a associação correta para todos os 41 ambientes.
- O IFC original não é regravado. Sewing e recortes produzem apenas objetos derivados em memória e arquivos BRep separados.

O grafo usa predicados locais de evidência candidata. `geom:asBody` contém WKT XYZ no referencial local do projeto, explicitamente identificado, em metros; não é atribuído CRS84 ou localização geográfica. Não são produzidas novas afirmações BOT de adjacência ou contenção como se estivessem validadas.
