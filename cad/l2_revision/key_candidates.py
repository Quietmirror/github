"""Backside key pockets: preserve outer touch surface, footprint and interfaces."""
from pathlib import Path
import sys,json,ctypes
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(1,str(ROOT/'cad/rebuild_r2'))
import build as exporter
from mechanics import box,cylinder,check
from audit_baseline import volume

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    outer=cq.importers.importStep(str(ROOT/'exports/rebuild_r3_2/gauges/MOTHER_OUTER_REFERENCE.step')).val()
    results=[]
    for thickness in [1.6,1.4,1.2]:
        label=f'K{int(round(thickness*10))}';out=ROOT/f'exports/l2_revision/{label}';rp=ROOT/f'reports/l2_revision/{label}';rp.mkdir(parents=True,exist_ok=True)
        exporter.OUT=out;exporter.REPORT=rp;exporter.CACHE=ROOT.parent/f'_support/work/l2/{label}/build';exporter.CACHE.mkdir(parents=True,exist_ok=True)
        metrics={};rows=[]
        for name,sign in [('LEFT_KEY',1),('RIGHT_KEY',-1)]:
            original=cq.importers.importStep(str(ROOT/f'exports/rebuild_r3_2/assembly/{name}.step')).val()
            cx=sign*18.3
            area=cq.Workplane('XY').box(14,24,55).edges('|Z').fillet(1.).val().translate((cx,19,27.5))
            # A 2 mm full-thickness longitudinal spine and switch contact island
            # retain the existing load route; holes/pin barrel/web are outside.
            keep=box(2.,40,60,(cx,20,30)).fuse(cylinder(3.2,60,(cx,24,0)))
            tool=outer.translate((0,0,-thickness)).intersect(area.cut(keep))
            key=check(original.cut(tool).clean(),name)
            before,_=volume(original);after,_=volume(key)
            assert 0<before-after<700,(name,before,after)
            exporter.export(name,key,True,metrics)
            rows.append(dict(part=name,remaining_vertical_skin_mm=thickness,removed_mm3=before-after,
                PA12_saving_g=(before-after)*.00101,pocket_Y_mm=[7,31],protected_spine_width_mm=2.,contact_island_radius_mm=3.2,
                limit='Nominal vertical skin, not minimum normal wall; torsion/edge-press and slicing validation required.'))
        report=dict(candidate=label,parts=rows,total_saving_g=sum(r['PA12_saving_g'] for r in rows),status='CANDIDATE_NOT_RELEASED')
        (rp/'key_pockets.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        (rp/'cad_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8')
        results.append(report);print(label,report['total_saving_g'],flush=True)
    (ROOT/'reports/l2_revision/key_candidates.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
