"""K14 with two deeper longitudinal ribs, without changing touch footprint."""
import sys,json,ctypes
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build as exporter
from mechanics import box,check
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    name='K14R';out=ROOT/f'exports/l2_revision/{name}';rp=ROOT/f'reports/l2_revision/{name}';rp.mkdir(parents=True,exist_ok=True)
    exporter.OUT=out;exporter.REPORT=rp;exporter.CACHE=ROOT.parent/f'_support/work/l2/{name}/build';exporter.CACHE.mkdir(parents=True,exist_ok=True)
    outer=cq.importers.importStep(str(ROOT/'exports/rebuild_r3_2/gauges/MOTHER_OUTER_REFERENCE.step')).val();met={};rows=[]
    for part,sign in [('LEFT_KEY',1),('RIGHT_KEY',-1)]:
        key=cq.importers.importStep(str(ROOT/f'exports/l2_revision/K14/assembly/{part}.step')).val()
        before=volume(key)[0]
        ribbed_skin=outer.cut(outer.translate((0,0,-3.0)))
        for x in (12.1,25.3):
            rib=ribbed_skin.intersect(box(1.4,23,50,(sign*x,19.5,25)))
            key=key.fuse(rib)
        key=check(key.clean(),part);exporter.export(part,key,True,met)
        rows.append(dict(part=part,volume_mm3=volume(key)[0],added_to_K14_mm3=volume(key)[0]-before,
            ribs=dict(width_mm=1.4,overall_vertical_depth_mm=3.,y_range_mm=[8,31],x_centers_abs_mm=[12.1,25.3])))
    (rp/'cad_metrics.json').write_text(json.dumps(met,indent=2)+'\n')
    (rp/'key_pockets.json').write_text(json.dumps(dict(candidate=name,parts=rows,status='CANDIDATE_CLEARANCE_AND_FEM_PENDING'),indent=2)+'\n')
    print(rows,flush=True)
if __name__=='__main__':main()
