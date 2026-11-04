# Referências utilizadas na rotina apresentada

A lista relaciona a contribuição efetivamente usada e distingue código dos autores, adaptação metodológica e decisão própria do estudo. A revisão integral da literatura e as alternativas ensaiadas estão no arquivo técnico do Drive indicado no README principal.

| Fonte | Contribuição usada | Limite da aplicação |
|---|---|---|
| [Bonduel et al. (2018), IFC to Linked Building Data](https://ceur-ws.org/Vol-2159/04paper.pdf) · [IFCtoLBD](https://github.com/jyrkioraskari/IFCtoLBD) | Conversão semântica executada com IFCtoLBD 2.49.0; base de entidades, propriedades e identidades do grafo. | Motor com duas correções textuais documentadas; não se atribui a conversão geométrica completa ao motor. |
| [Fichter et al. (2021), IFC2SB](https://doi.org/10.26868/25222708.2021.30156) · [código](https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad) | Adaptação parcial de recortes e ancestralidade de faces; motivação para preparo antes de exigir sólido fechado. | OCP/Python; não é execução integral do IFC2SB. Healing e guardas são implementação específica deste estudo. |
| [Kiavarz et al. (2023)](https://doi.org/10.3390/buildings13020350), §§4.2.2–4.4 | Interfaces por orientação, projeção/interseção, raios e sondas; associação local com aberturas. | Adaptação do pseudocódigo, com extensões próprias; a pré-condição literal `BoundedBy` não é atendida pelo IFC. |
| [Ying e Lee (2021), múltiplas representações](https://doi.org/10.1016/j.autcon.2021.103659), §§3.1 e 4.3 | Separação entre sólido, faces poligonais e pré-filtro; orientação da normalização planar controlada. | Inspiração metodológica. A normalização é própria e não reproduz integralmente o MGR. |
| [Lilis et al. (2026), diagnóstico geométrico](https://doi.org/10.1016/j.jobe.2026.115667), §§4–5 | Orientação para separar diagnóstico, correção e pré-condições no preparo conservador. | Não é execução do algoritmo completo dos autores; não implica correção universal da geometria. |
| [Zhang, Beetz e De Vries (2018), BimSPARQL](https://doi.org/10.3233/SW-180297) | Padrão de representação GEOM, com `geom:asBody`, usado nos polígonos WKT 3D. | Uso do vocabulário; o motor de funções geométricas Java dos autores não é executado. |
| [FNDE, Projeto Tipo 2](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2) | IFC arquitetônico DTV R03 e pranchas R03 02, 20 e 24–27, usados como objeto e referência documental da análise. | Um projeto e uma amostra de desenvolvimento; não representa validação externa. |

Documentação técnica usada: [IfcOpenShell](https://docs.ifcopenshell.org/), [Open CASCADE ShapeFix](https://dev.opencascade.org/doc/refman/html/class_shape_fix___shape.html), [Shapely](https://shapely.readthedocs.io/), [RDFLib](https://rdflib.readthedocs.io/), [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/), [codificação de strings IFC](https://technical.buildingsmart.org/resources/ifcimplementationguidance/string-encoding/) e [strings Java 21](https://docs.oracle.com/javase/21/docs/api/java.base/java/lang/String.html).

Os artigos completos permanecem no acervo de referências do trabalho; esta pasta apresenta a bibliografia aplicada. As atribuições e licenças de código derivado permanecem nos cabeçalhos, em [codigo/README.md](../codigo/README.md) e no arquivo de licença.

## Referências aplicadas no Notebook 2

A [bibliografia da integração](integracao/README.md) acrescenta o processo de checagem geométrica de Lilis et al. (2025), agora efetivamente aplicado, o artigo BOT de Rasmussen et al. (2021), com cópia aberta, e as normas RDF Datasets/N-Quads. A tabela distingue os conceitos das fontes das adaptações próprias e das limitações que permaneceram.


## Referências aplicadas no Notebook 3

A [bibliografia da organização e exploração](organizacao/README.md) relaciona contexto de integração, orientação a objetivos, propriedades contextualizadas, navegação visual, BOT, SHACL, PROV-O e IFC4. Cada fonte tem sua contribuição e limite explicitados. A matriz integral das alternativas e a cobertura real das leituras permanecem no Drive.


## Fundamentação complementar do preparo geométrico

As duas fontes abaixo foram incorporadas à discussão em 04/11/2026, depois da implementação. Fundamentam aspectos do preparo já existente no N1 (§§3.4 e 3.5) e reutilizado no N2 (§§4.2 e 4.3). A relação com o código é uma análise deste estudo, com diferenças de mecanismo e de domínio explicitadas nos notebooks.

| Fonte e trecho conferido | O que pode fundamentar | Alcance e diferença em relação ao código |
|---|---|---|
| BRONSART, Robert; EDESSA, Desta M.; KLEINSORGE, Lutz. *Automatic pre-mesh CAD data repairing*. International Journal of Mechanical Engineering and Applications, 1(1), 1 a 9, 2013. [DOI](https://doi.org/10.11648/j.ijmea.20130101.11). §§6.3 e 7, p. 4 a 6; §§8 e 9, p. 7 e 8. | Encadeamento ShapeFix seguido de sewing em Open CASCADE; necessidade de cuidado com tolerâncias para evitar conexão indevida e alteração da forma. | Estudo de preparo CAD/IGES para malha, sem transformação IFC em RDF. Não fornece os nossos valores de tolerância nem valida nossos resultados. As condições combinadas de aceitação são próprias. |
| BAREQUET, Gill; DUNCAN, Christian A.; KUMAR, Subodh. *RSVP: A Geometric Toolkit for Controlled Repair of Solid Models*. IEEE Transactions on Visualization and Computer Graphics, 4(2), 162 a 177, 1998. [DOI](https://doi.org/10.1109/2945.694983). §1.2, p. 163 e 164; §4.2, p. 167 e 168. | Princípio de limitar alterações em relação à geometria original e distinção entre validade geométrica e intenção de projeto. | Apoio conceitual. O RSVP não foi implementado. Sua verificação de deslocamentos individuais e autointerseções difere da comparação entre conjuntos de vértices usada aqui, que não garante proximidade de toda a superfície. |

Os PDFs integrais estão no [acervo do Drive, Reparo geométrico e tolerâncias](https://drive.google.com/drive/u/0/folders/1R_j9oQb_xVaMvgPhTe9y8G2aqYm9tQzf). Os testes do projeto avaliam comportamentos da implementação; os artigos não comprovam sua exatidão arquitetônica ou sua generalização.
