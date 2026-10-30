"""Supervisor reprodutível de um ensaio CGAL parcial, sem modificar IFC/RDF.
Krijnen et al. (2020), §3.3, Zenodo 3633653. Harness específico deste estudo.
"""
from pathlib import Path
import subprocess,json,hashlib,time,platform,sys,math
R=Path(__file__).resolve().parent
def save(name,d):(R/name).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
    start=time.monotonic();(R/'intersecoes').mkdir(exist_ok=True)
    cfg=json.loads((R/'entrada/Registro_Entrada.json').read_text())
    for r in cfg['objetos']:assert sha(R/'entrada'/r['arquivo'])==r['sha256_off']
    cmd=['clang++','-std=c++17','-O1',str(R/'ensaio_nef.cpp'),'-o',str(R/'ensaio_nef'),'-lgmp','-lmpfr']
    t=time.monotonic();p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
    (R/'Compilacao.log').write_text(p.stdout+p.stderr)
    save('Compilacao.json',{'comando':cmd,'retorno':p.returncode,'segundos':time.monotonic()-t})
    assert p.returncode==0,p.stderr[-3500:]
    c=subprocess.run([str(R/'ensaio_nef'),'controle'],capture_output=True,text=True,timeout=90)
    (R/'Controles.log').write_text(c.stdout+c.stderr)
    assert c.returncode==0,c.stderr[-3500:]
    tests=[]
    for line in c.stdout.splitlines():
        d=json.loads(line);eps=d['eps_m'];name=d['caso'];x=d['resultado']
        volume_expected=name in ['sobreposicao','contido'] or (eps>0 and name in ['contato','fresta_10um','aresta'])
        nonempty_expected=name not in ['fresta_10um','fresta_1mm'] or (eps>0 and name=='fresta_10um')
        # Expectativas analíticas de caixas, independentes do motor CGAL.
        expected=(.2+2*eps)**3 if name=='contido' else ((.1+2*eps)*(1+2*eps)**2 if name=='sobreposicao' else None)
        d['esperado_volume_3d']=volume_expected;d['esperado_nao_vazio']=nonempty_expected
        d['volume_analitico_m3']=expected
        d['aprovado']=x['volume_3d_presente']==volume_expected and x['nao_vazio']==nonempty_expected and (expected is None or math.isclose(x['volume_m3'],expected,rel_tol=1e-8,abs_tol=1e-12))
        tests.append(d)
    save('Controles.json',{'testes':tests,'aprovados':sum(t['aprovado'] for t in tests),'total':len(tests)})
    assert len(tests)==12 and all(t['aprovado'] for t in tests),'Controles não aprovados; não executar creche'
    result={'estado':'executando','artigo':cfg['artigo'],'fonte':cfg['codigo_depositado'],
      'natureza':'Ensaio de operações CGAL/Nef isoladas com geometria OFF de IfcOpenShell/OpenCascade; não é reprodução integral do método de 2020.',
      'sha256_entrada':sha(R/'entrada/Registro_Entrada.json'),'sha256_executavel':sha(R/'ensaio_nef'),
      'limite_par_segundos':45,'limite_ensaio_segundos':600,'eps_m':[0.,1e-5],
      'nota_eps':'eps é a meia-aresta do cubo de padding; ambos os operandos são expandidos, alcance relativo por eixo até 2 eps. Não é tolerância normativa.',
      'sistema':platform.platform(),'python':sys.version,
      'pacotes':subprocess.run(['dpkg-query','-W','libcgal-dev','libgmp-dev','libmpfr-dev','clang'],capture_output=True,text=True).stdout,
      'casos':[]}
    save('Execucao.json',result)
    for obj in cfg['objetos'][1:]:
      for eps in [0.,1.e-5]:
        tag=obj['codigo']+('_e0' if eps==0 else '_e1e5')
        if time.monotonic()-start>600:
            result['casos'].append({'codigo':obj['codigo'],'eps_m':eps,'estado':'nao_executado_limite_total'})
            continue
        cmd=[str(R/'ensaio_nef'),'par',str(R/'entrada/S00.off'),str(R/'entrada'/obj['arquivo']),str(eps),str(R/'intersecoes'/tag)]
        t=time.monotonic();row={'codigo':obj['codigo'],'guid':obj['guid'],'eps_m':eps,'comando':cmd}
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
            (R/(tag+'.log')).write_text(p.stdout+p.stderr)
            row.update(retorno=p.returncode,estado='concluido' if p.returncode==0 else 'rejeitado_ou_erro')
            if p.returncode==0:row['resultado']=json.loads(p.stdout)
            else:row['motivo']=p.stderr[-1800:]
        except subprocess.TimeoutExpired as e:
            row.update(retorno=124,estado='limite_por_par_atingido');(R/(tag+'.log')).write_bytes((e.stdout or b'')+(e.stderr or b''))
        row['segundos']=time.monotonic()-t;result['casos'].append(row);save('Execucao.json',result)
        print(tag,row['estado'],round(row['segundos'],2),flush=True)
    result['estado']='concluido';result['segundos_total']=time.monotonic()-start
    result['entradas_off_preservadas']=all(sha(R/'entrada'/o['arquivo'])==o['sha256_off'] for o in cfg['objetos'])
    save('Execucao.json',result)
    print('ENSAIO_CONCLUIDO',len(result['casos']),flush=True)
if __name__=='__main__':run()
