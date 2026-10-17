"""Re-run ordered finite assembly paths using current side-switch coordinates."""
import importlib.util,inspect,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    variant=sys.argv[1]
    spec=importlib.util.spec_from_file_location('old_insertion',ROOT/'cad/rebuild_r3_2/insertion_check.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    old.RP=ROOT/f'reports/l2_revision/{variant}';old.OUT=ROOT/f'exports/l2_revision/{variant}/assembly'
    d=json.loads((old.RP/'design_metadata.json').read_text())
    centers={m['part']:m['actuation_point'][1] for m in d['mechanisms']['side_motions']}
    old.SIDE_Z={m['part']:m['actuation_point'][2] for m in d['mechanisms']['side_motions']}
    src=inspect.getsource(old.main)
    route_file=old.RP/'side_switch_route_search.json'
    if route_file.exists():
        old.ROUTES={q['part']:q['waypoints'] for q in json.loads(route_file.read_text())['routes'] if 'waypoints' in q}
    else:old.ROUTES={}
    src=src.replace("for suffix,cy in [('REAR',65.),('FRONT',50.)]:",f"for suffix,cy in {[(q,centers['SIDE_'+q+'_KEY']) for q in ['FRONT','REAR']]}:")
    src=src.replace("n='SWITCH_SIDE_'+suffix", "n='SWITCH_SIDE_'+suffix\n        entry_lift=19.2-SIDE_Z['SIDE_'+suffix+'_KEY'];transfer_lift=17.2-SIDE_Z['SIDE_'+suffix+'_KEY']")
    src=src.replace('[[entry_x,-cy-15,4.2],[entry_x,43.5-cy,4.2],[entry_x,43.5-cy,2.2],[entry_x,0,2.2],[0,0,2.2],[0,0,0]]',
        "ROUTES[n]")
    # Install both switches before the clamps; otherwise the first clamp
    # obstructs the second clamp's same-height entry from the open nose.
    src=src.replace("        clamp='SIDE_'+suffix+'_KEY_SWITCH_CLAMP'\n        path(clamp,[clamp],[[0,-cy-20,0],[0,0,0]])",'')
    clamp_loop=f"    for suffix,cy in {[(q,centers['SIDE_'+q+'_KEY']) for q in ['REAR','FRONT']]}:\n        clamp='SIDE_'+suffix+'_KEY_SWITCH_CLAMP'\n        path(clamp,[clamp],[[0,-cy-20,0],[0,0,0]])\n"
    src=src.replace("    path('SWITCH_MIDDLE'",clamp_loop+"    path('SWITCH_MIDDLE'")
    src=src.replace("waypoints=[[20,-.30,0],[0,-.30,0],[0,0,0]] if suffix=='REAR' else [[20,0,0],[0,0,0]]","waypoints=[[20,0,0],[0,0,0]]")
    src=src.replace("'Offset 0.30mm towards the nose, insert from the left, then slide back 0.30mm into final position before fitting the capture pin. Straight insertion interferes at the new rear aperture edge; physical tolerance remains unverified.'", "'New aligned side mechanisms: straight X insertion before capture pins. No Y-offset workaround. Finite paths only; actual tolerances unverified.'")
    exec(compile(src,'l2_current_insertion','exec'),old.__dict__);old.main()
if __name__=='__main__':main()
