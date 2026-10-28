"""Gera figuras a partir do grafo corrigido, sem alterar suas triplas.

Uso: python consultas/10_visualizacao_grafo.py caminho/do/grafo.ttl
Dependências: RDFLib 7.1.4 e Matplotlib 3.10.7.
Base técnica: RDFLib, Navigating Graphs; Matplotlib, Annotations.
https://rdflib.readthedocs.io/en/latest/intro_to_graphs/
https://matplotlib.org/3.10.7/users/explain/text/annotations.html
O arranjo gráfico é uma elaboração deste estudo. As figuras selecionam
relações e propriedades existentes; não representam a geometria do edifício.
"""
import hashlib
import json
import shutil
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from rdflib import Graph, Namespace, RDF, RDFS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resultados" / "visualizacao_grafo"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = Path(sys.argv[1]).resolve()
g = Graph().parse(SOURCE, format="turtle")
BOT = Namespace("https://w3id.org/bot#")
P = Namespace("http://lbd.arch.rwth-aachen.de/props#")
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
INK, EDGE = "#16324F", "#8294A4"
COLORS = {"site": "#E3EAF1", "building": "#D9E8F7", "storey": "#CFEBE3", "space": "#FFF0CF", "literal": "#F0F3F6"}

def value(s, p):
    v = g.value(s, p, any=False)
    if v is None:
        raise ValueError(f"Propriedade ausente: {s} {p}")
    return str(v)

def unique(cls):
    items = list(g.subjects(RDF.type, cls))
    if len(items) != 1:
        raise ValueError(f"Esperado um recurso: {cls}")
    return items[0]

site, building = unique(BOT.Site), unique(BOT.Building)
spaces = sorted(g.subjects(RDF.type, BOT.Space), key=lambda s: (value(s, RDFS.label), value(s, P.longNameIfcSpatialElement_attribute_simple)))
storeys = list(g.objects(building, BOT.hasStorey))
active = [s for s in storeys if any(g.objects(s, BOT.hasSpace))]
assert len(active) == 1 and len(spaces) == 41
floor = active[0]
assert set(g.objects(floor, BOT.hasSpace)) == set(spaces)
assert (site, BOT.hasBuilding, building) in g
selected_overview = Graph()
selected_detail = Graph()
for s in [site, building, *storeys, *spaces]:
    for p in [RDF.type, RDFS.label, P.longNameIfcSpatialElement_attribute_simple]:
        for o in g.objects(s, p):
            selected_overview.add((s, p, o))
for p in [BOT.hasBuilding, BOT.hasStorey, BOT.hasSpace]:
    for triple in g.triples((None, p, None)):
        selected_overview.add(triple)

def canvas(title, subtitle, w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=.025, right=.975, top=.91, bottom=.065)
    fig.text(.04, .965, title, fontsize=23, weight="bold", color=INK, va="top")
    fig.text(.04, .93, subtitle, fontsize=11, color="#526779", va="top")
    ax.set(xlim=(0, 100), ylim=(0, 100))
    ax.axis("off")
    return fig, ax

def box(ax, x, y, text, kind, w=20, h=5, size=10):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
        boxstyle="round,pad=0.25,rounding_size=0.6", linewidth=1.0,
        facecolor=COLORS[kind], edgecolor=INK, zorder=3))
    ax.text(x, y, text, ha="center", va="center", color=INK, fontsize=size, zorder=4)

def arrow(ax, a, b, label=None, label_xy=None, size=9):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10,
        linewidth=1, color=EDGE, zorder=1))
    if label:
        xy = label_xy or ((a[0]+b[0])/2, (a[1]+b[1])/2)
        ax.text(*xy, label, ha="center", va="center", fontsize=size,
            color=INK, bbox={"facecolor": "white", "edgecolor": "none", "pad": 2}, zorder=2)

def save(fig, stem, note):
    fig.text(.04, .025, note, fontsize=9, color="#526779", va="bottom")
    for suffix in ["png", "svg"]:
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=180, facecolor="white")
    plt.close(fig)

fig, ax = canvas("Organização espacial dos 41 ambientes", "Creche Pré-Escola Tipo 2 · FNDE · R03/2025 | Relações extraídas do grafo IFC–LBD corrigido", 18, 17)
box(ax, 15, 96, "TERRENO\n"+value(site, RDFS.label), "site", w=23, h=6, size=11)
box(ax, 52, 96, "EDIFICAÇÃO\n"+value(building, RDFS.label), "building", w=37, h=6, size=11)
arrow(ax, (27,96), (33,96), "bot:hasBuilding", (30,99.8), size=9)
box(ax, 52, 85, "PAVIMENTO · "+value(floor, RDFS.label)+"\n41 ambientes vinculados", "storey", w=36, h=6, size=11)
arrow(ax, (52,92.7), (52,88.3), "bot:hasStorey", (62,90.5))
for s in storeys:
    if s != floor:
        box(ax, 86, 85, "PAVIMENTO · "+value(s,RDFS.label)+"\n0 ambientes vinculados", "storey", w=24, h=6, size=10)
        arrow(ax, (69,92.7), (86,88.3), "bot:hasStorey", (84,92.5))
ax.plot([52,52], [81.7,78], color=EDGE, linewidth=1)
ax.plot([2,77], [78,78], color=EDGE, linewidth=1)
ax.text(50, 75.8, "Cada seta abaixo representa bot:hasSpace (pavimento → ambiente).", ha="center", fontsize=11, color=INK)
for col in range(4):
    x = 14 + col*25
    chunk = spaces[col*11:(col+1)*11]
    if not chunk:
        continue
    ys = [70-i*6 for i in range(len(chunk))]
    ax.plot([x-12,x-12], [78,ys[-1]], color=EDGE, linewidth=1)
    for s,y in zip(chunk,ys):
        name = value(s, P.longNameIfcSpatialElement_attribute_simple)
        wrapped = textwrap.fill(name, width=24)
        box(ax, x,y, value(s,RDFS.label)+" · "+wrapped, "space", w=20.7,h=4.9,size=9)
        arrow(ax, (x-12,y), (x-10.6,y))
save(fig, "grafo_organizacao_espacial", "Fonte: grafo corrigido (411 triplas). Recorte: organização espacial e nomes. As posições no desenho não indicam localização física ou adjacência.")

kitchens = [s for s in spaces if value(s,P.longNameIfcSpatialElement_attribute_simple)=="COZINHA"]
assert len(kitchens)==1
kitchen=kitchens[0]
for s,p,o in g:
    if s==kitchen or (s in [site,building,floor] and p in [RDF.type,RDFS.label,BOT.hasBuilding,BOT.hasStorey] and (p!=BOT.hasStorey or o==floor)) or (s==floor and p==BOT.hasSpace and o==kitchen):
        selected_detail.add((s,p,o))
fig, ax=canvas("Como ler o grafo: o ambiente COZINHA", "Recorte do resultado corrigido | Setas ligam recursos aos seus vínculos e valores", 16, 9)
box(ax,15,86,"TERRENO\n"+value(site,RDFS.label),"site",w=25,h=12,size=12)
box(ax,15,55,"EDIFICAÇÃO\n"+textwrap.fill(value(building,RDFS.label),width=20),"building",w=25,h=15,size=11)
box(ax,15,21,"PAVIMENTO\n"+value(floor,RDFS.label),"storey",w=25,h=12,size=12)
arrow(ax,(15,79.5),(15,63),"bot:hasBuilding",(15,72),11)
arrow(ax,(15,47),(15,27.5),"bot:hasStorey",(15,37),11)
box(ax,46,21,"AMBIENTE\nCOZINHA","space",w=22,h=13,size=14)
arrow(ax,(27.7,21),(34.7,21),"bot:hasSpace",(31,30),11)
fields=[("tipo", "bot:Space", None, 88),
        ("nome",value(kitchen,RDFS.label),RDFS.label,69),
        ("nome descritivo",value(kitchen,P.longNameIfcSpatialElement_attribute_simple),P.longNameIfcSpatialElement_attribute_simple,50),
        ("categoria",value(kitchen,P.category_property_simple),P.category_property_simple,31),
        ("GlobalId",value(kitchen,P.globalIdIfcRoot_attribute_simple),P.globalIdIfcRoot_attribute_simple,12)]
for label,txt,p,y in fields:
    box(ax,84,y,txt,"literal" if p else "space",w=30,h=11,size=12 if label!="GlobalId" else 10)
    arrow(ax,(57.4,23),(68.5,y),"rdf:type" if p is None else label,(63,y),10)
save(fig,"grafo_detalhe_cozinha","Fonte: grafo corrigido. Recursos em caixas coloridas; valores textuais em cinza. Nomes simplificados das propriedades: correspondências no README.")

for subset,name in [(selected_overview,"recorte_organizacao_espacial.ttl"),(selected_detail,"recorte_cozinha.ttl")]:
    for prefix,ns in [("bot",BOT),("props",P),("rdfs",RDFS)]: subset.bind(prefix,ns)
    assert all(t in g for t in subset)
    subset.serialize(OUT/name,format="turtle")
if SOURCE != (OUT/"creche_tipo2_lbd_corrigido.ttl").resolve():
    shutil.copyfile(SOURCE,OUT/"creche_tipo2_lbd_corrigido.ttl")
(OUT/"registro_visualizacao.json").write_text(json.dumps({
    "sha256_grafo_origem":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "triplas_origem":len(g),"ambientes_representados":len(spaces),
    "relacoes_pavimento_ambiente":len(list(g.triples((floor,BOT.hasSpace,None)))),
    "triplas_recorte_espacial":len(selected_overview),"triplas_recorte_cozinha":len(selected_detail),
    "bibliotecas":{"rdflib":"7.1.4","matplotlib":matplotlib.__version__},
    "criterio":"Apenas triplas presentes no grafo corrigido; disposição gráfica sem significado geométrico."
},ensure_ascii=False,indent=2),encoding="utf-8")
print("Figuras e recortes salvos em:",OUT)
