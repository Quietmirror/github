"""One common set plus both actually generated, clearly estimated adapter kits."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[2]
def main():
 v='L2_BOTH_EST';out=ROOT/f'exports/l2_revision/{v}';rp=ROOT/f'reports/l2_revision/{v}';rp.mkdir(parents=True,exist_ok=True)
 c=ROOT/'exports/l2_revision/F1H';met=json.loads((ROOT/'reports/l2_revision/F1H/cad_metrics.json').read_text());d=json.loads((ROOT/'reports/l2_revision/F1H/design_metadata.json').read_text())
 for folder in ['assembly','print','gauges']:shutil.copytree(c/folder,out/folder,dirs_exist_ok=True)
 for route in ['H','D']:
  name='L2_'+route+'_EST';r=ROOT/f'reports/l2_revision/{name}';m=json.loads((r/'cad_metrics.json').read_text());check=json.loads((r/'mesh_and_volume.json').read_text());assert check['pass_check']
  for n,info in m.items():
   if info['printable'] and n not in met:
    met[n]=info
    for folder in ['assembly','print']:
     for ext in ['stl','step']:shutil.copyfile(ROOT/f'exports/l2_revision/{name}/{folder}/{n}.{ext}',out/f'{folder}/{n}.{ext}')
 (rp/'cad_metrics.json').write_text(json.dumps(met,indent=2)+'\n');d['parameters']['version']=v;d['scope']='PRINT KIT ONLY: common plastic plus two alternative adapter kits; never install both at once. Electronic fit blockers remain.';(rp/'design_metadata.json').write_text(json.dumps(d,indent=2)+'\n')
 print(v,'prepared',sum(m['printable'] for m in met.values()),'separate parts',flush=True)
if __name__=='__main__':main()
