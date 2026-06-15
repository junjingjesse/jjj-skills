# CI 指南 (v1.4.2)

> GitHub Actions 集成 + v1.4 闭环 SOP：AI 写完代码 → 开 PR → **手动跑 CI**（pnpm + Vitest + 可选 Playwright 截图）→ 失败自动 rework → 通过后请主理人 review

---

## 1. 概念扫盲

**GitHub Actions = GitHub 帮你跑脚本**，不是编程语言，是一种 YAML 配置。

| 概念 | 类比 | 作用 |
|------|------|------|
| **Workflow** | 一个完整流程 | 跑测试 / 部署 / 发通知 |
| **Job** | 阶段 | 一个 workflow 可有多个并行 job |
| **Step** | 步骤 | 一条命令或一个 action |
| **Trigger** | 触发器 | `pull_request` / `push` / `schedule` / `manual` |
| **Runner** | 虚拟机 | GitHub 提供的干净 Ubuntu 机器 |

**YAML 调用的命令是语言无关的**——bash、node、python 都行，同一个 workflow 里都能用。

---

## 2. 成本

| 仓库类型 | 免费额度 | 超出后 |
|----------|----------|--------|
| **公开仓库** | 无限分钟 | — |
| **私有仓库** | 2000 分钟/月（Linux） | $0.008/分钟 |
| **Mac runner** | 私有 10x 计费 | — |
| **Windows runner** | 私有 2x 计费 | — |
| **Self-hosted runner** | 免费 | 你提供机器 |

**v1.4.1 实际预算参考**（1 人 + AI 节奏）：
- 一次完整 CI 跑约 6-10 分钟（unit + verify + build）
- 手动触发后**默认 0 分钟/天**
- 偶尔验证、debug、月跑 20-30 次 ≈ 200 分钟 ≈ 10% 预算
- 2000 分钟够一年有余

**避免踩坑**：
- ❌ 不要每次 push 都自动跑（v1.3.2 的 post-merge gate 对单人项目浪费）
- ❌ 不要用 Mac/Windows runner（10x/2x 计费，跑不出更多价值）
- ❌ 不要装 self-hosted 除非你真有 Linux 服务器闲置
- ✅ 默认走 v1.4.1 的 `workflow_dispatch` 手动触发

---

## 3. 文件结构

所有 workflow 文件放在项目根的 `.github/workflows/`：

```
你的Next.js项目/
├── .github/
│   └── workflows/
│       └── regression.yml   ← v1.4.1 手动触发，跑测试（unit/verify/build）
├── app/                     ← Next.js 业务代码
├── package.json
├── tests/                   ← 单元测试 (Vitest，v1.4 硬约束)
│   └── *.test.ts
├── e2e/                     ← E2E 测试 (Playwright)
│   └── *.spec.ts
├── verify_t001.sh           ← v1.4 verify 脚本
├── verify_t002.sh
└── async_comm/              ← v1.4 文档结构
```

GitHub 一看到 `.github/workflows/` 里出现 `.yml` 文件就自动启用。

---

## 4. 测试金字塔（不同类型怎么选）

| 测试类型 | 工具 | 速度 | 覆盖 | 何时跑 | 在 CI 里的位置 |
|---------|------|------|------|--------|----------------|
| **单元** | Jest / Vitest | 极快（秒级） | 单个函数 | 每次 commit | 第 1 个 job |
| **集成/API** | supertest / Postman / Newman | 中等（10s 级） | API 端点 | 每次 PR | 第 2 个 job |
| **E2E/UI** | Playwright | 慢（分钟级） | 用户流程 | 每次 PR | 第 3 个 job |
| **v1.3 verify** | bash 脚本 | 中等 | 端到端集成 | 每次 PR | 第 4 个 job |
| **Build** | `next build` | 慢 | 编译过 | 每次 PR | 第 5 个 job（最后） |

**原则**：
- 单元测试**必跑**（快，反馈快）
- E2E **选跑**（慢，但能抓 UI 问题）
- v1.3 verify 脚本**必跑**（和本地跑同一份）

---

## 5. regression.yml 模板（v1.4.1：pnpm + Vitest，**manual gate**）

把下面文件保存到 `.github/workflows/regression.yml`：

```yaml
# ============================================
# regression.yml (v1.4.1)
# 策略：手动触发（workflow_dispatch），不自动跑
# 工具栈：pnpm + Vitest（v1.4 起统一，不再支持 npm/pytest）
# 调优点：
#   1. 触发器：默认 workflow_dispatch（手动）；如需自动，参考第 5.1 节切换 push 触发
#   2. 任务：注释/删除某个 job 块来跳过；E2E 默认不跑（手动本地）
#   3. pnpm 版本：默认 9.x；如团队用 8.x 改 version 字段
# ============================================

name: Regression Tests

# === 触发器（v1.4.1 改成纯手动）===
on:
  workflow_dispatch:        # GitHub Actions 页面手动点 "Run workflow" 触发
  # push:                    # ← 取消注释改回自动模式（不推荐，月消耗大）
  #   branches: [main]

# 不需要 concurrency 取消逻辑（手动跑不会撞车）

jobs:
  # ========== 1. 单元测试（必跑，v1.4 硬约束）==========
  unit:
    name: Unit Tests (Vitest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      - name: Run unit tests
        run: pnpm test --coverage
      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  # ========== 2. 集成/API 测试（可选）==========
  # 如果项目没有 API 路由，注释或删除整个 api 块
  api:
    name: API Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - name: Run API tests
        run: pnpm run test:api

  # ========== 3. v1.4 verify 脚本（必跑）==========
  # 每个 T-ID 的端到端验证，与本地跑同一份
  v14-verify:
    name: v1.4 Verify Scripts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - name: Run all verify_t*.sh
        run: |
          chmod +x verify_t*.sh
          for t in verify_t*.sh; do
            echo "=========================================="
            echo "Running $t"
            echo "=========================================="
            bash "$t" || exit 1
          done

  # ========== 4. Build 检查（必跑）==========
  build:
    name: Next.js Build
    runs-on: ubuntu-latest
    # unit 和 v14-verify 必须过；api 可选
    needs: [unit, v14-verify]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - name: Next.js build
        run: pnpm build

  # ========== 5. E2E（默认关闭，手动本地跑）==========
  # 如需在 CI 跑 E2E，取消下方注释
  # 注意：Playwright 浏览器 ~500MB（chromium）/ ~2GB（3 浏览器）
  # 建议加 actions/cache 缓存 ~/.cache/ms-playwright，避免每次重下
  # e2e:
  #   name: E2E Tests (Playwright)
  #   runs-on: ubuntu-latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - uses: pnpm/action-setup@v4
  #       with:
  #         version: 9
  #     - uses: actions/setup-node@v4
  #       with:
  #         node-version: '20'
  #         cache: 'pnpm'
  #     - run: pnpm install --frozen-lockfile
  #     - name: Cache Playwright browsers
  #       uses: actions/cache@v4
  #       with:
  #         path: ~/.cache/ms-playwright
  #         key: playwright-${{ hashFiles('pnpm-lock.yaml') }}
  #     - run: pnpm exec playwright install --with-deps chromium
  #     - run: pnpm exec playwright test

  # ========== 6. 截图（v1.4.2 新增，默认关闭）==========
  # 本地不装 Playwright；CI 跑完后 screenshots/ 目录上传到 Actions artifact
  # 用法：UI 改动的 T-ID 临时取消下方注释，跑完把 artifact 链接贴 PR 描述
  # 缓存 ~/.cache/ms-playwright，避免每次重下 chromium（~500MB）
  # screenshots:
  #   name: Playwright Screenshots
  #   runs-on: ubuntu-latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - uses: pnpm/action-setup@v4
  #       with:
  #         version: 9
  #     - uses: actions/setup-node@v4
  #       with:
  #         node-version: '20'
  #         cache: 'pnpm'
  #     - run: pnpm install --frozen-lockfile
  #     - name: Cache Playwright browsers
  #       uses: actions/cache@v4
  #       with:
  #         path: ~/.cache/ms-playwright
  #         key: playwright-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
  #         restore-keys: |
  #           playwright-${{ runner.os }}-
  #     - run: pnpm exec playwright install --with-deps chromium
  #     - run: pnpm exec playwright test --reporter=github
  #     - name: Upload screenshots
  #       if: always()
  #       uses: actions/upload-artifact@v4
  #       with:
  #         name: screenshots-${{ github.run_id }}
  #         path: screenshots/
  #         retention-days: 30
```

**v1.4.2 调整点**（vs v1.3.2 / v1.4.0 / v1.4.1）：

| 调整项 | 怎么做 | 影响 |
|--------|--------|------|
| 想改回自动模式 | 注释 `workflow_dispatch`，取消 `push: branches: [main]` 注释 | 每次 merge 跑 CI，月消耗 200-1000 分钟（1 人项目不推荐） |
| 想加回 E2E | 取消 `e2e` job 注释 | 单次慢 3-5 分钟；建议加 `actions/cache` 缓存 Playwright |
| **想加 UI 截图（v1.4.2 新增）** | 取消 `screenshots` job 注释 | 单次慢 1-2 分钟（cache 命中后 10s），artifact 30 天有效；本地**不**需要装 Playwright |
| 想跳过 API 测试 | 注释或删除 `api` job | 单次快 1-2 分钟，但 API bug 可能漏到生产 |
| 想改 Node 版本 | 改 `node-version` | 适用所有 job |
| 想改 pnpm 版本 | 改 `pnpm/action-setup` 的 `version` | 适用所有 job |

**v1.4.1 效果**（手动 gate）：
- 默认 0 分钟/天
- 想验证时去 GitHub Actions 页面点 "Run workflow"，1-3 分钟出结果
- 失败时 `gh run list` 查得到，AI 下次启动扫描时能感知
- 月跑 20-30 次 ≈ 200 分钟，远低于 2000 预算

---

## 6. 闭环 SOP（v1.4.1 manual gate）

### 6.1 执行者侧流程（v1.4.1：manual gate）

```
[完成 T-001，本地 verify 通过]
    ↓
git commit + push
    ↓
gh pr create --draft
    ↓
补充 verify 结果到 PR
    ↓
gh pr ready   ← 标 ready，等主理人 review
    ↓
TASK.md → in_review
    ↓
不等 review，开始下一 T-ID
    ↓
...
[主理人 review + merge PR 到 main]
    ↓
★ ★ ★ 不再自动跑 CI！★ ★ ★
    ↓
[主理人 / AI 手动去 GitHub Actions 点 "Run workflow"]
    ↓
[1-3 分钟后，CI 跑完]
    ↓
[可选] AI 扫描 gh run list 看主理人跑的结果
```

**关键变化（vs v1.4.0 post-merge gate）**：
- ❌ **merge 不再自动触发 CI**（省 99% 分钟）
- ✅ 主理人在 GitHub Actions 页面手动点 "Run workflow"
- ✅ 失败时 `gh run list` 仍能查到，AI 启动扫描时可感知
- ✅ fix forward 机制不变

### 6.2 失败处理（v1.4.1 manual gate）

AI 每次启动扫描时，可以查最近一次手动跑的 CI 状态：

```bash
# 1. 查最近一次 CI（不限分支，手动触发的会留在 default branch）
gh run list --workflow=regression.yml --limit 1

# 2. 看具体 run
gh run view <run_id>
# 输出示例：
# ✓ unit        1m23s
# ✓ v14-verify  0m12s
# ✗ build       2m45s  ← 失败
# Status: completed, conclusion: failure

# 3. 看失败日志
gh run view <run_id> --log-failed

# 4. 写修复任务（TASK.md 加一条）
#   T-FIX-001：修复最近一次 CI build 失败
#   关联：被 T-XXX 引入（哪个 PR 引入的）
#   verify 方式：手动重跑 gh run rerun 通过
#   优先级：P0

# 5. 写 Q&A 记录
#   Q-XXX：CI 失败，run_id=12345，错误信息：xxx
```

**Fix Forward 流程**（v1.4.1）：

```
CI 跑失败（手动触发的那次）
    ↓
[AI 下次启动扫描到]
    ↓
写 T-FIX-XXX（P0 优先级）
    ↓
T-FIX 进入 pending（最先被领）
    ↓
AI 修复 + commit + push
    ↓
[不需要等自动 CI，PR 等主理人 review]
    ↓
[主理人 review + merge]
    ↓
[主理人手跑一次 CI 验证 fix]
    ↓
   ┌─ pass ─→ T-FIX → completed，RETROSPECTIVE 记录
   │
   └─ fail ─→ 再写 T-FIX-002，连续 3 次失败升级 blocked
```

### 6.3 gh CLI 命令速查（v1.4.1 manual gate）

```bash
# 查最近 CI 状态（不限分支，manual trigger 不绑定到 main）
gh run list --workflow=regression.yml --limit 5

# 看具体 run 的失败日志
gh run view <run_id> --log-failed

# 列出最近的 workflow runs（不限分支）
gh run list --workflow=regression.yml --limit 10

# 重新跑某次 CI（不开新 commit）
gh run rerun <run_id>

# 取消正在跑的 CI
gh run cancel <run_id>

# 看 PR 的 check 状态（manual gate 模式下，PR 不会有 CI check）
gh pr checks <PR号>
```

### 6.4 retry 机制（v1.4.1 manual gate 修复循环）

```python
# 伪代码（AI 内部决策）
max_fix_retry = 3
fix_retry = 0

while True:
    latest_runs = gh_run_list(workflow='regression.yml', limit=1)
    latest = latest_runs[0]
    
    if latest.conclusion == 'success':
        break  # 最近一次跑通
    
    if fix_retry >= max_fix_retry:
        # 升级为 blocked
        write_qa(f"CI 连续 {max_fix_retry} 次失败")
        create_blocked_task()
        return
    
    # 读失败日志
    log = gh_run_view(latest.id, log_failed=True)
    
    # 修代码 + commit + push
    fix_code()
    commit_push()
    
    fix_retry += 1
    # 不需要 sleep 等 CI（manual gate 下要等主理人 review merge + 手跑）
    # 等下次 AI 启动时再继续
```

### 6.5 边缘情况

| 情况 | 处理 |
|------|------|
| CI 跑超过 10 分钟 | `gh run cancel` 取消，标记 CI 慢，简化 verify 脚本或加 cache |
| `pnpm install` 失败 | 网络问题，重试 1 次，还失败则 T-FIX blocked |
| build job 失败 | 99% 是类型错误或 lockfile 不一致，T-FIX-001 直接修 |
| v14-verify 失败 | 某个 T-ID 的 verify 脚本不严，T-FIX 改脚本或改代码 |
| Secrets 缺失 | 在 GitHub repo Settings → Secrets 加 |
| 忘记手动跑 CI | AI 启动时 `gh run list --limit 1` 自检，提醒主理人 |

---

## 7. v1.4.2 完整闭环图（pnpm + Vitest + 可选 Playwright，**manual gate**）

```
                    AI (执行者)
                       │
       写代码 ─→ 本地 verify ─→ commit + push
                                       │
                                       ↓
                              开 PR (draft)
                                       │
                                       ↓
                              补充 verify 结果
                                       │
                                       ↓
                              gh pr ready
                                       │
                                       ↓
                         更新 TASK.md → in_review
                                       │
                                       ↓
                       不等 review，开始下一 T-ID
                                       │
                                       ↓
                            ┌─────────────────┐
                            │  主理人 review   │
                            │  (GitHub Desktop)│
                            └────────┬────────┘
                                     │
                              Approve + Merge
                                     │
                                     ↓
                              托管平台原生自动部署
                              （如 Vercel / Netlify / Cloudflare Pages，不消耗 GitHub Actions 分钟）
                                     │
                                     ↓
                       ╔═══════════════════════╗
                       ║ 主理人 / AI 手动跑 CI  ║  ← workflow_dispatch
                       ║ GitHub Actions 点     ║
                       ║ "Run workflow" 按钮   ║
                       ╚═══════════╤═══════════╝
                                   │
                              ┌────┴────┐
                              │         │
                          全部 ✅     有 ❌
                              │         │
                              ↓         ↓
                       主理人安心    AI 启动时
                       TASK 推进    gh run list 看到失败
                              │         │
                              ↓         ↓
                       archive/   创建 T-FIX-XXX
                       归档        (P0 优先级)
                              │         │
                              ↓         ↓
                       RETROSPECTIVE  AI 修代码 + push
                       更新                │
                                            ↓
                                    等主理人 review merge
                                            │
                                            ↓
                                    主理人手跑 CI 再验证
                                            │
                                      ┌─────┴─────┐
                                      │           │
                                  pass ✅     fail ❌
                                      │           │
                                      ↓           ↓
                                  T-FIX →    再写 T-FIX-002
                                  completed  (max 3 次)
                                            ↓
                                         blocked
```

**v1.4.2 vs v1.3.1 关键差异**（一图看懂四代演进）：

| 维度 | v1.3.1 (PR-time gate) | v1.3.2 (post-merge auto) | v1.4.1 (manual gate) | **v1.4.2 (+ Playwright 截图)** |
|------|----------------------|--------------------------|--------------------------|--------------------------|
| CI 触发 | PR 打开 + push main | 只 push main（自动） | 手动 workflow_dispatch | **手动 workflow_dispatch** |
| 反馈时机 | PR 阶段就有 CI 结果 | merge 后自动跑 | 主理人想验证时手动跑 | **同 v1.4.1** |
| AI 等待 | 要等 CI 才能 ready | 不等 CI（自动跑后台） | 不等 CI，按需跑 | **同 v1.4.1** |
| 工具栈 | pytest + npm + Jest | pytest + npm + Jest | pnpm + Vitest | **pnpm + Vitest + Playwright（可选）** |
| 单元测试 | pytest tests/（可选） | pytest tests/（可选） | Vitest tests/，v1.4 硬约束 | **同 v1.4.1** |
| Deploy | 自己写 deploy.yml | 自己写 deploy.yml | 托管平台原生 | **同 v1.4.1** |
| E2E | CI 里跑 Playwright | 本地手动跑 | 本地手动跑 | **本地手动跑 / CI 可选截图** |
| UI 截图 | 无 | 无 | 无 | **CI 跑完上传 artifact（v1.4.2 新增）** |
| 失败处理 | PR 上 rework | fix forward（T-FIX） | fix forward（T-FIX） | **同 v1.4.1** |
| 月分钟消耗 | 500-1500 分钟 | 500-1500 分钟 | 50-200 分钟 | **50-300 分钟**（+screenshots job） |
| 适合场景 | 大团队、严苛质量门 | 中型团队、半自动 | 1 人 + AI、低开销 | **1 人 + AI + 偶尔 UI 改动** |

---

## 8. 常见问题（v1.4.2）

### Q: 私有仓库 2000 分钟够用吗？

A: v1.4.1 manual gate 下默认 0 分钟/天；月跑 20-30 次 ≈ 200 分钟，远低于 2000 预算。

### Q: 为什么要改成手动触发（v1.4.0 → v1.4.1）？

A: v1.4.0 post-merge gate 对单人项目是过度工程：
- 每次 merge 都跑 ≈ 500-1500 分钟/月（1 人项目根本用不到这么多）
- 主理人 / AI 都被"等 CI" 打断
- 同事实测 docker build 一晚 400+ 分钟（cache 没用好），手动触发可控得多

### Q: 手动触发会不会漏掉回归？

A: 不会。AI 启动时 `gh run list --limit 1` 自检，提示主理人"距离上次跑通 N 天/有 X 个未验证 PR"。fix-forward 机制不变。

### Q: CI 跑失败但本地跑没问题？

A: 可能是：
- 操作系统差异（macOS 本地 vs Linux CI）
- 环境变量缺失（要加到 GitHub Secrets）
- Node 版本不一致（用 `.nvmrc` 锁版本）
- 时区/编码问题
- pnpm lockfile 没同步（`pnpm install --frozen-lockfile` 严格模式）

### Q: AI retry 3 次后还是失败，怎么办？

A: 写 Q&A.md 升级为 blocked，**不要无限循环**。可能是：
- 外部 API 变更（需要人工调整）
- 设计问题（需要重新设计 verify）
- 环境问题（需要人工配置 Secrets）

### Q: 怎么让 CI 跑得更快？

A:
- `cache: 'pnpm'`（已加）
- 删掉不需要的 `pnpm install` 步骤
- E2E 用 `actions/cache` 缓存 `~/.cache/ms-playwright`，key: `playwright-${{ hashFiles('pnpm-lock.yaml') }}`
- 用 self-hosted runner（自己的机器，免费）

### Q: Vercel 部署怎么配？

A: **不要写 deploy.yml**。Vercel 的 GitHub 原生集成（项目 Settings → Git → Connect Repo）会在 push 到 main 时自动部署，不消耗 GitHub Actions 分钟。只有在 deploy 前需要做额外操作（如数据库迁移、通知）时才自己写 Actions。

### Q: v1.4.1 还能切回自动模式吗？

A: 可以。注释掉 `workflow_dispatch`，取消 `push: branches: [main]` 注释即可。但月消耗会从 ~200 涨到 ~1000 分钟（1 人项目不推荐）。
