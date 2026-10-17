"""Re-tessellate valid STEP when coarse OCC triangulation is invalid.

No triangle hole filling, disconnected-component removal, Boolean mesh
repair, or shrink-wrap is allowed. Both placed and printing STL are replaced
only after a fresh CAD tessellation passes closed/self-intersection checks.
"""
from pathlib import Path
import sys,json,ctypes
import cadquery as cq,trimesh,pymeshlab,numpy as np
from OCP.BRepTools import BRepTools
ROOT=Path(__file__).resolve().parents[2]

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];name=sys.argv[2] if len(sys.argv)>2 else 'BODY'
    out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    work=ROOT.parent/f'_support/work/l2/{variant}/tessellation';work.mkdir(parents=True,exist_ok=True)
    metrics=json.loads((rp/'cad_metrics.json').read_text());trials=[]
    for chord in [.015,.01,.005]:
        s=cq.importers.importStep(str(out/f'assembly/{name}.step')).val()
        assert s.isValid() and len(s.Solids())==1
        BRepTools.Clean_s(s.wrapped)
        raw=work/f'{name}_{chord}.stl';s.exportStl(str(raw),tolerance=chord,angularTolerance=.08,relative=False,parallel=False)
        m=trimesh.load_mesh(raw);m.merge_vertices(digits_vertex=6)
        m.update_faces(m.nondegenerate_faces(height=1e-7));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
        temp=work/'candidate.stl';m.export(temp);ms=pymeshlab.MeshSet();ms.load_new_mesh(str(temp));ms.compute_selection_by_self_intersections_per_face()
        count=ms.current_mesh().selected_face_number();ok=m.is_watertight and m.is_winding_consistent and count==0
        trials.append(dict(chord_mm=chord,faces=len(m.faces),watertight=m.is_watertight,self_intersections=count,pass_check=ok));print(trials[-1],flush=True)
        if ok:
            m.export(out/f'assembly/{name}.stl');q=m.copy()
            angle=metrics[name].get('print_rotation_y_deg',0)
            if angle:q.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(angle),[0,1,0]))
            q.apply_translation(metrics[name]['print_translation']);q.export(out/f'print/{name}.stl')
            metrics[name]['mesh_cleanup'].update(absolute_chord_mm=chord,angular_tolerance_rad=.08,final_faces=len(m.faces),holes_patched=0,components_discarded=0)
            (rp/'cad_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8');break
    (rp/f'{name}_tessellation_trials.json').write_text(json.dumps(trials,indent=2)+'\n',encoding='utf8')
    assert trials[-1]['pass_check'],'Valid BRep still cannot produce a valid mesh; fix CAD before release.'

if __name__=='__main__':main()
