# 行动前证据保全：独立公共底座

本目录为 CPU-only 新研究命名空间，不修改 `Long-context-continuity-study-20261107-v1`、G8、原 benchmark、live source 或私有 pool。没有启动机器人、付费模型、环境或评分。预测与联合选择仅定义接口，尚未研发；配置相等、单元测试通过不等于真实任务效果通过。

## 已实现与边界

`evidence_foundation.py` 提供单宿主写入的追加账本：原公开观测、模型 claim、失效事件分开，宿主分配顺序和 ID，引用只能指向已存在前缀；历史不可被 claim 改写，过期不删除原记录。原图只接受宿主注册的 opaque asset ID，不打开路径、网络或机器人。哈希链检查篡改，不证明视觉事实为真。观察文本仍需原 adapter 严格投影白名单；仅靠字段校验无法判断调用方是否把 oracle 或秘密写进 text。账本不是并发多写者数据库，若需要并发写入须通过单 host writer。

`AvailabilityPredictor.predict(public_prefix, candidate_action, future_requirement)` 和 `PreservationSelector.select(...)` 是待研发扩展点。它们只看截至当下的公开前缀，不接触 scorer/GT。可获取性输出应分别描述 retrieval/reobserve/physical-recovery 的 `available/unavailable/unknown`、证据引用、预测成本与置信度。不得把未观察记成已知、不得把历史身份绑定当当前真值。这里不实现固定规则冒充学习或联合规划贡献。

各配置提供五条独立路线；每条路线内 `common` 指纹一致，各路线不混用模型、权重、norm、动作、chunk、评分或 horizon。公共参数是实际最新规则：CLI0.149.1 / native16k、每 key 600秒、最多7槽各一次、无整例墙钟限制、保留原150/100决策及原评分步数、无 extra goalcheck/物理重放。memory/query/write与act/view共享原工具决策cap，不能在桥外配置免费记忆账本；原当前RGB/本体不降采样、不删帧。无新模型调用免费预算。旧公共配置的共享600及7200/1800墙钟字段不能复制成新有效配置。

容量字段16MiB是**待预注册的元数据/引用存储候选**，不是已批准的长RGB存储上限；原始RGB保留不受该字段截断。须先按长程预期作容量预检，在同一面板全组冻结后才启用。不得以此字段删原图或拒绝原当前观察。4096byte历史读出候选与原当前图也必须分开计量；如原冻结profile不同，先统一配置审批与记录，不能静默降低baseline观察。

## 三种比较面板不得混用

- `configs/<benchmark>-MAIN_COMPARISONS.json` 是**报告主表**：B0_native / B1_summary / B2_retrieval / B3_fixed_precheck / Ours_S / Ours_SH。它比较native、摘要、检索、规则检查、skill和skill+harness整体方案，不能从中单独归因S/H贡献。
- `configs/<benchmark>-CORE2x2.json` 是**因果核心消融**：S0H0 / S1H0 / S0H1 / S1H1，四组相同provenance基础内存、相同检索和容量、相同工具schema及训练制品，仅context skill、可获取性predictor、selector开关变化。S=证据需求与行动前保全skill，H=预测与联合选择harness；H单开允许generic默认需求，不偷偷注入S文本。
- `configs/<benchmark>-six-arms.json` 是**早期阶段研发方案 staged-methods**，不是主表；下表B编号仅限该面板。B5学习制品是后续训练研究，不是主表现成组。`COMPARISON_FAMILY_MAPPING.json` 明确映射及不可等同项。不得把同名B编号或旧C0..C5历史结果自动挪到主表。

以下仅为 staged-methods（非主表），可在预注册前统一更名；不是原 C0..C5 的直接后续成绩：

| 组 | 唯一研究变化 | 当前状态 |
|---|---|---|
| B0_native | 无外部证据策略 | 模板 |
| B1_retrieval | 来源可追溯历史检索 | 模板 |
| B2_fixed_precheck | 固定行动前检查规则 | 模板 |
| B3_predict_only | 预测可获取性，禁用联合选择 | 扩展未实现 |
| B4_joint_preserve | 同预算的预测+联合保全选择 | 扩展未实现 |
| B5_joint_learned | 加入开发集分支代价学习 | 扩展未实现 |

所有组注册同一工具 schema，动作/view原接口不动，memory调用计入原150/100 cap。固定文本/能力上限应在新组间共同冻结；方法技能差异单独版本化。跨 benchmark 报表分开，PRO/RC保留Sol，其他保持Astra。RMA冻结独立LIBERO，不拿DROID8维替代OSC7。

## 新方案接线顺序

1. 从实际服务器已冻结G8逐路线 receipt 提取 checkpoint/norm/physical_tool_schema/native_scorer/native_adapter/planner_prefix/execution_protocol 的 SHA256，填到**新副本** `required_bound_hashes`。当前 null 明确不允许激活；不得从目录名称猜哈希。source receipt应另含 source paths 与版本，不放key值。
2. `prepare-binding` 核对全部七类组件、benchmark与receipt完全匹配；输出只能是prepare-only请求。真正启动必须通过现有各benchmark专用launcher/精确PID与锁检查。此工具不会偷偷执行 launcher，也没有 `--execute` 后门。
3. 原公开工具返回 → host白名单投影 → ledger.observe；Codex语义解释 → ledger.claim；新公开观察否定当前绑定 → ledger.invalidate。把账本查询结果作为原memory工具有界返回，不增加视觉模型、图像、动作或额外回合。宿主时间与 tool_call_id 由原返回绑定。
4. 在单个新快照里实现预测器/selector并接在原工具提案前。先离线回放已公开前缀做契约测试，后单独显式准备新run，原live任务不热改。新增先看/检索/保全动作只能调用现有工具、进入同一ledger决策cap。
5. `scenario.template.json` 填真实原生ID、split、seed和可观察依赖。原生不支持的隐藏标记/交换/封箱任务必须成为独立扩展协议，不能冒称原benchmark任务或混入其原生评分。

## 离线统计

原始结果规范化成 `case_result.template.json` 形状，逐行JSONL。只有 `valid is True` 且原 `native` 严格bool才记T/F。缺失/无效False是UNKNOWN；integration-only剔除。相同case重复记录直接拒绝，必须在导入时显式选择最终attempt，不按最高分选。当前case_id应包含attempt，分析配对时另按task/seed/arm配对；原有效baseline不被新attempt替换。

`aggregate` 统计有效覆盖率、原native成功率、行动前保全率、后续决策准确率、过期证据使用数与恢复步数；来源是独立离线标注，不是模型自述。没有eligible loss标签时保全率为null，没有未来决策时准确率为null。成本缺测计入resource_missing_cases，合计只表示已测样本，不当作全体成本；每case usage只取最后累计一次，不是账单。bootstrap/paired CI、可获取性标注可靠性、反事实因果收益需实验分析另实现，不能拿这些描述性计数替代因果结论。

policy进程不得读取带 `offline_labels` 的case结果、分支未来、scorer或完整env.info；评价数据放独立目录和进程权限，路径不能注册为public_asset。

`paired_ci.py` 提供离线 task-cluster bootstrap：输入每个预注册task/seed/episode/arm一行终局（未执行或失联也写valid=false/native=null），两组按相同task/seed/episode配对。同一benchmark单独统计，先求每task内配对差，再对task等权宏平均，固定seed20261107、默认10000次重采样task；不把动作/证据事件或同task多个seed当独立cluster。CI仅针对完整有效对，同时输出完整对覆盖率，以及所有预注册对UNKNOWN取0/1的敏感性上下界。少于2个有效task不输出CI，少task仅探索结果。遗漏双方都无结果的预注册格无法从日志推断，导入器必须补null行，不能只导入成功格。它不修复选择性缺失，也不是可获取性因果学习验证。

```text
python -B paired_ci.py OFFLINE_PREREGISTERED_CASES.jsonl --reference S0H0 --target S1H1 --seed 20261107 --resamples 10000
```

## CPU验证命令

`public_bridge.py` 是可注入原 executor / 原公开 projector 的无策略桥，fixture 已走通 `observation → ledger → bounded memory_query → original proposal record → executor stub → returned observation`。它不替换现有 host 完整提案/成功 item/completed/interrupt ack 门；只有已被原 host 接受的提案才可进入。一次原 call_id 派发前先登记，异常也不重发动作。query与act共享同一决策账本；返回观测不是额外模型调用。**生产构造必须传 `original_charge(tool_name)` 回调**，由原共享 ledger 唯一扣费；不传即拒绝构造，不会自己分配第二份cap。该回调耗尽时必须原样抛错，在派发前停止。仅显式 `fixture_mode=True` 才允许本地cap合成计数。host已有扣费时接线只保留一个实际扣费点，禁止重复扣费或用no-op回调绕过。

`memory_tool_facade.py` 提供与旧工具**输入字段同形**的 `.call(name,args) → inputText` facade：`memory_query(query,sql,params)`、`memory_write(text,entity,attribute,value,evidence_ids,supersedes)`。构造须传显式 `tool_schema_ref`，核对inputSchema完全匹配；`original_memory_schema_reference.json` 从旧工程纯 `tool_specs()` AST提取，未导入或执行旧runtime。新副本可用该facade替换memory seam，现live不接线。检索是确定性有界词匹配，最多64条/2048字节单次、4096字节每原决策、4read/1write；所有尝试包括非法SQL均扣原工具预算。SQL与非空params明确拒绝，没有eval、文件、网络或动作能力。写入必须引用本episode已存在的**原公开observation**，不接受claim作为事实证据；supersedes只使旧current-state claim失效，不撤销原观测或历史。confidence=null表示未知、不伪造校准概率。写入结果不证明语义真值。只做公共接线，不实现预测或联合选择。

生产宿主应在原policy决策开始时调用 `facade.begin_decision()` 一次；key重试/压缩不得重置工具或读出预算。新/旧事件ID空间不得混接，必须由新副本从原观察重新登记并把新ID hint交同一Codex；不能把旧claim ID当新原观察。新输出是兼容inputText envelope及工具inputSchema，具体row字段为新证据协议，不宣称旧返回内容字节等价。

`bind_deployed_readonly.py` 读取实际 `runtime-g8/common-bound.json`、该 benchmark 的已准备 `profile.json` 和显式 component-map；只按 JSON key path 取已有 SHA，不导入 runtime、不加载 checkpoint、不读 private config。核对无整例墙钟/每key600、原模型及七类实际绑定哈希，然后在**不存在的新目录**输出 `frozen_receipt.json`、`six-profiles-bound.json`、`prepared-launch-requests.json`；不会改原G8/handoff、不会launch。component-map 是每个组件到实际 receipt 的键路径，例如 `{"checkpoint":["robot","checkpoint_hash"], ...}`；示例路径不是对实际字段的猜测。实际receipt未记录相应hash时必须先由宿主针对原文件产生可靠绑定，不能用全零/目录名代替。六组研究字段可在root方案预注册前统一改名/替换；不得改变common。

```text
python -B bind_deployed_readonly.py --common-bound ORIGINAL/runtime-g8/common-bound.json --route-profile ORIGINAL_CASE/profile.json --component-map REVIEWED_COMPONENT_MAP.json --six-profiles configs/LADDER-six-arms.json --output-dir NEW_NAMESPACE/LADDER-frozen
```

在仓库根运行（Windows）：

```powershell
D:/anaconda3/python.exe -u -B -m unittest discover -s research/pre_action_evidence_20261107/foundation -p test_foundation.py
D:/anaconda3/python.exe -u -B research/pre_action_evidence_20261107/foundation/build_profiles.py
D:/anaconda3/python.exe -u -B research/pre_action_evidence_20261107/foundation/evidence_foundation.py validate-six research/pre_action_evidence_20261107/foundation/configs/RoboMemArena-six-arms.json
```

Linux使用同等Python3解释器。标准库，无第三方安装/下载/模型。24项测试覆盖日志篡改、未知/过期/历史分离、未来引用、特权字段与路径拒绝、五路线×主表/阶段组/CORE2x2非上下文一致、核心内存一致、动作/预算漂移、跨路线绑定、未解析哈希禁止激活、严格bool/UNKNOWN/接口诊断与成本口径、完整公开fixture闭环及原receipt只读绑定/禁止覆盖、task-macro配对CI/固定seed/UNKNOWN敏感范围/拒绝重复与跨benchmark混表、旧memory输入schema→新证据账本→原共享扣费、claim不能冒充原证据、SQL拒绝仍扣费、生产缺共享扣费拒绝构造、memory耗尽原cap后阻止动作派发。真实环境接线效果尚未运行，不生成native分数。
