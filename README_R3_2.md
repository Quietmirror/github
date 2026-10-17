# Quietmirror · Fenrir / MiniSE R3.2

**两个侧键更顺着壳体线条，触感面缩小为 9.4×4.6 mm，向前移动，两键间隔由 5.0 缩到 3.6 mm。** 保留 R3.1 短脚基准与内部微动位置；需更新主壳和两个侧键，其余 6 个打印件可沿用。

![侧键修改前后](views/rebuild_r3_2/R3_2_SIDE_COMPARISON.png)
![R3.2 实际 CAD](views/rebuild_r3_2/R3_2_FOUR_VIEWS.png)

[详细设计与验证](reports/rebuild_r3_2/README.md) · [全部 STL](releases/Fenrir-MiniSE-R3.2/R3_2_PRINT_STL.zip) · [STEP](releases/Fenrir-MiniSE-R3.2/R3_2_STEP.zip) · [FreeCAD](releases/Fenrir-MiniSE-R3.2/FENRIR_MINISE_R3_2.FCStd) · [3MF](releases/Fenrir-MiniSE-R3.2/FENRIR_MINISE_R3_2_PLA_PRINT_PLATE.3mf) · [可编辑源码](cad/rebuild_r3_2/)

前键前移 0.7 mm，后键前移 2.7 mm；外面沿母壳曲面 X 向偏置 0.45 mm，保留 0.60 mm 名义滑动行程。静态 98 个实体／包络、4753 对，五键各 41 个位置，滚轮 72 组合及 18 个机械装入阶段通过；9 个打印网格封闭且各自连通。实物打印、公差、按压力与回弹仍未验证。

本轮实际切片估计 **PLA 37.69 g，4h 54m 57s**，含支撑与裙边。五脚粘贴面保持 Z5.2；0.5 mm 脚贴示例下离地约 0.30 mm。真实主板与镜头高度仍待确认，电子包络不是实测适配。

历史保留：[R3.1 原首页](README_R3_1.md) · [R3 原首页](README_R3.md) · [R2 原首页](README_R2.md) · [更早历史](HISTORY.md)。[本轮历史](HISTORY_R3_2.md) · [主板兼容性边界](reports/rebuild_r3/COMPATIBILITY.md)。

许可 [CERN-OHL-P-2.0](LICENSE)；保留[原署名](NOTICE.md)与[R3.2 署名](reports/rebuild_r3_2/NOTICE_R3_2.md)。
