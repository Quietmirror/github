"""First single-variable full-mouse candidate: equal-area six-hole rounding.

R3.2 geometry and the original R2 generators remain immutable. P1 changes
only the opening rounding from R0.85 to R1.30 and compensates its 2D area.
This is a screening candidate, not the final L2 shell.
"""
from pathlib import Path
import importlib.util,json,sys
from shapely.geometry import Polygon
from scipy.optimize import brentq
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r32_builder',ROOT/'cad/rebuild_r3_2/build.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
original_layout=r.exporter.window_layout
records=[]

def layout(p):
    result=[];s=p['host']['scale']
    for name,points,oldtool in original_layout(p):
        poly=Polygon(points)
        target=poly.buffer(-.85,quad_segs=96).buffer(.85,quad_segs=96).area
        radius=1.30
        def smoothed(offset):
            return poly.buffer(offset,join_style='mitre').buffer(-radius,quad_segs=96).buffer(radius,quad_segs=96)
        offset=brentq(lambda x:smoothed(x).area-target,0,.5,xtol=1e-11)
        adjusted=list(poly.buffer(offset,join_style='mitre').exterior.coords)[:-1]
        raw=cq.Workplane('XY').polyline(adjusted).close().extrude(50).edges('|Z').fillet(radius).val().translate((0,0,10.5*s))
        side=-1 if name.endswith('_L') else 1
        keep=r.box(14,28,10,(-29*s,53.5*s,14.75*s)) if side<0 else r.box(14,33,8,(29*s,48*s,13*s))
        tool=raw.cut(keep)
        # Independent BRep area is computed before 3D grip-band masking.
        brep_area=raw.Volume()/50
        assert abs(brep_area-target)<.002,(name,brep_area,target)
        records.append(dict(name=name,target_original_rounded_area_mm2=target,new_brep_area_mm2=brep_area,
                            nominal_radius_mm=radius,uniform_profile_offset_mm=offset,xy=adjusted))
        result.append((name,adjusted,tool))
    return result

def main():
    variant='P1_R13';out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}'
    params=json.loads((ROOT/'cad/rebuild_r3_2/parameters.json').read_text())
    params.update(version=variant,candidate_only=True)
    config=HERE/'p1_config';config.mkdir(parents=True,exist_ok=True)
    (config/'parameters.json').write_text(json.dumps(params,indent=2)+'\n',encoding='utf8')
    r.OUT=out;r.RP=rp;r.HERE=config;r.exporter.window_layout=layout
    r.main()
    d=json.loads((rp/'design_metadata.json').read_text());d['parameters']['version']=variant
    d['candidate_scope']='P1 equal-area six-hole rounding; R3.2 side mechanism and main keys retained for isolation. Not final L2.'
    d['P1']=records
    (rp/'design_metadata.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    (rp/'equal_area_profiles.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
    print('P1 full CAD complete; downstream checks required',flush=True)

if __name__=='__main__':main()
