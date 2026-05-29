#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘API爬取器
按照夸克项目规范：API优先策略
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class MeituanAPICrawler:
    """美团招聘API爬取器"""
    
    def __init__(self):
        # 配置信息
        self.api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
        self.referer_url = "https://zhaopin.meituan.com/web/social"
        
        # 筛选参数（基于用户说明）
        self.city_code = "001019002"  # 深圳
        self.category_codes = "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001"
        
        # 岗位类别映射（根据API响应）
        self.category_mapping = {
            "11002": "产品类",
            "11003": "运营类",
            "11005": "市场营销类",
            "11007": "金融类",
            "11010": "销售、客服与支持类"
        }
        
        # API响应中的jobFamily映射
        self.job_family_mapping = {
            "产品类": "产品类",
            "运营类": "运营类",
            "市场营销类": "市场营销类",
            "金融类": "金融类",
            "销售、客服与支持类": "销售、客服与支持类"
        }
        
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://zhaopin.meituan.com",
            "Referer": f"{self.referer_url}?cityList={self.city_code}&jfJgList={self.category_codes}",
            "Sec-Ch-Ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Priority": "u=1, i"
        }
        
        # 字段映射（13个字段，包含岗位亮点）
        self.field_mapping = {
            "position_id": "岗位ID",
            "position_name": "岗位名称",
            "work_location": "工作地点",
            "position_category": "岗位类别",
            "publish_time": "发布时间",
            "detail_url": "详情链接",
            "department": "部门信息",
            "education_requirement": "学历要求",
            "work_experience": "工作经验",
            "job_responsibilities": "工作职责",
            "job_requirements": "任职要求",
            "salary_range": "薪资范围",
            "high_light": "岗位亮点"  # 新增字段
        }
        
        logger.info(f"✅ 美团API爬取器初始化完成 - 深圳，{len(self.category_mapping)}个类别")
    
    def build_request_data(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """构建请求数据（使用准确格式）"""
        import time
        import uuid
        
        # 生成query_id
        timestamp = int(time.time() * 1000)
        u_query_id = uuid.uuid4().hex
        r_query_id = f"{timestamp}{int(time.time())}"
        
        return {
            "page": {
                "pageNo": page,
                "pageSize": page_size
            },
            "jobShareType": "1",
            "keywords": "",
            "cityList": [{"code": self.city_code}],
            "department": [],
            "jfJgList": [
                {"code": "11002", "subCode": []},
                {"code": "11003", "subCode": []},
                {"code": "11005", "subCode": []},
                {"code": "11007", "subCode": []},
                {"code": "11010", "subCode": ["1101001"]}
            ],
            "jobType": [{"code": "3", "subCode": []}],
            "typeCode": [],
            "specialCode": [],
            "u_query_id": u_query_id,
            "r_query_id": r_query_id
        }
    
    def send_api_request(self, page: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """发送API请求"""
        try:
            # 构建请求数据
            data = self.build_request_data(page, page_size)
            
            logger.info(f"📡 发送API请求 - 第{page}页，每页{page_size}条")
            logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            # 发送POST请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            logger.info(f"📥 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查API返回状态（美团使用status:1表示成功）
                if result.get("status") == 1:
                    logger.info(f"✅ API请求成功 - 第{page}页")
                    return result.get("data", {})
                else:
                    error_status = result.get("status", "未知")
                    error_msg = result.get("message", "未知错误")
                    logger.error(f"❌ API返回错误: status={error_status} - {error_msg}")
                    return None
            else:
                logger.error(f"❌ HTTP请求失败: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ API请求超时")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 网络连接错误")
            return None
        except json.JSONDecodeError:
            logger.error(f"📄 JSON解析失败")
            return None
        except Exception as e:
            logger.error(f"💥 API请求异常: {str(e)}")
            return None
    
    def extract_position_data(self, raw_position: Dict[str, Any]) -> Dict[str, Any]:
        """提取岗位数据（根据API响应格式）"""
        position_data = {}
        
        try:
            # 提取基础字段
            position_data["position_id"] = raw_position.get("jobUnionId", "未知ID")
            position_data["position_name"] = raw_position.get("name", "未知岗位")
            
            # 工作地点（从cityList提取）
            city_list = raw_position.get("cityList", [])
            if city_list:
                cities = [city.get("name", "") for city in city_list if city.get("name")]
                position_data["work_location"] = ", ".join(cities) if cities else "未知地点"
            else:
                position_data["work_location"] = "未知地点"
            
            # 岗位类别
            position_data["position_category"] = raw_position.get("jobFamily", "未知类别")
            position_data["position_subcategory"] = raw_position.get("jobFamilyGroup", "")
            
            # 发布时间（从refreshTime转换）
            refresh_time = raw_position.get("refreshTime")
            if refresh_time:
                # 时间戳转日期
                from datetime import datetime
                try:
                    dt = datetime.fromtimestamp(refresh_time / 1000)
                    position_data["publish_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    position_data["publish_time"] = str(refresh_time)
            else:
                position_data["publish_time"] = ""
            
            # 详情链接
            job_id = raw_position.get("jobUnionId", "")
            position_data["detail_url"] = f"https://zhaopin.meituan.com/job/{job_id}" if job_id else ""
            
            # 部门信息
            department_list = raw_position.get("department", [])
            if department_list:
                departments = [dept.get("name", "") for dept in department_list if dept.get("name")]
                position_data["department"] = ", ".join(departments) if departments else "未知部门"
            else:
                position_data["department"] = "未知部门"
            
            # 其他字段
            position_data["education_requirement"] = "学历不限"  # API未提供
            position_data["work_experience"] = raw_position.get("workYear", "经验不限")
            position_data["job_responsibilities"] = raw_position.get("jobDuty", "待补充")
            position_data["job_requirements"] = raw_position.get("jobRequirement", "待补充")
            position_data["salary_range"] = "面议"  # API未提供
            
            # 岗位亮点（重要字段）
            high_light = raw_position.get("highLight", "")
            position_data["high_light"] = high_light if high_light else "无"
            
            # 额外信息
            position_data["job_type"] = raw_position.get("jobType", "")
            position_data["job_special_code"] = raw_position.get("jobSpecialCode", "")
            position_data["desc"] = raw_position.get("desc", "")
            
            # 添加元数据
            position_data["raw_data"] = json.dumps(raw_position, ensure_ascii=False, separators=(',', ':'))
            position_data["extract_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            position_data["data_source"] = "meituan_api"
            
            # 验证数据完整性
            missing_fields = []
            for field in self.field_mapping.keys():
                if field not in position_data or not position_data[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.debug(f"⚠️ 岗位 {position_data['position_id']} 缺少字段: {missing_fields}")
            
        except Exception as e:
            logger.error(f"💥 数据提取异常: {str(e)}")
            position_data["error"] = str(e)
        
        return position_data
    
    def crawl_single_page(self, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """爬取单页数据"""
        logger.info(f"📄 开始爬取第{page}页，每页{page_size}条")
        
        # 发送API请求
        api_data = self.send_api_request(page, page_size)
        
        if not api_data:
            logger.warning(f"⚠️ 第{page}页爬取失败")
            return [], {}
        
        # 提取岗位列表
        positions = []
        raw_positions = api_data.get("list", [])
        
        # 美团API可能返回异常的totalCount，使用page信息
        page_info_data = api_data.get("page", {})
        total_count = page_info_data.get("totalCount", 0)
        total_pages = page_info_data.get("totalPage", 0)
        
        # 如果page_info中没有，尝试从api_data根获取
        if not total_count:
            total_count = api_data.get("total", 0)
        if not total_pages:
            total_pages = api_data.get("pages", 0)
        
        logger.info(f"📊 第{page}页数据: {len(raw_positions)}个岗位，总计{total_count}个，共{total_pages}页")
        
        # 提取每个岗位数据
        for raw_position in raw_positions:
            position_data = self.extract_position_data(raw_position)
            if position_data:
                positions.append(position_data)
        
        # 页面信息
        page_info = {
            "page": page,
            "page_size": page_size,
            "current_count": len(positions),
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": len(raw_positions) == page_size,  # 如果本页满员，可能有下一页
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"✅ 第{page}页爬取完成: {len(positions)}个岗位")
        return positions, page_info
    
    def crawl_all_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """爬取所有页面数据"""
        all_positions = []
        
        logger.info(f"🚀 开始爬取所有页面，最多{max_pages}页")
        
        # 先获取第一页，了解总页数
        first_positions, first_page_info = self.crawl_single_page(1)
        all_positions.extend(first_positions)
        
        total_pages = first_page_info.get("total_pages", 0)
        actual_max_pages = min(total_pages, max_pages)
        
        # 根据实际数据判断总页数
        if total_pages > 0:
            actual_max_pages = min(total_pages, max_pages)
            logger.info(f"📊 API返回总页数: {total_pages}，实际爬取: {actual_max_pages}页")
        else:
            # API未返回总页数，根据第一页数据判断
            actual_max_pages = max_pages
            logger.info(f"📊 API未返回总页数，按最大页数爬取: {actual_max_pages}页")
        
        # 爬取后续页面
        current_page = 2
        while current_page <= actual_max_pages:
            logger.info(f"⏳ 爬取进度: {current_page-1}/{actual_max_pages}页")
            
            # 添加延迟，避免请求过快
            time.sleep(1)
            
            positions, page_info = self.crawl_single_page(current_page)
            
            if not positions:
                logger.warning(f"⚠️ 第{current_page}页无数据，停止爬取")
                break
            
            all_positions.extend(positions)
            
            # 显示进度
            if current_page % 5 == 0 or current_page == actual_max_pages:
                logger.info(f"📈 已爬取 {current_page}/{actual_max_pages} 页，累计 {len(all_positions)} 个岗位")
            
            # 检查是否有下一页
            if not page_info.get("has_next", False):
                logger.info(f"📄 第{current_page}页不满{page_info['page_size']}条，可能无更多数据")
                break
            
            current_page += 1
        
        logger.info(f"🎉 所有页面爬取完成: {len(all_positions)}个岗位，{actual_max_pages}页")
        return all_positions
    
    def test_api_connection(self) -> Tuple[bool, str, Dict[str, Any]]:
        """测试API连接"""
        logger.info("🔍 测试美团API连接...")
        
        test_steps = []
        
        # 步骤1: 测试网络连接
        try:
            response = requests.get("https://zhaopin.meituan.com", timeout=10)
            test_steps.append({
                "step": "网络连接",
                "status": "success",
                "message": f"网站可访问，状态码: {response.status_code}"
            })
        except Exception as e:
            test_steps.append({
                "step": "网络连接",
                "status": "failed",
                "message": f"网站访问失败: {str(e)}"
            })
            return False, "网络连接失败", {"steps": test_steps}
        
        # 步骤2: 测试API端点
        try:
            response = requests.head(self.api_url, timeout=10)
            test_steps.append({
                "step": "API端点",
                "status": "success",
                "message": f"API端点可访问，状态码: {response.status_code}"
            })
        except Exception as e:
            test_steps.append({
                "step": "API端点",
                "status": "failed",
                "message": f"API端点访问失败: {str(e)}"
            })
        
        # 步骤3: 测试API数据获取
        api_data = self.send_api_request(1, 1)
        if api_data:
            test_steps.append({
                "step": "数据获取",
                "status": "success",
                "message": f"API数据获取成功，获取到{len(api_data.get('list', []))}个岗位"
            })
            return True, "API连接测试成功", {"steps": test_steps}
        else:
            test_steps.append({
                "step": "数据获取",
                "status": "failed",
                "message": "API数据获取失败"
            })
            return False, "API数据获取失败", {"steps": test_steps}
    
    def save_positions(self, positions: List[Dict[str, Any]], filename: str = None) -> str:
        """保存岗位数据"""
        import os
        
        # 创建输出目录
        output_dir = "output/crawl_data"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meituan_positions_{timestamp}.json"
        
        filepath = os.path.join(output_dir, filename)
        
        # 构建完整数据
        data = {
            "company": "美团",
            "city_code": self.city_code,
            "city_name": "深圳",
            "categories": list(self.category_mapping.values()),
            "total_positions": len(positions),
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "meituan_api",
            "api_url": self.api_url,
            "positions": positions
        }
        
        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 数据已保存: {filepath} ({len(positions)} 个岗位)")
        
        # 同时保存CSV格式
        self.save_to_csv(positions, filepath.replace('.json', '.csv'))
        
        return filepath
    
    def save_to_csv(self, positions: List[Dict[str, Any]], csv_filepath: str):
        """保存为CSV格式（包含high_light字段）"""
        import csv
        
        if not positions:
            logger.warning("⚠️ 没有数据可保存为CSV")
            return
        
        # 获取所有字段（包含high_light）
        fieldnames = list(self.field_mapping.keys())
        
        # 添加额外字段
        fieldnames.extend(["extract_time", "data_source"])
        
        try:
            with open(csv_filepath, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for position in positions:
                    # 只保留需要的字段
                    row = {}
                    for field in fieldnames:
                        value = position.get(field, "")
                        # 处理换行符，确保CSV格式正确
                        if isinstance(value, str) and '\n' in value:
                            # CSV中换行符需要特殊处理
                            value = value.replace('\n', ' ').replace('\r', ' ')
                        row[field] = value
                    writer.writerow(row)
            
            logger.info(f"📊 CSV数据已保存: {csv_filepath} ({len(positions)}行, {len(fieldnames)}列)")
            
            # 验证CSV文件
            self.verify_csv_file(csv_filepath, fieldnames)
            
        except Exception as e:
            logger.error(f"❌ CSV保存失败: {str(e)}")
            
    def verify_csv_file(self, csv_filepath: str, expected_columns: List[str]):
        """验证CSV文件格式"""
        import csv
        
        try:
            with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                actual_columns = reader.fieldnames
                
                if actual_columns != expected_columns:
                    logger.warning(f"⚠️ CSV列不匹配: 预期{len(expected_columns)}列，实际{len(actual_columns)}列")
                    logger.warning(f"   缺失列: {set(expected_columns) - set(actual_columns)}")
                    logger.warning(f"   多余列: {set(actual_columns) - set(expected_columns)}")
                else:
                    logger.info(f"✅ CSV验证通过: {len(actual_columns)}列正确")
                    
                    # 检查high_light列是否存在
                    if 'high_light' in actual_columns:
                        logger.info(f"✅ high_light字段已包含在CSV中")
                    else:
                        logger.error(f"❌ high_light字段未包含在CSV中")
        except Exception as e:
            logger.error(f"❌ CSV验证失败: {str(e)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='美团招聘API爬取器')
    parser.add_argument('--mode', choices=['test', 'single', 'all', 'pages'], 
                       default='test', help='运行模式: test(测试), single(单页), all(全部), pages(指定页数)')
    parser.add_argument('--pages', type=int, default=1, help='爬取页数')
    parser.add_argument('--page-size', type=int, default=10, help='每页数量')
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--verbose', action='store_true', help='详细日志')
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("🚀 美团招聘API爬取器启动")
    print(f"📋 公司: 美团")
    print(f"🌐 API: https://zhaopin.meituan.com/api/official/job/getJobList")
    print(f"🏙️ 城市: 深圳 (001019002)")
    print(f"📁 类别: {len(MeituanAPICrawler().category_mapping)}个")
    print("=" * 60)
    
    crawler = MeituanAPICrawler()
    
    if args.mode == 'test':
        # 测试模式
        print("🔍 测试API连接...")
        success, message, details = crawler.test_api_connection()
        
        if success:
            print(f"✅ {message}")
            print("\n📋 测试步骤详情:")
            for step in details['steps']:
                status_icon = '✅' if step['status'] == 'success' else '❌'
                print(f"  {status_icon} {step['step']}: {step['message']}")
        else:
            print(f"❌ {message}")
        
        # 显示配置信息
        print("\n⚙️ 当前配置:")
        print(f"  API地址: {crawler.api_url}")
        print(f"  城市代码: {crawler.city_code} (深圳)")
        print(f"  类别代码: {crawler.category_codes}")
        print(f"  字段映射: {len(crawler.field_mapping)}个字段")
        
    elif args.mode == 'single':
        # 单页爬取
        print(f"📄 爬取单页数据 (第1页，每页{args.page_size}条)...")
        positions, page_info = crawler.crawl_single_page(1, args.page_size)
        
        if positions:
            print(f"✅ 爬取成功: {len(positions)}个岗位")
            print(f"📊 页面信息: 第{page_info['page']}页，共{page_info['total_pages']}页，总计{page_info['total_count']}个岗位")
            
            # 保存数据
            if args.output:
                filename = args.output
            else:
                filename = f"meituan_page_1_{int(time.time())}.json"
            
            saved_file = crawler.save_positions(positions, filename)
            print(f"💾 数据已保存: {saved_file}")
            
            # 显示前几个岗位
            print("\n📋 前3个岗位示例:")
            for i, position in enumerate(positions[:3]):
                print(f"\n  [{i+1}] {position.get('position_name', '未知岗位')}")
                print(f"     地点: {position.get('work_location', '未知')}")
                print(f"     类别: {position.get('position_category', '未知')}")
                print(f"     部门: {position.get('department', '未知')}")
        else:
            print("❌ 爬取失败，未获取到数据")
    
    elif args.mode == 'all':
        # 爬取所有页面
        print(f"🚀 爬取所有页面数据 (最多{args.pages}页)...")
        positions = crawler.crawl_all_pages(args.pages)
        
        if positions:
            print(f"✅ 爬取完成: {len(positions)}个岗位")
            
            # 保存数据
            saved_file = crawler.save_positions(positions, args.output)
            print(f"💾 数据已保存: {saved_file}")
            
            # 数据统计
            print("\n📊 数据统计:")
            categories = {}
            departments = {}
            for position in positions:
                category = position.get('position_category', '未知')
                department = position.get('department', '未知')
                
                categories[category] = categories.get(category, 0) + 1
                departments[department] = departments.get(department, 0) + 1
            
            print(f"  岗位类别分布:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"    {category}: {count}个")
            
            print(f"\n  热门部门 (前5):")
            for department, count in sorted(departments.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {department}: {count}个")
        else:
            print("❌ 爬取失败，未获取到数据")
    
    elif args.mode == 'pages':
        # 爬取指定页数
        print(f"📚 爬取指定页数: {args.pages}页")
        all_positions = []
        
        for page in range(1, args.pages + 1):
            print(f"\n📄 爬取第{page}页...")
            positions, page_info = crawler.crawl_single_page(page, args.page_size)
            
            if positions:
                all_positions.extend(positions)
                print(f"✅ 第{page}页: {len(positions)}个岗位")
            else:
                print(f"⚠️ 第{page}页: 爬取失败")
            
            # 页间延迟
            if page < args.pages:
                time.sleep(1)
        
        if all_positions:
            print(f"\n🎉 所有页面爬取完成: {len(all_positions)}个岗位")
            saved_file = crawler.save_positions(all_positions, args.output)
            print(f"💾 数据已保存: {saved_file}")
        else:
            print("❌ 所有页面爬取失败")
    
    print("\n" + "=" * 60)
    print("🎉 美团招聘API爬取器执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()