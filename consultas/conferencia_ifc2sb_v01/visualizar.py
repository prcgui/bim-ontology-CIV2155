"""Visualização de malhas IFC para conferência interna; não infere relações.
Leitura XYZ conforme IfcOpenShell/geometry_processing; corte e gráficos
são rotinas de apresentação específicas do estudo, não algoritmos do artigo.
"""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

def section(v,f,z):
    """Corte ilustrativo por interpolação linear nas arestas das malhas."""
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

LABELS={'evidencia_geometrica_de_coincidencia':'Recorte coincidente',
 'coincidencia_com_interpenetracao_parede_ambiente':'Recorte coincidente + sinal global na parede bruta',
 'sem_intersecao_de_face_no_criterio':'Sem interseção pelo critério',
 'fora_do_ambiente_por_separacao_bbox':'Separada da cozinha'}

def draw(out):
    out=Path(out);d=json.loads((out/'Conferencia_Geometrica_Cozinha.json').read_text(encoding='utf8'))
    figs=out/'figuras';figs.mkdir(exist_ok=True)
    def load(g):
        a=np.load(out/'malhas'/f'{g}.npz');return a['vertices'],a['faces']
    rv,rf=load(d['ambiente']);plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    blue='#176581';grey='#666b72';orange='#c26611';green='#478649'
    # Mesma escala e referencial por caso; o corte é escolhido pelo Z da abertura.
    for r in d['casos']:
        ov,of=load(r['abertura']);wv,wf=load(r['parede']);fv,ff=load(r['preenchimento'])
        z=float((ov[:,2].min()+ov[:,2].max())/2)
        fig,ax=plt.subplots(figsize=(7.2,5.4))
        for v,f,c,lw in [(wv,wf,grey,1.6),(rv,rf,blue,2.3),(ov,of,orange,2.8),(fv,ff,green,1.2)]:
            lines=section(v,f,z)
            if lines:ax.add_collection(LineCollection(lines,colors=c,linewidths=lw))
        mid=(ov[:,:2].min(0)+ov[:,:2].max(0))/2;span=np.maximum(ov[:,:2].ptp(0) if hasattr(ov[:,:2],'ptp') else np.ptp(ov[:,:2],axis=0),[2.3,2.3])
        # A escala de detalhe cobre a abertura com margem, sem ajustar as formas.
        ax.set_xlim(mid[0]-span[0]/2-.65,mid[0]+span[0]/2+.65)
        ax.set_ylim(mid[1]-span[1]/2-.65,mid[1]+span[1]/2+.65)
        ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_xlabel('X do projeto (m)');ax.set_ylabel('Y do projeto (m)')
        ax.set_title(r['codigo']+' · '+r['nome_preenchimento']+' · Z = '+f'{z:.3f} m',loc='left',fontsize=13,pad=11)
        fig.text(.13,.08,'Estado anterior: '+LABELS.get(r['estado'],r['estado']),fontsize=8.5)
        fig.text(.13,.045,f"Distância mínima abertura–cozinha: {r['distancia_abertura_cozinha_m']:.6f} m | Decisão arquitetônica: pendente",fontsize=8.5)
        ax.legend(handles=[Line2D([0],[0],color=blue,lw=2,label='IfcSpace: corte'),Line2D([0],[0],color=grey,lw=2,label='Parede com vazios'),Line2D([0],[0],color=orange,lw=2,label='Abertura'),Line2D([0],[0],color=green,lw=2,label='Preenchimento')],fontsize=8,loc='best',framealpha=.95)
        fig.subplots_adjust(left=.13,right=.97,top=.89,bottom=.19)
        fig.savefig(figs/(r['codigo']+'.png'),dpi=165);plt.close(fig)
    # Comparação de volumes nas dez paredes com sinal bruto positivo.
    selected=[w for w in d['paredes'] if w['volume_bruto_cozinha_m3']>1e-8]
    fig,ax=plt.subplots(figsize=(7.2,5.3));y=np.arange(len(selected));bar=.36
    ax.barh(y-bar/2,[w['volume_bruto_cozinha_m3'] for w in selected],height=bar,color='#dba76d',label='Geometria usada no recorte (bruta)')
    ax.barh(y+bar/2,[w['volume_com_vazios_cozinha_m3'] for w in selected],height=bar,color='#78529a',label='Com subtração de aberturas')
    ax.set_yticks(y,[w['codigo'] for w in selected]);ax.invert_yaxis();ax.set_xlabel('Volume de interseção com a cozinha (m³)')
    ax.set_title('Interseção global: qual geometria foi comparada?',loc='left',fontsize=12,pad=15)
    ax.grid(axis='x',alpha=.2);ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(figs/'Comparacao_Volumes_Paredes.png',dpi=180);plt.close(fig)
    # Galeria navegável com todos os casos e métricas, sem escolhas manuais de vínculo.
    esc=lambda a:html.escape(str(a))
    doc='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Conferência geométrica da cozinha</title><style>body{font:16px/1.5 Arial;background:#f5f3ee;color:#24384a;margin:0}main{max-width:1150px;margin:auto;padding:28px}h1{font-size:30px}h2{font-size:23px}article{background:white;border:1px solid #ddd;padding:22px;margin:22px 0;border-radius:8px}img{width:100%;height:auto;max-width:850px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}code{word-break:break-all;font-size:13px}.note{border-left:5px solid #c26611;padding:15px;background:#fff5e8}a{color:#176581}</style><main><h1>Conferência geométrica da cozinha</h1><p>CIV2155 · FNDE Tipo 2 · ARQ-DTV R03 · 29/10/2026</p><p class="note">Conferência interna do mesmo IFC com IfcOpenShell/OpenCascade. As figuras mostram cortes das malhas, não uma planta validada. A decisão arquitetônica permanece pendente. O IFC e o RDF anterior foram preservados.</p>'''
    doc+='<p><a href="Conferencia_Geometrica_Cozinha.json">Registros completos</a> · <a href="Casos_Arquitetonicos_Cozinha.csv">24 casos em CSV</a> · <a href="Relatorio_Conferencia_Geometrica_IFC2SB_v01.pdf">Relatório em PDF</a></p>'
    doc+='<h2>Geometria bruta e geometria com vazios</h2><p>As interseções globais são comparadas após nova leitura do IFC. Não se altera o critério anterior nem se regrava o modelo.</p><img src="figuras/Comparacao_Volumes_Paredes.png" alt="Comparação dos volumes globais nas paredes">'
    doc+='<h2>Casos individuais</h2><p>'+' · '.join('<a href="#'+r['codigo']+'">'+r['codigo']+'</a>' for r in d['casos'])+'</p>'
    for r in d['casos']:
        doc+='<article id="'+r['codigo']+'"><h2>'+r['codigo']+' · '+esc(r['nome_preenchimento'])+'</h2><p>'+esc(LABELS.get(r['estado'],r['estado']))+'</p><a href="figuras/'+r['codigo']+'.png"><img src="figuras/'+r['codigo']+'.png" alt="Corte das malhas do caso '+r['codigo']+'"></a><table>'
        for label,key in [('Parede (GUID)','parede'),('Abertura (GUID)','abertura'),('Preenchimento (GUID)','preenchimento'),('Classe do preenchimento','classe_preenchimento'),('Volume global bruto (m³)','volume_intersecao_ambiente_parede_m3'),('Volume global com vazios (m³)','volume_intersecao_parede_com_vazios_m3'),('Volume local com vazios, na abertura (m³)','volume_intersecao_com_vazios_na_abertura_m3'),('Área do recorte coincidente anterior (m²)','area_coincidente_cozinha_m2'),('Distância mínima abertura–cozinha (m)','distancia_abertura_cozinha_m'),('Fração volumétrica do preenchimento na cozinha','fracao_volumetrica_na_cozinha'),('Condição para aceitar a relação','condicao_para_aceitar')]:
            value=r[key];doc+='<tr><th>'+label+'</th><td>'+esc(f'{value:.9g}' if isinstance(value,float) else value)+'</td></tr>'
        doc+='</table><p class="note">'+esc(r['alcance_do_sinal_anterior'])+'. O corte XY é somente ilustração em uma altura. A análise quantitativa é 3D.</p></article>'
    doc+='<h2>Fontes e natureza do código</h2><p>Adaptação anterior: <a href="https://doi.org/10.26868/25222708.2021.30156">Fichter et al. (2021)</a>; <a href="https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad">IFC2SB dos autores</a>. A comparação e a visualização desta conferência são código específico do estudo, apoiado na <a href="https://docs.ifcopenshell.org/ifcopenshell/geometry_settings.html#disable-opening-subtractions">documentação técnica do IfcOpenShell</a>. Não correspondem a um novo método publicado nem a validação externa.</p></main></html>'
    (out/'Conferencia_Geometrica_Cozinha.html').write_text(doc,encoding='utf8')
    print('25 figuras e galeria com 24 casos geradas; sem alteração de relações.')

if __name__=='__main__':
    import sys
    draw(sys.argv[1])
