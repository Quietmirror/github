"""Partition a problematic trimmed roof face in CAD; retain every solid.

The subsequent Boolean union keeps the split exterior faces (no clean()).
This changes BRep segmentation, not the intended outline. Fresh STL must pass
all checks before replacing a candidate; failures remain diagnostic files.
"""
from pathlib import Path
import sys,json,ctypes
import cadquery as cq,trimesh,pymeshlab,numpy as np
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));from audit_baseline import volume

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    work=ROOT.parent/f'_support/work/l2/{variant}/partition';work.mkdir(parents=True,exist_ok=True)
    s=cq.importers.importStep(str(out/'assembly/BODY.step')).val();v0=volume(s)[0]
    plane=cq.Face.makePlane(120,120,(0,67.5,20),(0,1,0));split=s.split(plane);parts=split.Solids()
    print('SPLIT',len(parts),[volume(q)[0] for q in parts],flush=True)
    assert len(parts)>=2 and split.isValid()
    r=parts[0].fuse(*parts[1:]);v1=volume(r)[0]
    assert r.isValid() and len(r.Solids())==1 and abs(v1-v0)<.15,(r.isValid(),len(r.Solids()),v0,v1)
    cq.exporters.export(r,str(work/'BODY.step'));rr=cq.importers.importStep(str(work/'BODY.step')).val()
    assert rr.isValid() and len(rr.Solids())==1
    trials=[]
    for chord in [.025,.01]:
        raw=work/f'BODY_{chord}.stl';rr.exportStl(str(raw),tolerance=chord,angularTolerance=.12,relative=False,parallel=False)
        m=trimesh.load_mesh(raw);m.merge_vertices(digits_vertex=6);m.update_faces(m.nondegenerate_faces(height=1e-7));m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
        temp=work/'clean.stl';m.export(temp);ms=pymeshlab.MeshSet();ms.load_new_mesh(str(temp));ms.compute_selection_by_self_intersections_per_face()
        count=ms.current_mesh().selected_face_number();ok=m.is_watertight and m.is_winding_consistent and count==0
        trials.append(dict(chord_mm=chord,watertight=m.is_watertight,self_intersections=count,pass_check=ok));print(trials[-1],flush=True)
        if ok:
            # Only after passing, replace both assembly and print exports.
            cq.exporters.export(rr,str(out/'assembly/BODY.step'));m.export(out/'assembly/BODY.stl')
            metrics=json.loads((rp/'cad_metrics.json').read_text());shift=metrics['BODY']['print_translation']
            q=m.copy();q.apply_translation(shift);q.export(out/'print/BODY.stl');cq.exporters.export(rr.translate(shift),str(out/'print/BODY.step'))
            metrics['BODY']['mesh_cleanup'].update(absolute_chord_mm=chord,final_faces=len(m.faces),holes_patched=0,components_discarded=0)
            (rp/'cad_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8');break
    result=dict(method='CAD split at Y67.5 then fuse ALL pieces without unifying exterior faces',pieces_retained=len(parts),
        original_mm3=v0,partitioned_mm3=v1,difference_mm3=v1-v0,trials=trials,pass_check=trials[-1]['pass_check'],mesh_holes_patched=0)
    (rp/'cad_partition.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    assert result['pass_check']

if __name__=='__main__':main()
