"""Real complete BODY candidates B1--B4; no historical sources overwritten."""
from pathlib import Path
import sys,json
from build_p1 import r,ROOT,HERE
import mechanics_l2
from surfaces import make_surfaces
def main():
    variant=sys.argv[1];assert variant in ['B1','B2','B3','B4']
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text());p['l2']={'skeleton':variant}
    p['l2']['diagnostic_dir']=str(ROOT/f'exports/l2_revision/failed_construction/{variant}')
    outer,inner,_=make_surfaces(p);mech=mechanics_l2.build_mechanics(p,outer,inner)
    r.build_mechanics=lambda *args:mech
    out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    config=HERE/'configs'/variant;config.mkdir(parents=True,exist_ok=True)
    params=json.loads((ROOT/'cad/rebuild_r3_2/parameters.json').read_text());params.update(version=variant,candidate_only=True)
    (config/'parameters.json').write_text(json.dumps(params,indent=2)+'\n')
    r.OUT=out;r.RP=rp;r.HERE=config;r.main()
    (rp/'source_parameters.json').write_text(json.dumps(p,indent=2)+'\n')
    d=json.loads((rp/'design_metadata.json').read_text());d['parameters']['version']=variant
    d['candidate_scope']='Single-variable upper skeleton comparison; original key interfaces and five feet. Not L2 released.'
    d['skeleton']=p['l2'];(rp/'design_metadata.json').write_text(json.dumps(d,indent=2)+'\n')
    print(variant,'full CAD complete; net volume, mesh and FEM pending',flush=True)
if __name__=='__main__':main()
