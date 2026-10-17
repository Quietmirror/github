"""Validate actual exports; never infer success from CAD construction alone."""
from pathlib import Path
import sys,json,ctypes,importlib.util
import trimesh,pymeshlab,numpy as np
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(1,str(ROOT/'cad/rebuild_r2'))
from audit_baseline import volume
from mesh_motion import from_mesh,intersection

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    metrics=json.loads((rp/'cad_metrics.json').read_text());rows=[];checks=[]
    for n,m in metrics.items():
        if not m['printable']:continue
        path=out/f'assembly/{n}.stl';mesh=trimesh.load_mesh(path)
        s=cq.importers.importStep(str(path.with_suffix('.step'))).val();v,e=volume(s)
        ms=pymeshlab.MeshSet();ms.load_new_mesh(str(path));ms.compute_selection_by_self_intersections_per_face()
        intersections=ms.current_mesh().selected_face_number()
        row=dict(part=n,valid=s.isValid(),solids=len(s.Solids()),watertight=mesh.is_watertight,
                 winding_consistent=mesh.is_winding_consistent,mesh_components=len(mesh.split(only_watertight=False)),
                 self_intersection_faces=intersections,adaptive_CAD_mm3=v,mesh_mm3=mesh.volume,PA12_g=v*.00101,PLA_solid_g=v*.00124)
        row['pass']=row['valid'] and row['solids']==1 and row['watertight'] and row['winding_consistent'] and row['mesh_components']==1 and intersections==0
        rows.append(row);print('MESH',n,row['pass'],round(v,3),flush=True)
    result=dict(parts=rows,total_PA12_g=sum(r['PA12_g'] for r in rows),pass_check=all(r['pass'] for r in rows))
    (rp/'mesh_and_volume.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    spec=importlib.util.spec_from_file_location('r32_validation',ROOT/'cad/rebuild_r3_2/validate.py')
    val=importlib.util.module_from_spec(spec);spec.loader.exec_module(val)
    val.OUT=out;val.RP=rp;val.HERE=ROOT/'cad/rebuild_r3_2';val.WORK=ROOT.parent/f'_support/work/l2/{variant}/validation';val.WORK.mkdir(parents=True,exist_ok=True)
    sys.argv=[sys.argv[0],'--mechanical-only'];val.main()
    body=from_mesh(trimesh.load_mesh(out/'assembly/BODY.stl'))
    for n in ['SIDE_FRONT_KEY','SIDE_REAR_KEY']:
        mesh=from_mesh(trimesh.load_mesh(out/f'assembly/{n}.stl'));bad=[]
        for dx in np.linspace(20,0,101):
            v=intersection(mesh.translate([dx,0,0]),body)
            if v>.01:bad.append(dict(offset_X_mm=float(dx),volume_mm3=v))
        checks.append(dict(part=n,poses=101,path='Straight inward X20 -> X0 before capture pin and switch assembly',conflicts=bad,pass_check=not bad))
    (rp/'side_direct_insertion.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
    print('MASS',result['total_PA12_g'],'mesh',result['pass_check'],'direct side entry',[c['pass_check'] for c in checks],flush=True)

if __name__=='__main__':main()
