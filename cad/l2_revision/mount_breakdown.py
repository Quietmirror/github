"""Net sub-allocation of fixed mounts; helps target material actually present."""
import sys,json,ctypes
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import mechanics_l2
from surfaces import make_surfaces
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text());outer,inner,_=make_surfaces(p)
    mech=mechanics_l2.build_mechanics(p,outer,inner)
    remaining=cq.importers.importStep(str(ROOT/'exports/l2_revision/partitions/R32/C_BODY_MOUNTS.step')).val()
    start=volume(remaining)[0];rows=[]
    for i,(name,s) in enumerate(zip(mech['addition_labels'],mech['body_additions'])):
        local=remaining.intersect(s.mirror('YZ'));v=volume(local)[0]
        if v>.001:
            rows.append(dict(index=i,label=name,net_mm3=v,PA12_g=v*.00101))
            remaining=remaining.cut(local)
            print(name,round(v,3),flush=True)
    residual=volume(remaining)[0];rows.append(dict(label='RESIDUAL_INTERFACE_AND_NEW_FOOT_LANDS',net_mm3=residual,PA12_g=residual*.00101))
    result=dict(rows=rows,total_mm3=start,closure_mm3=sum(q['net_mm3'] for q in rows)-start,
        scope='Disjoint net allocation of C_BODY_MOUNTS to source supports, in source order. Shared intersections assigned to first support; residual contains later interface and short-foot revisions.')
    (ROOT/'reports/l2_revision/mount_breakdown.json').write_text(json.dumps(result,indent=2)+'\n')
    print('mount ledger closure',result['closure_mm3'],flush=True)
if __name__=='__main__':main()
