"""Figuras científicas derivadas das malhas XYZ do IFC, sem editar imagens.
O corte horizontal e a projeção XY apoiam inspeção; não inferem relações RDF.
"""
from pathlib import Path
import json,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
KITCHEN='3UFjAT4k55zg_Pqo6VMw5l'

def sections(v,f,z):
    lines=[]
    for tri in v[f]:
        d=tri[:,2]-z
        if np.all(d>1e-9) or np.all(d<-1e-9) or np.all(abs(d)<1e-9):continue
        points=[]
        for a,b in [(0,1),(1,2),(2,0)]:
            if abs(d[a])<1e-9:points.append(tri[a,:2])
            if d[a]*d[b]<0:points.append((tri[a]+(tri[b]-tri[a])*(-d[a])/(d[b]-d[a]))[:2])
        unique=[]
        for p in points:
            if all(np.linalg.norm(p-q)>1e-8 for q in unique):unique.append(p)
        if len(unique)==2 and np.linalg.norm(unique[0]-unique[1])>1e-8:lines.append(unique)
    return lines

def draw(case_path,cache_path,out):
    case=json.loads(Path(case_path).read_text(encoding='utf8'));cache=Path(cache_path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    inv=json.loads((cache/'inventario_geometria.json').read_text(encoding='utf8'))
    rec={r['guid']:r for r in inv['entidades']};loaded={}
    def load(guid):
        if guid not in loaded:
            z=np.load(cache/rec[guid]['cache']);loaded[guid]=(z['vertices'],z['faces'])
        return loaded[guid]
    vr,fr=load(KITCHEN);color='#176581';orange='#c06516';red='#b43736';purple='#795498'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':16,'axes.labelsize':11})
    def setup(ax):
        ax.set_aspect('equal');ax.set_xlabel('X do projeto (m)');ax.set_ylabel('Y do projeto (m)');ax.grid(alpha=.12)
        ax.spines[['top','right']].set_visible(False)
    def label(ax,xy,text,c,offset=(8,7)):
        ax.annotate(text,xy,xytext=offset,textcoords='offset points',color=c,fontsize=10,fontweight='bold',
          bbox={'facecolor':'white','edgecolor':c,'alpha':.94,'boxstyle':'round,pad=.25'},
          arrowprops={'arrowstyle':'-','color':c,'lw':.7})
    fig,ax=plt.subplots(figsize=(9.5,10),layout='constrained')
    for r in case['paredes']:
        v,f=load(r['guid']);qualified=r['codigo'].startswith('P')
        c=orange if qualified else '#aab0b6';lw=2 if qualified else .7
        if r['situacao_N1']=='contato_com_intersecao_volumetrica':c=purple
        lines=sections(v,f,1.2)
        if lines:ax.add_collection(LineCollection(lines,colors=c,linewidths=lw,alpha=.85))
    ax.add_collection(LineCollection(sections(vr,fr,1.2),colors=color,linewidths=2.4))
    ax.text(*vr.mean(0)[:2],'COZINHA\nIfcSpace #132558',ha='center',va='center',color=color,fontsize=14,fontweight='bold')
    # Rótulos derivados dos pontos das interfaces registradas, não de desenho manual.
    relpath=Path(case_path).parent/'relacoes_origem_cozinha.json'
    if relpath.exists():
        pairs=json.loads(relpath.read_text(encoding='utf8'))
        for r in case['paredes']:
            if not r['codigo'].startswith('P'):continue
            p=next((p for p in pairs if p['parede']==r['guid']),None)
            if p:
                w=next((s['wkt_estrito'] for s in p['superficies'] if s['area_estrita_m2']>1e-6),'')
                xyz=np.asarray([float(x) for x in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',w)]).reshape(-1,3)
                if len(xyz):label(ax,xyz.mean(0)[:2],r['codigo'],orange,(-30,8) if xyz.mean(0)[0]<vr.mean(0)[0] else (8,8))
    ax.set_xlim(vr[:,0].min()-1,vr[:,0].max()+1);ax.set_ylim(vr[:,1].min()-1,vr[:,1].max()+1)
    ax.set_title('Cozinha: corte das malhas IFC em Z = 1,20 m',loc='left',pad=20)
    setup(ax)
    handles=[Line2D([0],[0],color=color,lw=2,label='Limite da malha IfcSpace'),Line2D([0],[0],color=orange,lw=2,label='Parede com aresta derivada no RDF'),Line2D([0],[0],color=purple,lw=2,label='Contato com sobreposição volumétrica'),Line2D([0],[0],color='#aab0b6',lw=1,label='Demais paredes pré-selecionadas')]
    ax.legend(handles=handles,loc='upper left',bbox_to_anchor=(0,-.10),frameon=False,fontsize=10)
    fig.savefig(out/'01_Cozinha_Corte_IFC.png',dpi=180,bbox_inches='tight');plt.close(fig)
    # Extensão inteira da parede compartilhada P01 e todas as suas aberturas.
    wall=next(r for r in case['paredes'] if r['codigo']=='P01');vw,fw=load(wall['guid'])
    fig,ax=plt.subplots(figsize=(9.5,10),layout='constrained')
    edges=vw[fw][:,[0,1,2,0],:2]
    for edge in edges:ax.plot(edge[:,0],edge[:,1],color='#969da4',lw=.65,alpha=.75)
    ax.add_collection(LineCollection(sections(vr,fr,1.2),colors=color,linewidths=2.4))
    ax.text(*vr.mean(0)[:2],'COZINHA',ha='center',va='center',color=color,fontsize=14,fontweight='bold')
    for i,r in enumerate(case['cadeias']):
        if r['parede_codigo']!='P01':continue
        vo,fo=load(r['abertura_guid']);outside=r['abertura_vs_cozinha']['teste_3d']=='fora_do_filtro_espacial_2mm'
        c=red if outside else orange
        for edge in vo[fo][:,[0,1,2,0],:2]:ax.plot(edge[:,0],edge[:,1],color=c,lw=1.3)
        gap=r['abertura_vs_cozinha'].get('separacao_caixas_XYZ_m',[0,0,0])[1]
        text=r['codigo']+' · '+r['nome_preenchimento']+(f'\nseparação em Y: {gap:.3f} m' if outside else '')
        label(ax,vo.mean(0)[:2],text,c,(-125,8) if i%2==0 else (15,8))
    allv=np.vstack([vr,vw]);ax.set_xlim(allv[:,0].min()-1.5,allv[:,0].max()+1.5);ax.set_ylim(allv[:,1].min()-1,allv[:,1].max()+1)
    ax.set_title('Parede P01: a cadeia RDF percorre sua extensão inteira',loc='left',pad=20)
    setup(ax)
    ax.legend(handles=[Line2D([0],[0],color=color,lw=2,label='Cozinha: corte do IfcSpace'),Line2D([0],[0],color='#969da4',lw=1,label='Parede P01: projeção de todas as faces'),Line2D([0],[0],color=orange,lw=2,label='Abertura: requer análise do vínculo'),Line2D([0],[0],color=red,lw=2,label='Abertura separada da cozinha em Y')],loc='upper left',bbox_to_anchor=(0,-.10),frameon=False,fontsize=10)
    fig.savefig(out/'02_Parede_Compartilhada_Aberturas.png',dpi=180,bbox_inches='tight');plt.close(fig)
    print('Figuras geradas das malhas do IFC; não constituem padrão-ouro independente.')

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--dados',required=True);p.add_argument('--cache',required=True);p.add_argument('--saida',required=True)
    a=p.parse_args();draw(a.dados,a.cache,a.saida)
