# Guia dos resultados

Os arquivos abaixo são as saídas computacionais dos três notebooks. O recorte de consulta compreende cinco ambientes e os registros já produzidos nas etapas anteriores.

| Etapa | Arquivos principais |
|---|---|
| N1 — Arquitetura | [RDF arquitetônico](Arquitetura_Analisada.zip), [ambientes](Ambientes.csv) e [associações a esquadrias](Esquadrias_Por_Ambiente.csv) |
| N2 — Integração | [Dataset integrado](integracao/Integracao_Arquitetura_Estrutura.zip), [identidades](integracao/Identidades_Modelos.csv), [fontes e referenciais](integracao/Fontes_e_Referenciais.json), [modelos](integracao/Modelos_Integrados.csv), [relações espaciais](integracao/Relacoes_Espaciais.csv) e [síntese por ambiente](integracao/Integracao_Por_Ambiente.csv) |
| N3 — Recorte | [RDF N-Quads](recorte_cinco_ambientes/Recorte_Cinco_Ambientes_Relacoes.nq), [ambientes selecionados](recorte_cinco_ambientes/Ambientes_Selecionados.csv), [associações arquitetônicas](recorte_cinco_ambientes/Associacoes_Arquitetura.csv), [relações estruturais](recorte_cinco_ambientes/Relacoes_Estruturais.csv) e [objetos do contexto](recorte_cinco_ambientes/Objetos_Contexto.csv) |

## Recorte dos cinco ambientes

| Ambiente | Associações a esquadrias N1 | Relações estruturais N2 | Total registrado |
|---|---:|---:|---:|
| Cozinha | 9 | 16 | 25 |
| Despensa | 3 | 3 | 6 |
| Infantil 1 | Ausente | Indisponível | Inconclusivo |
| Playground | 0 | 1 | 1 |
| Varanda de serviço / DML | 1 | 8 | 9 |
| Total dos registros disponíveis | 13 | 28 | 41 |

As linhas contabilizam relações ambiente–componente. Um componente pode participar de mais de uma relação. Ausência de resultado por processamento inconclusivo é distinta de zero associações em um ambiente processado. Os números são resultados computacionais, não medidas de desempenho de uma avaliação independente.

## Consulta no GraphDB

Importe o [recorte N-Quads](recorte_cinco_ambientes/Recorte_Cinco_Ambientes_Relacoes.nq) preservando os grafos nomeados. Execute, sem inferência, as consultas exportadas pelo N3:

1. [Ambientes e estados](recorte_cinco_ambientes/01_ambientes_e_estados.rq) — [resultado CSV](recorte_cinco_ambientes/graphdb/01_ambientes_e_estados.csv).
2. [Esquadrias associadas](recorte_cinco_ambientes/02_esquadrias_associadas.rq) — [resultado CSV](recorte_cinco_ambientes/graphdb/02_esquadrias_associadas.csv).
3. [Relações estruturais](recorte_cinco_ambientes/03_relacoes_estruturais.rq) — [resultado CSV](recorte_cinco_ambientes/graphdb/03_relacoes_estruturais.csv).

Os recibos de [importação](recorte_cinco_ambientes/graphdb/Recibo_Importacao.json) e [consultas](recorte_cinco_ambientes/graphdb/Recibo_Consultas.json) registram essa execução externa. O N3 seleciona e exporta os dados; as consultas são executadas no GraphDB.
