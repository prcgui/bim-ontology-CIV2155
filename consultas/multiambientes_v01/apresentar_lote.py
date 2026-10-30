"""Figuras e relatório de cobertura, conferência e limites da generalização."""
from pathlib import Path
import json,csv,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run(out):
    out=Path(out);figs=out/'figuras';figs.mkdir(exist_ok=True)
    batch=json.loads((out/'Resumo_Lote_v09.json').read_text(encoding='utf8'))
    audit=json.loads((out/'conferencia/Conferencia_Multiambientes_v09.json').read_text(encoding='utf8'))
    overlaps=json.loads((out/'diagnosticos/Sobreposicoes_Entre_Espacos_v09.json').read_text(encoding='utf8'))
    rdf=json.loads((out/'rdf_principal/Registro_RDF_Multiambientes_v09.json').read_text(encoding='utf8'))
    rows=list(csv.DictReader((out/'Cobertura_Todos_Ambientes_v09.csv').open(encoding='utf-8-sig')))
    t=audit['totais'];plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axes=plt.subplots(1,2,figsize=(12.5,5.2),layout='constrained')
    states=batch['estados'];labels=['Associação executada','Executada com pendências','Preparo inconclusivo']
    values=[states.get('associacao_executada',0),states.get('associacao_executada_com_pendencias',0),states.get('inconclusivo_preparacao_espaco',0)]
    axes[0].barh(labels,values,color=['#176e5b','#6a9b90','#c8842a']);axes[0].invert_yaxis()
    for i,v in enumerate(values):axes[0].text(v+.3,i,str(v),va='center')
    axes[0].set(xlim=(0,24),xlabel='Ambientes do IFC',title='Aplicação aos 41 espaços')
    axes[0].grid(axis='x',alpha=.15)
    axes[1].barh(['Referências positivas','Referências negativas'],[t['TP'],t['TN']],color='#176e5b',label='Conferência correta')
    axes[1].barh(['Referências positivas','Referências negativas'],[t['positivos_nao_recuperados_por_preparacao'],t['negativos_nao_avaliaveis_por_preparacao']],left=[t['TP'],t['TN']],color='#c8842a',label='Sem resultado por preparo')
    axes[1].invert_yaxis();axes[1].set(xlim=(0,48),xlabel='Pares ambiente–esquadria na amostra',title='Conferência documental: 14 ambientes')
    axes[1].set_ylim(2.05,-.6)
    axes[1].legend(loc='lower right',fontsize=8);axes[1].grid(axis='x',alpha=.15)
    for i,(a,b) in enumerate([(t['TP'],t['positivos_nao_recuperados_por_preparacao']),(t['TN'],t['negativos_nao_avaliaveis_por_preparacao'])]):
        axes[1].text(a/2,i,str(a),ha='center',va='center',color='white',fontweight='bold')
        axes[1].text(a+b/2,i,str(b),ha='center',va='center',color='white',fontweight='bold')
    fig.suptitle('A rotina funciona em novos cômodos, com limites de cobertura',fontsize=15,fontweight='bold')
    fig.supxlabel('JA-09: 1 conflito documental, fora das métricas. Execução e validação arquitetônica são avaliações diferentes.',fontsize=9)
    fig.savefig(figs/'Cobertura_e_Conferencia_Multiambientes.png',dpi=180);plt.close(fig)
    metrics=audit['por_ambiente'];y=np.arange(len(metrics));fig,ax=plt.subplots(figsize=(11,8.5),layout='constrained')
    hit=[r['TP'] for r in metrics];unavailable=[r['positivos_nao_recuperados_por_preparacao'] for r in metrics]
    ax.barh(y,hit,color='#176e5b',label='Associações corretas na referência')
    ax.barh(y,unavailable,left=hit,color='#c8842a',label='Não recuperadas por preparo inconclusivo')
    for i,(a,b) in enumerate(zip(hit,unavailable)):ax.text(a+b+.1,i,str(a+b),va='center',fontsize=9)
    ax.set_yticks(y,[r['nome'] for r in metrics]);ax.invert_yaxis();ax.set_xlim(0,10)
    ax.set_xlabel('Referências positivas por ambiente; JA-09 indeterminada excluída')
    ax.set_title('Amostra documental · 13 novos ambientes e cozinha de controle',fontweight='bold',pad=15)
    ax.grid(axis='x',alpha=.15);ax.legend(loc='lower right',fontsize=9)
    fig.savefig(figs/'Conferencia_Por_Ambiente.png',dpi=170);plt.close(fig)
    esc=lambda v:html.escape(str(v))
    def table(data,fields):
        return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(label)+'</th>' for key,label in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(r.get(key,'—') if r.get(key,'') not in ['',None] else '—')+'</td>' for key,label in fields)+'</tr>' for r in data)+'</tbody></table></div>'
    failed=[r for r in rows if r['estado'].startswith('inconclusivo_')]
    docs=list(csv.DictReader((out/'conferencia/Conferencia_Caso_a_Caso_v09.csv').open(encoding='utf-8-sig')))
    doc=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Notebook 1 v09 · aplicação multiambientes</title><style>body{{font:16px/1.6 system-ui;max-width:1200px;margin:36px auto;padding:0 22px;color:#213d39}}h1,h2{{line-height:1.2}}h1{{font-size:34px}}h2{{margin-top:38px}}img{{width:100%;height:auto}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:18px 0}}th,td{{padding:9px;border:1px solid #d2dfd8;text-align:left;vertical-align:top}}th{{background:#eaf2ed}}.scroll{{overflow-x:auto}}.note{{background:#fff1dd;border-left:5px solid #c8842a;padding:18px}}a{{color:#176e5b}}code{{overflow-wrap:anywhere}}</style>
<h1>Aplicação da rotina aos demais cômodos</h1>
<p>Foram solicitados todos os 41 IfcSpace: a cozinha de controle e os outros 40. O mesmo núcleo IFC2SB parcial + Kiavarz foi aplicado com parâmetros comuns, sem ajustar tolerâncias por nome do ambiente. O recorte de cada parede foi preparado uma vez e compartilhado; a referência documental foi consultada depois da previsão.</p>
<p><b>{batch['espacos_com_associacao_executada']} espaços chegaram à associação; {batch['espacos_inconclusivos']} ficaram inconclusivos no preparo. Foram registradas {batch['pares_ambiente_esquadria']} associações geométricas ambiente–esquadria, envolvendo {batch['esquadrias_distintas_associadas']} esquadrias distintas.</b> Uma porta compartilhada pode participar de dois pares; o total de pares não é um quantitativo de peças.</p>
<img src="figuras/Cobertura_e_Conferencia_Multiambientes.png" alt="Cobertura dos 41 espaços e resultado documental em 14 ambientes">
<h2>O que foi possível conferir no projeto</h2><p>A amostra intencional contém 14 ambientes: cozinha, despensa, copa, dois vestiários, dois sanitários PCD, sala de atendimento, sala de professores, lactário, Infantil 2/3, Administração, Infantil 1 e Lavanderia/Rouparia. Os três últimos permanecem na avaliação mesmo sem associação calculável.</p>
<p>Entre os casos determinados em ambientes processados: <b>{t['TP']} associações corretas, {t['TN']} exclusões corretas, {t['FP']} associações indevidas e {t['FN']} omissões após associação</b>. Há ainda <b>{t['positivos_nao_recuperados_por_preparacao']} referências positivas não recuperadas por preparo inconclusivo</b> e {t['negativos_nao_avaliaveis_por_preparacao']} negativas não avaliáveis. A JA-09 da cozinha continua indeterminada por divergência entre a planta geral e as ampliações.</p>
<div class="note">Considerando todas as 43 referências positivas da amostra, inclusive as três salas inconclusivas, a recuperação foi 35/43 = {audit['recuperacao_incluindo_inconclusivos']:.1%}. Esse valor descreve esta amostra intencional, não é estimativa estatística para todos os cômodos ou outros edifícios. Ausência de cálculo em um ambiente não foi contada como exclusão correta.</div>
<img src="figuras/Conferencia_Por_Ambiente.png" alt="Referências positivas recuperadas e não recuperadas em cada ambiente da amostra">
{table(metrics,[('nome','Ambiente'),('TP','Corretas'),('FP','Indevidas'),('FN','Omissões após associação'),('TN','Exclusões corretas'),('positivos_nao_recuperados_por_preparacao','Não recuperadas por preparo'),('indeterminados','Conflito documental')])}
<p>A conferência é documental, assistida por IA, não cega nem revista por especialista independente. Identificações usam tipo, posição e vizinhança nas pranchas R03 02, 20, 24–27. Portas/janelas em limites, acessórios, preenchimentos IfcWall e elementos internos têm papéis distintos. Não foi produzida referência exaustiva de todas as superfícies 3D ou categorias.</p>
<p><a href="../../referencias/multiambientes_v01/Referencia_Multiambientes_R03.json">Referência e justificativas</a> · <a href="conferencia/Conferencia_Caso_a_Caso_v09.csv">Casos em CSV</a> · <a href="https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2">Origem oficial FNDE</a>.</p>
<h2>Ambientes inconclusivos</h2><p>O helper de preparo exige uma única casca fechada, válida e sem descarte de faces. Recusa nesse critério não demonstra inexistência de geometria ou erro do IFC. A rotina registra motivo e contagem indisponível, preservando o modelo original.</p>
{table(failed,[('nome','Ambiente'),('ambiente','GlobalId'),('motivo','Motivo do preparo')])}
<h2>Cobertura de todos os 41 ambientes</h2><p>Vinte chegaram à associação sem pendências registradas nesse recorte; nove chegaram com pendências de faces/recortes; doze ficaram inconclusivos no preparo. Mesmo nos vinte, o estado computacional não significa aprovação arquitetônica. A quantidade de interfaces depende da segmentação do IFC e não é a quantidade de paredes físicas.</p>
{table(rows,[('nome','Ambiente'),('estado','Estado'),('interfaces','Fragmentos de interface'),('esquadrias','Esquadrias associadas'),('internos','Internos candidatos'),('componentes','Componentes candidatos')])}
<h2>Diagnósticos preservados</h2><p>O preparo examinou 457 paredes: {batch['preparo_global']['paredes_preparadas']} tiveram recorte preparado e {batch['preparo_global']['paredes_inconclusivas']} ficaram inconclusivas no módulo parcial. O fallback por caixa do programa original não foi portado; não se fabricaram geometrias substitutas.</p>
<p>Uma verificação OCP dos 406 pares entre os 29 espaços aceitos encontrou {overlaps['pares_com_sobreposicao']} pares com volume comum acima de 10⁻⁸ m³. Essas medições são diagnósticos atuais do estudo; não são operações CGAL/Nef. As sobreposições ficam registradas e não vetam automaticamente toda abertura.</p>
<p>Os sinais CGAL/Krijnen da cozinha não foram transplantados aos novos pares. Lilis não foi executado no lote; seu módulo comparativo parcial e as referências permanecem disponíveis. A generalização desta revisão é do núcleo de recortes/interfaces, não dos programas completos dos autores.</p>
<h2>Regressão e integração ao Notebook 1</h2><p>A cozinha manteve nove esquadrias, 14 interfaces, dez internos e três componentes, com a área das interfaces preservada no limiar numérico. Cinco controles de regressão e seis controles da generalização verificam cobertura, isolamento do cache, parâmetros comuns e tratamento das inconclusões.</p>
<p>O novo grafo contém {rdf['triplas_uniao_v09']} triplas e preserva integralmente a base v08 de {rdf['triplas_base_v08']} triplas. A consulta reaberta encontrou os 41 estados e os 74 pares ambiente–esquadria. Nos 12 inconclusivos, a quantidade permanece ausente, em vez de zero.</p>
<p><a href="rdf_principal/Notebook1_Grafo_Multiambientes_v09.zip">Grafo completo compactado</a> · <a href="rdf_principal/Consultar_Todos_Ambientes_v09.rq">Consulta atual</a> · <a href="rdf_principal/Consulta_Todos_Ambientes_v09.csv">Resposta</a> · <a href="diagnosticos/Sobreposicoes_Entre_Espacos_v09.csv">Sobreposições</a>.</p>
<details><summary>Ver a conferência documental caso a caso</summary>{table(docs,[('nome_ambiente','Ambiente'),('nome','Objeto'),('guid','GlobalId'),('pertence_ao_ambiente','Referência'),('resultado_conferencia','Conferência'),('justificativa','Justificativa')])}</details>
<h2>Fontes e limites de uso</h2><p>IFC2SB parcial: <a href="https://doi.org/10.26868/25222708.2021.30156">Fichter et al. (2021)</a>. Faces e interseções adaptadas: <a href="https://doi.org/10.3390/buildings13020350">Kiavarz et al. (2023)</a>. Geometria RDF: <a href="https://doi.org/10.3233/SW-180297">Zhang et al. (2018)</a>. Conversão semântica anterior preservada: <a href="https://ceur-ws.org/Vol-2159/04paper.pdf">Bonduel et al. (2018)</a>. Diagnósticos anteriores e alternativas mantidas: <a href="https://doi.org/10.46421/2706-6568.37.2020.paper008">Krijnen et al. (2020)</a> e <a href="https://doi.org/10.1016/j.autcon.2026.106840">Lilis et al. (2026)</a>. O preparo compartilhado, a execução em lote, os diagnósticos OCP e a avaliação documental são adaptações deste estudo.</p>
<p><b>Conclusão:</b> há evidência de funcionamento além da cozinha em dez novos ambientes da amostra processada. Ainda não há cobertura geométrica completa do edifício: 12 espaços exigem investigação do preparo, e a conferência documental não foi estendida a todos os pares de todos os ambientes.</p></html>'''
    (out/'Relatorio_Multiambientes_v09.html').write_text(doc,encoding='utf8')
    print('Figuras e relatório multiambientes gerados.');return audit
