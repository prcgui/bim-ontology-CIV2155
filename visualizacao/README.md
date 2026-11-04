# Aplicações de exploração

As páginas publicadas e seus códigos estão em `docs/`, sem uma segunda cópia dos arquivos HTML.

| Aplicação | Abrir | Código |
|---|---|---|
| Explorador integrado dos três modelos | [GitHub Pages](https://prcgui.github.io/bim-ontology-CIV2155/) | [docs/index.html](../docs/index.html) |
| Exploração da arquitetura do N1 | [GitHub Pages](https://prcgui.github.io/bim-ontology-CIV2155/arquitetura-n1.html) | [docs/arquitetura-n1.html](../docs/arquitetura-n1.html) |

O explorador integrado lê o [índice produzido pelo N3](../docs/dados/exploracao.json). Permite filtrar os 26.601 produtos por origem, classe e tipo RDF, examinar relações e evidências, consultar os Psets da V137 e exportar recortes. As oito consultas mostram respostas salvas; o SPARQL está no N3. O índice conserva termos, datatypes, idiomas e grafos das quádruplas selecionadas, mas não substitui o Dataset completo.

A aplicação do N1 apresenta uma fotografia do RDF publicado: 80.234 triplas, 41 espaços e 101 pares ambiente-esquadria. Seus dados estão incorporados no HTML. Agrupar Door e Window na tela não cria uma nova classe OWL. Os três ambientes inconclusivos continuam sem contagem.

As [imagens em caixas](../resultados/grafo_rdf/README.md) são figuras de apresentação geradas no N1 com RDFLib e Matplotlib. As aplicações são próprias do estudo; não equivalem a uma ferramenta consolidada de edição de ontologias e não foram avaliadas com participantes.

Para uso local do explorador integrado, sirva a pasta `docs` por HTTP e abra `index.html`, que carrega `dados/exploracao.json` por caminho relativo. A página N1 também pode ser aberta como HTML local. O GitHub Pages publica a pasta `docs` da branch `main`.

[Método, fontes e limites](../docs/Organizacao_e_Exploracao.md) · [Grafo arquitetônico](../resultados/Arquitetura_Analisada.zip) · [Dataset integrado](../resultados/organizacao/README.md).
