# Notebook 1 v08 · consolidação e conferência documental da cozinha

[Notebook executado](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v08.ipynb) · [Relatório com figuras e casos](Relatorio_Consolidacao_Cozinha_v08.html) · [Código da rotina](../../consultas/consolidacao_hibrido_v01/) · [Pranchas e referência documental](../../referencias/consolidacao_hibrido_v01/).

## Conclusão verificada

Nos 14 casos com referência documental determinada, o núcleo associa oito esquadrias corretamente e exclui seis objetos vizinhos, sem associação indevida ou omissão. A JA-09 está fora dessas métricas: a planta geral 02 mostra a janela, mas as ampliações 24/25 não a representam. O IFC a contém; a associação geométrica permanece com pendência documental.

| Procedimento | Corretas | Indevidas | Omissões | Exclusões corretas |
|---|---:|---:|---:|---:|
| Listagem por parede v03, usada como hipótese de pertencimento | 4 | 2 | 4 | 4 |
| IFC2SB parcial v04 | 8 | 0 | 0 | 6 |
| Híbrido consolidado v08 | 8 | 0 | 0 | 6 |

A v03 já advertia que a cadeia parede–abertura–preenchimento não prova pertencimento ao cômodo. Sua linha avalia o uso exploratório dessa listagem para a pergunta atual, não um classificador arquitetônico previamente certificado. O ganho frente à listagem é recuperar quatro janelas do lado oeste e retirar uma PA2 e uma JA-06 da copa vizinha.

**Não foi demonstrado ganho de acerto frente ao IFC2SB parcial v04.** A consolidação mantém seus acertos e acrescenta interfaces, proveniência, integração ao grafo completo e saídas separadas. O fluxo atual recupera nove esquadrias geometricamente associadas (incluindo JA-09), outro preenchimento IfcWall AL25, dez alvenarias internas candidatas e três componentes sem FillsVoids candidatos. Dois componentes são compatíveis por posição com os requadros de tela das JA-10; o terceiro acompanha a JA-09 pendente. Essas categorias não são somadas como portas/janelas.

## Execução e integração

Oito células executadas em um novo kernel, sem erros; 59 controles aprovados. A adaptação parcial IFC2SB e Kiavarz foram reexecutados; o inventário examinou todas as 184 aberturas e as 92 entidades IfcDoor/IfcWindow. A conversão semântica e as avaliações CGAL anteriores foram verificadas por hash e reaproveitadas. Lilis fica opcional, desativado no núcleo desta execução.

O novo grafo reaberto contém **120191 triplas**, preservando byte a byte o grafo histórico de 117.591 triplas como prefixo do Turtle. Os produtos são ligados por GUID único às identidades anteriores. A consulta atual recupera nove esquadrias distintas e usa `con:esquadriaAssociada`, sem atribuição por transitividade via parede. Não se regrava o IFC.

[Grafo completo compactado](rdf_principal/Notebook1_Grafo_Completo_v08.zip) · [Complemento com identidades principais](rdf_principal/Complemento_Com_Identidades_N1_v08.ttl) · [Consulta atual](rdf_principal/Consultar_Cozinha_Atual_v08.rq) · [Resposta](rdf_principal/Consulta_Cozinha_Atual_v08.csv) · [Registro de integração](rdf_principal/Registro_Integracao_N1_v08.json).

## Conferência e limites

Foram lidas visualmente as pranchas FNDE R03 02/36, 24/36, 25/36 e 26/36. [Referência caso a caso e hashes](../../referencias/consolidacao_hibrido_v01/Referencia_Documental_Cozinha_R03.json). O algoritmo não recebe essa referência; a comparação é posterior. A leitura foi assistida por IA e não é revisão cega por especialista ou parecer do FNDE.

[Comparação dos métodos](conferencia/Comparacao_Metodos.csv) · [Casos individuais](conferencia/Conferencia_Esquadrias_Caso_a_Caso.csv) · [Componentes sem FillsVoids](conferencia/Conferencia_Componentes_Sem_FillsVoids.csv) · [Alvenarias internas candidatas](conferencia/Elementos_Internos_Candidatos.csv).

O perfil é restrito à cozinha e ao IFC original desta revisão. O resultado não certifica todas as 14 superfícies 3D, todas as paredes, lajes, coberturas, instalações ou os outros cômodos. Vértices internos não provam contenção integral de formas côncavas; a regra de caixas para componentes fornece candidatos. JA-09 exige compatibilização documental; não foi resolvida automaticamente.

## Fontes e reprodução

[Pacote fixado de código/entradas/referências](Pacote_Consolidacao_v08.zip) · [Fontes e papel de cada método](../../referencias/consolidacao_hibrido_v01/Fontes_Consolidacao_v08.json) · [Verificação de entrega](Verificacao_Entrega_v08.json).

Bonduel/IFCtoLBD: conversão anterior preservada. Fichter/IFC2SB: recortes e ancestralidade. Kiavarz: projeção/interseção e sondas adaptadas. Krijnen/CGAL: diagnóstico anterior reaproveitado. Lilis: comparação opcional parcial, sem alpha wrap. Zhang/GEOM: geometrias no RDF. Orquestração, componentes, referência documental e avaliação são específicos do estudo, com referências mantidas junto às etapas do notebook. Licenças e atribuição IFC2SB preservadas.
