"""Confirmação volumétrica de candidatos internos; motivação GRC de Lilis
et al. (2025), DOI 10.1016/j.autcon.2025.106081, §§3.2–3.4.
Operadores OCP atuais; não execução do GRC/BSP original nem inferência funcional.
"""
from pathlib import Path
from recuperar_geometria import preparar_volume_controlado
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from ifc2sb_faces import shapes,TopAbs_SOLID,volume,common,read_brep,unify
from preparar_geometria import init_worker,brep,save
import preparar_geometria as prep
import json

def conter(a,b,tol_volume_abs=1e-8,tol_volume_rel=1e-6):
    """a candidato; b ambiente. Exige sólidos válidos, volume fora e comum."""
    if not BRepCheck_Analyzer(a).IsValid() or not BRepCheck_Analyzer(b).IsValid():raise ValueError('Operando BRep inválido')
    if not shapes(a,TopAbs_SOLID) or not shapes(b,TopAbs_SOLID):raise ValueError('Operando não contém sólido')
    va=sum(abs(volume(s)) for s in shapes(a,TopAbs_SOLID))
    if va<=tol_volume_abs:raise ValueError('Volume insuficiente')
    c=common(a,b);inside=sum(abs(volume(s)) for s in shapes(c,TopAbs_SOLID))
    op=BRepAlgoAPI_Cut(a,b)
    if not op.IsDone():raise ValueError('Diferença OCP falhou')
    outside=sum(abs(volume(s)) for s in shapes(op.Shape(),TopAbs_SOLID))
    threshold=max(tol_volume_abs,tol_volume_rel*va)
    return {'volume_elemento_m3':va,'volume_comum_m3':inside,'volume_fora_m3':outside,
       'limiar_volume_m3':threshold,'contencao_confirmada':outside<=threshold and inside>tol_volume_abs,
       'balanco_volume_erro_m3':abs(va-inside-outside)}

def run(ifc,cache,resultados,out):
    init_worker(ifc);cache=Path(cache);resultados=Path(resultados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    cat=json.loads((cache/'Catalogo_Geometria_v10.json').read_text(encoding='utf8'));rooms={r['guid']:r for r in cat['espacos']};products={};rows=[]
    for path in sorted((resultados/'ambientes').glob('*/Resultado_Ambiente_v10.json')):
        d=json.loads(path.read_text(encoding='utf8'))
        if not d['elementos_internos_candidatos']:continue
        room=read_brep((cache/rooms[d['ambiente']]['arquivo_brep']).read_bytes())
        for p in d['elementos_internos_candidatos']:
            row={'ambiente':d['ambiente'],'nome_ambiente':d['nome'],'elemento':p['guid'],'nome_elemento':p['nome']}
            try:
                if p['guid'] not in products:
                    raw=brep(prep.MODEL.by_guid(p['guid']))
                    try:products[p['guid']]=unify(raw)
                    except (ValueError,RuntimeError):products[p['guid']]=preparar_volume_controlado(raw)[0]
                r=conter(products[p['guid']],room)
                row.update(estado='contencao_confirmada_no_criterio' if r['contencao_confirmada'] else 'candidato_nao_confirmado',**r)
            except (ValueError,RuntimeError) as exc:row.update(estado='inconclusivo_operador_ou_operando',motivo=str(exc))
            rows.append(row)
    result={'operador':'Common + Cut OCP; não GRC/BSP integral.',
      'limite':'Relação geométrica local. Não cria função arquitetônica, decomposição ou pertencimento exclusivo.',
      'pares_candidatos':len(rows),'confirmados':sum(r['estado']=='contencao_confirmada_no_criterio' for r in rows),
      'nao_confirmados':sum(r['estado']=='candidato_nao_confirmado' for r in rows),
      'inconclusivos':sum(r['estado']=='inconclusivo_operador_ou_operando' for r in rows),'pares':rows}
    save(out/'Contencao_Volumetrica_v10.json',result);print('Contenção volumétrica:',{k:result[k] for k in ['pares_candidatos','confirmados','nao_confirmados','inconclusivos']},flush=True);return result
