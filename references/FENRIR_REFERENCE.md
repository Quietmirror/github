# V0.4 · Fenrir 系列参考与采用范围

访问日期：2026-10-14。用户提供的 `fenrir-wireless-mouse` 对应 [G-Wolves 官方 Fenrir 系列页面](https://shop.g-wolves.com/collections/fenrir-wireless-mouse)。本轮实际读取了系列、Pro、Asym 和 Max 商品页面，并下载查看了以下六张 Pro / Asym 官方图的像素。商品图的网页 alt 名称有个别与实际视角不符，以下按实际画面标注。

## 实际查看的外形资料

| 产品 | 俯视 | 拇指侧 | 右侧 |
|---|---|---|---|
| [Fenrir Asym](https://shop.g-wolves.com/products/g-wolves-fenris-asym-8k-wireless-mouse) | [01-01 原图](https://shop.g-wolves.com/cdn/shop/files/01-01_8d9efcb2-b337-4539-8924-aaf5b46eb2fe.png?v=1741744378&width=1000) | [01-01-01 原图](https://shop.g-wolves.com/cdn/shop/files/01-01-01.png?v=1741744378&width=1000) | [01-01-03 原图](https://shop.g-wolves.com/cdn/shop/files/01-01-03.png?v=1741744378&width=1000) |
| [Fenrir Pro](https://shop.g-wolves.com/products/g-wolves-fenrir-pro-8k-wireless-mouse) | [1-01 原图](https://shop.g-wolves.com/cdn/shop/files/1-01_edb7c3b2-45c3-41f5-abd6-ebcaf92076fa.png?v=1759934416&width=1200) | [1-02 原图](https://shop.g-wolves.com/cdn/shop/files/1-02_7bbb97ff-8ebc-4c8c-a057-ffcc0c7ea3c6.png?v=1759934416&width=1200) | [1-03 原图](https://shop.g-wolves.com/cdn/shop/files/1-03_a221ab27-78fd-4db7-a46f-9330fba377ca.png?v=1759934416&width=1200) |

官网当日规格分别列出 Asym 75×63×27 mm、Pro 81.7×61.2×28.3 mm。这里仅用于判断短机身和低前端的设计方向，**没有按照片反推精确曲率、PCB轮廓或孔位**。Max 页面也已读，但没有把它作为本轮几何主参考。

本轮查看到的是商业产品图片和说明，未取得 Fenrir 的可编辑 CAD / STL 或开放几何许可。没有把 Fenrir 描述为开源项目，也没有把上游图片、网格或源码嵌入本项目的模型。官方图片通过上方链接查看，版权归其权利人；本仓库原创 CAD 的 CERN-OHL-P-2.0 不覆盖它们。

## 从图片观察到的特征及本项目取舍

| 视觉观察 | V0.4 对应设计 | 原因 |
|---|---|---|
| 主键从低前端向中后部缓升 | 鼻端上缘由约22降至12 mm，键面前段降低，最高壳背移向距前端约44 mm | 降低指尖前伸时的抬高幅度；效果须实物试握 |
| 机身短，背部蜂窝明显分区 | 保留90 mm旧底部，后壳改为两排共6个较大圆角六边窗口 | 用户要求底部不变，不能照搬75/81.7 mm整机尺寸 |
| 两个拇指键沿侧上缘布置 | 保留V0.3接口尺寸及同形键帽，纵向位置不变；前/后键分别降低2.7/0.4 mm | 避开降低后的上壳，并形成轻微前低后高的触达位置 |
| 大量主键/侧壳镂空 | 主键和主要夹持区继续完整，只开后壳窗口 | 延续用户此前“按键位置不镂空”和平顺侧面的要求；FDM筋条也不同于商品材料 |
| Pro低尾边、Asym非对称外形 | 沿用右侧低托边，末端仍短低；只更新上部轮廓 | 不破坏五脚、传感器框和底部承力路径 |

这是一套受视觉特征启发、重新参数化建立的原创试握几何，不是 Fenrir 复刻，也不宣称与它的重量、握感或强度相同。电子目标仍沿用本项目需求；没有因官网传感器规格而更换用户供体假设。

## 继续保留的开源参考

olliebella、Kotinos、paw3395-pcb 的已查看源文件、提交号、署名与许可，见 [REFERENCE_REVIEW.md](REFERENCE_REVIEW.md)。V0.3 的 Finalmouse / Mini SE 资料见 [FINALMOUSE_MINISE_REFERENCE.md](FINALMOUSE_MINISE_REFERENCE.md)。这些历史审阅记录原样保留。
