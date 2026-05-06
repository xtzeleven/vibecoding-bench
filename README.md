# vibecoding-bench
  > 面向真实开发场景的中外大模型编程能力评测
  > *Real-world coding benchmark for AI assistants*

  ![Status](https://img.shields.io/badge/status-WIP%20M2-orange)
  ![License](https://img.shields.io/badge/license-MIT-blue)
  ![Models](https://img.shields.io/badge/models-8%2B-green)

  ## 🎯 项目简介

  Vibecoding Bench 是一个**贴近真实软件工程工作流**的大模型编程能力评测项目。源于我们团队过去半年使用 Claude
  Code、Cursor、ChatGPT 等工具进行 AI 辅助开发的实战经验——我们发现现有学术 Benchmark（HumanEval / SWE-Bench /
  LiveCodeBench）与真实开发体感存在明显鸿沟。

  我们想回答一个简单问题：

  > **在真实开发者的日常工作流里,国产模型与 Claude / GPT 的差距究竟有多大?**

  ## 🧭 为什么需要这个项目

  - 📊 **跑分高 ≠ 好用**：很多模型 SWE-Bench 分数亮眼，但接入 Cursor/Claude Code 后步步出错
  - 🇨🇳 **国产模型缺真实场景反馈**：开发者选型靠玄学
  - 🌀 **Vibecoding 范式正在崛起**：传统单测式评测无法度量"自然语言驱动开发"的体验

  ## 📐 评测维度（12 类真实任务）

  | # | 维度 | 描述 |
  |---|---|---|
  | 1 | 需求拆解 | 一句模糊需求 → 完整 Tech Spec |
  | 2 | 多轮迭代 | 5+ 轮反复修改下不偏题 |
  | 3 | 跨文件修改 | 在 50+ 文件项目中精准定位修改点 |
  | 4 | 大型重构 | 整体改架构，不破坏旧测试 |
  | 5 | Bug 定位 | 给 stack trace + repo，找根因 |
  | 6 | 工具调用稳定性 | 长链 Tool Use 不中断 |
  | 7 | 长上下文 Code Review | 100K+ 输入下的批注质量 |
  | 8 | 中文母语场景 | 中文注释 / 需求 → 代码 |
  | 9 | 多模态调试 | 截图 + 报错 → 定位 |
  | 10 | 文档生成 | 代码 → API 文档 |
  | 11 | 测试编写 | 给函数 → 高覆盖率单测 |
  | 12 | 安全审计 | 代码 → 漏洞清单 |

  ## 🤖 评测对象

  ### ✅ 已完成基线（M1）
  - Claude Sonnet 4.5 / Opus 4
  - GPT-4o / GPT-4.1
  - DeepSeek-V3
  - Qwen3-Coder

  ### 🔜 计划纳入（M2 - 2026 Q2）
  - **Xiaomi MiMo V2.5**（旗舰推理 + 多模态 + TTS）
  - GLM-4.6
  - Kimi K2
  - Doubao 1.5

  ## 🛠️ 评测方法

  每个任务包含：

  ```
  tasks/<task-id>/
  ├── task.md          # 自然语言需求（模拟真实沟通）
  ├── repo/            # 真实可运行的项目（已脱敏）
  ├── expected.md      # 期望产出 + 验收标准
  └── rubric.json      # 评分细则（5 子维度，0-10 分）
  ```

  **评分流程**：每个模型每任务跑 3 次取中位 → 2 名团队成员盲评 → 1 名仲裁。

  ## 📊 阶段性观察（Preview）

  > 完整结果将在 M2 阶段后发布，当前为非定论性观察：

  - Claude Sonnet 4.5 在**跨文件修改稳定性**上仍领先
  - DeepSeek-V3 在**中文需求场景**体感超出预期
  - GPT-4o **工具调用链路**最稳
  - 国产模型在 50K+ 上下文下普遍表现下滑（待 MiMo 验证）

  ## 🗺️ Roadmap

  - [x] **M0** — 评测框架设计 + 任务清单（2026 Q1）
  - [x] **M1** — 国外三方基线测试完成（2026 Q1）
  - [ ] **M2** — 国产模型矩阵评测（2026 Q2）👈 **当前阶段**
  - [ ] **M3** — 公开评测平台 + Leaderboard（2026 Q3）
  - [ ] **M4** — 社区共建任务库（2026 Q4）
