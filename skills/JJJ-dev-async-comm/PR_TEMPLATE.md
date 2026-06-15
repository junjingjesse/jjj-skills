# PR 描述模板 (v1.4.2)

> 执行者开 PR 时，把这个模板的内容填好，存到项目的 `.github/PR_BODY.md`，然后用 `gh pr create` 开 PR。

## 使用流程

1. 复制下方"模板内容"到项目 `.github/PR_BODY.md`
2. 填好所有 `{}` 占位符和复选框
3. 跑 `gh pr create --draft --title "T-XXX: xxx" --body-file .github/PR_BODY.md`
4. 补充 verify 结果到 PR 描述
5. 跑 `gh pr ready`

---

## 模板内容

复制以下内容到 `.github/PR_BODY.md`：

```markdown
## 任务
- **T-ID**: T-{XXX}
- **标题**: {任务简短描述}
- **优先级**: P{0/1/2}
- **关联需求**: USER.md {P0/1/2}-{x}

## 变更摘要

### 新增
- `{文件路径}` - {作用}

### 修改
- `{文件路径}` - {作用}

### 删除
- {如适用}

## 验证方式

### 自动 verify（v1.4 起以 Vitest 为准）
- [ ] 跑 `bash verify_t{XXX}.sh` 通过
- [ ] 跑 `pnpm test tests/<T-ID 对应文件>` 通过（v1.4 硬约束，N/A 类 T-ID 除外）
- [ ] 全量回归 `pnpm test` 通过
- [ ] 覆盖率不低于 v1.4 基线（见 SETUP.md）

### 手动验证
- [ ] {场景1}
- [ ] {场景2}

### 边界用例
- [ ] 空输入
- [ ] 极端值
- [ ] 错误输入

## 关联
- **需求**: USER.md {P0/1/2}-{x}
- **阻塞问题**: 无 / Q-{XXX}（已解决）
- **前置 T-ID**: T-{XXX}（如有）
- **后续 T-ID**: T-{XXX}（如有）
- **复盘**: 见 RETROSPECTIVE.md L-{XXX}

## 主理人 review 检查点
- [ ] 代码风格符合项目约定
- [ ] 测试覆盖关键路径（v1.4：附 `pnpm test --coverage` 报告）
- [ ] 没有引入新依赖（或已在 package.json + pnpm-lock.yaml）
- [ ] 文档已更新
- [ ] verify 脚本可重复跑
- [ ] v1.4 硬约束：T-ID 的 `unit-test` 字段已填且对应文件存在

## 截图/录屏
（UI 变更必填；v1.4.2+ 推荐从 CI artifact 拿，本地**不**装 Playwright）

如适用：
- v1.4.2+ 启用了 `screenshots` job：粘 GitHub Actions artifact 链接（格式：`https://github.com/<owner>/<repo>/actions/runs/<run_id>#artifacts`）
- 临时本地截：粘图片（v1.4.2 之前的方式，本地需装 Playwright）
- N/A：明确写"N/A（非 UI 改动）"
```

---

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| T-ID | ✅ | 唯一标识，对应 TASK.md 的任务 |
| 标题 | ✅ | 简短描述，看 PR 列表就知道做什么 |
| 优先级 | ✅ | P0/P1/P2 |
| 关联需求 | ✅ | USER.md 的需求编号 |
| 变更摘要 | ✅ | 文件级别变更（新增/修改/删除） |
| 验证方式 | ✅ | 至少 1 个 verify 通过 + 1 个手动验证 |
| 关联 | ✅ | 至少要有需求关联 + 复盘 ID |
| 截图/录屏 | ❌（v1.4.2 起 UI 变更**推荐**填）| UI 改动粘 CI artifact 链接或本地截图 |

---

## 反例（不要这么写 PR 描述）

❌ **写代码"实现了一个功能"，没 T-ID**
→ 主理人不知道这个 PR 对应哪个需求

❌ **verify 方式只写"测试通过"，没具体命令**
→ 主理人无法本地复现

❌ **变更摘要不列文件，只说"改了一些"**
→ 主理人无法判断影响范围

❌ **关联留空**
→ 失去与 TASK.md / RETROSPECTIVE.md 的追溯链

❌ **verify 复选框没勾**
→ 看起来没真的验证过

---

## 完整示例

```markdown
## 任务
- **T-ID**: T-001
- **标题**: 实现关键词清洗函数
- **优先级**: P0
- **关联需求**: USER.md P0-1

## 变更摘要

### 新增
- `src/keyword_processor.py` - 关键词清洗主函数
- `tests/test_keyword_processor.py` - 单元测试
- `verify_t001.sh` - 端到端验证脚本

### 修改
- `src/main.py` - 在主流程中调用清洗函数

## 验证方式

### 自动 verify（v1.4 Vitest）
- [x] 跑 `bash verify_t001.sh` 通过
- [x] 跑 `pnpm test tests/lib/keyword.test.ts` 通过（3 tests）
- [x] 全量回归 `pnpm test` 通过
- [x] 覆盖率 92%（>= v1.4 基线 80%）

### 手动验证
- [x] 输入 "Hello, World!" → 输出 ["hello", "world"]
- [x] 输入 "" → 输出 []
- [x] 输入 "你好,世界" → 输出 ["你好", "世界"]

### 边界用例
- [x] 空字符串处理
- [x] Unicode 字符
- [x] 多分隔符混合

## 关联
- **需求**: USER.md P0-1
- **阻塞问题**: 无
- **前置 T-ID**: 无
- **后续 T-ID**: T-002
- **复盘**: 见 RETROSPECTIVE.md L-001

## 主理人 review 检查点
- [x] 代码风格符合项目约定
- [x] 测试覆盖关键路径（vitest 报告见 artifact）
- [x] 无新依赖
- [x] 文档已更新（README.md 新增使用说明）
- [x] v1.4 硬约束：T-ID 的 `unit-test` 字段填 `tests/lib/keyword.test.ts` ✅

## 截图/录屏
N/A（非 UI 改动）
```
