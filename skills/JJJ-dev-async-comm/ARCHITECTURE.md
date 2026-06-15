# 异步沟通机制架构设计 (v1.3)

> v1.3 的完整架构设计文档。配套使用：
> - [SKILL.md](./SKILL.md) — 主技能文件（操作 SOP）
> - [PR_TEMPLATE.md](./PR_TEMPLATE.md) — PR 描述模板
> - [VERIFY_GUIDE.md](./VERIFY_GUIDE.md) — verify 机制
> - [CHANGELOG.md](./CHANGELOG.md) — 版本变更

---

## 一、设计目标

**24 小时无人工厂**：人在不在 loop 中，系统都能持续推进任务。

### 三个核心约束

1. **可 review**：所有变更粒度适中，主理人能在 GitHub Desktop 决策
2. **可异步**：主理人不在线时，AI 持续推进，不阻塞
3. **可回滚**：每个版本有明确归档，错误能快速恢复

---

## 二、Kruchten 4+1 视图

### 2.1 逻辑视图

**角色与契约**（Conway 定律视角——架构反映组织）：

```
┌──────────────┐
│   主理人（人） │  ← 通过 GitHub Desktop 看 PR
│              │     决策：Approve / Request Changes / Close
└──────┬───────┘
       │ PR 评论（异步）
       ↓
┌──────────────┐         ┌──────────────┐
│  执行者（AI）  │ ←─────→ │  观察者（人）  │
│              │  读写    │   （只读）    │
└──────────────┘         └──────────────┘
```

**关键接口隔离**：
- 主理人**不读** TASK.md
- 执行者**不直接**找主理人
- 观察者只读 RETROSPECTIVE / Q&A

### 2.2 过程视图

正常流程：

```
[USER.md 需求]
     ↓
[TASK.md 任务化]
     ↓
[执行者领取] pending → in_progress
     ↓
[代码 + verify]
     ↓
[git commit + push]
     ↓
[gh pr create --draft] → [gh pr ready]
     ↓
in_progress → in_review
     ↓
[主理人 review]
     ↓
     ├──→ [Merge] → in_review → completed → archive/
     ├──→ [Request Changes] → in_review → in_progress（追加 commit）→ in_review
     └──→ [Close] → in_review → dropped
```

阻塞流程：

```
[执行者遇 Q&A]
     ↓
in_progress → blocked
     ↓
[用户回答 Q&A.md]
     ↓
blocked → in_progress
     ↓
... 继续主流程
```

### 2.3 开发视图

**单分支（main）多 commit**：

```
main ─────●─────●─────●─────●─────●─────●─────►
          │T-001│T-001│T-002│T-002│T-003│T-003│
          │ c1  │ c2  │ c1  │ c2  │ c1  │ c2  │
          └─────┴─────┴─────┴─────┴─────┴─────┘
           PR-001 (open)   PR-002 (open)   PR-003 (open)
```

**配套目录结构**：

```
async_comm/
├── USER.md              ← 需求（主理人写）
├── TASK.md              ← 任务（执行者维护）
├── Q&A.md               ← 技术疑问
├── REGRESSION.md        ← 回归测试
├── RETROSPECTIVE.md     ← 复盘
├── PR_TEMPLATE.md       ← PR 模板参考
├── archive/             ← 已完成任务
├── tests/               ← 单元测试
│   └── test_xxx.py
├── verify_t001.sh       ← T-001 端到端验证
├── verify_t002.sh
└── .github/
    └── PR_BODY.md       ← 每次开 PR 前的描述
```

### 2.4 物理视图

```
┌─────────────────────────────────────────────┐
│            本地 (主理人电脑)                  │
│                                             │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ Claude Code  │    │ GitHub Desktop   │  │
│  │ (执行者)      │    │ (主理人)          │  │
│  └──────┬───────┘    └────────┬─────────┘  │
│         │                     │            │
│         │  git commit/push    │  PR review  │
│         │  gh pr create       │             │
└─────────┼─────────────────────┼────────────┘
          │                     │
          ↓                     ↓
┌─────────────────────────────────────────────┐
│          远程仓库 (GitHub / Gitee)            │
│                                             │
│  - main 分支                                 │
│  - PR #1, #2, #3 (open/closed/merged)       │
│  - gh CLI 读写                               │
└─────────────────────────────────────────────┘
```

### 2.5 场景视图

| 场景 | 触发 | 流程 | 终态 |
|------|------|------|------|
| **正常完成** | T-ID 做完 + PR merge | pending → in_progress → in_review → completed | archive/ |
| **PR 打回** | 主理人 Request Changes | in_review → in_progress（rework）→ in_review | 再次 review |
| **PR 关闭** | 主理人 Close | in_review → dropped | （写原因） |
| **Q&A 阻塞** | 遇技术疑问 | in_progress → blocked（等回答）→ in_progress | 继续 |
| **Q&A 超时** | 72h 未回答 | blocked → dropped | （不复活） |
| **新迭代** | USER.md currentIteration++ | 旧迭代全 completed + 新建迭代区 | 进入新阶段 |

---

## 三、核心机制详解

### 3.1 状态机（6 态）

```
pending ─→ in_progress ─→ in_review ─┬─→ completed
            │   ↑           │   │    │
            │   │           ↓   │    │
            │   └─────(rework)─┘    │
            ↓                       │
         blocked ──(Q&A)──→ in_progress
            │
            ↓ (72h 超时)
         dropped
```

| 状态 | 含义 | AI 行为 |
|------|------|---------|
| `pending` | 待领取 | 等 AI pick up |
| `in_progress` | 进行中 | AI 在写代码，可有本地 commit |
| `in_review` | PR open | AI 完成任务，等主理人 review |
| `completed` | 已完成 | PR merged，归档 |
| `blocked` | 阻塞中 | 等用户回答 Q&A，可同时处理其他 T-ID |
| `dropped` | 已放弃 | PR closed 或 Q&A 超时 |

### 3.2 锁机制

防止 AI 实例重复领取同一任务：

- 加锁：领取任务时记录 `T-XXX (时间戳, 15min 超时)`
- 解锁：任务完成 / 主动释放 / 超时自动失效
- 锁写在 TASK.md 的"项目信息"区

### 3.3 异步打回机制（v1.3 核心创新）

**问题**：主理人不在线时打回了 PR，AI 怎么知道？

**解决**：AI 每次启动时**第一动作**是扫描 `gh pr list`：

```bash
gh pr list --state all --json number,title,state,reviewDecision,mergedAt
```

按 reviewDecision 分类处理：

| reviewDecision | AI 行为 |
|----------------|---------|
| `null`（无 review） | 保持 in_review，AI 跳过 |
| `APPROVED` | 等待主理人手动 merge，AI 跳过 |
| `CHANGES_REQUESTED` | 自动 rework，追加 commit 到原 PR |
| `COMMENTED`（仅评论） | 保持 in_review，AI 可选地处理评论 |

**关键设计**：
- PR 是"动态对象"，rework 追加 commit 到原 PR（不创建新 PR）
- "打回"不是失败，是"延迟确认"
- 主理人不需要实时在线，PR 列表是唯一接口
- rework 多次都在同一 PR，主理人看累积 diff

### 3.4 verify 机制（v1.3 核心创新）

**问题**：合入 main 后才知道代码有 bug。

**解决**：TASK.md 的 T-ID **强制**写明 verify 方式：

```markdown
⬜ [T-001] 实现关键词清洗
- 验收标准：xxx
- **verify 方式**：`bash verify_t001.sh`
```

AI 开 PR 前**必须**跑过 verify，未通过不开 PR。

三层验证金字塔：

| 层 | 工具 | 覆盖 | 触发 |
|----|------|------|------|
| 单元 | `tests/test_xxx.py` | 纯函数、算法 | AI 写代码时 |
| 集成 | `verify_tXXX.sh` | 端到端流程 | AI 开 PR 前 |
| E2E | 主理人 review | 用户体验 | PR 评论 |

### 3.5 阻塞超时

- 72h 未回答 → dropped
- 简化理由：从 v1.2 的 48h+72h 简化为单一 72h（配置项更少）
- 不复活：用户事后回答时，T-ID 已 dropped，可在 RETROSPECTIVE 记录"该问题被跳过"

---

## 四、关键架构决策记录 (ADR)

### ADR-1: 单分支多 commit（vs GitHub Flow / Trunk-based）

**决策**：单分支（main）多 commit，每个 T-ID 一个 PR。

**原因**：
- 1 主理人 + 1 AI 的组织结构，没有多分支协作需求
- 主理人 review 的是 PR diff，不是 commit history
- 一个 T-ID 内多次 commit 方便 AI 滚动开发

**权衡**：
- 失去分支隔离（但 1 人 1 AI 场景下不需要）
- PR 冲突处理靠 rebase（边缘情况）

### ADR-2: 6 态状态机（vs 5 态 / 7 态）

**决策**：`pending / in_progress / in_review / completed / blocked / dropped`

**原因**：
- v1.1 试过 7 态（含 `committed`），太细
- 5 态少一个中间态，"PR 已开等 review" 无法表达
- 6 态刚好：`committed` 和 `in_progress` 合并（都"在 AI 手里"）

**权衡**：
- "已 commit 但未开 PR" 状态不可见（但流程上 AI 一定 commit 后立刻开 PR）

### ADR-3: 阻塞超时 72h（vs 48h+72h 阶梯）

**决策**：单一 72h 阈值。

**原因**：
- v1.2 试过 48h 降级 + 72h 丢弃，复杂
- 实际场景：要么记得回答，要么忘了；中间态"降级"意义不大

**权衡**：
- 失去"提前降级提醒"

### ADR-4: 启动 SOP 第一动作是扫描 PR（vs 扫描 TASK.md）

**决策**：每次执行者启动，**先**扫 `gh pr list`，**再**看 TASK.md。

**原因**：
- 异步打回机制要求：主理人的 review 结果必须被及时消化
- 如果先看 TASK.md，可能忽略"PR 被打回需要 rework"

**权衡**：
- 增加一次 gh 调用（成本低）

### ADR-5: verify 强制度（vs 可选）

**决策**：TASK.md 的 T-ID 必填 verify 方式，PR 描述必含 verify 结果。

**原因**：
- 没有 verify 机制的 v1.0/v1.1/v1.2 都有"合入后才发现坏"
- verify 是测试金字塔的基础，不能省

**权衡**：
- 增加 T-ID 模板的字段（成本低）

### ADR-6: PR 描述用 draft → ready 两步

**决策**：开 PR 时用 `--draft`，补充 verify 结果后再 `gh pr ready`。

**原因**：
- 避免主理人看到不完整的 PR 描述就 review
- AI 有时间跑完 verify 再请主理人看

**权衡**：
- 流程多一步（但成本低）

---

## 五、与 v1.2 的对比

| 维度 | v1.2 | v1.3 | 变化 |
|------|------|------|------|
| 状态数 | 5 | 6 | + `in_review` |
| Git 治理 | 无 | 完整 | + PR 工作流 |
| 主理人介入 | 无 | GitHub Desktop | + review 入口 |
| verify | 可选 | 强制 | T-ID 必填 |
| 异步打回 | 无 | 启动扫描 PR | + rework 自动 |
| 阻塞超时 | 48h+72h | 72h | 简化 |
| PR 模板 | 无 | 有 | + 主理人 review 效率 |
| 回归触发 | 手动 | 自动 | 启动时抽样 |

---

## 六、未来可优化方向（v1.4+ 候选）

> 这些方向**不**在 v1.3 实施，避免 scope creep。

1. **跨 T-ID 依赖图**：当前靠 T-ID 排序隐式保证，可显式建模
2. **PR 自动合并**（auto-merge）：主理人 approve 后 GitHub 自动合入（无需点 Merge）
3. **AI 互相 review**：两个 AI 实例互相 review PR（鸡尾酒效应）
4. **verify 并行化**：用 pytest-xdist 并行跑测试
5. **REGRESSION.md 趋势图表**：从历史数据生成可视化
6. **CHANGELOG 自动生成**：从 commit message 自动生成
7. **Slack/邮件通知**：PR 状态变化时主动通知（v1.1 试过，撤回）

---

## 七、参考资源

- Kruchten 4+1 视图模型
- Conway 定律（Melvin Conway, 1968）
- GitHub Flow（https://guides.github.com/introduction/flow/）
- ATAM（架构权衡分析法）
