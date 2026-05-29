#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘城市代码验证脚本
验证城市代码与实际城市的对应关系
"""

import requests
import json
import time
import logging
from typing import Dict, List, Tuple, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeituanCityValidator:
    """美团城市代码验证器"""
    
    def __init__(self):
        self.base_url = "https://zhaopin.meituan.com/web/social"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 待验证的城市代码映射（推测）
        self.city_mapping = {
            "001019001": "北京",
            "001019002": "深圳",  # 已确认
            "001019003": "上海",
            "001019004": "杭州", 
            "001019005": "广州",
            "001019006": "成都",
            "001019007": "南京",  # 推测
            "001019008": "武汉",  # 推测
            "001019009": "西安",  # 推测
            "001019010": "苏州"   # 推测
        }
        
        # 验证结果
        self.validation_results = {}
    
    def validate_single_city(self, city_code: str, city_name: str) -> Dict[str, any]:
        """
        验证单个城市代码
        
        Args:
            city_code: 城市代码
            city_name: 城市名称（推测）
            
        Returns:
            验证结果字典
        """
        logger.info(f"🔍 验证城市代码: {city_code} ({city_name})")
        
        result = {
            "city_code": city_code,
            "expected_name": city_name,
            "status": "unknown",
            "http_status": None,
            "page_title": None,
            "page_size": None,
            "error": None,
            "suggested_name": None,
            "confidence": 0
        }
        
        try:
            # 构建URL
            url = f"{self.base_url}?cityList={city_code}"
            
            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=10)
            result["http_status"] = response.status_code
            
            if response.status_code == 200:
                # 分析页面内容
                content = response.text
                result["page_size"] = len(content)
                
                # 提取页面标题
                import re
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    result["page_title"] = title_match.group(1)
                
                # 分析页面内容判断城市
                city_found = self._analyze_city_from_content(content, city_name)
                
                if city_found:
                    result["status"] = "confirmed"
                    result["suggested_name"] = city_name
                    result["confidence"] = 90
                    logger.info(f"✅ {city_code} 确认对应 {city_name}")
                else:
                    # 尝试从页面提取城市信息
                    extracted_city = self._extract_city_from_content(content)
                    if extracted_city:
                        result["status"] = "corrected"
                        result["suggested_name"] = extracted_city
                        result["confidence"] = 70
                        logger.info(f"🔄 {city_code} 可能对应 {extracted_city} (原推测: {city_name})")
                    else:
                        result["status"] = "uncertain"
                        result["confidence"] = 30
                        logger.info(f"❓ {city_code} 无法确认城市")
            
            elif response.status_code == 404:
                result["status"] = "not_found"
                result["confidence"] = 10
                logger.warning(f"❌ {city_code} 页面不存在 (404)")
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                logger.warning(f"⚠️ {city_code} 请求失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "请求超时"
            logger.error(f"⏰ {city_code} 请求超时")
        except requests.exceptions.ConnectionError:
            result["status"] = "connection_error"
            result["error"] = "连接错误"
            logger.error(f"🔌 {city_code} 连接错误")
        except Exception as e:
            result["status"] = "exception"
            result["error"] = str(e)
            logger.error(f"💥 {city_code} 验证异常: {str(e)}")
        
        # 添加延迟，避免请求过快
        time.sleep(1)
        
        return result
    
    def _analyze_city_from_content(self, content: str, expected_city: str) -> bool:
        """
        从页面内容分析城市信息
        
        Args:
            content: 页面HTML内容
            expected_city: 期望的城市名称
            
        Returns:
            是否找到城市信息
        """
        # 转换为小写便于搜索
        content_lower = content.lower()
        expected_lower = expected_city.lower()
        
        # 检查页面是否包含城市名称
        if expected_lower in content_lower:
            return True
        
        # 检查常见城市关键词
        city_keywords = {
            "北京": ["beijing", "北京", "首都"],
            "深圳": ["shenzhen", "深圳", "sz"],
            "上海": ["shanghai", "上海", "sh"],
            "杭州": ["hangzhou", "杭州", "hz"],
            "广州": ["guangzhou", "广州", "gz"],
            "成都": ["chengdu", "成都", "cd"]
        }
        
        if expected_city in city_keywords:
            for keyword in city_keywords[expected_city]:
                if keyword.lower() in content_lower:
                    return True
        
        return False
    
    def _extract_city_from_content(self, content: str) -> Optional[str]:
        """
        从页面内容提取城市信息
        
        Args:
            content: 页面HTML内容
            
        Returns:
            提取到的城市名称，或None
        """
        import re
        
        # 尝试从标题提取
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            
            # 检查标题中的城市
            cities = ["北京", "深圳", "上海", "杭州", "广州", "成都", "南京", "武汉", "西安", "苏州"]
            for city in cities:
                if city in title:
                    return city
        
        # 尝试从页面文本提取
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', content)
        
        # 查找城市关键词
        city_patterns = {
            "北京": r'北京|beijing|首都',
            "深圳": r'深圳|shenzhen|SZ',
            "上海": r'上海|shanghai|SH',
            "杭州": r'杭州|hangzhou|HZ',
            "广州": r'广州|guangzhou|GZ',
            "成都": r'成都|chengdu|CD'
        }
        
        for city, pattern in city_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return city
        
        return None
    
    def validate_all_cities(self) -> Dict[str, Dict[str, any]]:
        """
        验证所有城市代码
        
        Returns:
            所有城市的验证结果
        """
        logger.info(f"🚀 开始验证 {len(self.city_mapping)} 个城市代码")
        
        results = {}
        
        for city_code, city_name in self.city_mapping.items():
            result = self.validate_single_city(city_code, city_name)
            results[city_code] = result
            
            # 显示进度
            completed = len(results)
            total = len(self.city_mapping)
            logger.info(f"📊 进度: {completed}/{total} ({completed/total*100:.1f}%)")
        
        self.validation_results = results
        return results
    
    def generate_report(self) -> str:
        """生成验证报告"""
        if not self.validation_results:
            return "❌ 没有验证结果，请先运行 validate_all_cities()"
        
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("📋 美团招聘城市代码验证报告")
        report_lines.append("=" * 70)
        report_lines.append(f"验证时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"验证总数: {len(self.validation_results)}")
        report_lines.append("")
        
        # 按状态分类
        status_counts = {}
        for result in self.validation_results.values():
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report_lines.append("📊 验证结果统计:")
        for status, count in sorted(status_counts.items()):
            report_lines.append(f"  {status}: {count} 个")
        
        report_lines.append("")
        report_lines.append("🏙️ 详细结果:")
        report_lines.append("-" * 70)
        
        # 显示每个城市的结果
        for city_code, result in sorted(self.validation_results.items()):
            expected = result["expected_name"]
            status = result["status"]
            suggested = result.get("suggested_name", "N/A")
            confidence = result.get("confidence", 0)
            
            # 状态图标
            status_icon = {
                "confirmed": "✅",
                "corrected": "🔄", 
                "uncertain": "❓",
                "not_found": "❌",
                "error": "⚠️",
                "timeout": "⏰",
                "connection_error": "🔌",
                "exception": "💥",
                "unknown": "❔"
            }.get(status, "❔")
            
            line = f"{status_icon} {city_code}: "
            line += f"期望={expected}, "
            
            if status == "confirmed":
                line += f"✅ 确认={suggested}"
            elif status == "corrected":
                line += f"🔄 修正为={suggested} (置信度:{confidence}%)"
            else:
                line += f"状态={status}"
                if result.get("error"):
                    line += f", 错误={result['error']}"
            
            report_lines.append(line)
        
        report_lines.append("")
        report_lines.append("💡 建议:")
        
        # 分析建议
        confirmed_cities = [c for c, r in self.validation_results.items() if r["status"] == "confirmed"]
        if confirmed_cities:
            report_lines.append(f"1. ✅ 已确认 {len(confirmed_cities)} 个城市代码")
            for city_code in confirmed_cities:
                result = self.validation_results[city_code]
                report_lines.append(f"   - {city_code}: {result['suggested_name']}")
        
        corrected_cities = [c for c, r in self.validation_results.items() if r["status"] == "corrected"]
        if corrected_cities:
            report_lines.append(f"2. 🔄 需要修正 {len(corrected_cities)} 个城市代码")
            for city_code in corrected_cities:
                result = self.validation_results[city_code]
                report_lines.append(f"   - {city_code}: {result['expected_name']} → {result['suggested_name']}")
        
        # 特别提醒深圳
        shenzhen_result = self.validation_results.get("001019002")
        if shenzhen_result and shenzhen_result["status"] == "confirmed":
            report_lines.append("3. 🎯 重要确认: 001019002 确实对应深圳（不是北京）")
        
        report_lines.append("")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def save_results(self, filepath: str = "city_validation_results.json"):
        """保存验证结果到文件"""
        if not self.validation_results:
            logger.warning("没有验证结果可保存")
            return
        
        data = {
            "validation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cities": len(self.validation_results),
            "results": self.validation_results,
            "summary": {
                "confirmed": sum(1 for r in self.validation_results.values() if r["status"] == "confirmed"),
                "corrected": sum(1 for r in self.validation_results.values() if r["status"] == "corrected"),
                "uncertain": sum(1 for r in self.validation_results.values() if r["status"] == "uncertain"),
                "failed": sum(1 for r in self.validation_results.values() if r["status"] in ["error", "timeout", "connection_error", "exception"])
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 验证结果已保存到: {filepath}")
    
    def update_config_files(self):
        """根据验证结果更新配置文件"""
        if not self.validation_results:
            logger.error("没有验证结果，无法更新配置")
            return
        
        # 收集确认的城市映射
        confirmed_mapping = {}
        for city_code, result in self.validation_results.items():
            if result["status"] == "confirmed":
                suggested = result.get("suggested_name")
                if suggested:
                    confirmed_mapping[city_code] = suggested
            elif result["status"] == "corrected":
                suggested = result.get("suggested_name")
                if suggested:
                    confirmed_mapping[city_code] = suggested
        
        if not confirmed_mapping:
            logger.warning("没有确认的城市映射可更新")
            return
        
        # 生成城市映射字符串
        mapping_str = ",".join([f"{code}:{name}" for code, name in confirmed_mapping.items()])
        
        logger.info(f"📝 确认的城市映射: {mapping_str}")
        
        # 这里可以添加更新配置文件的逻辑
        # 例如更新 config/.env 中的 MEITUAN_CITY_MAPPING
        
        return confirmed_mapping


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='美团招聘城市代码验证')
    parser.add_argument('--city', help='验证单个城市代码，如 001019002')
    parser.add_argument('--all', action='store_true', help='验证所有城市代码')
    parser.add_argument('--save', action='store_true', help='保存验证结果')
    parser.add_argument('--update', action='store_true', help='更新配置文件')
    parser.add_argument('--output', default='city_validation_results.json', help='输出文件路径')
    
    args = parser.parse_args()
    
    validator = MeituanCityValidator()
    
    if args.city:
        # 验证单个城市
        if args.city in validator.city_mapping:
            result = validator.validate_single_city(args.city, validator.city_mapping[args.city])
            print(f"\n🔍 单个城市验证结果:")
            print(f"城市代码: {args.city}")
            print(f"期望名称: {validator.city_mapping[args.city]}")
            print(f"验证状态: {result['status']}")
            if result.get('suggested_name'):
                print(f"建议名称: {result['suggested_name']}")
            if result.get('page_title'):
                print(f"页面标题: {result['page_title']}")
            if result.get('error'):
                print(f"错误信息: {result['error']}")
        else:
            print(f"❌ 未知的城市代码: {args.city}")
            print(f"已知代码: {', '.join(validator.city_mapping.keys())}")
    
    elif args.all:
        # 验证所有城市
        print("🚀 开始验证所有美团招聘城市代码...")
        results = validator.validate_all_cities()
        
        # 生成报告
        report = validator.generate_report()
        print(report)
        
        if args.save:
            validator.save_results(args.output)
        
        if args.update:
            confirmed = validator.update_config_files()
            if confirmed:
                print(f"\n✅ 确认的城市代码映射:")
                for code, name in confirmed.items():
                    print(f"  {code}: {name}")
    
    else:
        # 默认验证当前项目使用的深圳
        print("🔍 验证当前项目使用的城市代码 (001019002)...")
        result = validator.validate_single_city("001019002", "深圳")
        
        print(f"\n验证结果:")
        print(f"城市代码: 001019002")
        print(f"期望名称: 深圳")
        print(f"验证状态: {result['status']}")
        
        if result['status'] == 'confirmed':
            print("✅ 确认: 001019002 确实对应深圳")
            print("🎯 重要: 之前误识别为北京，现已修正")
        elif result['status'] == 'corrected':
            print(f"🔄 修正为: {result.get('suggested_name', '未知')}")
        else:
            print(f"⚠️ 无法确认: {result.get('error', '未知原因')}")
        
        if args.save:
            validator.validation_results = {"001019002": result}
            validator.save_results(args.output)


if __name__ == "__main__":
    main()