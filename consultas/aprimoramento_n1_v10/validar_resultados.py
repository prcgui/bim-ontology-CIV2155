"""SHACL adaptado ao vocabulário v10. Wang/Zhang/Yan (2024),
DOI 10.1016/j.autcon.2024.105293, fundamenta validação explícita;
não importa nem declara implementadas as regras WHERE de ifcOWL.
Jäkel et al. (2025) é a referência anterior de validação do Notebook 1.
"""
from pathlib import Path
from rdflib import Graph,Namespace,Literal,RDF
from pyshacl import validate
from preparar_geometria import save

M=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/aprimoramento#')
B=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/testes/v10/')
BOT=Namespace('https://w3id.org/bot#')
SH=Namespace('http://www.w3.org/ns/shacl#')

def validar(g):
    return validate(g,shacl_graph=Graph().parse(Path(__file__).with_name('Validacao_Resultados_v10.ttl')),
       inference='none',advanced=True,abort_on_first=False)

def testar(out):
    base=Graph();n=B.resultado;s=B.espaco
    for triple in [(n,RDF.type,M.ResultadoPorAmbiente),(n,M.ambiente,s),(s,RDF.type,BOT.Space),
       (n,M.nome,Literal('Teste')),(n,M.estado,Literal('associacao_executada')),(n,M.quantidadeEsquadrias,Literal(0))]:base.add(triple)
    rows=[]
    def graph():return Graph()+base
    def check(name,g,expected):
        conforms,report,_=validar(g);assert bool(conforms)==expected,name
        rows.append({'controle':name,'aprovado':True,'conformidade_esperada':expected,'violacoes':len(list(report.subjects(RDF.type,SH.ValidationResult)))})
    check('resultado_executado_zero_real_e_valido',graph(),True)
    g=graph();g.set((n,M.quantidadeEsquadrias,Literal(1)));check('contagem_incompativel_rejeitada',g,False)
    g=graph();g.set((n,M.estado,Literal('estado_inventado')));check('estado_nao_declarado_rejeitado',g,False)
    g=graph();g.set((n,M.quantidadeEsquadrias,Literal(-1)));check('contagem_negativa_rejeitada',g,False)
    g=graph();g.remove((n,M.estado,None));check('estado_ausente_rejeitado',g,False)
    g=graph();g.set((n,M.estado,Literal('inconclusivo_preparacao_espaco')));g.add((n,M.motivo,Literal('Teste')))
    check('inconclusivo_com_zero_falso_rejeitado',g,False)
    g.remove((n,M.quantidadeEsquadrias,None));check('inconclusivo_sem_contagem_e_valido',g,True)
    g.add((n,M.esquadriaAssociada,B.porta));check('inconclusivo_com_associacao_primaria_rejeitado',g,False)
    g=graph();g.remove((s,RDF.type,BOT.Space));check('ambiente_sem_tipo_space_rejeitado',g,False)
    g=graph();g.add((n,M.ambiente,B.outro));g.add((B.outro,RDF.type,BOT.Space));check('resultado_com_dois_ambientes_rejeitado',g,False)
    g=graph();g.add((B.duplicado,RDF.type,M.ResultadoPorAmbiente));g.add((B.duplicado,M.ambiente,s));check('dois_resultados_para_um_ambiente_rejeitados',g,False)
    g=graph();g.set((n,M.estado,Literal('inconclusivo_preparacao_espaco')));g.remove((n,M.quantidadeEsquadrias,None));check('inconclusivo_sem_motivo_rejeitado',g,False)
    g=graph();g.remove((n,M.quantidadeEsquadrias,None));check('executado_sem_contagem_rejeitado',g,False)
    result={'total':len(rows),'aprovados':len(rows),'controles':rows}
    out=Path(out);out.mkdir(exist_ok=True,parents=True);save(out/'Controles_SHACL_v10.json',result);print('SHACL:',len(rows),'controles aprovados');return result

def run(grafo_path,out):
    out=Path(out);out.mkdir(exist_ok=True,parents=True);g=Graph().parse(grafo_path)
    assert len(set(g.subjects(RDF.type,M.ResultadoPorAmbiente)))==41
    conforms,report,text=validar(g)
    report.serialize(out/'Relatorio_SHACL_v10.ttl',format='turtle')
    result={'conforme':bool(conforms),'resultados_v10':41,
      'violacoes':len(list(report.subjects(RDF.type,SH.ValidationResult))),
      'limite':'Conformidade às shapes declaradas do vocabulário v10. Não comprova correção geométrica ou arquitetônica.'}
    save(out/'Validacao_SHACL_v10.json',result);assert conforms,text;print('Validação SHACL dos 41 resultados aprovada',flush=True);return result
