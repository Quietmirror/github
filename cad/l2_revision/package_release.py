"""Package only named current components; exclude stale unused export files."""
from pathlib import Path
import json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'releases/Quietmirror-L2-Research';DEST.mkdir(parents=True,exist_ok=True)
def archive(path,entries):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for src,name in entries:z.write(src,name)
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
def main():
 for short,v in [('COMMON','F1H'),('H','L2_H_EST'),('D','L2_D_EST')]:
  base=ROOT/f'exports/l2_revision/{v}';rp=ROOT/f'reports/l2_revision/{v}';met=json.loads((rp/'cad_metrics.json').read_text());checks=json.loads((rp/'mesh_and_volume.json').read_text());assert checks['pass_check']
  printed=[n for n,m in met.items() if m['printable']]
  archive(DEST/(short+'_ALL_PARTS_STL.zip'),[(base/f'print/{n}.stl',n+'.stl') for n in printed])
  extras=[(p,folder+'/'+p.name) for folder in ['gauges','reserves'] for p in sorted((base/folder).glob('*.step'))]
  archive(DEST/(short+'_INDIVIDUAL_STEP.zip'),[(base/f'assembly/{n}.step',n+'.step') for n in met]+extras)
  archive(DEST/('FULL_ASSEMBLY_'+short+'_STEP.zip'),[(base/(v+'_FULL_ASSEMBLY.step'),'FULL_ASSEMBLY_'+short+'.step')])
  shutil.copyfile(base/(v+'_FULL_ASSEMBLY.FCStd'),DEST/('FULL_ASSEMBLY_'+short+'.FCStd'))
  shutil.copyfile(base/(v+'_ALL_PARTS_SINGLE_PLATE.3mf'),DEST/(short+'_ALL_PARTS_SINGLE_PLATE.3mf'))
  view=ROOT/f'views/l2_revision/{v}';archive(DEST/(short+'_ALL_CAD_VIEWS.zip'),[(p,p.name) for p in sorted(view.glob('*.png'))])
  status=dict(variant=v,full_spec_acceptance=False,mesh_checked=True,real_electronics_fit=False,physical_click_or_fatigue_tested=False,printing='Actual250x210 generic PLA slice; printer not confirmed',limitations=['14.89g unmet','H/D carrier assembly paths unresolved','H requires custom compact PCB','D identity and PCB unknown; gauge conflicts','RF/optics/power/runtime not verified'])
  (rp/'RELEASE_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 shutil.copyfile(ROOT/'exports/l2_revision/L2_BOTH_EST/L2_BOTH_EST_ALL_PARTS_SINGLE_PLATE.3mf',DEST/'BOTH_ADAPTER_KITS_SINGLE_PLATE.3mf')
 archive(DEST/'ALL_VALIDATION_REPORTS.zip',[(p,p.relative_to(ROOT/'reports/l2_revision').as_posix()) for p in sorted((ROOT/'reports/l2_revision').rglob('*')) if p.is_file() and p.suffix in ['.json','.md','.csv','.txt']])
 archive(DEST/'TOPOLOGY_AND_SIDE_COMPARISON_VIEWS.zip',[(p,p.name) for p in sorted((ROOT/'views/l2_revision/studies').glob('*.png'))])
 rows=[]
 for v in ['F1H','L2_H_EST','L2_D_EST','L2_BOTH_EST']:
  r=ROOT/f'reports/l2_revision/{v}';m=json.loads((r/'mesh_and_volume.json').read_text());s=json.loads((r/'slice_summary.json').read_text());rows.append(f'| {v} | {s["objects"]} | {m["total_PA12_g"]:.5f} | {s["slicer_total_PLA_g"]:.2f} | {s["estimated_time"]} |')
 text='''# Quietmirror L2 研究交付

**14.89g目标没有达到；不是已验证电子装配或生产版本。** 共用机械F1H通过有限几何检查与主要BODY刚度筛选，但次要抬起/安装耳刚度下降，实际打印材料、点击摩擦及寿命待测。H静态/运动采样通过，但托架装入路径尚未通过；D测量板存在17对冲突。请先读详细限制，再决定打印用途。

| 方案 | 塑料件数 | PA12理论g | PLA总耗材g | 估计时间 |
|---|---:|---:|---:|---|
'''+ '\n'.join(rows)+'''

PA12按1.01g/cm³假设；PLA总耗材含支撑边框，通用250×210床、0.4喷嘴、0.2层。没有真实打印机配置，不直接执行验证G-code。H/D单板及合板均实际切片；一板可切片不等于可组装。

- COMMON：九件共用机械模型。FULL_ASSEMBLY_COMMON.FCStd / FULL_ASSEMBLY_COMMON_STEP.zip / COMMON_ALL_PARTS_STL.zip / COMMON_INDIVIDUAL_STEP.zip / COMMON_ALL_PARTS_SINGLE_PLATE.3mf。
- H：18×18mm紧凑传感器板是**新的定制电路需求**。实际参考15.45×28板失败另存历史，未改名冒充适配。FULL_ASSEMBLY_H.FCStd及同名前缀STEP/STL/3MF。
- D：ATK A1 Pro身份与板型均未知；36×50mm红色测量块不是实板。FULL_ASSEMBLY_D.FCStd及同名前缀文件仅作示意/诊断。
- BOTH_ADAPTER_KITS_SINGLE_PLATE.3mf：一套共用件加两组替换转接件共13件；两组不能同时装入。
- ALL_VALIDATION_REPORTS.zip：完整原始JSON、失败/收敛/质量/路径/切片报告。
- history/：43项实际候选/失败构造CAD归档，另含完整72件R3.2基准包与[恢复说明](history/README.md)。全部本地历史网格也保留；失败候选不可当打印发布版。

完整STEP保留组件身份，没有把活动件融合。FCStd为实际保存重开的具名BRep组件，参数化Python随仓库提供；没有伪称有草图建模历史或求解装配运动副。源码见[构建说明](../../cad/l2_revision/README.md)，报告见[最终对比](../../reports/l2_revision/FINAL_COMPARISON_R3_2_L2_H_D.md)、[硬件空间](../../reports/l2_revision/HARDWARE_H_D_COMPATIBILITY.md)和[二次审核](../../reports/l2_revision/SECOND_PASS_REVIEW.md)。

![实际共用模型](../../views/l2_revision/F1H/FOUR_VIEWS.png)
'''
 (DEST/'README.md').write_text(text,encoding='utf8')
 index=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size) for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='PACKAGE_INDEX.json']
 (DEST/'PACKAGE_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
 (ROOT/'L2_START_HERE.md').write_text('''# Quietmirror 新版 L2 研究工程

本轮遵循新的R3.2→L2任务书。**14.89g未达到，当前共用塑料18.99951g；H/D装配仍有明确限制。**

- [下载入口与各文件用途](releases/Quietmirror-L2-Research/README.md)
- [全部实际文件](releases/Quietmirror-L2-Research)
- [最终尺寸/质量/切片对比](reports/l2_revision/FINAL_COMPARISON_R3_2_L2_H_D.md)
- [二次工程审核](reports/l2_revision/SECOND_PASS_REVIEW.md)
- [实际 CAD 质量分区图](views/l2_revision/studies/A_B_C_D_EXPLAINED.png)
- [H/D空间、冲突及功能边界](reports/l2_revision/HARDWARE_H_D_COMPATIBILITY.md)
- [完整建模源码与复现](cad/l2_revision/README.md)
- [历史CAD索引](releases/Quietmirror-L2-Research/history/INDEX.json)

H为需定制紧凑板的示意：97实体静态及有限运动无未允许干涉，托架直线装入仍失败。D的A1 Pro板型未知，红色测量块存在17对冲突。当前不是已适配供体或可直接生产整机。

![实际四视图](views/l2_revision/F1H/FOUR_VIEWS.png)

原R3.2及此前版本继续保留；本轮只发布到codex/l2-balanced研究分支。
''',encoding='utf8')
 print('Release package ready',len(index),'top-level files',flush=True)
if __name__=='__main__':main()
