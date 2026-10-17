"""Actual single-bed slice from a self-contained 3MF, with extrusion ledger."""
from pathlib import Path
import sys,ctypes,json,subprocess,zipfile,re,math,hashlib
import trimesh,numpy as np
ROOT=Path(__file__).resolve().parents[2];SUP=ROOT.parent/'_support'
SL=SUP/'tools/PrusaSlicer/PrusaSlicer-2.9.6/prusa-slicer-console.exe'
def analyze(path):
    current={k:0. for k in 'XYZE'};relative=True;role='Unclassified';amount={};segments={};bounds=np.array([[np.inf]*3,[-np.inf]*3]);footer={};layers=set();object_counts={};obj='unlabelled';small=[]
    for line in path.read_text(encoding='utf8').splitlines():
        if line.startswith(';TYPE:'):role=line[6:].strip()
        if line.startswith('; printing object '):obj=line[18:].strip()
        if line.startswith('; ') and ' = ' in line:
            k,v=line[2:].split(' = ',1);footer[k]=v
        code=line.split(';',1)[0].strip()
        if code=='M83':relative=True
        elif code=='M82':relative=False
        elif code.startswith('G92'):
            for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code):current[k]=float(v)
        elif re.match(r'^G[01](?: |$)',code):
            a=current.copy();vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)}
            de=vals.get('E',0.) if relative else vals.get('E',current['E'])-current['E']
            for k in 'XYZ':
                if k in vals:current[k]=vals[k]
            if 'E' in vals:current['E']=current['E']+de if relative else vals['E']
            length=math.hypot(current['X']-a['X'],current['Y']-a['Y'])
            if de>0 and length>1e-7:
                amount[role]=amount.get(role,0.)+de;segments[role]=segments.get(role,0)+1;layers.add(round(current['Z'],4))
                for pt in [a,current]:
                    xyz=np.array([pt[k] for k in 'XYZ']);bounds[0]=np.minimum(bounds[0],xyz);bounds[1]=np.maximum(bounds[1],xyz)
                object_counts[obj]=object_counts.get(obj,0)+1
                if length<.15 and len(small)<100:small.append(dict(role=role,xy_mm=[current['X'],current['Y']],z_mm=current['Z'],length_mm=length))
    grams={k:v*math.pi*(1.75/2)**2*1.24/1000 for k,v in amount.items()}
    support=sum(v for k,v in grams.items() if 'Support' in k);brim=sum(v for k,v in grams.items() if 'Skirt' in k or 'Brim' in k)
    total=sum(grams.values());net=total-support-brim
    reported=float(footer['filament used [g]'].split(',')[0]);bed_ok=bool(np.all(bounds[0,:2]>=0) and np.all(bounds[1,:2]<=[250,210]))
    return dict(roles_grams=grams,extrusion_segments_by_role=segments,net_parts_PLA_g=net,support_PLA_g=support,brim_PLA_g=brim,
        positive_XY_extrusion_PLA_g=total,slicer_total_PLA_g=reported,accounting_difference_g=total-reported,
        extrusion_centerline_bounds_mm=bounds.tolist(),extrusion_plus_half_width_inside_bed=bed_ok and bool(np.all(bounds[0,:2]>=.3) and np.all(bounds[1,:2]<=[249.7,209.7])),
        layers=len(layers),labelled_object_segments=object_counts,short_path_samples=small,estimated_time=footer.get('estimated printing time (normal mode)'),
        profile={k:footer.get(k) for k in ['bed_shape','nozzle_diameter','layer_height','perimeters','fill_density','filament_density','support_material','support_material_buildplate_only','temperature','bed_temperature']},
        accounting='Sum positive extrusion on XY-moving toolpath segments by slicer TYPE; retract/unretract-only E moves excluded. Footer rounded separately. Net parts excludes support and brim; no printer calibration claim.')
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    v=sys.argv[1];base=ROOT/f'exports/l2_revision/{v}';rp=ROOT/f'reports/l2_revision/{v}';work=SUP/f'work/l2/{v}/slice';work.mkdir(parents=True,exist_ok=True)
    if '--analyze-only' in sys.argv:
        result=json.loads((rp/'slice_summary.json').read_text());result.update(analyze(work/(v+'_validation_only.gcode')))
        result['pass_check']=result['extrusion_plus_half_width_inside_bed'] and abs(result['accounting_difference_g'])<.15 and result['profile']['bed_shape']=='0x0,250x0,250x210,0x210'
        (rp/'slice_summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print(v,'recount',result['pass_check'],result['net_parts_PLA_g'],result['support_PLA_g'],result['brim_PLA_g'],result['slicer_total_PLA_g'],flush=True);return
    met=json.loads((rp/'cad_metrics.json').read_text());names=[n for n,m in met.items() if m['printable']]
    profile=(ROOT/'slicing/V0.6_PLA_0.4_0.20_ESTIMATE.ini').read_text().replace('220x0,220x220,0x220','250x0,250x210,0x210').replace('support_material_buildplate_only = 1','support_material_buildplate_only = 0').replace('V0.5 generic',v+' generic').replace('220mm ESTIMATE','250x210mm ESTIMATE')
    profile+='\ngcode_label_objects = octoprint\n';ini=work/'profile.ini';ini.write_text(profile,encoding='utf8',newline='\n')
    def run(args,name):
        with (work/(name+'.log')).open('w',encoding='utf8') as f:subprocess.run([str(SL),'--sw-renderer','--datadir',str(SUP/'config/PrusaSlicer'),'--threads','2',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,timeout=1200,check=True)
    pieces=[(n,trimesh.load_mesh(base/f'print/{n}.stl')) for n in names];pieces.sort(key=lambda q:np.prod(q[1].extents[:2]),reverse=True)
    placed=[];scene=trimesh.Scene()
    for n,original in pieces:
        choices=[]
        for deg in [0,90]:
            m=original.copy();mat=trimesh.transformations.rotation_matrix(math.radians(deg),[0,0,1]);m.apply_transform(mat);w,h=m.extents[:2]
            xs=sorted(set([8.]+[q['bounds'][1][0]+12 for q in placed]));ys=sorted(set([8.]+[q['bounds'][1][1]+12 for q in placed]))
            for y in ys:
                for x in xs:
                    if x+w>242 or y+h>202:continue
                    if any(x<q['bounds'][1][0]+12-1e-5 and x+w+12>q['bounds'][0][0]+1e-5 and y<q['bounds'][1][1]+12-1e-5 and y+h+12>q['bounds'][0][1]+1e-5 for q in placed):continue
                    choices.append((y+h,x+w,deg,x,y,m,mat))
        if not choices:raise RuntimeError(f'{n}: all parts do not fit the assumed 250 x 210 bed')
        _,_,deg,x,y,m,mat=min(choices,key=lambda q:q[:4]);shift=[x-m.bounds[0,0],y-m.bounds[0,1],-m.bounds[0,2]];m.apply_translation(shift)
        mat[:3,3]=shift;scene.add_geometry(m,node_name=n,geom_name=n)
        placed.append(dict(part=n,bounds=m.bounds.tolist(),additional_rotation_z_deg=deg,print_to_plate_matrix=mat.tolist()))
    scene.units='mm';raw=work/'raw.3mf';raw.write_bytes(trimesh.exchange.threemf.export_3MF(scene))
    plate=base/(v+'_ALL_PARTS_SINGLE_PLATE.3mf');run(['--load',ini,'--dont-arrange','--export-3mf','--output',plate,raw],'export')
    full=work/'full.ini';run(['--load',ini,'--save',full],'full_profile')
    with zipfile.ZipFile(plate) as z:files={n:z.read(n) for n in z.namelist()}
    files['Metadata/Slic3r_PE.config']=('; generic PLA validation only\n'+''.join('; '+s+'\n' for s in full.read_text(encoding='utf8').splitlines() if ' = ' in s and not s.startswith('#'))).encode('utf8')
    with zipfile.ZipFile(plate,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in files.items():z.writestr(n,b)
    gcode=work/(v+'_validation_only.gcode');run(['--dont-arrange','--export-gcode','--output',gcode,plate],'slice_embedded_profile');run(['--info',plate],'model_info')
    result=analyze(gcode);result.update(variant=v,plate=str(plate.relative_to(ROOT)),slicer='PrusaSlicer 2.9.6',placements=placed,objects=len(placed),assumed_bed_mm=[250,210],printer_model_confirmed=False,
        independently_sliced_without_load_flag=True,plate_sha256=hashlib.sha256(plate.read_bytes()).hexdigest(),scope='Actual separated-parts slice with embedded profile. Requires actual printer profile and tolerance test coupons before printing; not printer-ready G-code.')
    result['pass_check']=result['extrusion_plus_half_width_inside_bed'] and abs(result['accounting_difference_g'])<.15 and result['profile']['bed_shape']=='0x0,250x0,250x210,0x210'
    (rp/'slice_summary.json').write_text(json.dumps(result,indent=2)+'\n');(rp/'slicer_model_info.txt').write_text((work/'model_info.log').read_text(encoding='utf8'))
    print(v,'slice',result['pass_check'],result['objects'],result['net_parts_PLA_g'],result['support_PLA_g'],result['brim_PLA_g'],result['slicer_total_PLA_g'],result['estimated_time'],flush=True)
if __name__=='__main__':main()
