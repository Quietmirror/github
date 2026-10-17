"""Same-scale views of actual generated candidates and recorded failures."""
from pathlib import Path
import sys,json,importlib.util,cadquery as cq
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
def main():
    spec=importlib.util.spec_from_file_location('renderer',ROOT/'cad/rebuild_r3_2/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    r.OUT=ROOT/'views/l2_revision/studies';r.OUT.mkdir(parents=True,exist_ok=True)
    def panel(v,label,category,view='top'):
        r.MESH=ROOT/('exports/rebuild_r3_2/assembly' if v=='R32' else f'exports/l2_revision/{v}/assembly')
        rp=ROOT/f'reports/l2_revision/{v}';screen=json.loads((rp/'geometry_screen.json').read_text()) if (rp/'geometry_screen.json').exists() else {}
        note='单变量实际 CAD；未通过模型不能用于打印' if not screen.get('geometry_screen_pass',True) else '单变量实际 CAD；几何有效不等于全部工况通过'
        cam=(0,40,230) if view=='top' else (125,-95,125)
        r.render(category+'_'+v+'.png',['BODY'],cam,up=(0,-1,0) if view=='top' else (0,0,1),title=label,note=note,footer='同一尺度 / mm / 保留原机制用于单变量对比；未选择候选不视为正式轻量化版')
        return r.OUT/(category+'_'+v+'.png')
    def montage(paths,file,cols=3):
        out=Image.new('RGB',(cols*750,((len(paths)+cols-1)//cols)*600),'#f8fafb')
        for i,p in enumerate(paths):
            q=Image.open(p).resize((750,600));out.paste(q,((i%cols)*750,(i//cols)*600))
        out.save(r.OUT/file,optimize=True)
    p=[]
    for v,label in [('R32','P0 / 原始六孔'),('P1_R13','P1 / 六孔等面积圆角 R1.3'),('P2','P2 / 保留保护带的分孔'),('P3','P3 / 局部蜂巢：面积不可匹配、网格失败'),('P4','P4 / 大圆角：原 STL 未闭合'),('P5','P5 / 受保护区约束的椭圆'),('P6','P6 / 分区圆角：未完成应力驱动拓扑')]:p.append(panel(v,label,'topology'))
    montage(p,'P0_P1_P2_P3_P4_P5_P6.png')
    p=[panel(v,label,'skeleton','iso') for v,label in [('R32','B0 / 原始骨架'),('B1','B1 / 上横梁局部减径'),('B2','B2 / 定向椭圆：体网格失败'),('B4','B4 / 椭圆核心与局部节点')]]
    diagnostic=ROOT/'exports/l2_revision/failed_construction/B3';tmp=ROOT.parent/'_support/work/l2/render_b3';tmp.mkdir(parents=True,exist_ok=True)
    s=cq.importers.importStep(str(diagnostic/'support_24_after.step')).val();s.exportStl(str(tmp/'B3_failed.stl'),tolerance=.03,relative=False)
    r.MESH=tmp;r.render('skeleton_B3.png',['B3_failed'],(90,-20,90),scale=35,focus=(0,56,23),title='B3 / 工具避空把三角撑切成两个实体',note='仅显示实际失败支撑；没有伪造完整连通 BODY',footer='失败几何保留，未丢弃小实体或用网格补洞')
    p.insert(3,r.OUT/'skeleton_B3.png');montage(p,'B0_B1_B2_B3_B4.png')
    paths=[]
    for v in ['F1G','F2E']:
        r.MESH=ROOT/f'exports/l2_revision/{v}/assembly';met=json.loads((ROOT/f'reports/l2_revision/{v}/cad_metrics.json').read_text());names=['BODY']+[n for n in met if n.startswith('SIDE_') or n.startswith('SWITCH_SIDE_')]
        r.render(v+'_side.png',names,(230,56,24),scale=22,focus=(26,56,16),title=v+' / 侧键与完整内部机构',note='F1：低突出；F2：略高触感面与 3° 轮廓倾斜；都为独立键',transparent_body=True,footer='实际 CAD；触达、摩擦、打印公差与回弹仍需物理试装')
        paths.append(r.OUT/(v+'_side.png'))
    montage(paths,'F1_F2_INTERNAL_COMPARISON.png',2)
    print('Actual study comparison renders saved',flush=True)
if __name__=='__main__':main()
