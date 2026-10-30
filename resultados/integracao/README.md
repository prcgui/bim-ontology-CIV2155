# Resultados da integração

Gerados pelo [Notebook 2](../../notebooks/02_Integracao_Arquitetura_Estrutura.ipynb). Consulte o [método, resultados e limitações](../../docs/Integracao_Arquitetura_Estrutura.md) e as [fontes utilizadas](../../referencias/integracao/README.md).

| Arquivo | Conteúdo |
|---|---|
| [Dataset RDF compactado](Integracao_Arquitetura_Estrutura.zip) | N-Quads com cinco grafos nomeados, 415.175 quádruplas. |
| [Relações RDF](Relacoes_Interdisciplinares.nt) | Vínculos e registros de medição em N-Triples; os modelos de origem estão no Dataset completo. |
| [Relações espaciais](Relacoes_Espaciais.csv) | 1.652 pares positivos, GlobalIds, critério e medições em SI. |
| [Integração por ambiente](Integracao_Por_Ambiente.csv) | 41 ambientes; os três inconclusivos mantêm células sem contagem. |
| [Identidades dos modelos](Identidades_Modelos.csv) | 26.601 produtos, nomes e URIs preservados. |
| [Modelos integrados](Modelos_Integrados.csv) | Contagens e fatores de unidade. |
| [Fontes e referenciais](Fontes_e_Referenciais.json) | Hashes IFC, unidades, placements espaciais e classes de origem. |
| [Consulta aos modelos](Consulta_Modelos.csv) · [Consulta aos vínculos](Consulta_Relacoes.csv) | Respostas SPARQL executadas sobre o Dataset reaberto. |
| [Resumo geométrico](Resumo_Geometrico.json) · [Resumo RDF](Resumo_Integracao.json) | Parâmetros, recorte e resultados primários. |

| Relação | SMT | SCO | Total |
|---|---:|---:|---:|
| Interseção parcial | 758 | 105 | 863 |
| Contenção | 196 | 2 | 198 |
| Contato por face | 124 | 467 | 591 |
| Total de pares | 1.078 | 574 | 1.652 |

São 1.333 elementos estruturais distintos nos pares positivos. A geometria foi examinada em 38 dos 41 ambientes. A reunião dos modelos preservou o resultado arquitetônico do N1, inclusive seus 101 pares ambiente–esquadria.

Os grafos nomeados contêm 80.234 enunciados arquitetônicos, 84.933 SMT, 205.194 SCO, 18.194 de relações e 26.620 de proveniência. A serialização/reabertura conserva os termos RDF por grafo. As relações não afirmam identidade de entidades, função, adequação ou conformidade estrutural.

![Relações por modelo](Relacoes_Por_Modelo.png)

![Grafo de um contato SCO–cozinha](Grafo_Integracao_Cozinha.png)

As duas figuras também estão disponíveis em SVG, com os mesmos nomes. Trilhas de auditoria e ensaios ficam no arquivo técnico do Drive, fora desta pasta.
