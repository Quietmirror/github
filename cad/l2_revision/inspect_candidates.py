"""Bounded geometry screening for completed single-variable candidates."""
import sys,json,ctypes
from pathlib import Path
import cadquery as cq,trimesh,pymeshlab
from audit_baseline import volume
ROOT=Path(__file__).resolve().parents[2]
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    result=[]
    for variant in sys.argv[1:]:
        base=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
        if not (rp/'design_metadata.json').exists():continue
        s=cq.importers.importStep(str(base/'assembly/BODY.step')).val();v=volume(s)[0]
        mesh=trimesh.load_mesh(base/'assembly/BODY.stl');ms=pymeshlab.MeshSet();ms.load_new_mesh(str(base/'assembly/BODY.stl'));ms.compute_selection_by_self_intersections_per_face()
        row=dict(variant=variant,BODY_CAD_mm3=v,BODY_PA12_g=v*.00101,BODY_mesh_mm3=mesh.volume,
            CAD_valid=s.isValid(),solids=len(s.Solids()),watertight=mesh.is_watertight,
            self_intersecting_faces=ms.current_mesh().selected_face_number(),mesh_components=len(mesh.split(only_watertight=False)),
            original_other_eight_parts_mm3=5704.9480357253,total_PA12_g=(v+5704.9480357253)*.00101,
            full_assembly_validation=False)
        row['geometry_screen_pass']=row['CAD_valid'] and row['solids']==1 and row['watertight'] and row['self_intersecting_faces']==0 and row['mesh_components']==1
        (rp/'geometry_screen.json').write_text(json.dumps(row,indent=2)+'\n');result.append(row)
        print(variant,'mass',row['total_PA12_g'],'geometry',row['geometry_screen_pass'],flush=True)
    (ROOT/'reports/l2_revision/topology_skeleton_mass_screen.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
