"""Parameterised H/D study kits after the common-shell digital review gate.

No placeholder is a supplier drawing, a donor fit certificate or a PCB design.
"""
from pathlib import Path
import sys,json,copy,shutil,ctypes,math,cadquery as cq
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build as exporter
from mechanics import box,cylinder,beam,join,check
from audit_baseline import volume
def carrier(route):
    def beam(a,b,radius):
        # Rectangular rails avoid the failed near-tangent capsule seams in
        # R1. The changed cross-section is real CAD, not an STL patch.
        va=cq.Vector(*a);vb=cq.Vector(*b);direction=vb-va
        return cq.Workplane(cq.Plane(origin=(va+vb)*.5,normal=direction)).box(2*radius,2*radius,direction.Length+2*radius).val()
    # The inherited ear's connecting arm partly fills its advertised slot.
    # R0 screws collided with it. This revision uses removable insulating
    # straps around two retained lower ribs, not invented cleared M2 holes.
    pieces=[beam((-26.7,67.8,12.1),(-22.,71.,12.1),1.),beam((-22.,71.,12.1),(-9.,71.,12.1),1.),
        beam((-9.,71.,12.1),(-9.,79.5,12.1),1.),beam((-9.,79.5,12.1),(10.5,79.5,12.1),1.)]
    # Side rail avoids the estimated optical passage and the side-switch pins.
    pieces.extend([beam((10.5,51.4,13.4),(10.5,79.5,12.1),.9),
        box(14.5,1.6,1.6,(4.,58.,13.4))])
    if route=='H':
        # Upper controller seats are a separate height from the sensor board.
        pieces.extend([beam((-9.,71.,12.1),(-5.8,72.5,17.),.8),beam((-5.8,72.5,17.),(10.8,72.5,17.),.8)])
        for x in [-5.8,10.8]:pieces.append(beam((x,57.,17.),(x,72.5,17.),.8))
        pieces.extend([beam((-6.2,72.5,17.1),(-6.7,61.5,23.4),.9),
            beam((-6.7,61.5,23.4),(-4.6,61.5,23.4),.9),box(10.,6.,1.2,(0.,61.5,24.))])
    # Removable cell rests on two open strips, with 0.5 mm example foam space.
    for y in [46.2,67.8]:pieces.append(box(19.2,2.,1.6,(-17.,y,12.1)))
    for x in [-26.7,-8.7]:pieces.append(box(1.8,23.6,1.6,(x,57.,12.1)))
    for x in [-26.7,-8.7]:pieces.append(box(3.6,5.,1.6,(x,57.5,12.1)).cut(box(1.2,3.5,4.,(x,57.5,12.1))))
    for x in [-22.,-13.]:
        y=46.+abs(x)*16.64/24.84
        saddle=box(5.6,5.,3.,(x,y,9.4)).cut(beam((-24.84,62.64,6.5),(0,46,6.5),1.55))
        # Side slots accept removable nonconductive cable ties; width is an
        # estimate and retention/cyclic load are unverified.
        saddle=saddle.cut(box(1.2,3.2,4.,(x-2.,y,10.2))).cut(box(1.2,3.2,4.,(x+2.,y,10.2)))
        pieces.extend([saddle,beam((x,y,10.6),(x,67.8,12.1),.9)])
    result=join(*pieces)
    # Native local keep-outs from actual common parts. Each intersecting solid
    # becomes a conservative axis-aligned relief with0.3mm margin. No change
    # to the common shell and no discarded disconnected carrier component.
    common=ROOT/'exports/l2_revision/F1H/assembly'
    for n in ['BODY','SWITCH_MIDDLE','WHEEL_M2_SWITCH_2_BOLT','WHEEL_M2_SWITCH_2_WASHER_NUT','WHEEL_M2_SWITCH_2_NUT']:
        obstruction=cq.importers.importStep(str(common/(n+'.step'))).val()
        overlaps=result.intersect(obstruction)
        for solid in overlaps.Solids():
            b=solid.BoundingBox();result=result.cut(box(b.xlen+.6,b.ylen+.6,b.zlen+.6,((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2)))
    result=result.cut(box(19.,23.,7.,(-17.,57.,16.4)))
    if route=='H':
        wire=next(q for q in json.loads((ROOT/'cad/rebuild_r3_2/electronics.json').read_text())['routes'] if q['name']=='ANTENNA_FEED_ROUTE_EST')
        for a,b in zip(wire['points'][:-1],wire['points'][1:]):result=result.cut(beam(a,b,wire['radius']+.25))
    debug=ROOT.parent/'_support/work/l2/module_debug';debug.mkdir(parents=True,exist_ok=True)
    cq.exporters.export(result,str(debug/(route+'_carrier.step')))
    solids=sorted(result.Solids(),key=lambda s:volume(s)[0],reverse=True)
    assert len(solids)==2 and min(volume(s)[0] for s in solids)>20.,[(volume(s)[0],s.BoundingBox().xlen) for s in solids]
    # Explicit two-piece revision: battery/RF saddle and separate sensor seat.
    # Both are exported and printed; no disconnected component is discarded.
    solids[1]=solids[1].cut(box(60.,100.,20.,(0.,60.,24.2)))
    return [check(s,'CARRIER_COMPONENT') for s in solids]
def module_hardware():
    hw={}
    # Explicit nominal fastener envelopes. A selected M2x6 button screw,
    # 0.3 washer and 1.2-thin nut must be measured before purchasing/assembly.
    for idx,(x,y) in enumerate([(-27.331,43.),(-28.604,66.)],1):
        hw[f'ADAPTER_M2x6_BUTTON_SCREW_{idx}_EST']=join(cylinder(1.,6.,(x,y,6.65)),cylinder(1.9,1.1,(x,y,12.65)))
        hw[f'ADAPTER_TOP_WASHER_{idx}_EST']=cylinder(2.1,.3,(x,y,12.35)).cut(cylinder(1.05,1.,(x,y,12.)))
        hw[f'ADAPTER_LOWER_WASHER_{idx}_EST']=cylinder(2.1,.3,(x,y,7.95)).cut(cylinder(1.05,1.,(x,y,7.6)))
        nut=cq.Workplane('XY').polygon(6,4./math.cos(math.pi/6)).extrude(1.2).val().translate((x,y,6.75)).cut(cylinder(1.05,2.,(x,y,6.4)))
        hw[f'ADAPTER_THIN_NUT_{idx}_EST']=check(nut,'NUT')
    return hw
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    common,route=sys.argv[1:3];assert route in ['H','D'];gate=json.loads((ROOT/f'reports/l2_revision/{common}/common_gate.json').read_text())
    assert gate['digital_geometry_reviewed'] and gate['numerical_reviewed'],'Common-shell gate not satisfied'
    variant='L2_'+route+'_EST';out=ROOT/f'exports/l2_revision/{variant}';rp=ROOT/f'reports/l2_revision/{variant}';rp.mkdir(parents=True,exist_ok=True)
    src=ROOT/f'exports/l2_revision/{common}'
    for folder in ['assembly','print','gauges']:shutil.copytree(src/folder,out/folder,dirs_exist_ok=True)
    met=json.loads((ROOT/f'reports/l2_revision/{common}/cad_metrics.json').read_text());d=json.loads((ROOT/f'reports/l2_revision/{common}/design_metadata.json').read_text())
    exporter.OUT=out;exporter.REPORT=rp;exporter.CACHE=ROOT.parent/f'_support/work/l2/{variant}/build';exporter.CACHE.mkdir(parents=True,exist_ok=True)
    for n,s in zip([route+'_REMOVABLE_CARRIER_EST',route+'_SENSOR_SEAT_EST'],carrier(route)):exporter.export(n,s,True,met)
    # R0's colliding M2 stack is retained in its history folder; new carrier
    # uses measured removable insulating straps instead of those screws.
    # Source outlines inform this sensor-board envelope only. Optical axis,
    # mounting stack and actual component keep-outs remain unverified.
    old=json.loads((ROOT/'cad/rebuild_r3_2/electronics.json').read_text());envelopes=[]
    exclude=['POWER_SWITCH_BODY_EST','POWER_SWITCH_TAB_EST','POWER_SWITCH_PCB_EST']
    for row in old['custom']:
        if row['name'] in exclude:continue
        row=copy.deepcopy(row);n=row['name']
        if n=='SENSOR_PCB_EST':row.update(size=[18.,18.,1.6],center=[3.4,66.,15.],basis='NEW CUSTOM PCB REQUIREMENT, not a purchased board. The actual referenced15.45x28 breakout gauge failed unchanged-body clearance; see L2_H_REFERENCE_BOARD_BLOCKED. A compact18x18 circuit requires electrical redesign or a verified supplier; no existing product is claimed.')
        if n=='PAW3950_PACKAGE_EST':row['center']=[0.,64.,13.]
        if n=='MATCHED_LENS_EST':row['center']=[0.,64.,9.8]
        if n=='SENSOR_HEADER_EST':row['center']=[13.5,75.,16.55]
        if n=='BATTERY_PLUG_EST':row['center']=[-18.,59.,21.5]
        if n=='SIDE_IO_PCB_EST':row.update(center=[13.2,57.5,15.5],size=[1.,30.,4.])
        if n=='SIDE_HEADER_EST':row['center']=[11.2,46.,16.9]
        if route=='D' and n in ['SENSOR_PCB_EST','CONTROLLER_RF_PCB_EST','MCU_RADIO_EST','CHARGE_POWERPATH_EST','REGULATOR_EST','RF_BAT_HEADER_EST','RF_IO_HEADER_EST','RF_SENSOR_HEADER_EST','SENSOR_HEADER_EST','RF_USB_HEADER_EST','ANTENNA_FEED_HEADER_EST']:continue
        s=box(*row['size'],row['center'])
        if n=='SIDE_IO_PCB_EST':
            for cy in [49.,62.]:
                for dy in [-5.08,0,5.08]:s=s.cut(box(3.,2.,1.2,(13.2,cy+2+dy,15.5)))
        if route=='D' and n in ['PAW3950_PACKAGE_EST','MATCHED_LENS_EST']:
            n={'PAW3950_PACKAGE_EST':'D_SENSOR_PACKAGE_UNVERIFIED','MATCHED_LENS_EST':'D_LENS_UNVERIFIED'}[n];row['name']=n
            row['basis']='Generic package/optical placeholder; donor sensor identity and lens are unverified, not assumed PAW3950.'
        exporter.export(n,check(s,n),False,met);envelopes.append(row)
    if route=='D':
        row=dict(name='D_BOARD_SWEEP_GAUGE_UNVERIFIED',kind='pcb',size=[36.,50.,1.2],center=[0.,58.,14.6],basis='Independent rectangular clearance gauge, NOT ATK A1 Pro dimensions, outline, holes, component locations or renamed A1 Plus geometry.')
        exporter.export(row['name'],box(*row['size'],row['center']),False,met);envelopes.append(row)
    reserves=copy.deepcopy(old['reserves']);next(q for q in reserves if q['name']=='OPTICAL_PATH_EST')['center']=[0.,64.,1.8]
    for row in reserves:
        s=box(*row['size'],row['center']);dest=out/'reserves';dest.mkdir(exist_ok=True);cq.exporters.export(s,str(dest/(row['name']+'.step')));s.exportStl(str(dest/(row['name']+'.stl')),tolerance=.03,relative=False)
    routes=[]
    if route=='H':
        for row in old['routes']:
            row=copy.deepcopy(row)
            if row['name']=='BATTERY_ROUTE_EST':row['points']=[[-15.5,59.,21.5],[-11.5,59.,21.5],[-7.5,61.5,21.4],[-4.7,61.5,21.4]]
            if row['name']=='SIDE_ROUTE_EST':row['points']=[[9.7,46.,16.9],[8.5,46.,16.9],[8.5,53.6,16.9],[11.,53.6,20.3],[11.,55.,20.3]]
            if row['name']=='SENSOR_ROUTE_EST':row['points']=[[9.5,71.,20.3],[14.8,71.,20.3],[16.3,75.,20.3],[16.3,75.,16.55],[15.,75.,16.55]]
            s=join(*[beam(a,b,row['radius']) for a,b in zip(row['points'][:-1],row['points'][1:])]);exporter.export(row['name'],check(s,row['name']),False,met);routes.append(row)
    d['parameters']['version']=variant;d['common_source']=common;d['electronics_status']='ESTIMATED_LAYOUT_ONLY' if route=='H' else 'DONOR_ID_UNVERIFIED;PCB_GEOMETRY_UNVERIFIED;FIT_NOT_CERTIFIED'
    d['electronics']=dict(envelopes=envelopes,reserves=reserves,routes=routes,donor_id='ATK A1 Pro' if route=='D' else None,
        no_external_DPI_button=True,no_added_external_power_slider=True,required_power_control='Must be provided by the selected controller/donor without removing protection or charging control.',
        battery=dict(size_mm=[18,22,6],capacity_mAh=None,minimum_runtime_h=12,usable_fraction_assumption=.75,max_current_for_300_400_500_mAh=[18.75,25.,31.25],measured_current_mA=None),
        optics=dict(estimated_axis_origin=[0,64,9.8],axis_direction=[0,0,-1],foot_plane_mm=5.2,example_skate_mm=.5,estimated_lens_bottom_mm=7.8,example_gap_mm=3.1,working_distance_verified=False),
        firmware_targets=['400-6400 DPI','2.4 GHz 1000 Hz','five buttons and wheel','macros','LOD adjustment','no optional sync','low latency','charging','>=12 h continuous full-power target'],function_verified=False,
        retention='R0 generic ear screw path was blocked by the inherited ear arm. Revised saddle uses removable insulating ties around retained lower ribs. PCB edge clips and battery strap require measured keep-outs. No glue/cell compression; no selected supplier or certified retention. Any failed carrier insertion is explicitly retained as a blocker.')
    for n,j in [('cad_metrics',met),('design_metadata',d),('source_parameters',dict(common=common,route=route,unverified=True)),('electronic_envelopes',dict(physical=envelopes,reserves=reserves))]:
        (rp/f'{n}.json').write_text(json.dumps(j,indent=2)+'\n')
    print(variant,'built for independent clearance review, not fit accepted',flush=True)
if __name__=='__main__':main()
