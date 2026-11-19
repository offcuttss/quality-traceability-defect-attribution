# FDE阶段成果与追溯

项目：质量追溯与缺陷归因
练习：bab8fc34-a451-4ade-91f6-8ad7cfd9405d

- 报告 REPORT-90f2a175-a564-4383-8d91-c6750ae7f596 v1：星衡精密 · 业务需求发现报告

## 业务挖掘 · stale

成果：ART-4701899f-775f-4d3f-bc09-40863a9c1610 v1

输入：REPORT-90f2a175-a564-4383-8d91-c6750ae7f596 v1

围绕质量追溯与缺陷归因整理业务挖掘。以下为基于已保存输入的待完善草稿。

### 业务机会清单

上游输入：星衡精密 · 业务需求发现报告 v1：现有事实已覆盖目标、流程、验收、权限、数据口径与一线操作约束，可形成若干待验证需求假设。最值得优先验证的不是“AI 归因”本身，而是返工换批号导致的追溯断链与批次/机台信息缺漏，因为它同时影响返工率、缺陷定位时长和错误放行风险；其次是数据口径与人工兜底边界。当前缺少各节点等待/处理时间的分项测量、试点两类零件的具体范围、误判样本归类与回退规则，以及快照保留与重连确认责任，均需访谈补齐。

本步整理：收集最近一次异常事件，区分客户提出的功能和真正要改善的业务结果。

待明确：哪个具体事件触发了需求？如果维持现状，会产生什么损失？
边界：只读核对与人工交接；合成训练不代表真实授权、业务执行或客户验收

引用：manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f44、manufacturing-quality-f01、manufacturing-quality-f10、manufacturing-quality-f13、manufacturing-quality-f14、manufacturing-quality-f12、manufacturing-quality-f51、manufacturing-quality-f31、manufacturing-quality-f33、manufacturing-quality-f50、manufacturing-quality-f53、manufacturing-quality-f30、manufacturing-quality-f32、manufacturing-quality-f05、manufacturing-quality-f52、manufacturing-quality-f40、manufacturing-quality-f41、manufacturing-quality-f22、manufacturing-quality-f45、manufacturing-quality-f23、manufacturing-quality-f25、manufacturing-quality-f34、manufacturing-quality-f35

### 指标基线与价值假设

上游输入：星衡精密 · 业务需求发现报告 v1：现有事实已覆盖目标、流程、验收、权限、数据口径与一线操作约束，可形成若干待验证需求假设。最值得优先验证的不是“AI 归因”本身，而是返工换批号导致的追溯断链与批次/机台信息缺漏，因为它同时影响返工率、缺陷定位时长和错误放行风险；其次是数据口径与人工兜底边界。当前缺少各节点等待/处理时间的分项测量、试点两类零件的具体范围、误判样本归类与回退规则，以及快照保留与重连确认责任，均需访谈补齐。

本步整理：定义指标分子、分母、时间窗、样本来源和测量责任人，缺失数据列为待采集。

待明确：现状耗时、返工和错误如何计算？哪些数字还只是估计？
边界：只读核对与人工交接；合成训练不代表真实授权、业务执行或客户验收

引用：manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f44、manufacturing-quality-f01、manufacturing-quality-f10、manufacturing-quality-f13、manufacturing-quality-f14、manufacturing-quality-f12、manufacturing-quality-f51、manufacturing-quality-f31、manufacturing-quality-f33、manufacturing-quality-f50、manufacturing-quality-f53、manufacturing-quality-f30、manufacturing-quality-f32、manufacturing-quality-f05、manufacturing-quality-f52、manufacturing-quality-f40、manufacturing-quality-f41、manufacturing-quality-f22、manufacturing-quality-f45、manufacturing-quality-f23、manufacturing-quality-f25、manufacturing-quality-f34、manufacturing-quality-f35

### 项目章程与利益相关者地图

上游输入：星衡精密 · 业务需求发现报告 v1：现有事实已覆盖目标、流程、验收、权限、数据口径与一线操作约束，可形成若干待验证需求假设。最值得优先验证的不是“AI 归因”本身，而是返工换批号导致的追溯断链与批次/机台信息缺漏，因为它同时影响返工率、缺陷定位时长和错误放行风险；其次是数据口径与人工兜底边界。当前缺少各节点等待/处理时间的分项测量、试点两类零件的具体范围、误判样本归类与回退规则，以及快照保留与重连确认责任，均需访谈补齐。

本步整理：明确业务发起人、使用者、出资者、审批者，记录访谈授权与调查边界。

待明确：谁承担结果？谁批准范围、数据访问及继续或停止？
边界：只读核对与人工交接；合成训练不代表真实授权、业务执行或客户验收

引用：manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f44、manufacturing-quality-f01、manufacturing-quality-f10、manufacturing-quality-f13、manufacturing-quality-f14、manufacturing-quality-f12、manufacturing-quality-f51、manufacturing-quality-f31、manufacturing-quality-f33、manufacturing-quality-f50、manufacturing-quality-f53、manufacturing-quality-f30、manufacturing-quality-f32、manufacturing-quality-f05、manufacturing-quality-f52、manufacturing-quality-f40、manufacturing-quality-f41、manufacturing-quality-f22、manufacturing-quality-f45、manufacturing-quality-f23、manufacturing-quality-f25、manufacturing-quality-f34、manufacturing-quality-f35

需求：
- REQ-1 返工换批号导致追溯断链是首要瓶颈，应优先建立原批号强制关联与断链拦截；负责人工艺工程师（唐映秋）牵头，质检员配合；验收先取近三个月返工换批号的实际单据样本，核对断链比例；与唐映秋、林亦舟确认返工节点是否可强制关联原批号及确认动作归属。验收以两类试点零件批次追溯完整率99%、错误放行为零为门槛，人工确认点由工艺工程师与产品安全负责人共同签核。；依据manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f44、manufacturing-quality-f01
- REQ-2 检测表手写再录入造成批次与机台信息缺漏，应验证就地录入与草稿暂存；负责人质检员（林亦舟）配合质量数据工程师；验收在一条产线用现有终端做小范围并行试点，记录录入、核对补漏、便签二次搬运三类耗时；与秦芮对齐统计口径（按批次还是检验单、计时起点）。人工确认点：质检员确认草稿同步状态，工艺工程师确认说明挂接字段。；依据manufacturing-quality-f10、manufacturing-quality-f13、manufacturing-quality-f14、manufacturing-quality-f12、manufacturing-quality-f51
- REQ-3 数据口径不统一（单位、公差版本、校准状态、统计分母）会直接污染归因与验收；负责人质量数据工程师（秦芮）牵头，客户质量经理参与；验收先列QMS、MES、量具采集软件的批次/机台/检测记录主键映射与状态口径清单，再定试点指标分母与排除规则。人工确认点：秦芮确认字段口径，叶书确认对外解释口径，顾明岚确认验收基线。；依据manufacturing-quality-f31、manufacturing-quality-f33、manufacturing-quality-f50、manufacturing-quality-f53、manufacturing-quality-f30、manufacturing-quality-f32
- REQ-4 异常定位辅助与追溯清单须限定为辅助，不自动认定根因或放行；负责人产品安全负责人（傅景）把关，质量总监推动；验收与傅景逐字段标注追溯清单的辅助信息与须签核项，形成权限矩阵草案；用历史资料回放验证不触发自动放行。人工确认点：产品安全负责人签核边界，客户质量经理确认对外可用字段。；依据manufacturing-quality-f05、manufacturing-quality-f52、manufacturing-quality-f40、manufacturing-quality-f41、manufacturing-quality-f22
- REQ-5 人工兜底与审计留痕需可重建处理链，而非模糊提醒；负责人产品安全负责人（傅景）与工艺工程师共同确认；验收用历史资料回放构造换批号、版本冲突、接口中断三类场景，检查留痕字段是否足以重建处理链。人工确认点：傅景确认审计字段完整性，唐映秋确认交接确认动作。；依据manufacturing-quality-f44、manufacturing-quality-f45、manufacturing-quality-f23、manufacturing-quality-f25
- REQ-6 接口中断与数据过期需以带时间戳快照和待刷新标识兜底；负责人质量数据工程师（秦芮）；验收在并行试点中模拟单套与多套系统中断，验证快照时间戳与待刷新标识是否被一线正确理解。人工确认点：秦芮确认补齐与去重规则，林亦舟确认现场可读性。；依据manufacturing-quality-f34、manufacturing-quality-f35、manufacturing-quality-f30




遗留项：书面Brief、行业可行性与现场测量是否已经核对？；本阶段责任人应补齐具体决定、执行证据与未解决事项。

确认：{"status":"待确认"}

## 现场调研 · missing

待生成；输入不足时先返回上游补齐。

## 需求定义 · missing

待生成；输入不足时先返回上游补齐。

## 方案设计 · missing

待生成；输入不足时先返回上游补齐。

## 构建集成 · missing

待生成；输入不足时先返回上游补齐。

## 测试评估 · missing

待生成；输入不足时先返回上游补齐。

## 客户试点 · missing

待生成；输入不足时先返回上游补齐。

## 上线交接 · missing

待生成；输入不足时先返回上游补齐。

## 运营迭代 · missing

待生成；输入不足时先返回上游补齐。

## 需求如何归纳

先从已采集事实形成问题假设，再约定业务结果、范围、失败控制和验收。缺少的来源标记待补，不能把六人访谈完整率当作四来源收敛或需求确认。

### 业务流程拆解

要回答：问题发生在哪一步，为什么要这样划分智能体？

1. 先画人工现状泳道，写出触发、输入、8–15个处理步骤、交接和异常。
2. 区分判断点与执行点；按使用的数据、权限、模型能力与失败方式组合执行步骤。
3. 在不可逆动作前设置确定性校验；为低置信、缺资料、冲突和越权安排具名人工接收人。

交付链：现状流程 → 失败方式 → 智能体/工具边界 → 校验与人工升级路径

原文：frameworks/workflow-decomposition.md

### 业务结果与不可逆风险矩阵

要回答：多个需求中，先做哪个最小可验证方案？

1. 列出3–5个候选切入点，分别说明改善的业务结果、现状基线和投入。
2. 评估失败何时被谁看见、能否在损害前拦截、是否可以撤销；不要把模型置信度等同于业务风险。
3. 优先选择高价值、可拦截且可恢复的切入点；高风险需硬约束和责任人否决权，价值或风险未知先补证据。

交付链：候选方案 → 价值/风险比较 → 选择与暂缓理由 → 验收指标与停止条件

原文：frameworks/outcome-risk-matrix.md

### 四来源收敛

要回答：谁说要做，哪里真的坏了，范围允许什么，技术是否可行？

1. Buyer：核实业务目标、预算、优先级和决定权；Operator：用最近一单还原真实操作和失败位置。
2. Brief：核对书面目标、范围、时间和排除项；Industry：寻找可比技术实践，并核实本项目的数据与接口差异。
3. 检查四个视角是否指向同一瓶颈。分歧保留在问题清单：一线帮助定位故障，决策者确认价值，Brief约束范围，行业证据帮助判断可行性。

交付链：四视角陈述与来源 → 收敛/分歧 → 待核实问题 → 有边界的需求假设

原文：frameworks/4-source-convergence.md

### 本次四来源核对

- Buyer · 业务决策者：顾明岚
  状态：已采集角色陈述，目标和预算仍待确认；已采集依据：manufacturing-quality-f00、manufacturing-quality-f02、manufacturing-quality-f01、manufacturing-quality-f05、manufacturing-quality-f04、manufacturing-quality-f03
- Brief · 书面需求：我们在“质量追溯与缺陷归因”上投入了很多人力。检测表手写后再录入，批次与机台信息经常缺漏。管理层希望用 AI 改善，但还没有确定优先环节、验收标准和权限边界。请你先和各岗位聊聊，找出值得验证的业务需求。
  状态：当前只有场景开场；书面Brief原文与版本待补；已采集依据：暂无
- Industry · 行业可行性：需要可比技术案例、数据条件和接口能力的核验材料。企业业务介绍不能证明技术可行。
  状态：待补行业实践与本项目适用性验证；已采集依据：暂无
- Operator · 一线使用者：林亦舟
  状态：已采集现场陈述，仍需样本与操作观察核实；已采集依据：manufacturing-quality-f13、manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f12、manufacturing-quality-f10、manufacturing-quality-f14

### 从证据到候选需求

- REQ-1 返工换批号导致追溯断链是首要瓶颈，应优先建立原批号强制关联与断链拦截
  依据：manufacturing-quality-f11、manufacturing-quality-f15、manufacturing-quality-f44、manufacturing-quality-f01
  推导：一线给出具体失败例：螺纹不合格品返工后换批号，追溯不到原刀具（f11）；质检员明确遇此情况暂停建议、由工艺工程师核对，错误结果不得覆盖原记录（f15）；兜底规则也把该情形列为转人工触发条件（f44）。这说明断链发生在返工节点而非归因算法，但换批号是强制关联还是人工备注尚未确定，影响现场是否增加确认动作。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：先取近三个月返工换批号的实际单据样本，核对断链比例；与唐映秋、林亦舟确认返工节点是否可强制关联原批号及确认动作归属。验收以两类试点零件批次追溯完整率99%、错误放行为零为门槛，人工确认点由工艺工程师与产品安全负责人共同签核。
- REQ-2 检测表手写再录入造成批次与机台信息缺漏，应验证就地录入与草稿暂存
  依据：manufacturing-quality-f10、manufacturing-quality-f13、manufacturing-quality-f14、manufacturing-quality-f12、manufacturing-quality-f51
  推导：痛点为手写后再录入、批次与机台信息经常缺漏（f10）；现场高峰期只能用现有终端、不能离场补录，草稿需可暂存并显示最后同步时间（f13）；同事把关键说明留在便签或群里、不随单据交接（f14）。工作量基线为每月320批次、每批约25分钟（f12/f51），但该数只覆盖录入环节，不含核对补漏，实际负担可能被低估。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：在一条产线用现有终端做小范围并行试点，记录录入、核对补漏、便签二次搬运三类耗时；与秦芮对齐统计口径（按批次还是检验单、计时起点）。人工确认点：质检员确认草稿同步状态，工艺工程师确认说明挂接字段。
- REQ-3 数据口径不统一（单位、公差版本、校准状态、统计分母）会直接污染归因与验收
  依据：manufacturing-quality-f31、manufacturing-quality-f33、manufacturing-quality-f50、manufacturing-quality-f53、manufacturing-quality-f30、manufacturing-quality-f32
  推导：测量单位和公差版本混用、部分量具校准状态过期（f31），有歧义记录须进人工修复队列、不进自动推荐样本（f33）；工艺按缺陷原因归类、客户按不合格批次统计、返工件重复计数（f50/f53），试点指标须固定分母、排除规则和统计周期。三套系统账号权限独立、业务状态无统一视图（f30），接口只能读检验数据和工艺版本、不能自动放行（f32）。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：先列QMS、MES、量具采集软件的批次/机台/检测记录主键映射与状态口径清单，再定试点指标分母与排除规则。人工确认点：秦芮确认字段口径，叶书确认对外解释口径，顾明岚确认验收基线。
- REQ-4 异常定位辅助与追溯清单须限定为辅助，不自动认定根因或放行
  依据：manufacturing-quality-f05、manufacturing-quality-f52、manufacturing-quality-f40、manufacturing-quality-f41、manufacturing-quality-f22
  推导：范围明确为异常定位辅助和追溯清单，不自动认定根因或放行（f05/f52）；客户图纸受限，未经复检和签核不得放行（f40）；只有授权岗位可查看检测量值、校准证书、工艺版本和返工单，最终决定须对应审批人确认（f41）；工艺工程师只能整理、校核和发起复核，不能代替产品安全负责人签核（f22）。但追溯清单中哪些字段属辅助信息、哪些须人工签字尚未核实。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：与傅景逐字段标注追溯清单的辅助信息与须签核项，形成权限矩阵草案；用历史资料回放验证不触发自动放行。人工确认点：产品安全负责人签核边界，客户质量经理确认对外可用字段。
- REQ-5 人工兜底与审计留痕需可重建处理链，而非模糊提醒
  依据：manufacturing-quality-f44、manufacturing-quality-f45、manufacturing-quality-f23、manufacturing-quality-f25
  推导：出现换批号追溯不到原刀具、资料缺依据、版本冲突或关键系统不可用时转人工，须标注触发原因、接手人和确认时间（f44）；每次建议保留业务编号、资料版本、事实引用、建议结果、人工改动和签核人，审计应能重建首件检验到复检的处理（f45）；交接须含业务编号、版本、状态、未解决事项和接手人，对方确认接手才算完成（f23）；超时升级到质量总监（f25）。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：用历史资料回放构造换批号、版本冲突、接口中断三类场景，检查留痕字段是否足以重建处理链。人工确认点：傅景确认审计字段完整性，唐映秋确认交接确认动作。
- REQ-6 接口中断与数据过期需以带时间戳快照和待刷新标识兜底
  依据：manufacturing-quality-f34、manufacturing-quality-f35、manufacturing-quality-f30
  推导：试点计划每天两次更新已授权业务状态，超过一个更新周期标为待刷新，不能作实时承诺（f34）；接口中断时用带时间戳的上一份只读快照并显示暂未更新，重连后按业务编号去重补齐，现有人工流程继续（f35）。但快照保留多久、由谁确认补齐结果、去重以哪个业务编号为准尚未核实。
  判断：候选需求；需用结果与不可逆风险矩阵比较，P0/P1/P2不等于已完成价值风险评分。
  下一步：在并行试点中模拟单套与多套系统中断，验证快照时间戳与待刷新标识是否被一线正确理解。人工确认点：秦芮确认补齐与去重规则，林亦舟确认现场可读性。


## Demo执行证据

尚未执行绑定Demo评估。

## 阶段练习与训练评分



## 历史版本

保留0个旧版本。JSON导出包含原始报告、成果版本和完整输入引用。
