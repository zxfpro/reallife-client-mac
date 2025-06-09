"""
Reallife Client - 改进版本
一个用于管理任务和看板系统的客户端应用
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from appscriptz.scripts.applescript import Display
from kanbanz.manager import KanBanManager, Pool


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """客户端配置类"""
    base_url: str = "http://localhost:8020"
    timeout: int = 30
    max_retries: int = 3
    kanban_path: str = "/Users/zhaoxuefeng/GitHub/obsidian/工作/事件看板/事件看板.md"
    pathlibs: List[str] = None
    
    def __post_init__(self):
        if self.pathlibs is None:
            self.pathlibs = [
                "/工程系统级设计/项目级别/数字人生/模拟资质认证/模拟资质认证.canvas",
                "/工程系统级设计/项目级别/数字人生/DigitalLife/DigitalLife.canvas",
                "/工程系统级设计/项目级别/自动化工作/coder/coder.canvas",
            ]
    
    @classmethod
    def from_env(cls) -> 'ClientConfig':
        """从环境变量创建配置"""
        return cls(
            base_url=os.getenv('REALLIFE_BASE_URL', cls.base_url),
            timeout=int(os.getenv('REALLIFE_TIMEOUT', cls.timeout)),
            max_retries=int(os.getenv('REALLIFE_MAX_RETRIES', cls.max_retries)),
            kanban_path=os.getenv('REALLIFE_KANBAN_PATH', cls.kanban_path),
        )


class APIClient:
    """API 客户端类，负责与后端服务的通信"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """创建配置好的 requests 会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认头部
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ReallifeClient/1.0"
        })
        
        return session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """统一的请求处理方法"""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            logger.info(f"{method.upper()} {endpoint} - Status: {response.status_code}")
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"请求 {endpoint} 超时")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"连接 {endpoint} 失败")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 错误 {endpoint}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求 {endpoint} 失败: {e}")
            return None
        except ValueError as e:
            logger.error(f"解析 {endpoint} 响应 JSON 失败: {e}")
            return None
    
    def update_tasks(self, tasks: List[Any]) -> bool:
        """
        更新任务列表
        
        Args:
            tasks: 任务列表
            
        Returns:
            bool: 更新是否成功
        """
        if not tasks:
            logger.warning("任务列表为空，跳过更新")
            return False
            
        tasks_data = {"tasks": tasks}
        result = self._make_request("POST", "/update_tasks", json=tasks_data)
        
        if result:
            logger.info("任务更新成功")
            return True
        else:
            logger.error("任务更新失败")
            return False
    
    def receive_task(self) -> Optional[Dict[str, Any]]:
        """
        接收当前任务
        
        Returns:
            Optional[Dict[str, Any]]: 任务数据或 None
        """
        result = self._make_request("GET", "/receive")
        if result:
            logger.info("成功接收任务")
        else:
            logger.warning("接收任务失败")
        return result
    
    def complete_task(self) -> bool:
        """
        完成当前任务
        
        Returns:
            bool: 完成是否成功
        """
        result = self._make_request("GET", "/complete")
        if result:
            logger.info("任务完成成功")
            return True
        else:
            logger.error("任务完成失败")
            return False
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            logger.info("API 客户端会话已关闭")


class TaskProcessor:
    """任务处理器类"""
    
    @staticmethod
    def process_task(task: str) -> None:
        """
        处理任务
        
        Args:
            task: 任务内容
        """
        logger.info(f"处理任务: {task}")
        # 这里可以添加具体的任务处理逻辑
        print(f"正在处理任务: {task}")


class ReallifeClient:
    """
    Reallife 客户端主类
    负责协调看板管理和任务处理
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        初始化客户端
        
        Args:
            config: 客户端配置，如果为 None 则从环境变量加载
        """
        self.config = config or ClientConfig.from_env()
        self.api_client = APIClient(self.config)
        self.task_processor = TaskProcessor()
        
        # 初始化看板管理器
        try:
            if os.path.exists(self.config.kanban_path):
                self.manager = KanBanManager(self.config.kanban_path, self.config.pathlibs)
                logger.info("看板管理器初始化成功")
            else:
                logger.warning(f"看板文件不存在: {self.config.kanban_path}")
                self.manager = None
        except Exception as e:
            logger.error(f"看板管理器初始化失败: {e}")
            self.manager = None
    
    def kanban(self) -> bool:
        """
        执行看板同步操作
        
        Returns:
            bool: 操作是否成功
        """
        if not self.manager:
            logger.error("看板管理器未初始化，无法执行看板操作")
            return False
            
        try:
            logger.info("开始看板同步操作")
            
            # 同步操作
            self.manager.sync_ready()
            self.manager.sync_order()
            
            # 显示调整对话框
            Display.display_dialog('调整', '调整时间和顺序')
            
            self.manager.sync_run()
            
            # 获取执行池中的任务
            tasks = self.manager.kanban.get_tasks_in(Pool.执行池)
            
            # 更新任务
            if tasks:
                success = self.api_client.update_tasks(tasks)
                if success:
                    logger.info("看板操作完成")
                    return True
                else:
                    logger.error("任务更新失败")
                    return False
            else:
                logger.warning("执行池中没有任务")
                return True
                
        except Exception as e:
            logger.error(f"看板操作失败: {e}")
            return False
    
    def receive(self) -> Optional[str]:
        """
        接收任务
        
        Returns:
            Optional[str]: 任务内容或 None
        """
        try:
            task_data = self.api_client.receive_task()
            if task_data and isinstance(task_data, dict):
                task = task_data.get("message")
                if task:
                    logger.info(f"接收到任务: {task}")
                    return task
                else:
                    logger.info("没有待处理的任务")
                    return None
            else:
                logger.warning("接收任务失败")
                return None
        except Exception as e:
            logger.error(f"接收任务时发生错误: {e}")
            return None
    
    def start(self) -> bool:
        """
        开始处理任务
        
        Returns:
            bool: 处理是否成功
        """
        try:
            task = self.receive()
            if task and "待办" in task:
                logger.info(f"开始处理待办任务: {task}")
                self.task_processor.process_task(task)
                success = self.api_client.complete_task()
                if success:
                    logger.info("任务处理完成")
                    return True
                else:
                    logger.error("任务完成标记失败")
                    return False
            else:
                logger.info("没有待办任务需要处理")
                return True
        except Exception as e:
            logger.error(f"处理任务时发生错误: {e}")
            return False
    
    def close_task(self) -> bool:
        """
        关闭正在进行的任务
        
        Returns:
            bool: 关闭是否成功
        """
        try:
            task = self.receive()
            if task and "进行中" in task:
                logger.info(f"关闭进行中任务: {task}")
                success = self.api_client.complete_task()
                if success:
                    logger.info("任务关闭成功")
                    return True
                else:
                    logger.error("任务关闭失败")
                    return False
            else:
                logger.info("没有进行中的任务需要关闭")
                return True
        except Exception as e:
            logger.error(f"关闭任务时发生错误: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取客户端状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "kanban_path": self.config.kanban_path,
                "kanban_available": self.manager is not None
            },
            "current_task": self.receive()
        }
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.api_client.close()
        except:
            pass


# 为了向后兼容，保留原始函数接口
def update_task(tasks: list) -> bool:
    """向后兼容的任务更新函数"""
    client = ReallifeClient()
    return client.api_client.update_tasks(tasks)


def receive_task() -> Optional[Dict[str, Any]]:
    """向后兼容的任务接收函数"""
    client = ReallifeClient()
    return client.api_client.receive_task()


def complete_task() -> bool:
    """向后兼容的任务完成函数"""
    client = ReallifeClient()
    return client.api_client.complete_task()


def deal_task(task: str) -> None:
    """向后兼容的任务处理函数"""
    TaskProcessor.process_task(task)


if __name__ == "__main__":
    # 示例用法
    client = ReallifeClient()
    
    # 获取状态
    status = client.get_status()
    print("客户端状态:", status)
    
    # 根据需要执行操作
    # client.kanban()      # 看板同步
    # client.start()       # 开始处理任务
    # client.close_task()  # 关闭任务