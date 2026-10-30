using Kernel_=K;
CGAL::Nef_polyhedron_3<Kernel_> create_nef_polyhedron(CGAL::Polyhedron_3<Kernel_> &polyhedron) {
	if (polyhedron.is_valid() && polyhedron.is_closed()) {
		// @todo is it necessary to triangulat?
		CGAL::Polygon_mesh_processing::triangulate_faces(polyhedron);
		CGAL::Nef_polyhedron_3<Kernel_> nef_polyhedron;
		try {
			nef_polyhedron = CGAL::Nef_polyhedron_3<Kernel_>(polyhedron);
		} catch (...) {
			Logger::Message(Logger::LOG_ERROR, "Conversion to Nef polyhedron failed!");
		}
		return nef_polyhedron;
	} else {
		Logger::Message(Logger::LOG_ERROR, "Polyhedron not valid: cannot create Nef polyhedron!");
		return CGAL::Nef_polyhedron_3<Kernel_>();
	}
}
