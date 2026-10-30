"""Apresenta uma projeção consultada do RDF, sem inventar relações gráficas."""
from pathlib import Path
import json,html
from collections import Counter
from rdflib import Graph,Namespace,RDF,RDFS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from exportar_hibrido import H,B,OLD

def run(out):
    out=Path(out);g=Graph().parse(out/'Cozinha_Interfaces_Hibridas_IFC2SB_Krijnen_Kiavarz_v01.ttl',format='turtle')
    q=(out/'Consultar_Cozinha_Interfaces_Aberturas.rq').read_text(encoding='utf8');rows=list(g.query(q))
    counts=Counter(r.interface for r in rows if r.recorte is not None);chosen=sorted(counts,key=lambda u:(-counts[u],str(u)))[0]
    subset=[r for r in rows if r.interface==chosen and r.recorte is not None]
    height=max(6,1.8+len(subset)*1.25);fig,ax=plt.subplots(figsize=(18,height));ax.set_xlim(0,18);ax.set_ylim(0,height);ax.axis('off')
    positions={};colors={'room':'#d9eef5','interface':'#e5f2dc','wall':'#f4e5d5','piece':'#f7f1cf','opening':'#e6e5f2','filling':'#dfedf0'}
    def box(key,x,y,title,subtitle,kind,width=2.65):
        positions[key]=(x,y,width,.72)
        ax.add_patch(FancyBboxPatch((x,y-.36),width,.72,boxstyle='round,pad=.08',facecolor=colors[kind],edgecolor='#315367',linewidth=.9))
        ax.text(x+width/2,y+.12,title,ha='center',va='center',fontsize=9.5,weight='bold')
        ax.text(x+width/2,y-.14,subtitle,ha='center',va='center',fontsize=8.3)
    def edge(a,b,label,vertical=False):
        x,y,w,h=positions[a];X,Y,W,Hh=positions[b]
        p=(x+w/2,y+h/2) if vertical else (x+w,y)
        e=(X+W/2,Y-Hh/2) if vertical else (X,Y)
        ax.add_patch(FancyArrowPatch(p,e,arrowstyle='-|>',mutation_scale=10,color='#42677b',linewidth=.9,connectionstyle='arc3,rad=0'))
        if vertical:ax.text(x+w/2+.12,(p[1]+e[1])/2,label,ha='left',fontsize=7.2)
        elif label:ax.text((p[0]+e[0])/2,(p[1]+e[1])/2+.12,label,ha='center',fontsize=7.2,bbox={'facecolor':'white','edgecolor':'none','pad':1})
    mid=height/2-.3
    iid=str(chosen).rsplit('/',1)[-1];wall=g.value(chosen,H.paredeHospedeira);wg=str(wall).rsplit('/',1)[-1]
    box('room',.1,mid,'Cozinha','IfcSpace · '+str(subset[0].ambiente).rsplit('/',1)[-1][:8],'room')
    box('interface',3.3,mid,'Interface geométrica',iid,'interface',3.0)
    box('wall',3.5,height-1.5,'Parede hospedeira','GlobalId · '+wg[:12]+'…','wall')
    edge('room','interface','interface\nCandidata');edge('interface','wall','paredeHospedeira',True)
    ax.text(6.65,mid+.7,'recortes de\nabertura',ha='center',fontsize=8,color='#284b60')
    for k,r in enumerate(subset):
        y=height-2.4-k*1.25
        key='p'+str(k);opening='o'+str(k);fill='f'+str(k)
        box(key,7.0,y,'Recorte local',str(r.recorte).rsplit('/',1)[-1],'piece',2.4)
        box(opening,10.5,y,'Abertura IFC',str(r.abertura).rsplit('/',1)[-1][:12]+'…','opening',2.4)
        box(fill,14,y,str(r.nome or 'Sem nome'),str(r.classe),'filling',2.7)
        edge('interface',key,'');edge(key,opening,'abertura');edge(opening,fill,'preenchimento')
    fig.suptitle('Cozinha: interface e aberturas consultadas no RDF híbrido',fontsize=16,weight='bold',y=.99)
    ax.text(.1,.15,'Qualificação geométrica experimental. Validação arquitetônica independente pendente.\nFonte: consulta ao arquivo Turtle; esta figura exibe um recorte do grafo.',fontsize=9,color='#435461')
    fig.tight_layout(rect=[0,.02,1,.95]);fig.savefig(out/'Grafo_RDF_Recorte_Interface.png',dpi=170,bbox_inches='tight');fig.savefig(out/'Grafo_RDF_Recorte_Interface.svg',bbox_inches='tight');plt.close(fig)
    data=json.loads((out/'Resultado_Hibrido_Kiavarz_v01.json').read_text(encoding='utf8'))
    reg=json.loads((out/'Registro_RDF_Hibrido_v01.json').read_text(encoding='utf8'))
    def tab(headers,values):return '<table><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in values)+'</table>'
    table=tab(['Interface','Parede','Área bruta m²','Sondas','Sinal CGAL global'],[[i['id'],i['codigo_parede'],f"{i['area_m2']:.6f}",i['sondas']['qualificacao_local'],i['sinal_global_cgal']] for i in data['interfaces']])
    openings=tab(['Preenchimento','Classe IFC','Recortes na interface','Estado no critério'],[[r['nome'],r['classe'],r['recortes_na_interface'],r['estado']] for r in data['avaliacao_aberturas']])
    text='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CIV2155 · Interfaces híbridas</title><style>body{font:16px/1.6 Segoe UI,sans-serif;max-width:1250px;margin:36px auto;padding:0 22px;color:#19384a}h1,h2{color:#14647b}section{background:#eef6f8;border-left:5px solid #33859b;padding:18px;margin:18px 0}table{border-collapse:collapse;width:100%;font-size:13px;margin:18px 0}td,th{padding:9px;border:1px solid #c6d8df;text-align:left;overflow-wrap:anywhere}th{background:#e7f1f4}img{width:100%;height:auto}a{color:#00698c}</style><h1>Interfaces da cozinha e recortes locais de aberturas</h1><p>Fluxo experimental: recortes IFC2SB + evidências CGAL + adaptação de operações de Kiavarz.</p><section><b>Resultado:</b> 14 interfaces apoiadas pelo critério geométrico, em dez paredes; 11 recortes associados a dez aberturas. Os dez preenchimentos incluem três IfcDoor, seis IfcWindow e um IfcWall. O papel de preenchimento não altera a classe IFC.</section><p>O RDF contém '''+str(reg['triplas_saida'])+''' triplas e conserva as 1.946 anteriores. A seleção de cada abertura depende do recorte da interface; a relação com a parede inteira não basta. As 24 avaliações, inclusive as negativas, permanecem registradas.</p><p><a href="Cozinha_Interfaces_Hibridas_IFC2SB_Krijnen_Kiavarz_v01.ttl">RDF completo</a> · <a href="Consultar_Cozinha_Interfaces_Aberturas.rq">Consulta SPARQL</a> · <a href="Consulta_Cozinha_Interfaces_Aberturas.csv">Tabela extraída do RDF</a></p><img src="Grafo_RDF_Recorte_Interface.png" alt="Recorte consultado do RDF: cozinha, interface, parede e aberturas"><h2>Interfaces</h2>'''+table+'''<h2>Todos os preenchimentos examinados</h2>'''+openings+'''<h2>Interpretação e limites</h2><p>As contagens de recortes e aberturas coincidem com o piloto anterior. A contribuição é a combinação operacional e rastreável, a conferência do contorno parental e o suporte por sondas/raios; não houve demonstração de maior acurácia arquitetônica. Onze faces ficaram fora da serialização poligonal de arestas retas. Todas as 14 interfaces mantiveram a qualificação para sondas de 0,1, 1 e 2 mm. São parâmetros experimentais, não tolerâncias normativas.</p><p>O sinal CGAL pertence à parede inteira. Não significa que cada abertura esteja em conflito. Não foram certificadas novas adjacências BOT, nem concluída a arquitetura dos 41 ambientes.</p><h2>Fontes</h2><p><a href="https://doi.org/10.3390/buildings13020350">Kiavarz et al. (2023), §§4.2.2–4.4 e Tabelas 4–5</a>; <a href="https://github.com/RWTH-E3D/IFC2SB">IFC2SB dos autores</a>; <a href="https://doi.org/10.5281/zenodo.3633653">código de Krijnen citado no artigo</a>. A Tabela 5 de Kiavarz contém pseudocódigo com chamadas incompatíveis com a API. As alterações seguem a <a href="https://shapely.readthedocs.io/en/stable/reference/shapely.intersection.html">documentação oficial do Shapely</a> e estão explicitadas no registro metodológico. Não foi confirmado um repositório específico com a implementação completa de Kiavarz.</p></html>'''
    (out/'Relatorio_Interfaces_Hibridas_v01.html').write_text(text,encoding='utf8')
    (out/'Registro_Visualizacao_RDF.json').write_text(json.dumps({'origem':'consulta SPARQL ao RDF gerado','interface':str(chosen),'linhas_exibidas':len(subset),'imagem':'Grafo_RDF_Recorte_Interface.png','imagem_nao_substitui_dados_rdf':True},ensure_ascii=False,indent=2),encoding='utf8')
    print('Figura extraída do RDF:',iid,len(subset),'recortes')
if __name__=='__main__':
    import sys
    run(sys.argv[1])
