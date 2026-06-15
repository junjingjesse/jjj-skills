---
name: JJJ-dev-async-comm
description: "开发场景专用异步沟通治理：PR 评审、CI 验证、manual gate（已在 Next.js 模板项目验证）"
trigger: ["开发异步沟通","dev_async_comm","初始化开发工厂","开dev开发工厂"]
---

# JJJ-dev-async-comm 开发场景异步沟通技能 (v1.4.2)

> 本 skill 是**开发场景专用**异步沟通治理流程（v1.4.1），集成 Git PR 评审、CI 验证、**manual gate**（手动触发，避免每次 merge 浪费 Actions 分钟）。
> 已在 **Next.js 模板项目**验证，但**不限于**该模板——任何有 Git 仓库的代码项目均可使用。
> 如需**通用版本**（不假设在代码项目中），请使用 [JJJ-general-async-comm](../JJJ-general-async-comm/SKILL.md)。

> 24 小时无人工厂：通过文件通信 + Git PR 评审，让 AI 持续推进任务，人异步决策。
> 配套架构文档见 [ARCHITECTURE.md](./ARCHITECTURE.md)，变更历史见 [CHANGELOG.md](./CHANGELOG.md)。

---

## 整体流程 (v1.3.3)

```
用户触发技能
    ↓
★ Step 0: Preflight Check（gh/git 必须就绪，失败立即停手）
    ↓ 失败 → 报告 + 停手（**禁止自动降级**）
★ Step 1: 项目基础信息收集（owner/repo/主理人/约定/项目类型 → PROJECT.md）
    ↓
★ Step 2: 创建 12 个文件脚手架（8 文档 + 2 .github + 2 占位）
    ↓
★ Step 2.5: 远程仓库检查与创建（v1.4 新增，gh repo create）
    ↓
Step 3: 初始化/确认 git 仓库（main 分支）
    ↓
Step 4: 创建定时任务 (每 5 分钟执行)
    ↓
┌──────────────────────────────────────┐
│ 定时任务执行 SOP (v1.3.3)            │
│                                      │
│ 0. ★ 读 PROJECT.md 拿到仓库和约定    │
│ 0.1 扫描 PR 状态（异步打回）          │
│   - ★ 检查 main CI 状态              │
│ 1. 回归测试 → 检查 REGRESSION        │
│ 2. 任务执行 → 从 TASK.md 取任务      │
│ 3. 写代码 → 跑 verify               │
│ 4. 提交：commit + push + 开 PR      │
│ 5. 复盘沉淀 → 写 RETROSPECTIVE      │
│ 6. 归档已完成 → archive/             │
│ 7. 重置 TASK 占位符                  │
│ 8. 输出结果                          │
└──────────────────────────────────────┘
```

★ = v1.3 引入；v1.3.3 加深（Preflight + PROJECT.md + 12 文件脚手架 + 任务粒度 + 复盘质量门）

**v1.3.2 关键变化**：CI 不在 PR 阶段跑（不阻塞主理人 review），改为 merge 到 main 后才跑。失败时 AI 自动创建 T-FIX-XXX 任务修复。详见 [CI_GUIDE.md](./CI_GUIDE.md)。

## v1.3.3 增量变化（vs v1.3.2）

| 变化 | 解决的问题 | 验证方法 |
|------|----------|---------|
| **Step 0 Preflight Check**（强制） | gh 不在 PATH 时 AI 自行降级 | 故意卸 gh 跑技能，AI 立即停手报告 |
| **Step 1 项目信息收集**（AskUserQuestion） | 仓库定位/主理人用户名 AI 靠猜 | PROJECT.md 字段齐全，AI 不再问 |
| **12 文件脚手架**（含 .github/workflows + PULL_REQUEST_TEMPLATE） | 上版 CI 从未跑过（无 workflow 文件） | 初始化后 `gh workflow list` 看到 regression.yml |
| **任务粒度硬约束**（20min-2h） | 上版 5min 微任务稀释 review 信号 | T-002/3/4 合并为 1 个 T |
| **SETUP.md + 复盘质量门** | 上版 24 条 L-XXX 一半是 Windows PATH 陷阱 | L-XXX 全是决策/洞察类，环境陷阱进 SETUP.md |
| **推后项 spec 约束**（不允许"见 USER.md"占位） | 上版 T-008/T-009 空心 | 推后项验收标准完整 |
| **PR 模式唯一**（砍 Tag 模式） | 上版 AI 自行切 tag 模式 | 没有"## 4'. Tag SOP"分支 |

---

## 快速开始 (v1.3.3)

用户触发此技能时，**严格按 3 步走**：Preflight Check → 项目基础信息收集 → 路径与初始化。**不可跳步，不可 AI 自主猜测项目信息**。

### Step 0: Preflight Check（强制，不通过则停手）

在问用户任何事情之前，先验证工具链（命令退出码必须为 0）：

```bash
command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1 && git --version >/dev/null 2>&1
```

| 检查项 | 失败信息 | 修复指引 |
|--------|---------|---------|
| `command -v gh` 失败 | gh CLI 未安装 | `winget install GitHub.cli`（Win）/ `brew install gh`（Mac）|
| `gh auth status` 失败 | gh 未登录 | `gh auth login` |
| `git --version` 失败 | git 不可用 | 安装 git |

**任一失败 → 立即告诉用户并停手**：

> 工具链预检未通过：[失败项列表]。请修复后重新触发本技能。**我不会降级到任何替代模式。**

> **v1.3.3 关键变化**：移除了 v1.3.2 隐含的"工具不可用 → 自动降级"分支。原因是降级行为会绕过主理人接口和 CI 闭环（参考 2026-06-05 示例项目 项目的复盘：gh 不在 PATH 时 AI 直接切 tag 模式，导致 0 PR、0 CI、Q-001 答了 gh 路径后 AI 没切回 PR 模式）。

### Step 1: 项目基础信息收集（必问，写入 PROJECT.md）

Preflight 通过后，**用 AskUserQuestion 问用户**这些项目基础信息（不可 AI 自主猜测）：

| 字段 | 示例 | 写入 PROJECT.md 后用途 |
|------|------|----------------------|
| **GitHub owner/repo** | `<owner>/<repo>` | 远程仓库定位；PR 描述、verify 脚本、CI workflow 引用 |
| **主理人 GitHub 用户名** | `jun-jing` | PR 描述 @ 提及；自动 assign reviewer |
| **项目类型** | Web App / 静态站 / 工具脚本 / 库 / 其它 | 决定 verify 脚本范围（pnpm build / pytest / go test / etc.）|
| **commit 风格** | 中文 / 英文 / 中英混排 | commit message 模板、RETROSPECTIVE 引用风格 |

> 这些信息只问一次，写入 `async_comm/PROJECT.md` 后整个项目周期复用，**不再每次问**。SOP 每次启动**第一动作**是读 PROJECT.md 拿到仓库定位和约定。

### Step 2: 获取路径 + 初始化（**必须建 12 个文件**）

项目信息收集后，问路径：**请提供要初始化异步沟通的文件夹路径。**

然后告知用户：

> 初始化后，我将**严格按清单创建 12 个文件**（不只是 7 个文档，还有 .github 脚手架）：
>
> **async_comm/ 8 个文件**：
> 1. `USER.md` — 项目需求（frontmatter + P0/P1/P2 + 验收标准 + 完整 spec）
> 2. `TASK.md` — 任务清单（任务粒度 20min-2h，推后项带完整 spec）
> 3. `Q&A.md` — 任务内技术疑问
> 4. `REGRESSION.md` — 全量回归
> 5. `RETROSPECTIVE.md` — 复盘（只收决策/洞察，环境陷阱去 SETUP.md）
> 6. `PR_TEMPLATE.md` — PR 描述参考
> 7. `PROJECT.md` — 项目基础信息（owner/repo/主理人/约定/项目类型）
> 8. `SETUP.md` — 环境陷阱速查（Windows 编码/PATH/工具链等）
>
> **.github/ 脚手架（2 个文件）**：
> 9. `.github/PULL_REQUEST_TEMPLATE.md` — GitHub PR 模板
> 10. `.github/workflows/regression.yml` — CI workflow（v1.4.1 manual gate，手动触发）
>
> **空目录占位（2 个）**：
> 11. `async_comm/archive/.gitkeep`
> 12. `async_comm/tests/.gitkeep`
>
> 完成后我会跑 `gh workflow list` + `ls -la async_comm/` 确认全部就位，再交给你验收。

### Step 2.5: 远程仓库检查与创建（v1.4 新增）

**触发**：Step 0 Preflight 通过 + Step 2 脚手架完成。

**流程**：
1. AI 跑 `gh repo view` 试探当前目录是否已关联远程
2. **已有远程** → 直接用，不问（常见于 clone 已有项目后初始化）
3. **未关联** → 用 AskUserQuestion 询问：
   - 仓库名（默认 = 当前目录名）
   - 可见性（**默认 private** —— v1.4 用户偏好）
   - 描述（可空）
4. 跑命令一次性建仓 + 推 main：
   ```bash
   gh repo create <name> --$visibility \
     --description "<desc>" \
     --source=. --remote=origin --push
   ```
5. 验证：`gh repo view --json name,visibility,url` 输出新仓库信息

**关键参数说明**：
- `--source=.`：把当前目录作为来源
- `--remote=origin`：自动设置 `origin` 指向新仓库（**后续 push 不用再 `git remote add`**）
- `--push`：把 main 分支推上去（**不用再 `git push -u origin main`**）

**注意事项**：
- 这是 destructive 操作（在 GitHub 上创建真实仓库），但**只对全新仓库生效**
- 仓库名必须 GitHub 全局唯一，冲突时 gh 会报错 → 提示用户重选
- 用户的偏好是 **private**——询问时把 private 设为默认选项

---

等待用户输入路径后，**严格按清单创建 12 个文件**，初始化 git，设置定时任务。

---

## v1.3 核心变化（vs v1.2）

| 变化 | 解决的问题 | 验证方法 |
|------|----------|----------|
| 启动 SOP 第一步改为扫描 PR | 异步打回 | 提交 PR 后打回，下次启动自动 rework |
| 状态机从 5 态合并到 6 态 | PR 评审显式化 | 看 TASK.md 知道每个 PR 在哪一步 |
| T-ID 强制 `verify 方式` 字段 | 测试回归 | PR 描述包含 verify 结果 |
| 增加 PR 描述模板 | 主理人 review 效率 | 扫一眼就能决策 |
| 角色接口显式化（Conway） | 主理人介入点 | 主理人只用 GitHub Desktop |
| 阻塞超时从 48h+72h 简化为 72h | 简化流程 | 配置项更少 |

## v1.3.2 增量变化（vs v1.3.1）

| 变化 | 解决的问题 | 验证方法 |
|------|----------|----------|
| **Post-merge gate**（CI 只在 merge 后跑） | PR 阶段不阻塞主理人 review | AI 流程不等 CI |
| **T-FIX-XXX 自动修复** | main CI 失败时自动写修复任务 | TASK.md 出现 T-FIX-XXX（P0） |
| **去掉 Playwright E2E** | CI 跑 E2E 慢且脆，本地更可控 | regression.yml 默认无 e2e job |
| **regression.yml 约束可调** | 不同项目对 E2E/API 需求不同 | YAML 注释控制开关 |
| **启动扫描加 CI 检查** | AI 知道 main CI 失败 | 启动 SOP 第 0 步包含 gh run list |

详细设计见 [ARCHITECTURE.md](./ARCHITECTURE.md)，回滚内容见 [ARCHIVE_v1.1_20260601.md](./ARCHIVE_v1.1_20260601.md)。

---

## 架构视图 (Kruchten 4+1)

### 逻辑视图
- **主理人（人）**：通过 GitHub Desktop 看 PR，决策 Approve / Request Changes / Close
- **执行者（AI）**：领任务、写代码、commit、push、开 PR
- **观察者（人）**：只读 RETROSPECTIVE、Q&A

### 过程视图
```
[USER.md 需求] → [TASK.md 任务] → [代码+verify] → [commit+push] → [PR] → [主理人 review] → [merge] → [completed]
                          ↑________________Q&A 反馈_________________|
```

### 开发视图
- **单分支（main）多 commit**：所有任务在 main 上 commit + push
- **一个 T-ID = 一个 PR**：PR 自动跟踪该 T-ID 的所有 commit
- **配套目录**：
  - `tests/` — 单元测试
  - `verify_tXXX.sh` — 每个 T-ID 的端到端验证脚本

### 物理视图
- 本地 git + GitHub Desktop + 远程 repo（GitHub / Gitee / 自建均可）

### 场景视图
1. **正常**：pending → in_progress → in_review → completed
2. **打回**：in_review → in_progress（重做）→ in_review
3. **关闭**：in_review → dropped
4. **阻塞**：in_progress → blocked（Q&A）→ in_progress
5. **Q&A 超时**：blocked（72h）→ dropped

---

## 角色与契约

按 Conway 定律——架构反映组织。1 主理人 + 1 AI 的组织，接口必须两边都清晰：

| 角色 | 输入 | 输出 | 工具 |
|------|------|------|------|
| **主理人** | GitHub Desktop PR 列表 | Merge / Request Changes / Close | GitHub Desktop |
| **执行者** | TASK.md 的 pending T-ID | commit + push + PR | Claude + git/gh |
| **观察者** | RETROSPECTIVE.md / Q&A.md | （只读） | 任意编辑器 |

**硬约束**：
- 主理人**不读** TASK.md（只通过 PR 看工作）
- 执行者**不直接**找主理人（通过 PR 评论异步沟通）
- Q&A.md 仅用于**任务内的技术疑问**；PR 评审的反馈通过 PR comment，不进 Q&A

---

## 第一步：创建文档结构 (v1.3.3：12 文件脚手架)

在用户提供的路径下**严格按清单创建 12 个文件**（8 文档 + 2 .github + 2 占位）。内联模板见 [初始化必建脚手架](#初始化必建脚手架v133-新增) 章节。

```
路径/
├── async_comm/
│   ├── USER.md              ← 用户写需求（frontmatter + P0/P1/P2 + 完整 spec）
│   ├── TASK.md              ← 执行者任务清单（任务粒度 20min-2h，推后项带完整 spec）
│   ├── Q&A.md               ← 任务内技术疑问
│   ├── REGRESSION.md        ← 全量回归测试
│   ├── RETROSPECTIVE.md     ← 复盘（v1.3.3 起只收决策/洞察，环境陷阱去 SETUP.md）
│   ├── PR_TEMPLATE.md       ← PR 描述参考模板
│   ├── PROJECT.md           ← 项目基础信息（v1.3.3 新增，owner/repo/主理人/约定）
│   ├── SETUP.md             ← 环境陷阱速查（v1.3.3 新增，Windows PATH/编码等）
│   ├── archive/             ← 已完成任务归档
│   │   └── .gitkeep
│   ├── tests/               ← 单元测试
│   │   └── .gitkeep
│   ├── verify_t001.sh       ← T-001 的验证脚本
│   └── verify_t002.sh
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md   ← GitHub PR 模板（v1.3.3 新增，PR 描述必填字段）
    └── workflows/
        └── regression.yml         ← CI workflow（v1.4.1 manual gate，手动触发）
```

### 文档分工 (v1.3.3)

| 文件 | 用途 | 写入方 | 频率 |
|------|------|--------|------|
| USER.md | 需求（frontmatter + P0/P1/P2 + 验收） | 主理人 | 每次迭代 |
| TASK.md | 任务清单（粒度 20min-2h，推后项 spec） | 执行者 | 持续 |
| Q&A.md | 任务内技术疑问 | 执行者 | 遇阻时 |
| REGRESSION.md | 全量回归 | 执行者 | 合入 main 后 |
| RETROSPECTIVE.md | 复盘（关联 T-ID，**只收决策/洞察**） | 执行者 | 每 T-ID 完成后 |
| PR_TEMPLATE.md | PR 描述参考 | （只读） | — |
| PROJECT.md | 项目基础信息（owner/repo/主理人/约定） | 主理人（init）+ AI（读） | init 时一次 |
| SETUP.md | 环境陷阱速查（**不**写进 RETROSPECTIVE） | 执行者 | 遇环境问题时 |
| .github/PULL_REQUEST_TEMPLATE.md | GitHub PR 模板 | （只读） | — |
| .github/workflows/regression.yml | CI workflow（v1.4.1 手动触发） | （只读） | — |

---

## USER.md 模板

```markdown
---
version: 2026-06-04-001
lastUpdated: 2026-06-04T00:00:00Z
updateCount: 1
currentIteration: 1
---

# 用户需求文档

> 项目目标与核心需求

---

## 版本变更日志

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 2026-06-04-001 | 2026-06-04 | 初始版本 |

---

## 项目概述
[简述这个项目要做什么]

## 背景说明
[为什么要做这个项目，有什么约束]

## 核心需求

### P0 - 必做
1. [需求1]
2. [需求2]

### P1 - 重要
3. [需求3]

### P2 - 优化
4. [需求4]

---

## 验收标准

- [ ] 标准1：xxx
- [ ] 标准2：xxx

---

## 重要说明
[任何执行者需要知道的关键信息]

---

## 迭代记录

### 迭代规划完整性要求（v1.3.3 硬约束）

**每个迭代的规划必须包含 P0 / P1 / P2 全部三类**：

- **P0**：本迭代必做（验收标准 100% 详细）
- **P1**：本迭代重要（验收标准 ≥ 80% 详细）
- **P2**：本迭代规划/下迭代展开（验收标准 ≥ 50% 详细，**不允许只写"见 TASK.md"**）

**为什么**：上版 USER.md 把 P2 写成"恢复 logos / stats / testimonials"，没有验收标准。TASK.md 的 T-008/T-009 推后时也只写"见 USER.md"——形成"两边都没规划"的空心。

**AI 写完 USER.md 后必须自检**：
- 当前迭代的 P0/P1/P2 是否都有验收条目
- P2 至少有 50% 详细度（即每条都有"是什么 + 验收什么"，但具体实现可迭代3 展开）
- 推后到下个迭代的条目，**也必须**有验收标准

### 迭代1（<日期>）
- 状态：进行中 / 已完成
- 新增需求：xxx
- 任务关联：见 TASK.md 迭代1任务
- P0 完成率：N/M
- P1 完成率：N/M
- P2 完成率：N/M（推后到迭代 2 的有几条）

---

## 修改协议

执行者在读取 USER.md 时，应该：
1. 检查 version 字段
2. 与上次读取的版本对比
3. 如果 version 变化，记录变更内容
4. 如果 currentIteration 变化，说明进入了新迭代
   - 将旧迭代的所有任务标记为 completed
   - 开始执行新迭代的任务
5. 如果没有变化，跳过解析直接使用缓存
```

---

## TASK.md 模板 (v1.3.3 升级：任务粒度硬约束 + 推后项 spec 强制)

**v1.3.3 核心变化**：
1. **任务粒度硬约束**：单个 T-ID **20min ≤ 耗时 ≤ 2h**（v1.3.3 引入）
2. **推后项 spec 强制**：迭代 N 标记的"推后到迭代 N+1"任务，**必须**带完整验收标准（v1.3.3 引入）
3. T-ID 必含 `verify 方式` 字段（v1.3 已有）
4. 必含"评审中"表（v1.3 已有）

### 任务粒度规则（v1.3.3 硬约束）

| 粒度 | 处理方式 |
|------|---------|
| < 20 分钟 | **必须**合并到相邻 T-ID（v1.3.3 之前：上版 T-002/3/4 各自 5-10min，违反此规则）|
| 20min ~ 2h | **理想粒度**，按这个切 |
| \> 2 小时 | **必须**拆分成 2-3 个 T-ID |

**为什么**：单个 PR 承载的工作太少（如 5min），主理人 review 价值被稀释——打开 PR 列表看 5 个 PR 都是 5 行 diff。粒度太粗则 review 风险高，1 个 PR 改动 2000 行主理人难决策。

**AI 写完 TASK.md 后必须自检**：
- 检查所有 T-ID 的预估耗时
- 任何不在 [20min, 2h] 区间的 T-ID，**必须重新切分**再写入 TASK.md
- 不允许"先这样吧，跑起来再说"

### 推后项 spec 强制（v1.3.3 硬约束）

如果某 T-ID 标记为"推后到迭代 N+1"，**必须**同时填完整：

- 验收标准（具体可验证的条目）
- verify 方式（命令/脚本）
- 关联需求（USER.md 的哪条 P0/P1/P2）
- 关联文件（预计改哪些）

**不允许**只写"见 USER.md"、"迭代 2 规划"、"后续展开"等占位。**v1.3.3 起 TASK.md 看到占位描述必须重新填**。

**为什么**：上版 T-008/T-009 推后时只写了"见 USER.md"，但 USER.md 也没详细展开——下个迭代实际启动时发现要从空白开始规划。

### T-ID 必含字段（v1.3 已有，v1.3.3 强化，v1.4 新增 unit-test，v1.4.2 新增 screenshot）

每个 T-ID 必含：
- **T-ID**（T-001 等编号）
- **任务描述**（1-2 句）
- **预估耗时**（v1.3.3 新增字段，必须在 20min-2h 区间）
- **验收标准**（具体可验证）
- **verify 方式**（命令/脚本路径）
- **关联需求**（USER.md 的 P0/P1/P2 编号）
- **关联文件**（预计改哪些）
- **unit-test**（v1.4 新增硬约束）—— 单元测试文件路径
  - 纯函数 / 组件类 T-ID **必须**填，如 `tests/lib/keyword.test.ts`
  - UI/配置类 T-ID 可标 `N/A`（如纯样式调整）
  - 没填且不是 N/A 的 T-ID **不允许开 PR**（PR 模板的 `pnpm test` 复选框未勾选）
- **screenshot**（v1.4.2 新增，可选）—— UI 改动是否要截图
  - 填 `yes` 或 `no`（默认 `no`，非 UI 改动不用特意填）
  - 填 `yes` 的 T-ID：PR 描述需粘 CI artifact 链接（启用 `screenshots` job 后）或本地截图
  - **不强制**——与 `unit-test` 不同，不开 PR 硬约束（截图是 review 体验优化，不是质量门）

```markdown
# 任务清单 (v1.3)

> 执行者按此清单推进项目，每项完成后开 PR

---

## 项目信息
- 用户需求：见 USER.md
- 当前状态：进行中
- 队列版本：2026-06-04-001
- 当前迭代：1
- 锁：T-001 (2026-06-04 14:00, 15min 超时)  ← 执行中任务的锁，空则表示无锁

---

## 任务状态定义 (v1.3 6 状态)

| 状态 | 含义 | 可转换状态 |
|------|------|------------|
| `pending` | 待领取 | → in_progress |
| `in_progress` | 进行中（本地写代码） | → in_review, blocked |
| `in_review` | PR open，等待主理人 | → in_progress（打回）, completed（merge）, dropped（close） |
| `completed` | PR merged，已归档 | （终态） |
| `blocked` | 阻塞中（Q&A 等待） | → in_progress, dropped |
| `dropped` | 已放弃 | （终态） |

### 状态转换规则
- 领取任务：pending → in_progress，加锁
- 本地完成 + push + 开 PR：in_progress → in_review
- PR 合并：in_review → completed，移到 archive/
- PR 打回：in_review → in_progress，追加 commit 到原 PR
- PR 关闭：in_review → dropped（记录原因）
- 遇 Q&A：in_progress → blocked，写 Q&A.md
- Q&A 解决：blocked → in_progress
- Q&A 超时（72h）：blocked → dropped

### 阻塞超时机制
- 默认超时：72 小时（v1.3 简化）
- 超时处理：标记 dropped，跳过该 T-ID
- 用户事后回答：不复活（已 dropped），在 RETROSPECTIVE 记录"该问题被跳过"

### 任务领取规则
1. 严格顺序：P0 → P1 → P2
2. 同优先级按 T-ID 升序
3. 阻塞任务不参与排序
4. 每次只领一个，完成（或进入 in_review）后才能领下一个

---

## 待执行任务

### 迭代1

#### 🔴 P0 - 必做

⬜ [T-001] [任务1 描述]
- 验收标准：xxx
- **verify 方式**：`bash verify_t001.sh`
- 相关需求：USER.md P0-1
- 关联文件：src/xxx.py, tests/test_xxx.py

⬜ [T-002] [任务2 描述]
- 验收标准：xxx
- **verify 方式**：`pytest tests/test_xxx.py`
- 相关需求：USER.md P0-2

#### 🟡 P1 - 重要

⬜ [T-003] [任务3 描述]
- 验收标准：xxx
- **verify 方式**：`bash verify_t003.sh`
- 相关需求：USER.md P1-1

#### 🟢 P2 - 优化

⬜ [T-004] [任务4 描述]
- 验收标准：xxx
- **verify 方式**：`bash verify_t004.sh`
- 相关需求：USER.md P2-1

---

## 进行中任务

| T-ID | 任务 | 优先级 | 领取时间 | 当前 commit | verify 状态 |
|------|------|--------|----------|-------------|-------------|
|      |      |        |          |             |             |

---

## 评审中任务

| T-ID | 任务 | PR 编号 | 优先级 | 提交时间 | PR 状态 | review 决策 |
|------|------|---------|--------|----------|---------|-------------|
|      |      |         |        |          |         |             |

---

## 阻塞中任务

| T-ID | 阻塞 Q-ID | 阻塞开始 | 等待时长 |
|------|-----------|----------|----------|
|      |           |          |          |

---

## 已完成任务

| T-ID | 任务 | 完成时间 | 耗时 | 归档文件 | PR 编号 |
|------|------|----------|------|----------|---------|
|      |      |          |      |          |         |

---

## 完成流程 (v1.4.1 升级：PROJECT.md 入口 + t-XXX 分支 + manual gate)

**v1.3.3 核心变化**：SOP 入口改为"读 PROJECT.md"，拿到仓库定位和协作约定；每个 T-ID 用 t-XXX 临时分支（一个 T-ID 一个 PR，PR base = main）；v1.3.3 起 PR 模式为唯一模式，Tag 模式已移除。

### SOP 入口（v1.3.3 强制第一步）

每次 SOP 启动时，**第一动作**是读 `async_comm/PROJECT.md`：

1. 读 `githubOwner` / `githubRepo` / `maintainer` / `commitStyle` 等字段
2. 校验 `workflowMode == PR`（v1.3.3 起这是唯一模式）
3. **不可在 SOP 中途切换模式或修改 PROJECT.md**
4. 工具不可用 → 写 Q&A.md 等主理人决策，**不擅自降级**

1. 读取 TASK.md 获取当前任务（看"锁"字段）
2. **检查锁**：如有任务在 in_progress 且锁未超时（15min），跳过本轮
3. 领取任务：pending → in_progress，加锁
4. **创建工作分支**（v1.3.3 分支策略）：每个 T-ID 从 main 拉临时分支
   - `git checkout -b t-XXX main`
   - 单 T-ID 全生命周期在该分支上工作（commit / push / 后续 rework）
5. 按 verify 方式实现（边写边跑测试）
6. 完成后跑 verify，**未通过不进入下一步**
7. 写 commit：`T-001: 实现xxx子功能`（多次细粒度 commit）
8. **git push origin t-XXX**
9. **生成 PR 描述**：按 PR_TEMPLATE.md 填好，存到 `.github/PR_BODY.md`
10. **开 PR**：`gh pr create --draft --title "T-001: xxx" --body-file .github/PR_BODY.md --base main`
11. **★ 不再查 `gh pr checks`**（v1.3.2）：CI 在 PR 阶段不跑，AI 不阻塞
12. 补充 verify 结果到 PR 描述
13. **gh pr ready**（PR 描述齐全后）
14. 更新 TASK.md：in_progress → in_review，清锁
15. **不等待 review**，开始下一个 T-ID

> **关键**：第 14-15 步让 PR 处于"等 review"状态，但 AI 不阻塞。CI 在主理人 merge 后才跑（详见 [CI_GUIDE.md](./CI_GUIDE.md)）。

### CI 失败处理（v1.3.2：T-FIX-XXX 修复前推）

**触发时机**：AI 启动扫描 PR 时，**多看一步** main 的最近 CI 状态。

```bash
# 1. 查 main 分支最近一次 CI
gh run list --workflow=regression.yml --branch=main --limit 1

# 2. 看具体 run
gh run view <run_id>
# 输出示例：
# ✓ unit        1m23s
# ✓ v13-verify  0m12s
# ✗ build       2m45s  ← 失败
# Status: completed, conclusion: failure

# 3. 看失败日志
gh run view <run_id> --log-failed
```

**Fix Forward 流程**：

```
main CI 失败
    ↓
[AI 下次启动扫描到]
    ↓
写 T-FIX-XXX（P0 优先级）
   - 关联：被 T-XXX 引入
   - verify 方式：gh run list 显示 main CI 通过
    ↓
T-FIX 进入 pending（最先被领）
    ↓
AI 修复 + commit + push
    ↓
[触发新 CI 在 main 跑]
    ↓
   ┌─ pass ─→ T-FIX → completed
   │
   └─ fail ─→ 再写 T-FIX-002，连续 3 次失败升级 blocked
```

**关键命令**：
```bash
gh run list --workflow=regression.yml --branch=main --limit 5  # 看 main CI 状态
gh run view <run_id> --log-failed                              # 读失败日志
gh run rerun <run_id>                                          # 重跑（不开新 commit）
```

**设计原则**：
- **不阻塞 PR review**：CI 失败不影响主理人 review 流程
- **fix forward**：失败时创建新任务修复，不回头改历史
- **max retry = 3**：避免无限循环（3 次失败 → blocked + Q&A）
- **失败要读 log**：不能盲目改代码

完整 CI 模板见 [CI_GUIDE.md](./CI_GUIDE.md)。

---

## 异步打回处理（v1.3 核心）

每次执行者启动时，**第一动作**是扫描 PR 状态：

```bash
gh pr list --state all --json number,title,state,reviewDecision,mergedAt
```

按 PR 状态分类处理：

| PR 状态 | reviewDecision | AI 行为 |
|---------|----------------|---------|
| **merged** | 任意 | 该 T-ID → completed，归档到 archive/，解下一个 |
| **closed**（未 merge） | 任意 | 该 T-ID → dropped，写入关闭原因（从 comment 抓），解下一个 |
| **open** | CHANGES_REQUESTED | 该 T-ID → in_progress，拉最新代码，rework，**追加 commit 到原 PR**（不开新 PR） |
| **open** | APPROVED | 等待主理人手动 merge，AI 跳过 |
| **open** | （无 review） | PR 刚开，保持 in_review，AI 跳过 |
| **无对应 PR** | — | T-ID 还在 in_progress，可能 commit 后没开 PR，开 PR |

**核心原则**：
- PR 是动态对象，rework 追加 commit 到原 PR（不创建新 PR）
- "打回"不是失败，是"延迟确认"
- 主理人不需要实时在线，PR 列表是唯一接口
- rework 多次都在同一 PR，主理人看累积 diff

### Rework 流程（CHANGES_REQUESTED）

```bash
# 1. 确认 T-ID 处于 in_review 状态但 review 是 CHANGES_REQUESTED
gh pr list --search "T-001 in:title" --json reviewDecision

# 2. 切换回该 T-ID 的工作分支（v1.3.3 分支策略）
git checkout t-XXX
git pull origin main  # 拉最新 main（主理人可能 merge 了其他 PR）

# 3. 重新进入 in_progress 状态

# 4. 修改代码 + 新 commit
git commit -m "T-001: 修复review指出的xxx问题"

# 5. push 到同一 PR（PR 自动跟踪该分支的 commit）
git push origin t-XXX

# 6. PR 自动更新
gh pr ready  # 如果之前是 draft

# 7. 更新 TASK.md：in_progress → in_review
```

### 边缘情况：PR 冲突

主理人 merge 了其他 PR 后，原 PR 可能与 main 冲突。处理：

```bash
git fetch origin main
git rebase origin/main  # 优先用 rebase 保持线性
# 如果有语义冲突（不是简单的 merge conflict）：
# → 升级为 blocked，写 Q&A.md，请主理人决策
```

---

## Q&A.md 模板

```markdown
# 问答记录 (Q&A.md)

> 执行者在推进项目过程中遇到的疑问和困惑记录

---

## 记录格式

| Q-ID | 日期 | 阶段 | 问题/困惑 | 状态 |
|------|------|------|-----------|------|
| Q-001 | 2026-06-04 | T-002 | 关键词清洗遇到空字符串如何处理？ | 已回答 |

---

## 待回答问题

（执行者无法确定的问题记录在这里，等待用户回答）

---

## 已回答问题

| Q-ID | 日期 | 问题 | 答案 | 触发动作 |
|------|------|------|------|----------|
| Q-001 | 2026-06-04 | 关键词清洗遇到空字符串如何处理？ | 跳过，保留为 None | 重试 T-002 |
```

---

## REGRESSION.md 模板 (v1.3 升级)

```markdown
# 回归测试

> 每次 PR merge 后跑全量回归，确保核心功能未退化

---

## 回归触发时机

| 时机 | 触发者 | 范围 |
|------|--------|------|
| PR merge 后 | 下次执行者启动时 | 全量 |
| 主理人手动触发 | 主理人运行 `bash regression.sh` | 全量 |
| 执行者启动时（自动） | 定时任务 | 抽样（最近 3 个 T-ID 的 verify） |

---

## 回归测试项

| 检查项 | verify 命令 | 上次状态 | 当前状态 |
|--------|-------------|----------|----------|
| T-001 功能 | `bash verify_t001.sh` | ⬜ | ⬜ |
| T-002 功能 | `bash verify_t002.sh` | ⬜ | ⬜ |
| T-003 功能 | `bash verify_t003.sh` | ⬜ | ⬜ |
| 全量单元测试 | `pytest tests/` | ⬜ | ⬜ |

---

## 测试结果

- 最后测试：2026-xx-xx
- 通过项：N/M
- 失败项：[列表]

---

## 修复记录

| 日期 | 问题 | 修复方案 | 关联 T-ID |
|------|------|----------|----------|
|      |      |          |          |

---

## 复盘记录（经验沉淀）

> 每次任务推进后的复盘，沉淀可复用的经验

### 复盘历史

（随着项目推进，经验会沉淀在这里，供未来参考）
```

---

## RETROSPECTIVE.md 模板 (v1.3.3 升级：质量门 + 经验分类)

**v1.3.3 核心变化**：
1. **质量门**：L-XXX 只收**决策/洞察/取舍**类经验，**环境陷阱去 SETUP.md**（v1.3.3 引入）
2. 每条经验**必须**关联 T-ID（v1.3 已有）

### 质量门（v1.3.3 硬约束）

**L-XXX 收什么**（保留）：

- ✅ 决策类（"为什么选 A 不选 B"）
- ✅ 洞察类（"这个项目有 X 规律"）
- ✅ 取舍类（"性能 vs 简洁，我们选了 X"）
- ✅ 流程类（"PR review 一次通过关键是 verify 充分"）

**L-XXX 不收什么**（移到 SETUP.md）：

- ❌ Windows 编码报错（Python GBK、taskkill 路径）
- ❌ 工具链缺失（`gh` 不在 PATH、`pnpm` EPERM）
- ❌ 命令行语法（`cmd //c` 才能跑 taskkill）
- ❌ Next.js 16 框架行为（next-intl 重定向）

**为什么这样分**：上版 24 条 L-XXX 有一半是 Windows 编码 / PATH 陷阱——这些是"环境问题"，不写一遍下次还会忘，但写进 L-XXX 会**淹没**真正的决策/洞察。环境陷阱应该写进 SETUP.md 做一次性沉淀，L-XXX 留给有思考含量的经验。

**AI 写完 RETROSPECTIVE 后必须自检**：
- 每条 L-XXX 是否属于"决策/洞察/取舍"类
- 任何环境陷阱类条目，**必须**移到 SETUP.md（创建对应 TRAP-XXX）
- 不允许"L-XXX 写环境陷阱"的混用

```markdown
# 复盘记录

> 每条经验必须能追溯到 T-ID，事后能复盘

---

## 复盘格式

| ID | T-ID | 日期 | 任务阶段 | 经验/教训 | 可复用点 | 标签 |
|----|------|------|----------|-----------|----------|------|
| L-001 | T-001 | 2026-06-04 | 关键词清洗 | 边界空字符串需显式处理 | 增加空值守卫 | #技术方案 |
| L-002 | T-002 | 2026-06-04 | 报告生成 | PR review 一次通过关键是 verify 充分 | 三层验证金字塔 | #效率 |

---

### 复盘历史

（随着项目推进，经验沉淀在这里）

---

## 经验分类索引

### #技术方案
（暂无）

### #需求洞察
（暂无）

### #效率
（暂无）

### #沟通
（暂无）

---

## 每轮复盘引导

执行任务后，请回答以下问题并记录：

1. **本次关键决策**：这次我做了什么决定？为什么？
2. **收获**：学到了什么？
3. **教训**：哪里可以做得更好？
4. **可复用点**：下次同类任务怎么做得更快？

格式：L-XXX | T-XXX | 日期 + 任务阶段 + 经验/教训 + 可复用点 + 标签
```

---

## PR 描述生成（v1.3 核心）

执行者开 PR 时，按 [PR_TEMPLATE.md](./PR_TEMPLATE.md) 生成 `.github/PR_BODY.md`：

```bash
# 1. 复制模板到项目的 .github/PR_BODY.md
# 2. 填好所有字段
# 3. 开 PR
gh pr create --draft --title "T-XXX: 任务名" --body-file .github/PR_BODY.md
# 4. 补充 verify 结果到 PR 描述（如 gh pr edit --body ...）
# 5. 标记 ready
gh pr ready
```

完整 PR 描述模板见 [PR_TEMPLATE.md](./PR_TEMPLATE.md)。

---

## PROJECT.md 模板 (v1.3.3 重命名自 MODE.md，简化)

**作用**：项目基础信息的单一事实源。SOP 每次启动**第一动作**是读这里，拿到仓库定位、主理人用户名、协作约定，避免 AI 靠猜。

```markdown
---
githubOwner: <owner>
githubRepo: <repo>
maintainer: <GitHub 用户名>
projectType: <Web App | 静态站 | 工具脚本 | 库 | 其它>
commitStyle: <中文 | 英文 | 中英混排>
workflowMode: PR
initAt: <ISO 日期时间>
schedulerId: <cron job id, 形如 async-comm-<project>>
schedulerCreatedAt: <ISO, schedule 创建时间>
schedulerStatus: active  # active | lost
---

# 项目基础信息 (PROJECT.md)

> 本文件由初始化时主理人确认，整个项目周期复用。修改需走 v1.3.3 的更新协议。

---

## 仓库信息

| 字段 | 值 |
|------|----|
| **GitHub owner/repo** | `<owner>/<repo>` |
| **主分支** | `main` |
| **默认远程名** | `origin` |
| **PR 模板路径** | `.github/PULL_REQUEST_TEMPLATE.md` |
| **CI workflow** | `.github/workflows/regression.yml` |

## 主理人

| 字段 | 值 |
|------|----|
| **GitHub 用户名** | `<username>`（PR 描述 @ 提及、assign reviewer 用）|

## 协作约定

| 项 | 约定 |
|----|------|
| **commit 风格** | `<中文 / 英文 / 中英混排>` |
| **commit 格式** | `T-XXX: 子功能描述`（TASK.md 任务号 + 冒号 + 简述）|
| **PR 标题格式** | `T-XXX: 任务名`（与 commit 一致）|
| **协作模式** | **PR 模式**（每 T-ID 一个 PR，v1.3.3 起强制，不再支持 Tag 模式）|

## 项目类型与 verify

| 项 | 约定 |
|----|------|
| **项目类型** | `<Web App / 静态站 / 工具脚本 / 库 / 其它>` |
| **build 工具** | `<pnpm / npm / yarn / go / pip / etc.>` |
| **verify 范围** | `<pnpm build / pytest / go test / etc.>` |
| **CI 触发时机** | 手动 workflow_dispatch（v1.4.1 manual gate）|
| **CI 失败处理** | AI 自动写 T-FIX-XXX 任务（P0）|

## 初始化元数据

| 字段 | 值 |
|------|----|
| **初始化时间** | `<ISO 日期时间>` |
| **技能版本** | v1.4.1 |
| **触发预检** | Preflight Check 通过 |

## Scheduler 状态（v1.3.3-patch2 新增）

> **必填字段**——AI 启动 SOP 时必须先读这三个字段，确认 schedule 还在跑。

| 字段 | 值 |
|------|----|
| **schedulerId** | `<cron job id>`（用 `CronList` 查到） |
| **schedulerCreatedAt** | `<ISO>` |
| **schedulerStatus** | `active` / `lost` |

**状态说明**：
- `active`：schedule 正常运行（默认期望状态）
- `lost`：**schedule 丢失**（7 天 expire / 误删 / 系统异常），需要用 `schedulerId` 同名重建

**AI 启动 SOP 自检**（v1.3.3-patch2 新增）：
1. 读 `schedulerId` 字段
2. 跑 `CronList` 确认同 id 的 schedule 还在
3. 如果不在 → status = `lost` → **不要自动重建**（重建需要主理人确认 + 完整 SOP prompt），写 Q&A.md 等决策
4. 如果在且 status == `active` → 继续 SOP

**为什么**：2026-06-05 示例项目 项目里 AI 误删 cron 后无任何可见信号，主理人过几小时才发现。PROJECT.md 加 status 字段后，AI 每次启动都能自检，主理人也能 `cat async_comm/PROJECT.md` 一眼看到 schedule 当前状态。

### Scheduler 重启历史

| 日期 | 旧 id | 新 id | 原因 | 操作人 |
|------|-------|-------|------|--------|
|      |       |       |      |        |

（每次 schedule 被删/重建，在这里追加一行，便于追溯）

---

## 修改协议

SOP 执行时：
1. **第一动作**：读 `async_comm/PROJECT.md`，拿到 `githubOwner` / `githubRepo` / `maintainer` / `commitStyle` 等字段
2. **不要重新询问主理人**（已锁定）
3. 遇到工具不可用：**写 Q&A.md 等主理人决策**，不擅自降级
4. 修改本文件需主理人明确同意（v1.3.3 起硬约束）
```

---

## 初始化必建脚手架（v1.3.3 新增）

> **触发事件**：2026-06-05 示例项目 项目跑完后复盘发现，**初始化时 AI 只建了 7 个文档，完全没建 .github 脚手架**——导致 CI 闭环从来没跑过、PR 描述靠 AI 自由发挥。这是最严重的"协作骨架漏洞"。
>
> v1.3.3 起，**以下 4 个内联模板**必须在 Step 2 初始化时原样写入目标项目。AI 不允许"按需精简"或"合并"。

### 文件 1：`.github/workflows/regression.yml`

```yaml
# regression.yml - v1.4.1 manual gate
# 触发：仅手动 workflow_dispatch（避免每次 merge 浪费 Actions 分钟）
# 失败处理：AI 启动时 gh run list 自检，看到失败自动写 T-FIX-XXX 任务到 TASK.md
# 优势：默认 0 分钟/天，月跑 20-30 次 ≈ 200 分钟
# 注：Vercel 部署走 GitHub 原生集成（不消耗 Actions），不需要 deploy.yml
#
# ★★★ step 顺序硬约束（v1.3.3 修补，根因见 RETROSPECTIVE L-001 / Q&A Q-001）★★★
#   pnpm/action-setup@v4 必须在 actions/setup-node@v4 之前
#   原因：actions/setup-node@v4 的 cache: 'pnpm' 算 cache hash 时需要 pnpm 在 PATH；
#         反过来 Node 先跑会报 "Unable to locate executable file: pnpm"，main CI 必挂
#
# ★ 格式硬约束：所有 job 的 steps 之间必须留空行（包括 unit 这种短 job）
#   原因：edit/replace_all 用 pattern 匹配时，空行是关键标识；不统一会导致多 job workflow 漏改一半
#   经验：2026-06-05 示例项目 项目 T-FIX-001 改 build 改对了、unit 因没空行漏改，触发 T-FIX-002
name: regression

on:
  workflow_dispatch:  # v1.4.1 起只手动触发（避免每次 merge 浪费 Actions 分钟）
  # push:               # ← 取消注释切回自动模式（不推荐，单人项目月消耗大）
  #   branches: [main]

# 手动触发不撞车，不需要 concurrency 取消逻辑

jobs:
  # 默认 job：编译/构建（项目类型决定具体命令）
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # ★ pnpm 必须在 Node 之前（cache: 'pnpm' 依赖 pnpm 在 PATH）
      - name: Setup pnpm
        if: ${{ hashFiles('pnpm-lock.yaml') != '' }}
        uses: pnpm/action-setup@v4
        with:
          version: 10

      - name: Setup Node
        if: ${{ hashFiles('package.json') != '' }}
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'pnpm'

      - name: Install
        if: ${{ hashFiles('package.json') != '' }}
        run: pnpm install --frozen-lockfile

      - name: Build
        if: ${{ hashFiles('package.json') != '' }}
        run: pnpm build

  # 可选 job：单元测试（默认开启）
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # ★ pnpm 必须在 Node 之前（同 build job 约束）
      - name: Setup pnpm
        if: ${{ hashFiles('pnpm-lock.yaml') != '' }}
        uses: pnpm/action-setup@v4
        with:
          version: 10

      - name: Setup Node
        if: ${{ hashFiles('package.json') != '' }}
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'pnpm'

      - name: Install
        if: ${{ hashFiles('package.json') != '' }}
        run: pnpm install --frozen-lockfile

      - name: Test
        if: ${{ hashFiles('package.json') != '' }}
        run: pnpm test --if-present

  # 可选 job：E2E（默认关闭，按需开启）
  # e2e:
  #   runs-on: ubuntu-latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - run: pnpm playwright install --with-deps
  #     - run: pnpm test:e2e
```

**AI 写完后验证**（v1.3.3 加严，三条全过才算 OK）：
1. `gh workflow list` 应能看到 `regression` workflow
2. **顺序自检（新增）**：
   ```bash
   # pnpm-setup 行号必须 < setup-node 行号（任何 job 都得满足）
   grep -n "pnpm/action-setup@v4" .github/workflows/regression.yml
   grep -n "actions/setup-node@v4" .github/workflows/regression.yml
   # 人工对比：前者行号必须 < 后者
   ```
3. **空行一致性自检（新增）**：
   ```bash
   # 所有 job 的 steps 之间必须有空行
   awk '/^  [a-z]+:$/{job=$0; next} /^      - name:/{if(prev!="" && prev!~/^      - name:/ && prev!~/^      #/){print job" 缺空行前导："prev} prev=$0}' .github/workflows/regression.yml
   # 不输出即合格
   ```

### 文件 2：`.github/PULL_REQUEST_TEMPLATE.md`

```markdown
<!-- PULL_REQUEST_TEMPLATE.md - v1.3.3 起每个 PR 必填 -->

## T-ID

<!-- 这个 PR 关联的任务 ID（必填，从 TASK.md 抄）-->
T-XXX

## 任务描述

<!-- 一句话说这个 T-ID 做什么 -->
-

## 改动文件

<!-- 主要改了哪些文件，- 列出 -->
-

## verify 结果

<!-- 跑 verify_tXXX.sh 的输出（粘关键行，不要全粘）-->
- 命令：`bash async_comm/verify_tXXX.sh`
- 结果：✅ PASS / ❌ FAIL（粘关键输出）

## 截图（如适用）

<!-- UI 改动附 web-access 截图，路径在 async_comm/verify_screenshots/T-XXX/ -->
-

## 关联需求

<!-- USER.md 的哪条 P0/P1/P2 -->
USER.md P0-N / P1-N / P2-N

## checklist

- [ ] verify 脚本本地跑过且 PASS
- [ ] 中英文内容（en + zh）已同步（如适用）
- [ ] commit message 格式：`T-XXX: 子功能描述`
- [ ] 复盘 RETROSPECTIVE.md 已写
- [ ] archive/ 已归档本次 T-ID
```

**AI 写完后验证**：开一个 draft PR，看 PR 描述区是否套用了这个模板。

### 文件 3：`async_comm/SETUP.md`（环境陷阱速查）

```markdown
---
initAt: <ISO 日期>
lastUpdated: <ISO 日期>
---

# 环境陷阱速查 (SETUP.md)

> **本文件收纳"环境配置陷阱"类经验**——如 Windows 编码、PATH 缺失、build 工具报错等。
> 决策/洞察类经验写 RETROSPECTIVE.md，本文件**只**收录环境陷阱。
> 来源：v1.3.3 复盘质量门——上版 24 条 L-XXX 一半是 PATH/编码问题，污染了 RETROSPECTIVE。

---

## 类别索引

### Windows 平台

（暂无）

### Python / 脚本工具

（暂无）

### Next.js / 框架

（暂无）

### Git / gh CLI

（暂无）

---

## 陷阱记录

### TRAP-XXX | <日期> | <类别> | <问题>

- **现象**：<报错信息或行为>
- **根因**：<为什么会出现>
- **修复**：<具体解决命令或配置>
- **验证**：<怎么确认修好>

```bash
# 复现命令
<command>

# 修复命令
<fix-command>
```

---

## 修改协议

- **新陷阱**：发现后**立即**追加到本文件，**不要**写进 RETROSPECTIVE
- **修过的陷阱**：标记为 ✅ 已解决，保留作为历史
- **决策/洞察**：写 RETROSPECTIVE.md，本文件**不收**
```

---

## 初始化验证清单（v1.3.3 新增）

Step 2 完成后，**AI 必须跑这些命令并把输出贴给主理人**：

```bash
# 1. 12 个文件都建好
ls -la async_comm/ async_comm/archive/ async_comm/tests/ .github/workflows/

# 2. CI workflow 注册成功
gh workflow list | grep regression

# 3. PR 模板路径对
test -f .github/PULL_REQUEST_TEMPLATE.md && echo "PR template OK"

# 4. PROJECT.md 字段齐
grep -E "githubOwner|githubRepo|maintainer" async_comm/PROJECT.md
```

**任何一项不通过 → AI 必须重新初始化，不允许"先跑起来再说"**。

---

## 第二步：初始化 Git

执行者首次初始化时：

```bash
cd <项目路径>
git init  # 如果还没初始化
git remote add origin <远程仓库>  # 如果还没关联
git checkout -b main  # 确保在 main 分支
git add .
git commit -m "init: async_comm 初始结构"
git push -u origin main
```

**GitHub Desktop 配置**（主理人侧）：
- File → Clone Repository → 选远程仓库
- 之后所有 review 在 GitHub Desktop 完成
- 主理人不直接用 git 命令

---

## 第三步：自动创建定时任务

```json
{
  "id": "项目ID",
  "cron": "*/5 * * * *",
  "prompt": "异步沟通任务执行 SOP (v1.3.3)：\n\n## AI 自主行为边界（v1.3.3 硬约束，先看这个再开干）\n1. **AI 永不主动调 CronDelete / TaskStop**：无 work / 队列空 / 重复任务 / 锁超时 → exit 0（pause 模式），schedule 5min 后再触发\n2. **AI 不得 rm .claude/scheduled_tasks***：删了 = 删 schedule（v1.3.4 用外部 scheduler 解决）\n3. **AI 不得在项目根创建意外文件**：`git log > how` / `touch xxx` / 临时输出都禁——临时文件落 `async_comm/`\n4. **PR 模式唯一**（v1.3.3 起）：Tag 模式已删除，不切；workflowMode == PR 不可改\n5. **工具不可用 → 写 Q&A.md 等主理人决策**，不擅自降级\n6. **任务内容来自 TASK.md**，不硬编码\n7. **不可在 SOP 中途切换模式或修改 PROJECT.md**\n\n**每轮自检**：\n- [ ] 我没调 CronDelete / TaskStop\n- [ ] 我没 rm .claude/scheduled_tasks*\n- [ ] 我没在项目根创建意外文件\n- [ ] "无 work" 退出原因写到本轮 output 第 1 行\n\n## 0. 读 PROJECT.md 拿到仓库和约定（v1.3.3 关键第一步，PR 模式唯一）\n1. 读 `async_comm/PROJECT.md` 拿到 `githubOwner` / `githubRepo` / `maintainer` / `commitStyle`\n2. 校验 `workflowMode == PR`（v1.3.3 起 PR 模式是唯一模式）\n3. 工具不可用 → 写 Q&A.md 等主理人决策，**不擅自降级**\n\n## 0.1. 扫描 PR 状态（v1.3 关键第一步 + v1.3.2 main CI 检查）\n1. 跑 `gh pr list --state all --json number,title,state,reviewDecision,mergedAt`\n2. 按 PR 状态处理（异步打回）：\n   - merged → 更新 TASK.md 该 T-ID 为 completed，归档到 archive/\n   - closed（未 merge）→ 更新 TASK.md 为 dropped，写关闭原因\n   - open + CHANGES_REQUESTED → 拉最新代码，rework，追加 commit 到原 PR，gh pr ready\n   - open + APPROVED → 跳过（等主理人 merge）\n   - open + 无 review → 跳过\n   - T-ID 在 in_progress 但无 PR → 开 PR\n3. ★ Post-merge CI 检查（v1.3.2 新增）：\n   a. 跑 `gh run list --workflow=regression.yml --branch=main --limit 1`\n   b. 拿最近一次 main CI run\n   c. 如果 conclusion == 'failure'：\n      - 读 `gh run view <run_id> --log-failed`\n      - 写 T-FIX-XXX 任务到 TASK.md（P0 优先级）\n        - 关联：被哪个 T-XXX 引入\n        - verify 方式：gh run list 显示 main CI 通过\n      - 写 Q&A.md 记录失败原因\n   d. 如果有 in_progress 的 T-FIX 任务：先领 T-FIX 修复\n4. 解锁被处理任务\n\n## 1. 回归测试\n1. 检查 async_comm/REGRESSION.md 存在\n2. 抽样跑最近 3 个 T-ID 的 verify\n3. 全量回归在 PR merge 后触发\n\n## 2. 版本检测\n1. 读取 async_comm/USER.md，检查 version 和 currentIteration\n2. 读取 async_comm/TASK.md，检查当前迭代号\n3. 如果 USER.md currentIteration > TASK.md 当前迭代：\n   - 将旧迭代所有任务标记为 completed\n   - 在 TASK.md 创建新迭代的任务区块\n\n## 3. 锁检测与任务领取\n1. 读取 TASK.md 的'锁'字段\n2. 如果有锁且未超时（<15min）：已有任务执行中，跳过本轮\n3. 如果锁已超时或无锁：清除过期锁\n4. 优先领 T-FIX-XXX 任务（如有）\n5. 按 P0→P1→P2 找第一个 pending 任务\n6. 领取：更新为 in_progress + 加锁\n\n## 4. 任务执行（v1.3.3 PR 模式唯一，## 0 走完直接执行此节）\n1. **创建工作分支**（v1.3.3 策略）：`git checkout -b t-XXX main`\n2. 写代码（边写边跑测试）\n3. 完成后跑 verify（必须通过，未通过不开 PR）\n4. 多次小 commit：`T-XXX: 子功能描述`\n5. git push origin t-XXX\n6. 按 PR_TEMPLATE.md 生成 .github/PR_BODY.md\n7. gh pr create --draft --title 'T-XXX: xxx' --body-file .github/PR_BODY.md --base main\n8. ★ 不再查 gh pr checks（v1.3.2 关键变化）：CI 在 PR 阶段不跑，AI 不阻塞\n9. 补充 verify 结果到 PR 描述\n10. gh pr ready\n11. 更新 TASK.md：in_progress → in_review\n12. 不等 review，开始下一个 T-ID\n\n## 5. 复盘沉淀\n1. 完成 T-ID 后（不是 PR merge 后），立即写 RETROSPECTIVE.md\n2. 格式：L-XXX | T-XXX | 日期 | 经验 | 标签\n3. PR merge 后更新该条记录为'已验证'\n4. T-FIX-XXX 完成后也写一条 L-XXX（标签：#CI 修复）\n\n## 6. Q&A 记录\n- 任务内技术疑问写到 async_comm/Q&A.md\n- Q-ID 与 T-ID 关联\n- 用户回答后 AI 自动继续被阻塞任务\n- main CI 连续 3 次失败时也写 Q&A.md 并升级为 blocked\n\n## 7. 主理人 review 接口（v1.3 明确）\n- 主理人只用 GitHub Desktop\n- 操作：Approve + Merge / Request Changes / Close\n- AI 通过 PR 状态自动响应\n- 主理人 review 不会被 CI 阻塞（v1.3.2）",
  "recurring": true,
  "durable": true
}
```

---

## 核心原则 (v1.3)

### 角色分工
- **主理人（人）**：通过 GitHub Desktop review PR，决策 Approve / Request Changes / Close
- **执行者（AI）**：领任务、写代码、跑 verify、commit、push、开 PR
- **观察者（人）**：只读 RETROSPECTIVE、Q&A

### 文档流转
```
USER.md 需求 ──→ TASK.md 任务 ──→ 代码 + verify ──→ commit + push ──→ PR ──→ 主理人 review ──→ merge ──→ completed
       ↑                                ↓
       └──────── Q&A.md 反馈 ──────────┘
```

### 优势 (v1.3)
- 用户只需表达"要什么"，不用关心具体怎么做
- 执行者不用担心任务丢失，PR 状态保证不重复
- **主理人不用实时在线，PR 列表是异步接口**
- 所有 PR 可追溯，review 粒度可控（一个 T-ID = 一个 PR）
- 异步打回自动 rework，不阻塞任务推进
- verify 强制机制，合入后不会破

---

## 常见问题

### Q: PR 没合入前我能合并下一个 T-ID 吗？
A: 可以。v1.3 的关键设计就是"PR 评审不阻塞任务推进"。下一个 T-ID 完成后开新 PR，老 PR 继续等 review。

### Q: 主理人打回了 PR，AI 怎么知道？
A: AI 启动时扫描 `gh pr list --json reviewDecision`，发现 `CHANGES_REQUESTED`，自动 rework 追加 commit 到原 PR。

### Q: 一个 T-ID rework 多次会怎样？
A: 都在同一个 PR 里追加 commit，主理人看的是累积 diff。多次 rework 的过程可以从 commit history 看。

### Q: PR 一直不被 merge 会怎样？
A: AI 持续推新 T-ID 进度，主理人攒一批一起 merge 也没问题。每个 T-ID 独立归档。

### Q: 怎么本地 verify？
A: 跑 TASK.md 里写的 verify 命令。详见 [VERIFY_GUIDE.md](./VERIFY_GUIDE.md)。

### Q: 跨 T-ID 的功能怎么协调？
A: 通过 TASK.md 的 T-ID 排序隐式保证（T-001 必在 T-002 前完成）。

### Q: 24h 没人 review 会怎样？
A: AI 继续推任务，但 REGRESSION.md 不会更新（等 PR merge 后才触发）。归档等 PR merge 后做。

### Q: 主理人能不能直接看 TASK.md？
A: 不能。TASK.md 是执行者内部状态，主理人只通过 PR 看工作。这是 Conway 定律要求的接口隔离。

### Q: 远程仓库必须用 GitHub 吗？
A: 不必须。Gitee、自建 Gitea 都可以，只要支持 PR 概念和 `gh` CLI（或类似工具）。

---

## 附录：常用命令

```bash
# === PR 操作（执行者和主理人都用）===

# 查看 PR 列表
gh pr list --state all

# 查看具体 PR
gh pr view <编号>

# 创建 PR（带 draft）
gh pr create --draft --title "T-001: xxx" --body-file .github/PR_BODY.md

# 标记 PR 为 ready
gh pr ready

# 合并 PR（主理人侧，GitHub Desktop 更方便）
gh pr merge <编号> --merge

# 关闭 PR（主理人侧）
gh pr close <编号>

# === Git 操作（执行者用）===

# 拉取最新 main
git pull origin main

# 强制 rebase（解决 PR 冲突时）
git fetch origin main
git rebase origin/main
git push --force-with-lease

# === Verify 操作（执行者用）===

# 跑单个 T-ID 的 verify
bash verify_t001.sh

# 跑全量测试
pytest tests/

# 跑回归（主理人侧）
bash regression.sh  # 如有
```

---

## 版本变更记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| **v1.3.3** | **2026-06-05** | **12 文件脚手架（.github/workflows + PULL_REQUEST_TEMPLATE 必建）+ Preflight Check 强制 + 任务粒度 20min-2h 硬约束 + SETUP.md/RETROSPECTIVE 质量门分离 + 推后项 spec 强制 + t-XXX 分支策略 + 移除 Tag 模式 + PROJECT.md 替代 MODE.md** |
| v1.3.2 | 2026-06-04 | Post-merge gate：CI 只在 main 跑，失败自动 T-FIX-XXX 修复；去掉 Playwright；regression.yml 约束可调 |
| v1.3.1 | 2026-06-04 | CI 闭环：gh pr checks + 自动 rework，max retry = 3，[CI_GUIDE.md](./CI_GUIDE.md) |
| v1.3 | 2026-06-04 | 集成 Git + GitHub Desktop PR 工作流，6 态状态机，异步打回机制，verify 强制 |
| v1.2 | 2026-06-02 | 状态枚举（5 态）、锁机制、迭代支持 |
| v1.1 | 2026-05-29 | 尝试复杂化，回滚（见 ARCHIVE） |
| v1.0 | 2026-05-06 | 5 文件基础版 |

完整变更历史见 [CHANGELOG.md](./CHANGELOG.md)。
