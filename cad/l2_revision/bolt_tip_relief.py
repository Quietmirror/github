"""Tiny local clearance for the existing M2x12 tip, without changing the screw."""
from pathlib import Path
import sys,json,shutil,ctypes
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build as exporter
from mechanics import cylinder,check
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    source=sys.argv[1] if len(sys.argv)>1 else 'F1D';variant=sys.argv[2] if len(sys.argv)>2 else 'F1E'
    out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}';rp.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/f'exports/l2_revision/{source}',out,dirs_exist_ok=True)
    for n in ['cad_metrics.json','design_metadata.json','source_parameters.json']:shutil.copyfile(ROOT/f'reports/l2_revision/{source}/{n}',rp/n)
    met=json.loads((rp/'cad_metrics.json').read_text());d=json.loads((rp/'design_metadata.json').read_text())
    body=cq.importers.importStep(str(out/'assembly/BODY.step')).val();before=volume(body)[0]
    bolt=met['SIDE_FRONT_KEY_M2_SWITCH_1_BOLT'];x=(bolt['min'][0]+bolt['max'][0])/2;y=(bolt['min'][1]+bolt['max'][1])/2
    tool=cylinder(1.25,1.05,(x,y,bolt['min'][2]-.1));after_shape=check(body.cut(tool),'BODY_TIP_RELIEF')
    removed=before-volume(after_shape)[0];assert .01<removed<5.,removed
    exporter.OUT=out;exporter.REPORT=rp;exporter.CACHE=ROOT.parent/f'_support/work/l2/{variant}/build';exporter.CACHE.mkdir(parents=True,exist_ok=True)
    exporter.export('BODY',after_shape,True,met)
    d['parameters']['version']=variant;d['l2_side']['variant']=variant
    d['bolt_tip_relief']=dict(source=source,center_xy_mm=[x,y],radius_mm=1.25,z_mm=[bolt['min'][2]-.1,bolt['min'][2]+.95],removed_mm3=removed,
        purpose='Clear existing M2x12 tip below the nut; retain full nut/washer stack and four existing side-switch screws.')
    for m in d['mechanisms']['side_motions']+[q for q in d['mechanisms']['motions'] if q['part'].startswith('SIDE_')]:
        m.update(guide_length_mm=5.4,minimum_guide_engagement_mm=5.1)
    for n,v in [('cad_metrics',met),('design_metadata',d)]: (rp/f'{n}.json').write_text(json.dumps(v,indent=2)+'\n')
    print(variant,'net relief',removed,'mm3',flush=True)
if __name__=='__main__':main()
