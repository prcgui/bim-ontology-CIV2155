"""Conferência interna da geometria do piloto IFC2SB parcial.

Não implementa novo algoritmo publicado nem validação arquitetônica independente.
Fichter et al. (2021), DOI 10.26868/25222708.2021.30156: origem do módulo
geométrico reutilizado. Código dos autores, commit fixado:
https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad
IfcOpenShell: create_shape e disable-opening-subtractions (fontes técnicas):
https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html
https://docs.ifcopenshell.org/ifcopenshell/geometry_settings.html#disable-opening-subtractions

Diagnóstico específico deste estudo: comparar parede bruta, parede processada
com os vazios subtraídos e a região de cada abertura; não alterar associações.
"""
from pathlib import Path
import json,csv,hashlib,sys,time
from collections import Counter
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.ifcopenshell_wrapper as W
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from ifc2sb_faces import (read_brep,closed_space_solid,shapes,volume,common,
                         BRepCheck_Analyzer,TopAbs_SOLID,write_brep,polygon_wkt)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')

def solid_volume(s):
    solids=shapes(s,TopAbs_SOLID)
    return {'solidos':len(solids),'brep_valido':BRepCheck_Analyzer(s).IsValid(),
            'volume_m3':sum(abs(volume(a)) for a in solids)}

def controls(out):
    """Dimensões de caixas fornecem expectativas independentes dos resultados."""
    wall=BRepPrimAPI_MakeBox(4,.2,3).Shape()
    room=BRepPrimAPI_MakeBox(gp_Pnt(0,.15,0),2,2,3).Shape()
    opening=BRepPrimAPI_MakeBox(gp_Pnt(0,-.1,0),2,.4,3).Shape()
    other=BRepPrimAPI_MakeBox(gp_Pnt(3,-.1,0),.5,.4,3).Shape()
    cut=BRepAlgoAPI_Cut(wall,opening);assert cut.IsDone()
    gross=solid_volume(common(room,wall))['volume_m3']
    net=solid_volume(common(room,cut.Shape()))['volume_m3']
    local=solid_volume(common(common(room,wall),opening))['volume_m3']
    elsewhere=solid_volume(common(common(room,wall),other))['volume_m3']
    tests=[{'teste':'volume_bruto_analitico','aprovado':abs(gross-.3)<1e-9,'obtido':gross,'esperado':.3},
      {'teste':'vazio_pode_remover_intersecao_bruta','aprovado':net<1e-9,'obtido':net,'esperado':0},
      {'teste':'intersecao_local_na_abertura','aprovado':abs(local-.3)<1e-9,'obtido':local,'esperado':.3},
      {'teste':'conflito_na_parede_nao_prova_conflito_em_toda_abertura','aprovado':elsewhere<1e-9 and gross>0,'obtido':elsewhere,'esperado':0}]
    d={'testes':tests,'aprovados':sum(t['aprovado'] for t in tests),'total':4}
    Path(out).mkdir(parents=True,exist_ok=True);save(Path(out)/'Controles_Conferencia.json',d)
    assert d['aprovados']==4;return d

def run(ifc_path,pilot_path,out):
    start=time.perf_counter();ifc_path=Path(ifc_path);pilot_path=Path(pilot_path);out=Path(out)
    out.mkdir(exist_ok=True,parents=True);(out/'malhas').mkdir(exist_ok=True)
    pilot=json.loads(pilot_path.read_text(encoding='utf8'))
    before=sha(ifc_path);inputhash=sha(pilot_path);assert before==pilot['sha256_IFC']
    model=ifcopenshell.open(str(ifc_path));errors=[];cache={};mesh_data={}
    def settings(subtract,serialized):
        s=ifcopenshell.geom.settings();s.set('use-world-coords',True);s.set('convert-back-units',False)
        s.set('disable-opening-subtractions',not subtract)
        if serialized:s.set('iterator-output',W.SERIALIZED)
        return s
    bs={b:settings(b,True) for b in [False,True]}
    ms=settings(True,False)
    def brep(guid,subtract=False):
        key=(guid,subtract)
        if key not in cache:
            # Conservar o wrapper vivo até concluir a leitura, conforme API.
            holder=ifcopenshell.geom.create_shape(bs[subtract],model.by_guid(guid))
            cache[key]=read_brep(holder.geometry.brep_data)
        return cache[key]
    def mesh(guid):
        if guid not in mesh_data:
            holder=ifcopenshell.geom.create_shape(ms,model.by_guid(guid))
            v=np.asarray(holder.geometry.verts,dtype=float).reshape(-1,3)
            f=np.asarray(holder.geometry.faces,dtype=int).reshape(-1,3)
            mesh_data[guid]=(v,f);np.savez_compressed(out/'malhas'/f'{guid}.npz',vertices=v,faces=f)
        return mesh_data[guid]
    def distance(a,b):
        op=BRepExtrema_DistShapeShape(a,b);op.Perform()
        if not op.IsDone():raise ValueError('Distância entre formas não calculada')
        return op.Value()
    room,topology=closed_space_solid(brep(pilot['ambiente']))
    rv,rf=mesh(pilot['ambiente']);walls=[];wall_shapes={}
    for w in pilot['paredes']:
        guid=w['parede']
        try:
            gross=brep(guid,False)
            # Reproduz a entrada do recorte anterior: remover somente aberturas
            # sem preenchimento, antes de comparar o valor bruto registrado.
            for rel in model.by_guid(guid).HasOpenings:
                op=rel.RelatedOpeningElement
                if not op.HasFillings:
                    c=BRepAlgoAPI_Cut(gross,brep(op.GlobalId));assert c.IsDone();gross=c.Shape()
            net=brep(guid,True);gi=common(room,gross);ni=common(room,net)
            gv,nv=solid_volume(gi),solid_volume(ni)
            assert abs(gv['volume_m3']-w['volume_intersecao_ambiente_parede_m3'])<1e-7
            net_info=solid_volume(net)
            wall_shapes[guid]=(gross,net,gi,ni)
            record={'parede':guid,'codigo':w['codigo'],'nome':w['nome'],
              'volume_bruto_cozinha_m3':gv['volume_m3'],'volume_com_vazios_cozinha_m3':nv['volume_m3'],
              'volume_parede_com_vazios_m3':net_info['volume_m3'],'solidos_parede_com_vazios':net_info['solidos'],
              'brep_com_vazios_valido':net_info['brep_valido'],'brep_intersecao_com_vazios_valido':nv['brep_valido'],
              'classificacao':'sobreposicao_persiste_com_vazios' if nv['volume_m3']>1e-8 else 'sem_volume_comum_com_vazios_no_criterio'}
            walls.append(record);mesh(guid)
            if nv['volume_m3']>1e-8:write_brep(ni,out/(w['codigo']+'_Intersecao_Com_Vazios.brep'))
            print(w['codigo'],round(gv['volume_m3'],8),'->',round(nv['volume_m3'],8),flush=True)
        except Exception as ex:errors.append({'guid':guid,'etapa':'parede','erro':str(ex)})
    wall_records={w['parede']:w for w in walls};rows=[]
    for index,row in enumerate(pilot['aberturas']):
        try:
            o=model.by_guid(row['abertura']);fill=model.by_guid(row['preenchimento'])
            links=[r for r in o.VoidsElements if r.RelatingBuildingElement.GlobalId==row['parede']]
            filling=[r for r in o.HasFillings if r.RelatedBuildingElement.GlobalId==row['preenchimento']]
            assert len(links)==1 and len(filling)==1
            os=brep(o.GlobalId);ov,of=mesh(o.GlobalId);fv,ff=mesh(fill.GlobalId)
            gross,net,gi,ni=wall_shapes[row['parede']]
            ol=solid_volume(common(gi,os));nl=solid_volume(common(ni,os))
            inside=solid_volume(common(room,os));dist=distance(room,os)
            info=wall_records[row['parede']]
            r=dict(row,codigo=f'C{index+1:02d}',relacao_voids=links[0].GlobalId,relacao_fills=filling[0].GlobalId,
              distancia_abertura_cozinha_m=dist,abertura_min_xyz=ov.min(0).tolist(),abertura_max_xyz=ov.max(0).tolist(),
              preenchimento_min_xyz=fv.min(0).tolist(),preenchimento_max_xyz=fv.max(0).tolist(),
              volume_abertura_na_cozinha_m3=inside['volume_m3'],
              volume_intersecao_bruta_na_abertura_m3=ol['volume_m3'],
              volume_intersecao_com_vazios_na_abertura_m3=nl['volume_m3'],
              volume_intersecao_parede_com_vazios_m3=info['volume_com_vazios_cozinha_m3'],
              classificacao_parede_com_vazios=info['classificacao'],
              conferencia='interna; sem padrão-ouro arquitetônico independente')
            if row['estado']=='coincidencia_com_interpenetracao_parede_ambiente':
                r['alcance_do_sinal_anterior']='volume global da parede bruta; não localizado no recorte da abertura'
            else:r['alcance_do_sinal_anterior']='critério geométrico do piloto, sem validação arquitetônica'
            r['decisao_arquitetonica']='pendente'
            r['condicao_para_aceitar']='Conferência em planta/cortes e definição da relação pretendida: delimita, contém, permite acesso ou conecta ambientes.'
            rows.append(r)
        except Exception as ex:errors.append({'guid':row['abertura'],'etapa':'abertura','erro':str(ex)})
    boundaries=model.by_type('IfcRelSpaceBoundary')
    relevant=[r for r in boundaries if r.RelatingSpace==model.by_guid(pilot['ambiente'])]
    result={'procedimento':'conferência interna do piloto; comparação de representações e escopo espacial dos sinais',
      'sha256_IFC':before,'sha256_piloto':inputhash,'original_preservado':sha(ifc_path)==before,
      'piloto_preservado':sha(pilot_path)==inputhash,'ambiente':pilot['ambiente'],'nome':pilot['nome'],
      'topologia_ambiente':topology,'paredes':walls,'casos':rows,'erros':errors,
      'limites_de_espaco_declarados_total':len(boundaries),'limites_de_espaco_declarados_cozinha':len(relevant),
      'parametros':{'subtracao_vazios_na_conferencia':True,'tolerancia_comparacao_volume_m3':1e-7,'limiar_relato_volume_m3':1e-8,
        'distancia_exata':'BRepExtrema_DistShapeShape; distância mínima entre formas, não prova de ligação funcional'},
      'resumo':{'paredes_conferidas':len(walls),'casos_conferidos':len(rows),
        'paredes_sobreposicao_bruta':sum(w['volume_bruto_cozinha_m3']>1e-8 for w in walls),
        'paredes_sobreposicao_com_vazios':sum(w['volume_com_vazios_cozinha_m3']>1e-8 for w in walls),
        'casos_sinalizados_anteriormente':sum(r['estado']=='coincidencia_com_interpenetracao_parede_ambiente' for r in rows),
        'casos_anteriores_com_volume_local_com_vazios':sum(r['estado']=='coincidencia_com_interpenetracao_parede_ambiente' and r['volume_intersecao_com_vazios_na_abertura_m3']>1e-8 for r in rows)},
      'limite':'Nova leitura do mesmo IFC por IfcOpenShell/OpenCascade; não é motor independente nem validação arquitetônica externa. Não resolve conflitos nem modifica o grafo anterior.',
      'segundos':time.perf_counter()-start}
    save(out/'Conferencia_Geometrica_Cozinha.json',result)
    for name,values in [('Casos_Arquitetonicos_Cozinha.csv',rows),('Paredes_Brutas_e_Com_Vazios.csv',walls)]:
        if values:
            with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in values for k in r)));w.writeheader();w.writerows(values)
    assert result['original_preservado'] and result['piloto_preservado']
    assert len(rows)==len(pilot['aberturas']) and len(walls)==len(pilot['paredes']) and not errors,errors
    print(json.dumps(result['resumo'],ensure_ascii=False),flush=True);return result

def filling_metrics(ifc_path,out):
    """Confronta localização do preenchimento com o critério de superfícies.
    Diagnóstico específico: razão volumétrica não é decisão de uso funcional.
    """
    out=Path(out);path=out/'Conferencia_Geometrica_Cozinha.json'
    d=json.loads(path.read_text(encoding='utf8'));assert sha(ifc_path)==d['sha256_IFC']
    model=ifcopenshell.open(str(ifc_path));s=ifcopenshell.geom.settings()
    s.set('iterator-output',W.SERIALIZED);s.set('use-world-coords',True)
    s.set('convert-back-units',False);s.set('disable-opening-subtractions',False)
    def body(guid):
        holder=ifcopenshell.geom.create_shape(s,model.by_guid(guid))
        return read_brep(holder.geometry.brep_data)
    room,_=closed_space_solid(body(d['ambiente']));rows=[]
    for r in d['casos']:
        obj=body(r['preenchimento']);raw=solid_volume(obj);topology=None;reason=None
        if raw['solidos']==0:
            try:obj,topology=closed_space_solid(obj)
            except ValueError as exc:reason=str(exc)
        total=solid_volume(obj);inside=solid_volume(common(room,obj))
        available=total['solidos']>0 and total['brep_valido'] and inside['brep_valido'] and total['volume_m3']>1e-12
        info={'codigo':r['codigo'],'preenchimento':r['preenchimento'],'classe':r['classe_preenchimento'],
          'volume_preenchimento_m3':total['volume_m3'] if available else None,
          'volume_preenchimento_na_cozinha_m3':inside['volume_m3'] if available else None,
          'fracao_volumetrica_na_cozinha':inside['volume_m3']/total['volume_m3'] if available else None,
          'solidos_preenchimento':total['solidos'],'brep_preenchimento_valido':total['brep_valido'],
          'solidos_preenchimento_entrada':raw['solidos'],'solido_derivado_sem_descarte_de_faces':topology is not None,
          'motivo_indisponibilidade_volume':None if available else reason or 'Sem sólido válido para interpretar volume',
          'interpretacao':'Indicador geométrico de localização; não define função nem relação ontológica automaticamente.'}
        r.update({k:v for k,v in info.items() if k not in ['codigo','preenchimento','classe']});rows.append(info)
    d['tipagem_esquema_IFC4_RelFillsElement']={a.name():str(a.type_of_attribute()) for a in W.schema_by_name('IFC4').declaration_by_name('IfcRelFillsElement').all_attributes() if a.name() in ['RelatingOpeningElement','RelatedBuildingElement']}
    d['resumo']['classes_preenchimento']=dict(Counter(r['classe_preenchimento'] for r in d['casos']))
    save(path,d)
    with (out/'Preenchimentos_Vs_Cozinha.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (out/'Casos_Arquitetonicos_Cozinha.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in d['casos'] for k in r)));w.writeheader();w.writerows(d['casos'])
    assert sha(ifc_path)==d['sha256_IFC'];return d

if __name__=='__main__':
    controls(sys.argv[3]);run(sys.argv[1],sys.argv[2],sys.argv[3]);filling_metrics(sys.argv[1],sys.argv[3])
