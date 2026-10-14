# 上游来源与实际审阅记录

本文件记录V0.1阶段的真实源文件审阅，后续V0.2继续采用这些来源。V0.2改为超椭圆放样连续薄壳；新增游狼视觉参考见[GWOLVES_REFERENCE.md](GWOLVES_REFERENCE.md)。下文球面接触片和局部2.4 mm边缘等描述专指V0.1。

审阅日期：2026-10-14。源仓库在本机 `.reference/` 中浅克隆，未将其整体打包或上传。下面的几何、SCAD 和 KiCad 文件均实际读取；数值提取见 `reports/reference_geometry.json`，网格实视图见 `views/ref_olliebella.png`、`views/ref_kotinos.png`。

## olliebella — badjeff

- 仓库：https://github.com/badjeff/olliebella
- 固定提交：`03441afe9fff56abf8dc31e4603e627237b769a9`
- 许可证：CERN-OHL-P-2.0；完整文本保留在 `licenses/olliebella-CERN-OHL-P-2.0.txt`。
- 实际读取网格：`STLs/base.stl`、`shell.stl`、`shell (thumb rest).stl`、`shell (pinky rest).stl`、`m1.stl`、`m2.stl`、`wheel.stl`、`lens U mount.stl`、`rear skake.stl`（上游文件名如此）。
- 实际读取说明：`README.md`、`LICENSE`。
- 已枚举 `CADs/olliebella v1.f3z` 等 Fusion 档案，但本轮没有在 Fusion 中打开参数时间线；几何判断依据是上述真实 STL，而非假称已经解析 F3Z。

采用的结构思想：紧凑的前部按键/滚轮区域、独立传感器定位区、五点圆形脚贴布局、以连续承力路径保留夹持刚度。上游原生三个按键，因此本轮两个拇指凸台为新增的固定试触达几何。上游的 1.1 mm 壁厚没有照搬，本轮普通面采用 1.8 mm，接触边缘局部 2.4 mm。

上游 README 的五个脚贴为 7.5 mm 圆点；本轮重新设计五个 Ø8.8 mm 平台。其镜头到表面的约 2.4±0.2 mm 是该项目自己的设计尺寸，**不是本项目已验证的 PAW3950 光学高度**。本轮也没有沿用其无线系统或宣称已经实现 1000 Hz。

## Kotinos — pseudoku

- 仓库：https://github.com/pseudoku/Kotinos
- 固定提交：`7b367537a29e647da2a012a21f46507734d47ec2`
- 许可证：GPL-3.0；完整文本保留在 `licenses/Kotinos-GPL-3.0.txt`。
- 实际读取网格：`STL/Kotinos.stl`、`IndexPaddle.stl`、`MiddlePaddle.stl`。
- 实际读取 SCAD：`Build/DataHand.scad`、`Build/DataIndexPaddle.scad`、`Build/MainBuild.scad`；同时查看 `Build/HSK_PCB.scad`、`Build/PaddleSurfaceGenerator.scad` 的板形与曲面构造部分。
- 实际读取说明：`README.md`、`LICENSE`。

采用的结构思想：分开的食指/中指接触区、连续接触面与开放骨架分工、用承力筋连接接触区和底部、按部位独立调节参数。上游的指节长度、关节角度与掌指原点分别参数化，这支持“不按手长整体等比缩放”的做法。

**没有把 DataHand.scad 的作者手部数值当成用户尺寸。没有采用 HSK Pro 主板、螺孔或紧固件位置。** 本轮以独立的 CadQuery 球面薄壳和圆角承力筋重新建模，没有复制其 SCAD 代码或把其 STL 并入交付模型。

## paw3395-pcb — badjeff

- 仓库：https://github.com/badjeff/paw3395-pcb
- 固定提交：`b71e346fc04ef18c26e0e8638ce0333395d41a14`
- 许可证：CERN-OHL-P-2.0；完整文本保留在 `licenses/paw3395-pcb-CERN-OHL-P-2.0.txt`。
- 实际读取：`paw3395.kicad_pcb` 中的 `Edge.Cuts`、传感器 U2 封装与定位数据；另读 `README.md`、`LICENSE`。
- KiCad 外框测得 **15.45 × 28 mm**；README 取整为 **15.5 × 28 mm**，板厚 **1.6 mm**。本轮使用后者作为参考裸板包络，保守保留 0.05 mm 宽度。

该项目是传感器转接板，**不是统一的无线鼠标主板**。上游明确列有 PAW3950 选项及其元件配置差异；本轮未制造或验证该电路。传感器封装的 KiCad 放置锚点也没有被当成已确认的光轴中心或安装孔位。

本轮只采用已查到的参考裸板外框；其在鼠标内的位置，以及芯片、镜头、主板和所有其他电子包络均是预布局估计，仍待实际器件确认。

## 署名与复用边界

V0.1 的参数化源文件及打印几何是独立生成的设计，没有复制上述项目的源代码或几何。仍在此保留参考作者、项目链接、固定提交及许可证副本。上游审阅渲染图来自原 STL，只用于说明实际查看的文件，相关权利与许可证归原作者；不把它们作为本项目原创结构图。

若后续直接引入 Kotinos 的 SCAD/网格，必须保留其署名并按 GPL-3.0 处理该部分及适用的衍生作品；不能以本项目的 CERN-OHL-P 文件覆盖上游许可。若直接复用 badjeff 的源码或几何，也应保留原许可及来源通知。
