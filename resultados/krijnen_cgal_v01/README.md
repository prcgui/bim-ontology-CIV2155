# Ensaio parcial de relações espaciais com CGAL/Nef

Krijnen et al. (2020), *Validation and inference of geometrical relationships in IFC*, DOI [10.46421/2706-6568.37.2020.paper008](https://doi.org/10.46421/2706-6568.37.2020.paper008), seção 3.3. [Código dos autores citado no artigo](https://doi.org/10.5281/zenodo.3633653) · [Repositório dos autores, versão arquivada](https://github.com/aothms/IfcOpenShell/tree/v0.7.0-validation) · [PDF](../../referencias/krijnen_cgal_v01/Validation%20and%20inference%20of%20geometrical%20relationships%20in%20IFC.pdf).

## Implementação e alcance

Ensaio de operações CGAL/Nef isoladas; não é reprodução integral do IfcConvert de 2020. A entrada usa IfcOpenShell 0.8.4/OpenCascade e malhas OFF, em metros e no referencial do projeto. EPECK, soma de Minkowski com cubo e interseção Nef seguem os trechos publicados. O corpo de `create_nef_polyhedron` foi extraído; a alteração de namespace está registrada. O cubo mantém o domínio dos autores, com construtor CGAL diferente.

A primeira variante processou a malha composta como um único poliedro: 14 paredes aceitas e 20 rejeitadas por autointerseção da entrada combinada. A segunda separa os componentes fechados e aplica união Nef antes da expansão. Essa preparação é extensão deste estudo, fundamentada nas operações booleanas do [manual CGAL 5.6](https://doc.cgal.org/5.6/Nef_3/index.html). Não desloca vértices, preenche vazios ou modifica o IFC. Foram conferidos os volumes assinados positivos e a preservação das faces dos componentes deste conjunto; não se generaliza a cascas internas de vazios.

## Resultado

- 34 paredes candidatas da mesma cozinha; 68 ensaios na variante por componentes, todos concluídos.
- 14 controles analíticos aprovados, incluindo união de componentes sobrepostos e separados.
- 29 interseções não vazias sem expansão; 31 com meia-aresta de 0,00001 m. W08 e W09 passam a apresentar interseção com expansão; já tinham evidência de superfície no piloto anterior.
- 19 interseções volumétricas sem expansão acima de 1e-8 m³; 11 candidatos por contato/tolerância; três sem interseção; um caso tridimensional não quantificado (W22).
- 11 paredes não possuem `TopAbs_SOLID` na representação BRep consultada. Nesses casos a soma vazia de volumes foi retificada para **indisponível**, e não zero. A representação por componentes Nef permite investigar o volume, sem afirmar reparação do modelo.
- Novo RDF: 1.946 triplas, incluindo as 676 triplas anteriores e 68 avaliações. Identificadores, coordenadas, parâmetros e proveniência estão registrados. Nenhuma adjacência BOT foi confirmada automaticamente.

`1e-8 m³` é limiar experimental de relato; não é tolerância normativa. EPECK opera de modo exato sobre os números de entrada: não recupera precisão perdida na interpretação IFC/triangulação. Pequenos volumes próximos de zero não são apresentados como conflitos arquitetônicos.

## Comparação e limitações

O piloto anterior mede coincidência de superfícies; o teste CGAL mede interseções de sólidos triangulados, com e sem expansão. Os sinais têm significados distintos. Maior contagem não demonstra maior acurácia. As dez paredes com evidência de superfície no piloto correspondem a 14 fragmentos de superfície, não a 14 paredes.

O método não gera automaticamente o limite semântico cômodo–parede. O artigo restringe a validação a paredes/lajes; portas/janelas e segundo nível de limites não foram implementados no protótipo descrito. `fix_spaceboundaries` da fonte arquivada também depende de `boundaries-triangulated.ifc`; o programa completo não foi executado neste ensaio. Não foram testados lajes, revestimentos, todos os ambientes ou integração estrutural. A seleção inicial de 34 paredes pode excluir outros limites. Validação arquitetônica independente permanece necessária.

## Reutilização no fluxo do Notebook 1

O módulo acrescenta uma camada opcional de avaliação ao grafo IFC2SB parcial, preservando cadeias e geometria anteriores. Contato, sobreposição, ausência no critério e inconclusão permanecem separados. A transformação híbrida desejada deve manter essa distinção antes de afirmar `delimita`, `contém`, `hospeda` ou `atravessa`.

[Código e fontes](../../consultas/krijnen_cgal_v01/) · [Consulta SPARQL](Consultar_Avaliacoes_CGAL.rq) · [Comparação por parede](Comparacao_Paredes_IFC2SB_CGAL_v01.csv) · [Relatório navegável](Relatorio_Krijnen_CGAL_v01.html) · [RDF](Cozinha_IFC2SB_Com_Avaliacoes_CGAL_v01.ttl).

Os ZIPs de execução preservam as saídas reais do Linux/Colab. A tentativa de leitura com listas CRLF e sua correção de transporte estão documentadas; esse erro de caminho não é tratado como limitação científica. O IFC original e o RDF de origem mantêm seus hashes.
