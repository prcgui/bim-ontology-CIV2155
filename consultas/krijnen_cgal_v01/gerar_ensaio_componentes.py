"""Gera variante controlada com união explícita dos componentes fechados.
Não é portabilidade adicional atribuída a Krijnen: extensão deste estudo,
fundamentada nas operações booleanas Nef documentadas pela CGAL.
https://doc.cgal.org/5.6/Nef_3/index.html
"""
from pathlib import Path
import difflib,zipfile,json,hashlib
R=Path(__file__).resolve().parent
old=(R/'ensaio_nef.cpp').read_text(encoding='utf8')
extra=r'''
// Extensão CIV2155: união dos componentes individualmente fechados e válidos.
// Nef Boolean set union: manual CGAL 5.6, Nef_3. Não desloca coordenadas.
N load_components(const std::string& path){
    auto pos=path.find_last_of("/\\");auto dir=path.substr(0,pos+1);
    std::ifstream list(path+".partes");
    if(!list)throw std::runtime_error("Lista de componentes ausente");
    N result;std::string name;int count=0;
    while(std::getline(list,name)){
        if(name.empty())continue;
        auto part=load((dir+name).c_str());
        result+=part;++count;
    }
    if(!count)throw std::runtime_error("Lista de componentes vazia");
    return result;
}
'''
new=old.replace('void emit(',extra+'\nvoid emit(',1)
new=new.replace('N a=load(argv[2]),b=load(argv[3]);double eps=std::stod(argv[4]);','N a=load_components(argv[2]),b=load_components(argv[3]);double eps=std::stod(argv[4]);')
insert=r'''
        for(double offset:{.5,2.}){
            P b0=box(0,0,0,1,1,1),b1=box(offset,0,0,1,1,1);
            N merged=create_nef_polyhedron(b0);merged+=create_nef_polyhedron(b1);
            std::cout<<"{\"caso\":\""<<(offset==.5?"uniao_sobreposta":"uniao_separada")<<"\",\"eps_m\":0,\"resultado\":";
            emit(merged,"");std::cout<<"}\n";
        }
'''
new=new.replace('    }else{\n        if(argc!=6)',insert+'    }else{\n        if(argc!=6)',1)
assert 'load_components(argv[2])' in new and 'uniao_sobreposta' in new
(R/'ensaio_nef_componentes.cpp').write_text(new,encoding='utf8')
(R/'Preparacao_Componentes.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='v01/ensaio_nef.cpp',tofile='v02/ensaio_nef_componentes.cpp')),encoding='utf8')
t=(R/'executar_colab.py').read_text(encoding='utf8').replace("'ensaio_nef.cpp'","'ensaio_nef_componentes.cpp'")
t=t.replace("volume_expected=name in ['sobreposicao','contido']","volume_expected=name in ['sobreposicao','contido','uniao_sobreposta','uniao_separada']")
t=t.replace("expected=(.2+2*eps)**3 if name=='contido'", "expected=1.5 if name=='uniao_sobreposta' else 2.0 if name=='uniao_separada' else (.2+2*eps)**3 if name=='contido'")
t=t.replace('len(tests)==12','len(tests)==14')
t=t.replace("'natureza':'Ensaio de operações", "'preparacao_componentes':'União Nef de componentes fechados, sem deslocar vértices; extensão do estudo, distinta da entrada composta v01.',\n      'natureza':'Ensaio de operações")
t=t.replace("str(R/'entrada/S00.off'),str(R/'entrada'/obj['arquivo'])","str(R/'entrada_componentes/S00.off'),str(R/'entrada_componentes'/obj['arquivo'])")
(R/'executar_componentes_colab.py').write_text(t,encoding='utf8')
with zipfile.ZipFile(R/'Pacote_Componentes_Krijnen_v02.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['ensaio_nef_componentes.cpp','executar_componentes_colab.py','nef_extraido.h','Proveniencia_Fonte.json','Preparacao_Componentes.diff']:z.write(R/name,name)
    for folder in ['entrada','entrada_componentes']:
        for p in (R/folder).iterdir():z.write(p,folder+'/'+p.name)
print('Variante preparada')
