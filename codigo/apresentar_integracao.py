"""Figuras dos resultados primários da integração, extraídas das tabelas/RDF."""
from pathlib import Path
import json,csv,zipfile
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rdflib import Dataset,Namespace,URIRef,Literal,RDF
from visualizar_rdf import canvas,box,arrow,save,EDGE

def gerar_figuras_integracao(resultados):
    out=Path(resultados);summary=json.loads((out/'Resumo_Integracao.json').read_text(encoding='utf8'))
    rows=list(csv.DictReader((out/'Relacoes_Espaciais.csv').open(encoding='utf-8-sig')))
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
    labels=['SMT · estrutura metálica','SCO · estrutura de concreto'];left=[0,0]
    for state,name,color in [('adjacente','Contato por face','#6a9d92'),('intersecciona','Interseção parcial','#397b9e'),('contido','Contenção','#cc985c')]:
        values=[sum(r['modelo']==key and r['estado']==state for r in rows) for key in ['smt','sco']]
        bars=ax.barh(labels,values,left=left,label=name,color=color)
        for bar,value in zip(bars,values):
            if value>=20:ax.text(bar.get_x()+bar.get_width()/2,bar.get_y()+bar.get_height()/2,str(value),ha='center',va='center',color='white',weight='bold')
            elif value:ax.annotate(str(value),xy=(bar.get_x()+bar.get_width()/2,bar.get_y()+bar.get_height()/2),xytext=(0,45),textcoords='offset points',ha='center',va='bottom',arrowprops={'arrowstyle':'-','color':'#666666'},color='#333333')
        left=[a+b for a,b in zip(left,values)]
    ax.set_xlabel('Pares ambiente–elemento estrutural');ax.set_xlim(0,max(left)*1.15)
    ax.set_title('Relações geométricas entre arquitetura e estruturas',loc='left',weight='bold')
    for i,total in enumerate(left):ax.text(total+10,i,str(total),va='center')
    ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.18),ncol=3,frameon=False);ax.spines[['top','right']].set_visible(False)
    for suffix in ['png','svg']:fig.savefig(out/('Relacoes_Por_Modelo.'+suffix),dpi=180)
    plt.close(fig)
    candidates=[r for r in rows if r['nome_ambiente']=='COZINHA' and r['modelo']=='sco' and r['estado']=='adjacente']
    if not candidates:raise ValueError('Não há exemplo de contato SCO–cozinha para a figura selecionada.')
    chosen=sorted(candidates,key=lambda r:(-float(r['area_contato_m2']),r['elemento']))[0]
    ids=list(csv.DictReader((out/'Identidades_Modelos.csv').open(encoding='utf-8-sig')))
    index={(r['modelo'],r['guid']):r for r in ids}
    room=URIRef(index[('arquitetura',chosen['ambiente'])]['uri']);element=URIRef(index[('sco',chosen['elemento'])]['uri'])
    base='https://github.com/prcgui/bim-ontology-CIV2155/';N=Namespace(base+'vocab/integracao#');B=Namespace(base+'id/integracao/')
    BOT=Namespace('https://w3id.org/bot#');PROV=Namespace('http://www.w3.org/ns/prov#')
    relation=B['relacao/sco/'+chosen['ambiente']+'/'+chosen['elemento']]
    with zipfile.ZipFile(out/'Integracao_Arquitetura_Estrutura.zip') as z:
        ds=Dataset(default_union=True);ds.parse(data=z.read('Integracao_Arquitetura_Estrutura.nq'),format='nquads')
    selected=[(relation,N.ambiente,room),(relation,N.elementoEstrutural,element),
              (room,BOT.adjacentElement,element),(room,PROV.wasDerivedFrom,B['modelo/arquitetura']),
              (element,PROV.wasDerivedFrom,B['modelo/sco']),(relation,N.modelo,B['modelo/sco']),
              (relation,N.areaContatoM2,Literal(float(chosen['area_contato_m2'])))]
    if not all(t in ds for t in selected):raise ValueError('O exemplo desenhado não está integralmente no RDF integrado.')
    fig,ax=canvas('Arquitetura + estrutura no RDF: exemplo da cozinha',
        'Notebook 2 | Um vínculo medido, com identidade e origem de cada recurso preservadas',18,10)
    box(ax,15,80,'AMBIENTE\nCOZINHA\nbot:Space','space',w=25,h=15,size=12)
    box(ax,50,80,'RELAÇÃO ESPACIAL\nint:RelacaoEspacial','result',w=25,h=15,size=12)
    box(ax,85,80,chosen['classe_ifc']+'\n'+chosen['nome_elemento'],'element',w=25,h=15,size=12)
    arrow(ax,(37.2,80),(27.8,80),'int:ambiente',(32.5,90),10)
    arrow(ax,(62.8,80),(72.2,80),'int:elementoEstrutural',(68,90),10)
    ax.plot([15,15,85],[87.8,97,97],color=EDGE,linewidth=1)
    arrow(ax,(85,97),(85,87.8),'bot:adjacentElement',(50,99),10)
    box(ax,15,25,'MODELO\nARQUITETURA','building',w=25,h=15,size=12)
    box(ax,85,25,'MODELO\nESTRUTURA SCO','building',w=25,h=15,size=12)
    box(ax,50,25,f"{float(chosen['area_contato_m2']):.4f}".replace('.',',')+' m²\nÁrea de contato','literal',w=25,h=15,size=12)
    arrow(ax,(15,72.2),(15,32.8),'prov:wasDerivedFrom',(15,53),10)
    arrow(ax,(85,72.2),(85,32.8),'prov:wasDerivedFrom',(85,53),10)
    arrow(ax,(50,72.2),(50,32.8),'int:areaContatoM2',(50,53),10)
    arrow(ax,(62,72.2),(73,32.8),'int:modelo',(68,45),10)
    save(fig,out,'Grafo_Integracao_Cozinha','Fonte: Dataset integrado. Exemplo do maior contato SCO–cozinha no critério. Área arredondada apenas para exibição; não representa função ou conformidade estrutural.')
    return {'figuras':['Relacoes_Por_Modelo','Grafo_Integracao_Cozinha'],'exemplo':chosen}

if __name__=='__main__':
    import sys
    gerar_figuras_integracao(sys.argv[1])
