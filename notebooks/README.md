# Notebooks do estudo

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
