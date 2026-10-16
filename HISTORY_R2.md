# R2 续接与历史保存

| 阶段 | 来源 / 状态 | 保存位置 |
|---|---|---|
| V0.1–V0.9 | 原 Quietmirror 指握鼠标系列；上一轮主分支为 `65d2ee671d70bcb294c66902392cb64b8058e74f` | 原 `cad/`、`exports/`、`views/`、`reports/`、`references/` 和 [HISTORY.md](HISTORY.md) 保留；[V0.9 原首页](README_V0.9.md) |
| Fenrir / MiniSE R1 | `ht1580/Quietmirror-mouse` 的 `rebuild/fenrir-minise-r1`，提交 `07fcd46dc8b719804473313ddc0c5f36acd422a9`；原始未验收状态 | [原提交](https://github.com/ht1580/Quietmirror-mouse/tree/07fcd46dc8b719804473313ddc0c5f36acd422a9)及[R1 原始快照 ZIP](releases/Fenrir-MiniSE-R2/R1_07fcd46_UNACCEPTED.zip) |
| R2 | 根据分享记录续接、修正真实干涉和装入次序，补齐交付与验证；待实物校准的机械样机 | [当前报告](reports/rebuild_r2/README.md)、[源码](cad/rebuild_r2/)、[下载](releases/Fenrir-MiniSE-R2/) |

R1 ZIP 由 `git archive` 按上述提交生成，包含当时的 `cad/rebuild_r1`、`reports/rebuild_r1`、`views/rebuild_r1`、`exports/rebuild_r1`、LICENSE 和 NOTICE.md，共 133 个归档条目。它保存旧结果，不将其失败记录包装成 R2 验收。

R2 发布以原 Quietmirror/github 主分支为父提交，只增加新版目录、此说明与原首页快照，并更新首页入口。旧版本文件的 Git blob 会逐项核对，保留结果见 `reports/rebuild_r2/history_preservation.json`。

分享记录将新一轮改为 Fenrir Pro 比例的独立重建。它不是在 V0.9 原底框上继续小改：新主壳布局 +8%，但五脚和功能界面独立锁定；两种电子方案待取得实物尺寸后再适配。因此不应把 V0.9 的尺寸、行程、电子包络或验证结论套用到 R2。
