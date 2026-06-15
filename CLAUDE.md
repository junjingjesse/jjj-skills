# CLAUDE.md

## 初始化检查清单

1. **先读 README.md** — 获取安装路径、触发词等基础信息
2. **遇到问题先看 README** — 别装傻问用户已知信息
3. **README 里没有的再问用户**
4. **发布到 main / 公开版改动前，先读 [DEV_WORKFLOW.md](./DEV_WORKFLOW.md)** — 工作流和硬性检查清单都在那里

---

## 技能命名规范

### 格式结构
```
JJJ-分类-技能名
```

| 层级 | 说明 | 示例 |
|------|------|------|
| 前缀 | JJJ品牌（大写） | JJJ |
| 分类 | 技能所属领域 | seo, design, writing |
| 技能名 | 具体技能名称 | kgr-search, competitor-analysis |

### 常用分类

| 分类 | 说明 |
|------|------|
| seo | SEO相关技能 |
| design | 设计相关技能 |
| writing | 写作相关技能 |
| biz | 商业相关技能 |
| general | 通用工具 |

### 示例
- `JJJ-seo-kgr-search` = JJJ + seo(SEO) + kgr-search(KGR搜索)
- `JJJ-seo-competitor-analysis` = JJJ + seo(SEO) + competitor-analysis(竞品分析)
- `JJJ-design-basics` = JJJ + design(设计) + basics(基础)

---

## 技能描述规范（创建新技能时）

### 两层描述结构

**1. Frontmatter描述（斜杠选择显示）**
```yaml
---
name: 技能名称
description: "简短描述（20-30字），让用户一眼看懂是做什么的"
trigger: ["触发词1","触发词2","触发词3"]
---
```

**要求**：
- description：20-30字，简短有力
- trigger：主要触发词，用逗号分隔

**2. 正文（SKILL.md详细说明）**
- 开头直接告诉用户要做什么（快速开始）
- 正文包含完整的方法论和操作指引

**检查清单**：
- [ ] description是否20-30字
- [ ] trigger词是否包含主要触发方式
- [ ] 正文是否包含快速开始说明
- [ ] 方法论是否清晰完整

---

## 当前项目

- 技能仓库：当前目录 `./`
- 技能安装路径：
  - Windows: `C:\Users\<用户名>\.claude\skills\`
  - Linux/Mac: `~/.claude/skills/`
- 安装命令：`cp -r ./skills/* ~/.claude/skills/`

---

## 常用操作

- 复制技能到本地：
  - Windows: `cp -r ./skills/<skill-name> C:\Users\admin\.claude\skills\`
  - Linux/Mac: `cp -r ./skills/<skill-name> ~/.claude/skills/`

---

## 仓库分支结构（AI 必读）

这个仓库是**单分支公开 + 双分支本地**的结构，AI 协作时必须知道：

- `main`（云端 + 本地）= **孤儿 root commit**，单 commit 结构，外部 clone 下来 git log 只看到 1 条
- `dev`（仅本地）= 日常迭代分支，带全部演进历史
- `backup-main` / `backup-dev` = 历史重写前的备份（仅本地）

**AI 协作时的硬性规则**：

1. **不要把改动 commit 到 main**：main 的更新永远走 orphan + 强制推送流程（详见 [DEV_WORKFLOW.md](./DEV_WORKFLOW.md)）
2. **不要建议 `git merge dev` 合到 main**：merge 会破坏 main 的单 commit 结构
3. **dev 永远不要 push 到 origin**：如果用户让你 push dev，立刻提醒这是违规操作
4. **改动前先 `git checkout dev`**：所有改动都该发生在 dev 上
5. **跨文档引用**：发布相关问题看 [DEV_WORKFLOW.md](./DEV_WORKFLOW.md)，公开项目说明看 [README.md](./README.md)

