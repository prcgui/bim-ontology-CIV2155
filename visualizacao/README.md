# Exploração do resultado do Notebook 1

[Abrir a aplicação original N1 no GitHub Pages](https://prcgui.github.io/bim-ontology-CIV2155/arquitetura-n1.html).

A aplicação permite selecionar conceitos, ambientes, esquadrias e recortes de abertura. Os nós e relações foram extraídos do mesmo RDF entregue pelo Notebook 1: 80.234 triplas, 41 espaços e 101 pares ambiente–esquadria. A visão de classes agrupa visualmente Door/Window; isso não cria uma nova classe OWL. Contagens indisponíveis nos ambientes inconclusivos permanecem ausentes.

- [Fonte editável da aplicação](ontologia-notebook-1.html).
- [Versão exportada para abrir no navegador](../docs/arquitetura-n1.html). Para uso local, baixe o arquivo HTML e abra-o; o GitHub exibe o código HTML quando ele é aberto como arquivo do repositório.
- [Imagens do RDF em caixas](../resultados/grafo_rdf/README.md).
- [Grafo completo](../resultados/Arquitetura_Analisada.zip) e [vocabulário próprio](../codigo/Vocabulario.ttl).

A aplicação é uma fotografia do resultado publicado. Seus dados estão incorporados no arquivo, sem chamadas a serviços para recuperar o modelo. A versão exportada carrega os estilos públicos do componente de visualização. Atualizações futuras do grafo exigem regenerar os dados incorporados e exportar novamente a aplicação. A versão atual contém o hash do Turtle de origem no campo `sourceSha256`.

O GitHub Pages publica a pasta `/docs` da branch `main`. A aplicação N1 foi preservada byte a byte em `docs/arquitetura-n1.html`. As figuras em caixas são resultados de apresentação, gerados pelo módulo `codigo/visualizar_rdf.py`; auditorias e ensaios continuam no Drive indicado no README principal.


## Explorador integrado dos três modelos

[Abrir o explorador integrado](https://prcgui.github.io/bim-ontology-CIV2155/) · [fonte editável](explorador-integrado.html) · [página publicada](../docs/index.html) · [índice gerado pelo N3](../docs/dados/exploracao.json).

A nova página permite filtrar todos os 26.601 produtos por origem, classe IFC e tipo RDF; passar dos tipos aos indivíduos; consultar ambientes, vizinhanças e evidências; abrir os Psets da V137 e baixar recortes. O desenho usa apenas conexões efetivamente presentes no índice, com expansão seletiva. O JSON de contexto é baixado por uma ação separada da exportação RDF. As oito consultas apresentam respostas salvas, com o SPARQL disponível no notebook para edição e execução.

O índice preserva termos RDF, datatypes, idiomas e grafos das quádruplas selecionadas. Recursos auxiliares e geometria extensa continuam no Dataset integral; o índice não o substitui. Não há execução de inferência ou serviço SPARQL no navegador. Para abrir localmente, sirva a pasta `docs` com um servidor HTTP e acesse seu `index.html`; o novo explorador carrega `dados/exploracao.json` por caminho relativo. A fonte editável é publicada por cópia para `docs/index.html`.

Consulte [método, fontes e limites](../docs/Organizacao_e_Exploracao.md). A visualização foi conferida funcionalmente, mas não houve estudo de usabilidade com participantes.
