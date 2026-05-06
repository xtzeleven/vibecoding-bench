# Expected Output — Task 05

## 参考根因

**位置**：`src/export/order-export.service.ts:142`

**问题**：使用 `pipeline()` 串联 `DB Cursor → CsvTransform → S3 UploadStream`，但 `CsvTransform._flush()` 中错误地在 `callback()` 之后又调用了 `this.push(buffer)` 推送最后一批数据。当上游 cursor 已结束、下游 S3 stream 因网络抖动稍慢消费时，`_flush` 的 callback 已触发 destroy，迟到的 push 失败 → S3 stream 得到 0 字节 → uploadStream 抛 `read after destroyed`。

```ts
// order-export.service.ts:135-150 (问题代码示意)
class CsvTransform extends Transform {
  _flush(cb) {
    cb();                          // ❌ 先 cb()
    this.push(this.buffer);        // ❌ 再 push，buffer 可能丢失
  }
}
```

## 参考修复 diff

```diff
  _flush(cb) {
-   cb();
-   this.push(this.buffer);
+   if (this.buffer) {
+     this.push(this.buffer);
+     this.buffer = null;
+   }
+   cb();
  }
```

## 偶发性解释（参考）

只有当满足**所有**条件才触发：

1. 数据量足够大，触发了 `_flush` 路径（小数据走 `_transform` 直接 push 完）
2. S3 上传 stream 的 high watermark 恰好被填满，导致下游 backpressure
3. cursor close 时机早于 flush 完成
4. Node 事件循环把 destroy 调度到 push 之前

生产环境网络抖动 + 大数据量 + cursor batch 边界 → 30% 概率命中。本地环境 S3 替换为 minio 且无延迟，所以稳定不复现。

## 参考回归测试

```ts
// tests/export/csv-transform.test.ts
import { CsvTransform } from '../../src/export/csv-transform';
import { Writable } from 'stream';

it('flushes pending buffer before signaling end', (done) => {
  const sink: Buffer[] = [];
  const writable = new Writable({
    write(chunk, _enc, cb) { sink.push(chunk); setTimeout(cb, 5); }, // 模拟慢消费
  });

  const t = new CsvTransform();
  t.pipe(writable);

  for (let i = 0; i < 200_000; i++) t.write({ id: i, total: 99.5 });
  t.end();

  writable.on('finish', () => {
    const total = Buffer.concat(sink).toString();
    expect(total.split('\n').length).toBeGreaterThan(199_000);
    done();
  });
});
```

## 验收标准

- [ ] **根因定位正确**：`_flush` 中 `cb()` 与 `push()` 顺序倒置（误判直接 0 分）
- [ ] **修复 diff 最小**：只改 flush 逻辑，不重写整个 stream pipeline
- [ ] **偶发原因合理**：能至少说出"backpressure"或"cursor close 时机"中的一个
- [ ] **测试能稳定复现**：通过模拟慢消费触发 flush 路径
- [ ] **不引入新问题**：修复后大文件导出耗时不显著增加

## 常见误判模式（评分时警惕）

- ❌ 怪 S3 SDK 版本问题
- ❌ 怪 DB cursor 超时
- ❌ 给"加重试"的方案（治标不治本）
- ❌ 重写整个 pipeline（过度修复）
