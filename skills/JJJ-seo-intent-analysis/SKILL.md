---
name: JJJ-seo-intent-analysis
description: "搜索意图分析，基于Google自动补全延伸词分析搜索意图"
trigger: "意图分析","搜索意图","关键词延伸","intent分析"
---

# 搜索意图分析工具

## 快速开始

用户触发此技能后，直接说：

**请提供你要分析意图的关键词（可多个，用逗号或换行分隔）**

然后等待用户输入关键词。

---

## 方法论

### 搜索建议获取

Google 自动补全（Suggest API）可以获取与关键词相关的搜索建议：
- 用户输入关键词时，Google 会自动补全推荐
- 这些补全是真实用户的搜索行为，反映实际需求

### 意图类型

| 类型 | 说明 | 商业价值 |
|------|------|----------|
| INFO | 信息查询 | 低 |
| NAV | 导航寻找 | 中 |
| TRANSAC | 交易购买 | 高 |
| COMM | 交流讨论 | 低 |

### 意图判断规则

| 关键词特征 | 意图类型 |
|------------|----------|
| how to, 什么是, 教程 | INFO |
| 官网, 哪里买, download | NAV |
| coupon, price, buy, discount | TRANSAC |
| review, vs, comparison | COMM |

---

## 执行流程

### 第1步：接收关键词

用户输入一个或多个核心关键词。

### 第2步：获取搜索建议

对每个关键词调用 Google Suggest API：
- 获取前10-20个自动补全建议
- 保存原始数据

### 第3步：意图分类

对每个建议词分析：
- 提取关键词特征（how to, buy, price等）
- 归类到对应意图类型

### 第4步：可视化输出

```
# 搜索意图分析结果

## [核心关键词]

### 搜索建议 (10条)
1. keyword + how to
2. keyword + price
3. keyword + buy
...

### 意图分布
- INFO: 5条 (50%)
- TRANSAC: 3条 (30%)
- NAV: 2条 (20%)

### 意图详情
| 建议词 | 意图类型 | 特征词 |
|-------|---------|-------|
| keyword how to | INFO | how to |
| keyword price | TRANSAC | price |
...
```

---

## 输出格式示例

```
# 搜索意图分析结果

## chatgpt

### 搜索建议 (10条)
1. chatgpt how to use
2. chatgpt login
3. chatgpt free
4. chatgpt app download
5. chatgpt vs claude
6. chatgpt api price
7. chatgpt plus
8. chatgpt not working
9. chatgpt alternative
10. chatgpt for business

### 意图分布
- INFO: 3条 (30%)
- TRANSAC: 3条 (30%)
- NAV: 2条 (20%)
- COMM: 2条 (20%)

### 意图详情
| 建议词 | 意图类型 | 特征词 |
|-------|---------|-------|
| chatgpt how to use | INFO | how to |
| chatgpt login | NAV | login |
| chatgpt free | TRANSAC | free |
| chatgpt app download | NAV | download |
| chatgpt vs claude | COMM | vs |
| chatgpt api price | TRANSAC | price |
| chatgpt plus | TRANSAC | plus |
| chatgpt not working | INFO | not working |
| chatgpt alternative | COMM | alternative |
| chatgpt for business | INFO | for business |

### 结论
- 主要意图: INFO/TRANSAC 混合
- 商业价值: 中等
- 建议: 可做教程内容 + 部分付费功能
```

---

## Python脚本使用方法

```bash
pip install requests
python3 intent_analysis.py
```

输入关键词后自动获取建议并分析意图。