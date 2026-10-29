"""Compila e executa IFC2SB dos autores em Linux (Colab), com ajustes registrados.
Fontes: Fichter et al. (2021), DOI 10.26868/25222708.2021.30156;
https://github.com/RWTH-E3D/IFC2SB/tree/96a89cdff65f13279c0c3ce67e729ad9f9f5adad
Preparação de ambiente adaptada do add/Dockerfile dos autores. Não altera algoritmos.
"""
from pathlib import Path
from urllib.request import urlopen,urlretrieve
import subprocess,os,sys,json,hashlib,zipfile,time,platform,threading
from compatibilidade_occt import adaptar_occt,adaptar_occt_functions,adaptar_occt_cpp,adaptar_occt_curve,adaptar_includes_motor,adaptar_includes_octree,adaptar_occt_writer

if platform.system()!='Linux':raise RuntimeError('Este teste de compilação requer Linux.')
ROOT=Path('/content/civ2155_ifc2sb');ROOT.mkdir(exist_ok=True)
LOGS=ROOT/'logs';LOGS.mkdir(exist_ok=True)
if (ROOT/'manifesto_execucao.json').exists():
 (ROOT/'manifesto_execucao.json').rename(LOGS/('manifesto_anterior_'+str(time.time_ns())+'.json'))
env=dict(os.environ,DEBIAN_FRONTEND='noninteractive',QT_QPA_PLATFORM='offscreen')
env['LD_LIBRARY_PATH']='/usr/local/lib:'+env.get('LD_LIBRARY_PATH','')
manifest={'etapas':[],'inicio_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'artigo':'https://doi.org/10.26868/25222708.2021.30156',
 'ifc2sb_commit':'96a89cdff65f13279c0c3ce67e729ad9f9f5adad',
 'observacao':'Preparação de ambiente adaptada; algoritmos IFC2SB originais.'}
def save():
 (ROOT/'manifesto_execucao.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
def run(stage,command,cwd=None,timeout=3600):
 print('\nETAPA:',stage,flush=True)
 log=LOGS/(stage+'.log');t=time.monotonic()
 if log.exists():
  backup=log.with_name(log.stem+'_'+str(time.time_ns())+'.log')
  log.rename(backup)
 with log.open('w') as fp:
  p=subprocess.Popen(command,cwd=cwd,env=env,stdout=fp,stderr=subprocess.STDOUT)
  last=''
  while p.poll() is None:
   time.sleep(10)
   lines=log.read_text(errors='replace').splitlines()
   tail=' | '.join(lines[-2:])[-400:]
   if tail!=last:print(stage,round(time.monotonic()-t),'s:',tail,flush=True);last=tail
   if time.monotonic()-t>timeout:p.terminate();raise TimeoutError(stage)
  rc=p.returncode
 manifest['etapas'].append({'etapa':stage,'comando':command,'retorno':rc,'segundos':round(time.monotonic()-t,1),'log':str(log.relative_to(ROOT))});save()
 if rc:
  lines=log.read_text(errors='replace').splitlines()
  for i,line in enumerate(lines):
   if 'error:' in line or 'CMake Error' in line:
    print('\n'.join(lines[max(0,i-2):i+6]),flush=True)
  print('\n'.join(lines[-35:]),flush=True)
  raise RuntimeError(stage+' falhou: '+str(rc))
def archive(repo,ref):
 zip_path=ROOT/(repo.split('/')[-1]+'_'+ref[:12]+'.zip')
 if not zip_path.exists():urlretrieve('https://codeload.github.com/'+repo+'/zip/'+ref,zip_path)
 out=ROOT/(repo.split('/')[-1]+'_fonte');out.mkdir(exist_ok=True)
 with zipfile.ZipFile(zip_path) as z:
  for member in z.infolist():
   q=Path(member.filename)
   if q.is_absolute() or '..' in q.parts:raise ValueError('Caminho inválido no ZIP')
  z.extractall(out)
 return next(p for p in out.iterdir() if p.is_dir())

print(platform.platform(),flush=True)
run('01_apt_update',['apt-get','update','-qq'])
packages=['build-essential','clang','cmake','ninja-build','git','libboost-all-dev',
 'libxml2-dev','libcgal-dev','libgmp-dev','libmpfr-dev','libtbb-dev','libomp-dev',
 'qtbase5-dev','libpolyclipping-dev','libglu1-mesa-dev',
 'libocct-foundation-dev','libocct-modeling-data-dev','libocct-modeling-algorithms-dev',
 'libocct-ocaf-dev','libocct-data-exchange-dev','libocct-visualization-dev','libocct-draw-dev']
run('02_dependencias',['apt-get','install','-y','--no-install-recommends']+packages)
manifest['ambiente']={'sistema':platform.platform(),'python':sys.version,
 'pacotes':subprocess.check_output(['dpkg-query','-W','-f=${Package}=${Version}\n',
 'clang','cmake','libocct-foundation-dev','libboost-all-dev','libcgal-dev','libtbb-dev','libomp-dev'],text=True)}
save()
repo='IfcOpenShell/IfcOpenShell'
sha='b8d36a63a29f37193f52027b421607f7c37434ce'
manifest['ifcopenshell_v060_commit']=sha;save()
ifcos=archive(repo,sha)
motor=archive('RWTH-E3D/IFC2SB',manifest['ifc2sb_commit'])
adaptar_occt(ifcos,LOGS);adaptar_occt_functions(ifcos,LOGS);adaptar_occt_cpp(ifcos,LOGS)
adaptar_occt_curve(ifcos,LOGS)
adaptar_includes_motor(motor,LOGS)
adaptar_includes_octree(motor,LOGS)
adaptar_occt_writer(motor,LOGS)
manifest['ajustes_compatibilidade']=[str(p.relative_to(ROOT)) for p in LOGS.glob('compatibilidade*.diff')];save()
manifest['sha256_fontes_zip']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.zip') if p.name.startswith(('IfcOpenShell_','IFC2SB_'))}
manifest['sha256_diffs']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in LOGS.glob('compatibilidade*.diff')};save()
build_ifcos=ROOT/'build_ifcopenshell';build_ifcos.mkdir(exist_ok=True)
occt_dirs=list(Path('/usr').glob('lib/*/cmake/opencascade'))
if not occt_dirs:occt_dirs=list(Path('/usr').glob('lib/cmake/opencascade'))
opts=['-DBUILD_CONVERT=OFF','-DBUILD_IFCPYTHON=OFF','-DBUILD_GEOMSERVER=OFF',
 '-DBUILD_EXAMPLES=OFF','-DBUILD_DOCUMENTATION=OFF','-DBUILD_PACKAGE=OFF',
 '-DCOLLADA_SUPPORT=OFF','-DGLTF_SUPPORT=OFF','-DIFCXML_SUPPORT=OFF',
 '-DBUILD_SHARED_LIBS=ON','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=-O1 -DNDEBUG',
 '-DCMAKE_CXX_COMPILER=clang++','-DCMAKE_C_COMPILER=clang',
 '-DSCHEMA_VERSIONS=2x3;4;4x1;4x2;4x3_rc1','-DOCC_INCLUDE_DIR=/usr/include/opencascade',
 '-DCMAKE_INSTALL_PREFIX=/usr/local']
run('03_configura_ifcopenshell',['cmake','-S',str(ifcos/'cmake'),'-B',str(build_ifcos)]+opts)
run('04_compila_ifcopenshell',['cmake','--build',str(build_ifcos),'--parallel','2'],timeout=5400)
run('05_instala_ifcopenshell',['cmake','--install',str(build_ifcos)])
run('06_ldconfig',['ldconfig'])
build_motor=ROOT/'build_ifc2sb';build_motor.mkdir(exist_ok=True)
run('07_configura_ifc2sb',['cmake','-S',str(motor/'cmake'),'-B',str(build_motor),
 '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS_RELEASE=-O1 -DNDEBUG',
 '-DCMAKE_CXX_COMPILER=clang++','-DCMAKE_C_COMPILER=clang',
 '-DCLIPPER_INCLUDE_PATH=/usr/include/polyclipping'])
run('08_compila_ifc2sb',['cmake','--build',str(build_motor),'--target','IFC2SB','--parallel','2'],timeout=5400)
exe=build_motor/'IFC2SB'
run('09_ajuda_motor',[str(exe),'--help'])

# Compilação somente. Os ensaios ficam em controle_ifc2sb.py.
import shutil
shutil.copy2(exe,ROOT/'IFC2SB_FiltroOriginal')
print('SHA256_BINARIO_COMPILADO',hashlib.sha256(exe.read_bytes()).hexdigest())
