# Baseline Report

## Pi baseline without additional skills (2026-10-01)

[Full PDF report](pdf/pi_baseline_no_skills_report.pdf) / [LaTeX source](pdf/pi_baseline_no_skills_report.tex) / [Statistics](results/pi_baseline_20260927/statistics.json).

All 1,200 development and 2,400 evaluation episodes are valid, with 1,800 matched initial-state pairs. Evaluation final success is 37.00% for direct VLA and 37.83% for Pi: a paired difference of +0.83 percentage points (task-cluster 95% interval: -1.42 to +3.08). The report includes group results, false completion claims, paired gains and losses, actions, latency, estimated API costs, and audit hashes. This baseline is separate from the mature-agent comparisons below.

## 最新机器人操作 Agent 测试汇总

2026-09-16：[长程时序能力测试 PDF](pdf/robotics_agent_long_horizon_report.pdf) / [LaTeX 源文件](pdf/robotics_agent_long_horizon_report.tex)。汇总 Fixed Pi0.5、EmbodiedSkills、Thea port、RPent、Zetta 候选和 CaP-Agent0 单模型适配，共 47 条有效测试轨迹，另列 Zetta 开发数据边界。

报告以具体失败案例区分状态记忆、子目标验证、完成判断、恢复触发与执行成本；不同协议不直接排名，不把全部失败归因于长期记忆退化。各 Agent 的方法、结果与原始记录索引见 [测试入口](OPEN_PERCEPTION_AGENTS.md) 和 [统一条件三组实验](SAM3_FREE_LONG_RESULTS.md)。下列旧基线报告与历史审计继续保留，不代表这些 Agent 的最新测试状态。

## 既有模型基线报告

当前总报告：[Baseline Report](BASELINE_REPORT.md)。它取代本目录此前分散的总表，汇总 19 项既有测试，并采用统一五列：dataset、model、harness、reported performance(in paper)、our reproduced performance。

- [PDF 报告](pdf/baseline_reproduction_report.pdf) / [LaTeX 源文件](pdf/baseline_reproduction_report.tex)
- [机器可读总表与原始结果哈希](baseline_table.json)
- [统一对照协议](../BASELINE_REPRODUCTION.md)

文献及报告核查截至 2026-09-13；实验记录截至 2026-09-05。本次只重算和整理已有结果，没有新增训练或评测。PDF 文件名保持不变，已有 GitHub 链接仍有效。

主评测组合确定为 LIBERO-Plus、MIKASA-Robo（MemoryVLA 五任务协议）和 SAFE-DROID；标准 LIBERO 保留为干净控制项。MIKASA-Robo 尚未接入或复现，不能列为现有成绩。现有 Plus 分数属于含提示词混杂的旧诊断，不能作为修正协议的论文主结果。

报告正文包含五列实验总表、H1-H9 含义与执行流程，以及有提升空间的数据集说明。2026-09-14 补充 harness 的输入、执行流程、输出边界与研究位置，未修改既有实验成绩。表内及正文编号可直接打开论文或官方资源；会议数据集数量统计不纳入报告。

## 历史复现审计

下列状态与文件保留其原审计日期，用于追溯，不覆盖当前总报告的证据边界和数据集选择。

本目录按“可写入论文的证据强度”记录基线状态。仓库存在、依赖安装成功或单次前向通过，均不等同于论文结果复现。

审计日期：2026-09-05。本次实验入口见 [数据准备与基线实验记录](BASELINE_RUN_20260905.md)、[SAFE 定量记录](SAFE_20260905.md) 和 [本次数据准备](DATASETS_20260905.md)。

## 判定标准

- **L3 指标复现**：完成明确声明的数据、配置和评测协议，得到可追溯的定量指标；有限样本或固定配置必须标明，不自动代表整篇论文成绩复现。
- **L2 链路复现**：真实模型、真实环境或真实数据完成端到端执行，但尚未跑完整评测。
- **L1 工程核验**：代码、配置、数据格式或入口通过；不能作为论文数值基线。
- **L0 未复现**：关键代码、权重、数据、硬件或协议缺失。

## 历史状态（2026-09-05）

| 工作 | 状态 | 已取得的证据 | 能否作为论文数值基线 |
|---|---:|---|---:|
| OpenVLA-OFT | L3（有限协议） | 原版 LIBERO Spatial，10 任务 × 5 初始状态，50/50 成功 | 仅限本批固定协议，不是官方 500 次全量成绩 |
| AVA-VLA | L3（有限协议） | 同一批原版 Spatial 初始状态，48/50 成功 | 同上；与 OFT 的训练数据范围不同 |
| ActiveVLA | L0 | 上游仓库仅有说明和素材，代码、权重、评测仍标为待发布 | 否 |
| AHA / FailGen | AHA L1；FailGen L2 | 57 条 REFLECT 记录与图像；FailGen 完成 8 次注入并取得实际结果 | AHA 无数值结果；FailGen 是数据生成检查 |
| SAFE | L3（固定配置） | WidowX 532 条、DROID 筛选后 780 条；两域分别 LSTM、MLP 各 3 种子、1,000 epoch，独立测试与校准；DROID 另有标签异常敏感性测试 | 仅限声明的域内固定配置，不是全量网格最优或跨策略零样本迁移 |
| SAFE 距离型 / RND | L3（固定配置） | cosine、Euclidean 两域各 3 种子，共 12 组；RND 两域各 3 种子、200 epoch；加载评测、校准及 DROID 标签敏感性检查 | 固定配置，不是等计算预算或完整网格最优 |
| I-FailSense | L3（固定公开检查点） | CALVIN 单视角、作者 validation 派生 203 样本；完整模型 184/203，VLM 组件 174/203；逐例配对及指标重算通过 | 外部图像检测参考，不是主环境 OOD 或在线恢复结果 |
| ADV / VeGAS | L0 | VeGAS 作者仓库已找到但尚无可执行代码；ADV 本次仍未定位官方可执行入口 | 否 |
| WCM | L3（公开 quick benchmark） | 官方数据、episode split 与权重完成 1,617 个窗口/18 个 episode 的完整验证 | 是，仅限公开 pick-place 协议 |
| VAP-TAMP | L1 | 源码可审计；完整系统依赖 ROS2、OmniGibson、API 与实体平台 | 否 |
| Thea | L1 | 公开预览代码可审计；论文级仿真结果依赖用户提供策略与评测器 | 否 |
| Self-Harness / Zetta | L1 | Zetta 代码可审计；Self-Harness 是方法框架，缺少统一可复现数值入口 | 否 |
| LIBERO-Plus | 实现诊断 | 七维各 10 个任务的固定子集已用于策略测试；上游提示词混入扰动名称 | 不能直接作论文主 OOD 表；需先冻结无提示词混杂的协议 |
| ManiSkill3 | L2 | 三任务 RGB-D 环境通过，9 条官方动作演示全部重放成功 | 不是学习模型性能；作为第二环境的数据与生成链路 |

## 论文使用规则

L3 是进入数值对照的必要条件，不是自动进入论文主表的充分条件：还必须统一任务、输入权限、划分、预算、策略来源和评测协议。L2 可写入“系统实现与可运行性”，L1 仅用于工程设计依据或消融入口，L0 只能作为相关工作。任何后续升级都必须在对应文档中补充：代码提交、环境、数据修订版、命令、日志、随机种子和指标。

## 文件索引

- [PDF 总报告](pdf/baseline_reproduction_report.pdf)与 [LaTeX 源文件](pdf/baseline_reproduction_report.tex)
- [I-FailSense 完整模型及组件对照](IFAILSENSE_20260905.md)
- [OpenVLA-OFT 与 AVA-VLA](OPENVLA_AVA_VLA.md)
- [ActiveVLA](ACTIVEVLA.md)
- [AHA / FailGen](AHA_FAILGEN.md)
- [SAFE](SAFE.md)
- [SAFE Pi0-FAST / DROID 补充结果](SAFE_DROID_20260905.md)
- [SAFE 距离型补充结果](EXTENDED_BASELINES_20260905.md)
- [SAFE RND 补充结果](SAFE_RND_20260905.md)
- [上游发布与复现可行性核查](UPSTREAM_FEASIBILITY_20260905.md)
- [ADV / VeGAS](ADV_VEGAS.md)
- [WCM](WCM.md)
- [VAP-TAMP](VAP_TAMP.md)
- [Thea](THEA.md)
- [Self-Harness / Zetta](SELF_HARNESS_ZETTA.md)
- [LIBERO-Plus](LIBERO_PLUS.md)
- [ManiSkill3](MANISKILL3.md)
- [数据集清单](DATASETS.md)
