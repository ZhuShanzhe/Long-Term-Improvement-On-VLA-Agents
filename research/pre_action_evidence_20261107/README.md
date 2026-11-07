# 行动前证据保全：当前研究主线

这里是独立的新研究包，不是当前测试 runtime。原始开题PDF保持不变。

阅读顺序：`REPORT.md`（完整完善版）→ `design/benchmark_protocol.md`（任务、指标、分割）→ `design/methods_and_related_work.md`（三条技术路线与文献差异）→ `foundation/README.md`（可运行的公共基础设施与研发扩展口）。`artifacts/`提供定稿PDF；`design/task_panel.proposed.json`包含预注册候选任务。

建议先做短证据 skill 和行动前获取条件预测，使用公开证据及原执行器；不新增运动控制器、不读取oracle、不把接口PASS当native任务分数。RoboMME和RoboMemArena主测机制，LADDER作长程连续性/低风险对照，PRO及RoboCasa做迁移。新增 EVID-Preserve 是独立拟议协议，尚未建成物理benchmark。

## 公共底座与研发边界

已提供标准库实现的追加证据账本、来源/时序校验、公开事件桥、冻结profile、离线聚合、任务与结果模板、CPU测试及只读服务器绑定。可获取性预测器、联合选择器、短机制skill内容与离线分支学习是研究研发项，不因配置模板存在而称已经实现。

本目录不自动执行原launcher。所有模型、冻结π权重/norm、原动作/观察、chunk、原生评分和上层决策/控制步预算按各benchmark独立绑定；每key600秒、七槽各最多一次、整例无墙钟截断。新增策略不得在现有活worker上热改。

## 再现

```text
python -B -m unittest discover -s foundation -p test_foundation.py
python -B foundation/build_profiles.py
```

命令以本目录为cwd。测试是CPU/fixture，不加载权重、评分器、模型key或机器人，也不声称方法成绩。

## 历史与清理原则

旧长上下文方案与旧主动验证方案作为历史参考，不再作为本课题主方案。原结果、源码锁、运行入口、依赖和已开始测试不可删除/搬移/覆盖。新目录与Git研究分支提供主入口；旧服务器工作树有未提交工作，保持原样。禁止上传私钥、API key、原HTTP、图像、checkpoint、数据集或整个第三方仓库。

源码与论文引用见`design/references_verified.json`及`design/sources_benchmarks.json`。文献的“已访问”不等于其代码已经在本框架复现。
