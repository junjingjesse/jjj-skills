# CLAUDE.md

## 初始化检查清单

1. **先读 README.md** — 获取安装路径、触发词等基础信息
2. **遇到问题先看 README** — 别装傻问用户已知信息
3. **README 里没有的再问用户**

---

## 技能描述规范（创建新技能时）

### 两层描述结构

**1. Frontmatter描述（斜杠选择显示）**
```yaml
---
name: 技能名称
description: "简短描述（20-30字），让用户一眼看懂是做什么的"
trigger: "触发词1","触发词2","触发词3"
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

