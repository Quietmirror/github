"""Isolated native-CAD mount-corner and local 1.7 mm skin experiments."""
from pathlib import Path
import sys,json,copy,shutil,ctypes,cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build as exporter
from mechanics import box,cylinder,join,check
from surfaces import make_surfaces
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];assert variant in ['C1','S17'];base=ROOT/'exports/rebuild_r3_2';out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}';rp.mkdir(parents=True,exist_ok=True)
    for folder in ['assembly','print','gauges']:shutil.copytree(base/folder,out/folder,dirs_exist_ok=True)
    met=json.loads((ROOT/'reports/rebuild_r3_2/cad_metrics.json').read_text());d=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text());p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text())
    body=cq.importers.importStep(str(base/'assembly/BODY.step')).val();before=volume(body)[0]
    if variant=='C1':
        mount=cq.importers.importStep(str(ROOT/'exports/l2_revision/partitions/R32/C_BODY_MOUNTS.step')).val();tools=[]
        for y,x in [(43.,27.331),(66.,28.604)]:
            for sign in [-1,1]:
                xx=sign*x;corner=box(7.6,7.6,2.5,(xx,y,9.5)).cut(cylinder(3.8,2.5,(xx,y,8.25)))
                tools.append(corner.intersect(mount))
        description='Four square PCB-ear corners trimmed to radius3.8, only inside mutually exclusive C_BODY_MOUNTS. Existing 2.4x4 mm slots and A/B structural material retained. New bearing stress remains to be checked.'
    else:
        old_skin=cq.importers.importStep(str(ROOT/'exports/l2_revision/partitions/R32/A_BODY_SKIN.step')).val()
        q=copy.deepcopy(p);q['host']['skin']=1.7;outer,new_inner,_=make_surfaces(q)
        # Two rear-side patches outside the defined thumb/finger pinch zone,
        # all original installation/skeleton material excluded by A mask.
        tools=[new_inner.mirror('YZ').intersect(old_skin).intersect(box(8,6,12,(sgn*25,75,11))) for sgn in [-1,1]]
        description='Nominal1.7 inner cavity only in rear-side boxes X+/-25 width8,Y72..78,Z5..17, clipped to A_BODY_SKIN. Rest remains1.8. Candidate placement is geometric, not claimed stress optimisation.'
    removals=[]
    for tool in tools:
        b=volume(body)[0];body=check(body.cut(tool),'BODY_'+variant);removals.append(b-volume(body)[0])
    exporter.OUT=out;exporter.REPORT=rp;exporter.CACHE=ROOT.parent/f'_support/work/l2/{variant}/build';exporter.CACHE.mkdir(parents=True,exist_ok=True);exporter.export('BODY',body,True,met)
    after=volume(cq.importers.importStep(str(out/'assembly/BODY.step')).val())[0]
    d['parameters']['version']=variant;d['candidate_scope']=description
    for n,data in [('cad_metrics',met),('design_metadata',d),('source_parameters',p),('local_change',dict(description=description,baseline_BODY_mm3=before,new_BODY_mm3=after,net_removed_mm3=before-after,PA12_saving_g=(before-after)*.00101,individual_operations_mm3=removals,not_strength_accepted=True))]:
        (rp/f'{n}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(variant,'actual net removed',before-after,'PA12g',(before-after)*.00101,flush=True)
if __name__=='__main__':main()
