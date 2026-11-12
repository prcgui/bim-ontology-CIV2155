# BIM e grafos de conhecimento CIV2155

Estudo de caso com os modelos de arquitetura, estrutura metálica e estrutura de concreto da Creche Tipo 2 do Fundo Nacional de Desenvolvimento da Educação (FNDE), revisão R03.

O repositório reúne os procedimentos e os resultados computacionais usados no trabalho. O fluxo é organizado em três notebooks:

| Etapa | Procedimento | Resultado |
|---|---|---|
| [N1 — Arquitetura](notebooks/01_Arquitetura_IFC_RDF.ipynb) | Representação RDF e associações entre ambientes e esquadrias | [RDF arquitetônico](resultados/Arquitetura_Analisada.zip) |
| [N2 — Integração](notebooks/02_Integracao_Arquitetura_Estrutura.ipynb) | Integração dos três modelos e cálculo das relações espaciais | [Dataset integrado](resultados/integracao/Integracao_Arquitetura_Estrutura.zip) |
| [N3 — Recorte e consulta](notebooks/03_Organizacao_e_Exploracao.ipynb) | Seleção de cinco ambientes e reutilização dos registros do N1/N2 | [Recorte RDF](resultados/recorte_cinco_ambientes/Recorte_Cinco_Ambientes_Relacoes.nq) |

O recorte reúne Cozinha, Despensa, Infantil 1, Playground e Varanda de serviço/DML, com 41 associações registradas e um ambiente inconclusivo. Esses números são resultados do processamento; as imagens não validam, por si, o limiar geométrico de 0,1 mm.

Para consultar os resultados, importe o recorte no GraphDB e execute as três consultas indicadas no [guia de resultados](resultados/README.md). Para reproduzir o processamento, siga N1 → N2 → N3 e as instruções das primeiras células.

## Executar no Google Colab

1. Mantenha a pasta `bim-ontology-CIV2155` diretamente em **Meu Drive**. Os três arquivos oficiais ficam em `notebooks/`. O código Python está nas próprias células; `codigo/COPYING` preserva a licença do código adaptado.
2. No Colab, abra **Ambiente de execução → Alterar tipo de ambiente de execução**. Use **CPU** e a versão **2026.07**, que fornece **Python 3.12**. Os notebooks verificam essa versão antes da preparação. As bibliotecas de geometria permanecem nas versões utilizadas pelo estudo. Consulte a [lista oficial de versões do Colab](https://research.google.com/colaboratory/runtime-version-faq.html).
3. Execute as células em ordem: **N1 → N2 → N3**. Cada notebook conecta o Drive e localiza a mesma pasta principal. O N2 utiliza o resultado arquitetônico do N1; o N3 reúne os resultados existentes do N2.
4. Os resultados ficam em `resultados/`, `resultados/integracao/` e `resultados/recorte_cinco_ambientes/`, respectivamente. Os intermediários ficam em `.execucao/`; para uma nova rodada independente, preserve os anteriores separadamente e comece com essa pasta vazia.
5. O N3 exporta o recorte e três consultas. A execução das consultas no GraphDB e a conferência no Navisworks são etapas externas aos notebooks.

Abrir a versão publicada no Colab: [N1](https://colab.research.google.com/github/prcgui/bim-ontology-CIV2155/blob/main/notebooks/01_Arquitetura_IFC_RDF.ipynb), [N2](https://colab.research.google.com/github/prcgui/bim-ontology-CIV2155/blob/main/notebooks/02_Integracao_Arquitetura_Estrutura.ipynb), [N3](https://colab.research.google.com/github/prcgui/bim-ontology-CIV2155/blob/main/notebooks/03_Organizacao_e_Exploracao.ipynb). Para continuar no Drive, use os arquivos oficiais da pasta `notebooks/` e evite criar cópias com nomes diferentes.

Os [dados de entrada](dados/README.md) identificam os modelos originais. As [referências e atribuições](referencias/README.md) registram as fontes utilizadas. A licença do código está em [LICENSE](LICENSE).
