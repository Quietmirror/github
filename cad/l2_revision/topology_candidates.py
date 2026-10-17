"""Single-variable full CAD candidates, preserving all R3.2 mechanisms.

P2 splits rear bays into triangular cells. P3 uses local hexagonal cells;
P4 rounded large openings; P5 directional ellipses; P6 graded round profiles.
Design limits constrain profile growth to 0.65 mm from original polygon.
An infeasible equal-area target is reported, never silently thinned to fit.
"""
from pathlib import Path
import sys,json,math
import numpy as np,cadquery as cq
from shapely.geometry import Polygon,Point,LineString
from shapely import affinity
from shapely.ops import unary_union
from scipy.optimize import brentq
from build_p1 import r,ROOT,HERE,original_layout
records=[];FAMILY='P2'
def polygons(g):return [g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon' and p.area>2]
def make_profile(poly,family,offset):
    allowed=poly.buffer(offset,join_style='mitre')
    if family in ['P1_R10','P1_R15','P4','P6']:
        radius={'P1_R10':1.,'P1_R15':1.5,'P4':3.8,'P6':1.3 if poly.area<200 else 2.2}[family]
        return allowed.buffer(-radius,quad_segs=12).buffer(radius,quad_segs=12)
    if family=='P2':
        pts=list(allowed.exterior.coords)[:-1]
        if len(pts)==3:return allowed.buffer(-1.1,quad_segs=12).buffer(1.1,quad_segs=12)
        cut=LineString([pts[0],pts[2]]).buffer(.9,cap_style='square')
        return allowed.difference(cut).buffer(-.85,quad_segs=12).buffer(.85,quad_segs=12)
    if family=='P3':
        xmin,ymin,xmax,ymax=allowed.bounds;cells=[];radius=6.0
        for j,y in enumerate(np.arange(math.floor(ymin/10)*10,ymax+10,10.)):
            for x in np.arange(math.floor(xmin/11.6)*11.6,xmax+12,11.6):
                center=[x+(5.8 if j%2 else 0),y]
                pts=[(center[0]+radius*math.cos(t),center[1]+radius*math.sin(t)) for t in np.linspace(0,2*math.pi,6,endpoint=False)]
                q=Polygon(pts).buffer(-.8,join_style='mitre').intersection(allowed)
                q=q.buffer(-.65,quad_segs=10).buffer(.65,quad_segs=10)
                if not q.is_empty:cells.extend(polygons(q))
        return unary_union(cells)
    if family=='P5':
        # Principal-axis ellipse inside the local protected bay.
        pts=np.array(poly.exterior.coords[:-1]);center=np.array(poly.centroid.coords[0]);cov=np.cov((pts-center).T)
        eig,v=np.linalg.eigh(cov);direction=v[:,-1];angle=np.rad2deg(np.arctan2(direction[1],direction[0]))
        u=affinity.rotate(poly,-angle,origin=tuple(center));b=u.bounds
        disk=Point(center).buffer(1,resolution=48)
        e=affinity.scale(disk,xfact=(b[2]-b[0])/2+offset,yfact=(b[3]-b[1])/2+offset,origin=tuple(center))
        return affinity.rotate(e,angle,origin=tuple(center)).intersection(allowed)
    raise ValueError(family)
def layout(p):
    result=[];s=p['host']['scale']
    for name,points,unused in original_layout(p):
        poly=Polygon(points);target=poly.buffer(-.85,quad_segs=64).buffer(.85,quad_segs=64).area
        lo,hi=-.3,.65;maxarea=make_profile(poly,FAMILY,hi).area
        feasible=maxarea>=target
        off=brentq(lambda x:make_profile(poly,FAMILY,x).area-target,lo,hi,xtol=1e-7) if feasible else hi
        geom=make_profile(poly,FAMILY,off);pieces=polygons(geom)
        side=-1 if name.endswith('_L') else 1
        keep=r.box(14,28,10,(-29*s,53.5*s,14.75*s)) if side<0 else r.box(14,33,8,(29*s,48*s,13*s))
        for j,q in enumerate(pieces):
            points2=list(q.exterior.coords)[:-1]
            raw=cq.Workplane('XY').polyline(points2).close().extrude(50).val().translate((0,0,10.5*s))
            result.append((name+f'_{j}',points2,raw.cut(keep)))
        records.append(dict(bay=name,profile_count=len(pieces),original_rounded_area_mm2=target,new_area_mm2=geom.area,
            equal_projected_area_feasible=feasible,profile_growth_mm=off,maximum_allowed_growth_mm=.65,
            area_deficit_mm2=max(0,target-geom.area),source_geometry=geom.__geo_interface__))
    return result
def main():
    global FAMILY
    FAMILY=sys.argv[1];assert FAMILY in ('P1_R10','P1_R15','P2','P3','P4','P5','P6')
    variant=FAMILY;out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    config=HERE/'configs'/variant;config.mkdir(parents=True,exist_ok=True)
    params=json.loads((ROOT/'cad/rebuild_r3_2/parameters.json').read_text());params.update(version=variant,candidate_only=True)
    (config/'parameters.json').write_text(json.dumps(params,indent=2)+'\n')
    r.OUT=out;r.RP=rp;r.HERE=config;r.exporter.window_layout=layout;r.main()
    d=json.loads((rp/'design_metadata.json').read_text());d['parameters']['version']=variant
    d['candidate_scope']='Single-variable topology screening. Original R3.2 mechanisms. Not L2 accepted.';d['topology_profiles']=records
    (rp/'design_metadata.json').write_text(json.dumps(d,indent=2)+'\n')
    (rp/'topology_feasibility.json').write_text(json.dumps(dict(variant=variant,profiles=records),indent=2)+'\n')
    print(variant,'actual CAD built; independent mesh/structure validation pending',flush=True)
if __name__=='__main__':main()
