"""Compara recortes calculados por OCP (piloto) e Shapely (adaptação).
Mesma geometria/seleção, operadores diferentes; não é padrão-ouro arquitetônico.
"""
from pathlib import Path
import json,csv
def run(pilot_path,result_path,out):
    old=json.loads(Path(pilot_path).read_text(encoding='utf8'));new=json.loads(Path(result_path).read_text(encoding='utf8'))
    groups={}
    for i in new['interfaces']:
        key=(i['parede'],i['face_parede'],i['face_ambiente']);groups[key]=groups.get(key,0)+i['area_m2']
    rows=[]
    for wall in old['paredes']:
        for f in wall['superficies_brutas_coincidentes']:
            key=(wall['parede'],f['original_face_index'],f"R{f['face_ambiente']:02d}")
            other=groups.pop(key,None)
            rows.append({'parede':wall['codigo'],'face_parede':f['original_face_index'],'face_ambiente':key[2],
                'area_ocp_m2':f['area_m2'],'area_shapely_m2':other,
                'diferenca_absoluta_m2':abs(other-f['area_m2']) if other is not None else None})
    assert not groups,'Interfaces novas sem par no piloto: registrar antes de generalizar a comparação'
    result={'interfaces_comparadas':len(rows),'pares_correspondentes':sum(r['area_shapely_m2'] is not None for r in rows),
      'maior_diferenca_area_m2':max(r['diferenca_absoluta_m2'] for r in rows if r['diferenca_absoluta_m2'] is not None),
      'natureza':'Conferência entre operadores, condicionada à mesma entrada e seleção; não validação arquitetônica independente.'}
    assert result['pares_correspondentes']==14 and result['maior_diferenca_area_m2']<1e-7
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    (out/'Comparacao_Operadores_OCP_Shapely.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    with (out/'Comparacao_Operadores_OCP_Shapely.csv').open('w',encoding='utf-8-sig',newline='') as fp:
        wr=csv.DictWriter(fp,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
    import sys
    run(*sys.argv[1:])
