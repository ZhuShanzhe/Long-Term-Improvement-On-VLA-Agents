# Codex + π0.5 实现蓝图与明确研发边界

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
