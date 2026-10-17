"""Orthographic/isometric/cutaway/plate views from the actual exported meshes."""
from pathlib import Path
import sys,json,importlib.util,inspect,shutil
ROOT=Path(__file__).resolve().parents[2]
def main():
 v=sys.argv[1];rp=ROOT/f'reports/l2_revision/{v}';base=ROOT/f'exports/l2_revision/{v}'
 spec=importlib.util.spec_from_file_location('rr',ROOT/'cad/rebuild_r3_2/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 r.OUT=ROOT/f'views/l2_revision/{v}';r.OUT.mkdir(parents=True,exist_ok=True);r.MESH=base/'assembly'
 met=json.loads((rp/'cad_metrics.json').read_text());d=json.loads((rp/'design_metadata.json').read_text());names=list(met)
 palette={'pcb':(.12,.53,.37),'sensor':(.21,.26,.31),'lens':(.52,.31,.68),'battery':(.34,.52,.79),'chip':(.25,.27,.31),'antenna':(.93,.69,.22),'connector':(.8,.61,.3)}
 for row in d.get('electronics',{}).get('envelopes',[]):r.COLORS[row['name']]=palette.get(row['kind'],(.6,.6,.6))
 for n in names:
  if 'CARRIER_EST' in n:r.COLORS[n]=(.71,.44,.19)
  if 'ROUTE_EST' in n:r.COLORS[n]=(.92,.42,.1)
  if 'GAUGE_UNVERIFIED' in n:r.COLORS[n]=(.84,.13,.13)
  if n.startswith('ADAPTER_'):r.COLORS[n]=(.62,.67,.7)
 donor=v=='L2_D_EST';title=v+' / '+('PCB PLACEHOLDER / 未核实尺寸' if donor else '需定制18×18传感器板 / 估计包络')
 footer='真实 CAD · mm · 不代表已选实物适配、点击/疲劳、无线或续航验证'
 note='绿色板卡 / 蓝色电池 / 紫色镜头 / 橙色线束 / 铜色可拆托架；均保留原机械件'
 views=[('top',(0,40,230),(0,-1,0)),('bottom',(0,40,-230),(0,-1,0)),('left',(230,40,17),(0,0,1)),('right',(-230,40,17),(0,0,1)),('front',(0,-230,17),(0,0,1)),('rear',(0,230,17),(0,0,1)),('left_front',(125,-95,125),(0,0,1)),('right_front',(-125,-95,125),(0,0,1)),('left_rear',(125,165,125),(0,0,1)),('right_rear',(-125,165,125),(0,0,1))]
 for name,cam,up in views:r.render(name+'.png',names,cam,up=up,title=title+' / '+name,note=note,footer=footer)
 internals=[n for n in names if n not in ['LEFT_KEY','RIGHT_KEY']]
 r.render('internal.png',internals,(125,-95,125),transparent_body=True,title=title+' / 内部',note=note,footer=footer)
 r.render('internal_top.png',internals,(0,44,230),up=(0,-1,0),transparent_body=True,title=title+' / 内部俯视',note=note,footer=footer)
 positions=r.render('exploded.png',names,(125,-95,125),scale=70,explode=True,labels=True,title=title+' / 爆炸图',note='爆炸位移仅用于分件识别，不是装入路径；编号清单见 EXPLODED_LABELS.json',footer=footer)
 (rp/'EXPLODED_LABELS.json').write_text(json.dumps([dict(id=i+1,part=n) for i,(n,x,y) in enumerate(positions)],indent=2)+'\n')
 source=inspect.getsource(r.render).replace('plane.SetOrigin(0,0,5);plane.SetNormal(0,0,1)','plane.SetOrigin(*SECTION_ORIGIN);plane.SetNormal(*SECTION_NORMAL)')
 exec(compile(source,'real_mesh_section','exec'),r.__dict__)
 sections=[('section_side',(28.4,0,0),(1,0,0),(230,56,16),(28,56,15.5),23,'X28.4 剖切：双侧键、导向与微动'),('section_main',(18.3,0,0),(1,0,0),(230,26,20),(18.3,28,17),25,'X18.3 剖切：主键轴、触点和止挡'),('section_wheel',(0,0,0),(1,0,0),(230,30,20),(0,30,17),22,'X0 剖切：滚轮、载架、中键'),('section_optics',(0,0,0),(1,0,0),(230,61,14),(0,61,12),20,'X0 剖切：镜头底 Z7.8 / 脚贴面 Z5.2 / 示例垫面 Z4.7'),('section_battery',(-17,0,0),(-1,0,0),(-230,57,20),(-17,57,17),23,'X-17 剖切：电池、可拆托架；容量与固定细节待测')]
 for name,origin,normal,cam,focus,scale,desc in sections:
  r.SECTION_ORIGIN=origin;r.SECTION_NORMAL=normal;r.render(name+'.png',names,cam,focus=focus,scale=scale,lowclip=True,title=title,note=desc,footer=footer)
 from PIL import Image,ImageDraw,ImageFont
 sheet=Image.new('RGB',(1800,1440),'white')
 for i,n in enumerate(['top','left','internal','left_front']):
  im=Image.open(r.OUT/(n+'.png'));im.thumbnail((900,720));sheet.paste(im,((i%2)*900,(i//2)*720))
 sheet.save(r.OUT/'FOUR_VIEWS.png')
 print(v,'rendered actual assembly/cutaways',flush=True)
if __name__=='__main__':main()
