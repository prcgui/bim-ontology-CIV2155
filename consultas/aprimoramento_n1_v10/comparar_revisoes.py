"""Comparação pareada v09/v10 no mesmo IFC e referência documental fixa."""
from pathlib import Path
import json
from preparar_geometria import save

def run(cache,resultados,controle_v09,out):
    cache=Path(cache);resultados=Path(resultados);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    base=json.loads(Path(controle_v09).read_text(encoding='utf8'))
    cat=json.loads((cache/'Catalogo_Geometria_v10.json').read_text(encoding='utf8'));newcat={r['guid']:r for r in cat['espacos']}
    records=[json.loads(p.read_text(encoding='utf8')) for p in (resultados/'ambientes').glob('*/Resultado_Ambiente_v10.json')]
    old={r['ambiente']:r for r in base['ambientes']};new={r['ambiente']:r for r in records};checks=[]
    def check(name,ok):
        assert ok,name;checks.append({'controle':name,'aprovado':True})
    check('mesmos_41_GUIDs_de_espacos',set(old)==set(new)==set(newcat) and len(new)==41)
    oldpairs={(r['ambiente'],x['guid']) for r in old.values() for x in r['esquadrias_associadas']}
    newpairs={(r['ambiente'],x['guid']) for r in new.values() for x in r['esquadrias_associadas']}
    check('nenhum_par_associado_da_v09_foi_perdido',oldpairs<=newpairs)
    preserved=[r for r in base['catalogo_espacos'] if r['estado'].startswith('volume_')]
    check('todos_29_BReps_aceitos_anteriores_preservados_por_hash',len(preserved)==29 and all(r['sha256_brep']==newcat[r['guid']]['sha256_brep'] for r in preserved))
    recovered=[r for r in cat['espacos'] if r.get('preparacao',{}).get('metodo_v10')=='ShapeFix_Shape_e_costura_controlada']
    check('recuperacoes_com_guardas_e_sem_descarte_de_faces',bool(recovered) and all(r['preparacao']['tentativas'][-1]['aceito'] and r['preparacao']['tentativas'][-1]['guardas']['aceito_guardas'] for r in recovered))
    check('preparo_457_paredes_sem_recorte_inconclusivo',cat['resumo']['paredes_preparadas']==457 and cat['resumo']['paredes_inconclusivas']==0)
    incomplete=[r for r in records if r['estado'].startswith('inconclusivo_')]
    check('falhas_remanescentes_preservadas_sem_zero_falso',len(incomplete)==3 and all(r['resumo']['esquadrias'] is None for r in incomplete))
    audit=json.loads((resultados/'conferencia/Conferencia_Multiambientes_v10.json').read_text(encoding='utf8'));t=audit['totais'];previous=base['conferencia']['totais']
    check('amostra_documental_e_denominadores_originais_preservados',audit['referencia_sha256']==base['conferencia']['referencia_sha256'] and t['TP']+t['FN']+t['positivos_nao_recuperados_por_preparacao']==43 and t['TN']+t['FP']+t['negativos_nao_avaliaveis_por_preparacao']==39 and t['indeterminados']==1)
    check('ganho_de_associacoes_documentalmente_confirmadas',t['TP']>previous['TP'])
    check('sem_associacoes_indevidas_nos_negativos_da_amostra',t['FP']==0 and audit['previsoes_fora_referencia']==0)
    check('cobertura_efetiva_aumentou',sum(r['estado'].startswith('associacao_') for r in records)>base['lote']['espacos_com_associacao_executada'])
    area=json.loads((resultados/'auditorias/Auditoria_Interfaces_v10.json').read_text(encoding='utf8'))
    check('todas_particoes_satisfazem_balanco_de_area',all(r['erro_balanco_m2']<=max(1e-6,r['uniao_m2']*1e-7) and r['uniao_m2']<=r['soma_m2']+1e-6 for r in area['faces']))
    check('proveniencia_preservada_em_todas_as_regioes',all(a['interfaces_fonte'] and a['paredes_fonte'] for r in area['faces'] for a in r['regioes_particionadas']))
    result={'total':len(checks),'aprovados':len(checks),'controles':checks,
      'pares_v09':len(oldpairs),'pares_v10':len(newpairs),'pares_novos':len(newpairs-oldpairs),'pares_perdidos':len(oldpairs-newpairs),
      'espacos_recuperados':len(recovered),'tp_v09':previous['TP'],'tp_v10':t['TP'],
      'recuperacao_v09':base['conferencia']['recuperacao_incluindo_inconclusivos'],'recuperacao_v10':audit['recuperacao_incluindo_inconclusivos'],
      'metodo':'Comparação pareada no mesmo IFC e amostra de desenvolvimento. Não é teste externo independente.'}
    save(out/'Comparacao_v09_v10.json',result);print('Comparação pareada:',len(checks),'controles aprovados;',len(newpairs-oldpairs),'novos pares;',len(recovered),'espaços recuperados',flush=True);return result
