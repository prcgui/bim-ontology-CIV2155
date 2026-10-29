# Notebook 1 — revisão 03: resultados executados

Ensaio sobre o IFC arquitetônico FNDE Tipo 2 R03, preservado por SHA-256. [Notebook com saídas](../../notebooks/01_Conversao_Arquitetura_IFC_LBD_v03.ipynb) · [Código](../../consultas/notebook1_v03/) · [Fontes](../../referencias/notebook1_v03/).

| Verificação | Resultado |
|---|---:|
| Ambientes processados | 41 |
| Produtos com malha XYZ no RDF | 2109 |
| Falhas de malha registradas | 3 |
| Triplas da conversão IFCtoLBD | 56961 |
| Triplas da união enriquecida | 117591 |
| Adjacências derivadas com evidência | 135 |
| Testes geométricos analíticos aprovados | 12 |
| Violações nas regras SHACL declaradas | 0 |

O controle negativo SHACL detectou a retirada da geometria de um ambiente em cópia na memória. Os dez testes da correção textual Java também foram aprovados. A [conferência independente](conferencia_independente.json) compara as coordenadas TIN Z recuperadas do RDF às malhas de cozinha, parede, porta e janela.

Situações geométricas registradas: {'contato_sem_validacao_volumetrica': 194, 'adjacencia_geometrica_no_limiar_numerico': 135, 'contato_com_intersecao_volumetrica': 84, 'proximidade_de_superficies': 18}.

## Consulta e reprodução

O [pacote ZIP completo](CIV2155_Notebook1_v03_Resultados.zip) contém `rdf/arquitetura_grafos_nomeados.trig`, a união `rdf/arquitetura_enriquecida.ttl`, consultas, respostas, regras, relatórios e manifesto com hashes. Os grafos completos são compactados devido ao volume da geometria. A pasta [consultas](consultas/) contém as consultas SPARQL e respostas CSV efetivamente obtidas após reabrir o Turtle.

Na cozinha, 10 paredes atenderam ao critério geométrico estrito; 1 permaneceu por proximidade e 1 apresentou interseção volumétrica. As relações parede → abertura → preenchimento são provenientes de IfcRelVoidsElement e IfcRelFillsElement. A associação de uma porta ao cômodo não é inferida por transitividade via parede compartilhada.

## Limites

O resultado não demonstra completude arquitetônica. Não gera limites IFC de segundo nível, corrige o modelo ou integra arquitetura e estrutura. Distância estrita: 0,01 mm; proximidade: 2 mm; desvio angular: 0,1°; área mínima: 1 mm²; tolerância de volume: 10⁻⁸ m³. Estes são parâmetros do ensaio, não constantes atribuídas aos artigos. Uma generalização requer análise de sensibilidade e validação arquitetônica independente.

SHA-256 do IFC: `0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a`.

Falhas no processamento de relações: 17 pares, registrados em [JSON](relacoes/falhas_relacoes_geometricas.json) e no grafo de avaliação, sem correção automática. Esses casos permanecem indeterminados.

Doze ambientes não apresentaram adjacência qualificada; não se conclui que não tenham paredes. O RDF conserva malhas trianguladas, não toda a representação paramétrica IFC. Deflexão linear: 0,001 m; angular: 0,5 rad; precisão: 0,00001 m. O limiar estrito de 0,01 mm não comprova exatidão física nessa escala; a relação entre tolerâncias e triangulação exige avaliação de sensibilidade.
