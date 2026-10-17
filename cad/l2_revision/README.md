# L2 研究工程与复现

用户选择2026-10-16新MASTER_SPEC，2026-10-17执行。当前是研究交付，不是完成14.89g或真实电子适配的版本。以 reports/l2_revision/FINAL_COMPARISON_R3_2_L2_H_D.md 和 SECOND_PASS_REVIEW.md 为准。

## 文件与版本

- F1H：当前共用机械候选，九件约18.99951g PA12。
- L2_H_EST：97实体，11塑料件；紧凑18×18传感器板是定制电路需求，非现货模块。静态/有限运动采样通过，托架装入路径与RF净空未放行。
- L2_D_EST：82实体，11塑料件；A1 Pro身份、板型均未知。红色36×50测量块产生17对冲突。
- L2_BOTH_EST：只用于拼版的13塑料件，共用件一套、两种转接件各一套。不能同时把两套转接件装进鼠标。
- history ZIP储存每个实际候选独立装配STEP的差异及基准引用；失败候选不是可打印发布。STL/打印位姿可由源码和逐版cad_metrics再导出。最终三套另外提供完整STL/STEP/FCStd/3MF。

## 环境

沿用 cad/rebuild_r3_2/ENVIRONMENT.md。实际本机：CadQuery2.8、OCP、NumPy、SciPy、trimesh、manifold3d、pymeshlab、VTK、Pillow；FreeCAD1.1.4、Gmsh4.15.2、CalculiX2.22、PrusaSlicer2.9.6。依赖在D:/Projects/Quietmirror/_support，源码不下载或上传整个依赖树。先运行 cad/rebuild_r3/enter-project.ps1 设置缓存和线程上限。

## 主要复现入口

所有Python命令使用相同虚拟环境，以仓库根为工作目录；使用不同输出目录或备份后再重建，不覆盖自有修改。

```powershell
python cad/l2_revision/restore_history.py R3.2 --output exports/rebuild_r3_2
python cad/l2_revision/audit_baseline.py
python cad/l2_revision/build_side.py F1W
python cad/l2_revision/bolt_tip_relief.py F1W F1H
python cad/l2_revision/check_candidate.py F1H
python cad/l2_revision/search_side_route.py F1H
python cad/l2_revision/insertion_check.py F1H
python cad/l2_revision/geometry_review.py F1H
python cad/l2_revision/fem.py --version F1H --sizes 2.4 2.0 1.8
python cad/l2_revision/body_second_review.py F1H --extra --targeted
python cad/l2_revision/slice_plate.py F1H
python cad/l2_revision/toolpath_review.py F1H
python cad/l2_revision/assembly_export.py F1H
```

FreeCADCmd执行native.py前设置QUIETMIRROR_ROOT和QM_L2_VARIANT，完成真实保存重开后才运行common_gate.py。历史构建参数的version=R2、feet=0描述的是构造起点，实际R3.1短脚与L2后续操作在build_side/bolt_tip_relief及design_metadata中；不要单独把该构造输入当最终装配尺寸。

common_gate.py只允许已记录几何/主要数值审核的布局研究，明确full_master_spec_acceptance=false。随后modules.py F1H H/D生成两版，module_review.py检查最终姿态、运动、服务净空和采样路径；check_candidate.py --mesh-only只检查网格，绝不是整机适配通过。slice_plate.py自带250×210假定床配置，真实打印机未选定，不直接运行验证G-code。

H/D全部网格通过后，both_kit.py和slice_plate.py L2_BOTH_EST生成双套拼版。render_common/render_modules/render_fem/render_plate分别从实际文件出图。final_reports.py生成汇总；package_history.py整理真实候选CAD，package_release.py整理发布。

A/B/C/D图来自cad_partition_cavity.py F1H导出的实际互斥STEP，再执行render_partition.py；统计切分不代表可拆卸打印零件。完整历史恢复方式见releases/Quietmirror-L2-Research/history/README.md。

## 署名与限制

保留仓库原LICENSE和references/licenses、ATTRIBUTION及各开源参考。读取badjeff/paw3395-pcb的KiCad外轮廓仅用于尺寸审计；没有把未公开Fenrir原厂CAD复制进来。Puppy v3Air获取失败，18g配置未核实。FreeCAD文件包含具名可编辑BRep与参数化Python来源，不伪称有原生草图历史或完整求解装配运动副。
