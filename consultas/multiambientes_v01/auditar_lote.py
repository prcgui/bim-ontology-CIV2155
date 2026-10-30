"""Conferência posterior: cobertura, regressão, documentos e sobreposições.
As medições OCP entre espaços são diagnóstico específico; não são CGAL/Nef.
"""
from pathlib import Path
from collections import Counter
import json,time
from ifc2sb_faces import read_brep,common,shapes,TopAbs_SOLID,volume
from preparar_geometria import save,sha,SHA
from rotina_multiambientes import write_csv

def auditar_sobreposicoes(cache,out):
    started=time.perf_counter();cache=Path(cache);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=json.loads((cache/'Catalogo_Geometria_v09.json').read_text(encoding='utf8'))
    rooms=[r for r in data['espacos'] if r['estado'].startswith('volume_')];bodies={};pairs=[]
    def body(r):
        if r['guid'] not in bodies:
            assert sha(cache/r['arquivo_brep'])==r['sha256_brep']
            bodies[r['guid']]=read_brep((cache/r['arquivo_brep']).read_bytes())
        return bodies[r['guid']]
    for i,a in enumerate(rooms):
        for b in rooms[i+1:]:
            r={'a':a['guid'],'nome_a':a['nome'],'b':b['guid'],'nome_b':b['nome']}
            A,B=a['bbox'],b['bbox']
            if not all(min(A[k+3],B[k+3])-max(A[k],B[k])>1e-7 for k in range(3)):
                r['estado']='sem_sobreposicao_interior_bbox_no_criterio'
            else:
                try:
                    shape=common(body(a),body(b));v=sum(abs(volume(s)) for s in shapes(shape,TopAbs_SOLID))
                    r.update(estado='volume_comum_acima_limiar' if v>1e-8 else 'sem_volume_comum_acima_limiar',volume_m3=v)
                except (RuntimeError,ValueError) as exc:r.update(estado='inconclusivo_operador',motivo=str(exc))
            pairs.append(r)
    result={'ifc_sha256':SHA,'espacos_com_solido':len(rooms),'pares_examinados':len(pairs),
        'pares_com_sobreposicao':sum(r['estado']=='volume_comum_acima_limiar' for r in pairs),
        'pares_inconclusivos':sum(r['estado']=='inconclusivo_operador' for r in pairs),'pares':pairs,
        'operador':'Common OCP sobre sólidos derivados; não é CGAL/Nef nem algoritmo integral de Lilis.',
        'limite':'Sobreposição volumétrica é diagnóstico, não correção do IFC ou veto automático a toda abertura.',
        'segundos':time.perf_counter()-started}
    save(out/'Sobreposicoes_Entre_Espacos_v09.json',result)
    write_csv(out/'Sobreposicoes_Entre_Espacos_v09.csv',[r for r in pairs if r['estado']=='volume_comum_acima_limiar'])
    print('Sobreposições:',result['pares_com_sobreposicao'],'em',len(pairs),'pares.');return result

def conferir_documentos(out,reference_path):
    out=Path(out);ref=json.loads(Path(reference_path).read_text(encoding='utf8'));rows=[];metrics=[]
    assert ref['ifc_sha256']==SHA
    for room in ref['ambientes']:
        d=json.loads((out/'ambientes'/room['guid']/'Resultado_Ambiente_v09.json').read_text(encoding='utf8'))
        executed=d['estado'].startswith('associacao_');predicted={r['guid'] for r in d['esquadrias_associadas']}
        metric={'ambiente':room['guid'],'nome':room['nome'],'estado_processamento':d['estado'],'casos':len(room['casos']),
          'TP':0,'FP':0,'FN':0,'TN':0,'indeterminados':0,'positivos_nao_recuperados_por_preparacao':0,
          'negativos_nao_avaliaveis_por_preparacao':0,'previsoes_fora_referencia':[]}
        for r in room['casos']:
            truth=r['pertence_ao_ambiente'];prediction=r['guid'] in predicted
            if truth=='indeterminado':status='indeterminado_documental';metric['indeterminados']+=1
            elif not executed:
                status='nao_recuperado_por_preparacao' if truth=='sim' else 'nao_avaliavel_por_preparacao'
                metric['positivos_nao_recuperados_por_preparacao' if truth=='sim' else 'negativos_nao_avaliaveis_por_preparacao']+=1
            else:
                key='TP' if truth=='sim' and prediction else 'FN' if truth=='sim' else 'FP' if prediction else 'TN'
                metric[key]+=1;status={'TP':'associacao_correta','FP':'associacao_indevida','FN':'omissao_apos_associacao','TN':'exclusao_correta'}[key]
            rows.append({'ambiente':room['guid'],'nome_ambiente':room['nome'],**r,
              'previsto':prediction if executed else None,'resultado_conferencia':status,'estado_processamento':d['estado']})
        known={r['guid'] for r in room['casos']};metric['previsoes_fora_referencia']=sorted(predicted-known)
        # Não aprova automaticamente um caso que a referência não definiu.
        for guid in metric['previsoes_fora_referencia']:
            rows.append({'ambiente':room['guid'],'nome_ambiente':room['nome'],'guid':guid,
              'pertence_ao_ambiente':'nao_definido','previsto':True,'resultado_conferencia':'previsao_fora_referencia','estado_processamento':d['estado']})
        metrics.append(metric)
    totals={k:sum(r[k] for r in metrics) for k in ['TP','FP','FN','TN','indeterminados','positivos_nao_recuperados_por_preparacao','negativos_nao_avaliaveis_por_preparacao']}
    positives=totals['TP']+totals['FN']+totals['positivos_nao_recuperados_por_preparacao']
    result={'ifc_sha256':SHA,'referencia_sha256':sha(reference_path),'amostra_ambientes':len(metrics),
       'novos_ambientes_alem_cozinha':len(metrics)-1,'ambientes_amostra_com_associacao':sum(r['estado_processamento'].startswith('associacao_') for r in metrics),
       'ambientes_amostra_inconclusivos':sum(r['estado_processamento'].startswith('inconclusivo_') for r in metrics),
       'totais':totals,'referencias_positivas_totais':positives,
       'recuperacao_incluindo_inconclusivos':totals['TP']/positives if positives else None,
       'previsoes_fora_referencia':sum(len(r['previsoes_fora_referencia']) for r in metrics),
       'por_ambiente':metrics,'limites':ref['limites'],'avaliacao_cega_por_especialista':False,
       'denominadores':'TP/FP/FN/TN somente em ambientes com associação executada. Positivos não recuperados por preparo aparecem separados e entram na recuperação global da amostra; não são ocultados como sucesso.'}
    target=out/'conferencia';target.mkdir(exist_ok=True)
    save(target/'Conferencia_Multiambientes_v09.json',result)
    write_csv(target/'Conferencia_Caso_a_Caso_v09.csv',rows);write_csv(target/'Conferencia_Por_Ambiente_v09.csv',metrics)
    print('Conferência:',json.dumps({k:result[k] for k in ['amostra_ambientes','totais','recuperacao_incluindo_inconclusivos','previsoes_fora_referencia']},ensure_ascii=False));return result

def regressao_cozinha(out,controle_v08):
    out=Path(out);old=json.loads(Path(controle_v08).read_text(encoding='utf8'))
    new=json.loads((out/'ambientes'/old['ambiente']/'Resultado_Ambiente_v09.json').read_text(encoding='utf8'))
    old_ids={r['preenchimento'] for r in old['esquadrias_associadas']};new_ids={r['guid'] for r in new['esquadrias_associadas']}
    checks={'mesmas_nove_esquadrias':old_ids==new_ids and len(new_ids)==9,
      'mesmas_14_interfaces':len(old['interfaces_delimitadoras'])==len(new['interfaces'])==14,
      'mesmos_dez_internos':{r['guid'] for r in old['elementos_internos_candidatos']}=={r['guid'] for r in new['elementos_internos_candidatos']},
      'mesmos_tres_componentes':{r['guid'] for r in old['componentes_sem_FillsVoids_candidatos']}=={r['guid'] for r in new['componentes_sem_FillsVoids_candidatos']},
      'area_interfaces_preservada':abs(sum(r['area_m2'] for r in old['interfaces_delimitadoras'])-sum(r['area_m2'] for r in new['interfaces']))<1e-6}
    assert all(checks.values()),checks
    save(out/'Regressao_Cozinha_v08_v09.json',{'verificacoes':checks,'aprovadas':sum(checks.values()),'total':len(checks),
       'limite':'Controle de regressão numérica/identidades; não substitui a avaliação documental dos novos espaços.'})
    print('Regressão cozinha:',sum(checks.values()),'controles aprovados.');return checks

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('cache');p.add_argument('resultados');p.add_argument('referencia');p.add_argument('controle_cozinha')
    a=p.parse_args();auditar_sobreposicoes(a.cache,Path(a.resultados)/'diagnosticos');conferir_documentos(a.resultados,a.referencia);regressao_cozinha(a.resultados,a.controle_cozinha)
