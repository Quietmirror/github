"""Independent L2 Gate 1 arithmetic and delivered CAD/mesh audit (mm, N, MPa)."""
from pathlib import Path
import ctypes,json,math,sys,time
import numpy as np
import cadquery as cq
import trimesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/l2_revision'; OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build as source

def volume(shape):
    props=GProp_GProps()
    error=BRepGProp.VolumeProperties_s(shape.wrapped,props,1e-7,False,False)
    return props.Mass(),error

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    started=time.time(); rows=[]
    old=json.loads((ROOT/'reports/rebuild_r3_2/thickness_volume_audit.json').read_text())
    reference={r['part']:r['adaptive_cad_volume_mm3'] for r in old['parts']}
    for path in sorted((ROOT/'exports/rebuild_r3_2/print').glob('*.stl')):
        name=path.stem
        shape=cq.importers.importStep(str(ROOT/f'exports/rebuild_r3_2/assembly/{name}.step')).val()
        v,error=volume(shape); mesh=trimesh.load_mesh(path)
        row=dict(part=name,valid_brep=shape.isValid(),solids=len(shape.Solids()),cad_volume_mm3=v,
                 integrator_error=error,mesh_volume_mm3=mesh.volume,mesh_watertight=mesh.is_watertight,
                 mesh_components=len(mesh.split(only_watertight=False)),PA12_g=v*.00101,PLA_solid_g=v*.00124,
                 difference_from_R32_report_mm3=v-reference[name])
        rows.append(row); print(name,round(v,6),flush=True)
    total=sum(r['cad_volume_mm3'] for r in rows)
    budgets={k:dict(target_g=w,target_mm3=w/1.01*1000,remove_g=total*.00101-w,
                        remove_mm3=total-w/1.01*1000,remove_percent=(1-w/(total*.00101))*100)
             for k,w in [('L1',16.49),('L2',14.89),('L3',12.59)]}
    beams=[]
    for t in [1.5,1.6,1.7,1.8,2.0]:
        I=3*t**3/12;stress=3*3*18/(2*3*t*t);u=3*18**3/(4*1700*3*t**3)
        beams.append(dict(thickness_mm=t,I_mm4=I,stress_MPa=stress,deflection_mm=u,
                          mass_ratio=t/1.8,EI_ratio=(t/1.8)**3))
    segments=[((-23.22,12,6.5),(0,46,6.5),2.6),((23.22,12,6.5),(0,46,6.5),2.6),
              ((-24.84,62.64,6.5),(0,46,6.5),2.6),((24.84,62.64,6.5),(0,46,6.5),2.6)]
    bars=[dict(length_mm=float(np.linalg.norm(np.array(a)-b)),diameter_mm=d) for a,b,d in segments]
    bars.extend(dict(length_mm=l,diameter_mm=d) for l,d in [(54.0903,2.4),(51.9717,2.4),(58.3053,2.6)])
    gross=sum(math.pi*r['diameter_mm']**2/4*r['length_mm'] for r in bars)
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text())
    sharp=[]; rounded=[]; holes=[]
    for name,points,tool in source.window_layout(p):
        poly=Polygon(points); smooth=poly.buffer(-.85,quad_segs=48).buffer(.85,quad_segs=48)
        sharp.append(poly);rounded.append(smooth)
        holes.append(dict(name=name,xy=points,sharp_area_mm2=poly.area,rounded_R085_area_mm2=smooth.area,
                          note='2D rounded contour before 3D contact-band masks; not final shell opening volume'))
    result=dict(version='L2 Gate 1',status='BASELINE_AND_ARITHMETIC_AUDITED',baseline_commit='f1b1090931d717117287ea2b79c2e14ddc234937',
                units='mm N MPa g',parts=rows,total_CAD_mm3=total,total_PA12_g=total*.00101,total_PLA_solid_g=total*.00124,
                budgets=budgets,beam_example=beams,skeleton_gross=dict(bars=bars,volume_mm3=gross,PA12_g=gross*.00101,
                limitation='Gross ideal cylinders; junction and skin overlap NOT removed. Not net removable material.'),
                planar_proxy=dict(holes=holes,sharp_union_mm2=unary_union(sharp).area,
                R085_union_mm2=unary_union(rounded).area,claimed_hole_union_mm2=1301.27,
                claimed_panel_mass_recomputed_g=(2542-1301.27)*1.8*.00101,
                historical_fem_status='NOT_REPRODUCIBLE_AS_SPECIFIED: exact boundary nodes, panel origin, load distribution, discretisation and P1 equal-area algorithm were not supplied. Reconstruct transparently; do not claim matching old stress/stiffness.'),
                elapsed_s=time.time()-started,
                limits=['No measured PA12 process or PLA batch properties.','No actual A1 Pro board or optical dimensions.',
                        'Volume and closed mesh do not establish strength, fatigue or physical fit.'])
    (OUT/'baseline_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    lines=['# L2 基准与计算复核','', '当前读取 R3.2 的实际 STEP 和 STL，未把任务书数值当作新验证结果。','',
           '|零件|CAD 体积 mm³|PA12 理论 g|PLA 实心理论 g|','|---|---:|---:|---:|']
    lines.extend(f"|{r['part']}|{r['cad_volume_mm3']:.6f}|{r['PA12_g']:.6f}|{r['PLA_solid_g']:.6f}|" for r in rows)
    lines+=['',f'总计 {total:.6f} mm³，PA12 假设密度 1.01 下 {total*.00101:.6f} g；PLA 假设密度 1.24 下 {total*.00124:.6f} g。均非含支撑的切片用量。',
            f"L2 目标需净减少 {budgets['L2']['remove_mm3']:.3f} mm³ / {budgets['L2']['remove_g']:.6f} g ({budgets['L2']['remove_percent']:.2f}%)。",'',
            f'七根理想圆柱梁毛体积 {gross:.3f} mm³，未扣交叠，不是可删除净体积。','',
            '历史二维模拟缺少完整边界与网格定义，无法按任务书唯一复现。旧 6.6%/10.3% 刚度改善仅保留为待复核先导，不作 L2 强度证据。',
            f'原 CAD 孔轮廓已有 R0.85 圆角；按源多边形复算尖角联合面积 {unary_union(sharp).area:.3f} mm²，二维 R0.85 内圆角后 {unary_union(rounded).area:.3f} mm²。须与任务书的 1301.27 mm² 区别。',
            '', '实际打印前还需公差小样、按键偏心/回弹、疲劳和真实硬件测量。']
    (OUT/'calculation_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print('BASELINE',total,total*.00101,'L2 removal',budgets['L2'],flush=True)

if __name__=='__main__':main()
