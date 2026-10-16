# Quietmirror · Fenrir / MiniSE R3

**R3 已修正主键限位、编码器小板与 USB 固定，并完成机械模型及两种电子方案的空间检查。** 机械模型与声明的分体包络通过有限几何检查；ATK 整板假设不通过，实际主板适配尚未确认。

![R3 实际 CAD](views/rebuild_r3/R3_FOUR_VIEWS.png)

[完整检查报告](reports/rebuild_r3/README.md) · [主板与按键兼容性](reports/rebuild_r3/COMPATIBILITY.md) · [打印和安装](reports/rebuild_r3/INSTALLATION.md) · [可编辑源文件](cad/rebuild_r3/)

| 下载 | 内容 |
|---|---|
| [R3 STL](releases/Fenrir-MiniSE-R3/R3_PRINT_STL.zip) | 9 个可打印塑料件 |
| [R3 3MF](releases/Fenrir-MiniSE-R3/FENRIR_MINISE_R3_PLA_PRINT_PLATE.3mf) | 已实际切片，PLA 44.29 g，5h 35m 21s，含支撑与裙边 |
| [R3 STEP](releases/Fenrir-MiniSE-R3/R3_STEP.zip) | 纯机械、PAW3950 分体估计、ATK 不通过诊断三种场景，含分件与接口 |
| [R3 FreeCAD](releases/Fenrir-MiniSE-R3/FENRIR_MINISE_R3.FCStd) | 72 个命名机械／硬件参考实体，已保存重开 |
| [源码与精确 R2 基准](releases/Fenrir-MiniSE-R3/R3_SOURCE_AND_BASE.zip) | Python/JSON 与依赖基准几何，可复现 R3 |

主壳 **88.236×66.096×30.564 mm**。主键触感面／宽度、五脚和既有功能参考位置保留；底部 Z=0–5 mm 与 R2 精确对比一致。主键按微动轴线计算的名义压入量由约 0.477 修正为 0.586 mm。

**检查：98 个实体／包络、4753 对静态组合；五键各 41 个位置；72 个滚轮按压／旋转组合；18 个机械装入阶段。** 9 个打印 STL 封闭、各自连通，无检出的自相交。有限采样不能代替实物试印、公差、回弹或强度测试。

![内部估计空间](views/rebuild_r3/05_custom_estimates.png)

两种电子路线的边界：ATK 真实板未测，历史 36×50×1.2 mm 假设与现机构相交；PAW3950 分体架构的所列包络可放入，但不是某款半组装板的已验证替换。候选电池空间为18×22×6 mm，容量未知；光学工作距离、所有电子支架／线束、固件、无线1 kHz、宏、LOD、充电和12小时续航均未实测。[详细兼容性与待测数据](reports/rebuild_r3/COMPATIBILITY.md)

**历史全部保留：** [R2 原首页](README_R2.md) · [R2 报告](reports/rebuild_r2/README.md) · [V0.9 原首页](README_V0.9.md) · [原历史](HISTORY.md) · [R3 保存说明](HISTORY_R3.md)。R2 有限元结论不自动覆盖 R3 修改后的结构。

许可 [CERN-OHL-P-2.0](LICENSE)，保留[原署名](NOTICE.md)、[R2 署名](reports/rebuild_r2/NOTICE_R2.md)和[R3 署名](reports/rebuild_r3/NOTICE_R3.md)。本项目为独立参数化重建，未复制原厂 CAD 或受限商业扫描。
