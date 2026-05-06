# Task 05: Bug Localization

> 真实线上偶发 bug 的定位与修复能力评测

## 场景

线上告警：某 SaaS 产品的「**导出订单 CSV**」功能在用户数据 ≥ 10 万行时**偶发返回空文件**，但 HTTP 接口仍返回 200。Sentry 捕获到一些错误，但日志看似与现象不强相关。

你刚加入这个项目，没人能立刻给你解释这块代码。

## 提供材料

### 1. Stack Trace（来自 Sentry）

```
[2026-04-15 03:22:11.142] WARN  ExportService.streamToCsv
  - stream ended without error, rows_written=0, expected_rows=124871

[2026-04-15 03:22:11.156] INFO  HttpResponse
  - 200 OK, body length: 0, duration: 12.4s, path=/api/orders/export

[2026-04-15 03:22:18.044] ERROR S3UploadService.uploadStream
  - Error: Cannot read properties of undefined (reading 'pipe')
    at S3UploadService.uploadStream (s3-upload.service.ts:87)
    at ExportService.streamToCsv (order-export.service.ts:142)
    at processTicksAndRejections (node:internal/process/task_queues:95:5)
```

### 2. 仓库代码

`repo/` 目录提供了脱敏后的关键模块（约 200 文件，核心逻辑约 3000 行）。

关键文件：

```
src/
├── export/
│   ├── order-export.service.ts     # 主流程
│   ├── csv-transform.ts            # CSV 转换 stream
│   └── s3-upload.service.ts        # S3 上传 stream
├── db/
│   └── order.repository.ts         # 含 streamCursor()
└── controllers/
    └── orders.controller.ts        # /api/orders/export 入口
```

### 3. 已知复现路径

- **触发条件**：用户订单数 ≥ 100k 的企业账号
- **操作**：点击"导出全部"
- **概率**：约 30%
- **环境**：生产 + 预发都能复现，本地很难

## 你的任务

### Step 1: 根因定位
- 一句话说清问题（含相关 `文件:行号`）

### Step 2: 修复方案
- 给出最小 diff
- 说明为什么这样改

### Step 3: 偶发性解释
- 为什么不是 100% 必现？涉及哪些时序因素？

### Step 4: 回归测试建议
- 至少 1 个能稳定复现 bug 的测试用例（可以是 mock 出来的）

## 输出格式

```
## 根因
（一句话 + 文件:行号）

## 修复 diff
```diff
- 旧代码
+ 新代码
```

## 偶发性解释
（≤ 200 字）

## 回归测试
```ts
// 测试代码
```

## 额外发现（可选）
（如果发现其他相关问题）
```

## 约束

- 不允许"改一切"——必须最小修复
- 修复必须能解释为什么之前会失败
- 误判（指错文件/机制）会导致根因维度直接 0 分
