"""Plan view of actual G-code extrusion, not an imagined placement diagram."""
from pathlib import Path
import sys,json,re,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
def main():
 v=sys.argv[1];rp=ROOT/f'reports/l2_revision/{v}';s=json.loads((rp/'slice_summary.json').read_text());out=ROOT/f'views/l2_revision/{v}';out.mkdir(parents=True,exist_ok=True)
 im=Image.new('RGB',(1500,1300),'#f8fafb');d=ImageDraw.Draw(im);font='C:/Windows/Fonts/msyh.ttc';f=lambda n:ImageFont.truetype(font,n)
 scale=4.7;x0=160;y0=1155;xy=lambda x,y:(x0+x*scale,y0-y*scale)
 d.rectangle((*xy(0,210),*xy(250,0)),fill='#e9edf0',outline='#758999',width=2)
 cur=dict(X=0.,Y=0.,E=0.);relative=False;role='';lines={'support':[],'brim':[],'part':[]}
 for line in (ROOT.parent/f'_support/work/l2/{v}/slice/{v}_validation_only.gcode').open(encoding='utf8'):
  if line.startswith(';TYPE:'):role=line[6:].strip()
  code=line.split(';',1)[0].strip()
  if code=='M83':relative=True
  elif code=='M82':relative=False
  elif code.startswith('G92'):
   for k,val in re.findall(r'([XYE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code):cur[k]=float(val)
  elif re.match(r'^G[01](?: |$)',code):
   old=cur.copy();q={k:float(val) for k,val in re.findall(r'([XYE])(-?(?:\d+(?:\.\d*)?|\.\d+))',code)};de=q.get('E',0.) if relative else q.get('E',cur['E'])-cur['E']
   cur['X']=q.get('X',cur['X']);cur['Y']=q.get('Y',cur['Y'])
   if 'E' in q:cur['E']=cur['E']+de if relative else q['E']
   if de>0 and math.hypot(cur['X']-old['X'],cur['Y']-old['Y'])>1e-7:
    group='support' if 'Support' in role else 'brim' if 'Skirt' in role or 'Brim' in role else 'part';lines[group].append((*xy(old['X'],old['Y']),*xy(cur['X'],cur['Y'])))
 for group,color in [('brim','#cbbca8'),('support','#b8bfc5'),('part','#285c66')]:
  for segment in lines[group]:d.line(segment,fill=color,width=1)
 for i,p in enumerate(s['placements'],1):
  a,b=p['bounds'];x,y=xy((a[0]+b[0])/2,(a[1]+b[1])/2);d.ellipse((x-14,y-14,x+14,y+14),fill='white',outline='#162e3e',width=2);d.text((x-6,y-13),str(i),font=f(18),fill='#172f40')
 d.text((40,22),v+' / 实际单板挤出刀路俯视',font=f(31),fill='#183645');d.text((40,74),'250 × 210 mm 假定床 / 0.4喷嘴 / 所有层投影 / 蓝绿=零件 灰=支撑 米色=边框',font=f(21),fill='#50616f')
 label='　'.join(str(i+1)+':'+p['part'].replace('REMOVABLE_CARRIER_EST','CARRIER') for i,p in enumerate(s['placements']))
 for i in range(0,len(label),105):d.text((40,1180+(i//105)*25),label[i:i+105],font=f(16),fill='#314c5c')
 im.save(out/'PRINT_PLATE.png');print(v,'actual toolpath image',flush=True)
if __name__=='__main__':main()
