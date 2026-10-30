"""Desenha recortes reais do RDF em caixas, como nas figuras da apresentação.

RDFLib lê as triplas; Matplotlib desenha recursos, valores e predicados.
O arranjo é do estudo, sem significado de posição física ou adjacência.
https://rdflib.readthedocs.io/en/latest/intro_to_graphs/
https://matplotlib.org/3.10.7/users/explain/text/annotations.html
Uso: python codigo/visualizar_rdf.py resultados/Arquitetura_Analisada.zip resultados/grafo_rdf
"""
from pathlib import Path
import zipfile,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from rdflib import Graph,Namespace,RDF,RDFS,URIRef

BOT=Namespace('https://w3id.org/bot#')
P=Namespace('http://lbd.arch.rwth-aachen.de/props#')
C=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/analise#')
INK,EDGE='#16324F','#8294A4'
COLORS={'site':'#E3EAF1','building':'#D9E8F7','storey':'#CFEBE3','space':'#FFF0CF',
        'literal':'#F0F3F6','result':'#DCEAF7','interface':'#E2F0E8','cut':'#E8E2F2','element':'#F9E7D6'}

def canvas(title,subtitle,w,h):
    fig,ax=plt.subplots(figsize=(w,h));fig.patch.set_facecolor('white')
    fig.subplots_adjust(left=.025,right=.975,top=.91,bottom=.065)
    fig.text(.04,.965,title,fontsize=22,weight='bold',color=INK,va='top')
    fig.text(.04,.93,subtitle,fontsize=11,color='#526779',va='top')
    ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off');return fig,ax

def box(ax,x,y,text,kind,w=25,h=12,size=12):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.25,rounding_size=0.6',
        linewidth=1,facecolor=COLORS[kind],edgecolor=INK,zorder=3))
    ax.text(x,y,text,ha='center',va='center',color=INK,fontsize=size,zorder=4)

def arrow(ax,a,b,label=None,label_xy=None,size=10):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,linewidth=1.1,color=EDGE,zorder=1))
    if label:
        x,y=label_xy or ((a[0]+b[0])/2,(a[1]+b[1])/2)
        ax.text(x,y,label,ha='center',va='center',fontsize=size,color=INK,
                bbox={'facecolor':'white','edgecolor':'none','pad':2},zorder=2)

def save(fig,out,name,note):
    fig.text(.04,.025,note,fontsize=9,color='#526779',va='bottom')
    for suffix in ['png','svg']:fig.savefig(out/(name+'.'+suffix),dpi=180,facecolor='white')
    plt.close(fig)

def gerar_figuras(grafo_zip,saida):
    """Lê o resultado entregue e grava três figuras e seus recortes Turtle."""
    source=Path(grafo_zip);out=Path(saida);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source) as z:g=Graph().parse(data=z.read('Arquitetura_Analisada.ttl'),format='turtle')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
    def value(s,p):
        v=g.value(s,p,any=False)
        if v is None:raise ValueError(f'Propriedade ausente: {s} {p}')
        return str(v)
    def unique(cls):
        values=list(g.subjects(RDF.type,cls))
        if len(values)!=1:raise ValueError('Era esperado um recurso de '+str(cls))
        return values[0]
    def subset_save(subset,name):
        if not all(t in g for t in subset):raise ValueError('O desenho contém relação ausente no grafo.')
        for prefix,ns in [('bot',BOT),('props',P),('civ',C),('rdfs',RDFS)]:subset.bind(prefix,ns)
        subset.serialize(out/name,format='turtle')
    site,building=unique(BOT.Site),unique(BOT.Building)
    spaces=sorted(g.subjects(RDF.type,BOT.Space),key=lambda s:(value(s,RDFS.label),value(s,P.longNameIfcSpatialElement_attribute_simple)))
    storeys=sorted(g.objects(building,BOT.hasStorey),key=lambda s:value(s,RDFS.label))
    active=[s for s in storeys if any(g.objects(s,BOT.hasSpace))]
    if len(active)!=1 or set(g.objects(active[0],BOT.hasSpace))!=set(spaces):
        raise ValueError('A organização espacial difere da estrutura representada nesta figura.')
    floor=active[0]
    kitchens=[s for s in spaces if value(s,P.longNameIfcSpatialElement_attribute_simple)=='COZINHA']
    if len(kitchens)!=1:raise ValueError('Cozinha não identificada de forma unívoca.')
    kitchen=kitchens[0]

    overview=Graph()
    for s in [site,building,*storeys,*spaces]:
        for p in [RDF.type,RDFS.label,P.longNameIfcSpatialElement_attribute_simple]:
            for o in g.objects(s,p):overview.add((s,p,o))
    for p in [BOT.hasBuilding,BOT.hasStorey,BOT.hasSpace]:
        for t in g.triples((None,p,None)):overview.add(t)
    subset_save(overview,'Organizacao_Espacial.ttl')
    fig,ax=canvas('Organização espacial dos '+str(len(spaces))+' ambientes',
        'Notebook 1 · FNDE Tipo 2 R03 | Recorte das '+f'{len(g):,}'.replace(',','.')+' triplas entregues',18,17)
    box(ax,15,96,'TERRENO\n'+value(site,RDFS.label),'site',w=23,h=6,size=11)
    box(ax,52,96,'EDIFICAÇÃO\n'+value(building,RDFS.label),'building',w=37,h=6,size=11)
    arrow(ax,(27,96),(33,96),'bot:hasBuilding',(30,99.8),9)
    box(ax,52,85,'PAVIMENTO · '+value(floor,RDFS.label)+'\n'+str(len(spaces))+' ambientes vinculados','storey',w=36,h=6,size=11)
    arrow(ax,(52,92.7),(52,88.3),'bot:hasStorey',(62,90.5),9)
    for other in storeys:
        if other!=floor:
            count=len(list(g.objects(other,BOT.hasSpace)))
            box(ax,86,85,'PAVIMENTO · '+value(other,RDFS.label)+'\n'+str(count)+' ambientes vinculados','storey',w=24,h=6,size=10)
            arrow(ax,(69,92.7),(86,88.3),'bot:hasStorey',(84,92.5),9)
    ax.plot([52,52],[81.7,78],color=EDGE,linewidth=1);ax.plot([2,77],[78,78],color=EDGE,linewidth=1)
    ax.text(50,75.8,'Cada seta abaixo representa bot:hasSpace (pavimento → ambiente).',ha='center',fontsize=11,color=INK)
    per_column=(len(spaces)+3)//4
    for col in range(4):
        x=14+col*25;chunk=spaces[col*per_column:(col+1)*per_column]
        if not chunk:continue
        ys=[70-i*6 for i in range(len(chunk))];ax.plot([x-12,x-12],[78,ys[-1]],color=EDGE,linewidth=1)
        for s,y in zip(chunk,ys):
            name=textwrap.fill(value(s,P.longNameIfcSpatialElement_attribute_simple),width=24)
            box(ax,x,y,value(s,RDFS.label)+' · '+name,'space',w=20.7,h=4.9,size=9)
            arrow(ax,(x-12,y),(x-10.6,y))
    save(fig,out,'Organizacao_Espacial','Fonte: Arquitetura_Analisada.ttl. Caixas são recursos RDF. As posições do desenho não indicam localização física ou adjacência.')

    identity=Graph()
    for s,p,o in overview:
        if s in [site,building,floor,kitchen] and (p!=BOT.hasSpace or o==kitchen) and (p!=BOT.hasStorey or o==floor):identity.add((s,p,o))
    identity_props=[RDF.type,RDFS.label,P.longNameIfcSpatialElement_attribute_simple,P.category_property_simple,P.globalIdIfcRoot_attribute_simple]
    for p in identity_props:
        for o in g.objects(kitchen,p):identity.add((kitchen,p,o))
    subset_save(identity,'Cozinha_Identidade.ttl')
    fig,ax=canvas('Como ler o RDF: o ambiente COZINHA','Notebook 1 atual | Recursos, relações e valores, no mesmo estilo da apresentação',16,9)
    box(ax,15,86,'TERRENO\n'+value(site,RDFS.label),'site',w=25,h=12,size=12)
    box(ax,15,55,'EDIFICAÇÃO\n'+textwrap.fill(value(building,RDFS.label),width=20),'building',w=25,h=15,size=11)
    box(ax,15,21,'PAVIMENTO\n'+value(floor,RDFS.label),'storey',w=25,h=12,size=12)
    arrow(ax,(15,79.5),(15,63),'bot:hasBuilding',(15,72),11)
    arrow(ax,(15,47),(15,27.5),'bot:hasStorey',(15,37),11)
    box(ax,46,21,'AMBIENTE\nCOZINHA','space',w=22,h=13,size=14)
    arrow(ax,(27.7,21),(34.7,21),'bot:hasSpace',(31,30),11)
    fields=[('rdf:type','bot:Space',None,88),('nome',value(kitchen,RDFS.label),RDFS.label,69),
            ('nome descritivo',value(kitchen,P.longNameIfcSpatialElement_attribute_simple),P.longNameIfcSpatialElement_attribute_simple,50),
            ('categoria',value(kitchen,P.category_property_simple),P.category_property_simple,31),
            ('GlobalId',value(kitchen,P.globalIdIfcRoot_attribute_simple),P.globalIdIfcRoot_attribute_simple,12)]
    for label,txt,p,y in fields:
        box(ax,84,y,txt,'literal' if p else 'space',w=30,h=11,size=12 if label!='GlobalId' else 10)
        arrow(ax,(57.4,23),(68.5,y),label,(63,y),10)
    save(fig,out,'Cozinha_Identidade','Fonte: Arquitetura_Analisada.ttl. Recursos em caixas coloridas; valores textuais em cinza. Correspondência dos predicados no README.')

    result=g.value(kitchen,C.resultado)
    doors=[e for e in g.objects(result,C.esquadriaAssociada) if str(g.value(e,RDFS.label))=='PA2']
    if len(doors)!=1:raise ValueError('PA2 não identificada de forma unívoca na cozinha.')
    fill=doors[0];paths=[]
    for cut in g.subjects(C.preenchimento,fill):
        interface=g.value(cut,C.interfaceFonte)
        if (result,C.interface,interface) in g and bool(g.value(cut,C.qualificada)):paths.append((str(cut),cut,interface))
    if not paths:raise ValueError('Recorte qualificado não encontrado.')
    _,cut,interface=sorted(paths)[0]
    wall=g.value(interface,C.paredeHospedeira);opening=g.value(cut,C.aberturaFonte)
    geometry=Graph()
    links=[(kitchen,C.resultado,result),(result,C.ambiente,kitchen),(result,C.interface,interface),
           (result,C.esquadriaAssociada,fill),(interface,C.paredeHospedeira,wall),
           (cut,C.interfaceFonte,interface),(cut,C.aberturaFonte,opening),(cut,C.preenchimento,fill)]
    for t in links:
        if t not in g:raise ValueError('Relação ausente no RDF: '+str(t))
        geometry.add(t)
    for s in [kitchen,result,interface,cut,wall,opening,fill]:
        for p in [RDF.type,RDFS.label,C.nome,C.estado,C.quantidadeEsquadrias,C.areaM2,C.qualificada,P.globalIdIfcRoot_attribute_simple]:
            for o in g.objects(s,p):geometry.add((s,p,o))
    subset_save(geometry,'Cozinha_Associacao_PA2.ttl')
    fig,ax=canvas('RDF da cozinha: da associação à abertura PA2','Notebook 1 atual | Um caminho real entre ambiente, resultado, interface, parede, abertura e porta',18,10)
    box(ax,15,89,'AMBIENTE\nCOZINHA','space',w=25,h=13)
    box(ax,50,89,'RESULTADO\n'+str(g.value(result,C.estado)).replace('_',' '),'result',w=27,h=13,size=11)
    iface_id=str(interface).rsplit('/',1)[-1]
    suffix='_'.join(iface_id.split('_')[-3:])
    box(ax,85,89,'INTERFACE\n'+suffix,'interface',w=25,h=13)
    arrow(ax,(27.8,89),(36.2,89),'civ:resultado',(32,98),10)
    arrow(ax,(63.8,89),(72.2,89),'civ:interface',(68,98),10)
    box(ax,15,57,value(result,C.quantidadeEsquadrias)+' esquadrias','literal',w=25,h=12)
    box(ax,50,57,'RECORTE\n'+str(cut).rsplit('/',1)[-1],'cut',w=25,h=13)
    box(ax,85,57,'PAREDE\n'+value(wall,RDFS.label),'element',w=25,h=13)
    arrow(ax,(45,82),(27.8,57),'civ:quantidadeEsquadrias',(30,70),10)
    arrow(ax,(85,82.2),(85,63.8),'civ:paredeHospedeira',(85,73),10)
    arrow(ax,(62.8,62),(74,82),'civ:interfaceFonte',(66.5,72),10)
    box(ax,15,22,'PORTA\n'+value(fill,RDFS.label),'element',w=25,h=13)
    op_guid=value(opening,P.globalIdIfcRoot_attribute_simple)
    box(ax,50,22,'ABERTURA IFC\n'+op_guid[:11]+'…','element',w=25,h=13,size=11)
    area=float(g.value(cut,C.areaM2))
    box(ax,85,22,f'{area:.4f}'.replace('.',',')+' m²','literal',w=25,h=12)
    arrow(ax,(50,50.2),(50,28.8),'civ:aberturaFonte',(50,40),10)
    arrow(ax,(38,50),(27.8,28.8),'civ:preenchimento',(29.5,40),10)
    arrow(ax,(62.8,53),(75,28.5),'civ:areaM2',(75,40),10)
    ax.plot([50,50,1,1],[82,77,77,22],color=EDGE,linewidth=1.1,zorder=1)
    arrow(ax,(1,22),(2.2,22),'civ:esquadriaAssociada',(19,78.3),10)
    save(fig,out,'Cozinha_Associacao_PA2','Fonte: Arquitetura_Analisada.ttl. Exemplo de um recorte qualificado; a cozinha tem nove associações. IDs abreviados e área arredondada apenas na figura.')
    print('Figuras RDF geradas a partir de',len(g),'triplas:',out)
    return {'triplas_origem':len(g),'ambientes':len(spaces),'figuras':['Organizacao_Espacial','Cozinha_Identidade','Cozinha_Associacao_PA2']}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('grafo_zip');parser.add_argument('saida');args=parser.parse_args()
    gerar_figuras(args.grafo_zip,args.saida)
