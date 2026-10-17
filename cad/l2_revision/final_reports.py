"""Generate user-facing release evidence from actual saved results; no synthetic passes."""
from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'reports/l2_revision';COMMON='F1H'
def rd(path):return json.loads(path.read_text())
def put(name,text):(RP/name).write_text(text.strip()+'\n',encoding='utf8')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(map(str,row))+' |' for row in rows]])
def main():
 base=rd(RP/'baseline_audit.json');gate=rd(RP/COMMON/'common_gate.json');f=rd(RP/f'fem_{COMMON}.json');ref=rd(RP/'fem_R32.json');mass=gate['actual_PA12_g'];slice=rd(RP/COMMON/'slice_summary.json')
 put('BASELINE_R3_2_AUDIT.md',f'''# R3.2 独立基准审计

基准提交 `f1b1090931d717117287ea2b79c2e14ddc234937`；保留整个历史，工作位于 `codex/l2-balanced`。当前工程在 D 盘，依赖和计算缓存也在 D 盘。

实际读取九件 STEP 与 STL；采用 OCP 自适应原生体积积分容差 1e-7。原始总实体 18506.6760995 mm³，按 PA12 1.01 g/cm³ 得 18.69174286 g；按 PLA 1.24 得 22.94827836 g，后者不含切片支撑。默认 OCC 对裁剪 NURBS 的简化 Volume 会偏大，不能用于本项目 BODY 的质量计算。详见 `baseline_audit.json` 与 `calculation_audit.md`。

五个脚贴平台 Ø8、厚1.6、粘贴面 Z5.2；壳体最低约 Z5.0。示例0.5脚贴使鼠标垫为 Z4.7，约0.299离地；估计镜头最低 Z7.8，3.1光学距离只是尺寸链示例。

真实孔型有 R0.85 圆角；尖角多边形面积1301.271 mm² 与圆角后约1292.284 mm²不同。七根理想梁的1544.045 mm³是未扣交叠毛体积，不能当净骨架质量或全删预算。
''')
 put('ORIGINAL_CALCULATION_SECOND_REVIEW.md','''# 原始计算二次复核

L2目标14.89g相对18.69174286g需要净移除3764.101842mm³，即20.34%。工作包预算只是目标分配，并非已找到的可删材料。

原二维6.6%/10.3%改进无法唯一复现：缺少精确边界、载荷分配、圆角及网格实现。新的独立 Gmsh/CST 面板62×41、三个网格0.75/0.5/0.35完成，P0/P1末档后缘刚度504.196/518.586、侧缘271.566/282.609 N/mm，新定义下约+2.85%/+4.07%，最后网格变化小于1%。这些是面内代理，不是鼠标整体刚度。见 `conforming_2d_proxy.json`。

三维采用实际 STEP 体网格C3D10。曾发现顶部选面误选内部横梁顶面，已改为只在解析母壳外表面0.15mm范围内加载，全部当前对比重新计算；97/45等早期数值不可和当前120左右的结果混用。独立积分复核曾发现 CalculiX 积分点排列差异，已修正为L1/L2/L3/L4顺序，重新校核力、力矩与应变能。失败记录保留，不把修正后的检查伪称为第二个硬件试验。

互斥体积分类使用同一内腔分类法同时重做R32/F1H；避免与外壳母曲面重合的布尔交导致无效分区。未经容差复核的 ShapeFix 被拒绝；没有修补或改变交付 BODY 来凑质量。
''')
 ledgerrows=[]
 for v in ['R32',COMMON]:
  led=rd(RP/f'partition_v2_{v}/volume_ledger.json')
  for q in led['parts']:ledgerrows.append([v,q['category'],q['mm3'],q['PA12_g'],q['PLA_solid_g']])
 with (RP/'A_B_C_D_VOLUME_BUDGET.csv').open('w',newline='',encoding='utf-8-sig') as out:
  w=csv.writer(out);w.writerow(['variant','category','volume_mm3','PA12_g','PLA_solid_g']);w.writerows(ledgerrows)
 put('MATERIALS_AND_LOAD_CASES.md','''# 材料、载荷与适用范围

PA12 rho1.01 g/cm³、E1700 MPa、ν0.37都是本轮统一比较假设；不是已测打印件。PLA切片rho1.24独立计算。EOS不同工艺材料数据不能自动覆盖学校机器、层间方向、温湿度、疲劳或蠕变。

LC1左右主键各1.5N，中心/内缘/外缘/前端四个面斑；钢轴径向支承和微动接触岛为明确简化夹具。LC2两侧键各1.5N，前/中/后三处，导向面与接触岛支承，不求解摩擦与开合接触。LC3两侧外皮相向各2N，合力和合矩为零，3-2-1仅去刚体模态，不把鼠标固定在桌上。LC4上背外皮5N，五脚竖向支承并检查负反力。LC5后角向上2N、两个刚性手指接触区，是局部扭转夹具。LC6载架两轴承及编码器区域共1.5N，独立滚轮轴端参考支承。LC7真实PCB耳维护下压力2N；没有用FR4当无限刚性梁。

线弹性范围内0.5/1/1.5倍载荷的位移与应力严格线性缩放、刚度不变；R32 LC4已经实际重跑三档以检查实现。所有其他工况的倍载结果是方程推导，不能标为另一次求解。LC8 15N可由LC4乘3作线弹性情景，不代表误压损伤/屈曲/接触已计算。E1200/1700/2200的同质敏感性已在R32实跑，选定模型按k比例E、位移反比E估算；ν0.30与锚点交换另行实跑。打印各向异性、温湿度和寿命缺少试样参数，保持未验证。

梁基准完成两档，弯曲误差约1.12%、轴向约0.463%；见FEM_BEAM_BENCHMARK.md。许用应力和安全系数没有被虚构；有限元结果不是产品安全或疲劳认证。
''')
 rows=[]
 for file in sorted(RP.glob('fem_*.json')):
  q=rd(file)
  if 'version' not in q or not q.get('levels') or 'first_fixture' in file.name:continue
  z=q['levels'][-1]
  if len(z['cases'])!=2:continue
  if 'outer_back' not in z['cases'][0]['case']['name']:continue
  rows.append([q['version'],z['h_mm'],*[f'{c["effective_stiffness_N_mm"]:.3f}' for c in z['cases']]])
 put('TOPOLOGY_WALL_THICKNESS_STUDY.md','''# 实际孔型、骨架、壁厚与主键研究

真实单变量候选P1 R1.0/1.3/1.5、P2三角网格、P3蜂巢、P4圆角槽、P5椭圆、P6混合圆角均留存源码和几何。P1维持圆角后投影面积，曲面体积并不完全相同；不能称严格等质量。P3受限于保护带不能保持等面积且有240个自交面，拒绝。P4原生实体可求解但输出STL不闭合，拒绝打印。P5/P6夹持或顶部刚度下降。P6是非均匀几何候选，不冒称已经完成自动拓扑优化。

B1圆梁变细仅省约0.067g且夹持变弱；B2定向椭圆的体网格两次因重合面失败，无强度通过；B3桁架两种路径产生分离实体，保留失败支撑模型，不能悄悄删除小块；B4混合加强更重。C1耳角削料仅省0.04960g，网格和夹持筛选不通过；S17局部侧壁1.7mm仅省0.01538g且两项刚度下降。无全壳统一减薄。

主键K16/K14/K12每对分别省0.21139/0.31794/0.42491g；三个网格与四处偏心按压都显示刚度损失。K14R加深背筋只改善前端，其他方向仍较弱。选择保留原主键。原滚轮和载架保留，三档独立有限元完成；末档刚度分别132.687和5.268N/mm，夹具含刚性参考接触，未测滚动阻力。

F1H组合P1 R1.3、前移低突出侧键、绕开工具的对称横梁、局部横梁竖向加强及0.817mm³螺栓尖端避空。它是本轮完整检查的较保守组合，并非全设计空间的最轻解。侧键以外维持对称视觉，功能机构保留左右差异。底部与五脚基准保留。

下表均为同一修正外皮载荷定义；单档候选只作筛选：

'''+table(['候选','最细网格mm','上背N/mm','夹持N/mm'],rows)+'''

壁厚采用原生BRep线段交和法向弦长抽样，详见F1H/geometry_second_review.json。最短边缘弦长不能直接解释成连续薄墙。保留1.8mm主体标称、主键2mm、实际圆梁/加强节点；这不是全表面最小厚度证明。实际刀路核对局部零件与五脚支撑，未完成每条孔边逐层手工测量，不能声称所有细小配合可直接FDM到尺寸。
''')
 conv=[]
 for v,z in [('R32',ref),(COMMON,f)]:
  for level in z['levels']:
   for q in level['cases']:conv.append([v,level['h_mm'],q['case']['name'],f'{q["effective_stiffness_N_mm"]:.5f}',f'{q["maximum_displacement_mm"]:.6f}',f'{q["volume_weighted_P99_vm_MPa"]:.5f}',f'{q["maximum_vm_stress_MPa"]:.5f}'])
 put('FEM_CONVERGENCE_AND_FAILURES.md','''# 三维收敛、独立复核与失败记录

Gmsh4.15.2 / CalculiX2.22；C3D10，三个目标尺寸2.4/2.0/1.8mm。记录网格连通、积分点Jacobian、源STEP、输入deck和结果摘要。F1H最后两档刚度变化：顶部0.633%、夹持0.335%；P99变化0.945%和0.248%。顶刚度增幅约0.96%很小，处于网格差异量级，合理表述为基本保持；夹持约+6.84%是该夹具结果。

独立第二脚本直接在全部单元积分Bᵀσ和应变能，不依赖求解器显示的总反力，主要力/矩/能量相对误差约1e-8，门槛0.002。锚点交换与ν变化均另跑。次要LC5/LC7夹具若比基准降低，在SECOND_PASS_REVIEW中原样报告，不将全部工况概括为“提升”。

'''+table(['版本','h','工况','k N/mm','最大位移mm','P99 MPa','峰值MPa'],conv)+'''

历史失败包括：h1.3求解器访问冲突、早期细分多边形造成超大体网格、B2重合面、F1最初STL自交、横梁/螺栓干涉、旧装入路径碰撞。采用真实CAD修正、精确圆弧、必要的独立Gmsh表面剖分解决相应问题；未用补洞或删除分离体掩盖错误。压缩发布包保留候选差异，原始求解缓存留在D盘_support/work/l2。重新求解需要本地依赖及磁盘空间。
''')
 put('FENRIR_SIDE_KEY_REDESIGN.md','''# 顺形双侧键与内部机构

F1H使用F1低突出造型：接触面10.4×3.6mm、中心Y49/62、Z15.5、间隔2.6mm；母壳法向抽样最大突出约0.193mm。相对R3.2，面更低、更贴壳，长度稍增，前后位置各前移0.3mm；与任务书“细长低突出”路线一致。下方连续拇指面保留。F2E为10.4×4.0、约0.31mm突出、3°轮廓斜度的另一真实完整方案，保留研究文件。

微动、导轨、捕获销、夹条一起移动；不是单改键帽。导轨有效长度5.4mm，全行程最小啮合5.1mm，原参考约3.5mm。两键独立滑动0.60mm，接触轴线投影约0.58mm。实际开关自由高、预行程与过行程待测，0.02mm间隙不能作为普通FDM免调整承诺。

每键前/中/后1.5N有限元三网格，最弱位置刚度提高；部分旧后缘支点位置更硬，不能说每一位置均改善。约束为无摩擦双面导轨及刚性微动接触；真实偏心卡滞、回弹、磨耗需要实物。简化两导轨反力模型给摩擦/驱动力比例约2μe/L，取e约3.3mm、L5.1mm，μ0.1/0.2/0.3/0.4时约0.13/0.26/0.39/0.52；只是敏感性示意，μ未测且不覆盖毛刺/收缩/斜插。

两键直线X向装入各101位置通过。侧微动改从底部装入，前微动先、后微动后，然后后夹条先、前夹条后。完整18阶段有限采样通过。螺丝旋入、工具握柄和连续扫掠未完全证明；不能声称不存在任何真实装配冲突。
''')
 extras=gate['secondary_fixture_comparison'];put('SECOND_PASS_REVIEW.md',f'''# 独立第二轮审核

状态：**{gate['status']}**。只冻结本次几何用于估计布局和原型交付；`full_master_spec_acceptance=false`。14.89g目标没有达到，实际材料/硬件/疲劳验证仍缺失，因此不发布“全面通过”“可直接生产”结论。

九个打印件各为一个有效原生实体；交付STL封闭、统一方向、单连通、零自交。72零件2556静态对零未允许干涉；仅明确的螺纹啮合区允许局部相交。五个运动机构各41位置，滚轮转动与中键72组合；18装入阶段；五脚原生共面；FreeCAD72个具名BRep保存重开通过。

主要BODY工况比较与三档收敛通过；主键、侧键、滚轮、载架均另作三维夹具筛选。未测试实际接触非线性、摩擦、层间方向和疲劳。次要夹具结果如下，下降项保留为开放问题：

'''+table(['次要工况','R32 k','F1H k','比值'],[[q['case'],f"{q['R32_k']:.5f}",f"{q['selected_k']:.5f}",f"{q['ratio']:.5f}"] for q in extras])+'''

F1H体积分类闭合误差-0.18557mm³，R32为-0.00907mm³，容差0.25mm³；整件独立积分是质量权威值，未把积分差记为减重。外皮/骨架/安装分区不是商业原厂结构解析。每个脚贴圆盘的共面与实体包含关系另以原生布尔验证；最小弦长只作抽样风险提示。
''')
 put('DONOR_A1PRO_MISSING_MEASUREMENTS.md','''# ATK A1 Pro 待测尺寸

`DONOR_ID_UNVERIFIED / PCB_GEOMETRY_UNVERIFIED / FIT_NOT_CERTIFIED`。旧A1 Plus失败诊断不改名当作A1 Pro。当前36×50×1.2mm板仅是通用空间测量块，不是供体轮廓。

需要：底部铭牌及完整官方型号；PCB正反面带尺照片及外形DXF/STEP；板厚、每个孔坐标/孔径/禁布区；传感器真实型号与轴心；镜头基准面及推荐工作距离；最高元件与底部凸件；左右/侧微动型号、轴线、自由高/预行程/总行程；编码器轴高、六角尺寸、焊脚与中键位置；USB壳体、插头外包与拔插方向；电池容量、尺寸、质量、保护板、插头极性和线长；电源控制、天线净空、接收器和固件支持。

不能切PCB、剪天线、移除充电保护或私自取消原板零件来实现适配。真实板过大时，先考虑不同板型/分体方案；若必须改外壳，回到结构审核。
''')
 donor=dict(product_name='ATK A1 Pro',status=['DONOR_ID_UNVERIFIED','PCB_GEOMETRY_UNVERIFIED','FIT_NOT_CERTIFIED'],units='mm',verified_outline=None,board_thickness=None,mount_holes=None,sensor_identity=None,optical_center=None,lens_datum=None,component_keepouts=None,usb=None,battery=None,antenna=None,reference_gauge_only=[36,50,1.2])
 (ROOT/'cad/l2_revision/donor_template.json').write_text(json.dumps(donor,indent=2)+'\n');(RP/'ATK_A1_PRO_UNVERIFIED.json').write_text(json.dumps(donor,indent=2)+'\n')
 slicing=[];boms=[];variants=[COMMON,'L2_H_EST','L2_D_EST','L2_BOTH_EST']
 for v in variants:
  r=RP/v
  if not (r/'slice_summary.json').exists():continue
  s=rd(r/'slice_summary.json');mv=rd(r/'mesh_and_volume.json') if (r/'mesh_and_volume.json').exists() else None
  slicing.append([v,s['objects'],f"{mv['total_PA12_g']:.5f}" if mv else '-',f"{s['net_parts_PLA_g']:.2f}",f"{s['support_PLA_g']:.2f}",f"{s['brim_PLA_g']:.2f}",s['slicer_total_PLA_g'],s['estimated_time']])
  met=rd(r/'cad_metrics.json');vol={q['part']:q for q in mv['parts']} if mv else {}
  with (r/'BOM.csv').open('w',newline='',encoding='utf-8-sig') as out:
   w=csv.writer(out);w.writerow(['id','name','quantity','printable','CAD_mm3','PA12_theory_g','measured_mass_g','supplier_identity','evidence'])
   for i,(n,m) in enumerate(met.items(),1):
    q=vol.get(n,{});w.writerow([i,n,1,m['printable'],q.get('adaptive_CAD_mm3',''),q.get('PA12_g',''),'UNMEASURED','UNSELECTED' if 'EST' in n or 'UNVERIFIED' in n else 'REFERENCE_GEOMETRY_ONLY','No purchased assembly or electrical test'])
 put('PRINT_SLICING_VALIDATION.md','''# 实际PLA单板切片

PrusaSlicer2.9.6；假定床250×210mm、0.4喷嘴、0.2层高、4墙、20%gyroid、210/60°C、4mm brim、snug支撑并允许模型上支撑。打印机型号未确认。所有塑料件独立、无缩放，.3mf自带完整配置，重新打开后不用外部--load再切片校验。

'''+table(['方案','件数','PA12理论g','净件PLA g','支撑g','边框g','总PLA g','估时'],slicing)+'''

耗材由真实G-code正挤出XY刀路按TYPE独立累加，与切片器页脚差小于0.15g；首个解析器曾漏读“.02919”这种省略整数位小数，已修正并重新统计。所有挤出中心线加半线宽在假定床内；一板通过只针对这个床与配置。

BODY保持正立、五脚朝下；五脚接触面比最低结构高0.2mm，已核对首层每个脚点下有支撑路径。主键顶面向上，侧键按导轨方向平放，滚轮轴竖直以减少六角轮廓失真。支撑主要在上壳、横梁、铰链/安装座、主键底部和适配托架。清除孔内支撑、测量后修孔；2.35mm轴孔、M2通孔、侧键导轨/触点、1.67mm六角都应先做公差小样测试，不能依靠0.02–0.06mm名义差直接装配。没有实际床型，不交付可直接上机的G-code；验证G-code留D盘缓存。H/D托架的直线装入检查未通过，当前3MF只证明能够一板切片，不代表整机可按图装成。
''')
 put('BOM_AND_ASSEMBLY_INSTRUCTIONS.md','''# BOM与装配顺序

各版本BOM.csv按实际装配组件编号，qty=1代表文件中的一个实体；不把估计电子盒当作已采购物料。所有购买件质量为UNMEASURED，供体及电池容量未确定，无法给真实整机克重。理论塑料质量不包含螺钉、钢轴、开关、板卡、电池、脚贴；接收器不装在鼠标里，不计鼠标质量。

1. 先打印公差小样；清支撑、去毛刺，测五脚共面与轴/螺丝孔，不能磨穿承力筋。
2. 从开放底部按路径先装前侧微动，再后侧微动；后夹条先于前夹条，随后螺钉/垫片/螺母。不得采用旧版从前端穿过横梁的路径。
3. 装左右主微动、USB参考座；两侧键从外侧直入后装捕获销。实测按钮自由高，调整触点与止挡，确保释放和最大行程，不把厂家PT+OT直接当安全总行程。
4. 组装滚轮、编码器参考板、载架、钢轴与中键机构；检验旋转和点击分别独立。最后装左右主键与铰链轴。
5. 电子转接件仅按module_review的可达路径装入；载架与PCB的真实固定方式未测时不能宣称功能装配完成。H/D示意中的支架先试装，存在冲突的D测量板不要强塞。
6. 电池使用可拆束带和绝缘缓冲，避免挤压/螺钉尖端/导线拉扯；天线按实物RF要求留空；校验极性、保护及充电后才通电。没有通过实际电气测试。

试握记录：有效夹持宽度、顶掌、无名指/小指拖地、滚轮与侧键触达、误触、抬鼠稳定性、前/中/后偏心按压卡滞和回弹。实际500/1000次初期循环后再测间隙；这只是建议的验证步骤，不是已有寿命数据。
''')
 hardware=[]
 for v in ['L2_H_EST','L2_D_EST']:
  r=RP/v
  if not (r/'static_checks.json').exists():continue
  st=rd(r/'static_checks.json');mod=rd(r/'module_review.json');hardware.append([v,len(st['conflicts']),mod['carrier_insertion']['pass_check'],'否'])
 put('HARDWARE_H_D_COMPATIBILITY.md','''# H/D电子空间与功能边界

H首先实际试放从badjeff/paw3395-pcb读取外轮廓的15.45×28×1.6板包络，在原壳内失败，完整记录留在L2_H_REFERENCE_BOARD_BLOCKED。当前H改为**18×18×1.6自定义紧凑传感器板的设计需求**，这需要另做电路或找到已核实的板，不是宣称参考板已缩小适配、更不是已采购的半组装模块。RF/电池/天线/线束同样为估计。D仅提供可换载架与36×50×1.2空间测量板，绝不是实测ATK A1 Pro。

'''+table(['方案','未允许静态冲突数','底部直入支架采样通过','真实主板适配证明'],hardware)+'''

完整干涉对与原生交叠体积在各版本static_checks.json，净空和支架路径在module_review.json。H当前最终姿态静态及按键有限运动采样通过；但从底部以及其余五个直线方向插入托架仍失败，须继续把支架拆为可连接小件或验证旋转装入路径。没有证明绝对无法装入，也没有伪称可装配。H天线净空内仍有约74.92mm³塑料托架和4.58mm³馈线；馈线本属必要天线连接，介质影响要按真实天线测试。D的17个未允许交叠全部涉及未知板测量块，其电池服务区也不通过。

旧通用耳的连接臂部分填回了名义槽孔，M2螺钉实放失败。新托架改为非永久的绝缘束带鞍座，不改动common壳；束带、PCB边缘固定和实际元件禁布区尚未验证。当前装配与3MF是研究示意，未知板不放行“已适配打印”。

PAW3950仅是传感器型号。400–6400DPI、2.4GHz1k、宏、LOD、五键、低延迟、无可选同步、充电和12h续航均需PCB/固件/接收器证据。保持原供电保护，不新加外部DPI或独立拨动开关；选定系统必须提供合适电源控制。

电池18×22×6是包络而非容量保证。按可用容量75%情景，300/400/500mAh要持续12h，平均电流上限18.75/25/31.25mA。最大功耗实测、截止电压、容量与温度均未知，不能宣称达标。光轴垂直鼠标垫；Z7.8镜头底、Z5.2脚贴面、0.5脚贴仅给出3.1mm示例光学间距，最终必须按真实镜头尺寸链调整。
''')
 put('FINAL_COMPARISON_R3_2_L2_H_D.md',f'''# R3.2至本轮L2研究交付

**14.89g目标未达到。** 选择F1H的九件共用塑料为{mass:.5f}g（PA12假设1.01），比R3.2增加{mass-18.6917428605:.5f}g，超目标{mass-14.89:.5f}g。必要横梁加强与侧键机构修正占用了减重空间；所有减薄候选的收益与失败如实保留。不能称为成功减重20%或25g整机。

F1H是本轮完整几何检查、主要工况基本保持及低突出侧键的研究候选，不是数学全局最轻解，也不代表所有二次夹具、实际材料、硬件和疲劳完全通过。H/D再加实际可拆支架，质量另列，不能把共用19g当含适配件总重。

'''+table(['方案','件数','PA12理论g','净PLA g','支撑g','边框g','总PLA g','估时'],slicing)+'''

实际交付：参数化Python、历史候选差异包、独立STL/STEP、具名完整STEP与FreeCAD原生文档、真正切片3MF、实际CAD渲染、BOM、装入路径及数值审计。FreeCAD是具名可编辑BRep组件，随附参数化源码；不是伪称原生草图历史或已求解运动副。原R3.2及main保持。

建议继续使用FreeCAD/CadQuery/Gmsh/CalculiX完成实测板型导入、装配约束和局部修正；本轮已经实际调用这些外部工具。缺的关键是板卡实物、打印公差和功能测试，换一个建模软件不会自动补齐它们。
''')
 put('RESEARCH_PROGRESS.md',(RP/'FINAL_COMPARISON_R3_2_L2_H_D.md').read_text()+'\n详细研究：TOPOLOGY_WALL_THICKNESS_STUDY.md、FEM_CONVERGENCE_AND_FAILURES.md、SECOND_PASS_REVIEW.md。\n')
 (ROOT/'cad/l2_revision/STATUS.md').write_text((RP/'FINAL_COMPARISON_R3_2_L2_H_D.md').read_text(),encoding='utf8')
 print('Final evidence documents generated from actual results',flush=True)
if __name__=='__main__':main()
