"""Figura de apresentação: cobertura de execução, sem extrapolar a amostra."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def figura(resultados):
    resultados=Path(resultados);d=json.loads((resultados/'Resumo.json').read_text(encoding='utf8'))
    fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
    labels=['Associação executada','Preparo inconclusivo'];values=[d['espacos_com_associacao'],d['espacos_inconclusivos']]
    bars=ax.barh(labels,values,color=['#256b8c','#bf7340']);ax.bar_label(bars,padding=5)
    ax.set_xlim(0,43);ax.set_xlabel('Quantidade de IfcSpace (total: 41)')
    ax.set_title('FNDE Tipo 2 · Arquitetura R03',loc='left',weight='bold')
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(resultados/'Cobertura.png',dpi=170);plt.close(fig)
