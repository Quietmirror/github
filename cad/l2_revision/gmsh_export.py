"""Independent CAD surface meshing; never fill STL holes or discard pieces.

Accept an alternate tessellation only after closedness, self-intersection,
volume and surface-distance checks. Failed candidates remain in work/.
"""
from pathlib import Path
import sys,json,subprocess,ctypes,hashlib
import numpy as np,trimesh,pymeshlab,cadquery as cq
from audit_baseline import volume
ROOT=Path(__file__).resolve().parents[2];SUP=ROOT.parent/'_support'
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];name=sys.argv[2] if len(sys.argv)>2 else 'BODY'
    out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    step=out/f'assembly/{name}.step';source=hashlib.sha256(step.read_bytes()).hexdigest()
    work=SUP/f'work/l2/{variant}/surface_mesh_h070_{source[:10]}';work.mkdir(parents=True,exist_ok=True)
    s=cq.importers.importStep(str(step)).val();cv=volume(s)[0]
    geo=work/f'{name}.geo';stl=work/f'{name}.stl'
    geo.write_text(f'''SetFactory("OpenCASCADE");
General.NumThreads=2;
Merge "{step.as_posix()}";
Mesh.MeshSizeMin=0.15;
Mesh.MeshSizeMax=0.70;
Mesh.MeshSizeFromCurvature=32;
Mesh.MeshSizeFromPoints=0;
Mesh.Algorithm=6;
Mesh.MinimumCirclePoints=24;
Mesh 2;
Save "{stl.as_posix()}";
''')
    exe=SUP/'tools/Gmsh/gmsh-4.15.2-Windows64/gmsh.exe'
    if not stl.exists():
        with (work/'gmsh.log').open('w') as log:
            run=subprocess.run([str(exe),str(geo),'-0','-nopopup'],stdout=log,stderr=subprocess.STDOUT)
        if run.returncode:raise RuntimeError(f'Gmsh failed: {run.returncode}; {work}')
    m=trimesh.load_mesh(stl);m.merge_vertices(digits_vertex=6)
    m.update_faces(m.nondegenerate_faces(height=1e-8));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
    m.export(stl)
    ms=pymeshlab.MeshSet();ms.load_new_mesh(str(stl));ms.compute_selection_by_self_intersections_per_face()
    ints=ms.current_mesh().selected_face_number()
    # Deterministic stratified face-centroid samples, exact BRep distance.
    print('Gmsh mesh: closed',m.is_watertight,'intersections',ints,flush=True)
    centroids=m.triangles_center;idx=np.linspace(0,len(centroids)-1,min(500,len(centroids))).astype(int)
    boundary=cq.Compound.makeCompound(s.Shells())
    distances=np.array([boundary.distance(cq.Vertex.makeVertex(*p)) for p in centroids[idx]])
    result=dict(variant=variant,part=name,source_STEP_sha256=source,method='Gmsh independent CAD surface triangulation',faces=len(m.faces),
        watertight=m.is_watertight,winding_consistent=m.is_winding_consistent,
        connected_components=len(trimesh.graph.connected_components(m.face_adjacency,nodes=np.arange(len(m.faces)))),
        self_intersection_faces=ints,volume_relative_error=abs(m.volume/cv-1),
        sampled_CAD_distance_mm=dict(samples=len(distances),maximum=float(distances.max()),P99=float(np.quantile(distances,.99))),
        holes_filled=0,components_discarded=0)
    result['pass_check']=bool(m.is_watertight and m.is_winding_consistent and result['connected_components']==1 and ints==0 and result['volume_relative_error']<.002 and distances.max()<.035)
    if result['pass_check']:
        old=out/f'assembly/{name}.stl';old.replace(work/f'{name}_original_occ.stl')
        m.export(old);metrics=json.loads((rp/'cad_metrics.json').read_text());info=metrics[name]
        pm=m.copy()
        if info.get('print_rotation_y_deg'):pm.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(info['print_rotation_y_deg']),[0,1,0]))
        pm.apply_translation(info['print_translation']);pm.export(out/f'print/{name}.stl')
        info['alternate_mesh']=result;(rp/'cad_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    (rp/f'{name}_gmsh_export.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
