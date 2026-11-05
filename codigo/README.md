# Vocabulários, consultas e atribuições

O procedimento Python oficial está nos [três notebooks](../notebooks/), com funções completas, descrição, referências, aplicação e limites junto a cada bloco. Execute as células na ordem. Nenhum notebook importa módulos Python desta pasta.

Esta pasta conserva os recursos RDF, SPARQL e SHACL usados no estudo em arquivos próprios, para consulta e abertura em ferramentas externas. Os recursos dos três notebooks também aparecem nas células; as consultas adicionais para a figura do artigo estão identificadas separadamente.

| Recurso | Uso |
|---|---|
| `Vocabulario.ttl` | Classes, propriedades e estados dos resultados geométricos do N1. |
| `01_ambientes.rq`, `02_esquadrias.rq` | Consultas da arquitetura. |
| `Vocabulario_Integracao.ttl` | Identidade dos modelos, vínculos qualificados, medidas e proveniência do N2. |
| `03_modelos_integrados.rq`, `04_relacoes_estrutura_ambientes.rq` | Consultas dos grafos integrados. |
| `Perfil_Organizacao.ttl` | Perfil próprio acrescentado pelo N3. |
| `Restricoes_Organizacao.ttl` | Contrato SHACL executado na projeção documentada. |
| `consultas_exploracao/` | Oito consultas executadas no N3 e duas consultas auxiliares da visualização do artigo, identificadas como 09 e 10. |
| `COPYING` | Texto da licença GPL das adaptações de IFC2SB. |

As cópias dos módulos Python foram retiradas para manter uma única implementação de uso, nas células. As atribuições continuam nos notebooks e nas [referências](../referencias/README.md).

**IFC2SB:** adaptação parcial de `Kernel_pre.cpp`, `Kernel_occ.cpp` e `cFace.cpp`, fonte RWTH-E3D/IFC2SB, commit `96a89cdff65f13279c0c3ce67e729ad9f9f5adad`. Copyright 2022 Eric Fichter, GPL-3.0-or-later, com [licença integral](COPYING). A tradução para Python/OCP acrescenta critérios próprios de aceitação e a aplicação às interfaces ambiente-face. Não executa integralmente o programa original, o outer hull ou a reconstrução completa de limites.

**Kiavarz:** adaptação metodológica do pseudocódigo, com projeção 3D para 2D, interseção de polígonos com anéis, tolerância entre planos e sondas no sólido. O IFC não fornece os limites `BoundedBy` exigidos pelo fluxo literal do artigo. Não é reprodução integral.

**IFCtoLBD:** distribuição oficial 2.49.0, conferida por hash, com duas correções textuais documentadas para Unicode e apóstrofos. As classes modificadas precedem os JARs originais na execução. As bibliotecas e fontes externas conservam suas licenças.

Os intermediários ficam em `.execucao/`; os resultados primários, em `resultados/`. As conferências de execução permanecem somente no [Drive](https://drive.google.com/drive/u/0/folders/1kVGXvERWXieeMeURrJF07tuLaADdrJ_O).
