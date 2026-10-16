# R2 续接来源与设计边界

2026-10-16 续接分享记录《导入 Quietmirror/github》。用户指定新工程、工具及缓存放在 `D:\Projects\Quietmirror`。原 C 盘工程保留；本轮不覆盖 R1 或 V0.9 文件。

续接基线为公开仓库 `ht1580/Quietmirror-mouse` 的 `rebuild/fenrir-minise-r1` 分支，提交 `07fcd46dc8b719804473313ddc0c5f36acd422a9`。该提交明确未验收，不能将其旧导出或旧检查沿用为 R2 验收结果。源码沿用仓库的 CERN-OHL-P-2.0 许可；保留原许可证和作者来源。R2 的主面、机构和检查代码由该基线继续修改。

## 本轮固定的设计条件

- 外壳母体按名义 81.7 × 61.2 × 28.3 mm 放大 1.08，目标 88.236 × 66.096 × 30.564 mm。这是布局试验，不是已验证的人体工学最优尺寸。
- 五脚直径仍为 8 mm，脚底 Z=0；Z=0–5 mm 只允许五脚所在的圆柱范围有打印材料。保留上方的连续承力路线。
- 五个 D2F 微动、EC10E 编码器、M2 安装界面、USB-C、传感器预留和侧键触感面均不随外壳缩放。
- 实心独立左右键、大尺度 MiniSE 风格三角／梯形窗口；前端为 Y=0，X 横向、Z 向上，全部毫米。
- 本轮是可装机械元件的样机。通用板支耳和传感器空间不等于某块现成主板的安装尺寸，也不等于已经实现无线、充电、DPI、宏或 LOD。

## 实际阅读的上游工程文件

R1 的 `parameters.json`、`surfaces.py`、`mechanics.py`、`interfaces.py`、`build.py`、`check.py`、`interface_check.py`、`check_requirements.py`、`fem_check.py`、`native.py`、`slice.py`、`render.py`、`PROGRESS.md` 以及已输出的冲突记录。

外形源于独立 BSpline 参数化，不含原厂 CAD 或商业扫描。R1 的照片轮廓比较只反映所选图片上的投影相似度，不能作为三维制造精度。放大和后续机械修改后，不沿用旧照片比较数值作为新版本验收分数。

## 公开资料

- [Fenrir Pro 官方](https://shop.g-wolves.com/products/g-wolves-fenrir-pro-8k-wireless-mouse)：外形、短宽比例与名义尺寸。
- [Razer Viper Mini Signature Edition 官方](https://www.razer.com/gaming-mice/razer-viper-mini-signature-edition)：独立主键和大尺度外骨骼分区的风格参考。
- [Omron D2F 原厂图](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf)：实际读取并查看尺寸页。壳体 12.8 × 5.8 × 6.5 mm，安装孔间距 6.5 mm。OP 的基准是安装孔中心线，不能直接当作距壳底高度。自由高度与可用行程仍须对实购型号校准。
- [Alps EC10E 原厂图](https://tech.alpsalpine.com/cms.media/product_catalog_ec_03_ec10e_en_a9ede251c7.pdf)：实际读取并查看图 1。使用 7 mm 安装高度的轮廓和轴接口作为设计参考；产品目录本身要求实际供货规格另行确认。
- [GCT USB4105](https://gct.co/connector/usb4105)：沿用 R1 的机械包络。16 × 10 mm 小板是自定义适配板建议，不是现货电路。
- [olliebella](https://github.com/badjeff/olliebella)、[Kotinos](https://github.com/pseudoku/Kotinos)：上轮开放结构与模块分离参考沿革。本轮不把这些工程的 PCB 孔位移植为 Fenrir 或 ATK 孔位，亦未新增复制其几何。

原厂 PDF 留在 D 盘支持目录供工程核对；仓库引用原始资料链接，不将产品图片或完整手册作为本项目自行授权的素材。
