"""IFCtoLBD 2.49.0: mesma conversão e correção textual usadas no estudo.

Fontes originais verificadas por SHA-256 antes de duas adaptações:
66 escapes Unicode na tabela e preservação do conteúdo do token STEP.
As fontes e dependências mantêm suas licenças de origem.
"""
from pathlib import Path
import os, subprocess, zipfile, hashlib, time
from urllib.request import urlretrieve
from rdflib import Graph

def converter(ifc, destino, trabalho, *,
              ifc_sha256='0975bf1394694eff8746e5e49232bdf950c36c37c858edb715c9e7bc8f65603a',
              base_uri='https://github.com/prcgui/bim-ontology-CIV2155/id/notebook1-v03/',
              java_heap='4g'):
    """Mesmo extrator para diferentes disciplinas; origem e namespace explícitos.

    Os padrões preservam a chamada e as identidades usadas pelo Notebook 1.
    O Notebook 2 informa os hashes e namespaces de cada modelo estrutural.
    """
    import difflib,hashlib,json,os,re,subprocess,time,shutil
    from pathlib import Path
    from urllib.request import urlretrieve
    from rdflib import Graph
    rdf_destino=Path(destino).resolve()
    ROOT=Path(trabalho).resolve();ROOT.mkdir(parents=True,exist_ok=True)
    PASTA_RESULTADOS=ROOT/'conversao';PASTA_RESULTADOS.mkdir(exist_ok=True)
    sha256=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if not re.fullmatch(r'[0-9a-f]{64}',ifc_sha256) or sha256(ifc)!=ifc_sha256:
        raise ValueError('IFC diferente da fonte declarada.')
    if not base_uri.startswith(('https://','http://')) or not base_uri.endswith('/'):
        raise ValueError('Informar namespace absoluto terminado em /.')
    if not re.fullmatch(r'[1-9][0-9]*[mg]',java_heap):
        raise ValueError('Limite de memória Java inválido.')
    entrada_motor=Path(ifc).resolve()
    if not entrada_motor.name.endswith('.ifc'):
        # A CLI 2.49.0 acrescenta .ifc ao nome com extensão .IFC maiúscula.
        # Compatibilizar só o nome de uma cópia de trabalho, mantendo os bytes.
        entrada_motor=ROOT/'entrada_motor.ifc'
        shutil.copyfile(ifc,entrada_motor)
        if sha256(entrada_motor)!=ifc_sha256:raise ValueError('Cópia de entrada alterada.')
    MOTOR=Path(os.environ.get("CIV2155_MOTOR",ROOT/"motor"));MOTOR.mkdir(parents=True,exist_ok=True)
    pacote_motor=MOTOR/"IFCtoLBD.zip"
    if not pacote_motor.exists():urlretrieve("https://github.com/jyrkioraskari/IFCtoLBD/releases/download/2.49.0/IFCtoLBD.zip",pacote_motor)
    HASH_MOTOR="49dc8833418cadf552fd688eca8f56499c5d1dad8783712aab56825b84bba14e"
    assert sha256(pacote_motor)==HASH_MOTOR
    lib=MOTOR/"IFCtoLBD/IFCtoLBD-Desktop_Java_21_lib"
    if not lib.exists():
        with zipfile.ZipFile(pacote_motor) as z:z.extractall(MOTOR)
    java=Path(os.environ.get("CIV2155_JAVA","/usr/lib/jvm/java-21-openjdk-amd64/bin/java"))
    if not java.is_file():
        if os.name=="nt":raise RuntimeError("Definir CIV2155_JAVA com Java 21 JDK")
        subprocess.run(["apt-get","-qq","update"],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(["apt-get","-qq","install","-y","openjdk-21-jdk-headless"],check=True,stdout=subprocess.DEVNULL)
    classpath=str(lib/"*")
    classe_cli="org.linkedbuildingdata.ifc2lbd.IFCtoLBDConverter_CLI"
    pasta_resultados=PASTA_RESULTADOS
    print(subprocess.run([str(java),"-version"],capture_output=True,text=True,check=True).stderr.splitlines()[0])

    import difflib
    import hashlib
    import json
    import os
    import re
    import subprocess
    import time
    from pathlib import Path
    from urllib.request import urlretrieve
    from rdflib import Graph

    pasta_correcao = ROOT / "correcao_textual"
    pasta_correcao.mkdir(exist_ok=True)
    pasta_resultados_corrigidos = pasta_resultados / "correcao_textual"
    pasta_resultados_corrigidos.mkdir(exist_ok=True)
    commit_fonte = "ca7811b7132a843b85beee748d255f9b5b709e07"
    base_fonte = "https://raw.githubusercontent.com/jyrkioraskari/IFCtoLBD/" + commit_fonte + "/"
    fontes = {
        "StringOperations.java": (
            "IFCtoLBD/src/main/java/org/linkedbuildingdata/ifc2lbd/core/utils/StringOperations.java",
            "5f7e65b41d6ce9acd00e03c38070f533a6902575a3f201629cc3b56708dced13",
        ),
        "RDFWriter.java": (
            "IFCtoRDF/src/main/java/be/ugent/RDFWriter.java",
            "6924f236cb17fd6cf89bcf69e393a874a22f964be84d4c1e6a46c5cc01433621",
        ),
    }
    registro_fontes, diferencas = {}, []
    for nome, (caminho, esperado) in fontes.items():
        original = pasta_correcao / ("original_" + nome)
        urlretrieve(base_fonte + caminho, original)
        dados = original.read_bytes()
        if hashlib.sha256(dados).hexdigest() != esperado:
            raise ValueError("Fonte diferente da versão documentada: " + nome)
        texto_original = dados.decode("utf-8")
        texto_corrigido = texto_original
        if nome == "StringOperations.java":
            padrao = r'(line = line\.replace\("\\\\X2\\\\([0-9A-Fa-f]{4})\\\\X0\\\\", ")[^"\n]*("\);)'
            texto_corrigido, quantidade = re.subn(
                padrao, lambda m: m[1] + "\\u" + m[2] + m[3], texto_original
            )
            if quantidade != 66:
                raise ValueError("A tabela Unicode tem uma estrutura não prevista.")
        else:
            inicio = "private static String filterExtras(String txt) {\n"
            acrescimo = (
                '\t\t// CIV2155: preserve the content of the parser string token.\n'
                '\t\tif (txt.startsWith("\'")) return txt.substring(1);\n'
            )
            if texto_original.count(inicio) != 1:
                raise ValueError("A função de leitura de texto não foi localizada.")
            texto_corrigido = texto_original.replace(inicio, inicio + acrescimo, 1)
        destino = pasta_correcao / nome
        destino.write_text(texto_corrigido, encoding="utf-8")
        registro_fontes[nome] = {
            "url": base_fonte + caminho, "sha256_original": esperado,
            "sha256_corrigido": hashlib.sha256(destino.read_bytes()).hexdigest(),
        }
        diferencas.extend(difflib.unified_diff(
            texto_original.splitlines(keepends=True),
            texto_corrigido.splitlines(keepends=True),
            fromfile="original/" + nome, tofile="corrigido/" + nome,
        ))
    (pasta_resultados_corrigidos / "alteracoes.patch").write_text("".join(diferencas), encoding="utf-8")

    # O compilador é necessário somente para preparar as duas classes modificadas.
    javac = Path(str(java)).with_name("javac.exe" if os.name=="nt" else "javac")
    if not javac.is_file():
        subprocess.run(["apt-get", "-qq", "update"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["apt-get", "-qq", "install", "-y", "openjdk-21-jdk-headless"],
                       check=True, stdout=subprocess.DEVNULL)
    classes_corrigidas = pasta_correcao / "classes"
    classes_corrigidas.mkdir(exist_ok=True)
    subprocess.run([
        str(javac), "-encoding", "UTF-8", "-cp", classpath, "-d", str(classes_corrigidas),
        str(pasta_correcao / "StringOperations.java"), str(pasta_correcao / "RDFWriter.java"),
    ], check=True, capture_output=True, text=True)
    classpath_corrigido = str(classes_corrigidas) + os.pathsep + classpath

    destino=rdf_destino;destino.parent.mkdir(parents=True,exist_ok=True)
    cmd=[str(java),'-Xmx'+java_heap,'-Dfile.encoding=UTF-8','-cp',classpath_corrigido,classe_cli,str(entrada_motor),
      '--url='+base_uri,
      '--target_file='+str(destino),'--level=1','--hasBuildingElements=true',
      '--hasBuildingElementProperties=true','--hasIfc_based_elements=true',
      '--hasSeparateBuildingElementsModel=false','--hasSeparatePropertiesModel=false',
      '--propertiesAsPropertySets=false','--hasUnits=true','--hasGeometry=false','--ifcOWL=false']
    inicio=time.perf_counter()
    with (PASTA_RESULTADOS/'conversao.log').open('w',encoding='utf8') as log:
        subprocess.run(cmd,cwd=PASTA_RESULTADOS,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
    grafo=Graph().parse(destino,format='turtle')
    print('Conversão executada:',len(grafo),'triplas;',round(time.perf_counter()-inicio,1),'s')
    return destino
