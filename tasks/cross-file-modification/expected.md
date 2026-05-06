# Expected Output — Task 03

## 参考文件清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `src/middleware/rateLimit.ts` | 新建 | 限流中间件，参数化 |
| `src/config/rateLimit.config.ts` | 新建 | 限流参数集中管理 |
| `src/config/index.ts` | 修改 | 导出新配置 |
| `src/routes/auth.ts` | 修改 | register 使用严格限流 |
| `src/routes/orders.ts` | 修改 | 应用通用限流 |
| `src/routes/products.ts` | 修改 | 应用通用限流 |
| `src/app.ts` | 修改 | 注册中间件，admin 跳过 |
| `tests/middleware/rateLimit.test.ts` | 新建 | 至少覆盖 3 个用例 |

## 验收标准

### Must Have（缺一项扣 2 分）

- [ ] 限流中间件可独立使用、参数化
- [ ] `/auth/register` 5 次/分钟生效
- [ ] 普通接口 60 次/分钟生效
- [ ] `/admin/*` 路由不被限流
- [ ] 配置可通过环境变量覆盖
- [ ] 至少 1 个测试用例 pass
- [ ] 现有测试不被破坏

### Nice to Have（每项加 0.5 分，封顶）

- 返回标准的 `RateLimit-Limit` / `RateLimit-Remaining` / `Retry-After` HTTP 头
- 限流粒度可按 IP / userId 切换
- 限流命中后日志友好（含 IP、路径、剩余时间）
- 预留 Redis 后端接口（适配集群部署）

## 示例参考决策

> 选用 `express-rate-limit`（社区主流、零依赖、~2KB），自己造轮子风险高。
> 配置抽离到 `rateLimit.config.ts`，env 覆盖通过 `parseInt(process.env.RATE_LIMIT_GENERAL_PER_MIN ?? '60')` 实现。
> admin 路由通过 `app.use('/admin', adminRouter)` 在限流中间件**之前**注册避开。
> register 单独 `router.post('/register', strictLimiter, handler)`。
