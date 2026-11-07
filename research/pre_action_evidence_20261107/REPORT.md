# 第一部分：研究定位、方法边界与实施

研究开题报告完善版 · 测试协议、方法路线与工程实施

版本：2026-11-07 / 研究方案 v1。基于用户原始五页报告修订；原文件不覆盖。研究主线由一般长上下文连续操作，收紧为“物理操作改变信息条件之前的证据保全”。本报告中的方法收益、学习效果和统计检验均为待验证假设，不是已经取得的实验结果。

## 1. 首先做什么，以及为什么

建议先做一个具有明确负例的最小研究闭环：同一个机器人即将关闭、覆盖、移动或交换对象时，判断后续选择依赖的证据是否仍可取得；根据判断选择继续、保存现有观察、检索、补充观察或合法重排。重点不是长摘要是否完整，而是关键决策是否仍有足够、有效、可核实的依据。

第一阶段采用 RoboMME 的公开视频/标记/交换任务研究“证据召回与当前绑定”；用 LADDER 的顺序、计数和长链操作检查通用连续执行是否退化。原生任务没有给智能体选择“先看再遮挡”的控制权时，不能据其成绩单独证明行动前联合选择。为此另设小规模 EVID-Preserve 诊断扩展，用明确的观察机会、损失动作、延迟决策和可恢复条件验证核心机制。RoboMemArena、LIBERO-PRO、RoboCasa承担跨物体、布局、目标与执行接口的迁移复核；五个平台独立配置、独立结果表。

工程实现优先 A 短证据 skill + 公共运行时，再实现 B 动作条件化的可执行证据契约，最后才做 C 离线分支反馈学习。A 是低成本可行性与规则对照；B 是主要方法候选；C 为有可靠分支环境后才开展的学习增量。不要把三个尚未验证模块一起堆上去后只报告总成功率。

## 2. 科学问题、状态定义与可证伪假设

设 h_t 为截至时刻 t 已实际返回的公开 RGB、本体状态、自然语言任务和普通工具反馈；a 为一个原执行接口可表达的候选物理动作；d 为未来某个合法决策所需的信息。历史原图和执行记录是证据来源，模型提取的语义断言是可能错误的解释，两者必须区分。

对每个 (h_t, a, d)，预测操作后的获取途径：已保留且可引用、从历史检索、重新观察、允许的物理恢复、在剩余控制/决策预算下不可获取、未知；同时预测当前对象绑定是否仍有效以及取得信息的代价。获取途径不是天然互斥类别：一个事实可能既可检索，也可重新打开柜门核实。因此宜使用多标签可获取性及条件成本，不把所有状态挤进一个互斥 softmax。

“从未看见”“看见但没有保留”“已有记录但当前绑定过期”“可重新取得”和“无法判断”应分别记录。遮挡只是可见性变化，不自动等于物理不可恢复。执行指令中写了交换，不等于交换实际完成；当前状态的失效由真实返回的证据支持或明确保留为待核实。

候选选择可从简单的有限集合开始：continue / save / retrieve / observe / reorder。save 只保存已经收到的内容，不创造观察；observe 和任何重新打开、移动对象均使用原有 view/act、占用相同决策与原生控制步预算。reorder 只能改变允许的任务执行顺序，不能改变任务目标或评分条件。

一个可检验的选择目标是：在任务推进价值相近时，最小化“后续决策错误的预测代价 + 证据获取成本 + 不必要干预成本”。初期不要求全局最优，也不声称形式化安全保证。所有代价权重在开发集冻结；正式测试同时提供多组固定权重的成本-效果曲线，不事后挑最优点。

H1：在同样可访问历史、存储容量和决策预算下，动作条件化预测，比无动作条件的检索或固定检查更能减少关键延迟决策错误。

H2：在对象身份发生可见扰动的任务中，显式绑定有效性比只保留图像或文本摘要更能降低“引用真实旧证据却支持错误当前对象”的比例。

H3：收益集中在有实际证据损失风险的场景；在无风险负对照中不应以大量额外观察换取接近零的收益。若收益仅来自更多调用、更大存储或更长运行，应否定相应机制主张。

H4：离线分支价值监督在未见任务族/操作组合上改善预测校准和后续决策；若只记住训练中的触发词或布局，则不能声称学习了可迁移的保全价值。

## 3. 现有日志提供的证据与限制

既往测试已经分别运行过原 API-loop 的 GPT + π0.5 与 Codex + π0.5，但二者上下文管理、协议版本、服务商与时间不同，不构成严格受控的“Codex优于GPT”因果比较。Codex仍由GPT模型进行推理；改变的是文件、工具、会话、压缩和执行管理的上层运行框架，并非绕过模型的认知局限。

历史 LIBERO/PRO API-loop 的48格中有46个有效布尔结果（23 True、23 False）及2个保留UNKNOWN。False中实际有5例 finish(success) 与原生评分失配，不能把所有主动结束都叫误报成功。成功轨迹中19/23存在至少10次相同指令连段，说明重复指令可能是冻结chunk策略完成动作所必需，不能把强制去重作为研究公共底座。RC的短chunk主动stuck/failure只是待归因线索，agent自述不构成底层物理失败真值。

接口层已经出现并修过部署漏依赖、宿主600秒主动关闭Codex导致stdout closed掩盖超时、工具成功回包与interrupt过早竞态等问题；这些属于公共执行正确性，必须先固定，再做方法消融。上游过载、断流、工具参数空白停滞、加密推理项兼容与压缩阶段等待曾造成UNKNOWN，不能算机器人任务False，也不能据此证明benchmark数据损坏。曾成功的任务在新的诊断运行也会遇到服务端停滞，因此成功/失败不应简单归于某一个key或数据文件。

现有五路线已有原生闭环证据，但不是五者都已有完整任务分数：LADDER有原生True，LIBERO-PRO有原生True，RoboCasa有原生有效False；RoboMME与RoboMemArena有执行接口证明，后续有限验证仍按实时原日志判定。所有结果保留原路径与版本，不把接口PASS、CLI退出码、日志增长或attempts_complete当成任务成功。

本轮配置期间的只读记录还显示，RoboMemArena一个既定验证运行达到原150次上层决策cap，原评估被PolicyDecisionBudgetExceeded中断，保留UNKNOWN；资源收尾后才接RoboMME。这是预算删失，不能算任务False，也不能靠延长决策cap补分。新实验将预算耗尽率、实际原生步数和评分覆盖率一起报告。

上述事实只支持开展更可归因的研究，尚未直接证明“压缩丢证据”是所有机器人失败的根因。新实验必须同时标注上层决策、证据采集/绑定/利用、工具交付、π执行、基础设施和预算耗尽，避免把所有失败统称记忆失败。

## 4. Coding agent 的优势应如何进入方法

Codex的优势在于能把证据组织成可版本化、可查询、可测试的外部工件：同一引用能跨原生上下文压缩保存；查询代码可以在冻结fixture上回归；每个动作可以追溯其依据；开发轨迹可以离线生成反例单测。它也适合把稳定通用代码与少量任务机制说明分开，避免把整段操作轨迹重新塞入上下文。

这些能力不等于真实感知正确。hash只证明内容一致，schema只证明字段合法，引用存在只证明来源可定位；不能证明模型识别的对象身份正确、执行动作成功或当前世界仍与旧证据一致。方法必须保留置信与unknown，并以真实后续选择和原生环境结果检验。

建议使用如下分层：公开观察适配器 → 只追加证据仓与事件索引 → Codex任务/候选动作与证据需求 → 可替换上下文插件 → 公共引用/时序/预算检查 → 原执行适配器 → 冻结π0.5 → 原环境。评分侧单独接原生结果文件，不反向提供GT、目标完成度或私有谓词给Codex。离线分支及标签工具位于开发侧，测试时关闭。

公共底座负责文件和字节引用、时间边界、不可变事件、原预算记账、数据权限、profile哈希、原始错误归类及结果聚合。研究插件负责“哪些证据未来重要”“候选动作怎样影响获取条件”“该选哪种保全行动”。前者对所有组一致并在方法实验前冻结；后者才是消融变量。

线上不开放任意Python去读模拟器或网络。Codex可以离线编写纯查询函数并在fixture上单测；线上只允许白名单查询/受限JSON契约，读取当前episode已到达的证据。默认不引入跨episode记忆、额外视觉模型、IK、运动规划器、新的抓取恢复策略或额外模型代理，以免掩盖上下文机制的贡献。

## 5. 统一实验控制与统计纪律

每个benchmark单独冻结模型名与high、实际Codex CLI/profile和原生16k压缩、πcheckpoint/norm、相机与本体字段、动作语义/chunk/频率、任务指令、seed/init、原生评分/步数与100或150上层决策预算。RoboMemArena使用已经单独授权的冻结LIBERO路线，绝不把DROID8D关节向量切成7D当成末端动作。跨平台分表，汇总时使用预注册的macro指标并保留各表，不以不同profile混合胜率替代结论。

最新用户明确取消整例墙钟上限。请求采用每个备选key最多600秒、一次逻辑请求各槽最多一次、最多七槽，按原自动轮换策略；整例没有7200/1800墙钟截断，但原native控制步数、工具/决策上限不放宽。API失败切key不重放机器人动作，不把未试槽说成失败。输出generation预算耗尽不通过换key绕过。研究方法不可把失败后重跑的最好一次当作成绩。

对核心方法做 S×H 的2×2：S是短证据skill，H是动作条件化获取预测与选择。B00两者关闭；B10仅S；B01仅H；B11两者开启。公共证据schema、文件存取、查询工具集合、原执行协议在四组完全一致。再加入Braw同容量原始检索、Breact同结构但仅事后修订、Bperiod同观察成本的固定/随机检查作为强对照；按阶段运行，不必一次付费跑完全部组合。所谓REMM/PAL/HexaShell-style若只是思路适配，必须显式标为adapted，不能称官方复现。

每个task/seed成一个配对block，组顺序随机化，开发与留出任务族/布局/证据损失组合分开。固定公共随机源和provider起始slot快照，保存实际尝试序列，避免时间段/服务商波动与某组混杂。线程/压缩/内存重置规则相同；不允许方法组免费新建无限线程延长有效预算。

任务结果同时报告：有效native SR、有效结果覆盖率、T/F/UNKNOWN原计数；有效子集SR可能选择偏差，另给全分配样本的成功下界T/N与失败上界(T+UNKNOWN)/N。任务聚类配对bootstrap给置信区间；同一episode多关键事件不能伪装独立样本。McNemar只用于配对有效布尔格，报告被排除的UNKNOWN及原因；小样本以效应量/区间为主，不追显著性。多个主要比较预注册并校正，确认集不反复调参。

主要机制指标是关键延迟决策正确率与行动前可用证据覆盖；后者需要独立标注“确实必要的证据机会”，不是模型自评。预测多标签可获取性用Brier/ECE和各途径AUPRC，成本预测用MAE/区间覆盖，缺真值不填分。记录旧绑定误用率、未观察却声称知道率、不必要检查率、恢复控制步数及每成功任务的额外观察/模型token/存储字节/延迟。把重新读旧图、新采图、物理恢复分开计。无账单或GPU利用率采集时写UNKNOWN，成功响应usage不等于全部重试费用。

## 6. 实施里程碑与停止条件

M0公共执行冻结：使用新独立目录，不修改当前正在运行的G8/launcher/source/keypool。导入本轮只读绑定、CPU事件闭环、schema与时序测试、五路线非上下文一致性检查。没有匹配的checkpoint/norm/profile/hash收据时阻止正式启动，不用占位hash假装完成。

M1测量先行：人工审阅开发集少量公开轨迹，确认原生任务确实存在可标注的延迟依赖；建立双人标注指南、分歧记录及少量裁决集。先运行无策略变化的shadow记录，不给Codex额外GT。若低层π几乎无法完成关键前缀，先报告可行性边界，不通过改变动作/权重来让上下文方法显得有效。

M2规则与强对照：只实现路线A的短机制skill，比较普通检索、定时保存/检查与事后修订。若关键机会太少或原生cue不可控，则转独立EVID-Preserve，原生结果仍保留为迁移表。

M3主要方法：实现路线B。先预测再shadow校准，确认可获取性与成本有质量，再启用联合选择。依次去掉动作条件、对象绑定、物理恢复代价及来源证据，检验各机制而非只比较总分。

M4学习与泛化：仅在可靠模拟state分支或明确配对重置可用时开发C；开发标签与测试policy严格隔离。确认集冻结后才运行，记录负结果、资源消耗和全样本覆盖率。

停止或收缩主张：若更大存储/更多观察即可解释收益，则不主张行动条件预测贡献；若只有固定规则有效，则不主张学到可迁移价值；若当前绑定不能可靠观测，则该类样本标未知；若分支恢复不可靠，不称反事实实验；若π执行失败主导，需将高层选择诊断与端到端结果分开，而不是换更强底层后继续叫同一消融。

## 7. 文件组织、迁移与本次交付边界

新研究资料、实验协议和公共底座放在独立的pre_action_evidence_20261107命名空间；旧长上下文方案转为历史参考，已有原结果、源码锁、依赖和正在运行的任务保留。GitHub使用独立研究分支与新的主README指向本方向，旧README归档；服务器不对脏的旧工作树做reset/clean/强制覆盖，另建干净研究目录和入口索引。这里只整理本研究的入口和新增文件，不删除他人或未核明的实验资料。

原始PDF保持字节不变，完善版PDF与可编辑文本另存。公共基础设施的CPU验证只能说明日志/协议/数据接线可用，不等于三条方法已实现，不等于任务native验证。核心需求识别、动作条件化预测、联合选择与分支价值学习保留为明确研发扩展点。真实机器人运行仅在已有任务自然释放资源后，按冻结协议另行选择有限验证；本轮配置工作不抢GPU、不发额外付费探针。

# 第二部分：具体benchmark、任务与指标协议

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

# 第三部分：相关工作核验与候选方法

## 研究对象与可证伪主张

研究对象是**候选物理操作改变未来证据获取条件时，如何在行动前选择保全措施**。不是一般性“大记忆”，也不是 Codex 或文件系统本身。应检验：在相同执行器、观察权限、决策与控制步预算下，行动条件化的证据获取预测是否比同容量反应式检索、定时保存或静态检查，更能支持后续正确决策，并降低必要恢复动作的成本。

把三类情况分开：①从未实际观察，不能由检索补造；②曾观察且有可追溯记录，当前只需正确召回；③曾观察但物理对象交换、容器移动或状态变化使原绑定失效，需要更新。第四类是可以重新打开/换视角恢复信息，不能仅因离开视野标成“不可逆”。预测必须相对于允许动作及剩余原生控制步数，不针对取消后的整例墙钟上限。

**建议主贡献**：动作条件化的“获取途径—绑定有效性—恢复代价”预测，加上由真实后续决策反馈驱动的保全选择；代码和短 skill 是承载这一问题的实现机制。若只有固定触发规则有效，而学习预测没有增加价值，应将结论收缩为工程方法及受控评测，不主张新的预测理论。

## 原报告九篇文献：核验及与本项目的边界

以下题名与作者在论文原站可核对；它们主要是预印本，不宜写成已获顶会录用。方法简述均限于本课题需要的范围，定量成绩不跨系统搬用。

| 工作 | 已核验重点 | 对本项目的启示与区别 | 可复现状态 |
|---|---|---|---|
| [Chameleon, v2](https://arxiv.org/html/2603.24576v2) | 控制索引的前瞻记忆；针对观察到执行之间的延迟 | “让过去对行动有用”已是明确目标；其作者也提出未来与主动感知结合。因此不能把前瞻性记忆本身称为新颖。本课题强调具体操作造成的获取条件变化 | 已读论文；本轮未核验可执行代码/权重完整性。不可称已复现 |
| [ActiveArena, v2](https://arxiv.org/html/2609.24124v2) | 主动信息获取与记忆的35任务评测 | 主动感知加记忆不是空白。本课题另测破坏信息前的取舍。当前主要 Astribot S1，不能直接当现有 DROID/π0.5 的等价适配 | 论文写明计划开放完整工具，未据此认定全套已发布 |
| [TTT-RM](https://arxiv.org/abs/2610.04701) | 有界记忆之外，用快权重保存当前上下文解释不了的历史残差 | 可借鉴“不可从当前恢复”的监督目标；直接移植 TTT 会改变策略结构/学习条件，不能列作纯上下文公平对照 | 论文已核；项目页本轮不可访问，代码可用性待核 |
| [Imagine-TAMP](https://arxiv.org/html/2609.20396v1) | 比较观察与操作方案，考虑目标可见性和操作成本 | 可借鉴非单位代价及有限候选方案；本项目不引入完整几何想象/TAMP 以免扩大边界 | 已读论文；本轮未验证运行包 |
| [BudgetPM](https://arxiv.org/html/2609.37125v3) | 根据未来需求分配外部状态检查预算 | 未来需求感知与共享预算已经有工作；本课题增加物理操作导致的历史绑定失效、重新观察/物理恢复差异 | 已读方法与实验目录；未找到可直接核实的官方代码链接，不等于断言闭源 |
| [Counterfactual Memory Audit](https://arxiv.org/abs/2609.27247) | 在核实相同当前输入下交叉历史，区分动作变化与正确使用记忆 | 应移植其因果审计思路；“换历史使动作变化”不能作为本工作成功标准，须检查该历史下正确分支及实际价值 | 论文已核；本轮未验证运行包 |
| [Automated Planning for Robotics](https://doi.org/10.1146/annurev-control-082619-100135) | 机器人规划形式与能力组合综述 | 明确已有的前置条件/效果/部分可观测规划基础，不能把依赖图或前置条件检查重新命名为创新 | DOI打开失败；出版社 PDF 检索确认题名、作者、2020年3卷417–439页 |
| [PAL](https://arxiv.org/html/2610.29329v1) | 流式观察转为语义事件和可执行子任务列表，并学习更新时机 | “先计划后执行”“可执行记忆”已存在；本课题需要证明预测证据消失比只预写子任务更有价值 | 论文声明项目含复现材料；网页本轮访问失败，未做代码/权重完整性验证 |
| [REMM](https://arxiv.org/html/2610.12710v1) | 不可变证据史与可修订任务状态分离，通过支持依赖撤销过期结论 | 可以作为反应式修订对照。其固定谓词/编译依赖及技能边界恢复不是任意物理因果发现；本课题的差别应是行动前获取条件预测与选择，而不是再造账本 | 论文写将发布实现；本轮未验证公开运行包，不称已复现 |

## HexaShell：可迁移的组织方式，不能直接比较报告分数

采用 [v3（2026-11-03）](https://arxiv.org/html/2610.23479v3) 的正式题名 *A Universal Harness for Robot Coding Agents in Simulation and the Real World*；旧版本薄壳/任务特化代码表述与当前版本应区分。[官方仓库](https://github.com/HexaFuture/HexaShell) 可访问，含 Apache-2.0 许可及源码，但尚未在本项目运行。

v3 使用通用机器人 API、循环和沙箱，任务特化主要为约一页 Markdown skill。其包含判断、流程、已验证参数、常见失败和步数成本；大部分 skill 没有代码。可迁移的是“稳定公共执行逻辑 + 短小、可审计且来自开发轨迹的特化说明”。本项目的短 skill 应改写为“需要什么证据、什么操作可能使其失效、何时补看/保存、如何确认绑定”，而非抄其抓取参数。HexaShell 有额外感知/几何与不同控制工具，完整移植会改变现有冻结 π0.5 接口；只能做带明确标签的思路适配，不能宣称官方复现或直接搬排行榜分数。

## 三条可分别尝试的具体路线

### 路线 A：短证据 skill + 公共保全运行时（先做，低复杂度）

**Codex skill 内容**：按证据损失机制写少量跨任务模板，而不是每个测试任务一本答案。模板包括 `future_dependency`（后续选择需要哪类事实）、`loss_trigger`（关闭/覆盖/交接等可能触发条件）、`required_evidence`、`binding_expiry`、`allowed_preservation` 和 `unknown_fallback`。模板不得带测试对象身份、坐标、真实目标、评分阈值或最佳任务轨迹。

**Harness**：所有组共享只追加事件文件、原图内容 hash、对象别名、来源引用、候选动作登记和原控制步统计；每次原宿主动作前调用纯 CPU 的公共接口 `propose -> assess -> selected_action -> original_executor`。A 的插件依据短 skill 返回 `continue / save / retrieve / observe / reorder` 与所引用记录。运行时只核验引用存在、时间边界、模式与访问权限，不能把模型文字或“已检查”当物理事实。未知时可正常继续并记录不确定，不设置任务无关的无限拦截。

**实现顺序**：先只日志，不改变执行；离线标注哪些触发是有效机会；再启用可控的 skill，所有真实观察仍走原 `view/act` 和原预算。保存已收到的图像不多发环境 RPC，重新查看必须计原 view/决策预算。每次决策合并证据卡和动作提案，不默认增加第二个免费模型调用。

**预期贡献强度**：可作为可运行的最小方法和学习法的规则基线；仅 A 有效时不声称学习了获取代价。消融 A 去触发、去对象绑定、定时保存、随机同成本观察，检验是否只是更多检查。

### 路线 B：可执行证据契约与证据“租约”（主要方法候选）

**Codex 产物**：由同一上层决策生成一个受限 JSON/声明式契约：后续决策需求、支持记录、适用对象别名、可能失效事件、下一步获取途径、预测概率与成本。可以离线生成并单测契约查询代码；线上仅运行经过白名单的纯数据查询，不让生成代码接触 simulator、评分器、网络或任意磁盘。

**核心状态**：事实分为历史事件和当前可修订状态。证据状态建议 `unobserved / retained / stale_binding / retrievable / physically_recoverable / inaccessible_under_remaining_budget / unknown`，其中 retained 不自动等于当前有效。对象遮挡不触发确定删除，物体交换也不能仅靠动作指令就确定发生。动作后用实际 RGB/本体与工具反馈更新置信/待核实状态。

**保全选择**：对原 skill 能表达的有限操作，预测执行后的每种证据获取途径和成本，再选择预期下游错误与保全成本较低的允许操作。避免一开始重建完整世界模型。简单可实现模型是针对可见特征的逻辑回归/小决策树 + 校准，训练仅用开发轨迹；若候选动作和证据语义由 GPT 提取，必须记录模型版本、提示、输出引用与不确定性。

**coding agent 独特优势**：证据不是挤入自然语言摘要，而是可版本管理、可差分、可运行查询和可回放测试的对象；压缩只保留文件索引及当前契约，重载来源验证而不是相信摘要。代码检查证明的是引用/时序/模式正确，不证明视觉解释正确。此边界必须写在论文中。

**关键比较**：与同结构但只在失效后修订的 REMM-style 适配、同检索容量但无动作条件预测、相同观察成本的定时检查比较；契约加技能 2×2 分解。创新成立要求动作条件预测在未见损失机制组合上有可校准质量，且改善后续决策，不只是 JSON 更整齐。

### 路线 C：离线分支反馈蒸馏“保全价值”（后续学习亮点）

在开发环境中，若官方支持可靠保存/恢复模拟状态，固定相同前缀、随机性和物理状态，分别执行 `直接操作`、`先保存`、`先观察` 或合法重排；每条分支保留相同上层总决策和原生控制步数上限。若保存/恢复不可信，退化为预注册的配对 episode，不称严格反事实。所有分支计算和付费成本都计入开发成本。

离线标注标签是后续选择正确性、所需恢复步数、原任务结果和无法恢复的原因，不是模型自报重要性。拟合 `availability(route | evidence, candidate_action)` 与 `cost(route)`，或直接拟合 `value(preservation)-value(continue)`。部署时不额外查询分支世界、真实目标或评分器，只读截至当前已到达的事件。

**迁移与风险**：由 Codex 将开发失败轨迹整理成可审计测试 fixture，自动运行纯 CPU 的契约回归；通过任务族/物体/布局留出防止把执行答案背进 skill。先 A 建立任务可测性，再 B 做机制，再 C 学价值，不一次上复杂世界模型。分支结果可以被错误低层执行污染，所以同时记录“上层选择正确但 π 执行失败”等独立标签，并报告标签不确定。

## 架构和职责边界

```text
RGB/本体/普通工具反馈（截至 t）
        -> 只追加事件与图像引用（公共、各组一致）
        -> Codex：候选子任务 + 所需证据/来源 + 候选保全操作
        -> 上下文插件 A/B/C：证据获取预测、选择
        -> 公共验证器：schema/引用/时间/权限/剩余原预算
        -> 原动作适配器 -> 冻结 π0.5 -> 原环境 -> 新观察
原评分器 -> 独立 evaluator 文件（不反馈给 Codex）
离线 evaluator/训练 -> 开发集插件版本；最终测试期间冻结
```

Codex 管理文件、证据查询、短 skill、单测和离线改进；π0.5 仍只接收原子自然语言指令和原本观察，输出原动作 chunk。不让 Codex 新写 IK、改变 chunk 或替换 motor policy。五 benchmark 用各自原生 launcher/profile；上述证据接口位于共同上层边界，不能把不同权重或观察条件混成一个受控胜率。

## 从其他领域迁移的两个明确思路

1. [HAM-VLN](https://arxiv.org/abs/2607.29600) 将决策与记忆写入放在同一模型调用，并以有界近期窗口和检索的空间图组织历史。可迁移“同回合写证据、按任务查询局部子图”，避免另开昂贵记忆 agent；本项目不引入它的 depth-grounded 世界图，因为那会改变现有观测权限。
2. [MemoNav（CVPR 2024）](https://openaccess.thecvf.com/content/CVPR2024/papers/Li_MemoNav_Working_Memory_Model_for_Visual_Navigation_CVPR_2024_paper.pdf) 用工作记忆组织保留的场景特征。可借鉴短期工作集与长期记录分离；本项目进一步要求候选物理操作下的证据获取预测，不能把层级记忆或图本身当新贡献。

## 公平对比与负结果

所有上下文组共享模型与推理强度、π权重/norm、动作接口/chunk/控制频率、公开观察、原生评分与步预算、上层决策 cap、同一 Codex 协议及压缩配置、七密钥策略。当前每密钥最多600秒且整例无墙钟上限；必须同时报告延迟、实际尝试槽位及基础设施 UNKNOWN，不以更久服务等待暗称方法能力。

工具集合/schema 对所有组一致；对照组禁用某记忆能力须显式记录，不让实验组多获得 free view、free LLM call、评分RPC 或未来轨迹。上下文选择可不同，原始可访问观察权限不能不同。重看已有图和新采集图分别计量。纯 CPU 查询及存储操作不是物理步，但仍报告时间/字节/查询次数；线上模型调用计同一总决策预算。

需要同时包含：无信息损失的负对照（不应过度检查）、从未观察的信息（检索应承认未知）、可重查与不可重查、身份绑定扰动和无扰动、短/长延迟。若只在人工预设的触发器上有效或只提高保存率却不提高正确分支，应如实报告。

本轮只提供文献核验与实现设计，没有声称这些 skill 已达到论文性能，也没有启动付费测试、修改 live worker、导入新的感知/控制模型。

# 第四部分：Codex实现蓝图

## 共同架构

```text
native public RGB/proprio/ordinary return
  -> benchmark-specific public projector
  -> immutable evidence events + original-image opaque refs
  -> Codex persistent thread (pinned CLI, same native16k compaction)
     -> task requirement / candidate action / evidence contract
     -> A short-skill or B predictor/selector (research extension)
  -> common schema / past-reference / budget validation
  -> original accepted-proposal & item/completed/interrupt gate
  -> dedicated native adapter -> frozen pi0.5 -> native environment
  -> real returned observation, appended once

native scorer -> evaluator-only result file -> offline metrics
development trajectories -> pure query-code tests / C value fitting
```

两条数据通道隔离：policy只能看已到达公开前缀；evaluator才可看离线标签/原评分。ledger ID和hash只保证引用完整，不把语义claim升级为视觉真值。五route共用证据协议，不共用动作或checkpoint。存储原图仍在服务器，通过opaque ID引用；不得把原环境info整体透传。

## 路线A：HexaShell-style短说明 + 稳定公共执行代码

可以先写三份按机制跨任务共享的短skill：`before_occlusion`、`before_binding_change`、`before_order_commitment`。每份只说明适用情形、未来依赖、必要公开证据、失效条件、允许的补看/保存/重排和unknown处理。不是每个测试task写固定动作答案。用开发轨迹编写与冻结；留出任务不能新增特化身份或脚本。

skill草案的声明式内容示例（设计说明，不是已注册的Codex skill）：

```yaml
mechanism: before_occlusion
future_dependency: identity_or_relation_needed_by_later_decision
trigger: proposed_action_may_hide_current_discriminating_cue
requirements:
  - actual_observation_ref
  - object_alias_binding_and_validity
choices: [continue, save, retrieve, observe, reorder]
unknown: report_missing_evidence_without_inventing_a_fact
constraints:
  - only_existing_public_tools
  - same_episode_decision_and_native_step_budgets
  - no_test_target_or_ground_truth
```

公共运行时不替skill猜任务答案。Codex在同一个决策提案里同时写候选动作和证据引用；额外新观察必须走原view/act。可先shadow记录，确认触发机会再启用策略。离线写出的辅助查询代码通过fixture后作为白名单函数发布，测试期间禁止在线改宿主代码。

## 路线B：可执行证据契约 + 动作条件预测

每个候选操作携带有限JSON，字段例子如下；object_alias只能由公开证据关联，不是私有sim object ID：

```json
{
  "requirement": "later_choose_the_previously_observed_object",
  "source_refs": ["e00000012"],
  "object_alias": "public_alias_3",
  "binding_status": "requires_recheck",
  "candidate_operation": "close_current_drawer",
  "post_action_routes": {
    "retrieve": {"available": "unknown", "cost_steps": null},
    "reobserve": {"available": "unknown", "cost_steps": null},
    "physical_recovery": {"available": "unknown", "cost_steps": null}
  },
  "selected_preservation": "observe",
  "rationale_refs": ["e00000012"]
}
```

分三步实现：先做离线标注与多标签获取预测；再校准预测置信与物理恢复成本；最后让selector选原工具可表达的操作。初期可用小决策树/逻辑回归，语义特征由当前Codex回合输出；不额外调用免费记忆模型。保持“预测未知”“无法取得”“没有需求”互不混同。合同检查能拒绝未来引用和非法工具，但不能据schema判定对象识别正确。

压缩前保留短索引、未解决证据义务和文件版本；压缩后由同一memory工具按引用重新读取已取得证据。证据源不变、当前完整观察不删，避免把压缩改良与偷偷降采样混在一起。对比同信息纯文本卡、可执行查询卡、去动作条件、去绑定失效及去成本模型。

## 路线C：离线分支价值 → 短skill/小预测器

仅开发侧允许固定前缀下建立分支，比较先取证/保存/重排与直接操作对后续正确决策和恢复代价的影响。snapshot/restore必须核验随机状态和物理state一致；不可靠则明确标配对reset诊断。所有分支调用和物理步数计开发成本。Codex把失败前缀整理为可运行的纯CPU回归fixture；训练只用开发任务，测试时冻结代码、skill、阈值和模型。

标签可来自完整开发轨迹，但预测特征不能看未来。上层选择正确而π执行失败的分支不可直接当负保全价值；需另记执行混杂/未知。路线C不在测试episode里偷偷试世界，不引入测试时学习权重或更多评分查询。

## 接现有Codex时的顺序

1. 服务器只读绑定现有runtime-g8的实际profile和源码/权重收据；在新目录生成公共冻结receipt，不热改旧默认入口。
2. 使用公共`EvidenceLedger`与`PublicBridge`以fixture完整检查观察→查询→提案→原执行返回；生产桥必须注入原共享Ledger，不能分出额外免费cap。
3. 用现有memory工具注册边界提供有界查询/写入；所有组schema一致。先挂shadow日志，不改变动作选择。当前离线fixture通过不等于native插件已部署。
4. 实现A或B扩展点，冻结后在独立run namespace把桥接到原已接受提案处。保留G8原item/completed+interrupt门，不用memory事件代替原tool ack。
5. 先检查代表性短任务和长链含压缩任务，再按task block运行预注册面板。基础设施错误保持UNKNOWN，动作False不因换key追分。当前live有限测试只读观察。

现成工程：`foundation/evidence_foundation.py`、`public_bridge.py`、`build_profiles.py`、`bind_deployed_readonly.py`、`paired_ci.py`。尚需研究：未来需求识别、可获取性/绑定预测、联合选择、短skill实证优化、分支价值学习和EVID-Preserve物理场景构建。后者是评测研究设计的一部分，不能把JSON模板存在当成环境已经下载并可执行。

## 官方Codex接口参考与版本纪律

官方[Skills说明](https://learn.chatgpt.com/docs/build-skills)支持把说明与脚本组织为可复用技能；[App Server文档](https://learn.chatgpt.com/docs/app-server)描述工具与turn生命周期。实现沿项目已验证的固定0.149.1协议，不因当前网页新增字段就修改原会话；任何schema新功能先核实固定CLI实际协议并做CPU闭环。研究中改变的是上下文skill/harness策略，不更换上层模型或引入额外运动工具。

# 附录A：参考文献与固定版本

核验截止2026-11-07。近期论文多数为预印本；版本、代码是否实际运行和访问限制另见 references_verified.json。以下链接是原论文、作者仓库或官方文档，不以新闻转述作方法依据。

1. Guo X, Jiang C, Kim H B, et al. Chameleon: Control-Indexed Prospective Memory for Visuomotor Manipulation. arXiv:2603.24576v2, 2026. https://arxiv.org/html/2603.24576v2
2. Li Y, Zhou E, Chen R, et al. ActiveArena: Benchmarking and Understanding Active Perception in Robotic Manipulation. arXiv:2609.24124v2, 2026. https://arxiv.org/html/2609.24124v2
3. Wang H, Zhang G, Kompella R R, et al. Test-Time Training as Residual Memory for Robot Policies. arXiv:2610.04701v1, 2026. https://arxiv.org/abs/2610.04701
4. Singha A, Kumar S, Kim Y, et al. Imagine-TAMP: Imagination-Guided Task and Motion Planning in Partial Observability. arXiv:2609.20396v1, 2026. https://arxiv.org/html/2609.20396v1
5. Di Z, Shi B, Sun K, et al. When Should Agents Check External State? Budgeting Observations for Stored Intentions. arXiv:2609.37125v3, 2026. https://arxiv.org/html/2609.37125v3
6. Zhang J, Xiang Y, Chen C. Memory That Changes Action Is Not Memory That Guides It: Counterfactual Auditing of History-Conditioned Robot Policies. arXiv:2609.27247v1, 2026. https://arxiv.org/abs/2609.27247
7. Karpas E, Magazzeni D. Automated Planning for Robotics. Annual Review of Control, Robotics, and Autonomous Systems, 2020, 3:417-439. https://doi.org/10.1146/annurev-control-082619-100135
8. Liu Q, Wang C, Li Z, et al. Plan First, Act Later: Streaming Reasoning for Executable Memory in Robot Control. arXiv:2610.29329v1, 2026. https://arxiv.org/html/2610.29329v1
9. Senthilkumaran R K, Wickramarachchi R, Oltramari A, et al. REMM: Revisable Embodied Memory for Manipulation. arXiv:2610.12710v1, 2026. https://arxiv.org/abs/2610.12710
10. HexaShell: A Universal Harness for Robot Coding Agents in Simulation and the Real World. arXiv:2610.23479v3, 2026. https://arxiv.org/html/2610.23479v3 ; 作者代码 https://github.com/HexaFuture/HexaShell
11. HAM-VLN. arXiv:2607.29600, 2026. https://arxiv.org/abs/2607.29600 （本报告只借鉴同回合记忆管理，不声称已复现）
12. Li et al. MemoNav: Working Memory Model for Visual Navigation. CVPR, 2024. https://openaccess.thecvf.com/content/CVPR2024/papers/Li_MemoNav_Working_Memory_Model_for_Visual_Navigation_CVPR_2024_paper.pdf
13. RoboMME official benchmark and IO. https://github.com/RoboMME/robomme_benchmark ; https://github.com/RoboMME/robomme_benchmark/blob/main/doc/env_format.md
14. RoboMemArena official benchmark. https://robomemarena.github.io/ ; https://github.com/OpenHelix-Team/RoboMemArena
15. LADDER official repository. https://github.com/insait-institute/ladder
16. LIBERO-PRO. arXiv:2510.03827. https://arxiv.org/abs/2510.03827
17. RoboCasa official project. https://robocasa.ai/
18. OpenAI. Codex App Server / Build skills. https://learn.chatgpt.com/docs/app-server ; https://learn.chatgpt.com/docs/build-skills （具体实验仍固定已验证CLI0.149.1，不自动采用文档新增协议）

# 附录B：工程状态与验证边界

## 已完成并可复查

- 保留原始五页报告，新增完善版PDF和可编辑REPORT.md；文献核验、任务面板与实现蓝图分别存文件，避免把未验证想法写成实验结论。
- 固定源码中逐项核对37个原生task ID（LADDER16、RoboMME10、RoboMemArena11）；PRO/RC沿现有独立入口并保留语义映射与版本绑定门。已使用过的开发身份不冒充未见测试集。
- 五路线分别生成主表六组、同内存的CORE 2×2、阶段方法配置；公共字段指纹逐路线相同，研究字段单独版本化。原RGB不削减，存储容量候选不是已确定的长图像截断规则。
- 只追加证据账本、时序与来源校验、旧memory工具字段兼容facade、必须注入原预算回调的公开执行桥、离线聚合和task-cluster配对CI已实现。
- 39项CPU测试通过（28项证据底座、4项任务矩阵、7项指标），包括旧memory schema→证据账本→原预算→执行器fixture闭环、无物理重放、claim不冒充来源事实、严格布尔/UNKNOWN及五路线配置一致性。
- 已提供独立标注指南与ESC、LMER、旧绑定误用、过度保全、Brier/ECE和成本MAE离线工具；未知标签不补False。开发CORE 2×2配对矩阵已离线生成：MME 240行、RMA 100行、LADDER 64行，全部禁止执行，不代表已启动404次测试。
- 服务器同步到独立新目录；Git研究材料在独立干净检出整理，不覆盖原有脏工作树。现有有限测试不被停止、热改或抢占GPU；本次未为研究方案另起付费测试。

服务器只读核验还确认：五条现有独立路线及新对比面板可对应，18项既有执行源码锁一致；未修改原launcher、模型或私有密钥。DROID复用此前完整内容哈希并核对文件身份未变；RMA记录已有冻结LIBERO路线、norm实际哈希和HF预期内容摘要，本次不在活任务期间重新通读大权重。该审计不是新方法的native成绩。

## 后续真正需要研发的内容

未来需求识别、动作条件化获取/绑定有效性预测、联合保全选择、短证据skill及离线分支价值学习尚未实现或证明有效。EVID-Preserve目前是协议/场景模板，物理任务资产与评分尚待构建及独立审计，不是已有官方数据集的下载完成证明。

`execution_enabled=false`是新研究插件未研发、待冻结实验快照的显式准备状态，不影响现有G8任务。绑定工具不会执行launcher；实际模型/权重/norm/动作/scorer必须从服务器当下的独立路线收据取值。未解析的组件hash不得用零值或目录名代替。公共fixture通过不是native任务分数，也不是五个benchmark都已取得完整评分。

## 文件与历史

主入口为本研究README及REPORT；旧长上下文和主动验证材料保留作历史对照，不再作为本课题主设计。已完成原True/False、UNKNOWN、源码锁、正在运行的任务和第三方基准均不删。同步收据单独记录SHA、实际目录和Git提交，避免把本文件内的设计状态误当运行状态。
