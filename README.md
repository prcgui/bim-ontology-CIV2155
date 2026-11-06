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

Os [dados de entrada](dados/README.md) identificam os modelos originais. As [referências e atribuições](referencias/README.md) registram as fontes utilizadas. A licença do código está em [LICENSE](LICENSE).
