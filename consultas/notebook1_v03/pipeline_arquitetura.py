"""Notebook 1 v03: inventário, geometria 3D, relações e avaliação rastreável.

Fontes metodológicas: Bonduel et al.2018 (IFCtoLBD); Huitzil et al.2024
(preservação e configuração); Zhang et al.2018 (geometria no RDF);
Lilis et al.2025 §§3.2–3.4 (relações geométricas); Wang et al.2024 e
Jäkel et al.2025 (validação por regras). Código Python específico do estudo.
Não executa os programas GRC/BimSPARQL nem reproduz seus benchmarks.
"""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
from urllib.parse import quote
import csv,json,hashlib,time,os
import numpy as np
import ifcopenshell,ifcopenshell.geom,ifcopenshell.util.unit,ifcopenshell.util.placement
from rdflib import Dataset,Graph,Namespace,URIRef,Literal,RDF,RDFS,XSD,OWL
from pyshacl import validate
from shapely.errors import GEOSException
from geometria_relacoes import (mesh_diagnostics,surfaces,solid,classify_pair,surface_wkt,
    STRICT_M,NEAR_M,ANGLE_DEG,MIN_AREA_M2,VOLUME_EPS_M3)

BOT=Namespace('https://w3id.org/bot#');GEOM=Namespace('http://bimsparql.org/geometry#')
PROPS=Namespace('http://lbd.arch.rwth-aachen.de/props#');PROV=Namespace('http://www.w3.org/ns/prov#')
CIV=Namespace('https://github.com/prcgui/bim-ontology-CIV2155/vocab/arquitetura#')
BASE='https://github.com/prcgui/bim-ontology-CIV2155/id/notebook1-v03/'
METRE=URIRef('http://qudt.org/vocab/unit/M')
EXPECTED_IFC='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
PAPER_GRC=URIRef('https://doi.org/10.1016/j.autcon.2025.106081')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_json(path,data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def save_csv(path,rows,columns=None):
    rows=list(rows);columns=columns or (list(rows[0]) if rows else [])
    with Path(path).open('w',encoding='utf-8-sig',newline='') as fp:
        w=csv.DictWriter(fp,fieldnames=columns);w.writeheader();w.writerows(rows)

def extract_geometry(ifc_path,cache):
    """IfcOpenShell 0.8.4, original XYZ aplicado ao projeto, em metros.
    Não subtrai/reescreve o IFC. As aberturas dos hospedeiros são preservadas.
    Cache validado pelo hash da fonte, parâmetros e hash de cada malha.
    """
    path=Path(ifc_path);cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    source_hash=sha(path)
    if source_hash!=EXPECTED_IFC:raise ValueError('IFC diferente do modelo selecionado')
    model=ifcopenshell.open(str(path));settings=ifcopenshell.geom.settings()
    settings.set('use-world-coords',True);settings.set('convert-back-units',False);settings.set('disable-opening-subtractions',False)
    config={k:settings.get(k) for k in ['use-world-coords','convert-back-units','disable-opening-subtractions','mesher-linear-deflection','mesher-angular-deflection','precision']}
    manifest=cache/'inventario_geometria.json'
    if manifest.exists():
        data=json.loads(manifest.read_text(encoding='utf8'))
        if data['sha256_ifc']!=source_hash or data['configuracao']!=config or data['ifcopenshell']!=ifcopenshell.version:
            raise ValueError('Cache pertence a outra fonte/configuração; usar nova pasta')
        for r in data['entidades']:
            if 'cache' in r:
                h=sha(cache/r['cache'])
                if 'sha256_npz' in r and r['sha256_npz']!=h:raise ValueError('Malha de cache alterada: '+r['guid'])
                # Existing pilot extraction is imported explicitly with a digest now.
                r['sha256_npz']=h
        save_json(manifest,data)
        return data
    products=[e for e in model.by_type('IfcProduct') if e.Representation]
    inventory={};start=time.perf_counter();iterator=ifcopenshell.geom.iterator(settings,model,2,include=products)
    if not iterator.initialize():raise ValueError('Motor não inicializou geometria')
    while True:
        shape=iterator.get();e=model.by_id(shape.id)
        record={'guid':e.GlobalId,'classe':e.is_a(),'id':e.id(),'nome':e.Name,'long_name':getattr(e,'LongName',None)}
        try:
            v=np.asarray(shape.geometry.verts,dtype=np.float64).reshape(-1,3)
            f=np.asarray(shape.geometry.faces,dtype=np.int64).reshape(-1,3)
            record.update(mesh_diagnostics(v,f));record['cache']=e.GlobalId+'.npz'
            np.savez_compressed(cache/record['cache'],vertices=v,faces=f)
            record['sha256_npz']=sha(cache/record['cache'])
        except Exception as ex:record['erro']=str(ex)
        inventory[e.GlobalId]=record
        if len(inventory)%200==0:print('Geometrias processadas:',len(inventory),flush=True)
        if not iterator.next():break
    for e in products:
        if e.GlobalId not in inventory:inventory[e.GlobalId]={'guid':e.GlobalId,'classe':e.is_a(),'id':e.id(),'nome':e.Name,'erro':'Motor não produziu malha'}
    data={'sha256_ifc':source_hash,'ifcopenshell':ifcopenshell.version,'configuracao':config,
       'unidade_origem_para_metro':ifcopenshell.util.unit.calculate_unit_scale(model),'segundos':time.perf_counter()-start,'entidades':list(inventory.values())}
    save_json(manifest,data)
    if sha(path)!=source_hash:raise ValueError('IFC alterado durante extração')
    return data

def tin_wkt(v,f):
    """Padrão GEOM/BimSPARQL: triângulos XYZ completos, com anéis fechados."""
    return 'TIN Z ('+', '.join('(('+', '.join(' '.join(format(float(c),'.17g') for c in p) for p in v[list(t)+[int(t[0])]])+'))' for t in f)+')'

def contacts_all_spaces(model,cache,data,output):
    """Critérios GRC adaptados a malhas, com dupla checagem de volume.
    O teste é executado para TODOS os IfcSpace com malha e todas as paredes.
    Não cria conexões funcionais nem pertencimento de uma porta ao ambiente.
    """
    cache=Path(cache);output=Path(output);output.mkdir(exist_ok=True,parents=True)
    inventory={r['guid']:r for r in data['entidades']};loaded={}
    def load(guid):
        if guid not in loaded:
            r=inventory[guid]
            if sha(cache/r['cache'])!=r['sha256_npz']:raise ValueError('Cache não íntegro')
            z=np.load(cache/r['cache']);v=z['vertices'];f=z['faces']
            if r['orientacao_consistente'] and r['volume_assinado_m3']<0:f=f[:,[0,2,1]]
            loaded[guid]=(v,f,surfaces(v,f),solid(v,f))
        return loaded[guid]
    rooms=[inventory.get(e.GlobalId) for e in model.by_type('IfcSpace')]
    walls=[inventory[e.GlobalId] for e in model.by_type('IfcWall') if e.GlobalId in inventory and 'cache' in inventory[e.GlobalId]]
    results=[];coverage=[];failures=[];start=time.perf_counter()
    for e,r in zip(model.by_type('IfcSpace'),rooms):
        found=[];broad=0;failed=0
        if r and 'cache' in r:
            va,fa,sa,ma=load(r['guid'])
            for w in walls:
                if np.any(np.minimum(r['bbox_max'],w['bbox_max'])+NEAR_M<np.maximum(r['bbox_min'],w['bbox_min'])):continue
                broad+=1;vb,fb,sb,mb=load(w['guid'])
                try:
                    result=classify_pair(va,fa,vb,fb,sa,sb,ma,mb)
                except (ValueError,GEOSException) as ex:
                    # Diagnóstico sem buffer(0), make_valid ou alteração do IFC.
                    failures.append({'ambiente':e.GlobalId,'ambiente_nome':e.LongName,
                        'parede':w['guid'],'etapa':'projecao_e_intersecao_de_faces',
                        'erro':str(ex),'relacao_arquitetonica_determinada':False})
                    failed+=1
                    continue
                if result:
                    row={k:v for k,v in result.items() if k!='contacts'}
                    row.update(ambiente=e.GlobalId,ambiente_nome=e.LongName,parede=w['guid'],parede_nome=w['nome'],
                       superficies=[{'wkt':surface_wkt(c),'wkt_estrito':surface_wkt(c,True),'area_m2':c['area_m2'],'area_estrita_m2':c['strict_area_m2']} for c in result['contacts']])
                    results.append(row);found.append(row)
        qualified=sum(x['status']=='adjacencia_geometrica_no_limiar_numerico' for x in found)
        coverage.append({'GlobalId':e.GlobalId,'ambiente':e.LongName,'malha_disponivel':bool(r and 'cache' in r),'pares_preselecionados_bbox':broad,
          'paredes_adjacentes_geometricamente':qualified,'paredes_proximas_sem_adjacencia':sum(x['status']=='proximidade_de_superficies' for x in found),
          'contatos_sem_solido_validado':sum(x['status']=='contato_sem_validacao_volumetrica' for x in found),
          'contatos_com_intersecao':sum(x['status']=='contato_com_intersecao_volumetrica' for x in found),
          'pares_com_falha_de_processamento':failed,
          'completude_arquitetonica_demonstrada':False})
        print(e.Name,e.LongName,':',qualified,'paredes adjacentes no critério geométrico',flush=True)
    result={'sha256_ifc':data['sha256_ifc'],'segundos':time.perf_counter()-start,
      'parametros':{'distancia_estrita_m':STRICT_M,'distancia_proximidade_m':NEAR_M,'angulo_graus':ANGLE_DEG,'area_minima_m2':MIN_AREA_M2,'volume_intersecao_maximo_m3':VOLUME_EPS_M3},
      'fonte':'Lilis et al.2025, §§3.2–3.4, Fig.4; adaptação Python; booleanas Manifold3D substituem BSP e não são execução do GRC original.',
      'pares':results,'cobertura':coverage,'falhas_processamento':failures}
    save_json(output/'relacoes_geometricas.json',result);save_csv(output/'cobertura_ambientes.csv',coverage)
    save_csv(output/'relacoes_geometricas.csv',({k:v for k,v in r.items() if k!='superficies'} for r in results))
    save_json(output/'falhas_relacoes_geometricas.json',failures)
    return result

def build_dataset(model,base_rdf,cache,data,relations,output):
    """Materializa instâncias e evidências separadas em grafos nomeados.
    Sem associação transitiva parede→porta = porta do cômodo.
    """
    output=Path(output);output.mkdir(exist_ok=True,parents=True);cache=Path(cache)
    ds=Dataset();names={n:URIRef(BASE+'graph/'+n) for n in ['conversao','declarado','geometria','derivado','candidatos','avaliacao']}
    for k,ns in [('bot',BOT),('geom',GEOM),('props',PROPS),('civ',CIV),('prov',PROV)]:ds.bind(k,ns)
    gs={n:ds.graph(uri) for n,uri in names.items()}
    gs['conversao'].parse(str(base_rdf),format='turtle')
    idx=defaultdict(set)
    for s,o in gs['conversao'].subject_objects(PROPS.globalIdIfcRoot_attribute_simple):idx[str(o)].add(s)
    def uri(e):
        candidates=idx.get(e.GlobalId,set())
        if len(candidates)>1:raise ValueError('GUID ambíguo na conversão: '+e.GlobalId)
        return next(iter(candidates)) if candidates else URIRef(BASE+'entity/'+quote(e.GlobalId,safe=''))
    source=URIRef(BASE+'source/'+data['sha256_ifc']);execution=URIRef(BASE+'execution/'+data['sha256_ifc']+'/v03')
    frame=URIRef(BASE+'frame/'+model.by_type('IfcProject')[0].GlobalId)
    a=gs['avaliacao'];a.add((source,RDF.type,PROV.Entity));a.add((source,CIV.sha256,Literal(data['sha256_ifc'])))
    a.add((execution,RDF.type,PROV.Activity));a.add((execution,PROV.used,source));a.add((execution,PROV.wasAssociatedWith,PAPER_GRC))
    a.add((frame,RDF.type,CIV.ProjectCartesianFrame));a.add((frame,CIV.sourceProjectGuid,Literal(model.by_type('IfcProject')[0].GlobalId)))
    a.add((frame,CIV.unit,METRE));a.add((frame,CIV.sourceUnitScaleToMetre,Literal(float(data['unidade_origem_para_metro']))))
    contexts=[e.get_info(recursive=True) for e in model.by_type('IfcGeometricRepresentationContext') if not e.is_a('IfcGeometricRepresentationSubContext')]
    a.add((frame,CIV.declaredContextMetadata,Literal(json.dumps(contexts,ensure_ascii=False))))
    a.add((frame,RDFS.comment,Literal('Referencial cartesiano do projeto IFC; não reconciliado com estrutura ou georreferenciamento.',lang='pt')))
    declared=gs['declarado'];product_rows=[]
    for e in model.by_type('IfcProduct'):
        u=uri(e);declared.add((u,CIV.ifcClass,Literal(e.is_a())));declared.add((u,CIV.ifcStepId,Literal(e.id())))
        original_guid_terms=[o for o in gs['conversao'].objects(u,PROPS.globalIdIfcRoot_attribute_simple) if str(o)==e.GlobalId]
        declared.add((u,PROPS.globalIdIfcRoot_attribute_simple,original_guid_terms[0] if original_guid_terms else Literal(e.GlobalId)));declared.add((u,PROV.wasDerivedFrom,source))
        if e.Name is not None:declared.add((u,CIV.ifcName,Literal(e.Name)))
        if getattr(e,'LongName',None) is not None:declared.add((u,CIV.ifcLongName,Literal(e.LongName)))
        label=getattr(e,'LongName',None) or e.Name
        if label is not None:declared.add((u,RDFS.label,Literal(label)))
        if e.is_a('IfcSpace'):declared.add((u,RDF.type,BOT.Space))
        elif e.is_a('IfcElement'):declared.add((u,RDF.type,BOT.Element))
        product_rows.append({'GlobalId':e.GlobalId,'classe_ifc':e.is_a(),'Name':e.Name,'LongName':getattr(e,'LongName',None),'uri':str(u),'presente_na_conversao':e.GlobalId in idx})
    def evidence(rel,s,p,o):
        node=URIRef(BASE+'ifc-relation/'+str(rel.id()))
        declared.add((node,RDF.type,RDF.Statement));declared.add((node,RDF.subject,s));declared.add((node,RDF.predicate,p));declared.add((node,RDF.object,o))
        declared.add((node,CIV.ifcStepId,Literal(rel.id())));declared.add((node,CIV.ifcClass,Literal(rel.is_a())));declared.add((node,PROV.wasDerivedFrom,source))
    for rel in model.by_type('IfcRelVoidsElement'):
        s=uri(rel.RelatingBuildingElement);o=uri(rel.RelatedOpeningElement);declared.add((s,CIV.hasOpening,o));evidence(rel,s,CIV.hasOpening,o)
    for rel in model.by_type('IfcRelFillsElement'):
        s=uri(rel.RelatingOpeningElement);o=uri(rel.RelatedBuildingElement);declared.add((s,CIV.hasFilling,o));evidence(rel,s,CIV.hasFilling,o)
    for cls in ['IfcRelAggregates','IfcRelNests']:
        for rel in model.by_type(cls):
            parent=rel.RelatingObject
            if not parent.is_a('IfcProduct'):continue
            for child in rel.RelatedObjects:
                if not child.is_a('IfcProduct'):continue
                p=BOT.hasSpace if child.is_a('IfcSpace') else BOT.hasSubElement if parent.is_a('IfcElement') and child.is_a('IfcElement') else CIV.declaredDecomposition
                declared.add((uri(parent),p,uri(child)))
                node=URIRef(BASE+'decomposition/'+str(rel.id())+'/'+str(child.id()))
                declared.add((node,RDF.type,RDF.Statement));declared.add((node,RDF.subject,uri(parent)));declared.add((node,RDF.predicate,p));declared.add((node,RDF.object,uri(child)));declared.add((node,CIV.ifcStepId,Literal(rel.id())));declared.add((node,PROV.wasDerivedFrom,source))
    g=gs['geometria'];success=0
    for r in data['entidades']:
        if 'cache' not in r:continue
        e=model.by_id(r['id']);u=uri(e);geometry=URIRef(BASE+'geometry/'+r['guid'])
        z=np.load(cache/r['cache']);v=z['vertices'];f=z['faces']
        g.add((u,GEOM.hasGeometry,geometry));g.add((geometry,RDF.type,GEOM.Geometry));g.add((geometry,GEOM.asBody,Literal(tin_wkt(v,f))))
        g.add((geometry,CIV.unit,METRE));g.add((geometry,CIV.coordinateReference,frame));g.add((geometry,CIV.vertexCount,Literal(len(v))));g.add((geometry,CIV.triangleCount,Literal(len(f))))
        g.add((geometry,PROV.wasDerivedFrom,source));g.add((geometry,CIV.meshSettings,Literal(json.dumps(data['configuracao']))))
        for field,key in [('minimum','bbox_min'),('maximum','bbox_max')]:
            for axis,value in zip('XYZ',r[key]):g.add((geometry,CIV[field+axis],Literal(float(value))))
        g.add((geometry,CIV.meshClosed,Literal(r['fechada_por_arestas'])));g.add((geometry,CIV.meshOriented,Literal(r['orientacao_consistente'])))
        success+=1
    for n,r in enumerate(relations['pares']):
        s=uri(model.by_guid(r['ambiente']));o=uri(model.by_guid(r['parede']));qualified=r['status']=='adjacencia_geometrica_no_limiar_numerico'
        graph=gs['derivado'] if qualified else gs['candidatos'];p=BOT.adjacentElement if qualified else CIV.nearElement
        graph.add((s,p,o));node=URIRef(BASE+'contact/'+str(n));graph.add((node,RDF.type,CIV.GeometricRelationEvidence));graph.add((node,RDF.type,RDF.Statement))
        for pred,obj in [(RDF.subject,s),(RDF.predicate,p),(RDF.object,o),(PROV.wasDerivedFrom,source),(PROV.wasGeneratedBy,execution),(RDFS.seeAlso,PAPER_GRC)]:graph.add((node,pred,obj))
        for pred,val in [('status',r['status']),('contactAreaM2',r['strict_area_m2'] if qualified else r['area_m2']),('strictContactAreaM2',r['strict_area_m2']),('maxGapM',r['max_strict_gap_m'] if qualified else r['max_gap_m']),('distanceThresholdM',STRICT_M),('nearThresholdM',NEAR_M),('angleThresholdDeg',ANGLE_DEG),('volumeThresholdM3',VOLUME_EPS_M3)]:graph.add((node,CIV[pred],Literal(val)))
        if r['intersection_volume_m3'] is not None:graph.add((node,CIV.intersectionVolumeM3,Literal(r['intersection_volume_m3'])))
        for k,surf in enumerate(r['superficies']):
            if qualified and surf['area_estrita_m2']<=MIN_AREA_M2:continue
            sg=URIRef(str(node)+'/surface/'+str(k));graph.add((node,CIV.contactGeometry,sg));graph.add((sg,GEOM.asBody,Literal(surf['wkt_estrito'] if qualified else surf['wkt'])));graph.add((sg,CIV.coordinateReference,frame));graph.add((sg,CIV.unit,METRE))
    for n,r in enumerate(relations.get('falhas_processamento',[])):
        node=URIRef(BASE+'processing-failure/'+str(n))
        for pred,obj in [(RDF.type,CIV.GeometricProcessingFailure),(RDF.subject,uri(model.by_guid(r['ambiente']))),
             (RDF.object,uri(model.by_guid(r['parede']))),(CIV.stage,Literal(r['etapa'])),
             (CIV.errorMessage,Literal(r['erro'])),(PROV.wasDerivedFrom,source),(PROV.wasGeneratedBy,execution)]:
            gs['avaliacao'].add((node,pred,obj))
    union=Graph()
    for prefix,namespace in ds.namespaces():union.bind(prefix,namespace)
    for g in gs.values():
        for triple in g:union.add(triple)
    ds.serialize(output/'arquitetura_grafos_nomeados.trig',format='trig')
    union.serialize(output/'arquitetura_enriquecida.ttl',format='turtle')
    save_csv(output/'preservacao_produtos.csv',product_rows)
    classes=[]
    for cls in ['IfcSpace','IfcWall','IfcDoor','IfcWindow','IfcOpeningElement','IfcCovering','IfcRoof']:
        entities=model.by_type(cls);classes.append({'classe':cls,'origem':len(entities),'na_conversao':sum(e.GlobalId in idx for e in entities),'com_geometria_RDF':sum((uri(e),GEOM.hasGeometry,None) in g for e in entities for g in [gs['geometria']])})
    save_csv(output/'preservacao_por_classe.csv',classes)
    report={'triplas_por_grafo':{k:len(g) for k,g in gs.items()},'triplas_uniao':len(union),'produtos_com_geometria':success,'classes':classes,'nomes_grafos':{k:str(v) for k,v in names.items()},'sha256_ttl':sha(output/'arquitetura_enriquecida.ttl')}
    save_json(output/'registro_rdf.json',report)
    return union,report
