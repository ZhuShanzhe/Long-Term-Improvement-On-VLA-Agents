# 独立离线标注与指标工具

运行：`python analysis/metrics.py analysis/fixture.jsonl --output analysis/fixture.metrics.json`。标准库，无网络、模型、模拟器、scorer、额外goalcheck。`fixture`为人工合成，绝非真实结果。CI不重复实现：原生配对比较使用 `foundation/paired_ci.py`，按task簇计算；本工具event描述统计没有独立样本置信区间。

## 输入与身份

每行都有 `benchmark, task_id, seed, episode_id, arm, kind`。`kind=episode`每身份仅一行；`kind=event`还须唯一字符串 `event_id`。不能把同一episode多个attempt挑最好一条；先按预注册attempt选择规则出清单。一次调用仅允许一个benchmark，结果按arm分开。不同protocol/profile也应分别调用，并保留外部manifest。event可附 `decision_index, public_prefix_sha256, annotation_version, annotator_ids` 溯源，不向模型返回这些独立真值。

Episode行：`valid`须精确布尔true且`native`是精确bool才计入有效评分。`valid=false,native=false`仍UNKNOWN，数字0/1不冒充bool。原生字段只读原结果，未调用终局的case不补评分。报有效bool比例、有效样本SR及缺失敏感性范围，范围不是官方SR；不能把UNKNOWN当失败或删掉。

Event行可含 `prediction`，键限 `current_view,historical_retrieval,reobserve,physical_recovery`；每键为 `{p_available:0..1|null,predicted_cost:nonnegative|null}`。多途径可同时成立。cost单位必须在该数据集manifest预先固定，例如primitive步数或tool次数，不混单位。未知不是0，不可达的无穷代价用null并另记不可达，不能塞inf。

`label_source`仅 `blinded_public_prefix` 或 `isolated_evaluator` 才参与真值计算；其余缺失/`model_self_report`一律未标注。`labels`中布尔字段都可null，拒0/1、字符串。未知不补false。

- `commitment_required`：此行动是否为预注册的取证承诺机会。true时`necessary_evidence`须非空、独立id且每项有 `observed,retained,binding_current` 三个bool/null。全部项全部true才ESC成功；任一明确false即可定不充分；否则未知。保留指当前能resolve的证据源，不要求一定复制图像。当前可见的证据可由当前源引用满足。
- `critical_decision` true时 `missing_reason` ∈ `none,not_observed,not_retained,stale_binding,unknown` 或null。前三种失证/过期计LMER；none计没有缺证。无法分离多原因时记录优先主因规则或unknown，原始复选诊断可另存但不要重复事件行。
- `requires_binding` true时，`stale_evidence_used`是是否错误地沿用已经失效的对象绑定，非“绑定旧”本身。
- `preservation_needed` false是独立认定的低风险/无后续依赖机会；`preservation_action` true表示仍额外取证/保存/重开/阻塞。分母为已标清negative机会，计overpreservation；需求未知不混入负例。
- `routes`为各route独立标签 `{available:bool|null,actual_cost:nonnegative|null}`。没有已执行重查或可验证分支，不知道恢复代价就null，不由agent自报充当真值。

输出每指标 `eligible_count`（标签确认的机会）、`labeled_denominator`、`annotation_coverage`、值；没有标签时值null。另报全event独立来源coverage。**这不估计未标记事件中的漏机会**：同时离线审计所有预注册关键时点及随机非关键时点，公布抽样与机会定位覆盖率，避免只挑ours保存过的事件。Brier/ECE按有预测且独立标签的pair算；固定等宽10bins，报各bin量，少样本ECE仅描述。cost MAE单独报告已标注pair/全部cost预测数。

## 盲审与信息隔离

1. 冻结标签本体、模板、关键时点定义后再开留出；标注员不知道arm名称、模型自述、方法最终成功与否。随机重编号。
2. 判断行动前取到什么、引用能否resolve、绑定是否已经失效时，仅展示截至该时刻t的公开RGB/本体/已返回tool记录；不得根据后来成功倒推出t已有证据。候选预测必须在action前记录，禁止后验改写。
3. “后续是否需要”和“实际恢复是否可能”可用隔离evaluator/离线完整开发轨迹建立标签，但该标签不可回流到agent或同一测试episode的skill。模型可见事件与隔离标签分目录权限，论文明确哪些指标用了未来结果。
4. 每个task/arm分层随机抽至少20%事件双人独立复核（总量小时至少20事件），所有争议和稀有高风险事件另加复核；报告一致率/Cohen kappa及争议率，第三人裁决，仍不明保留null。20%不是精度保证。
5. 图像来源的身份无法从公开轨迹确认时，不使用private object ID给agent保持追踪。离线GT可核指标真值，但必须注明isolated_evaluator，绝不作为输入。
6. 临时离开视野≠不可恢复。没有同预行动状态分支/snapshot恢复证明时，只标“已知可见/实际执行的恢复代价”，反事实可获取性/成本null。恢复失败也未必证明绝对不可达。
7. agent选择错误与π执行失败分开；缺原始反馈标unknown。工具返回success不等于物理成功。既有nativeTrue/False永久保留，标签修订另版本不篡改原结果。

此工具验证汇总语义，**不判断标签是否真实**，也不提供研究用获取性预测器或行动门控。
