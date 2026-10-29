"""Ajuste da API Poly_Triangulation para OCCT 7.6; não altera IFC2SB.
Referência técnica: https://dev.opencascade.org/doc/refman/html/class_poly___triangulation.html
Troca o acesso às tabelas removidas pelos métodos Node, UVNode e NbNodes.
O diff é preservado para auditoria. Deve ser aplicado antes da compilação.
"""
from pathlib import Path
import difflib,hashlib,json

def adaptar_occt(ifcos,logs):
    path=Path(ifcos)/'src/ifcgeom/IfcGeomRepresentation.h'
    old=path.read_text()
    replacements={
      'const TColgp_Array1OfPnt& nodes = tri->Nodes();':'// CIV2155: OCCT 7.6 usa acesso Node(i).',
      'const TColgp_Array1OfPnt2d& uvs = tri->UVNodes();':'// CIV2155: OCCT 7.6 usa acesso UVNode(i).',
      'i <= nodes.Length()':'i <= tri->NbNodes()',
      'nodes(i).Transformed(loc)':'tri->Node(i).Transformed(loc)',
      'const gp_Pnt2d& uv = uvs(i);':'const gp_Pnt2d uv = tri->UVNode(i);'}
    if 'CIV2155: OCCT 7.6' in old:return
    new=old
    for a,b in replacements.items():
        assert a in new,a
        new=new.replace(a,b)
    path.write_text(new)
    log=Path(logs);log.mkdir(exist_ok=True,parents=True)
    (log/'compatibilidade_occt.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/IfcGeomRepresentation.h',tofile='adaptado/IfcGeomRepresentation.h')))
    (log/'compatibilidade_occt.json').write_text(json.dumps({'arquivo':str(path),'sha256_original':hashlib.sha256(old.encode()).hexdigest(),'sha256_adaptado':hashlib.sha256(new.encode()).hexdigest(),'fonte':'https://dev.opencascade.org/doc/refman/html/class_poly___triangulation.html','alteracao':'Acesso a vertices/UV pela API OCCT 7.6; algoritmo IFC2SB preservado.'},indent=2))

def adaptar_occt_functions(ifcos,logs):
    path=Path(ifcos)/'src/ifcgeom/IfcGeomFunctions.cpp'
    old=path.read_text()
    if 'CIV2155: acesso Node' in old:return
    new=old
    for a,b in {
      'const TColgp_Array1OfPnt& nodes = tri->Nodes();':'// CIV2155: acesso Node para OCCT 7.6.',
      'const gp_Pnt& uv = nodes.Value(n123[(j + k) % 3]);':'const gp_Pnt uv = tri->Node(n123[(j + k) % 3]);'}.items():
        assert a in new,a
        new=new.replace(a,b)
    path.write_text(new)
    (Path(logs)/'compatibilidade_occt_functions.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/IfcGeomFunctions.cpp',tofile='adaptado/IfcGeomFunctions.cpp')))

def adaptar_occt_cpp(ifcos,logs):
    for name in ['IfcGeomRepresentation.cpp','IfcGeomSerialisation.cpp']:
        path=Path(ifcos)/'src/ifcgeom'/name
        old=path.read_text()
        if 'CIV2155: acesso Node' in old:continue
        new=old
        for a,b in {
          'const TColgp_Array1OfPnt& nodes = tri->Nodes();':'// CIV2155: acesso Node para OCCT 7.6.',
          'nodes.Length()':'tri->NbNodes()',
          'nodes(i).Transformed(loc)':'tri->Node(i).Transformed(loc)'}.items():
            assert a in new,a
            new=new.replace(a,b)
        path.write_text(new)
        (Path(logs)/('compatibilidade_'+name+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/'+name,tofile='adaptado/'+name)))

def adaptar_occt_curve(ifcos,logs):
    """API oficial V7_6_0: BRepAdaptor_CompCurve já deriva de Adaptor3d_Curve.
    https://github.com/Open-Cascade-SAS/OCCT/blob/V7_6_0/src/BRepAdaptor/BRepAdaptor_CompCurve.hxx
    https://github.com/Open-Cascade-SAS/OCCT/blob/V7_6_0/src/Approx/Approx_Curve3d.hxx
    """
    path=Path(ifcos)/'src/ifcgeom/IfcGeomWires.cpp';old=path.read_text()
    if 'CIV2155: OCCT Curve' in old:return
    new=old
    for a,b in {
      '#include <BRepAdaptor_HCompCurve.hxx>':'// CIV2155: OCCT Curve sem adaptador H removido.',
      'BRepAdaptor_CompCurve cc(w, true);':'// Adaptor3d_Curve agora suporta Handle diretamente.',
      'Handle(Adaptor3d_HCurve) hcc = Handle(Adaptor3d_HCurve)(new BRepAdaptor_HCompCurve(cc));':'Handle(Adaptor3d_Curve) hcc = new BRepAdaptor_CompCurve(w, true);'}.items():
        assert a in new,a
        new=new.replace(a,b)
    path.write_text(new)
    (Path(logs)/'compatibilidade_occt_curve.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/IfcGeomWires.cpp',tofile='adaptado/IfcGeomWires.cpp')))

def adaptar_includes_motor(motor,logs):
    """Declara explicitamente o cabeçalho padrão usado por std::array.
    Fonte técnica: https://eel.is/c++draft/array.syn
    Não modifica operações de interseção nem os critérios do algoritmo.
    """
    path=Path(motor)/'src/intersector/intersector_includes.h';old=path.read_text()
    if '#include <array>' in old:return
    assert '#include <cmath>' in old
    new=old.replace('#include <cmath>','// CIV2155: include explicito exigido pelo compilador atual.\n#include <array>\n#include <cmath>',1)
    path.write_text(new)
    (Path(logs)/'compatibilidade_motor_array.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/intersector_includes.h',tofile='adaptado/intersector_includes.h')))

def adaptar_includes_octree(motor,logs):
    """Mesmo cabeçalho padrão no módulo octree; preserva a codificação original."""
    for name in ['octree.cpp','octree_interface.cpp']:
        path=Path(motor)/'src/octree'/name;old=path.read_bytes()
        if b'#include <array>' in old:continue
        marker=old.index(b'#include')
        new=old[:marker]+b'// CIV2155: cabecalho padrao explicito.\n#include <array>\n'+old[marker:]
        path.write_bytes(new)
        (Path(logs)/('compatibilidade_motor_'+name+'_array.diff')).write_text(''.join(difflib.unified_diff(old.decode('latin1').splitlines(True),new.decode('latin1').splitlines(True),fromfile='original/'+name,tofile='adaptado/'+name)),encoding='utf8')

def adaptar_occt_writer(motor,logs):
    """API Poly_Triangulation: atribuição ao nó pelo método SetNode."""
    path=Path(motor)/'src/stl_export/SB_StlAPI_Writer.cpp';old=path.read_text()
    if 'aMesh->SetNode(aNodeIter + aNodeOffset, aPnt);' in old:return
    token='aMesh->ChangeNode(aNodeIter + aNodeOffset) = aPnt;';assert token in old
    new=old.replace(token,'aMesh->SetNode(aNodeIter + aNodeOffset, aPnt);')
    path.write_text(new)
    (Path(logs)/'compatibilidade_motor_stl_writer.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/SB_StlAPI_Writer.cpp',tofile='adaptado/SB_StlAPI_Writer.cpp')))
