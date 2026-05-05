"""
搜索意图分析工具
基于Google Suggest API获取搜索建议并分析意图
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

# 意图关键词映射
INTENT_KEYWORDS = {
    'INFO': ['how to', 'what is', 'tutorial', 'tips', 'guide', 'learn', '什么是', '教程', '攻略'],
    'NAV': ['login', 'sign in', 'download', 'app', 'official', '官网', '下载', 'app'],
    'TRANSAC': ['price', 'buy', 'coupon', 'discount', 'free', 'paid', 'pro', 'plus', 'price', 'cost', 'pricing', '购买', '价格', '优惠'],
    'COMM': ['vs', 'review', 'comparison', 'alternative', 'compare', 'best', 'versus', '评价', '对比']
}


def get_suggestions(keyword: str, proxy: str = None) -> List[str]:
    """
    获取 Google 搜索建议

    Args:
        keyword: 搜索关键词
        proxy: 代理地址（可选）

    Returns:
        搜索建议列表
    """
    url = "https://suggestqueries.google.com/complete/search"
    params = {
        "output": "toolbar",
        "hl": "en",
        "q": keyword
    }

    proxies = {'http': proxy, 'https': proxy} if proxy else None

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=10)
        response.raise_for_status()

        # 解析 XML 响应
        root = ET.fromstring(response.text)
        suggestions = [suggestion.get('data') for suggestion in root.findall('.//suggestion')]

        return suggestions

    except Exception as e:
        print(f"请求出错: {e}")
        return []


def analyze_intent(suggestion: str) -> Dict:
    """
    分析单个搜索建议的意图

    Args:
        suggestion: 搜索建议词

    Returns:
        {'type': 意图类型, 'keyword': 特征关键词}
    """
    suggestion_lower = suggestion.lower()

    for intent_type, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in suggestion_lower:
                return {'type': intent_type, 'keyword': kw}

    return {'type': 'UNKNOWN', 'keyword': '-'}


def analyze_keyword(keyword: str, proxy: str = None) -> Dict:
    """
    分析关键词的搜索意图

    Args:
        keyword: 核心关键词
        proxy: 代理（可选）

    Returns:
        包含分析结果的字典
    """
    suggestions = get_suggestions(keyword, proxy)

    if not suggestions:
        return {'error': '获取建议失败'}

    # 分析每个建议
    analyzed = []
    intent_counts = {'INFO': 0, 'NAV': 0, 'TRANSAC': 0, 'COMM': 0, 'UNKNOWN': 0}

    for suggestion in suggestions:
        result = analyze_intent(suggestion)
        intent_type = result['type']
        analyzed.append({
            'suggestion': suggestion,
            'intent': intent_type,
            'keyword': result['keyword']
        })
        intent_counts[intent_type] += 1

    total = len(suggestions)
    intent_distribution = {k: f"{v/total*100:.0f}%" if total > 0 else "0%" for k, v in intent_counts.items()}

    return {
        'keyword': keyword,
        'suggestions': analyzed,
        'total': total,
        'intent_counts': intent_counts,
        'intent_distribution': intent_distribution
    }


def generate_report(keyword: str, proxy: str = None) -> str:
    """
    生成分析报告
    """
    result = analyze_keyword(keyword, proxy)

    if 'error' in result:
        return f"分析失败: {result['error']}"

    report = f"""
# 搜索意图分析结果

## {result['keyword']}

### 搜索建议 ({result['total']}条)
"""

    for i, item in enumerate(result['suggestions'], 1):
        report += f"{i}. {item['suggestion']}\n"

    report += f"""
### 意图分布
"""
    for intent, count in result['intent_counts'].items():
        if count > 0:
            report += f"- {intent}: {count}条 ({result['intent_distribution'][intent]})\n"

    report += f"""
### 意图详情
| 建议词 | 意图类型 | 特征词 |
|-------|---------|-------|
"""
    for item in result['suggestions']:
        report += f"| {item['suggestion']} | {item['intent']} | {item['keyword']} |\n"

    # 结论
    main_intents = [k for k, v in result['intent_counts'].items() if v == max(result['intent_counts'].values())]
    report += f"""
### 结论
- 主要意图: {', '.join(main_intents)}
- 商业价值: {'高' if 'TRANSAC' in main_intents else '中' if 'NAV' in main_intents else '低'}
"""

    return report


def main():
    """命令行入口"""
    keyword = input("请输入搜索关键词: ").strip()

    if not keyword:
        print("关键词不能为空")
        return

    print(f"\n正在分析: {keyword} ...")

    report = generate_report(keyword)
    print(report)


if __name__ == "__main__":
    main()