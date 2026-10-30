"""Localiza pares projetados separados por folga, sem aceitá-los como limite.
Motivação: Krijnen (2020), tolerância explícita, e Lilis (2026), definição
de espaços. A faixa exploratória de 20 mm NÃO é a precisão IFC nem o
predicado CGAL do artigo. Não muda a tolerância primária de 0,1 mm.
"""
from pathlib import Path
import json
from rotina_multiambientes import RotinaMultiambientes,frame,near
from faces_kiavarz import clipped_interface
from preparar_geometria import save

def run(cache,resultados,out):
    routine=RotinaMultiambientes(cache);resultados=Path(resultados);out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[]
    for path in sorted((resultados/'ambientes').glob('*/Resultado_Ambiente_v10.json')):
        d=json.loads(path.read_text(encoding='utf8'));room=routine.rooms[d['ambiente']]
        if not d['estado'].startswith('associacao_'):continue
        associated={r['guid'] for r in d['esquadrias_associadas']};frames=[];best={}
        for f in room['faces']:
            try:frames.append(frame(f))
            except ValueError:pass
        for entry in routine.data['paredes']:
            if not entry.get('bbox') or not near(room['bbox'],entry['bbox'],.02):continue
            _,(_,patches,_)=routine.wall(entry['guid'])
            for patch,pf in patches:
                target=patch['preenchimento'];product=routine.products[target]
                if target in associated or product['classe'] not in ['IfcDoor','IfcWindow']:continue
                for rf in frames:
                    poly,info=clipped_interface(rf,pf,gap=.02)
                    if poly is None or poly.area<.01 or info['distancia_planos_m']<=1e-4:continue
                    rec={'ambiente':d['ambiente'],'nome_ambiente':d['nome'],'elemento':target,'nome_elemento':product['nome'],
                      'parede':entry['guid'],'abertura':patch['abertura'],'face_espaco':rf.id,
                      'distancia_m':info['distancia_planos_m'],'area_projetada_m2':float(poly.area),
                      'estado':'candidato_com_folga_nao_promovido_a_associacao'}
                    if target not in best or rec['distancia_m']<best[target]['distancia_m']:best[target]=rec
        rows.extend(best.values())
    result={'parametros_exploratorios':{'folga_max_m':.02,'area_min_m2':.01},
       'limite':'Candidato apenas. Projeção separada não prova contato, preenchimento ou pertencimento. Sem referência documental na seleção; resultados primários não alterados.',
       'candidatos':rows,'total':len(rows)}
    save(out/'Candidatos_Com_Folga_v10.json',result);print('Candidatos com folga:',len(rows),'sem promoção à associação',flush=True);return result
