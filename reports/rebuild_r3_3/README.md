# R3.3 / r3_3 设计与验证

R3.3 对应 L2 研究提交 `4bce8639f48f880ffa490caaed50b67829bd5343`，本次按用户指定名称纳入 R3 系列并发布到 main。几何、材料假设、电子估计包络和已有检查结果没有改变。工程内部编号和原始报告保留，避免将重命名当作新一次建模或验证。

- [质量与切片完整对照](../l2_revision/FINAL_COMPARISON_R3_2_L2_H_D.md)
- [二次工程审核与未通过项目](../l2_revision/SECOND_PASS_REVIEW.md)
- [侧键设计与候选比较](../l2_revision/FENRIR_SIDE_KEY_REDESIGN.md)
- [H / D 空间及接口边界](../l2_revision/HARDWARE_H_D_COMPATIBILITY.md)
- [ATK A1 Pro 待测尺寸](../l2_revision/DONOR_A1PRO_MISSING_MEASUREMENTS.md)
- [实际单板切片与支撑](../l2_revision/PRINT_SLICING_VALIDATION.md)
- [BOM 与装配顺序](../l2_revision/BOM_AND_ASSEMBLY_INSTRUCTIONS.md)
- [本次版本打包检查](package_checks.json)

共用九个打印件通过已记录的实体、网格、静态与有限运动采样检查。共用塑料约 18.99951 g PA12，比 R3.2 增加约 0.30777 g，14.89 g 目标没有达到；抬起与安装耳工况刚度分别下降约 3.25% / 2.79%。H 静态及运动采样通过，但托架装入未通过；D 估计板存在 17 对干涉。打印公差、点击回弹、疲劳、真实板卡、光学高度、无线功能及续航未完成实测。

R3.3 的完整工程验收状态仍为 `false`。本次 `package_checks.json` 只确认重命名发布的文件与原产物一致、归档可读取以及打印件数量正确，不扩大任何工程结论。

保留原项目 [LICENSE](../../LICENSE)、[NOTICE](../../NOTICE.md) 与 [R3.2 署名](../rebuild_r3_2/NOTICE_R3_2.md)。本次没有引入新的第三方几何或修改许可证。
