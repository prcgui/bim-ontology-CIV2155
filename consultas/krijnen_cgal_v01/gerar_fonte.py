"""Extrai corpo publicado sem alteração e registra hashes e diferenças."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
S=R/'fonte_2020/aothms-IfcOpenShell-60b1604'
def sha(b):return hashlib.sha256(b).hexdigest()
def body(text,needle):
    start=text.index(needle);brace=text.index('{',start);depth=1;i=brace+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]
t=(S/'src/ifcgeom/kernels/cgal/CgalKernel.cpp').read_text()
needle='CGAL::Nef_polyhedron_3<Kernel_> ifcopenshell::geometry::utils::create_nef_polyhedron(CGAL::Polyhedron_3<Kernel_> &polyhedron)'
original=body(t,needle)
header='using Kernel_=K;\n'+original.replace('ifcopenshell::geometry::utils::','',1)+'\n'
(R/'nef_extraido.h').write_text(header,encoding='utf8')
manifest={'deposito':'https://doi.org/10.5281/zenodo.3633653','versao':'v0.7.0-validation','commit_curto_arquivo':'60b1604',
 'sha256_zip':sha((R/'IfcOpenShell-v0.7.0-validation.zip').read_bytes()),'md5_zip':hashlib.md5((R/'IfcOpenShell-v0.7.0-validation.zip').read_bytes()).hexdigest(),
 'funcao_extraida':needle,'sha256_funcao_original_texto':sha(original.encode()),
 'alteracao_extracao':'Removido apenas o qualificador de namespace da assinatura; alias Kernel_ e Logger mínimo no adaptador. Corpo preservado.',
 'diferencas_adaptador':['IfcOpenShell 0.8.4/OpenCascade triangula o IFC, em vez da interpretação CGAL de 2020.',
 'Cubo com mesmo domínio [-eps,+eps]^3 criado com CGAL make_hexahedron em vez do construtor próprio dos autores.',
 'Não executa o programa IfcConvert completo, conversão de limites declarados, remove_thickness nem escrita de IfcRelSpaceBoundary.',
 'Sem a filtragem de caixas da fonte: testa todos os 34 pares do recorte, reduzindo interferência da pré-seleção neste conjunto.',
 'Acrescenta rejeição de malha com autointerseção/orientação incompatível, limite de tempo por par e medição regularizada de volume.',
 'A interseção que decide nao_vazio permanece não regularizada; contato de dimensão inferior é registrado separadamente.'],
 'fontes_preservadas':[]}
old=R.parents[1]/'desenvolvimento/fontes_geometria_publicadas'
for p in ['src/ifcconvert/validation_utils.h','src/ifcconvert/validate_space_boundaries.cpp','src/ifcgeom/kernels/cgal/CgalKernel.cpp','src/ifcgeom/kernels/cgal/CgalConversionResult.h']:
    f=S/p;manifest['fontes_preservadas'].append({'arquivo':p,'sha256':sha(f.read_bytes())})
(R/'Proveniencia_Fonte.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
assert manifest['md5_zip']=='d47b7b7609dab0f88c49fd8dfd4ddb16'
with zipfile.ZipFile(R/'Pacote_Ensaio_Krijnen_v01.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['ensaio_nef.cpp','nef_extraido.h','Proveniencia_Fonte.json'] :z.write(R/name,name)
    for p in (R/'entrada').iterdir():z.write(p,'entrada/'+p.name)
print('Fonte/entrada prontas',manifest['sha256_zip'])
