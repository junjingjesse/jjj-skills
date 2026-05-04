---
name: JJJ-seo-kgr-search
description: "SEO关键词KGR调研，筛选月搜索量与allintitle比例低的值得做词汇"
trigger: "kgr搜索","kgr调研","seo关键词调研"
---

# SEO KGR关键词调研工具

## 快速开始

用户触发此技能时，直接说：

**请告诉我你要查哪一天的日期？（如2026-04-29）**

然后等待用户指定日期。

---

## KGR方法论

### KGR公式
```
KGR = allintitle结果数 / 月搜索量
```

### 核心逻辑
- **月搜索量**：从本地API获取（28天搜索量）
- **allintitle数据**：Google搜索 `allintitle:关键词` 获取结果数
- **比例越低**：竞争越小，越容易获得排名，值得做

### 关键词分类

| 类型 | 搜索量 | 难度 | 策略 |
|------|--------|------|------|
| Top Keywords | 高 | 难 | 谨慎切入 |
| Mid-tail Keywords | 中 | 中 | 稳步攻占 |
| Long-tail Keywords | 低 | 易 | 优先攻克 ✓ |

---

## 本地API调用

### API地址
```
http://localhost:8000
```

### 搜索端点
```
POST /api/v1/keywords/search
```

### 默认筛选参数

```json
{
  "min_volume": 46669,
  "max_difficulty": 30,
  "date_start": "用户指定的日期",
  "date_end": "用户指定的日期",
  "page_size": 10000000
}
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `min_volume` | 46669 | 最小月搜索量 |
| `max_difficulty` | 30 | 最大难度30 |
| `date_start` | 用户指定 | 用户导入数据的日期 |
| `date_end` | 用户指定 | 用户导入数据的日期 |
| `page_size` | 10000 | 取满全部数据，确保覆盖所有结果 |

**重要**：
- 必须先问用户要查哪一天的日期数据
- `date_end`是范围筛选（≤），不是精确匹配
- 如果数据库没有用户指定的日期，会返回空或旧数据

### 调用示例

```bash
# 获取符合条件的关键词
curl -s -X POST http://localhost:8000/api/v1/keywords/search \
  -H "Content-Type: application/json" \
  -d '{
    "min_volume": 46669,
    "max_difficulty": 30,
    "date_start": "2026-04-29",
    "date_end": "2026-04-29",
    "page_size": 10000
  }'
```

### 返回字段说明
- `keyword`: 关键词
- `search_volume_28d`: 28天搜索量（月搜索量）
- `difficulty`: 关键词难度 (0-100)
- `cpc`: 每次点击成本
- `intent`: 搜索意图
- `leader_domain`: 领先域名

---

## 执行流程

### 第1步：确认日期（必须先问用户）

用户触发技能后，**直接问**：请告诉我你要查哪一天的日期？

### 第2步：获取关键词列表

根据用户指定的日期，调用本地API获取符合条件的关键词：
```bash
curl -s -X POST http://localhost:8000/api/v1/keywords/search \
  -H "Content-Type: application/json" \
  -d '{
    "min_volume": 46669,
    "max_difficulty": 30,
    "date_start": "用户指定的日期",
    "date_end": "用户指定的日期",
    "page_size": 10000
  }'
```

返回关键词列表。

### 第3步：获取allintitle数据

对列表中**每个关键词**执行Google搜索 `allintitle:关键词`，提取搜索结果数量。

**注意**：每次搜索之间间隔1-2秒，避免被Google限制。

### 第4步：计算KGR和KDRoi

```python
KGR = allintitle结果数 / 月搜索量
KDRoi = (月搜索量 x CPC) / KD
```

### 第5步：可视化输出

输出**三个表格**：

#### 表格1：全部调研结果（按KGR升序）
```
# KGR调研结果 [日期]

| 关键词 | 月搜索量 | CPC | KD | Zero Click% | Allintitle | KGR | KDRoi | 评估 |
|--------|----------|-----|-----|-----------|----------|-----|------|------|
| xxx    | xxx      | xxx | xxx | xxx      | xxx      | x  | xxx  | xxx  |
```

#### 表格2：值得做的关键词（KGR < 0.1）

**按KGR升序**（最值得做的优先）：
```
## 值得做（按KGR）

| 关键词 | 月搜索量 | CPC | KD | Allintitle | KGR | KDRoi |
|--------|----------|-----|-----|----------|-----|------|------|
| xxx    | xxx      | xxx | xxx | xxx      | x  | xxx  |
```

**按KDRoi降序**（商业价值优先）：
```
## 值得做（按KDRoi）

| 关键词 | 月搜索量 | CPC | KD | Allintitle | KGR | KDRoi |
|--------|----------|-----|-----|----------|-----|------|
| xxx    | xxx      | xxx | xxx | xxx      | x  | xxx  |
```

**字段说明**：
- `CPC`：每次点击成本（美元）
- `KD`：Keyword Difficulty，关键词优化难度 (0-100)
- `KDRoi`：(搜索量 × CPC) / KD，商业价值/竞争难度比值，越高越值得做
- `Zero Click%`：零点击搜索量占比（越高说明用户越看完就走）

---

## 评估标准

| KGR比例 | 评估 | 说明 |
|--------|------|------|
| <0.1 | 值得做 | 竞争小，容易获得排名 |
| 0.1-0.5 | 一般 | 中等竞争 |
| >0.5 | 难 | 竞争大，不建议 |