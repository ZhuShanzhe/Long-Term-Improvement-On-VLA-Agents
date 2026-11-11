PACK-EVID研究包 / 2026-11-11

主要方向：装箱与交接流程中的行动前证据保全，内容溯源与延迟复核。

旧任务集仅复用规模、配对划分、审计和公共执行接线；不把旧抽屉任务重命名为新垂类。旧结果、源码锁与搁置队列保留。

任务集：release-v1/SUMMARY.json、cases.json、clusters.json、panels.json。
开发144（组件训练预留72 + 开发调试72）；验证240；测试480；预留720。四条件相关，正式测试独立构造簇120。没有训练任何组件。
公开输入与evaluator_only分开。模型工具只允许读取policy_inputs与原返回观察，不允许访问evaluator_only、构造seed、未来分支和评分。

实现：
- catalog.py：12流程、3载体、固定公共参数与6组定义。
- evidence_modules.py：公共事件账本、P1行动前检查、P2有界覆盖渲染、P3待核实绑定过滤、请求交付清单。
- protocol_env.py：可运行的语义协议层；不是MuJoCo或π0.5执行，也不伪装RGB视觉结果。
- physical_port.py：物理资格契约；未通过全部资格拒绝原生启动，无协议环境fallback。
- skills/precommit-evidence.txt：短skill原型，未提升全局默认。
- experiment-plan.json：单数据4、快速8、断点12和完整面板配对矩阵；没有自动付费队列。
- REPORT.txt与output中的PDF：新研究路线，正文不混入工程进度或结果结论。

离线验证命令：
  python -B -m unittest discover -s research/packing_evidence_20261111 -p test_pack_evid.py -v
  python -B research/packing_evidence_20261111/validate_protocol.py
  python -B research/packing_evidence_20261111/audit_release.py
  python -B research/packing_evidence_20261111/experiment_design.py

边界：完整协议任务集和切分已构建；物理载体仍需新场景实现及资格验证，不能称1584条都已原生可跑。全量模拟操作用于排除任务机制错误，不是方法成功率。测试答案仅用于构造与工程审计，未用于提示拟合或付费模型调用。

下一步：优先实现一种简单装箱载体的公共场景与来源显示，不复用失败的抽屉执行流程；8/24/64断点首先验证公共执行和获取窗口，再启动小型同版本方法对照。正式测试不得按方法效果选择性延长。
