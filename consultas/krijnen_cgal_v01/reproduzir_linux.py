"""Reexecuta o ensaio por componentes a partir do pacote preservado.
Dependências Linux: clang, libcgal-dev (5.6 no ensaio), libgmp-dev, libmpfr-dev.
Não instala pacotes do sistema nem altera IFC ou RDF de entrada.
"""
from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parent
if not (root/'execucao_v02').exists():root=root.parent
target=root/'replica_componentes';target.mkdir(exist_ok=False)
for name in ['ensaio_nef_componentes.cpp','nef_extraido.h','executar_componentes_colab.py']:
    shutil.copy2(root/'codigo'/name,target/name)
for folder in ['entrada','entrada_componentes']:
    shutil.copytree(root/'execucao_v02'/folder,target/folder)
for p in (target/'entrada_componentes').glob('*.partes'):
    p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
subprocess.run([sys.executable,str(target/'executar_componentes_colab.py')],check=True)
