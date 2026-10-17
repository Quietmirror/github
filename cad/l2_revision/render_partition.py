"""Render the actual mutually exclusive mass-accounting CAD partitions."""
from pathlib import Path
import importlib.util, json, shutil
import cadquery as cq
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]

def main():
    spec = importlib.util.spec_from_file_location('renderer', ROOT/'cad/rebuild_r3_2/render.py')
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    r.MESH = ROOT.parent/'_support/work/l2/partition_render_meshes'
    r.MESH.mkdir(parents=True, exist_ok=True)
    r.OUT = ROOT/'views/l2_revision/studies'
    ledger = json.loads((ROOT/'reports/l2_revision/partition_v2_F1H/volume_ledger.json').read_text())
    rows = {q['category']: q for q in ledger['parts']}
    for name in ['A_BODY_SKIN', 'B_BODY_SKELETON', 'C_BODY_MOUNTS']:
        shape = cq.importers.importStep(str(ROOT/f'exports/l2_revision/partitions_v2/F1H/{name}.step')).val()
        shape.exportStl(str(r.MESH/(name+'.stl')), tolerance=.035, relative=False)
    groups = [
        ('A', ['A_BODY_SKIN'], '外层表皮', (.20,.48,.55), rows['A_BODY_SKIN']['PA12_g']),
        ('B', ['B_BODY_SKELETON'], '中央承力骨架 + 五脚平台', (.39,.60,.37), rows['B_BODY_SKELETON']['PA12_g']),
        ('C', ['C_BODY_MOUNTS', 'SIDE_FRONT_KEY_SWITCH_CLAMP', 'SIDE_REAR_KEY_SWITCH_CLAMP', 'WHEEL_CARRIER'],
         '内部安装结构 + 独立夹具/滚轮载架', (.84,.55,.20), rows['C_BODY_MOUNTS']['PA12_g']+rows['C_SEPARATE_MOUNTS']['PA12_g']),
        ('D', ['LEFT_KEY', 'RIGHT_KEY', 'SIDE_FRONT_KEY', 'SIDE_REAR_KEY', 'WHEEL'],
         '活动触感件与滚轮', (.55,.42,.68), rows['D_MOVING_OTHER']['PA12_g']),
    ]
    panels = []
    for group, names, label, color, mass in groups:
        for name in names:
            r.COLORS[name] = color
            if not (r.MESH/(name+'.stl')).exists():
                shutil.copyfile(ROOT/f'exports/l2_revision/F1H/assembly/{name}.stl', r.MESH/(name+'.stl'))
        file = 'partition_'+group+'.png'
        r.render(file, names, (125,-95,125), title=f'{group} / {label} / PA12 {mass:.3f} g',
                 note='实际互斥 CAD 统计分区 / 同相机同尺度 / 不含任何电子件或金属件',
                 footer='统计切分不是可拆零件；仅最终完整打印件用于切片。PA12 密度假设 1.01 g/cm³。')
        panels.append(r.OUT/file)
    out = Image.new('RGB', (1800,1440), '#f8fafb')
    for i, p in enumerate(panels):
        im = Image.open(p).convert('RGB').resize((900,720))
        out.paste(im, ((i%2)*900,(i//2)*720))
    out.save(r.OUT/'A_B_C_D_EXPLAINED.png', optimize=True)
    print('Actual native partition figure generated', flush=True)

if __name__ == '__main__':
    main()
