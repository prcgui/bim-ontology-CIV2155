// Copyright 2022 Eric Fichter; GPL-3.0-or-later. Corpos extraídos do IFC2SB.
// Adaptador de teste CIV2155, 2026. Não representa o programa completo.
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cmath>
#include <climits>
#include <list>
#include <vector>
#include <algorithm>
#include <set>
#include <unordered_map>
#include <string>
#include <TopoDS.hxx>
#include <TopoDS_Compound.hxx>
#include <TopoDS_Face.hxx>
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <BRepLProp_SLProps.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BOPAlgo_CellsBuilder.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <TopExp_Explorer.hxx>
#include <gp_Pln.hxx>
namespace IfcUtil {struct IfcBaseClass {};}
using face_normal_status=int;
struct Product {std::string guid="W";};
struct oFace {TopoDS_Face face;int shell=0; oFace(TopoDS_Face f):face(f){};
unsigned short ShellID() const{return shell;} void SetShellID(int x){shell=x;}
unsigned ParentID() const{return 0;} IfcUtil::IfcBaseClass* Opening() const{return nullptr;}
int NormalStatus() const{return 0;} gp_Dir Normal() const;};
class Kernel {public:
struct opening_info {TopoDS_Face face;Product* product;unsigned short shell_id;unsigned parent_id;IfcUtil::IfcBaseClass* opening_product;int normal_status;
opening_info(TopoDS_Face f,Product* p,unsigned short s,unsigned a,IfcUtil::IfcBaseClass* o,int n):face(f),product(p),shell_id(s),parent_id(a),opening_product(o),normal_status(n) {}};
using OWP=std::unordered_map<IfcUtil::IfcBaseClass*,std::pair<TopoDS_Shape,IfcUtil::IfcBaseClass*>>;
static unsigned hash(const TopoDS_Shape& s){return s.HashCode(INT_MAX);}
static std::string round_double_three_digits(double x){return std::to_string(x);}
static std::string round_double_to_n_decimal_places(double x,int n){return std::to_string(x);}
static gp_Dir face_normal(const TopoDS_Face &face);
static gp_Pnt face_center(const TopoDS_Face &face);
static double area(const TopoDS_Shape &shape);
static TopoDS_Compound cvfcipw_compound_from_orig_faces(size_t n, const std::list<oFace *> &orig_faces);
static void cvfcipw_perform_fuse(const std::string &guid, BOPAlgo_CellsBuilder &CellBuilder, const TopoDS_Compound &Shell, const OWP &OSW);
static std::set<unsigned int>
cvfcipw_cut_openings_from_wall_faces(Product &product, BOPAlgo_CellsBuilder &CellBuilder, TopTools_ListOfShape &take, TopTools_ListOfShape &avoi, const TopoDS_Compound &Shell, const OWP &OSW,
                                             std::list<opening_info> &ins, const std::pair<const unsigned int, std::list<oFace *>> &m);
static void cvfcipw_commons_between_opening_and_wall_faces(Product &product, BOPAlgo_CellsBuilder &CellBuilder, TopTools_ListOfShape &take, TopTools_ListOfShape &avoi, const TopoDS_Compound &Shell, const std::set<unsigned int> &ids,
                                                            const OWP &OSW, std::list<opening_info> &ins, const std::pair<const unsigned int, std::list<oFace *>> &m);
};
gp_Dir oFace::Normal() const{return Kernel::face_normal(face);}
class cFace {public: TopoDS_Face face;cFace* parent=nullptr;int product=1;
cFace(TopoDS_Face f):face(f){};int RelProduct()const{return product;}
gp_Dir FixedFaceNormal()const{return Kernel::face_normal(face);}
double SurfaceArea()const{return Kernel::area(face);} std::string Info()const{return "controle";}
bool CheckParent(double tol_dist,double tol_angle);};
gp_Dir Kernel::face_normal(const TopoDS_Face &face) {

    Standard_Real UMin, UMax, VMin, VMax;
    BRepTools::UVBounds(face, UMin, UMax, VMin, VMax);
    BRepAdaptor_Surface surface = BRepAdaptor_Surface(face); // create surface to access the geometry of face
    gp_Dir normal = BRepLProp_SLProps(surface, UMin, VMin, 1, 1.e-3).Normal();

    if (face.Orientation() == TopAbs_FORWARD)
        return normal;
    else if (face.Orientation() == TopAbs_REVERSED)
        return normal.Reversed();
    else {
        std::cerr << "[Error] Wrong Orientation in normal calculation: " << normal.X() << "\t" << normal.Y() << "\t" << normal.Z() << "\t" << face.Orientation() << "\t" << hash(face) << std::endl;
        return normal;
    }
}

gp_Pnt Kernel::face_center(const TopoDS_Face &face) {
    GProp_GProps p;
    BRepGProp::SurfaceProperties(face, p);
    return p.CentreOfMass();
}

double Kernel::area(const TopoDS_Shape &shape) {
    GProp_GProps gprop;
    BRepGProp::SurfaceProperties(shape, gprop);
    return gprop.Mass();
}

TopoDS_Compound Kernel::cvfcipw_compound_from_orig_faces(size_t n, const std::list<oFace *> &orig_faces) {

    // Create Compound from set of orig faces
    TopoDS_Compound Shell;
    BRep_Builder B;
    B.MakeCompound(Shell);
    for (auto &orig_face: orig_faces) {
        B.Add(Shell, orig_face->face);
        orig_face->SetShellID(orig_face->ShellID() + n); // change of shell_id is necessary. Otherwise the faces in cut that were not altered will be deleted within orig_faces.remove(*orig_face)
    }
    return Shell;
}

void Kernel::cvfcipw_perform_fuse(const std::string &guid, BOPAlgo_CellsBuilder &CellBuilder, const TopoDS_Compound &Shell, const OWP &OSW) {

    // Add Walls and Openings to the Fuse list and Perform Fuse
    TopTools_ListOfShape L;
    L.Append(Shell);
    for (const auto &O: OSW)
        L.Append(O.second.first);
    CellBuilder.SetArguments(L);
    CellBuilder.Perform();

    if (CellBuilder.HasWarnings()) {
        std::cerr << "Warnings for " << guid << ":" << std::endl;
        CellBuilder.DumpWarnings(std::cerr);
    }
    if (CellBuilder.HasErrors()) {
        std::cerr << "Errors for " << guid << ":" << std::endl;
        CellBuilder.DumpErrors(std::cerr);
    }
}

std::set<unsigned int>
Kernel::cvfcipw_cut_openings_from_wall_faces(Product &product, BOPAlgo_CellsBuilder &CellBuilder, TopTools_ListOfShape &take, TopTools_ListOfShape &avoi, const TopoDS_Compound &Shell, const OWP &OSW,
                                             std::list<opening_info> &ins, const std::pair<const unsigned int, std::list<oFace *>> &m) {

    // cut openings from wall faces
    take.Clear();
    avoi.Clear();
    take.Append(Shell);
    for (const auto &O: OSW)
        avoi.Append(O.second.first);
    CellBuilder.AddToResult(take, avoi);

    // add to orig_faces
    std::set<unsigned int> ids;

    // fast way, without tracking parentship:
    // for (auto &face : Topo(CellBuilder.Shape()).faces())
    //    orig_faces.emplace_back(TopoDS::Face(face), &product, m.first);

    // slow way, tracking parentship:
    for (auto &orig_face: m.second) {
        auto NewFaces = CellBuilder.Modified(orig_face->face);

        // add to orig_faces
        if (NewFaces.IsEmpty()) {
            ins.emplace_back(TopoDS::Face(orig_face->face), &product, m.first, orig_face->ParentID(), orig_face->Opening(), orig_face->NormalStatus());
            ids.insert(hash(orig_face->face));
        } else {
            auto itr = TopTools_ListIteratorOfListOfShape(NewFaces);
            while (itr.More()) {
                ins.emplace_back(TopoDS::Face(itr.Value()), &product, m.first, hash(orig_face->face), orig_face->Opening(), orig_face->NormalStatus());
                ids.insert(hash(itr.Value()));
                itr.Next();
            }
        }
    }
    return ids;
}

void Kernel::cvfcipw_commons_between_opening_and_wall_faces(Product &product, BOPAlgo_CellsBuilder &CellBuilder, TopTools_ListOfShape &take, TopTools_ListOfShape &avoi, const TopoDS_Compound &Shell, const std::set<unsigned int> &ids,
                                                            const OWP &OSW, std::list<opening_info> &ins, const std::pair<const unsigned int, std::list<oFace *>> &m) {

    // Commons between openings and wall faces
    for (const auto &O: OSW) {
        take.Clear();
        avoi.Clear();
        CellBuilder.RemoveAllFromResult();
        take.Append(Shell);
        take.Append(O.second.first);
        for (const auto &O2: OSW) {
            if (O.first == O2.first) break;
            avoi.Append(O2.second.first);
        }
        CellBuilder.AddToResult(take, avoi);

        // It is possible to just add all faces of the CellBuilder.Shape() to the orig_faces ...
        //  add_cut_faces_to_orig_face(orig_faces, Topo(CellBuilder.Shape()).faces(), &product, m.first, O.second.second);
        // But I want to check the face normals
        for (auto &orig_face: m.second) {

            auto NewFaces = CellBuilder.Modified(orig_face->face);
            if (NewFaces.IsEmpty()) continue;

            auto itr = TopTools_ListIteratorOfListOfShape(NewFaces);
            while (itr.More()) {

                if (face_normal(TopoDS::Face(itr.Value())).Angle(orig_face->Normal()) > 0.1)
                    itr.Value().Complement();

                // add to orig_faces
                if (ids.find(hash(itr.Value())) == ids.end()) // if ifc in ifc the walls do already have openings before openingelements are subtracted,
                    // result of common operation are side faces of wall in the opening. Those are already taken into account by cut. So skip them, otherwise duplicate faces and ids
                    ins.emplace_back(TopoDS::Face(itr.Value()), &product, m.first, hash(orig_face->face), O.second.second, orig_face->NormalStatus());

                itr.Next();
            }
        }
    }
}
bool cFace::CheckParent(double tol_dist, double tol_angle) {

    if (parent == nullptr) return true;

    if (this == parent) {
        std::cerr << "[Warning] Parent face self reference. " << Info() << std::endl;
        return false;
    }

    gp_Pnt P1 = Kernel::face_center(face);
    gp_Pnt P2 = Kernel::face_center(parent->face);
    gp_Pln pln(P1, FixedFaceNormal());
    double dist = fabs(pln.Distance(P2));
    double a = fabs(FixedFaceNormal().Angle(parent->FixedFaceNormal()));

    if (RelProduct() != parent->RelProduct() || dist > tol_dist || a > tol_angle) {
        std::cerr << "[Warning] Parent face not matching. " << Info() << " - " << parent->Info() << " (" << Kernel::round_double_to_n_decimal_places(dist, 5) << "), (" << Kernel::round_double_three_digits(a * 180 / M_PI) << ")" << std::endl;
        return false;
    }

    double A1 = SurfaceArea();
    double A2 = parent->SurfaceArea();
    double dA = fabs(A1 - A2);

    if (A1 - A2 > 1e-7) {
        std::cerr << "[Warning] Parent face smaller than inner face. " << Info() << " - " << parent->Info() << " (" << Kernel::round_double_to_n_decimal_places(A1, 5) << "), (" << Kernel::round_double_to_n_decimal_places(A2, 5) << ")" << std::endl;
        return false;
    }

    if (dA < 1e-9)
        std::cout << "[Info] Parent face has same size. " << Info() << " - " << parent->Info() << " (" << Kernel::round_double_to_n_decimal_places(A1, 5) << "), (" << Kernel::round_double_to_n_decimal_places(A2, 5) << ")\n";
    else if (dA < 0.001)
        std::cout << "[Info] Parent face has approximately same size. " << Info() << " - " << parent->Info() << " (" << Kernel::round_double_to_n_decimal_places(A1, 5) << "), (" << Kernel::round_double_to_n_decimal_places(A2, 5) << ")\n";

    return true;
}

TopoDS_Face rect(double x,double y,double z,double w,double h){
BRepBuilderAPI_MakePolygon p;p.Add(gp_Pnt(x,y,z));p.Add(gp_Pnt(x+w,y,z));p.Add(gp_Pnt(x+w,y,z+h));p.Add(gp_Pnt(x,y,z+h));p.Close();return BRepBuilderAPI_MakeFace(p.Wire()).Face();}
std::string cut_test(int n){
Product product;TopoDS_Shape wall=BRepPrimAPI_MakeBox(4,.2,3).Shape();
std::list<oFace> storage;std::pair<const unsigned int,std::list<oFace*>> group(0,{});
for(TopExp_Explorer e(wall,TopAbs_FACE);e.More();e.Next()){storage.emplace_back(TopoDS::Face(e.Current()));group.second.push_back(&storage.back());}
IfcUtil::IfcBaseClass keys[2],fills[2];Kernel::OWP openings;
openings[&keys[0]]={BRepPrimAPI_MakeBox(gp_Pnt(1,-.1,.5),1,.4,1.5).Shape(),&fills[0]};
if(n==2)openings[&keys[1]]={BRepPrimAPI_MakeBox(gp_Pnt(3,-.1,.5),.5,.4,1.5).Shape(),&fills[1]};
auto shell=Kernel::cvfcipw_compound_from_orig_faces(1,group.second);BOPAlgo_CellsBuilder b;
Kernel::cvfcipw_perform_fuse(product.guid,b,shell,openings);
TopTools_ListOfShape take,avoid;std::list<Kernel::opening_info> ins;
auto ids=Kernel::cvfcipw_cut_openings_from_wall_faces(product,b,take,avoid,shell,openings,ins,group);
ins.clear();Kernel::cvfcipw_commons_between_opening_and_wall_faces(product,b,take,avoid,shell,ids,openings,ins,group);
std::vector<double> areas;for(auto&i:ins)areas.push_back(Kernel::area(i.face));std::sort(areas.begin(),areas.end());
std::ostringstream out;out<<"[";for(unsigned i=0;i<areas.size();i++){if(i)out<<",";out<<std::setprecision(17)<<areas[i];}out<<"]";return out.str();}
int main(){
std::string a=cut_test(1),b=cut_test(2);std::vector<bool> results;
cFace par(rect(0,0,0,4,3)),ch(rect(1,0,.5,1,1.5));ch.parent=&par;results.push_back(ch.CheckParent(1e-4,.001));
ch.product=2;results.push_back(ch.CheckParent(1e-4,.001));ch.product=1;
cFace displaced(rect(1,.01,.5,1,1.5));displaced.parent=&par;results.push_back(displaced.CheckParent(1e-4,.001));
cFace larger(rect(0,0,0,5,4));larger.parent=&par;results.push_back(larger.CheckParent(1e-4,.001));
cFace reversed(TopoDS::Face(ch.face.Reversed()));reversed.parent=&par;results.push_back(reversed.CheckParent(1e-4,.001));
ch.parent=&ch;results.push_back(ch.CheckParent(1e-4,.001));
cFace outside(rect(6,0,0,1,1));outside.parent=&par;results.push_back(outside.CheckParent(1e-4,.001));
std::cout<<"\nRESULT_JSON={\"cut_1\":"<<a<<",\"cut_2\":"<<b<<",\"parent\":[";
for(unsigned i=0;i<results.size();i++){if(i)std::cout<<",";std::cout<<(results[i]?"true":"false");}std::cout<<"]}\n";}
