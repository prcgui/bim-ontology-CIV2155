# 8. Correção documentada da leitura dos textos e nova conversão
#
# FINALIDADE
# Repetir a conversão do MESMO IFC com duas correções locais de leitura.
# Não substitui palavras no Turtle nem copia valores esperados para o grafo.
# A saída original das células 4 a 7 é mantida para a comparação posterior.
#
# PROBLEMAS IDENTIFICADOS E ALTERAÇÕES
# 1. StringOperations.handleUnicode(): a tabela do conversor contém saídas
#    corrompidas para caracteres isolados de sequências STEP X2. As 66 entradas
#    são escritas como escapes Unicode Java, com o código indicado na própria
#    sequência IFC. Exemplos: 00C7 = Ç; 00C1 = Á; 00E7 = ç.
# 2. RDFWriter.filterExtras(): a rotina elimina os apóstrofos dos valores.
#    Para tokens textuais iniciados pela aspa de abertura do parser utilizado,
#    remove-se apenas essa abertura, preservando apóstrofos internos e "=".
#    O comportamento anterior é mantido para tokens não textuais.
#
# BASE TÉCNICA E ORIGEM DA ADAPTAÇÃO
# 1. buildingSMART, IFC String Encoding: sequências X2 representam códigos
#    Unicode de 16 bits. Fundamenta a interpretação dos caracteres no IFC.
# https://technical.buildingsmart.org/resources/ifcimplementationguidance/string-encoding/
# 2. Oracle, Java Language Specification, Java SE 21, seção 3.3: escapes
#    Unicode Java representam o código hexadecimal indicado. Fundamenta a
#    escrita das entradas da tabela como escapes, por exemplo, \\u00C7.
# https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.3
# 3. Código-fonte do IFCtoLBD: handleUnicode contém a tabela examinada;
#    filterExtras remove apóstrofos e "=". A análise de IfcSpfParser (estados
#    2 e 3) identifica a aspa inicial conservada no token textual recebido.
#    Essa leitura fundamenta remover apenas a abertura desses tokens.
# Fontes fixadas no commit ca7811b7132a843b85beee748d255f9b5b709e07:
# https://github.com/jyrkioraskari/IFCtoLBD/blob/ca7811b7132a843b85beee748d255f9b5b709e07/IFCtoLBD/src/main/java/org/linkedbuildingdata/ifc2lbd/core/utils/StringOperations.java
# https://github.com/jyrkioraskari/IFCtoLBD/blob/ca7811b7132a843b85beee748d255f9b5b709e07/IFCtoRDF/src/main/java/be/ugent/RDFWriter.java
# https://github.com/jyrkioraskari/IFCtoLBD/blob/ca7811b7132a843b85beee748d255f9b5b709e07/IFCtoRDF/src/main/java/be/ugent/IfcSpfParser.java
# 4. Oracle, API String, Java SE 21: startsWith identifica o prefixo;
#    substring(1) preserva o conteúdo após o primeiro caractere.
# https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html#substring(int)
#
# A implementação específica é uma adaptação local deste estudo, fundamentada
# nessas fontes e verificada pelos testes abaixo. Não é uma correção publicada
# pelos autores nem um trecho extraído dos artigos citados. A conversão mantém
# o IFCtoLBD 2.49.0 e a referência geral Bonduel et al. (2018), da célula 4.
#
# COMO A INTERVENÇÃO É VERIFICADA
# Confere os fontes por SHA-256; compila somente as duas classes alteradas;
# verifica a compatibilidade das interfaces públicas; executa testes de texto;
# coloca as classes corrigidas antes dos JARs originais no caminho de execução.
# A nova conversão mantém os parâmetros da célula 4 e gera arquivos separados.
# O registro inclui fontes, diferenças, comandos, testes e hashes.

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

pasta_correcao = Path("/content/correcao_textual")
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
javac = Path(str(java)).with_name("javac")
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
javap = Path(str(java)).with_name("javap")
for classe in ["be.ugent.RDFWriter", "org.linkedbuildingdata.ifc2lbd.core.utils.StringOperations"]:
    assinaturas = [
        subprocess.run([str(javap), "-public", "-cp", cp, classe],
                       check=True, capture_output=True, text=True).stdout
        for cp in [classpath, classpath_corrigido]
    ]
    if assinaturas[0] != assinaturas[1]:
        raise ValueError("A classe corrigida tem interface incompatível: " + classe)

# Testes independentes: caracteres isolados, sequências combinadas e apóstrofos.
codigo_teste = r'''
import org.linkedbuildingdata.ifc2lbd.core.utils.StringOperations;
public class TesteTextosCIV2155 {
 public static void main(String[] args) throws Exception {
  String[][] unicode = {
   {"BER\\X2\\00C7\\X0\\ARIO", "BER\u00C7ARIO"},
   {"SOL\\X2\\00C1\\X0\\RIO", "SOL\u00C1RIO"},
   {"Servi\\X2\\00E7\\X0\\o", "Servi\u00E7o"},
   {"CIRCULA\\X2\\00C700C3\\X0\\O", "CIRCULA\u00C7\u00C3O"},
   {"COZINHA", "COZINHA"},
   {"CASTELO D'\\X2\\00C1\\X0\\GUA", "CASTELO D'\u00C1GUA"}
  };
  for (String[] par : unicode)
   if (!StringOperations.handleUnicode(par[0]).equals(par[1]))
    throw new AssertionError("Unicode: " + par[0]);
  java.lang.reflect.Method filtro =
   Class.forName("be.ugent.RDFWriter").getDeclaredMethod("filterExtras", String.class);
  filtro.setAccessible(true);
  String[][] tokens = {
   {"'CASTELO D'\u00C1GUA", "CASTELO D'\u00C1GUA"},
   {"'COZINHA", "COZINHA"}, {"'A=B", "A=B"}, {"'d'agua", "d'agua"}
  };
  for (String[] par : tokens)
   if (!filtro.invoke(null, par[0]).equals(par[1]))
    throw new AssertionError("Token: " + par[0]);
  System.out.println("10/10 testes de texto aprovados.");
 }
}
'''
teste_java = pasta_correcao / "TesteTextosCIV2155.java"
teste_java.write_text(codigo_teste, encoding="utf-8")
subprocess.run([str(javac), "-encoding", "UTF-8", "-cp", classpath_corrigido,
                "-d", str(classes_corrigidas), str(teste_java)], check=True, capture_output=True)
teste = subprocess.run([str(java), "-cp", classpath_corrigido, "TesteTextosCIV2155"],
                       check=True, capture_output=True, text=True)
(pasta_resultados_corrigidos / "testes_textos.txt").write_text(teste.stdout, encoding="utf-8")
print(teste.stdout.strip())

# Nova execução do conversor: mudam somente as classes de texto e o destino.
arquivo_ttl_corrigido = pasta_resultados_corrigidos / "creche_tipo2_lbd_corrigido.ttl"
comando_corrigido = list(comando_conversao)
comando_corrigido[comando_corrigido.index("-cp") + 1] = classpath_corrigido
comando_corrigido = [
    "--target_file=" + str(arquivo_ttl_corrigido) if a.startswith("--target_file=") else a
    for a in comando_corrigido
]
inicio = time.perf_counter()
print("Executando o mesmo IFC com as correções locais de texto...")
with (pasta_resultados_corrigidos / "conversao_corrigida.log").open("w", encoding="utf-8") as log:
    execucao_corrigida = subprocess.run(
        comando_corrigido, cwd=pasta_resultados_corrigidos,
        stdout=log, stderr=subprocess.STDOUT, timeout=900,
    )
execucao_corrigida.check_returncode()
if hashlib.sha256(arquivo_ifc.read_bytes()).hexdigest() != hash_esperado:
    raise ValueError("O IFC de entrada foi alterado.")
grafo_corrigido = Graph().parse(str(arquivo_ttl_corrigido), format="turtle")
registro_correcao = {
    "motor_base": "IFCtoLBD", "versao_base": versao_motor,
    "intervencao": "correcoes locais CIV2155: Unicode e apostrofos",
    "commit_fontes": commit_fonte, "fontes": registro_fontes,
    "sha256_ifc": hash_esperado, "sha256_pacote_motor": hash_motor,
    "comando": comando_corrigido, "codigo_saida": execucao_corrigida.returncode,
    "sha256_grafo_original": hashlib.sha256(arquivo_ttl.read_bytes()).hexdigest(),
    "sha256_grafo_corrigido": hashlib.sha256(arquivo_ttl_corrigido.read_bytes()).hexdigest(),
    "triplas_original": len(grafo_lbd), "triplas_corrigido": len(grafo_corrigido),
    "testes": teste.stdout.strip(), "duracao_segundos": round(time.perf_counter() - inicio, 1),
}
(pasta_resultados_corrigidos / "registro_correcao.json").write_text(
    json.dumps(registro_correcao, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Conversão concluída. Triplas:", len(grafo_corrigido))
print("IFC e grafo original mantidos. Próxima etapa: repetir a comparação dos valores.")
