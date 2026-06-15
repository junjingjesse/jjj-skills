"""
Google Trends API Wrapper
获取Google Trends多维度数据
"""
import requests
import json
import sys
import time
from typing import Dict, List, Optional
from pytrends.request import TrendReq

# 配置（pytrends需要列表格式）
PROXIES = ['http://127.0.0.1:9098']
TIMEOUT = 30

# GPTS变体列表（轮换使用，避免被识别）
BENCHMARK_VARIANTS = ['gpts', 'GPTs', 'Gpts', 'gPTS', 'GPTS']
BENCHMARK_INDEX = 0


def get_next_variant():
    """轮换获取变体"""
    global BENCHMARK_INDEX
    while True:
        yield BENCHMARK_VARIANTS[BENCHMARK_INDEX % len(BENCHMARK_VARIANTS)]
        BENCHMARK_INDEX += 1


variant_generator = get_next_variant()


def get_absolute_trend(word: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> Dict:
    """绝对趋势判断"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
        pytrends.build_payload(kw_list=[word])
        data = pytrends.interest_over_time()

        if data.empty or word not in data.columns:
            return {'error': 'No data'}

        word_data = data[word].dropna()
        if len(word_data) < 3:
            return {'error': 'Insufficient data'}

        recent_avg = word_data.tail(3).mean()
        overall_avg = word_data.mean()
        ratio = recent_avg / overall_avg if overall_avg > 0 else 0

        return {
            'recent_avg': round(recent_avg, 2),
            'overall_avg': round(overall_avg, 2),
            'is_rising': recent_avg > overall_avg,
            'ratio': round(ratio, 2),
            'data_points': len(word_data)
        }
    except Exception as e:
        return {'error': str(e)}


def get_benchmark_trend(word: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> Dict:
    """基准词对��比"""
    benchmark = next(variant_generator)
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
        pytrends.build_payload(kw_list=[word, benchmark])
        data = pytrends.interest_over_time()

        if data.empty or word not in data.columns or benchmark not in data.columns:
            return {'error': 'No data'}

        word_data = data[word].dropna()
        benchmark_data = data[benchmark].dropna()

        word_avg = word_data.mean()
        benchmark_avg = benchmark_data.mean()
        ratio = word_avg / benchmark_avg if benchmark_avg > 0 else 0

        return {
            'word_avg': round(word_avg, 2),
            'benchmark': benchmark,
            'benchmark_avg': round(benchmark_avg, 2),
            'ratio': round(ratio, 4),
            'is_near_benchmark': ratio > 0.1
        }
    except Exception as e:
        return {'error': str(e)}


def get_related_queries(keyword: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> List[Dict]:
    """获取相关查询词"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
        pytrends.build_payload(kw_list=[keyword])
        related = pytrends.related_queries()

        if keyword not in related:
            return []

        results = []
        for query_type in ['rising', 'top']:
            if query_type in related[keyword]:
                df = related[keyword][query_type]
                if df is not None and not df.empty:
                    for _, row in df.head(10).iterrows():
                        results.append({'query': row['query'], 'value': row['value'], 'type': query_type})
        return results
    except Exception as e:
        return [{'error': str(e)}]


def get_geo_trend(keyword: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> List[Dict]:
    """获取地域分布数据"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
        pytrends.build_payload(kw_list=[keyword])
        geo_data = pytrends.interest_by_region(region='US', resolution='COUNTRY')

        if geo_data.empty:
            return []

        results = []
        for region, value in geo_data[keyword].dropna().items():
            results.append({'region': region, 'value': int(value)})
        return sorted(results, key=lambda x: x['value'], reverse=True)
    except Exception as e:
        return [{'error': str(e)}]


def get_seasonality(keyword: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> Dict:
    """季节性分析"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
        pytrends.build_payload(kw_list=[keyword], timeframe='today 12-m')
        data = pytrends.interest_over_time()

        if data.empty or keyword not in data.columns:
            return {'error': 'No data'}

        word_data = data[keyword].dropna()
        values = word_data.tolist()
        if len(values) < 12:
            return {'error': 'Insufficient data'}

        monthly_avg = [sum(values[i*4:(i+1)*4])/4 for i in range(12)]
        peak = max(monthly_avg)
        valley = min(monthly_avg)
        avg = sum(monthly_avg) / 12
        peak_ratio = peak / valley if valley > 0 else 0

        return {
            'peak': round(peak, 2),
            'valley': round(valley, 2),
            'avg': round(avg, 2),
            'peak_ratio': round(peak_ratio, 2),
            'has_seasonality': peak_ratio > 3,
            'monthly_avg': [round(v, 2) for v in monthly_avg]
        }
    except Exception as e:
        return {'error': str(e)}


def get_trend_direction(keyword: str, proxies: List[str] = PROXIES, timeout: int = TIMEOUT) -> Dict:
    """趋势方向分析"""
    timeframes = {'3个月': 'today 3-m', '12个月': 'today 12-m', '5年': 'today 5-y'}
    results = {}

    for name, tf in timeframes.items():
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=timeout, proxies=proxies)
            pytrends.build_payload(kw_list=[keyword], timeframe=tf)
            data = pytrends.interest_over_time()

            if data.empty or keyword not in data.columns:
                results[name] = {'error': 'No data'}
                continue

            word_data = data[keyword].dropna()
            if len(word_data) < 2:
                results[name] = {'error': 'Insufficient data'}
                continue

            mid = len(word_data) // 2
            first_half = word_data.iloc[:mid].mean()
            second_half = word_data.iloc[mid:].mean()
            growth = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0

            direction = '上升' if growth > 5 else ('下降' if growth < -5 else '平稳')
            results[name] = {'first_half': round(first_half, 2), 'second_half': round(second_half, 2), 'growth': round(growth, 2), 'direction': direction}
        except Exception as e:
            results[name] = {'error': str(e)}

    return results


def draw_bar_chart(data: List[Dict], max_width: int = 30) -> str:
    """绘制横向条形图"""
    if not data or not isinstance(data[0], dict):
        return "无数据"

    max_value = max([d.get('value', 0) for d in data], default=1)
    if max_value == 0:
        return "无数据"

    lines = []
    for item in data[:8]:
        value = item.get('value', 0)
        name = item.get('region', item.get('query', str(item)))[:18]
        bar_len = int((value / max_value) * max_width)
        bar = '█' * bar_len
        lines.append(f"{name:18} |{bar} {value}")

    return '\n'.join(lines)


def draw_trend_chart(monthly_avg: List[float]) -> str:
    """绘制趋势柱状图"""
    if not monthly_avg:
        return "无数据"

    months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    lines = []
    for i in range(12):
        val = monthly_avg[i]
        bar = '▓' * int(val / 10)
        lines.append(f"  {months[i]} {bar} {val:.0f}")
    return '\n'.join(lines)


def generate_report(keyword: str) -> str:
    """生成CLI格式趋势验证报告"""
    abs_trend = get_absolute_trend(keyword)
    seasonality = get_seasonality(keyword)
    trend_dir = get_trend_direction(keyword)
    geo = get_geo_trend(keyword)
    related = get_related_queries(keyword)
    benchmark = get_benchmark_trend(keyword)

    report = ""
    report += "=" * 60 + "\n"
    report += "       Google Trends 趋势分析报告\n"
    report += "                关键词: " + keyword + "\n"
    report += "=" * 60 + "\n\n"

    report += "[绝对趋势判断]\n"
    is_rising = "是" if abs_trend.get('is_rising') else "否"
    report += f"  - 上升趋势: {is_rising}\n"
    report += f"  - 近期/整体比率: {abs_trend.get('ratio', 'N/A')}x ({abs_trend.get('recent_avg', 'N/A')}/{abs_trend.get('overall_avg', 'N/A')})\n"
    report += f"  - 数据点数: {abs_trend.get('data_points', 'N/A')}\n\n"

    report += "[趋势方向]\n"
    for period in ['3个月', '12个月', '5年']:
        d = trend_dir.get(period, {})
        growth = d.get('growth', 'N/A')
        if isinstance(growth, (int, float)):
            growth_str = f"{growth:+.1f}%"
        else:
            growth_str = str(growth)
        report += f"  - {period}: {d.get('direction', 'N/A')} ({growth_str})\n"

    report += "\n[季节性分析]\n"
    report += f"  - 峰谷比: {seasonality.get('peak_ratio', 'N/A')}x\n"
    has_season = "是" if seasonality.get('has_seasonality') else "否"
    report += f"  - 季节性: {has_season}\n"
    report += "  - 12个月走势:\n"
    if seasonality.get('monthly_avg'):
        chart = draw_trend_chart(seasonality['monthly_avg'])
        for line in chart.split('\n'):
            report += f"      {line}\n"

    report += "\n[地域分布 Top 8]\n"
    report += draw_bar_chart(geo[:8]) + "\n"

    report += "\n[相关查询 Top 8]\n"
    related_data = [{'query': r['query'], 'value': r['value']} for r in related[:8]]
    report += draw_bar_chart(related_data) + "\n"

    if benchmark and 'error' not in str(benchmark):
        report += "\n[基准词对比]\n"
        report += f"  - 基准词: {benchmark.get('benchmark', 'N/A')}\n"
        report += f"  - 基准搜索量: {benchmark.get('benchmark_avg', 'N/A')}\n"
        report += f"  - 目标词/基准比: {benchmark.get('ratio', 'N/A')}\n"
        near = "是" if benchmark.get('is_near_benchmark') else "否"
        report += f"  - 接近基准: {near}\n"

    # 综合评估
    report += "=" * 60 + "\n"
    report += "[综合评估]\n"

    issues = []
    if seasonality.get('has_seasonality'):
        issues.append("季节性明显")
    if not abs_trend.get('is_rising'):
        issues.append("趋势下降")
    if trend_dir.get('12个月', {}).get('growth', 0) < -10:
        issues.append("12个月下降")

    if not issues:
        report += "  推荐 - 稳定上升，非季节性词\n"
    else:
        for issue in issues:
            report += f"  {issue}\n"

    report += "=" * 60 + "\n"

    # 概念解读
    report += """
============================================================
[概念解读 - 帮助理解报告]

■ 绝对趋势判断
  - 上升趋势: 最近3个月搜索量是否超过历史平均
  - 近期/整体比率: "1.34x" 表示近期平均是整体的1.34倍
  - 数据点数: 统计的周数（52周=1年数据）

■ 趋势方向
  - 3个月: 短期趋势，判断是否正在崛起或衰落
  - 12个月: 中期趋势，判断全年走向
  - 5年: 长期趋势，判断是否是新兴词汇
  - 增长%为正=上升，为负=下降

■ 季节性分析
  - 峰谷比: 最高月/最低月的比值
  - >3倍=有明显季节性，<2倍=全年稳定
  - 季节性词只在特定时间有量（如圣诞词汇）

■ 地域分布
  - 各国家的搜索量占比
  - 用于判断目标市场

■ 相关查询
  - 和该关键词一起被搜索的词
  - rising=上升最快的词，top=搜索量最大的词

■ 基准词对比
  - gpts基准: 每天约5000搜索量的参考词
  - 目标词/基准比: >0.1=有探索价值
  - 接近基准=该词在目标市场有一定需求量

■ 综合评估
  - 推荐: 上升趋势+非季节性+趋势平稳或上升
  - 需谨慎: 季节性明显 或 趋势下降
============================================================"""

    return report


if __name__ == '__main__':
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    else:
        keyword = input("输入关键词: ")

    print(generate_report(keyword))