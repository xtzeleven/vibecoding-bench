# Task 03: Cross-File Modification

> 真实开发场景的跨文件修改能力评测

## 场景

你是一个 Node.js 后端工程师，正在维护一个使用 **Express.js + TypeScript** 的电商 API 项目（`repo/` 目录）。

产品在 Slack 上提了新需求：

> 最近爬虫太多，挑几个关键接口做个限流，每个 IP 每分钟最多 60 次。
> 但管理员后台不能限流，注册接口要更严格点（5 次/分钟）。
> 配置最好能改，别写死。

## 仓库结构

```
repo/
├── src/
│   ├── app.ts
│   ├── config/
│   │   └── index.ts
│   ├── routes/
│   │   ├── auth.ts          # /auth/register, /auth/login
│   │   ├── orders.ts
│   │   ├── products.ts
│   │   └── admin/
│   │       ├── users.ts
│   │       └── reports.ts
│   ├── middleware/
│   │   ├── auth.ts
│   │   └── logger.ts
│   └── ...
├── tests/
└── package.json
```

完整代码量约 50 个文件、3000 行 TS。

## 你的任务

1. 实现一个限流中间件
2. 应用到至少 3 个普通接口（任选）
3. `/auth/register` 使用更严格的限流
4. 所有 `/admin/*` 路由跳过限流
5. 限流参数从配置读取（环境变量可覆盖）
6. 至少一个测试用例验证限流生效
7. 不破坏现有 `npm test`

## 输出要求

请按以下格式输出：

```
## 决策说明
（150 字以内：你为什么这么设计、关键 trade-off）

## 修改清单
- src/middleware/rateLimit.ts (新建)
- src/config/index.ts (修改)
...

## 完整代码
### src/middleware/rateLimit.ts
```ts
// 完整代码
```

### src/config/index.ts

```ts
// 完整代码（修改后的版本）
```

...

```
## 约束

- 不引入新的大型框架（小工具库 OK，如 `express-rate-limit`）
- 必须能通过现有 `npm test`
- 修改/新建文件数预期在 5-8 个范围内
- 保持项目原有代码风格

```
