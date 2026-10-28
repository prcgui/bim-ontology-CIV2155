# Inspeção de portas e hospedeiros no IFC e no RDF

Análise-piloto da CQ2. CIV2155. 28 out. 2026.

## Procedimento e reprodução

O [notebook 3](../../notebooks/03_Inspecao_Portas_IFC_RDF_CQ2_v01.ipynb) contém 11 etapas com explicações, referências, código e saídas de execução. A seleção é feita por classe IFC; as relações declaradas identificam a abertura e o hospedeiro; o GlobalId permite localizar os recursos no RDF para consultar suas arestas diretas. O [relatório com o método detalhado, páginas 4 e 5](Analise_Piloto_CQ2_Portas_e_Hospedeiros_v02.pdf) complementa o procedimento.

## Entradas

- [IFC arquitetônico R03](../../dados/fnde/arquitetura/TIPO2-ARQ-DTV_R03.ifc), SHA-256 `0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a`.
- [RDF arquitetônico ampliado, 56.961 triplas](entradas/arquitetura_grafo.ttl), SHA-256 `b6b6c38fc13711db4f17d145dbc4efb0ff32c73c113fcdb992a25c2f43c2e4a3`.

Para o Colab, baixar e enviar esses dois arquivos na etapa 2. O RDF é a saída ampliada da arquitetura do Notebook 2, produzida com IFCtoLBD 2.49.0 e a adaptação textual documentada. A opção `--hasGeometry=false` foi utilizada. O recorte inicial de 411 triplas não corresponde à entrada deste teste. Para execução local, ajustar os caminhos da etapa 2 à organização utilizada.

## Resultado

| Classe do hospedeiro IFC | Portas | Pares com aresta direta no RDF |
| --- | ---: | ---: |
| IfcWall | 45 | 45 |
| IfcFurniture | 8 | 8 |
| Total | 53 | 53 |

Os oito casos fora do filtro estão associados a dois objetos descritos como divisórias de granito. Em todos os 53 pares, foi encontrado `bot:hasSubElement`, no sentido hospedeiro-porta. Não foi julgada a adequação da classe IfcFurniture ao projeto de autoria.

O valor 45/53 representa a cobertura do filtro IfcWall. Não constitui uma medida geral de perda do conversor. A associação dos elementos aos cômodos permanece sem demonstração. Nenhuma geometria, reclassificação ou integração foi implementada.

## Registros

- [Inventário das 53 portas](Inventario_das_53_Portas_v01.csv).
- [Oito casos fora do critério IfcWall](Oito_Portas_Fora_do_Criterio_IfcWall_v01.csv).
- [Registro original, relações, tipos, propriedades, versões e hashes](Registro_Inspecao_Portas_CQ2_v01.json).
- [Verificação da execução do notebook](Verificacao_Execucao_Notebook_CQ2_v01.json).
- [Fontes técnicas e localização das operações](../../referencias/Referencias_Notebook3_CQ2.txt).

A execução local do notebook reproduziu os 53 registros individuais e as descrições dos hospedeiros da rotina original. Os arquivos de entrada foram preservados. A verificação se restringe a esses registros e critérios.
