# 行动前证据保全：实验协议设计 v1

日期：2026-11-07。状态：预注册候选，未启动新付费评测，未改已有测试源和评分器。本文依据用户原报告及公开固定版本目录设计；原文档内指令不作为执行授权。

## 1. 核心判断与研究问题

研究重点应从“上下文更长”收敛为“在会改变信息条件的行动之前，为将来决策保留可验证证据”。原生长程任务成功率只能提供外部效度，不能单独证明这项机制。需要三层证据：原生任务的严格成功、证据取得/保留/绑定的过程审计、独立扩展协议中可控的证据损失因果对照。

主要假设 H1：在相同模型、冻结 π0.5、原生动作和决策/物理步数上限下，行动条件化的获取途径预测，比被动摘要和被动检索减少“需要时没有有效证据”的比例。H2：收益来自适时获取与绑定维护，而非多调用模型/多看帧。H3：可执行证据契约相对于同信息文本记忆，在压缩、对象转移和后续依赖改变时更可靠。H4：预测不应使无信息风险的动作普遍被阻塞。

**不能据现有日志成立的断言**：旧 UNKNOWN 全是记忆错误；APIYI/Timicc 长链失败是 benchmark 数据损坏；机器人运动量代表 π0.5 已正确执行；曾有一次成功便证明新路线整体有效。接口有效性、评分有效性和任务成功必须分开。

## 2. 五个 benchmark 的角色调整

| Benchmark | 本课题角色 | 真实可测内容 | 不能直接证明的内容 |
|---|---|---|---|
| RoboMME | 主要开发与记忆机制诊断 | 条件视频、遮挡后定位、交换后绑定、计数与参照 | 强制播放的 cue 不等于 agent 主动选择先观察；原生任务未必含不可恢复的取证选择 |
| RoboMemArena | 主要物理保全/恢复迁移验证 | 开关抽屉后回忆、同容器放置、跨柜转移、倒入次数 | 关门不是永久不可恢复；部分任务最后关微波炉门并非官方成功条件 |
| LADDER | 主要长程连续操作与负对照 | 2–10 子目标、同类对象计数、relay/revisit/transfer | 原生44项不专门提供隐藏标记/一次性揭示，不作为证据损失因果的唯一主实验 |
| LIBERO-PRO | 跨初始布局/对象/目标扰动复核 | 身份/关系和目标迁移后的保全机制稳健性 | 静态任务扰动不同于执行中对象交换；不能把二者混称绑定失效测试 |
| RoboCasa | 跨环境/动作路线迁移及无害性 | 厨房容器、遮挡与长期子操作 | 普通收纳任务未必必须记忆；控制器能力可能成为瓶颈 |

因此仍保留五个独立适配入口，但开发主轴应为 **RoboMME + RoboMemArena；LADDER 做连续性与低风险对照**。不必为保持旧方案把 LADDER 的得分强行解释为行动前保全能力。五条路线分别冻结自己的 checkpoint/norm/action profile，绝不跨路线混用或合并为同一受控胜率。

## 3. 精确原生任务面板

### 3.1 RoboMME：16个真实 ID 中预先选择

开发面板（val episode 0–9）：`VideoUnmask`、`ButtonUnmask`、`PickHighlight`、`PickXtimes`、`VideoPlaceButton`、`MoveCube`。前两个观察空间记忆，第三个观察临时指代，计数作为事件证据对照，最后两个区分时间参照与底层运动/程序能力。

同任务留出：上述六项 test episode 0–19；不使用 test 选择提示/阈值。未见组合/机制留出：`VideoUnmaskSwap`、`ButtonUnmaskSwap`、`VideoRepick`、`VideoPlaceOrder` 的 test episode 0–19。前两项检验交换后旧绑定是否过期，后两项检验对象/时间参照，而非仅按当前外观选择。官方 train 每task100、val/test各50；episode固定，不能把 policy seed 重新解释为环境 episode。完整所有16项可放最终附录，不是初始开发必跑。

每次接收 `front_rgb_list/wrist_rgb_list` **全部按顺序保留**，不能只用 `[-1]` 偷删条件视频。只读公开 RGB/本体状态和自然语言 task_goal；`simple_subgoal_online`、`grounded_subgoal_online`、status、GT/seg/depth不交给 agent。官方有 joint_angle/ee_pose/waypoint/multi_choice 四入口；本研究沿已绑定的 joint_angle 路线，不换离散动作取得虚假提升。[B1, B2]

### 3.2 RoboMemArena：官方26项中的固定面板

开发 task IDs：`4_drawer_butter`（检查有物抽屉）、`5_butter_middle_drawer`（检查空抽屉）、`12_cookies_chocolate_middle_drawer`（再次放入同抽屉）、`1_cookies_tomato_basket`（顺序控制）、`6_pour_tomato_sauce_into_bowl_drainer`（两次倒入，事件计数）。

留出 task IDs：`14_cookies_chocolate_drawers`、`17_butter_chocolate_middle_drawer`、`18_chocolate_butter_cabinet`、`19_tomato_milk_orange_cabinet`、`20_cookies_chocolate_microwave`、`24_cookies_popcorn_microwave`。以官方 numeric task_id 为主，BDDL stem作溯源；有些stem与自然语言对象名不完全一致，不据文件名自动生成任务指令。各task开发 reset seeds 0–4，冻结后同任务 seeds 5–14；未见task seeds 0–14。这里是**本研究自定义分割**，不是作者官方训练/测试划分；若已用于此前开发，则标为 seen，不再宣称未见。必须由固定 evaluator 校验 seed 可解析，未校验不得启动。

官方参考是统一26-task stage-based setting；保留原 CSR/TSR、全部所需stage以及倒入任务原30步第三次倒入监测；不为了得到分数关闭 FAIL_ON_EXTRA_POUR、不添加末关微波炉门条件。模型不见官方stage oracle。本课题使用用户已批准的独立冻结LIBERO policy profile，不能与作者PrediMem训练权重结果作同配置归因。[B3, B4]

### 3.3 LADDER：明确长程负对照与迁移

开发8项：`comp_ordered_bin_2`、`comp_ordered_bin_6`、`comp_relay_2`、`comp_relay_4`、`comp_revisit_1`、`comp_revisit_2`、`comp_identical_4`、`comp_bin_6`。reset seeds 0、1。

未见组合8项：`comp_ordered_bin_4`、`comp_ordered_bin_8`、`comp_ordered_bin_10`、`comp_relay_3`、`comp_relay_5`、`comp_revisit_3`、`comp_transfer_2`、`comp_transfer_3`；reset seeds 0–7。同任务布局留出用开发8项 seeds 2–7。所有这些ID均存在于固定44项目录。注意relay ID后数字不是总子目标数：relay2/3/4/5分别为4/6/8/10个目标；以spec真实goals数分析曲线。官方44项没有官方heldout split，本文所列为自定预注册分割。[B5]

`comp_bin_1`/`comp_plate_1`是无历史依赖/低风险校准，不作为记忆收益主结果。原catalog已指出pomegranate会形成policy抓取瓶颈；长任务失误须分解，不能把所有随N下降归因于遗忘。先前采用的其他旧split保留历史，本新方案不静默覆盖。

### 3.4 LIBERO-PRO 与 RoboCasa：复核而非主证据

LIBERO-PRO精确现有适配身份：suite `libero_object_swap` / `libero_goal_swap`，各task-index `1,3,8`；开发 reset seeds `0,1`，复核 `2–9`。这是现有launcher的0-based task-index，不是新命名的语义任务；评测锁定时同时导出对应原 task_name、BDDL SHA 和 init-state ID，防止不同版本索引漂移。未完成此解析的身份保持 `catalog_binding_pending`，禁止将其计入正式任务列表。真实PRO扰动入口、原初态与原native评分保留，不用标准LIBERO冒充PRO。[B6]

RoboCasa固定原有注册ID：`ArrangeBreadBasket`、`CoffeeSetupMug`、`StackBowlsCabinet`。按服务器当前target50原catalog核对，开发 seeds `1,2`（不使用不在catalog的seed0）；CoffeeSetupMug迁移候选 seeds `3–10`，两项composite迁移候选 seeds `3–5`，并记录精确layout/style/init-state metadata。现有Coffee seed2已用于接口检查，必须标记seen而不是留出；最终留出须选从未用于方案调整的其余身份。沿当前已验证的独立RoboCasa365版本，不自动追随最新版；catalog声明包版本不冒充本轮重新安装或验证的二进制版本。三项单列保全开销/无害性，不保证都有信息风险；没有真实机会的机制指标标N/A。[B7]

## 4. 必须新增、独立命名的因果协议 EVID-Preserve v1

原生任务之外建立一组最小扩展，不能仍称官方benchmark得分。优先复用RMA抽屉/容器的原生可执行资产和同一动作接口，**不在现在的live scorer内加判断**。为每个扩展版本单独pin reset、renderer、纹理、公开instruction、原底层动作预算与scorer；各方法之间完全一致，和原生分表。

三种模板族，每族2个开发实例+2个留出实例，共12实例：

1. `EP-acquire-before-cover-{drawer,container}`：目标身份线索只在可选择的检查视角可见；cover/close后仍可恢复但需重开，或任务显式不允许重开。分别形成可恢复/不可恢复条件。agent一开始知道完整任务需求，不能依赖未来才偷偷揭示的指令；必须先观察再覆盖，模型不能读纹理标签文件。**先在固定开发样本记录原π检查动作的可行性，低层失败照常保留；不设资格筛选门，也不靠oracle替agent执行。**
2. `EP-bind-before-transfer-{drawer,container}`：先观察关系并允许保存，跨相似容器转移后需要正确对象绑定。开发为无交换；留出采用公开可见的不同移动轨迹/顺序。另设可见交换条件检验绑定过期后的重新核实，不准凭private object IDs保持神谕追踪。
3. `EP-dependency-before-reorder-{drawer,container}`：两个物理目标皆可先做，其中一个会遮住后续取证视角；改变操作顺序可保留证据。对照条件让同一遮挡与后续目标无关，测过度保全。原子取放/开关动作集合不变，不增新控制器。

开发种子每实例5个，验证10个；冻结之后留出实例每项20个新种子。以上是计划数量而非已下载官方数据；现阶段可先用离线事件夹具验证计分接口，不能宣称已有物理benchmark。既有benchmark中“要先开所有抽屉”的指令不能被改成任意开关顺序再称原生结果。

关键环境因子按pair固定：证据是否曾可见 {未取到/已取到}、旧记忆是否存在 {未存/已存}、绑定是否仍有效 {不变/可见交换}、恢复路径 {检索/重新观察/物理重开/禁止恢复}。避免把四种因素笛卡尔全量铺开；先完成最小2×2因果对照，再扩大到交换/不可恢复。开发与留出图形/容器族及候选动作措辞分离，避免模型只认“关门”关键词。

## 5. 对比组与严格相同的非研究控制

推荐主表六组，全部用同一可审计IO/schema、原生16k压缩策略、相同可见帧与工具上限、相同单条返回截断规则，不能通过不给baseline原始图像压低baseline：

- B0：原Codex原生压缩，无外部保全策略。
- B1：被动固定摘要/事件记录（相同文本预算），不预测动作后损失。
- B2：来源可追溯的被动检索/关键帧（与ours相同存储及检索容量），无主动前置取证。
- B3：固定关键动作前检查规则，例如开关/遮挡/转移前统一存证；这是重要强对照。
- Ours-S：通用执行器+短文本“证据需求/失效条件”skill，由Codex选择先看/存/查/执行，无学习的风险预测。
- Ours-SH：上述skill + 行动条件化获取途径/恢复代价预测 + 可执行证据契约门控。可学习模块仅用开发轨迹，输出未知允许放行/请求信息的规则预先固定。

核心2×2：是否需求skill(S) × 是否预测/契约harness(H)。B0/S/H/SH必须保持同一个基础内存实现以免把存储差异归因于联合机制。B1/B2/B3是额外强参照，不与2×2的不同基础内存混成同一factorial。

容量/调用对照：按相同最大返回tokens、可读图像数、存储条目/字节、总工具/决策次数约束；取证、保存、查询、重开动作都占原预算，不能“后台免费多看”。单次host纯确定性账本写入不额外调模型，作为所有组共有基础日志；方法额外查询/重推理需计数。主比较保留原评分上限，另画相同实耗工具次数/输入tokens截面的成本曲线，不能单靠更多token获益。先做固定storage容量，不把“无上限外部记忆”作为默认ours。

移植文献算法若需训练权重、额外传感器、oracle子目标或作者不同动作控制，应列为“作者完整系统参考表”，不能当context-only基线；只移植其可复现的记忆机制须明确命名port，并公开偏离项。

## 6. 指标：主结果、机制、成本

### 6.1 原生主结果与有效性

原生SR/TSR = valid native True / valid native bool数量；同时报告 coverage = valid bool / 全部预注册attempt、UNKNOWN的原因分布和保守区间 [True/N, (True+UNKNOWN)/N]。该区间不是修正后的官方SR，而是缺失敏感性范围。RMA另报原CSR。完整False保留，None不转False；不能用finish(success)当nativeTrue。

主要方法比较每episode的配对native成功差值；分别报告每benchmark宏平均、每task结果及95%CI，禁止把5个不同底层profile揉成一个受控胜率。记录同场景任务进度只取原最终结果已有字段；无原字段标N/A，不额外运行评分RPC。历史预算/协议不同结果仅诊断背景，不当新方法对照。

### 6.2 行动前机制指标（新扩展主指标）

- **Evidence Sufficiency at Commitment, ESC**：在预注册需要证据的不可逆/高恢复代价行动前，满足全部必要证据项且绑定未失效的次数 / 全部这样的实际机会。必要项由独立环境模板/盲审标注定义，模型自报不作真值；分母只统计出现的机会，同时报告可达机会率防止靠不行动刷ESC。
- **Late Missing Evidence Rate, LMER**：后续关键决策发生时因未观察/未保存/过期绑定而无有效证据的次数 / 出现的关键决策数；分别拆三类，当前信息未知不强制标错误。
- **Prospective Preservation Recall/Precision**：对确会影响后续且有保全机会的证据损失，行动前采取有效取证/保存/调序的召回；所有触发动作中真正必要的比例。没有有效取证返回不算保全成功。
- **Binding Error Rate / Stale Evidence Acceptance**：对象交换后错误沿用旧绑定的次数 / 需要绑定的决策数；引用存在不等于引用有效。
- **Availability Prediction**：对每候选action预先输出p(可当前看见/可历史检索/可重观察/可物理恢复/未知)，分别以独立标注做Brier和校准图；多途径可同时成立，不能强迫互斥五分类。代价是原生步数/工具次数而非模型主观分数，报MAE与排序相关；没有可观测标签不强评分。
- **Recovery Burden**：证据重新获取消耗的物理步数、act/view/查询次数，及从信息损失至恢复的决策间隔；与正常任务推进消耗分开。
- **Over-preservation**：无后续依赖/低风险负对照中的额外取证/存储/阻塞率；同时报任务完成与卡死率，拒绝所有动作不是好方法。

原生任务的上述机制标注从已记录公开RGB/本体/工具回包做离线双人盲审，未知不补真值。独立scorer/privateGT仅用于扩展协议离线评测的隔离通道，绝不回传agent，不在旧任务运行时加RPC。无法标注真实因果时仅报告“可见事件审计”，不能把模型解释当证据价值学习标签。

### 6.3 资源与coding-agent特色指标

报每个完成/未完成episode的：accepted decisions、实际tool次数、原生物理steps、输入/输出tokens（各case最后累计一次）、memory bytes/records、引用resolve率/错绑率、压缩前后证据引用保留率、本地查询执行时间、模型等待、每请求尝试slot数及成功供应商。HTTP重试费用不从成功usage推断；账单未知则标UNKNOWN。每key600s、整例无wall限照现行授权，walltime只测量不用于悄悄终止。相同provider/时段尽量按task block随机化组顺序，provider固定失败可轮换但必须归因；不同组不能有不同轮换策略。

额外coding指标：离线query程序单测通过率、同一证据契约复用于未见task的比例、代码/短skill长度与变更量、压缩后不用完整长文就能重建待验证义务的比率。指标不是越多代码越好；把query程序/契约的作用与同信息文本记录比较，检验coding框架优势本身。

## 7. 统计和可执行排期

阶段0：不动live测试。只做目录绑定、纯CPU schema/指标/配对manifest验证。任何尚未绑定checkpoint/scorer/task-name的route fail closed。旧有效结果永久保留；新重复身份仅在明确新方法评测namespace，不能覆盖历史。

阶段1（可行性，不作论文主结果）：RoboMME开发6项×val episodes0–2×B0/B2/B3/SH=72attempt；RMA开发5项×seeds0–2×同四组=60attempt；共132attempt，串行单GPU。只有确认公开观测包含所需cue且原π可完成关键动作，才扩展模板，不能按ours分数筛任务。若policy成功率极低，先公开判定该route是policy-floor，不以更换checkpoint假装context收益。

阶段2（冻结后主评测）：MME四未见机制×test20epis×六组=480attempt；MME开发六task同任务test20epis×六组=720attempt；可分批预算，不预称已执行。RMA六留出task×15reset×六组=540attempt。最小主表可只先跑2×2四组，强参照另补；必须在预注册中写明规模/停止条件，不见到显著就停。每个固定task/episode跨组共享初始状态和原生预算，组顺序随机化。

阶段3：EVID-Preserve留出6实例×20reset×4个核心2×2组=480attempt；B2/B3仅在相同冻结实例补跑，若资源限制预先选固定模板子集。阶段4再跑LADDER与两迁移benchmark，不先花资源全面刷5个benchmark排行榜。

这些不是功效保证。先用开发pilot估计配对不一致概率，预先据最小可解释效应（例如绝对SR+10个百分点）计算所需episode数；“每项20”只起始规划。成功率差异用task分层配对cluster bootstrap（task为重采样单位，episode在task内）95%CI；task太少同时给逐task差值/episode配对exact McNemar结果，避免bootstrap虚假稳定。主假设唯一主指标预注册，其余校正多重比较（Holm）或标探索性。至少3个独立policy采样种子是可选稳健性扩展，不能冒充3倍独立环境样本。不得只对成功episode统计机制与成本。

失败分类轴：接口/传输→无有效评分；上层错误选择/证据未取得/未保留/失效误用/调度交付→需要原图和回包支持；π执行失败→只能在目标指令正确且输入/交付完整、可见动作未达目标时标“policy/execution疑似”，无需追加oracle检查；混合与无法归因保留unknown。日志推断不能代替物理反事实。

## 8. 可反事实与不泄漏的边界

配对counterfactual最强证据来自自建扩展中同一**预行动状态**的分支：save/retrieve vs no-save，observe vs no-observe，先A vs先B；底层采样seed对齐。若引擎不支持可验证snapshot/restore，则用从reset重放的显式独立诊断，不能称精确同状态反事实；仅在离线研究通道做，费用、动作全部记录，不插入正式episode免费试错。不向agent暴露scorer/GT/privategoal，不复用从留出未来帧生成的skill/query代码。训练可用完整开发轨迹但预测特征仅截至当前，按episode/task族划分防止未来泄漏。

## 来源与核验

固定源码目录本地已只读核验：LADDER commit `d645441a716595cce2ef9fb96abf2a324dc25b21`；RoboMME `5753639d62c167ba74fa64fcce8b2f4895d08e7b`；RoboMemArena `830a31ae7c08fb99f514843275cd264a2bf36f16`。原生具体task IDs来自这些公开源码，非模型猜测。当前README不自动覆盖固定runtime。PRO的swap语义task-name/初态映射仍须在准备快照时核对；RC三项ID及允许seed已与服务器原target50核对，catalog声明rpent-robocasa365 1.0.1，实际执行仍绑定既有独立源码锁。

[B1] [RoboMME 官方任务目录与split](https://github.com/RoboMME/robomme_benchmark)。[B2] [公开IO规范](https://github.com/RoboMME/robomme_benchmark/blob/main/doc/env_format.md)。[B3] [RoboMemArena作者任务表](https://robomemarena.github.io/)。[B4] [官方reference evaluation](https://github.com/OpenHelix-Team/RoboMemArena/tree/main/evaluation_benchmark/reference_evaluation)。[B5] [LADDER composition固定任务与配置](https://github.com/insait-institute/ladder/tree/main/ladder/components/inference/robots/robolab/composition)。[B6] [LIBERO-PRO论文](https://arxiv.org/abs/2510.03827)。[B7] [RoboCasa官方项目](https://robocasa.ai/)。
