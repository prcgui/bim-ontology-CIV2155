# Notebooks do estudo

## Notebook 1 v09 — aplicação multiambientes

[Versão atual](01_Conversao_Arquitetura_IFC_LBD_v09.ipynb) · [Resultados e relatório](../resultados/multiambientes_v01/) · [Referência documental](../referencias/multiambientes_v01/).

Oito células carregam código e preparo verificados, repetem controles, reexecutam a associação nos 41 espaços, conferem documentos, verificam regressão da cozinha e integram a saída ao grafo completo v08 preservado. O preparo global foi executado nesta revisão e fica disponível no pacote, com opção de regeneração. A conversão semântica anterior é reutilizada por hash. São 65 controles: 54 dos operadores, cinco de regressão e seis da generalização.

A etapa de associação foi executada em 29 espaços; 12 ficaram inconclusivos no preparo. Foram registrados 74 pares ambiente–esquadria. A conferência documental cobre 14 ambientes, 13 novos: 35 associações corretas, 33 exclusões corretas, oito referências positivas não recuperadas por preparo e JA-09 indeterminada. Os inconclusivos não são contados como exclusões corretas. A amostra não demonstra completude dos demais espaços ou validação integral das superfícies. O papel de cada método, as referências e o que não foi reexecutado estão explicados junto às células.

## Notebook 1 v08 — rotina consolidada e conferência no projeto

[Versão atual executada](01_Conversao_Arquitetura_IFC_LBD_v08.ipynb) · [Resultados e evidências](../resultados/consolidacao_hibrido_v01/) · [Pranchas e referência documental](../referencias/consolidacao_hibrido_v01/).

Oito células reorganizam o fluxo em uma chamada de previsão, conferência posterior e integração ao grafo completo. São 59 controles aprovados. IFC2SB e Kiavarz são reexecutados; a conversão e os resultados CGAL anteriores são reaproveitados por hash. A previsão não recebe a referência documental como entrada. Lilis permanece opcional e desativado no núcleo da execução registrada.

Nos 14 casos determinados, o híbrido associa corretamente oito esquadrias e exclui seis objetos vizinhos; a JA-09 permanece indeterminada devido ao conflito entre pranchas. O IFC2SB parcial v04 já mantém esses mesmos acertos. A comparação com a listagem v03 é exploratória: avalia o que ocorreria ao usá-la como pertencimento, apesar da advertência original de que o caminho por parede não demonstra essa relação. A conferência não é cega nem revista por especialista e não certifica todos os 41 cômodos ou todas as superfícies.

O arquivo preserva o grafo principal anterior e acrescenta relações específicas para esquadrias, outros preenchimentos, candidatos internos e componentes sem FillsVoids. As versões anteriores permanecem históricas; a v08 é um notebook reorganizado, sem acumular novamente todas as células anteriores.

## Notebook 9 e Notebook 1 v07 — ensaio parcial de Lilis

[Notebook 9 executado](09_Lilis_Hibrido_Cozinha_v01.ipynb) · [Notebook 1 completo v07](01_Conversao_Arquitetura_IFC_LBD_v07.ipynb) · [Resultados, fontes e limites](../resultados/lilis_hibrido_v01/).

Oito células novas executam 20 controles e a adaptação parcial de IP/IPS, PSS e maxA no IFC original. Mantêm as dez aberturas associadas do piloto, com 12 recortes candidatos: 11 apoiados no volume 3D e um adicional de 0,062 m² por projeção. O RDF preserva as 2.559 triplas anteriores e passa a 3.244. O notebook explica as diferenças em relação ao artigo, a sensibilidade à distância e a contribuição geométrica observada. Alpha wrap e validação arquitetônica independente permanecem pendentes. A v07 preserva as saídas históricas e identifica explicitamente as oito células reexecutadas.

## Notebook 5 — IFC2SB: controle e creche integral

[Notebook de auditoria executado](05_IFC2SB_Controle_e_Creche_v01.ipynb), com cinco células Python que conferem os arquivos de execuções C++ realizadas no Colab. Não representa uma execução do C++ em Windows. O método geométrico utilizado é o [IFC2SB publicado pelos autores](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad); as rotinas de supervisão e auditoria são específicas deste estudo.

[Resultados, relatório, instruções e registros completos](../resultados/ifc2sb_controle_v01/) · [PDF e fontes](../referencias/geometria_relacoes/). O controle gera limites, mas reúne ambientes. Na creche integral, o limite operacional de 600 segundos foi atingido sem arquivo de saída; não se conclui impossibilidade do método. O IFC original foi preservado.

## Notebook 3 - Inspeção de portas IFC-RDF (CQ2)

[Notebook executado, com referências e saídas](03_Inspecao_Portas_IFC_RDF_CQ2_v01.ipynb).

Seleciona as portas por classe IFC, percorre as relações porta-abertura-hospedeiro e verifica as arestas entre hospedeiro e porta no RDF ampliado da arquitetura. As 11 células de código foram executadas localmente e reproduziram os 53 registros individuais da rotina original. Cada etapa contém explicação e referências.

Para executar no Colab, abrir o notebook e enviar os dois [arquivos de entrada indicados nos resultados](../resultados/notebook3/#entradas). No computador, a etapa 2 está configurada para a organização da pasta local do projeto; ajustar os caminhos se a execução partir desta cópia do GitHub. Não é realizada nova conversão ou solução de integração.

[Resultados e relatório](../resultados/notebook3/) · [Fontes técnicas e código das bibliotecas](../referencias/Referencias_Notebook3_CQ2.txt).

## Notebook 2 — Diagnóstico da integração entre arquitetura e estrutura

[02_integracao_arquitetura_estrutura.ipynb](02_integracao_arquitetura_estrutura.ipynb)

[Abrir a cópia de desenvolvimento no Google Colab](https://colab.research.google.com/drive/1_oHXFR9fPiNCaO66wctd-6hs2ydmAIAZ).

O notebook repete o procedimento em dois blocos: arquitetura ARQ-DTV e estrutura SMT, ambos do Projeto Tipo 2 do FNDE. As duas saídas permanecem separadas. São examinados identificadores, textos, recuperação dos vínculos com pavimentos, unidades e candidatos de correspondência entre modelos.

A execução termina no **registro dos problemas e das decisões pendentes**, sem fundir recursos, reconciliar referenciais ou aplicar soluções aos conflitos novos. Os [resultados e registros do diagnóstico](../resultados/notebook2/) apresentam as evidências observadas.

As células contêm descrição da finalidade, fontes técnicas e critérios. O motor reutilizado é IFCtoLBD 2.49.0, com a adaptação textual previamente documentada. A ampliação do escopo para elementos está explicitada nos parâmetros. As saídas registradas correspondem a uma execução local em Windows, com Python e Java 21; o notebook também prepara o ambiente de execução do Google Colab.

## Conferência da cozinha

O [Notebook 4](04_Conferencia_Cozinha_IFC_RDF_v01.ipynb) foi executado em seis células de código e documenta comparação IFC–RDF, localização por malhas, figuras e controles de integridade. [Resultados e limites](../resultados/conferencia_cozinha_v01/).

## Notebook 1 — revisão 04: adaptação parcial do IFC2SB em Python

**Conferência complementar:** [Notebook 6 — conferência geométrica do piloto](06_Conferencia_Geometrica_Piloto_IFC2SB_v01.ipynb). Seis células executadas, quatro controles, 34 paredes e 24 casos. Compara as representações com e sem subtração das aberturas, verifica classes e relações e produz figuras e registros de valores inconclusivos. [Resultados, relatório e condições pendentes](../resultados/conferencia_ifc2sb_v01/).

[Notebook completo v04](01_Conversao_Arquitetura_IFC_LBD_v04.ipynb) · [módulo novo independente, executado](01_Modulo_Geometrico_IFC2SB_Python_v01.ipynb).

As seis células novas preparam fontes verificadas por hash, executam 17 controles, verificam o IFC original, processam o piloto da cozinha, exportam e consultam o RDF com coordenadas e conferem a integridade final. O notebook completo conserva as células e saídas v03, sem reexecutá-las nesta revisão. Para repetir apenas a adaptação, utilizar o módulo independente.

[Código dos autores IFC2SB](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad) · [mapa de funções, adaptações e licença](../consultas/ifc2sb_python_v01/) · [resultados e limitações](../resultados/ifc2sb_python_v01/).

## Notebook 1 · revisão 05 · avaliação complementar CGAL

[Notebook 1 v05](01_Conversao_Arquitetura_IFC_LBD_v05.ipynb) · [Notebook 7: auditoria independente do ensaio Krijnen](07_Auditoria_Krijnen_CGAL_v01.ipynb).

As novas células auditam registros reais dos testes C++/CGAL executados em Linux e incorporam 68 avaliações ao RDF. Seis células de código foram executadas na auditoria; a opção de reiniciar o motor ficou desativada e é identificada separadamente. As células anteriores do Notebook 1 permanecem como registro, sem reexecução. [Resultados e alcance](../resultados/krijnen_cgal_v01/) · [Código e instruções](../consultas/krijnen_cgal_v01/) · [Artigo e fonte dos autores](../referencias/krijnen_cgal_v01/).

## Notebook 1 · revisão 06 · interfaces híbridas

[Notebook 1 v06](01_Conversao_Arquitetura_IFC_LBD_v06.ipynb) · [Notebook 8 independente](08_Interfaces_Hibridas_Cozinha_v01.ipynb).

Oito células novas executadas: importação e integridade do IFC, 17 controles, combinação das interfaces, comparação OCP–Shapely, RDF e consulta, triagem de pré-condições de Lilis, visualização extraída do RDF e verificação final. Os recortes IFC2SB e sinais CGAL são entradas reais da etapa; as operações de Kiavarz são adaptações explicitadas do procedimento/pseudocódigo publicado. A triagem de Lilis não gera 2LSB. As células anteriores do Notebook 1 foram preservadas, sem reexecução nesta revisão. [Código](../consultas/interfaces_hibridas_v01/) · [Fontes e diferenças](../referencias/interfaces_hibridas_v01/) · [Resultados e limites](../resultados/interfaces_hibridas_v01/).
