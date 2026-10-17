"""Alternate strict ledger avoiding coincident outer-surface intersections.

Applied identically to R3.2 and the selected variant. A is material outside the
source inner cavity, excluding the five dedicated short foot platforms. B is
the remaining native structural-member union plus those platforms. C is the
remaining internal installation material. Original ledger is retained.
"""
from pathlib import Path
import sys,json,ctypes,cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import mechanics_l2
from mechanics import cylinder
from surfaces import make_surfaces
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];base=ROOT/('exports/rebuild_r3_2' if variant=='R32' else f'exports/l2_revision/{variant}')
    rp=ROOT/f'reports/l2_revision/partition_v2_{variant}';rp.mkdir(parents=True,exist_ok=True);out=ROOT/f'exports/l2_revision/partitions_v2/{variant}';out.mkdir(parents=True,exist_ok=True)
    p=json.loads((ROOT/('cad/rebuild_r2/parameters.json' if variant=='R32' else f'reports/l2_revision/{variant}/source_parameters.json')).read_text())
    d=json.loads((ROOT/('reports/rebuild_r3_2/design_metadata.json' if variant=='R32' else f'reports/l2_revision/{variant}/design_metadata.json')).read_text())
    outer,inner,_=make_surfaces(p);mech=mechanics_l2.build_mechanics(p,outer,inner)
    body=cq.importers.importStep(str(base/'assembly/BODY.step')).val();total=volume(body)[0]
    pads=[cylinder(4.,1.6,(*q['center'],5.2)) for q in d['mechanisms']['feet']];padmask=pads[0].fuse(*pads[1:])
    a=body.cut(inner.mirror('YZ')).cut(padmask);assert a.isValid(),'A invalid';print(variant,'A',volume(a)[0],flush=True)
    remaining=body.cut(a);assert remaining.isValid(),'remaining invalid'
    structural=('FOOT_','RAISED_CROSS_TIE','RAISED_DIAGONAL_TIE','LOCAL_MIDDLE_TRAY_HUB')
    tools=[s.mirror('YZ') for name,s in zip(mech['addition_labels'],mech['body_additions']) if any(name.startswith(q) for q in structural)]
    mask=padmask.fuse(*tools);assert mask.isValid(),'structural mask invalid'
    b=remaining.intersect(mask);c=remaining.cut(mask);assert b.isValid() and c.isValid(),('B/C invalid',b.isValid(),c.isValid())
    rows=[]
    for n,s in [('A_BODY_SKIN',a),('B_BODY_SKELETON',b),('C_BODY_MOUNTS',c)]:
        vol,error=volume(s);cq.exporters.export(s,str(out/(n+'.step')));rows.append(dict(category=n,mm3=vol,PA12_g=vol*.00101,PLA_solid_g=vol*.00124,adaptive_integration_error=error))
    closure=sum(q['mm3'] for q in rows)-total;assert abs(closure)<.25,(closure,total)
    for n,parts in [('C_SEPARATE_MOUNTS',['SIDE_FRONT_KEY_SWITCH_CLAMP','SIDE_REAR_KEY_SWITCH_CLAMP','WHEEL_CARRIER']),('D_MOVING_OTHER',['LEFT_KEY','RIGHT_KEY','SIDE_FRONT_KEY','SIDE_REAR_KEY','WHEEL'])]:
        vol=sum(volume(cq.importers.importStep(str(base/f'assembly/{part}.step')).val())[0] for part in parts);rows.append(dict(category=n,mm3=vol,PA12_g=vol*.00101,PLA_solid_g=vol*.00124))
    result=dict(variant=variant,method=__doc__,parts=rows,BODY_mm3=total,BODY_closure_error_mm3=closure,tolerance_mm3=.25,whole_PA12_g=sum(q['PA12_g'] for q in rows),
        scope='Native mutually exclusive BRep cut/intersection ledger. Source inner-cavity functional attribution with feet explicitly assigned to B; not directly interchangeable with the earlier outer-skin-first taxonomy. No delivered geometry modified.')
    (rp/'volume_ledger.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
