"""Fenrir-informed original F1/F2 caps with aligned relocated internal sliders.

This deliberately changes the microswitch, guide, pin and clamp coordinates
together. It does not retain R3.2's eccentric cap-to-slider translation.
"""
from pathlib import Path
import sys,importlib.util,json,copy,ctypes,shutil
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(1,str(ROOT/'cad/rebuild_r2'))
from mechanics import box,check
from surfaces import half_width,roof_height
from audit_baseline import volume
import mechanics_l2
spec=importlib.util.spec_from_file_location('r32_side_base',ROOT/'cad/rebuild_r3_2/build.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
from build_p1 import layout

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    variant=sys.argv[1] if len(sys.argv)>1 else 'F1'
    assert variant in ('F1','F2','F1S','F2S','F1_P0','F2_P0','F1B','F2B','F1C','F2C','F1D','F2D','F1V','F2V','F1W')
    style='F2' if variant.startswith('F2') else 'F1'
    out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}';rp.mkdir(parents=True,exist_ok=True)
    for folder in ('assembly','print','gauges'):
        shutil.copytree(ROOT/f'exports/rebuild_r3_2/{folder}',out/folder,dirs_exist_ok=True)
    corrected=variant.endswith(('B','C','D','V','W'))
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text());p['side']['centers_y']=[49.,62.];p['side']['z']=15.5 if corrected else 17.5
    p['l2']={'skeleton':'B0'}
    if variant.endswith('C'):p['l2']['upper_cross_tie_y']=[58.,71.]
    if variant.endswith(('D','V','W')):
        p['l2'].update(upper_cross_tie_path='dogleg_between_tools',side_guide_length_mm=5.4)
    if variant.endswith(('V','W')):p['l2']['dogleg_vertical_scale']=1.4
    d=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text())
    metrics=json.loads((ROOT/'reports/rebuild_r3_2/cad_metrics.json').read_text())
    outer=cq.importers.importStep(str(out/'gauges/MOTHER_OUTER_REFERENCE.step')).val()
    source_outer,source_inner,_=r.make_surfaces(p)
    mech=mechanics_l2.build_mechanics(p,source_outer,source_inner)
    original_sides=r.exporter.mirror_metadata(mech['metadata']['side_motions'])
    d['mechanisms']['side_motions']=original_sides
    d['mechanisms']['motions']=[m for m in d['mechanisms']['motions'] if not m['part'].startswith('SIDE_')]+copy.deepcopy(original_sides)
    d['parameters']['side']=p['side'];d['parameters']['version']=variant
    r.exporter.OUT=out;r.exporter.REPORT=rp;r.exporter.CACHE=ROOT.parent/f'_support/work/l2/{variant}/build';r.exporter.CACHE.mkdir(parents=True,exist_ok=True)
    # Every side-specific purchased part moves with the newly aligned socket.
    for name,s in {**mech['parts'],**mech['hardware']}.items():
        if name.startswith('SIDE_') or name.startswith('SWITCH_SIDE_'):
            r.exporter.export(name,s.mirror('YZ'),metrics[name]['printable'],metrics)
    length=10.4;height=3.6 if style=='F1' else 4.0;offset=.18 if style=='F1' else .30
    apertures={};rows=[]
    for cy,name in zip(p['side']['centers_y'],('SIDE_FRONT_KEY','SIDE_REAR_KEY')):
        cz=p['side']['z'];w=half_width(cy,p);h=roof_height(cy,p)
        wall=w*(1-((cz-5)/(h-5))**3.4)**(1/3.4);back=wall-1.45
        old=mech['parts'][name].mirror('YZ')
        mask=r.yz_mask(length,height,cy,cz,.7)
        if style=='F2':mask=mask.rotate((0,cy,cz),(1,cy,cz),3.)
        cap=outer.translate((offset,0,0)).intersect(mask).intersect(box(20,100,50,(back+10,44,25)))
        exposed=[e for e in cap.Edges() if min(v.X for v in e.Vertices())>back+.1]
        if exposed:cap=cap.Solids()[0].fillet(.22,exposed)
        hidden=old.intersect(box(8,5.2,3.4,(wall-5.8,cy,cz)))
        neck=box(.8,5.2,3.4,(wall-1.7,cy,cz)).intersect(mask)
        stops=[old.intersect(box(.5,1.,2.8,(wall-1.36,cy+dy,cz))) for dy in (-3.9,3.9)]
        key=check(hidden.fuse(neck).fuse(cap).fuse(*stops),name)
        r.exporter.export(name,key,True,metrics)
        clear=r.yz_mask(length+.7,height+.7,cy,cz,1.05)
        if style=='F2':clear=clear.rotate((0,cy,cz),(1,cy,cz),3.)
        aperture=clear.intersect(box(20,100,50,(back-.65+10,44,25)))
        apertures[round(cy)]=dict(skin=[clear,box(10,5.8,4.,(wall-6.5,cy,cz))],supports=[aperture])
        rows.append(dict(name=name,cap_center=[wall,cy,cz],touch_length_y_mm=length,touch_height_z_mm=height,
                         nominal_X_offset_mm=offset,local_normal_protrusion='To be measured on final cap versus mother surface',
                         relocated_micro_switch=True,two_end_stops=True,straight_insertion='Pending exported mesh check'))
    r.build_mechanics=lambda *args:mech
    if not (variant.endswith('_P0') or corrected) or variant.endswith('W'):r.exporter.window_layout=layout
    if variant.endswith('S'):
        from body_builder import rebuild_body
        body=rebuild_body(r,p,d,apertures)
    else:body=r.rebuild_body(p,d,apertures)
    # Do not auto-remove unexpected cavities or disconnected material.
    if not body.isValid() or len(body.Solids())!=1:
        cq.exporters.export(body,str(r.exporter.CACHE/'failed_body.step'))
        fail=[]
        for solid in body.Solids():
            bb=solid.BoundingBox();fail.append(dict(volume=volume(solid)[0],bounds=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]))
        (rp/'construction_failure.json').write_text(json.dumps(dict(parameters=p,valid=body.isValid(),components=fail),indent=2)+'\n')
    body=check(body,'BODY');r.exporter.export('BODY',body,True,metrics)
    d['candidate_scope']='Joint cap/slider/socket revision. Full clearance and force checks are pending; not final L2.'
    d['side_touch_geometry']=rows
    d['l2_side']={'variant':variant,'length_mm':length,'height_mm':height,'centers_y_mm':[49,62],
                  'center_z_mm':p['side']['z'],'gap_mm':13-length,'edge_clearance_mm':.35,'normal_offset_limit_mm':offset,
                  'clamp_length_mm':12.4,'original_nominal_travel_mm':.6,'no_eccentric_y_offset':True,
                  'outline_slope_deg':3. if style=='F2' else 0.,'keep_boolean_face_partitions':variant.endswith('S'),
                  'roof_hole_family':'P0_R085' if (variant.endswith('_P0') or corrected) and not variant.endswith('W') else 'P1_R130_EQUAL_AREA'}
    # Carry side-specific fastener coordinates and assembly instructions with
    # the actual new mechanism, instead of inherited R3.2 coordinates.
    new_meta=r.exporter.mirror_metadata(mech['metadata'])
    d['mechanisms']['raised_cross_ties']=new_meta['raised_cross_ties']
    d['mechanisms']['fasteners']=[q for q in d['mechanisms']['fasteners'] if not str(q).startswith("{'name': 'SIDE_") and not any(str(v).startswith('SIDE_') for v in q.values() if isinstance(v,str))]+[q for q in new_meta['fasteners'] if any(str(v).startswith('SIDE_') for v in q.values() if isinstance(v,str))]
    for name,data in [('design_metadata',d),('cad_metrics',metrics),('source_parameters',p)]:
        (rp/f'{name}.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(variant,'complete pending checks; BODY',volume(body),flush=True)

if __name__=='__main__':main()
