"""Bounded actual extrusion checks at critical feature regions and foot supports."""
from pathlib import Path
import sys,json,re,math,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[2]
def main():
 v=sys.argv[1];rp=ROOT/f'reports/l2_revision/{v}'
 met=json.loads((rp/'cad_metrics.json').read_text());d=json.loads((rp/'design_metadata.json').read_text());s=json.loads((rp/'slice_summary.json').read_text())
 placements={p['part']:p for p in s['placements']}
 def point(n,p):
  m=met[n];r=trimesh.transformations.rotation_matrix(math.radians(m.get('print_rotation_y_deg',0)),[0,1,0]);q=(r@[*p,1])[:3]+np.array(m['print_translation']);return (np.array(placements[n]['print_to_plate_matrix'])@[*q,1])[:3]
 feet=[point('BODY',[*f['center'],5.2]) for f in d['mechanisms']['feet']];counts=[0]*5
 # Region occupancy is a modest, auditable check, not a dimensional fit certificate.
 regions=[]
 for n in ['SIDE_FRONT_KEY','SIDE_REAR_KEY','WHEEL','WHEEL_CARRIER','LEFT_KEY','RIGHT_KEY']:
  m=met[n];center=(np.array(m['min'])+np.array(m['max']))/2;regions.append(dict(part=n,center_plate_mm=point(n,center).tolist(),radius_mm=5.,segments=0,layers=set()))
 path=ROOT.parent/f'_support/work/l2/{v}/slice/{v}_validation_only.gcode';cur=dict(X=0.,Y=0.,Z=0.,E=0.);relative=False;role='';layer=-1
 for line in path.open(encoding='utf8'):
  if line.startswith(';LAYER_CHANGE'):layer+=1
  if line.startswith(';TYPE:'):role=line[6:].strip()
  code=line.split(';',1)[0].strip()
  if code=='M83':relative=True
  elif code=='M82':relative=False
  elif code.startswith('G92'):
   for k,val in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code):cur[k]=float(val)
  elif re.match(r'^G[01](?: |$)',code):
   old=cur.copy();a={k:float(val) for k,val in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)};de=a.get('E',0.) if relative else a.get('E',cur['E'])-cur['E']
   for k in 'XYZ':cur[k]=a.get(k,cur[k])
   if 'E' in a:cur['E']=cur['E']+de if relative else a['E']
   pa=np.array([old[k] for k in 'XYZ']);pb=np.array([cur[k] for k in 'XYZ']);delta=pb-pa;den=float(delta@delta)
   if de<=0 or den<1e-8:continue
   if layer==0 and role.startswith('Support'):
    for i,p in enumerate(feet):
     q=pa[:2]+np.clip(((p[:2]-pa[:2])@delta[:2])/(delta[:2]@delta[:2]+1e-30),0,1)*delta[:2]
     if np.linalg.norm(q-p[:2])<3.5:counts[i]+=1
   if 'Support' in role or 'Skirt' in role or 'Brim' in role:continue
   for row in regions:
    p=np.array(row['center_plate_mm']);near=pa+np.clip((p-pa)@delta/den,0,1)*delta
    if np.linalg.norm(near-p)<row['radius_mm']:row['segments']+=1;row['layers'].add(round(cur['Z'],3))
 for r in regions:r['layers']=sorted(r['layers']);r['pass_check']=r['segments']>0 and len(r['layers'])>2
 result=dict(variant=v,foot_centers_plate_mm=[p.tolist() for p in feet],first_layer_support_segments_within_3_5mm=counts,regions=regions,
  pass_check=all(c>0 for c in counts) and all(r['pass_check'] for r in regions),
  scope='Actual extrusions beneath five feet and in six critical component regions. Does not certify every wall, bore size, hex fit or support removability; 0.02/0.03 mm actuator gaps and 0.06 mm encoder fit require coupons and measured postprocessing.')
 (rp/'toolpath_review.json').write_text(json.dumps(result,indent=2)+'\n');print(v,'toolpath',counts,result['pass_check'],flush=True)
if __name__=='__main__':main()
