"""Generate auditable progress tables from actual CAD/solver results."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'reports/l2_revision'
def main():
    baseline=json.loads((RP/'baseline_audit.json').read_text())
    lines=['# L2 结构研究进度与证据','',
        '本文件只汇总已经生成的文件和求解结果。候选不等于发布版；未通过项目不会以“待优化”措辞算作通过。',
        '', '基准：R3.2，提交 `f1b1090931d717117287ea2b79c2e14ddc234937`。PA12 密度 1.01 g/cm³ 是对照假设。14.89 g 是目标。',
        '', '## 基准质量分类','',
        '采用真实 BRep 相交/差集，归属顺序为 A 原外皮、B 剩余中的源骨架、C 其他固定安装实体。重合材料只归一次；新短脚贴圆盘未覆盖于旧骨架掩膜的部分计入 C 脚贴安装面。',
        '', '| 类别 | mm³ | PA12 理论 g | PLA 实体 g |','|---|---:|---:|---:|']
    ledger=RP/'partition_R32/volume_ledger.json'
    if ledger.exists():
        data=json.loads(ledger.read_text())
        for r in data['parts']:lines.append(f'| {r["category"]} | {r["mm3"]:.4f} | {r["PA12_g"]:.5f} | {r["PLA_solid_g"]:.5f} |')
        lines+=['',f'BODY 分区闭合差 {data["BODY_closure_error_mm3"]:.6f} mm³；容差 0.25 mm³。总实体独立积分为 18506.6761 mm³，18.69174 g PA12；不会把分类积分微小差异当作减重。']
    lines+=['','## 主键实际三维候选','',
        'C3D10、E=1700 MPa、ν=0.37；1.5 N 面载荷。轴孔使用径向约束、保留绕轴转动自由度；接触岛沿微动法向支承。该比较夹具未求解钢轴间隙、接触滑移或真实微动弹簧。',
        '', '独立复核直接积分全部单元的 Bᵀσ 与应变能，不依赖 CalculiX 对变换坐标约束不完整的 RF 输出。最初复核发现积分点顺序不一致，已更正并重算；原始求解没有被替换为估算。',
        '', '| 候选 | 网格 mm | 中心刚度 N/mm | 外缘 | 内缘 | 前端 | 独立平衡/能量 |','|---|---:|---:|---:|---:|---:|---|']
    ref=None;key_results=[]
    for variant in ['R32','K16','K14','K12','K14R']:
        file=RP/f'key_fem_{variant}.json'
        if not file.exists():continue
        report=json.loads(file.read_text());fine=report['levels'][-1];vals=[r['effective_stiffness_N_mm'] for r in fine['cases']]
        if variant=='R32':ref=vals
        passed=all(r['independent_review']['pass_check'] for r in fine['cases'])
        lines.append('| '+variant+' | '+str(fine['h_mm'])+' | '+' | '.join(f'{v:.4f}' for v in vals)+f' | {passed} |')
        if ref and variant!='R32':key_results.append(dict(candidate=variant,stiffness_retained=[v/r for v,r in zip(vals,ref)],numerical_review_pass=passed))
    lines+=['','减薄 K16/K14/K12 的计算刚度均降低，不能因减重而通过“原则上不弱于 R3.2”的门槛。K14R 为实际增加内侧纵筋后的新候选，须结合全行程碰撞、收敛和刀路判断。',
        '', '## BODY 实际三维筛选','',
        '上背部 5 N 面压力；相向夹持为两侧外皮各 2 N，调整到同一 Y/Z 合力中心。自由夹持仅消除六个刚体模态，反力应接近零；上压工况五脚 Z 向支承，单独检查是否出现负脚贴反力。',
        '', '| 候选 | 网格 mm | 上背刚度 N/mm | 相向夹持刚度 N/mm | 说明 |','|---|---:|---:|---:|---|']
    for file in sorted(RP.glob('fem_*.json')):
        d=json.loads(file.read_text())
        if 'version' not in d or 'levels' not in d or 'first_fixture' in file.name:continue
        for level in d['levels']:
            if len(level['cases'])!=2:continue
            a,b=level['cases'];new='free_equilibrated' in b['case']['name']
            lines.append(f'| {d["version"]} | {level["h_mm"]} | {a["effective_stiffness_N_mm"]:.4f} | {b["effective_stiffness_N_mm"]:.4f} | '+('新版自由夹持' if new else '旧约束，不可直接比较')+' |')
    lines+=['','## 当前验收边界','',
        '- 侧键 F1_P0：新 CAD 经 Gmsh 独立表面网格转换后封闭且无自相交；两键直线装入通过。但静态检查发现夹条/螺栓与横梁干涉，上背刚度下降，已转入 F1B 几何修正。',
        '- 缺少真实 ATK A1 Pro 板型、PAW3950 镜头/板卡尺寸、打印机与材料试样；不宣称电子适配、续航、无线延迟、真实点击与疲劳通过。',
        '- 尚未标记 COMMON_SHELL_REVIEWED。H/D 模块和最终打印包必须在通用壳可测门槛通过后继续。',
        '- 所有历史目录不覆盖。失败候选与错误日志保留，当前工作分支 codex/l2-balanced。','']
    (RP/'RESEARCH_PROGRESS.md').write_text('\n'.join(lines),encoding='utf8')
    (RP/'key_stiffness_comparison.json').write_text(json.dumps(key_results,indent=2)+'\n')
    print('Research tables updated from actual files')
if __name__=='__main__':main()
