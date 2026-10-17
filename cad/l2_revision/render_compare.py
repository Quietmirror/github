"""Same-camera actual R3.2 and F1H exterior/bottom comparisons."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def main():
 spec=importlib.util.spec_from_file_location('rr',ROOT/'cad/rebuild_r3_2/render.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 r.OUT=ROOT/'views/l2_revision/studies';r.OUT.mkdir(parents=True,exist_ok=True);r.MESH=ROOT/'exports/rebuild_r3_2/assembly';names=list(json.loads((ROOT/'reports/rebuild_r3_2/cad_metrics.json').read_text()))
 from PIL import Image
 im=Image.new('RGB',(1800,2880),'white')
 for i,(n,cam,up) in enumerate([('top',(0,40,230),(0,-1,0)),('left',(230,40,17),(0,0,1)),('right',(-230,40,17),(0,0,1)),('bottom',(0,40,-230),(0,-1,0))]):
  r.render('R32_'+n+'.png',names,cam,up=up,title='R3.2 基准 / '+n,note='同一相机、尺度与实际原始模型',footer='R3.2 / 未改变历史源文件')
  for j,p in enumerate([r.OUT/('R32_'+n+'.png'),ROOT/f'views/l2_revision/F1H/{n}.png']):
   q=Image.open(p);q.thumbnail((900,720));im.paste(q,(900*j,720*i))
 im.save(r.OUT/'R32_F1H_COMPARISON.png');print('Same-camera R32/F1H comparison',flush=True)
if __name__=='__main__':main()
