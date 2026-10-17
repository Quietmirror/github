"""Disjoint functional attribution on native source BReps.

Priority: original outer skin A; then actual load-carrying members B inside
remaining BODY; residual fixed installation material C. No gross bar sums.
"""
from pathlib import Path
import sys,json,ctypes,cadquery as cq,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(1,str(ROOT/'cad/rebuild_r2'))
import mechanics_l2
from surfaces import make_surfaces
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1] if len(sys.argv)>1 else 'R32'
    base=ROOT/'exports/rebuild_r3_2' if variant=='R32' else ROOT/f'exports/l2_revision/{variant}'
    rp=ROOT/f'reports/l2_revision/partition_{variant}';rp.mkdir(parents=True,exist_ok=True)
    out=ROOT/f'exports/l2_revision/partitions/{variant}';out.mkdir(parents=True,exist_ok=True)
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text())
    if variant!='R32':p=json.loads((ROOT/f'reports/l2_revision/{variant}/source_parameters.json').read_text())
    outer,inner,_=make_surfaces(p);mech=mechanics_l2.build_mechanics(p,outer,inner)
    body=cq.importers.importStep(str(base/'assembly/BODY.step')).val();total=volume(body)[0]
    skin=outer.cut(inner).mirror('YZ');a=body.intersect(skin)
    repairs=[]
    if not a.isValid():
        # Repair only the derived attribution solid, never the delivered BODY.
        # Native ShapeFix heals Boolean tolerances; check volume before/after
        # and the independent whole-body closure below.
        before=volume(a)[0];fixed=a.fix();after=volume(fixed)[0]
        def mesh_of(s):
            points,faces=s.tessellate(.035,.12)
            return trimesh.Trimesh(np.array([v.toTuple() for v in points]),np.array(faces),process=True)
        m0,m1=mesh_of(a),mesh_of(fixed);distances=[]
        for source,target in [(m0,m1),(m1,m0)]:
            points,_=trimesh.sample.sample_surface(source,1000,seed=731)
            distances.append(float(trimesh.proximity.closest_point(target,points)[1].max()))
        repairs.append(dict(category='A_BODY_SKIN',method='Native BRep ShapeFix on derived intersection only',before_mm3=before,after_mm3=after,valid=fixed.isValid(),
            bidirectional_surface_sample_max_mm=distances,scope='Invalid input integration is not an exact reference. The delivered BODY is untouched; healed attribution is accepted only with <0.035mm sampled boundary movement, <0.2% volume change, and strict final volume closure.'))
        assert fixed.isValid() and max(distances)<.035 and abs(after-before)<.002*abs(before),(before,after,distances)
        a=fixed
    remaining=body.cut(a);bparts=[]
    structural=('FOOT_','RAISED_CROSS_TIE','RAISED_DIAGONAL_TIE','LOCAL_MIDDLE_TRAY_HUB')
    for name,s in zip(mech['addition_labels'],mech['body_additions']):
        if any(name.startswith(prefix) for prefix in structural):
            local=remaining.intersect(s.mirror('YZ'));v=volume(local)[0]
            if v>1e-7:
                bparts.append(local);remaining=remaining.cut(local)
                print('Partition',name,v,flush=True)
    b=cq.Compound.makeCompound(bparts);c=remaining
    shapes={'A_BODY_SKIN':a,'B_BODY_SKELETON':b,'C_BODY_MOUNTS':c};rows=[]
    for name,s in shapes.items():
        v,e=volume(s);assert s.isValid(),name
        cq.exporters.export(s,str(out/f'{name}.step'))
        rows.append(dict(category=name,mm3=v,PA12_g=v*.00101,PLA_solid_g=v*.00124,adaptive_integration_error=e))
    closure=sum(r['mm3'] for r in rows)-total
    assert abs(closure)<.25,(closure,total)
    separate=['SIDE_FRONT_KEY_SWITCH_CLAMP','SIDE_REAR_KEY_SWITCH_CLAMP','WHEEL_CARRIER']
    moving=['LEFT_KEY','RIGHT_KEY','SIDE_FRONT_KEY','SIDE_REAR_KEY','WHEEL']
    for label,names in [('C_SEPARATE_MOUNTS',separate),('D_MOVING_OTHER',moving)]:
        v=sum(volume(cq.importers.importStep(str(base/f'assembly/{n}.step')).val())[0] for n in names)
        rows.append(dict(category=label,mm3=v,PA12_g=v*.00101,PLA_solid_g=v*.00124))
    result=dict(variant=variant,priority='A skin intersection first, B source structural members from remaining material, C residual fixed mounts. Intersections belong to earlier category.',
        parts=rows,BODY_mm3=total,BODY_closure_error_mm3=closure,tolerance_mm3=.25,
        whole_mm3=sum(r['mm3'] for r in rows),whole_PA12_g=sum(r['PA12_g'] for r in rows),derived_attribution_repairs=repairs)
    (rp/'volume_ledger.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
