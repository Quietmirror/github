# Quietmirror L2 研究交付

**14.89g目标没有达到；不是已验证电子装配或生产版本。** 共用机械F1H通过有限几何检查与主要BODY刚度筛选，但次要抬起/安装耳刚度下降，实际打印材料、点击摩擦及寿命待测。H静态/运动采样通过，但托架装入路径尚未通过；D测量板存在17对冲突。请先读详细限制，再决定打印用途。

| 方案 | 塑料件数 | PA12理论g | PLA总耗材g | 估计时间 |
|---|---:|---:|---:|---|
| F1H | 9 | 18.99951 | 37.99 | 4h 57m 55s |
| L2_H_EST | 11 | 19.74929 | 40.55 | 5h 17m 32s |
| L2_D_EST | 11 | 19.49544 | 39.24 | 5h 7m 29s |
| L2_BOTH_EST | 13 | 20.24522 | 41.82 | 5h 27m 56s |

PA12按1.01g/cm³假设；PLA总耗材含支撑边框，通用250×210床、0.4喷嘴、0.2层。没有真实打印机配置，不直接执行验证G-code。H/D单板及合板均实际切片；一板可切片不等于可组装。

- COMMON：九件共用机械模型。FULL_ASSEMBLY_COMMON.FCStd / FULL_ASSEMBLY_COMMON_STEP.zip / COMMON_ALL_PARTS_STL.zip / COMMON_INDIVIDUAL_STEP.zip / COMMON_ALL_PARTS_SINGLE_PLATE.3mf。
- H：18×18mm紧凑传感器板是**新的定制电路需求**。实际参考15.45×28板失败另存历史，未改名冒充适配。FULL_ASSEMBLY_H.FCStd及同名前缀STEP/STL/3MF。
- D：ATK A1 Pro身份与板型均未知；36×50mm红色测量块不是实板。FULL_ASSEMBLY_D.FCStd及同名前缀文件仅作示意/诊断。
- BOTH_ADAPTER_KITS_SINGLE_PLATE.3mf：一套共用件加两组替换转接件共13件；两组不能同时装入。
- ALL_VALIDATION_REPORTS.zip：完整原始JSON、失败/收敛/质量/路径/切片报告。
- history/：43项实际候选/失败构造CAD归档，另含完整72件R3.2基准包与[恢复说明](history/README.md)。全部本地历史网格也保留；失败候选不可当打印发布版。

完整STEP保留组件身份，没有把活动件融合。FCStd为实际保存重开的具名BRep组件，参数化Python随仓库提供；没有伪称有草图建模历史或求解装配运动副。源码见[构建说明](../../cad/l2_revision/README.md)，报告见[最终对比](../../reports/l2_revision/FINAL_COMPARISON_R3_2_L2_H_D.md)、[硬件空间](../../reports/l2_revision/HARDWARE_H_D_COMPATIBILITY.md)和[二次审核](../../reports/l2_revision/SECOND_PASS_REVIEW.md)。

![实际共用模型](../../views/l2_revision/F1H/FOUR_VIEWS.png)
