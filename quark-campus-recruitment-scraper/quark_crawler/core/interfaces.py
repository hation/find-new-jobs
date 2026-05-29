#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 核心接口定义
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于记忆系统原则: 契约优先设计

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class StrategyType(Enum):
    """策略类型枚举"""
    CLICK_BASED = "click_based"      # 点击方案 (现有)
    DIRECT_URL = "direct_url"        # 直接URL方案 (优化)
    HYBRID = "hybrid"                # 混合方案
    PARALLEL = "parallel"            # 并行方案


class ExtractionPhase(Enum):
    """提取阶段枚举"""
    LIST_EXTRACTION = "list_extraction"      # 列表页提取
    DETAIL_EXTRACTION = "detail_extraction"  # 详情页提取
    DATA_VALIDATION = "data_validation"      # 数据验证
    DATA_SAVING = "data_saving"              # 数据保存


@dataclass
class PositionData:
    """岗位数据模型 (12个字段)"""
    position_id: str                     # 岗位ID
    position_name: str                   # 岗位名称
    work_location: str                   # 工作地点
    position_category: str               # 岗位类别
    publish_time: str                    # 发布时间
    detail_link: str                     # 详情链接
    
    # 详情页字段
    department: str                      # 部门信息
    education_requirement: str           # 学历要求
    work_experience: str                 # 工作经验
    job_responsibilities: str            # 工作职责
    job_requirements: str                # 任职要求
    other_info: str                      # 其他信息
    
    # 元数据
    page_number: int                     # 所在页码
    position_index: int                  # 页面内序号
    extraction_time: str                 # 提取时间
    source_url: str                      # 来源URL
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "position_id": self.position_id,
            "position_name": self.position_name,
            "work_location": self.work_location,
            "position_category": self.position_category,
            "publish_time": self.publish_time,
            "detail_link": self.detail_link,
            "department": self.department,
            "education_requirement": self.education_requirement,
            "work_experience": self.work_experience,
            "job_responsibilities": self.job_responsibilities,
            "job_requirements": self.job_requirements,
            "other_info": self.other_info,
            "page_number": self.page_number,
            "position_index": self.position_index,
            "extraction_time": self.extraction_time,
            "source_url": self.source_url,
            "field_count": 12  # 核心字段数量
        }
    
    def validate(self) -> List[str]:
        """验证数据完整性，返回缺失字段列表"""
        missing_fields = []
        
        # 核心12个字段验证
        core_fields = [
            ("position_id", self.position_id),
            ("position_name", self.position_name),
            ("work_location", self.work_location),
            ("position_category", self.position_category),
            ("publish_time", self.publish_time),
            ("detail_link", self.detail_link),
            ("department", self.department),
            ("education_requirement", self.education_requirement),
            ("work_experience", self.work_experience),
            ("job_responsibilities", self.job_responsibilities),
            ("job_requirements", self.job_requirements),
            ("other_info", self.other_info)
        ]
        
        for field_name, field_value in core_fields:
            if not field_value or str(field_value).strip() == "":
                missing_fields.append(field_name)
        
        return missing_fields


@dataclass
class PageState:
    """页面状态模型"""
    page_number: int                     # 当前页码
    total_pages: int                     # 总页数
    positions_per_page: int              # 每页岗位数
    total_positions: int                 # 总岗位数
    filter_categories: List[str]         # 筛选类别列表
    url: str                             # 当前页面URL
    timestamp: str                       # 状态时间戳
    
    def validate_filter_state(self, expected_categories: List[str] = None) -> bool:
        """验证筛选状态"""
        if expected_categories is None:
            expected_categories = [
                "产品类", "运营类", "数据类", 
                "市场拓展", "销售类", "游戏类", "金融类"
            ]
        
        # 验证筛选类别数量
        if len(self.filter_categories) != len(expected_categories):
            return False
        
        # 验证具体类别
        for category in expected_categories:
            if category not in self.filter_categories:
                return False
        
        return True
    
    def get_display_info(self) -> Dict[str, Any]:
        """获取显示信息"""
        return {
            "current_page": f"{self.page_number}/{self.total_pages}",
            "total_positions": self.total_positions,
            "filter_categories": self.filter_categories,
            "filter_count": len(self.filter_categories),
            "expected_filters": 7
        }


@dataclass  
class ExecutionContext:
    """执行上下文"""
    strategy_type: StrategyType          # 使用的策略类型
    browser_profile: str                 # 浏览器配置
    current_page: int                    # 当前页码
    current_position_index: int          # 当前岗位索引
    retry_count: int                     # 重试次数
    timeout_ms: int                      # 超时时间(毫秒)
    
    # 状态跟踪
    positions_completed: int             # 已完成岗位数
    positions_failed: int                # 失败岗位数
    start_time: str                      # 开始时间
    last_update_time: str                # 最后更新时间
    
    def increment_retry(self) -> None:
        """增加重试计数"""
        self.retry_count += 1
    
    def reset_retry(self) -> None:
        """重置重试计数"""
        self.retry_count = 0
    
    def should_retry(self, max_retries: int = 3) -> bool:
        """检查是否应该重试"""
        return self.retry_count < max_retries


class IExtractionStrategy(ABC):
    """提取策略接口 - 所有插件必须实现"""
    
    @abstractmethod
    def get_strategy_type(self) -> StrategyType:
        """获取策略类型"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        pass
    
    @abstractmethod
    def initialize(self, context: ExecutionContext) -> bool:
        """初始化策略"""
        pass
    
    @abstractmethod
    def validate_environment(self) -> List[str]:
        """验证环境，返回问题列表"""
        pass
    
    @abstractmethod
    def extract_list_page(self, page_number: int) -> List[str]:
        """提取列表页，返回position_id列表"""
        pass
    
    @abstractmethod
    def extract_position_detail(self, position_id: str, page_number: int, position_index: int) -> PositionData:
        """提取岗位详情"""
        pass
    
    @abstractmethod
    def validate_page_state(self, expected_categories: List[str]) -> bool:
        """验证页面状态"""
        pass
    
    @abstractmethod
    def save_position_data(self, data: PositionData, output_dir: str) -> str:
        """保存岗位数据，返回文件路径"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理资源"""
        pass
    
    # 可选方法 - 提供默认实现
    def batch_extract_positions(self, position_ids: List[str], page_number: int) -> List[PositionData]:
        """批量提取岗位数据 (默认串行实现)"""
        results = []
        for i, position_id in enumerate(position_ids):
            try:
                data = self.extract_position_detail(position_id, page_number, i + 1)
                results.append(data)
            except Exception as e:
                print(f"❌ 提取失败 {position_id}: {e}")
                continue
        return results


class IBrowserManager(ABC):
    """浏览器管理器接口"""
    
    @abstractmethod
    def initialize(self, profile: str = "openclaw") -> bool:
        """初始化浏览器"""
        pass
    
    @abstractmethod
    def navigate(self, url: str, timeout_ms: int = 30000) -> bool:
        """导航到URL"""
        pass
    
    @abstractmethod
    def execute_script(self, javascript: str) -> Any:
        """执行JavaScript"""
        pass
    
    @abstractmethod
    def take_snapshot(self, refs: str = "aria") -> Dict[str, Any]:
        """获取页面快照"""
        pass
    
    @abstractmethod
    def click_element(self, ref: str, timeout_ms: int = 10000) -> bool:
        """点击元素"""
        pass
    
    @abstractmethod
    def switch_to_tab(self, tab_id: str) -> bool:
        """切换到指定标签页"""
        pass
    
    @abstractmethod
    def close_tab(self, tab_id: str) -> bool:
        """关闭标签页"""
        pass
    
    @abstractmethod
    def get_current_url(self) -> str:
        """获取当前URL"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """清理浏览器资源"""
        pass


class IDataManager(ABC):
    """数据管理器接口"""
    
    @abstractmethod
    def initialize(self, output_dir: str) -> bool:
        """初始化数据管理器"""
        pass
    
    @abstractmethod
    def save_position(self, data: PositionData) -> str:
        """保存单个岗位数据"""
        pass
    
    @abstractmethod
    def save_page_data(self, page_number: int, positions: List[PositionData]) -> str:
        """保存页面数据"""
        pass
    
    @abstractmethod
    def save_full_data(self, all_positions: List[PositionData]) -> str:
        """保存完整数据"""
        pass
    
    @abstractmethod
    def generate_report(self, positions: List[PositionData]) -> str:
        """生成报告"""
        pass
    
    @abstractmethod
    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        pass
    
    @abstractmethod
    def backup_data(self, backup_dir: str) -> bool:
        """备份数据"""
        pass


class IPluginRegistry(ABC):
    """插件注册接口"""
    
    @abstractmethod
    def register_strategy(self, strategy: IExtractionStrategy) -> bool:
        """注册策略插件"""
        pass
    
    @abstractmethod
    def get_strategy(self, strategy_type: StrategyType) -> Optional[IExtractionStrategy]:
        """获取策略插件"""
        pass
    
    @abstractmethod
    def list_strategies(self) -> List[Dict[str, Any]]:
        """列出所有可用策略"""
        pass
    
    @abstractmethod
    def validate_plugins(self) -> Dict[str, List[str]]:
        """验证所有插件"""
        pass


class IConfigurationManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def load_config(self, config_path: str) -> bool:
        """加载配置"""
        pass
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def update_config(self, key: str, value: Any) -> bool:
        """更新配置"""
        pass
    
    @abstractmethod
    def save_config(self, config_path: str) -> bool:
        """保存配置"""
        pass
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """验证配置完整性"""
        pass


# 错误和异常定义
class QuarkCrawlerError(Exception):
    """夸克爬取器基础异常"""
    pass


class StrategyError(QuarkCrawlerError):
    """策略相关异常"""
    pass


class BrowserError(QuarkCrawlerError):
    """浏览器相关异常"""
    pass


class DataError(QuarkCrawlerError):
    """数据相关异常"""
    pass


class ConfigurationError(QuarkCrawlerError):
    """配置相关异常"""
    pass


class PluginError(QuarkCrawlerError):
    """插件相关异常"""
    pass


# 工具函数
def create_position_data_from_dict(data_dict: Dict[str, Any]) -> PositionData:
    """从字典创建PositionData对象"""
    return PositionData(
        position_id=data_dict.get("position_id", ""),
        position_name=data_dict.get("position_name", ""),
        work_location=data_dict.get("work_location", ""),
        position_category=data_dict.get("position_category", ""),
        publish_time=data_dict.get("publish_time", ""),
        detail_link=data_dict.get("detail_link", ""),
        department=data_dict.get("department", ""),
        education_requirement=data_dict.get("education_requirement", ""),
        work_experience=data_dict.get("work_experience", ""),
        job_responsibilities=data_dict.get("job_responsibilities", ""),
        job_requirements=data_dict.get("job_requirements", ""),
        other_info=data_dict.get("other_info", ""),
        page_number=data_dict.get("page_number", 0),
        position_index=data_dict.get("position_index", 0),
        extraction_time=data_dict.get("extraction_time", ""),
        source_url=data_dict.get("source_url", "")
    )


def validate_required_fields(data_dict: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """验证必需字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data_dict or not data_dict[field]:
            missing_fields.append(field)
    return missing_fields