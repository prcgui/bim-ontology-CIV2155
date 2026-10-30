"""Relatório das medições do ensaio parcial; não infere relações por imagem."""
from pathlib import Path
import json,html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run(out):
    out=Path(out);d=json.loads((out/'Resultado_Lilis_Hibrido_v01.json').read_text(encoding='utf8'));s=d['resumo']
    checks=json.loads((out/'Controles_Lilis_v01.json').read_text(encoding='utf8'))
    rdf=json.loads((out/'Registro_RDF_Lilis_v01.json').read_text(encoding='utf8'))
    sensitivity=[r for r in d['sensibilidade'] if r['variante']=='maxA_global_artigo']
    fig,axes=plt.subplots(1,2,figsize=(12,4.7),layout='constrained')
    axes[0].plot([r['d_m']*100 for r in sensitivity],[r['aberturas_com_interface_hospedeira'] for r in sensitivity],marker='o',color='#14665c',lw=2)
    axes[0].set(xlabel='Distância máxima entre planos (cm)',ylabel='Aberturas distintas associadas',title='O resultado depende da distância',ylim=(0,12))
    axes[0].set_xticks([5,15,30,60]);axes[0].grid(axis='y',alpha=.2)
    for r in sensitivity:axes[0].annotate(str(r['aberturas_com_interface_hospedeira']),(r['d_m']*100,r['aberturas_com_interface_hospedeira']),xytext=(0,8),textcoords='offset points',ha='center')
    axes[1].barh(['Com apoio no volume 3D','Sem apoio no volume 3D'],[s['recortes_com_apoio_volume_3D'],s['recortes_sem_apoio_volume_3D']],color=['#14665c','#b66b26'])
    axes[1].set(xlabel='Recortes candidatos, d = 30 cm',title='Projeção e contato têm critérios distintos',xlim=(0,13))
    for i,v in enumerate([s['recortes_com_apoio_volume_3D'],s['recortes_sem_apoio_volume_3D']]):axes[1].text(v+.2,i,str(v),va='center')
    fig.suptitle('Cozinha · ensaio parcial de Lilis (2026)',fontsize=15,fontweight='bold')
    fig.savefig(out/'Comparacao_Lilis_v01.png',dpi=170);plt.close(fig)
    def table(rows,fields):
        return '<table><thead><tr>'+''.join('<th>'+html.escape(label)+'</th>' for field,label in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(f'{r[field]:.6f}' if isinstance(r[field],float) else str(r[field]))+'</td>' for field,label in fields)+'</tr>' for r in rows)+'</tbody></table>'
    anomalous=[r for r in d['comparacao_geometrica'] if r['area_lilis_sem_apoio_common_3D_m2']>1e-7]
    text=f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Ensaio parcial de Lilis · cozinha</title>
<style>body{{font:16px/1.6 system-ui;max-width:1120px;margin:40px auto;padding:0 24px;color:#18312e}}h1,h2{{line-height:1.2}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:20px 0}}td,th{{padding:9px;border:1px solid #d6e0dd;text-align:left;overflow-wrap:anywhere}}th{{background:#eaf3ef}}img{{width:100%;height:auto}}.note{{padding:18px;background:#fff2dd;border-left:4px solid #b66b26}}code{{font-size:13px}}</style>
<h1>Lilis no código híbrido da cozinha</h1>
<p>O ensaio adaptou operadores do artigo para projetar aberturas nas faces do ambiente e calcular o que sobra após os recortes. A associação à parede é herdada do código híbrido anterior. A contribuição observada é geométrica e comparativa; não foi demonstrado ganho de acurácia arquitetônica.</p>
<p><b>{checks['aprovados']} de {checks['total']} controles aprovados · {s['aberturas_ifc_examinadas']} aberturas examinadas no IFC · {s['aberturas_no_ensaio_local']} próximas avaliadas · {s['aberturas_associadas_apos']} aberturas associadas · {s['recortes_hibridos']} recortes candidatos.</b></p>
<img src="Comparacao_Lilis_v01.png" alt="Sensibilidade à distância e apoio dos recortes na interseção 3D">
<h2>O que mudou</h2><p>As dez aberturas distintas do procedimento anterior foram preservadas. Foram obtidos 12 recortes locais: 11 têm apoio no volume 3D no limiar de 10⁻⁷ m²; um recorte adicional de 0,062 m² aparece por projeção e não tem esse apoio. Isso não refuta Lilis: o artigo admite projeção entre planos separados. O híbrido mantém esse recorte como candidato e não certifica uma nova relação.</p>
<div class="note">A área bruta somada das 14 interfaces é {s['area_bruta_interfaces_m2']:.6f} m². A união dos recortes candidatos é {s['area_recortes_uniao_m2']:.6f} m², deixando {s['area_residual_m2']:.6f} m². Ao usar apenas a parte apoiada pelo volume 3D, os valores são {s['area_uniao_recortes_apoiados_3D_m2']:.6f} m² e {s['area_residual_apos_recortes_apoiados_3D_m2']:.6f} m². São alternativas geométricas; não áreas certificadas de parede opaca ou vidro. Interfaces em planos diferentes não são deduplicadas como uma superfície física única.</div>
<h2>De onde vem cada etapa</h2><ul><li>Lilis §§2.1–2.2: IP/IPS e PSS; §3.3.1/Alg. 3: pares de faces entre espaços; §3.3.4/Alg. 5 e Eq. 5: seleção maxA e recorte de aberturas.</li><li>Adaptações deste estudo: Shapely em bases locais, entrada por faces brutas do espaço, associação à parede IFC e às interfaces híbridas, conferência Common 3D e RDF.</li><li>Etapas ausentes: alpha wrap/Alg. 4, classificação externa certificada, método completo nos 41 ambientes, BEM e gbXML.</li></ul>
<h2>Sensibilidade</h2><p>5 cm associam três aberturas; 15, 30 e 60 cm associam dez. Aumentar a distância também aumenta os recortes brutos. Estabilidade da contagem não prova que as geometrias sejam idênticas ou arquitetonicamente corretas. A variante por componente é uma extensão separada; não substitui silenciosamente a escolha global maxA.</p>
{table(d['sensibilidade'],[('d_m','d (m)'),('variante','Variante'),('recortes_brutos','Recortes brutos'),('aberturas_com_interface_hospedeira','Aberturas associadas')])}
<h2>Recorte adicional que requer conferência</h2>{table(anomalous,[('interface','Interface'),('abertura','Abertura'),('area_lilis_m2','Projeção (m²)'),('area_common_3D_m2','Common 3D (m²)'),('area_lilis_sem_apoio_common_3D_m2','Sem apoio (m²)')])}
<h2>RDF e integridade</h2><p>Preservadas todas as {rdf['triplas_entrada']} triplas anteriores. Saída com {rdf['triplas_saida']} triplas e {rdf['linhas_consulta']} recortes recuperados por SPARQL. Candidatos de Lilis são identificados separadamente das relações anteriores. Nenhuma nova adjacência BOT é certificada. O IFC original mantém seu SHA-256.</p>
<p><a href="Cozinha_Hibrido_Com_Ensaio_Lilis_v01.ttl">RDF</a> · <a href="Consultar_Recortes_Lilis.rq">Consulta</a> · <a href="Comparacao_Geometrica_Recortes_v01.csv">Comparação geométrica</a> · <a href="Resultado_Lilis_Hibrido_v01.json">Registro completo</a></p>
<h2>Referências</h2><p>LILIS, G. N. et al. Automated generation of building energy model geometry from BIM-derived space and opening volumes. Automation in Construction, 185, 106840, 2026. <a href="https://doi.org/10.1016/j.autcon.2026.106840">DOI</a>. Artigo com licença CC BY. Código aqui reimplementado a partir das equações e pseudocódigos; não é o programa C++ dos autores.</p>
<p>KIAVARZ et al. (2023), <a href="https://doi.org/10.3390/buildings13020350">DOI</a>; FICHTER et al. (2021), <a href="https://doi.org/10.26868/25222708.2021.30156">DOI</a>; KRIJNEN et al. (2020), <a href="https://doi.org/10.46421/2706-6568.37.2020.paper008">DOI</a>; ZHANG et al. (2018), <a href="https://doi.org/10.3233/SW-180297">DOI</a>. São reutilizados os módulos parciais anteriores; equivalência aos programas completos não é afirmada.</p></html>'''
    (out/'Relatorio_Lilis_Hibrido_v01.html').write_text(text,encoding='utf8')
    print('Figura e relatório produzidos a partir das medições.');return s
