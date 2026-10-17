"""Bounded translation route search from the open underside, actual meshes."""
from pathlib import Path
import sys,json,ctypes,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
from mesh_motion import from_mesh,intersection
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1];base=ROOT/f'exports/l2_revision/{variant}/assembly';rp=ROOT/f'reports/l2_revision/{variant}'
    d=json.loads((rp/'design_metadata.json').read_text());fixed=[from_mesh(trimesh.load_mesh(base/'BODY.stl'))];routes=[]
    for suffix in ['FRONT','REAR']:
        n='SWITCH_SIDE_'+suffix;raw=trimesh.load_mesh(base/f'{n}.stl');moving=from_mesh(raw)
        m=next(q for q in d['mechanisms']['side_motions'] if q['switch']==n);cy=m['actuation_point'][1];cz=m['actuation_point'][2]
        center_x=float(raw.bounds[:,0].mean());attempts=0;chosen=None
        def clear(points):
            worst=0.;count=0
            for a,b in zip(points[:-1],points[1:]):
                a=np.array(a);b=np.array(b);steps=max(2,int(np.ceil(np.linalg.norm(b-a)/.75))+1)
                for t in np.linspace(0,1,steps):
                    state=a*(1-t)+b*t;obj=moving.translate(state.tolist());count+=1
                    v=max(intersection(obj,f) for f in fixed);worst=max(worst,v)
                    if v>.01:return False,count,worst
            return True,count,worst
        for lift in [2.0,2.2,1.8,2.4,2.6,1.6,3.0]:
            for absolute_x in [0.,-5.,5.,-10.,10.,15.]:
                for delta_y in [0.,-5.,5.,-10.,10.,-15.,15.]:
                    dx=absolute_x-center_x
                    for transfer_x in [dx,-5.,0.]:
                        points=[[dx,delta_y,-35.],[dx,delta_y,lift],[transfer_x,delta_y,lift],[transfer_x,0.,lift],[0.,0.,lift],[0.,0.,0.]]
                        attempts+=1;ok,count,worst=clear(points)
                        if ok:
                            chosen=dict(part=n,waypoints=points,samples=count,maximum_overlap_mm3=worst,attempts=attempts)
                            break
                    if chosen:break
                if chosen:break
            if chosen:break
        routes.append(chosen or dict(part=n,pass_check=False,attempts=attempts))
        print(n,routes[-1],flush=True)
        if not chosen:break
        fixed.append(moving)
        fixed.append(from_mesh(trimesh.load_mesh(base/f'SIDE_{suffix}_KEY_SWITCH_CLAMP.stl')))
    (rp/'side_switch_route_search.json').write_text(json.dumps(dict(routes=routes,scope='Finite translation paths from open underside; no force or full swept-volume certification.'),indent=2)+'\n')
if __name__=='__main__':main()
