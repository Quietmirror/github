"""Actual CAD-mesh review views, no generated concept images."""
from pathlib import Path
import sys,json,importlib.util
ROOT=Path(__file__).resolve().parents[2]
def main():
    v=sys.argv[1];spec=importlib.util.spec_from_file_location('renderer',ROOT/'cad/rebuild_r3_2/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    r.OUT=ROOT/f'views/l2_revision/{v}';r.OUT.mkdir(parents=True,exist_ok=True);r.MESH=ROOT/f'exports/l2_revision/{v}/assembly'
    met=json.loads((ROOT/f'reports/l2_revision/{v}/cad_metrics.json').read_text());names=list(met)
    base=v+' / L2 研究候选';footer='实际 CAD / mm / 灰色与铜色为独立硬件参考；不是已确认的供体装配或实物测试'
    views=[('top',(0,40,230),(0,-1,0)),('bottom',(0,40,-230),(0,-1,0)),('left',(230,40,17),(0,0,1)),('right',(-230,40,17),(0,0,1)),('front',(0,-230,17),(0,0,1)),('rear',(0,230,17),(0,0,1)),('left_front',(125,-95,125),(0,0,1)),('right_front',(-125,-95,125),(0,0,1)),('left_rear',(125,165,125),(0,0,1)),('right_rear',(-125,165,125),(0,0,1))]
    for name,cam,up in views:r.render(name+'.png',names,cam,up=up,title=base+' / '+name,note='新侧键与内部导轨、微动座一起前移；短脚贴与主键触感面保留',footer=footer)
    r.render('side_detail.png',names,(230,56,24),scale=22,focus=(26,56,16),title=base+' / 双侧键细节',note='F1：10.4 × 3.6 mm 触感面；中心 Y49 / 62；可见间隔 2.6 mm',footer=footer)
    r.render('internal.png',[n for n in names if n not in ['LEFT_KEY','RIGHT_KEY']],(125,-95,125),transparent_body=True,title=base+' / 内部机械结构',note='透明主壳只用于观察；实际打印 BODY 是一个连通实体',footer=footer)
    r.render('exploded.png',names,(125,-95,125),scale=63,explode=True,labels=True,title=base+' / 独立零件爆炸示意',note='分件保持独立；爆炸方向用于识别，不代表实际装入路径',footer=footer)
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGB',(1800,1440),'white')
    for i,name in enumerate(['top','left','bottom','left_front']):
        q=Image.open(r.OUT/(name+'.png'));q.thumbnail((900,720));im.paste(q,((i%2)*900,(i//2)*720))
    im.save(r.OUT/'FOUR_VIEWS.png')
    print('Rendered',v,13,'actual mesh views',flush=True)
if __name__=='__main__':main()
