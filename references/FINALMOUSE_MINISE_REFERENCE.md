# V0.3：Finalmouse 与 Mini SE 的实际参考记录

审阅日期：2026-10-14。用户的“minise”本轮按 **Razer Viper Mini Signature Edition（毒蝰 Mini SE）** 理解。它仅用于外观方向，不替换用户的候选电子供体。

## 实际查看的资料

| 来源 | 实际读取内容 | 用于本项目 |
|---|---|---|
| [Finalmouse ULX Frostlord 官方页](https://finalmouse.com/products/ulx-frostlord) | 产品页、侧斜视产品图、官方提供的形状试握 STL 链接 | 实面侧壁、两个相邻侧键、后冠规则孔阵的分区方式 |
| [Finalmouse 官方侧斜视图](https://finalmouse.com/cdn/shop/files/frost2.png?v=1765794920&width=1080) | 下载后实际查看像素 | 侧键下方连续实面，上方和后方镂空；不复制装饰图案 |
| [ULX_Cheetah.STL 官方下载](https://cdn.shopify.com/s/files/1/2377/4861/files/ULX_Cheetah.STL?v=1706114012) | 实际载入、计算边界并本地渲染；78,060 个三角面；XYZ 包围尺寸约59.504 ×115.568 ×35.291 mm | 对照商业形状试握模型的整体结构；该文件是连续外形模型，不能用它证明内部孔阵或装配结构 |
| [Razer Viper Mini Signature Edition 官方页](https://www.razer.com/gaming-mice/razer-viper-mini-signature-edition) | 产品介绍和产品图 | 完整前主键、连续侧握区、后部多边形开放骨架 |
| [Razer 官方侧视图](https://assets2.razerzone.com/images/pnx.assets/5d3ca584c6fc5b521ff215071336973a/razer-viper-mini-signature-edition-1300x600-top-2.webp) | 下载后实际查看像素 | 侧面与后壳的实体/开孔分界，以及两个侧键的相邻位置 |
| [Razer 官方近景图](https://assets2.razerzone.com/images/pnx.assets/bc378be1de3b6f05fc596ae33671b6fe/razer-viper-mini-se-white-magnesium-alloy-chassis.webp) | 下载后实际查看像素 | 完整前主键与滚轮的局部视觉关系 |

Finalmouse 的官方 STL 本地检查尺寸与其商品页标注可能有舍入和范围定义差异。本项目不采用该模型的整体尺寸：仍使用90 ×62 ×31 mm试握基准，没有按比例缩放或布尔裁切商业网格。

## 采用的结构与没有采用的内容

- 采用“完整触面 + 后部孔阵”的分区思路。最终10个六边孔由本项目独立参数生成，孔内角半径0.9 mm，孔间平面筋距至少3 mm；实际结果见V0.3验证报告。
- 两侧在中段减少宽度起伏，不再追求明显的内凹腰和后部外鼓。侧键下面仍是连续夹持带。
- 两个独立侧键采用本项目自己的窗口、导向段和内侧限位边。只用于打印配合和触达试验，没有沿用商业产品的转轴、卡扣、开关或PCB结构。
- 没有直接采用 Mini SE 的大窗口比例。商业镁合金、复合材料和0.4 mm喷嘴FDM塑料的材料、工艺不同，不能把成品的薄壁或强度结论搬到试握件上。
- 没有加入商业商标、图案、宣传文字或装饰几何。

## 来源与许可边界

上述商业照片和官方形状STL下载到本地忽略目录，仅用于审阅；没有上传为本项目开源素材，也没有嵌入本项目几何或源码。官方提供下载并不等于给出了开放硬件再许可。本项目只保存来源链接、审阅说明以及自己的CAD和渲染。

原先的[开源CAD/STL/SCAD审阅记录](REFERENCE_REVIEW.md)和[游狼外观参考](GWOLVES_REFERENCE.md)继续有效。Quietmirror V0.3仍是独立设计，许可见[NOTICE](../NOTICE.md)和[LICENSE](../LICENSE)。
