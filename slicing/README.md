# 切片复现

已实际使用 PrusaSlicer **2.9.6** 的命令行切片器；没有连接或控制打印机。

- `PLA_0.4_0.20_ESTIMATE.ini`：可读的关键设置。
- `PLA_0.4_0.20_FULL.ini`：PrusaSlicer 导出的完整配置。
- `../exports/quietmirror_fingertip_V0.1_PRINT.3mf`：最终模型、毫米单位、脚面朝下和完整估算配置。可作为项目打开，再选择实际机型。
- `../reports/slicer_model_info.txt`：真实 STL 导入尺寸、面数、流形与实体数。
- `../reports/slice_summary.json`：实际切片器耗材与时间输出，以及按刀路类别统计的材料。
- `../views/09_slice_layers.png`：从实际 G-code 提取的四个高度截面。

设置：0.4 mm 喷嘴，1.75 mm PLA，密度1.24 g/cm³，0.2 mm 层高，4道周壁，20% gyroid填充，5层顶底，0.45 mm普通线宽；外壁25、普通周壁40、支撑35 mm/s。估算温度210°C / 热床60°C，最终温度按实际耗材和机器确认。树状支撑、仅热床、45°阈值、顶部距离0.2、XY距离0.35、3层支撑界面，4 mm外裙边。

打印方向保持 Z=0 脚贴面向下；不要倒放主键接触面。支撑主要落在主键下方、固定滚轮和轮轴下方、侧键凸台及右托边下缘。去支撑后的磨痕尽量留在内侧；底部的连续承力筋是模型本体。

下列命令中的切片器路径按本机安装位置替换；先在项目根目录创建 `.tools`。输出 G-code 只用来核对与估算，不作为未知打印机的直接生产文件。

```powershell
$prusa = 'C:\YOUR_PRUSA_SLICER\prusa-slicer-console.exe'
New-Item -ItemType Directory -Force .tools | Out-Null
& $prusa --info exports\quietmirror_fingertip_V0.1.stl
& $prusa --load slicing\PLA_0.4_0.20_ESTIMATE.ini --threads 8 --center 110,110 --export-gcode --output .tools\V0.1_estimate_with_support.gcode exports\quietmirror_fingertip_V0.1.stl
& $prusa --load slicing\PLA_0.4_0.20_ESTIMATE.ini --save slicing\PLA_0.4_0.20_FULL.ini
& $prusa --load slicing\PLA_0.4_0.20_ESTIMATE.ini --center 110,110 --export-3mf --output exports\quietmirror_fingertip_V0.1_PRINT.3mf exports\quietmirror_fingertip_V0.1.stl
.\.venv\Scripts\python.exe cad\embed_3mf_profile.py
.\.venv\Scripts\python.exe cad\analyze_slice.py
```

3MF 配置按 [PrusaSlicer 2.9.6 官方格式实现](https://github.com/prusa3d/PrusaSlicer/blob/version_2.9.6/src/libslic3r/Format/3mf.cpp) 放入 `Metadata/Slic3r_PE.config`。已另行直接打开最终3MF重新切片（不加 `--load`），核对配置与估重；结果见 `reports/3mf_roundtrip.json`。

尚未做实体打印、去支撑试验、机器尺寸补偿或成品称重。模型试握刚度、脚贴粘接后的实际共面和人体舒适度由下一步实测确认。
