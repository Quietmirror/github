# 历史 CAD 恢复说明

本目录有 43 份实际候选/失败构造的 STEP 差异归档。`R3_2_BASELINE_ASSEMBLY.zip` 另存 72 个完整 R3.2 装配 STEP，逐字节核对过原 R3、R3.1、R3.2 发布归档的继承链；没有重新生成或改写基准几何。

候选 ZIP 中的 `RESTORE_MANIFEST.json` 明确哪些 STEP 已包含、哪些沿用 R3.2。下载同目录基准包后，以下命令可以恢复完整候选，已有不同内容的文件会拒绝覆盖：

```powershell
python cad/l2_revision/restore_history.py F1H --output exports/l2_revision/F1H
python cad/l2_revision/restore_history.py R3.2 --output exports/rebuild_r3_2
```

运行目录为仓库根。恢复脚本只需要 Python 标准库；生成 CAD 和复验仍需要建模依赖。43 份候选的全部归档条目已实际恢复到内存并核对本地 STEP 字节，报告见 `reports/l2_revision/history_restoration.json`。

归档完整不代表候选通过打印或装配验收。失败版本保留其真实失败几何，不能用作已验收打印件。最终共用/H/D 模型的完整 STL、STEP、FCStd、3MF 位于上一级。
