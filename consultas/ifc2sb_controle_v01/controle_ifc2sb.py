"""Teste do programa publicado IFC2SB, sem substituir operadores geométricos.

Fonte: Fichter et al. (2021), DOI 10.26868/25222708.2021.30156.
IFC2SB commit 96a89cdff65f13279c0c3ce67e729ad9f9f5adad, GPL-3.0.
Este arquivo organiza entradas, comandos, limites de duração e registros;
não implementa identificação geométrica de ambientes ou paredes.
O motor reutilizado mantém o filtro original de classes e os ajustes de
compatibilidade OCCT já registrados no notebook de compilação.
"""
from pathlib import Path
import os,json,hashlib,subprocess,sys,time,textwrap
from urllib.request import urlretrieve

RETOMADA=Path('/content/civ2155_ifc2sb_retomada_v01')
RETOMADA.mkdir(exist_ok=True)
BASE_MOTOR=Path('/content/civ2155_ifc2sb')
EXE=BASE_MOTOR/'IFC2SB_FiltroOriginal'
EXE_SHA='63e8c028956055f93ab973a80f2c8be99c95a2faf96b80fce18979210ba077c9'
IFC_SHA='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a'
FZK_URL='https://raw.githubusercontent.com/ibpsa/project1-wp-2-2-bim/a3cba6418feb17f7381b435cccc1f02432e35782/IFC_Files/MISC/AC20-FZK-Haus.ifc'
FZK_SHA='ea6f04eaf92fac4d7ad0038bc3d2dfea4c094dd3f516ecc33c50bf1835ca108d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert EXE.exists() and sha(EXE)==EXE_SHA,'Executável original não encontrado ou diferente do registrado'
assert sha(BASE_MOTOR/'dados/TIPO2-ARQ-DTV_R03.ifc')==IFC_SHA

worker=textwrap.dedent('''
from pathlib import Path
import sys,json,os,subprocess,time,hashlib
p=Path(sys.argv[1]);cfg=json.loads(p.read_text());folder=p.parent
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(cfg['exe'])==cfg['sha256_executavel']
assert sha(cfg['entrada'])==cfg['sha256_entrada']
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',LD_LIBRARY_PATH='/usr/local/lib:'+os.environ.get('LD_LIBRARY_PATH',''))
start=time.monotonic();result=dict(cfg,inicio_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),estado='executando')
dest=folder/'execucao.json';dest.write_text(json.dumps(result,ensure_ascii=False,indent=2))
with (folder/'motor.log').open('w') as log:
 try:
  proc=subprocess.run(cfg['comando'],cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=cfg['limite_segundos'])
  result['retorno']=proc.returncode;result['estado']='processo_concluido'
 except subprocess.TimeoutExpired:
  result['retorno']=124;result['estado']='limite_operacional_atingido'
result['segundos']=time.monotonic()-start
result['sha256_entrada_apos']=sha(cfg['entrada']);result['entrada_preservada']=result['sha256_entrada_apos']==cfg['sha256_entrada']
out=Path(cfg['saida']);result['arquivo_saida_existe']=out.exists()
if out.exists():result['sha256_saida']=sha(out);result['bytes_saida']=out.stat().st_size
result['sha256_log']=sha(folder/'motor.log')
result['aviso']='Retorno zero e arquivo presente não comprovam geração de espaços interiores ou relações corretas; a saída deve ser inspecionada.'
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
''')
(RETOMADA/'worker_execucao.py').write_text(worker,encoding='utf8')

def iniciar_caso(nome,entrada,hash_entrada,limite):
    folder=RETOMADA/nome;folder.mkdir(exist_ok=False)
    original=Path(entrada);assert sha(original)==hash_entrada
    output=folder/(original.stem+'_IFC2SB.ifc')
    cfg={'caso':nome,'artigo':'https://doi.org/10.26868/25222708.2021.30156',
         'codigo_autores':'https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad',
         'exe':str(EXE),'sha256_executavel':EXE_SHA,'filtro_classes':'original dos autores; IfcCovering não ativada',
         'entrada':str(original),'sha256_entrada':hash_entrada,'saida':str(output),
         'comando':[str(EXE),'-j2','--graph',str(original),str(output)],
         'limite_segundos':limite,'nota_limite':'Limite operacional predefinido; seu atingimento não demonstra falha matemática do algoritmo.',
         'nota_metodo':'Programa dos autores com compatibilidade de compilação registrada; sem substituição Python dos operadores geométricos.'}
    config=folder/'configuracao.json';config.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
    log=(folder/'supervisor.log').open('w')
    proc=subprocess.Popen([sys.executable,str(RETOMADA/'worker_execucao.py'),str(config)],stdout=log,stderr=subprocess.STDOUT)
    log.close();(folder/'pid_supervisor.txt').write_text(str(proc.pid))
    print('INICIADO',nome,'PID',proc.pid,'LIMITE',limite,'s',flush=True)
    return folder

controle=RETOMADA/'dados/AC20-FZK-Haus.ifc';controle.parent.mkdir(exist_ok=True)
if not controle.exists():urlretrieve(FZK_URL,controle)
assert sha(controle)==FZK_SHA
(RETOMADA/'fontes_controle.json').write_text(json.dumps({'url':FZK_URL,'sha256':FZK_SHA,
 'nota':'Arquivo com mesmo nome do exemplo no README do IFC2SB; não comprova identidade binária com o exemplar dos autores.',
 'origem':'Repositório IBPSA Project 1; modelo FZK-Haus, crédito IAI/KIT.'},ensure_ascii=False,indent=2),encoding='utf8')
if not (RETOMADA/'01_controle_FZK').exists():iniciar_caso('01_controle_FZK',controle,FZK_SHA,180)
else:print('Caso de controle já existente; os registros não foram sobrescritos.')
print('RAIZ_REPRODUCAO',RETOMADA)
