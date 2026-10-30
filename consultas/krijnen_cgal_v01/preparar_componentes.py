"""Decompõe a malha em componentes por conectividade de faces pelas arestas.
Não desloca vértices, remove faces ou preenche vazios. Alteração só da
representação da entrada OFF; o IFC original não é aberto para escrita.
CGAL Nef: operações booleanas fechadas, conforme Krijnen et al. (2020), §1.2.
União posterior é extensão de preparação deste estudo, não rotina dos autores.
"""
from pathlib import Path
import json,collections,hashlib,zipfile
R=Path(__file__).resolve().parent;dst=R/'entrada_componentes';dst.mkdir(exist_ok=True)
def split(path):
    w=path.read_text().split();nv,nf=int(w[1]),int(w[2]);v=[w[4+3*k:7+3*k] for k in range(nv)];i=4+3*nv;fs=[]
    for _ in range(nf):
        n=int(w[i]);i+=1;fs.append(list(map(int,w[i:i+n])));i+=n
    edge_faces=collections.defaultdict(list)
    for k,f in enumerate(fs):
        for a,b in zip(f,f[1:]+f[:1]):edge_faces[tuple(sorted((a,b)))].append(k)
    adj=collections.defaultdict(set)
    for ids in edge_faces.values():
        for k in ids:adj[k].update(ids)
    unseen=set(range(len(fs)));components=[]
    while unseen:
        seed=min(unseen);unseen.remove(seed);todo=[seed];component=[]
        while todo:
            k=todo.pop();component.append(k)
            for n in sorted(adj[k]):
                if n in unseen:unseen.remove(n);todo.append(n)
        components.append(sorted(component))
    names=[];signed=[]
    for k,ids in enumerate(components):
        vertices=sorted({j for face in ids for j in fs[face]});lookup={v:i for i,v in enumerate(vertices)}
        p=dst/(path.stem+f'_parte{k:02d}.off');names.append(p.name)
        p.write_text('OFF\n'+f'{len(vertices)} {len(ids)} 0\n'+'\n'.join(' '.join(v[j]) for j in vertices)+'\n'+'\n'.join(str(len(fs[j]))+' '+' '.join(str(lookup[x]) for x in fs[j]) for j in ids)+'\n')
        total=0.
        for j in ids:
            assert len(fs[j])==3
            a,b,c=[list(map(float,v[x])) for x in fs[j]]
            total+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        signed.append(total)
    assert all(vol>0 for vol in signed),'Componente interna/invertida/degenerada não aceita para união como sólido positivo'
    (dst/(path.name+'.partes')).write_text('\n'.join(names)+'\n',newline='\n')
    return {'arquivo':path.name,'componentes':len(names),'triangulos_antes':nf,'triangulos_depois':sum(len(c) for c in components),'vertices_inalterados':True,'volumes_assinados_m3':signed,'partes':names}
rows=[split(p) for p in sorted((R/'entrada').glob('*.off'))]
(dst/'Registro_Componentes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
assert all(r['triangulos_antes']==r['triangulos_depois'] for r in rows)
print([(r['arquivo'],r['componentes']) for r in rows])
