#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼多多招聘爬取器 - 基于夸克项目智能选择器框架
阶段1：基础API爬取（列表页数据）
"""

import logging
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import requests
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PddApiCrawler:
    """拼多多API爬取器（基础版）"""
    
    def __init__(self, config_path: str = None):
        """
        初始化API爬取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "config/api_auth.json"
        self.config = self._load_config()
        self.env_config = self._load_env_config()
        
        # API配置
        self.api_endpoint = self.env_config.get("PDD_API_FULL_URL", "https://careers.pddglobalhr.com/api/recruit/position/list")
        self.api_method = self.env_config.get("PDD_API_METHOD", "POST")
        self.content_type = self.env_config.get("PDD_API_CONTENT_TYPE", "application/json")
        
        # 认证信息
        self.cookie_nano_fp = self.env_config.get("PDD_COOKIE_NANO_FP", "")
        self.anti_content = self.env_config.get("PDD_ANTI_CONTENT", "")
        
        # 请求头配置
        self.headers = self._build_headers()
        
        # 请求参数
        self.page_param = self.env_config.get("PAGE_PARAM", "page")
        self.size_param = self.env_config.get("SIZE_PARAM", "pageSize")
        self.default_page_size = int(self.env_config.get("DEFAULT_PAGE_SIZE", 10))
        self.max_page_size = int(self.env_config.get("MAX_PAGE_SIZE", 50))
        
        # 响应字段
        self.success_field = self.env_config.get("SUCCESS_FIELD", "success")
        self.error_code_field = self.env_config.get("ERROR_CODE_FIELD", "errorCode")
        self.error_msg_field = self.env_config.get("ERROR_MSG_FIELD", "errorMsg")
        self.result_field = self.env_config.get("RESULT_FIELD", "result")
        self.list_field = self.env_config.get("LIST_FIELD", "list")
        self.total_field = self.env_config.get("TOTAL_FIELD", "total")
        self.success_code = int(self.env_config.get("SUCCESS_CODE", 1000000))
        
        # 数据字段映射
        self.field_mapping = {
            "position_id": self.env_config.get("FIELD_POSITION_ID", "code"),
            "position_name": self.env_config.get("FIELD_POSITION_NAME", "name"),
            "work_location": self.env_config.get("FIELD_WORK_LOCATION", "workLocation"),
            "position_category": self.env_config.get("FIELD_POSITION_CATEGORY", "job"),
            "update_time_str": self.env_config.get("FIELD_UPDATE_TIME", "updateTime"),
            "update_timestamp": self.env_config.get("FIELD_UPDATE_TIMESTAMP", "updateDate")
        }
        
        # 请求配置
        self.timeout = int(self.env_config.get("REQUEST_TIMEOUT", 30))
        self.max_retries = int(self.env_config.get("MAX_RETRIES", 3))
        self.retry_delay = int(self.env_config.get("ERROR_RETRY_DELAY", 5))
        
        # 状态跟踪
        self.total_positions = 0
        self.current_page = 0
        self.total_pages = 0
        self.last_error = None
        
        logger.info("✅ PDD API爬取器初始化完成")
        logger.info(f"   API端点: {self.api_endpoint}")
        logger.info(f"   认证方式: Cookie认证")
        logger.info(f"   字段映射: {len(self.field_mapping)}个字段")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"配置文件加载失败: {e}")
        return {}
    
    def _load_env_config(self) -> Dict[str, str]:
        """加载环境配置"""
        env_config = {}
        
        # 尝试从.env文件加载
        env_path = "config/.env"
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_config[key.strip()] = value.strip()
            except Exception as e:
                logger.warning(f"环境文件加载失败: {e}")
        
        # 设置默认值
        defaults = {
            "PDD_API_FULL_URL": "https://careers.pddglobalhr.com/api/recruit/position/list",
            "PDD_API_METHOD": "POST",
            "PDD_API_CONTENT_TYPE": "application/json",
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "PAGE_PARAM": "page",
            "SIZE_PARAM": "pageSize",
            "DEFAULT_PAGE_SIZE": "10",
            "MAX_PAGE_SIZE": "50",
            "SUCCESS_FIELD": "success",
            "ERROR_CODE_FIELD": "errorCode",
            "ERROR_MSG_FIELD": "errorMsg",
            "RESULT_FIELD": "result",
            "LIST_FIELD": "list",
            "TOTAL_FIELD": "total",
            "SUCCESS_CODE": "1000000"
        }
        
        for key, value in defaults.items():
            if key not in env_config:
                env_config[key] = value
        
        return env_config
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "User-Agent": self.env_config.get("USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"),
            "Accept": self.env_config.get("ACCEPT", "*/*"),
            "Content-Type": self.content_type,
            "Origin": self.env_config.get("ORIGIN", "https://careers.pddglobalhr.com"),
            "Referer": self.env_config.get("REFERER", "https://careers.pddglobalhr.com/jobs"),
            "Accept-Language": self.env_config.get("ACCEPT_LANGUAGE", "zh-CN,zh;q=0.9,en;q=0.8"),
            "Accept-Encoding": self.env_config.get("ACCEPT_ENCODING", "gzip, deflate, br, zstd"),
            "Cache-Control": self.env_config.get("CACHE_CONTROL", "no-cache"),
            "Pragma": self.env_config.get("PRAGMA", "no-cache")
        }
        
        # 添加Cookie
        if self.cookie_nano_fp:
            headers["Cookie"] = f"_nano_fp={self.cookie_nano_fp}"
        
        return headers
    
    def _build_payload(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """构建请求载荷"""
        payload = {
            "job": "",  # 岗位类别筛选（空表示所有）
            "page": page,
            "pageSize": page_size,
            "name": "",  # 关键词搜索（空表示所有）
            "workLocationList": [],  # 工作地点筛选（空数组表示所有）
            "anti_content": self.anti_content or "需要动态生成"  # 反爬虫参数
        }
        return payload
    
    def _make_request(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """发送API请求"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📡 发送API请求 (尝试 {attempt + 1}/{self.max_retries})...")
                
                if self.api_method.upper() == "POST":
                    response = requests.post(
                        self.api_endpoint,
                        json=payload,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                else:
                    # 理论上应该是POST，但支持GET备用
                    response = requests.get(
                        self.api_endpoint,
                        params=payload,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    error_msg = f"HTTP状态码错误: {response.status_code}"
                    logger.warning(f"   ⚠️ {error_msg}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False, None, error_msg
                
                # 解析响应
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    error_msg = f"JSON解析失败: {e}"
                    logger.warning(f"   ⚠️ {error_msg}")
                    return False, None, error_msg
                
                # 检查API响应状态
                if not data.get(self.success_field, False):
                    error_code = data.get(self.error_code_field, "未知")
                    error_msg = data.get(self.error_msg_field, "API请求失败")
                    error_msg_full = f"API错误: {error_code} - {error_msg}"
                    logger.warning(f"   ⚠️ {error_msg_full}")
                    return False, data, error_msg_full
                
                # 检查成功代码
                if self.error_code_field in data and data[self.error_code_field] != self.success_code:
                    error_code = data.get(self.error_code_field)
                    error_msg = data.get(self.error_msg_field, f"错误代码: {error_code}")
                    error_msg_full = f"API错误代码: {error_code} - {error_msg}"
                    logger.warning(f"   ⚠️ {error_msg_full}")
                    return False, data, error_msg_full
                
                logger.info("   ✅ API请求成功")
                return True, data, None
                
            except requests.exceptions.Timeout:
                error_msg = "请求超时"
                logger.warning(f"   ⚠️ {error_msg}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False, None, error_msg
                
            except requests.exceptions.ConnectionError:
                error_msg = "连接错误"
                logger.warning(f"   ⚠️ {error_msg}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False, None, error_msg
                
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                logger.warning(f"   ⚠️ {error_msg}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False, None, error_msg
        
        return False, None, "所有重试都失败了"
    
    def validate_auth(self) -> bool:
        """验证认证信息"""
        logger.info("🔐 验证认证信息...")
        
        # 检查必要配置
        if not self.cookie_nano_fp:
            logger.warning("   ⚠️ Cookie认证信息缺失 (_nano_fp)")
            return False
        
        # 测试API连接
        payload = self._build_payload(page=1, page_size=1)
        success, data, error = self._make_request(payload)
        
        if success:
            logger.info("   ✅ 认证信息有效")
            return True
        else:
            logger.warning(f"   ⚠️ 认证信息无效: {error}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取API状态"""
        logger.info("📊 获取API状态...")
        
        status = {
            "auth_valid": False,
            "api_accessible": False,
            "total_positions": 0,
            "config_loaded": bool(self.config),
            "env_loaded": bool(self.env_config),
            "last_error": self.last_error
        }
        
        # 验证认证
        status["auth_valid"] = self.validate_auth()
        
        # 测试API访问
        if status["auth_valid"]:
            payload = self._build_payload(page=1, page_size=1)
            success, data, error = self._make_request(payload)
            
            if success:
                status["api_accessible"] = True
                
                # 获取总岗位数
                result = data.get(self.result_field, {})
                total_str = result.get(self.total_field, "0")
                try:
                    status["total_positions"] = int(total_str)
                except:
                    status["total_positions"] = 0
                
                logger.info(f"   ✅ API可访问，总计 {status['total_positions']} 个岗位")
            else:
                status["api_accessible"] = False
                status["last_error"] = error
                logger.warning(f"   ⚠️ API不可访问: {error}")
        
        return status
    
    def fetch_page(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        获取单页数据
        
        Args:
            page: 页码
            page_size: 每页数量
        
        Returns:
            包含数据和状态的字典
        """
        logger.info(f"📄 获取第 {page} 页数据 (每页 {page_size} 条)...")
        
        self.current_page = page
        
        # 构建请求
        payload = self._build_payload(page=page, page_size=page_size)
        
        # 发送请求
        success, data, error = self._make_request(payload)
        
        result_dict = {
            "success": success,
            "page": page,
            "page_size": page_size,
            "error": error,
            "raw_data": data,
            "positions": [],
            "total_count": 0
        }
        
        if not success:
            self.last_error = error
            logger.error(f"   ❌ 第 {page} 页获取失败: {error}")
            return result_dict
        
        # 解析数据
        try:
            result = data.get(self.result_field, {})
            
            # 获取列表数据
            positions_raw = result.get(self.list_field, [])
            
            # 转换数据格式
            positions = []
            for pos in positions_raw:
                position = self._parse_position(pos)
                if position:
                    positions.append(position)
            
            # 获取总数量
            total_str = result.get(self.total_field, "0")
            try:
                total_count = int(total_str)
            except:
                total_count = len(positions_raw)
            
            # 更新结果
            result_dict["positions"] = positions
            result_dict["total_count"] = total_count
            
            logger.info(f"   ✅ 第 {page} 页获取成功: {len(positions)} 个岗位")
            
            # 更新总页数
            if total_count > 0 and page_size > 0:
                self.total_pages = (total_count + page_size - 1) // page_size
                self.total_positions = total_count
                
        except Exception as e:
            error_msg = f"数据解析失败: {str(e)}"
            result_dict["success"] = False
            result_dict["error"] = error_msg
            self.last_error = error_msg
            logger.error(f"   ❌ 数据解析失败: {e}")
        
        return result_dict
    
    def _parse_position(self, raw_position: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析单个岗位数据"""
        try:
            position = {}
            
            # 基础字段
            for field_key, api_field in self.field_mapping.items():
                if api_field in raw_position:
                    position[field_key] = raw_position[api_field]
                else:
                    position[field_key] = None
            
            # 添加详情页URL（需要调查）
            position_id = position.get("position_id")
            if position_id:
                position["detail_url"] = f"https://careers.pddglobalhr.com/jobs/{position_id}"
            else:
                position["detail_url"] = None
            
            # 添加原始数据（用于调试）
            position["raw_data"] = raw_position
            
            # 添加时间戳
            position["crawl_time"] = datetime.now().isoformat()
            
            return position
            
        except Exception as e:
            logger.warning(f"岗位数据解析失败: {e}")
            return None
    
    def fetch_all_pages(self, start_page: int = 1, max_pages: int = 10) -> List[Dict[str, Any]]:
        """获取所有页面数据"""
        logger.info(f"📚 开始获取所有页面数据 (从第 {start_page} 页开始，最多 {max_pages} 页)...")
        
        all_positions = []
        current_page = start_page
        
        # 先获取第一页获取总数量
        first_result = self.fetch_page(page=current_page)
        
        if not first_result["success"]:
            logger.error(f"❌ 第 {current_page} 页获取失败，停止爬取")
            return all_positions
        
        # 添加第一页数据
        all_positions.extend(first_result["positions"])
        
        # 计算总页数
        total_count = first_result["total_count"]
        page_size = first_result["page_size"]
        
        if total_count > 0 and page_size > 0:
            total_pages = (total_count + page_size - 1) // page_size
            actual_max_pages = min(total_pages, max_pages)
            
            logger.info(f"📊 总计 {total_count} 个岗位，共 {total_pages} 页，本次爬取 {actual_max_pages} 页")
            
            # 获取剩余页面
            for page in range(current_page + 1, actual_max_pages + 1):
                logger.info(f"⏳ 获取第 {page}/{actual_max_pages} 页...")
                
                # 请求间隔，避免过快
                time.sleep(1.0)
                
                result = self.fetch_page(page=page, page_size=page_size)
                
                if result["success"]:
                    all_positions.extend(result["positions"])
                    logger.info(f"   ✅ 第 {page} 页完成: {len(result['positions'])} 个岗位")
                else:
                    logger.warning(f"   ⚠️ 第 {page} 页失败: {result['error']}")
                    # 可以继续尝试下一页
        
        logger.info(f"🎉 爬取完成，共获取 {len(all_positions)} 个岗位")
        return all_positions


class PddCrawlerSelector:
    """拼多多爬取器选择器（基于夸克项目框架）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化选择器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 爬取器实例
        self.api_crawler = None
        self.browser_crawler = None  # 阶段1暂不实现
        
        # 状态跟踪
        self.current_mode = "unknown"
        self.positions_extracted = 0
        self.start_time = None
        self.last_error = None
        self.last_error_details = None
        
        # 输出配置
        self.output_dir = self.config.get("output_dir", "output/pdd_optimized")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 日志文件
        log_dir = self.config.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        logger.info("✅ PDD爬取器选择器初始化完成")
        logger.info(f"   输出目录: {self.output_dir}")
    
    def _initialize_api_crawler(self) -> Tuple[bool, Optional[str]]:
        """初始化API爬取器"""
        try:
            self.api_crawler = PddApiCrawler()
            logger.info("✅ API爬取器初始化成功")
            return True, None
        except Exception as e:
            error_msg = f"API爬取器初始化失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def test_api_connection(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """测试API连接"""
        logger.info("🔍 开始API连接诊断...")
        
        if not self.api_crawler:
            init_success, error = self._initialize_api_crawler()
            if not init_success:
                return False, f"API爬取器初始化失败: {error}", {"step": "initialize", "error": error}
        
        try:
            # 验证认证信息
            logger.info("   📋 验证认证信息...")
            auth_valid = self.api_crawler.validate_auth()
            
            if not auth_valid:
                return False, "API认证信息无效", {"step": "auth_validation", "status": "invalid"}
            
            logger.info("     ✅ 认证信息有效")
            
            # 获取状态
            logger.info("   📊 获取API状态...")
            status = self.api_crawler.get_status()
            
            if not status.get("auth_valid", False):
                return False, "API状态显示认证无效", {"step": "status_check", "status": status}
            
            logger.info("     ✅ API状态正常")
            
            # 测试获取第1页数据
            logger.info("   📡 测试获取数据...")
            result = self.api_crawler.fetch_page(page=1, page_size=1)
            
            if not result or not result.get("success"):
                error_details = {
                    "step": "api_fetch",
                    "response": str(result)[:200] if result else "无响应",
                    "status": "api_failed"
                }
                return False, "API数据获取失败", error_details
            
            logger.info("     ✅ API数据获取成功")
            
            # 分析响应数据
            positions = result.get("positions", [])
            total_count = result.get("total_count", 0)
            
            if total_count <= 0:
                return False, f"API返回岗位数为0", {"step": "data_analysis", "total_count": total_count}
            
            logger.info(f"     📊 总计 {total_count} 个岗位")
            logger.info(f"     📄 第1页获取 {len(positions)} 个岗位")
            
            # 检查数据字段
            if positions:
                position = positions[0]
                field_count = len([v for v in position.values() if v is not None])
                logger.info(f"     📋 数据字段: {field_count} 个有效字段")
            
            return True, "API连接测试通过", {
                "step": "complete",
                "total_positions": total_count,
                "sample_data": positions[0] if positions else None,
                "status": "success"
            }
            
        except Exception as e:
            error_details = {
                "step": "test_exception",
                "exception": str(e),
                "traceback": str(sys.exc_info())
            }
            return False, f"API测试异常: {e}", error_details
    
    def run_api_crawler(self, max_pages: int = 10) -> Tuple[bool, List[Dict[str, Any]], Optional[str]]:
        """运行API爬取器"""
        logger.info(f"🚀 开始运行API爬取器 (最多 {max_pages} 页)...")
        
        self.start_time = time.time()
        self.current_mode = "api"
        
        # 初始化API爬取器
        init_success, error = self._initialize_api_crawler()
        if not init_success:
            return False, [], f"API爬取器初始化失败: {error}"
        
        try:
            # 获取所有页面数据
            positions = self.api_crawler.fetch_all_pages(start_page=1, max_pages=max_pages)
            
            self.positions_extracted = len(positions)
            
            # 计算运行时间
            elapsed_time = time.time() - self.start_time
            
            if positions:
                logger.info(f"🎉 API爬取完成!")
                logger.info(f"   📊 获取岗位数: {len(positions)}")
                logger.info(f"   ⏱️  运行时间: {elapsed_time:.2f}秒")
                logger.info(f"   📈 平均速度: {len(positions)/elapsed_time:.2f} 岗位/秒")
                
                return True, positions, None
            else:
                logger.warning("⚠️  API爬取完成，但未获取到任何岗位")
                return False, [], "未获取到任何岗位数据"
                
        except Exception as e:
            error_msg = f"API爬取器运行异常: {e}"
            logger.error(error_msg)
            return False, [], error_msg
    
    def save_positions(self, positions: List[Dict[str, Any]], format: str = "excel") -> Tuple[bool, str]:
        """保存岗位数据 - 使用夸克项目导出系统"""
        logger.info(f"💾 保存岗位数据 ({format}格式) - 使用夸克项目导出系统...")
        
        try:
            # 导入PDD数据导出器
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))
            from pdd_data_exporter import PddDataExporter
            
            # 创建导出器
            exporter = PddDataExporter()
            
            # 导出数据
            export_result = exporter.export_positions(positions, format=format)
            
            if export_result.get("success"):
                filepath = export_result.get("filepath", "")
                logger.info(f"   ✅ 数据已保存: {filepath}")
                
                # 生成导出报告
                exporter.generate_export_report(export_result)
                
                return True, filepath
            else:
                error_msg = export_result.get("error", "导出失败")
                logger.error(f"   ❌ 数据保存失败: {error_msg}")
                
                # 如果夸克框架失败，尝试简单JSON保存
                logger.info("   🔄 尝试简单JSON保存...")
                return self._save_simple_json(positions)
                
        except ImportError as e:
            logger.warning(f"   ⚠️ PDD数据导出器导入失败: {e}")
            logger.info("   🔄 使用简单JSON保存...")
            return self._save_simple_json(positions)
            
        except Exception as e:
            error_msg = f"数据保存失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _save_simple_json(self, positions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """简单JSON保存（备用方案）"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)
            
            logger.info(f"   ✅ 简单JSON数据已保存: {filepath}")
            return True, filepath
            
        except Exception as e:
            error_msg = f"简单JSON保存失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def run_optimized(self, max_pages: int = 10) -> Dict[str, Any]:
        """运行优化爬取（阶段1：只使用API）"""
        logger.info("🎯 开始优化爬取（阶段1：基础API爬取）...")
        
        result = {
            "success": False,
            "mode": "api",
            "positions_count": 0,
            "error": None,
            "output_file": None,
            "execution_time": 0,
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # 1. 测试API连接
            logger.info("🔍 步骤1: 测试API连接...")
            api_success, api_message, api_details = self.test_api_connection()
            
            if not api_success:
                result["error"] = f"API连接测试失败: {api_message}"
                result["details"]["api_test"] = api_details
                logger.error(f"   ❌ {api_message}")
                
                # 阶段1只使用API，所以失败就结束
                elapsed_time = time.time() - start_time
                result["execution_time"] = elapsed_time
                return result
            
            logger.info("   ✅ API连接测试通过")
            
            # 2. 运行API爬取器
            logger.info("🚀 步骤2: 运行API爬取器...")
            crawl_success, positions, crawl_error = self.run_api_crawler(max_pages=max_pages)
            
            if not crawl_success:
                result["error"] = f"API爬取失败: {crawl_error}"
                logger.error(f"   ❌ {crawl_error}")
                
                elapsed_time = time.time() - start_time
                result["execution_time"] = elapsed_time
                return result
            
            result["positions_count"] = len(positions)
            logger.info(f"   ✅ API爬取成功: {len(positions)} 个岗位")
            
            # 3. 保存数据（使用夸克项目导出系统）
            logger.info("💾 步骤3: 保存数据（使用夸克项目导出系统）...")
            save_success, output_file = self.save_positions(positions, format="excel")
            
            if not save_success:
                result["error"] = f"数据保存失败: {output_file}"
                logger.error(f"   ❌ 数据保存失败")
                
                # 尝试JSON保存作为备用
                logger.info("   🔄 尝试JSON保存作为备用...")
                save_success_json, output_file_json = self.save_positions(positions, format="json")
                if save_success_json:
                    result["output_file"] = output_file_json
                    result["fallback_format"] = "json"
                    logger.info(f"   ✅ JSON数据已保存: {output_file_json}")
            else:
                result["output_file"] = output_file
                result["export_format"] = "excel"
                logger.info(f"   ✅ Excel数据已保存: {output_file}")
            
            # 4. 记录结果
            elapsed_time = time.time() - start_time
            result["execution_time"] = elapsed_time
            
            if positions:
                result["success"] = True
                logger.info(f"🎉 优化爬取完成!")
                logger.info(f"   📊 结果: {len(positions)} 个岗位")
                logger.info(f"   ⏱️  时间: {elapsed_time:.2f}秒")
                logger.info(f"   📁 文件: {output_file}")
            else:
                result["success"] = False
                result["error"] = "未获取到任何岗位数据"
                logger.warning("⚠️  优化爬取完成，但未获取到数据")
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"优化爬取异常: {e}"
            result["error"] = error_msg
            result["execution_time"] = elapsed_time
            logger.error(f"❌ {error_msg}")
            return result


def main():
    """主函数"""
    print("=" * 60)
    print("拼多多招聘爬取器 - 阶段1: 基础API爬取")
    print("=" * 60)
    
    # 创建选择器
    config = {
        "output_dir": "output/pdd_stage1",
        "log_dir": "logs"
    }
    
    selector = PddCrawlerSelector(config)
    
    # 运行优化爬取
    print("\n🚀 开始执行阶段1爬取...")
    result = selector.run_optimized(max_pages=5)  # 先测试5页
    
    print("\n" + "=" * 60)
    print("执行结果:")
    print("=" * 60)
    
    if result["success"]:
        print(f"✅ 成功: {result['positions_count']} 个岗位")
        print(f"📁 文件: {result['output_file']}")
        print(f"⏱️  时间: {result['execution_time']:.2f}秒")
        print(f"🎯 模式: {result['mode']}")
    else:
        print(f"❌ 失败: {result['error']}")
        print(f"⏱️  时间: {result['execution_time']:.2f}秒")
    
    # 显示详细信息
    if "details" in result and result["details"]:
        print("\n📋 详细信息:")
        for key, value in result["details"].items():
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    
    return result["success"]


if __name__ == "__main__":
    # 添加项目根目录到Python路径
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    # 确保utils目录在路径中
    utils_dir = os.path.join(project_root, "src", "utils")
    sys.path.insert(0, utils_dir)
    
    success = main()
    sys.exit(0 if success else 1)