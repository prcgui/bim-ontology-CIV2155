// Ensaio parcial CIV2155, 2026. LGPL-3.0-or-later.
// Krijnen et al. 2020, DOI 10.46421/2706-6568.37.2020.paper008, sec. 3.3.
// Fonte científica executável: Zenodo 3633653, v0.7.0-validation.
// Nef EPECK, Minkowski com cubo [-eps,+eps]^3 e interseção preservam
// as operações de validation_utils.h e validate_space_boundaries.cpp.
// Este adaptador usa OFF, não a interpretação IFC/CGAL original;
// não executa fix_spaceboundaries, remove_thickness ou geração de relações IFC.
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/minkowski_sum_3.h>
#include <CGAL/Polygon_mesh_processing/triangulate_faces.h>
#include <CGAL/Polygon_mesh_processing/self_intersections.h>
#include <CGAL/Polygon_mesh_processing/orientation.h>
#include <CGAL/Polygon_mesh_processing/measure.h>
#include <CGAL/boost/graph/generators.h>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <stdexcept>
using K=CGAL::Exact_predicates_exact_constructions_kernel;
using P=CGAL::Polyhedron_3<K>;
using N=CGAL::Nef_polyhedron_3<K>;
using Pt=K::Point_3;
namespace PMP=CGAL::Polygon_mesh_processing;

// Corpo de create_nef_polyhedron(Polyhedron&) da fonte de 2020, extraído
// automaticamente por gerar_fonte.py, com Logger mínimo no adaptador.
struct Logger{static const int LOG_ERROR=1;static void Message(int,const char* s){std::cerr<<s<<"\n";}};
#include "nef_extraido.h"

P box(double x,double y,double z,double dx,double dy,double dz){
    P p;
    CGAL::make_hexahedron(Pt(x,y,z),Pt(x+dx,y,z),Pt(x+dx,y+dy,z),Pt(x,y+dy,z),
      Pt(x,y+dy,z+dz),Pt(x,y,z+dz),Pt(x+dx,y,z+dz),Pt(x+dx,y+dy,z+dz),p);
    if(!PMP::is_outward_oriented(p)) PMP::reverse_face_orientations(p);
    return p;
}
N load(const char* path){
    P p; std::ifstream in(path);
    if(!(in>>p)||!p.is_valid()||!p.is_closed())throw std::runtime_error("OFF não forma poliedro fechado válido");
    PMP::triangulate_faces(p);
    if(PMP::does_self_intersect(p))throw std::runtime_error("Malha com autointerseção; sem reparação automática");
    if(!PMP::does_bound_a_volume(p))throw std::runtime_error("Orientação/componentes não delimitam volume; sem reparação automática");
    auto n=create_nef_polyhedron(p);
    if(n.is_empty())throw std::runtime_error("Conversão Nef vazia");
    return n;
}
void emit(const N& x,const std::string& prefix){
    auto reg=x.regularization();
    bool has_volume=!reg.is_empty();
    std::cout<<"{\"nao_vazio\":"<<(!x.is_empty()?"true":"false")<<",\"volume_3d_presente\":"<<(has_volume?"true":"false")
      <<",\"simples\":"<<(x.is_simple()?"true":"false")<<",\"volume_m3\":";
    if(has_volume && reg.is_simple()){
        P q;reg.convert_to_polyhedron(q);PMP::triangulate_faces(q);
        double vol=CGAL::to_double(PMP::volume(q));
        std::cout<<std::setprecision(17)<<vol;
        if(!prefix.empty()){std::ofstream out(prefix+".off");out<<std::setprecision(17)<<q;}
    }else std::cout<<"null";
    std::cout<<"}";
}
int main(int argc,char** argv){
 try{
    if(argc<2)throw std::runtime_error("modo: controle | par A.off B.off eps prefixo");
    if(std::string(argv[1])=="controle"){
        P pa=box(0,0,0,1,1,1);N a=create_nef_polyhedron(pa);
        for(auto test: {std::pair<const char*,double>{"contato",1.0},{"fresta_10um",1.00001},{"fresta_1mm",1.001},{"sobreposicao",.9},{"aresta",-1.0},{"contido",-2.0}}){
            P pb=test.second==-1.0?box(1,1,0,1,1,1):test.second==-2.0?box(.1,.1,.1,.2,.2,.2):box(test.second,0,0,1,1,1);
            N b=create_nef_polyhedron(pb);
            for(double eps:{0.,1.e-5}){
                auto A=a,B=b;
                if(eps>0){P c=box(-eps,-eps,-eps,2*eps,2*eps,2*eps);N cube=create_nef_polyhedron(c);
                    A=CGAL::minkowski_sum_3(A,cube);B=CGAL::minkowski_sum_3(B,cube);}
                auto x=A*B;
                std::cout<<"{\"caso\":\""<<test.first<<"\",\"eps_m\":"<<eps<<",\"resultado\":";emit(x,"");std::cout<<"}\n";
            }
        }
    }else{
        if(argc!=6)throw std::runtime_error("par A.off B.off eps prefixo");
        N a=load(argv[2]),b=load(argv[3]);double eps=std::stod(argv[4]);
        if(eps>0){P p=box(-eps,-eps,-eps,2*eps,2*eps,2*eps);N cube=create_nef_polyhedron(p);
            a=CGAL::minkowski_sum_3(a,cube);b=CGAL::minkowski_sum_3(b,cube);}
        // Interseção não regularizada, como o trecho dos autores. A regularização
        // em emit serve somente para medir volume, não decide nao_vazio.
        auto x=a*b;emit(x,argv[5]);std::cout<<"\n";
    }
    return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 2;}
}
