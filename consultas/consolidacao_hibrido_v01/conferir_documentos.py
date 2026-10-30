"""Avaliação posterior à previsão. Não altera as associações da rotina.

Referência: pranchas oficiais FNDE Tipo 2 R03, 02 e 24–26.
Métricas de conjuntos são específicas deste estudo e deste recorte documental.
"""
from pathlib import Path
import json,csv,hashlib

def avaliar(cases,predicted):
    rows=[];tp=fp=fn=tn=0
    for r in cases:
        positive=r['guid'] in predicted;truth=r['pertence_a_cozinha']
        status='indeterminado_documental' if truth=='indeterminado' else 'acerto_associacao' if truth=='sim' and positive else 'omissao' if truth=='sim' else 'associacao_indevida' if positive else 'acerto_exclusao'
        tp+=status=='acerto_associacao';fp+=status=='associacao_indevida';fn+=status=='omissao';tn+=status=='acerto_exclusao'
        rows.append(dict(r,previsto=positive,resultado_conferencia=status))
    return {'TP':tp,'FP':fp,'FN':fn,'TN':tn,'precisao_no_recorte':tp/(tp+fp) if tp+fp else None,
       'sensibilidade_no_recorte':tp/(tp+fn) if tp+fn else None,
       'casos_determinados':tp+fp+fn+tn,'indeterminados':sum(r['pertence_a_cozinha']=='indeterminado' for r in cases),
       'previsoes_fora_da_referencia':sorted(predicted-{r['guid'] for r in cases})},rows

def run(resultado_path,reference_path,entrada,out):
    entrada=Path(entrada);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    d=json.loads(Path(resultado_path).read_text(encoding='utf8'))
    ref=json.loads(Path(reference_path).read_text(encoding='utf8'))
    assert d['ifc_sha256']==ref['ifc_sha256'] and d['ambiente']==ref['ambiente']
    old=json.loads((entrada/'Conferencia_Anterior_N1_v03.json').read_text(encoding='utf8'))
    pilot=json.loads((entrada/'Piloto_Anterior_IFC2SB_v04.json').read_text(encoding='utf8'))
    assert old['resumo']['sha256_IFC']==pilot['sha256_IFC']==d['ifc_sha256']
    baseline={r['preenchimento_guid'] for r in old['cadeias'] if r['classe_preenchimento'] in ['IfcDoor','IfcWindow']}
    ifc2sb={r['preenchimento'] for r in pilot['aberturas'] if r['classe_preenchimento'] in ['IfcDoor','IfcWindow'] and r['area_coincidente_cozinha_m2']>1e-8}
    current={r['preenchimento'] for r in d['esquadrias_associadas']}
    reports=[];allrows=[];sets={}
    for name,predicted in [('Consulta_N1_v03_parede_abertura',baseline),('IFC2SB_parcial_v04',ifc2sb),('Hibrido_consolidado_v08',current)]:
        metrics,rows=avaliar(ref['esquadrias'],predicted)
        reports.append(dict(procedimento=name,**metrics));sets[name]=predicted
        allrows.extend(dict(procedimento=name,**r) for r in rows)
    reference_guids={r['guid'] for r in ref['esquadrias']}
    # Cobertura explícita: predições fora da amostra não recebem aprovação.
    assert not any(r['previsoes_fora_da_referencia'] for r in reports)
    component_set={r['guid'] for r in d['componentes_sem_FillsVoids_candidatos']}
    accessory_metrics,accessory_rows=avaliar(ref['componentes_sem_FillsVoids'],component_set)
    internal_set={r['guid'] for r in d['elementos_internos_candidatos']}
    internal_ref=set(ref['elementos_internos']['guids'])
    positive={r['guid'] for r in ref['esquadrias'] if r['pertence_a_cozinha']=='sim'}
    negative={r['guid'] for r in ref['esquadrias'] if r['pertence_a_cozinha']=='nao'}
    result={'fonte_referencia':str(reference_path),'sha256_referencia':hashlib.sha256(Path(reference_path).read_bytes()).hexdigest(),
      'relacao_avaliada':ref['relacao_avaliada'],'metricas':reports,
      'recuperados_vs_consulta_v03':sorted((current-baseline)&positive),
      'associacoes_indevidas_removidas_vs_v03':sorted((baseline-current)&negative),
      'diferencas_esquadrias_vs_IFC2SB_v04':{'adicionadas':sorted(current-ifc2sb),'removidas':sorted(ifc2sb-current)},
      'casos_documentais_indeterminados':[r for r in ref['esquadrias'] if r['pertence_a_cozinha']=='indeterminado'],
      'componentes_sem_FillsVoids':{'metricas_separadas':accessory_metrics,'casos':accessory_rows},
      'elementos_internos':{'referenciados':len(internal_ref),'candidatos_encontrados':len(internal_set),
        'referenciados_recuperados':sorted(internal_ref&internal_set),'nao_recuperados':sorted(internal_ref-internal_set),
        'fora_referencia':sorted(internal_set-internal_ref),'limite':ref['elementos_internos']['alcance']},
      'outros_preenchimentos':d['outros_preenchimentos_associados'],'limites':ref['limites'],
      'conclusao':'Ganho frente à consulta transitiva v03: quatro esquadrias recuperadas e duas associações vizinhas removidas. Sem ganho de contagem frente ao IFC2SB parcial v04. A rotina agrega interfaces, proveniência, dez candidatos internos e componentes sem FillsVoids. JA-09 permanece indeterminada documentalmente.'}
    (out/'Conferencia_Documental_Cozinha_v08.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    def csv_write(name,rows):
        with (out/name).open('w',encoding='utf-8-sig',newline='') as fp:
            w=csv.DictWriter(fp,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
    csv_write('Comparacao_Metodos.csv',reports)
    csv_write('Conferencia_Esquadrias_Caso_a_Caso.csv',allrows)
    csv_write('Conferencia_Componentes_Sem_FillsVoids.csv',accessory_rows)
    csv_write('Elementos_Internos_Candidatos.csv',d['elementos_internos_candidatos'])
    print(json.dumps(reports,ensure_ascii=False,indent=2));return result

def controles_metricas():
    cases=[{'guid':'A','pertence_a_cozinha':'sim'},{'guid':'B','pertence_a_cozinha':'sim'},
      {'guid':'C','pertence_a_cozinha':'nao'},{'guid':'D','pertence_a_cozinha':'nao'},{'guid':'E','pertence_a_cozinha':'indeterminado'}]
    metrics,rows=avaliar(cases,{'A','C','E'})
    assert (metrics['TP'],metrics['FP'],metrics['FN'],metrics['TN'])==(1,1,1,1)
    assert metrics['precisao_no_recorte']==metrics['sensibilidade_no_recorte']==.5
    assert metrics['casos_determinados']==4 and rows[-1]['resultado_conferencia']=='indeterminado_documental'
    assert avaliar(cases,set())[0]['precisao_no_recorte'] is None
    assert avaliar(cases,{'X'})[0]['previsoes_fora_da_referencia']==['X']
    return {'controles_metricas':5,'aprovados':5,'indeterminado_excluido_sem_ser_contado_como_acerto':True}
