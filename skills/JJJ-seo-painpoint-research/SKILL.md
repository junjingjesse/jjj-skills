---
name: JJJ-seo-painpoint-research
description: "SEO痛点采集，多平台收集用户真实痛点与吐槽"
trigger: "痛点采集","用户反馈调研","竞品痛点"
---

# SEO痛点采集工具

## 快速开始

用户触发此技能后，直接说：

**请提供你要调研的竞品关键词（可多个，用逗号或换行分隔）**

然后等待用户输入关键词。

---

## 方法论

### 痛点采集平台

| 平台 | 特点 | 适用场景 |
|------|------|----------|
| G2.com | 企业用户评价，Pros/Cons详细 | B2B产品 |
| Capterra | 企业用户反馈 | B2B/SaaS |
| Trustpilot | 普通用户吐槽，更真实 | 消费品 |
| Product Hunt | 早期用户反馈，第一印象 | 新产品 |
| Reddit | 真实情绪，"sucks/overpriced" | 深度调研 |
| Twitter/X | 最新反馈 | 实时舆情 |
| Hacker News | 技术用户视角 | 技术产品 |

### 搜索策略

| 平台 | 搜索关键词 |
|------|-----------|
| G2 | [竞品名] reviews |
| Capterra | [竞品名] review |
| Trustpilot | [竞品名] |
| Product Hunt | [竞品名] |
| Reddit | [竞品名] sucks / [竞品名] overpriced |
| Twitter | [竞品名] [痛点相关词] |
| Hacker News | [竞品名] |

### 痛点分类

| 类型 | 关键词 | 说明 |
|------|--------|------|
| 功能缺失 | "no feature", "can't", "wish" | 功能不能满足需求 |
| 性能问题 | "slow", "bug", "crash" | 性能/稳定性问题 |
| 价格问题 | "expensive", "overpriced", "expensive" | 价格/性价比 |
| 使用体验 | "confusing", "hard to use", "frustrating" | 学习成本/易用性 |
| 客服问题 | "support", "no response" | 服务支持问题 |
| 其他 | 其他真实用户反馈 | 补充类别 |

### 判断标准

**同一个痛点出现 3 次以上，来自不同平台，才是真痛点**
- 1-2 次可能是噪音
- 3次以上：跨平台验证，可信度高
- 多个平台都提：真实需求

---

## 执行流程

### 第1步：接收关键词

用户输入一个或多个关键词（竞品名称，如ahrefs, semrush, hubspot等）。

**支持批量**：多个关键词用逗号、换行或空格分隔。

### 第2步：多平台痛点采集

**使用web-access（CDP）登录各大平台进行采集**。

对每个关键词执行以下搜索：

```
1. G2.com: 搜索 "[竞品名] reviews"，提取Pros/Cons
2. Capterra: 搜索 "[竞品名] review"，提取评分和评价
3. Trustpilot: 搜索 "[竞品名]"，提取用户评价
4. Product Hunt: 搜索 "[竞品名]"产品页，提取首日评价
5. Reddit: 搜索 "r/[竞品名] sucks" 或 "r/[竞品名] overpriced"
6. Twitter/X: 搜索 "[竞品名] [痛点相关词]"
7. Hacker News: 搜索 "[竞品名]"
```

### 第3步：痛点提取与汇总

从各平台搜索结果中提取：
- 用户原声痛点
- 痛点类型（功能/性能/价格/体验/客服）
- 出现频率

### 第4步：可视化输出

```
# 痛点采集结果

## [竞品名]

### G2.com
| 类型 | 痛点 | 出现频次 |
|------|------|----------|
| 功能 | xxx | x |
| 价格 | xxx | x |

### Capterra
...

### Trustpilot
...

### Reddit
...

### Twitter/X
...

### 汇总
- 功能相关：x条
- 价格相关：x条
- 性能相关：x条
- 体验相关：x条

## [竞品名2]
...

## 总体痛点排名
1. [痛点1] - x条
2. [痛点2] - x条
3. [痛点3] - x条
```

---

## 输出格式示例

```
# 痛点采集结果

## ahrefs

### G2.com
| 类型 | 痛点 | 出现频次 |
|------|------|----------|
| 价格 | expensive for small business | 12 |
| 功能 | limited local SEO features | 8 |

### Trustpilot
| 类型 | 痛点 | 出现频次 |
|------|------|----------|
| 客服 | slow response time | 15 |
| 性能 | index sometimes slow | 6 |

### Reddit
- "ahrefs is overpriced for what it offers"
- "their customer support is terrible"
- "data freshness could be better"

### 汇总
- 价格相关：18条
- 客服相关：15条
- 功能相关：12条
- 性能相关：8条

## semrush
...
```

---

## 注意事项

1. **登录要求**：确保用户已登录相关平台（尤其是G2、Capterra等需登录查看完整评价）
2. **批量采集**：每个关键词在各平台搜索后保持页面，方便用户查看
3. **真实原声**：提取用户真实评价文字，不做过多加工
4. **频率统计**：相同或类似痛点归类统计出现频率
5. **隐私保护**：提取信息时脱敏，不暴露用户个人信息