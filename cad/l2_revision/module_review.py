"""New module vs retained mechanics, actual collision/reserve and bounded entry checks."""
from pathlib import Path
import sys,json,importlib.util,numpy as np,trimesh,cadquery as cq
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
from mesh_motion import from_mesh,intersection
from audit_baseline import volume
def main():
 v=sys.argv[1];rp=ROOT/f'reports/l2_revision/{v}';out=ROOT/f'exports/l2_revision/{v}';d=json.loads((rp/'design_metadata.json').read_text())
 spec=importlib.util.spec_from_file_location('l2modvalidate',ROOT/'cad/rebuild_r3_2/validate.py');val=importlib.util.module_from_spec(spec);spec.loader.exec_module(val)
 val.OUT=out;val.RP=rp;val.WORK=ROOT.parent/f'_support/work/l2/{v}/validation';val.WORK.mkdir(parents=True,exist_ok=True)
 (rp/'electronics.json').write_text(json.dumps(dict(routes=d['electronics']['routes'])))
 val.HERE=rp;sys.argv=[sys.argv[0],'--mechanical-only'];val.main()
 met=json.loads((rp/'cad_metrics.json').read_text());models={n:val.loadmesh(out/f'assembly/{n}.stl') for n in met};checks=[]
 for row in d['electronics']['reserves']:
  n=row['name'];r=val.loadmesh(out/f'reserves/{n}.stl');hits=[]
  # Named owners may occupy their own service/optical/RF reference region.
  owner=('BATTERY_CELL_EST',) if 'BATTERY' in n else ('MATCHED_LENS_EST','D_LENS_UNVERIFIED','PAW3950_PACKAGE_EST','D_SENSOR_PACKAGE_UNVERIFIED') if 'OPTICAL' in n else ('REMOTE_ANTENNA_PCB_EST','ANTENNA_FEED_HEADER_EST') if 'ANTENNA' in n else ()
  for k,m in models.items():
   if k in owner:continue
   x=intersection(r,m)
   if x>.01:hits.append(dict(part=k,overlap_mm3=x))
  checks.append(dict(reserve=n,excluded_named_owners=list(owner),conflicts=hits,scope='RF dielectric carrier can enter the antenna study box but must be tested with actual RF hardware; all overlaps listed without silently ignoring material.'))
 common_names=json.loads((ROOT/f'reports/l2_revision/{d["common_source"]}/cad_metrics.json').read_text())
 carriers=[n for n,m in met.items() if m['printable'] and n not in common_names];fixed={n:m for n,m in models.items() if n in common_names};bad=[]
 for c in carriers:
  for dz in np.linspace(-45,0,91):
   moving=models[c].translate([0,0,dz])
   for n,m in fixed.items():
    x=intersection(moving,m)
    if x>.01:bad.append(dict(moving=c,dz_mm=float(dz),fixed=n,overlap_mm3=x))
 alternatives=[]
 for c in carriers:
  for axis in [(0,0,45),(50,0,0),(-50,0,0),(0,-100,0),(0,100,0)]:
   failures=[]
   for t in np.linspace(0,1,61):
    x=intersection(models[c].translate(np.array(axis)*t),models['BODY'])
    if x>.01:failures.append(dict(t=float(t),overlap_mm3=x))
   alternatives.append(dict(part=c,extraction_direction_mm=axis,poses=61,against='BODY only, before other components',conflicts=failures,pass_check=not failures))
 result=dict(variant=v,reserves=checks,carrier_insertion=dict(path='Translation from underside Z-45 to Z0 relative to final carrier, before new electronic parts/fasteners',samples=91,conflicts=bad,pass_check=not bad),alternative_axis_paths=alternatives,
  real_hardware_fit_verified=False,functions_verified=False)
 (rp/'module_review.json').write_text(json.dumps(result,indent=2)+'\n');print(v,'module review reserves',[(q['reserve'],len(q['conflicts'])) for q in checks],'carrier entry',not bad,flush=True)
if __name__=='__main__':main()
