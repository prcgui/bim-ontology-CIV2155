# Exploração do resultado do Notebook 1

[Abrir a aplicação no GitHub Pages](https://prcgui.github.io/bim-ontology-CIV2155/).

A aplicação permite selecionar conceitos, ambientes, esquadrias e recortes de abertura. Os nós e relações foram extraídos do mesmo RDF entregue pelo Notebook 1: 80.234 triplas, 41 espaços e 101 pares ambiente–esquadria. A visão de classes agrupa visualmente Door/Window; isso não cria uma nova classe OWL. Contagens indisponíveis nos ambientes inconclusivos permanecem ausentes.

- [Fonte editável da aplicação](ontologia-notebook-1.html).
- [Versão exportada para abrir no navegador](../docs/index.html). Para uso local, baixe o arquivo HTML e abra-o; o GitHub exibe o código HTML quando ele é aberto como arquivo do repositório.
- [Imagens do RDF em caixas](../resultados/grafo_rdf/README.md).
- [Grafo completo](../resultados/Arquitetura_Analisada.zip) e [vocabulário próprio](../codigo/Vocabulario.ttl).

A aplicação é uma fotografia do resultado publicado. Seus dados estão incorporados no arquivo, sem chamadas a serviços para recuperar o modelo. A versão exportada carrega os estilos públicos do componente de visualização. Atualizações futuras do grafo exigem regenerar os dados incorporados e exportar novamente a aplicação. A versão atual contém o hash do Turtle de origem no campo `sourceSha256`.

O GitHub Pages publica `docs/index.html` a partir da pasta `/docs` da branch `main`. As figuras em caixas são resultados de apresentação, gerados pelo módulo `codigo/visualizar_rdf.py`; auditorias e ensaios continuam no Drive indicado no README principal.
