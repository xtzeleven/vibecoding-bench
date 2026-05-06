# Evaluation Scripts

跑评测的命令行工具。

## Setup

```bash
pip install anthropic openai

# 按需配置 API Key（评测哪个模型就配哪个）
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export MIMO_API_KEY=...
export DEEPSEEK_API_KEY=...
export DASHSCOPE_API_KEY=...
```

## 单任务单模型

```bash
cd scripts
python run_eval.py --task 03 --model claude-sonnet-4-5 --runs 3
```

## 全量任务跑 MiMo（M2 阶段主用法）

```bash
python run_eval.py --task all --model mimo-v2.5 --runs 3 \
    --output ../results/mimo-v2.5/
```

## 输出格式

每次 run 会生成：

```
results/<model>/<task>__run<N>.json
```

例如：

```json
{
  "task_id": "03-cross-file-modification",
  "model": "mimo-v2.5",
  "run": 1,
  "elapsed_s": 18.42,
  "input_tokens": 8421,
  "output_tokens": 2156,
  "prompt_chars": 32100,
  "response": "## 决策说明\n选用 express-rate-limit ...",
  "error": null,
  "timestamp": "2026-05-08 14:30:21"
}
```

## 评分流程

脚本只负责跑模型 + 收响应，**评分由人工进行**：

1. 团队成员 A、B 各自打开 `results/<model>/<task>__runN.json`
2. 对照 `tasks/<task>/rubric.json` 给每个维度打分
3. 分歧 ≥ 2 分由仲裁 C 决策
4. 最终结果汇总到 `results/leaderboard.md`

## 添加新模型

编辑 `models.py` 的 `REGISTRY`，加一行即可：

```python
"glm-4.6": OpenAICompatClient(
    name="glm-4.6",
    model_id="glm-4.6",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key_env="ZHIPU_API_KEY",
),
```

## 添加新任务

按 `tasks/<NN>-<slug>/` 的目录结构创建：

```
tasks/13-new-task/
├── task.md
├── expected.md
├── rubric.json
└── repo/          # 可选，需要项目代码的任务才有
```

`run_eval.py --task all` 会自动发现所有任务。
