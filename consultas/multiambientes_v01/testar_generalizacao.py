"""Contratos da generalização: isolamento, cobertura, parâmetros e inconclusão."""
from pathlib import Path
import json
import ifcopenshell
from rotina_multiambientes import RotinaMultiambientes,PARAMS
from preparar_geometria import save

def run(ifc_path,cache,resultados,out):
    resultados=Path(resultados);out=Path(out);out.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,value):
        assert value,name;checks.append({'controle':name,'aprovado':True})
    routine=RotinaMultiambientes(cache)
    model=ifcopenshell.open(str(ifc_path))
    ids={r.GlobalId for r in model.by_type('IfcSpace')}
    observed={p.parent.name for p in (resultados/'ambientes').glob('*/Resultado_Ambiente_v09.json')}
    check('todos_41_IfcSpace_tem_registro_sem_omissao_silenciosa',ids==observed and len(ids)==41)
    refused=False
    try:routine.executar_ambiente('GUID_INEXISTENTE',out/'nao_deve_ser_criado')
    except ValueError:refused=True
    check('GUID_desconhecido_e_rejeitado_antes_de_gravar_resultado',refused and not (out/'nao_deve_ser_criado').exists())
    records=[json.loads(p.read_text(encoding='utf8')) for p in (resultados/'ambientes').glob('*/Resultado_Ambiente_v09.json')]
    check('mesmos_parametros_para_todos_os_ambientes',all(r['parametros']==PARAMS for r in records))
    inconclusive=[r for r in records if r['estado'].startswith('inconclusivo_')]
    check('inconclusao_nao_e_zero_esquadria',len(inconclusive)==12 and all(r['resumo']['esquadrias'] is None for r in inconclusive))
    # Invertemos a ordem de dois ambientes que compartilham uma porta/janela.
    desp=routine.executar_ambiente('2zRoTG0q18vvDXCc_KqVNQ',out/'ordem/despensa')
    kitchen=routine.executar_ambiente('3UFjAT4k55zg_Pqo6VMw5l',out/'ordem/cozinha')
    original=json.loads((resultados/'ambientes/3UFjAT4k55zg_Pqo6VMw5l/Resultado_Ambiente_v09.json').read_text(encoding='utf8'))
    check('cache_nao_transfere_associacoes_entre_ambientes',
      {r['guid'] for r in kitchen['esquadrias_associadas']}=={r['guid'] for r in original['esquadrias_associadas']} and len(desp['esquadrias_associadas'])==3)
    audit=json.loads((resultados/'conferencia/Conferencia_Multiambientes_v09.json').read_text(encoding='utf8'));t=audit['totais']
    check('denominadores_incluem_nao_recuperados_e_nao_inflam_exclusoes',
      t['TP']+t['FN']+t['positivos_nao_recuperados_por_preparacao']==43 and t['TN']+t['FP']+t['negativos_nao_avaliaveis_por_preparacao']==39 and t['indeterminados']==1)
    result={'total':len(checks),'aprovados':len(checks),'controles':checks}
    save(out/'Controles_Generalizacao_v09.json',result);print('Generalização:',len(checks),'controles aprovados.');return result
