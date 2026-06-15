# jjj-skills

我的 Claude Code 技能集，源自 50+ 专项课程的经验压缩。

---

## 关于我

独立开发者，专注于出海Seo，AI 工作流自动化与效率系统构建。

- 🔧 擅长：将复杂流程封装为可复用的技能
- 📈 方向：SEO 关键词研究、内容策略
- 🎯 目标：让 AI 成为真正的生产力伙伴

## 出海Seo成果

- 
- 信息量过于庞大，一边梳理一边填入ing

## 联系我

<table>
<tr><td align="center">

微信公众号</td><td align="center">

<img src="README.assets/GZH-QRcode.jpg" width="500" /></td></tr>
<tr><td align="center">

知识星球</td><td align="center">

<img src="README.assets/zsxq.jpg" width="500" /></td></tr>
<tr><td align="center">

Email</td><td align="center">

tewbooaththb@hotmail.com</td></tr>
</table>

---

🤝 欢迎贡献！有问题提 Issue，一起让技能更好用。

## 安装

```bash
# 安装依赖
pip install requests pytrends

# 克隆到 ~/.claude/skills/
mkdir -p ~/.claude/skills
cp -r jjj-skills/skills/* ~/.claude/skills/
```

| 依赖 | 用途技能 |
|------|---------|
| requests | JJJ-seo-intent-analysis, JJJ-seo-trends-verify |
| pytrends | JJJ-seo-trends-verify |

## 技能列表

| skill | 说明 | 触发词 |
|-------|------|--------|
| [JJJ-general-email-notify](./skills/JJJ-general-email-notify/) | 邮件通知工具，被其他技能调用发送邮件 | 发邮件、通知我 |
| [JJJ-design-basics](./skills/JJJ-design-basics/) | 平面设计基础，图像文字形状颜色四大元素与构图技巧 | 做个海报、设计传单、设计封面 |
| [JJJ-design-brand](./skills/JJJ-design-brand/) | 品牌设计，从概念到视觉身份系统的完整流程 | 做品牌、logo设计、品牌指南 |
| [JJJ-biz-service-design](./skills/JJJ-biz-service-design/) | 服务设计方法，系统化访谈调研帮你推演完整商业方案 | 服务设计、需求分析、商业模式 |
| [JJJ-biz-creative-thinking](./skills/JJJ-biz-creative-thinking/) | 创新思维工具，用多种方法帮你生成大量创意并筛选评估 | 帮我发散、头脑风暴、创新 |
| [JJJ-general-async-comm](./skills/JJJ-general-async-comm/) | 异步沟通管理，创建USER/TASK/Q&A文档结构（通用版，不假设代码项目） | 初始化异步沟通、async_comm |
| [JJJ-dev-async-comm](./skills/JJJ-dev-async-comm/) | 开发场景专用异步沟通治理流程，Git PR 评审 + CI 验证 + manual gate（v1.4.2，已在一个 Next.js 模板项目验证） | 开发异步沟通、dev_async_comm |
| [JJJ-writing-storytelling](./skills/JJJ-writing-storytelling/) | 故事创作工具，教你构建情节、塑造人物、描写场景 | 写小说、写作技巧 |
| [JJJ-seo-kgr-search](./skills/JJJ-seo-kgr-search/) | SEO关键词KGR调研，筛选月搜索量与allintitle比例低的值得做词汇 | kgr搜索、kgr调研 |
| [JJJ-seo-competitor-analysis](./skills/JJJ-seo-competitor-analysis/) | SEO竞品分析，用关键词分析Google首页竞争对手网站状况 | seo竞争分析、关键词竞争 |
| [JJJ-seo-painpoint-research](./skills/JJJ-seo-painpoint-research/) | SEO痛点采集，多平台收集用户真实痛点与吐槽 | 痛点采集、用户反馈调研 |
| [JJJ-seo-trends-verify](./skills/JJJ-seo-trends-verify/) | Google趋势数据验证，检测季节性/趋势方向/地域分布 | 趋势验证、谷歌趋势 |
| [JJJ-seo-intent-analysis](./skills/JJJ-seo-intent-analysis/) | 搜索意图分析，基于Google自动补全分析搜索意图 | 意图分析、搜索意图 |
| [JJJ-architecture-oop-design](./skills/JJJ-architecture-oop-design/) | 面向对象设计技能，抽象/封装/分解/泛化四大核心概念 | OOP设计、面向对象、类图建模 |
| [JJJ-architecture-design-patterns](./skills/JJJ-architecture-design-patterns/) | 设计模式技能，23种GoF模式分类整理与SOLID原则应用 | 设计模式、GoF、ingleton、观察者 |
| [JJJ-architecture-software-architecture](./skills/JJJ-architecture-software-architecture/) | 软件架构技能，4+1视图模型、架构风格、质量属性评估与ATAM方法 | 软件架构、架构风格、分层架构、n层架构 |
| [JJJ-architecture-service-oriented-architecture](./skills/JJJ-architecture-service-oriented-architecture/) | 面向服务架构技能，SOA原则、Web服务标准(SOAP/WSDL/UDDI)、REST设计、微服务架构 | 面向服务架构、SOA、Web服务、REST、微服务 |

