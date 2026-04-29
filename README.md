# jjj-skills

我的 Claude Code 技能集，源自 50+ 专项课程的经验压缩。

## 安装

```bash
# 克隆到 ~/.claude/skills/
mkdir -p ~/.claude/skills
cp -r jjj-skills/skills/* ~/.claude/skills/
```

## 技能列表

| skill | 说明 | 触发词 |
|-------|------|--------|
| [JJJ-general-email-notify](./skills/JJJ-general-email-notify/) | 通用邮件通知工具，被其他技能调用发送邮件，支持自定义主题、正文、调用者 | 被其他技能调用；"发邮件"、"通知我" |
| [JJJ-design-basics](./skills/JJJ-design-basics/) | 平面设计基础技能，包含图像、文字、形状、颜色四大元素及构图技巧 | "帮我做个海报"、"帮我做个传单"、"帮我设计个封面" |
| [JJJ-design-brand](./skills/JJJ-design-brand/) | 品牌设计技能，包含从品牌概念到视觉身份系统的完整流程 | "帮我做品牌"、"帮我做个logo"、"帮我设计品牌指南" |
| [JJJ-biz-service-design](./skills/JJJ-biz-service-design/) | 服务设计需求分析方法，系统化访谈+联网调研，推演完整的商业方案 | "帮我做服务设计"、"分析一下这个商业模式"、"这个想法怎么落地" |
| [JJJ-biz-creative-thinking](./skills/JJJ-biz-creative-thinking/) | 商业创意推演与灵感方法论，帮你系统化地生成、评估和深化商业想法 | "帮我做创意"、"头脑风暴"、"这个想法还能怎么扩展" |
| [JJJ-async-comm](./skills/JJJ-general-async-Comm/) | 异步沟通初始化与管理技能，帮你创建异步沟通所需的标准文档结构（USER.md/TASK.md/Q&A.md），并引导设置定时监督任务 | "初始化异步沟通"、"帮我创建async_comm"、"设置监督任务" |
| [JJJ-writing-storytelling](./skills/JJJ-writing-storytelling/) | 故事创作工具，覆盖情节构建、人物塑造、场景描写、文体技巧、修订指南 | "帮我写小说"、"教我写情节"、"如何塑造人物"、"写作技巧" |

