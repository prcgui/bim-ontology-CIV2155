"""Relatório das previsões e da conferência documental, sem modificar decisões."""
from pathlib import Path
import json,html,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def section(v,f,z):
    lines=[]
    for tri in v[f]:
        d=tri[:,2]-z
        if np.all(d>1e-9) or np.all(d<-1e-9) or np.all(abs(d)<1e-9):continue
        ps=[]
        for a,b in [(0,1),(1,2),(2,0)]:
            if abs(d[a])<1e-9:ps.append(tri[a,:2])
            if d[a]*d[b]<0:ps.append((tri[a]+(tri[b]-tri[a])*(-d[a])/(d[b]-d[a]))[:2])
        unique=[]
        for p in ps:
            if all(np.linalg.norm(p-q)>1e-8 for q in unique):unique.append(p)
        if len(unique)==2:lines.append(unique)
    return lines

def run(saida,referencia):
    out=Path(saida);ref=Path(referencia);figs=out/'figuras';figs.mkdir(exist_ok=True)
    result=json.loads((out/'Resultado_Consolidado_Cozinha_v08.json').read_text(encoding='utf8'))
    audit=json.loads((out/'conferencia/Conferencia_Documental_Cozinha_v08.json').read_text(encoding='utf8'))
    reference=json.loads((ref/'Referencia_Documental_Cozinha_R03.json').read_text(encoding='utf8'))
    inventory=json.loads((out/'inventario/Inventario_Projeto_Cozinha.json').read_text(encoding='utf8'))
    integration=json.loads((out/'rdf_principal/Registro_Integracao_N1_v08.json').read_text(encoding='utf8'))
    allcases=list(csv.DictReader((out/'conferencia/Conferencia_Esquadrias_Caso_a_Caso.csv').open(encoding='utf-8-sig')))
    colors={'acerto_associacao':'#176f5b','omissao':'#c17a1b','associacao_indevida':'#b64236','acerto_exclusao':'#949b9e','indeterminado_documental':'#8a62a5'}
    figures=[]
    fig,axes=plt.subplots(1,3,figsize=(12,4.8),layout='constrained',sharey=True)
    titles=['Consulta antiga v03','IFC2SB parcial v04','Híbrido consolidado v08']
    for ax,m,title in zip(axes,audit['metricas'],titles):
        values=[m['TP'],m['FP'],m['FN']]
        bars=ax.bar(['Corretas','Indevidas','Omissões'],values,color=['#176f5b','#b64236','#c17a1b'])
        ax.set_title(title,fontsize=12);ax.set_ylim(0,9.4);ax.grid(axis='y',alpha=.15)
        ax.bar_label(bars,padding=5)
    axes[0].set_ylabel('Portas/janelas principais · casos determinados')
    fig.suptitle('Cozinha: o ganho de acerto aparece frente à consulta antiga',fontsize=15,fontweight='bold')
    fig.supxlabel('8 referências positivas e 6 negativas. JA-09: conflito documental, fora das métricas.',fontsize=10)
    fig.savefig(figs/'Comparacao_Acertos_Erros_Omissoes.png',dpi=180);plt.close(fig)
    positions={r['guid']:r['centro_bbox_xyz_m'] for r in inventory['esquadrias_ifc']}
    room=np.load(out/'inventario/malhas'/f"{result['ambiente']}.npz")
    room_lines=section(room['vertices'],room['faces'],1.2)
    fig,axes=plt.subplots(1,2,figsize=(11.5,10),layout='constrained',sharex=True,sharey=True)
    for ax,method,title in zip(axes,['Consulta_N1_v03_parede_abertura','Hibrido_consolidado_v08'],['Consulta antiga v03','Híbrido consolidado v08']):
        ax.add_collection(LineCollection(room_lines,colors='#244653',linewidths=1.8))
        cases=[r for r in allcases if r['procedimento']==method]
        for r in cases:
            p=positions[r['guid']];status=r['resultado_conferencia'];c=colors[status]
            ax.scatter(p[0],p[1],c=c,s=40,zorder=3,edgecolors='white',linewidths=.7)
            right=p[0]>-11
            ax.annotate(r['id'],p[:2],xytext=(8 if right else -8,0),textcoords='offset points',ha='left' if right else 'right',va='center',fontsize=8,color=c)
        ax.set(xlim=(-15.9,-7.4),ylim=(6,18.8),xlabel='X do projeto IFC (m)',title=title)
        ax.set_aspect('equal');ax.grid(alpha=.12)
    axes[0].set_ylabel('Y do projeto IFC (m)')
    from matplotlib.lines import Line2D
    handles=[Line2D([0],[0],marker='o',color='white',markerfacecolor=c,label=label,markersize=7) for label,c in [('Associação correta',colors['acerto_associacao']),('Omissão',colors['omissao']),('Associação indevida',colors['associacao_indevida']),('Exclusão correta',colors['acerto_exclusao']),('Conflito documental',colors['indeterminado_documental'])]]
    fig.legend(handles=handles,loc='outside lower center',ncol=3,fontsize=9)
    fig.suptitle('Casos conferidos nas pranchas oficiais R03',fontweight='bold',fontsize=15)
    fig.savefig(figs/'Mapa_Casos_Conferidos_IFC.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,7.5),layout='constrained')
    ax.add_collection(LineCollection(room_lines,colors='#6a777d',linewidths=1.8))
    for e in result['elementos_internos_candidatos']:
        p=e['centro_bbox_xyz_m'];ax.scatter(p[0],p[1],color='#176f5b',s=40)
        ax.annotate(e['nome'],p[:2],xytext=(6,5),textcoords='offset points',fontsize=8)
    ax.set(xlim=(-15.4,-8.1),ylim=(9.9,17.9),xlabel='X do projeto IFC (m)',ylabel='Y do projeto IFC (m)',title='10 alvenarias internas candidatas · localização separada dos limites')
    ax.set_aspect('equal');ax.grid(alpha=.12)
    fig.savefig(figs/'Elementos_Internos_Candidatos.png',dpi=170);plt.close(fig)
    esc=lambda x:html.escape(str(x))
    def table(rows,fields):
        return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(label)+'</th>' for key,label in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(r.get(key,''))+'</td>' for key,label in fields)+'</tr>' for r in rows)+'</tbody></table></div>'
    methods=[dict(r,precisao=f"{r['precisao_no_recorte']:.1%}",sensibilidade=f"{r['sensibilidade_no_recorte']:.1%}") for r in audit['metricas']]
    current=[r for r in allcases if r['procedimento']=='Hibrido_consolidado_v08']
    doc=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Cozinha · híbrido consolidado e conferência documental</title>
<style>body{{font:16px/1.6 system-ui;color:#233b3b;max-width:1150px;margin:36px auto;padding:0 22px}}h1,h2{{line-height:1.2}}h1{{font-size:34px}}h2{{margin-top:36px}}img{{width:100%;height:auto}}table{{border-collapse:collapse;font-size:13px;width:100%;margin:18px 0}}td,th{{padding:10px;border:1px solid #d1ddda;text-align:left;vertical-align:top}}th{{background:#e7f2ec}}.note{{background:#fff2df;border-left:4px solid #b97825;padding:18px}}.scroll{{overflow-x:auto}}a{{color:#176f5b}}code{{overflow-wrap:anywhere}}</style>
<h1>Cozinha: rotina consolidada e conferência no projeto</h1>
<p>O Notebook 1 v08 reúne uma entrada única para processar a cozinha: recortes IFC2SB, interfaces adaptadas de Kiavarz e sinais CGAL verificados. Lilis permanece comparação opcional. A referência documental é consultada depois da previsão e não seleciona as associações do algoritmo.</p>
<h2>Conclusão observada</h2><p><b>Frente à consulta antiga v03, foram recuperadas quatro janelas e removidas duas associações com a copa vizinha.</b> Nos 14 casos determinados da conferência, o híbrido obteve oito associações corretas, seis exclusões corretas, nenhuma associação indevida e nenhuma omissão. A janela JA-09 é indeterminada por conflito entre documentos e fica fora das métricas.</p>
<p>O IFC2SB parcial v04 já produz as mesmas esquadrias principais. Portanto, não foi demonstrado ganho de contagem frente a essa etapa. A consolidação acrescenta organização por interface, ligações com o grafo completo, dez candidatos internos e três componentes sem FillsVoids, mantendo sua natureza candidata.</p>
<img src="figuras/Comparacao_Acertos_Erros_Omissoes.png" alt="Comparação de acertos, associações indevidas e omissões">
{table(methods,[('procedimento','Procedimento'),('TP','Corretas'),('FP','Indevidas'),('FN','Omissões'),('TN','Exclusões corretas'),('precisao','Precisão no recorte'),('sensibilidade','Recuperação no recorte')])}
<div class="note">Conferência documental assistida por IA, realizada nesta revisão; não é revisão cega por especialista nem parecer do FNDE. O recorte é único e finito. Os percentuais não representam desempenho global nos 41 cômodos. Não foi produzida referência exaustiva para todas as 14 superfícies 3D, lajes, coberturas ou instalações.</div>
<h2>Referência documental e divergência JA-09</h2><p>Foram inspecionadas visualmente as pranchas oficiais R03: 02 (planta geral), 24 e 25 (cozinha) e 26 (despensa). A correspondência ao IFC usa tipo, posição relativa e vizinhança. A planta geral 02 mostra JA-09 no lado leste da cozinha; a ampliação 24 e a vista 02 da prancha 25 não a representam. O IFC contém a janela nessa posição. A rotina conserva sua associação geométrica e registra a divergência documental.</p>
<p><a href="../../referencias/consolidacao_hibrido_v01/Referencia_Documental_Cozinha_R03.json">Referência caso a caso e hashes</a> · <a href="https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/proinfancia/projetos-arquitetonicos-para-construcao/projeto-tipo-2">Origem oficial FNDE</a>.</p>
<img src="figuras/02_Cozinha_Contexto.png" alt="Recorte da planta geral oficial 02 com cozinha, despensa e copa; JA-09 aparece no lado leste"><p><small>Recorte da prancha 02/36 R03, FNDE. Desenho original sem anotações acrescentadas; extração apenas para leitura.</small></p>
<img src="figuras/Mapa_Casos_Conferidos_IFC.png" alt="Comparação dos casos na projeção XY do IFC"><p><small>Mapa derivado do IFC: contorno da cozinha em Z = 1,20 m e centros dos objetos projetados em XY. As janelas altas aparecem por projeção. R/N correspondem às linhas da referência documental; a figura não é a prancha original.</small></p>
<h2>Acertos, erros e omissões por caso</h2>{table(current,[('id','Caso'),('nome','Tipo'),('pertence_a_cozinha','Referência'),('previsto','Associado'),('resultado_conferencia','Resultado'),('justificativa','Leitura do projeto'),('evidencia','Prancha/vista')])}
<h2>O que ficava de fora da pergunta sobre esquadrias</h2><p>AL25 permanece IfcWall e é apresentado como outro preenchimento declarado no IFC, sem ser transformado em porta ou janela. Dez alvenarias de apoio internas são registradas como candidatos de localização. A prova por vértices não certifica contenção integral de geometrias côncavas nem função construtiva.</p>
<img src="figuras/Elementos_Internos_Candidatos.png" alt="Posição dos dez candidatos internos">
<p>Também foram localizados três componentes V02 sem IfcRelFillsElement. Dois correspondem por posição aos requadros para tela mosquiteiro indicados junto às JA-10; o terceiro acompanha a JA-09 e compartilha sua pendência documental. São ligações geométricas candidatas, distintas de preenchimento ou decomposição declarados.</p>
{table(audit['componentes_sem_FillsVoids']['casos'],[('id','Caso'),('nome','Nome IFC'),('pertence_a_cozinha','Referência'),('previsto','Candidato recuperado'),('resultado_conferencia','Conferência'),('justificativa','Evidência')])}
<h2>Integração efetiva ao Notebook 1</h2><p>A conversão IFCtoLBD e o grafo enriquecido v03 são reaproveitados por hash; Java e a extração global dos 41 ambientes não são reexecutados nesta revisão. IFC2SB e Kiavarz foram executados novamente na cozinha. As avaliações CGAL continuam entradas verificadas. Os GUIDs únicos ligam o complemento às identidades existentes do grafo principal.</p>
<p>O arquivo final preserva, byte a byte, o grafo histórico de 117.591 triplas como prefixo e contém {integration['triplas_uniao_atual']} triplas na união reaberta. A nova consulta recupera nove esquadrias distintas, incluindo a JA-09 pendente, além de permitir consultar dez candidatos internos e três componentes. As consultas antigas permanecem históricas; a consulta atual percorre <code>con:esquadriaAssociada</code>.</p>
<p><a href="rdf_principal/Notebook1_Grafo_Completo_v08.zip">Grafo completo compactado</a> · <a href="rdf_principal/Consultar_Cozinha_Atual_v08.rq">Consulta atual</a> · <a href="rdf_principal/Consulta_Cozinha_Atual_v08.csv">Resposta</a> · <a href="conferencia/Conferencia_Esquadrias_Caso_a_Caso.csv">Comparação completa em CSV</a>.</p>
<h2>Fontes e função de cada método</h2><ul><li>Bonduel et al. (2018), IFCtoLBD: conversão semântica anterior preservada. <a href="https://ceur-ws.org/Vol-2159/04paper.pdf">Artigo</a>.</li><li>Fichter et al. (2021), adaptação parcial IFC2SB: recortes e ancestralidade. <a href="https://doi.org/10.26868/25222708.2021.30156">DOI</a>.</li><li>Kiavarz et al. (2023): projeção/interseção de faces e sondas, com adaptações registradas. <a href="https://doi.org/10.3390/buildings13020350">DOI</a>.</li><li>Krijnen et al. (2020): resultados CGAL parciais, reaproveitados como diagnóstico. <a href="https://doi.org/10.46421/2706-6568.37.2020.paper008">DOI</a>.</li><li>Lilis et al. (2026): comparação opcional; Alg. 4/alpha wrap ausente. <a href="https://doi.org/10.1016/j.autcon.2026.106840">DOI</a>.</li><li>Zhang et al. (2018): geometria no RDF/GEOM. <a href="https://doi.org/10.3233/SW-180297">DOI</a>. Orquestração, inventário de cobertura, ligação dos acessórios, referência documental e avaliação são rotinas específicas deste estudo.</li></ul></html>'''
    (out/'Relatorio_Consolidacao_Cozinha_v08.html').write_text(doc,encoding='utf8')
    print('Figuras e relatório produzidos.');return audit['metricas']
