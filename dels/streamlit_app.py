"""
Reallife Client Streamlit 前端界面
提供一个直观的 Web 界面来管理任务和看板系统
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from main_improved import ReallifeClient, ClientConfig


# 页面配置
st.set_page_config(
    page_title="Reallife Client 管理界面",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 样式
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_client() -> ReallifeClient:
    """获取客户端实例（缓存）"""
    config = ClientConfig.from_env()
    return ReallifeClient(config)


def display_status(status_data: Dict[str, Any]) -> None:
    """显示状态信息"""
    st.header("📊 系统状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="服务地址",
            value=status_data["config"]["base_url"],
            help="FastAPI 服务的基础 URL"
        )
    
    with col2:
        st.metric(
            label="连接超时",
            value=f"{status_data['config']['timeout']}s",
            help="API 请求超时时间"
        )
    
    with col3:
        kanban_status = "✅ 可用" if status_data["config"]["kanban_available"] else "❌ 不可用"
        st.metric(
            label="看板状态",
            value=kanban_status,
            help="看板管理器是否正常初始化"
        )
    
    with col4:
        task_count = len(status_data.get("current_task", {}).get("message", "")) if status_data.get("current_task") else 0
        st.metric(
            label="当前任务",
            value="有任务" if task_count > 0 else "无任务",
            help="当前是否有待处理的任务"
        )


def display_current_task(client: ReallifeClient) -> None:
    """显示当前任务"""
    st.header("📝 当前任务")
    
    with st.spinner("正在获取当前任务..."):
        current_task = client.receive()
    
    if current_task:
        st.markdown(f"""
        <div class="info-message">
            <strong>任务内容:</strong> {current_task}
        </div>
        """, unsafe_allow_html=True)
        
        # 分析任务类型
        if "待办" in current_task:
            st.info("🔄 这是一个待办任务，可以开始处理")
        elif "进行中" in current_task:
            st.warning("⚡ 这是一个正在进行的任务，可以关闭")
        else:
            st.info("📄 任务状态未明确")
    else:
        st.markdown("""
        <div class="success-message">
            ✅ 当前没有待处理的任务
        </div>
        """, unsafe_allow_html=True)


def task_operations(client: ReallifeClient) -> None:
    """任务操作界面"""
    st.header("🚀 任务操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 开始处理任务", use_container_width=True, type="primary"):
            with st.spinner("正在处理任务..."):
                success = client.start()
            
            if success:
                st.markdown("""
                <div class="success-message">
                    ✅ 任务处理成功！
                </div>
                """, unsafe_allow_html=True)
                st.rerun()  # 刷新页面
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ 任务处理失败，请检查日志
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🛑 关闭当前任务", use_container_width=True):
            with st.spinner("正在关闭任务..."):
                success = client.close_task()
            
            if success:
                st.markdown("""
                <div class="success-message">
                    ✅ 任务关闭成功！
                </div>
                """, unsafe_allow_html=True)
                st.rerun()  # 刷新页面
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ 任务关闭失败，请检查日志
                </div>
                """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📋 同步看板", use_container_width=True):
            with st.spinner("正在同步看板..."):
                success = client.kanban()
            
            if success:
                st.markdown("""
                <div class="success-message">
                    ✅ 看板同步成功！
                </div>
                """, unsafe_allow_html=True)
                st.rerun()  # 刷新页面
            else:
                st.markdown("""
                <div class="error-message">
                    ❌ 看板同步失败，请检查看板路径和权限
                </div>
                """, unsafe_allow_html=True)


def configuration_panel() -> None:
    """配置面板"""
    st.sidebar.header("⚙️ 配置")
    
    # 当前配置显示
    client = get_client()
    config = client.config
    
    st.sidebar.subheader("当前配置")
    st.sidebar.text(f"服务地址: {config.base_url}")
    st.sidebar.text(f"超时时间: {config.timeout}s")
    st.sidebar.text(f"最大重试: {config.max_retries}")
    
    # 配置修改
    st.sidebar.subheader("修改配置")
    
    new_base_url = st.sidebar.text_input(
        "服务地址",
        value=config.base_url,
        help="FastAPI 服务的基础 URL"
    )
    
    new_timeout = st.sidebar.number_input(
        "超时时间(秒)",
        min_value=1,
        max_value=300,
        value=config.timeout,
        help="API 请求超时时间"
    )
    
    new_max_retries = st.sidebar.number_input(
        "最大重试次数",
        min_value=0,
        max_value=10,
        value=config.max_retries,
        help="API 请求失败时的最大重试次数"
    )
    
    if st.sidebar.button("💾 应用配置"):
        # 创建新配置
        new_config = ClientConfig(
            base_url=new_base_url,
            timeout=new_timeout,
            max_retries=new_max_retries,
            kanban_path=config.kanban_path,
            pathlibs=config.pathlibs
        )
        
        # 清除缓存并重新创建客户端
        st.cache_resource.clear()
        st.session_state.client = ReallifeClient(new_config)
        
        st.sidebar.success("✅ 配置已更新！")
        st.rerun()


def auto_refresh_toggle() -> None:
    """自动刷新开关"""
    st.sidebar.subheader("🔄 自动刷新")
    
    auto_refresh = st.sidebar.checkbox(
        "启用自动刷新",
        value=st.session_state.get("auto_refresh", False),
        help="每30秒自动刷新任务状态"
    )
    
    st.session_state.auto_refresh = auto_refresh
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider(
            "刷新间隔(秒)",
            min_value=10,
            max_value=300,
            value=30,
            step=10
        )
        
        # 自动刷新逻辑
        if "last_refresh" not in st.session_state:
            st.session_state.last_refresh = time.time()
        
        current_time = time.time()
        if current_time - st.session_state.last_refresh > refresh_interval:
            st.session_state.last_refresh = current_time
            st.rerun()


def logs_panel() -> None:
    """日志面板"""
    with st.expander("📜 操作日志", expanded=False):
        if "operation_logs" not in st.session_state:
            st.session_state.operation_logs = []
        
        # 显示最近的操作日志
        if st.session_state.operation_logs:
            for log in reversed(st.session_state.operation_logs[-10:]):  # 显示最近10条
                st.text(log)
        else:
            st.text("暂无操作日志")
        
        if st.button("清空日志"):
            st.session_state.operation_logs = []
            st.rerun()


def add_log(message: str) -> None:
    """添加操作日志"""
    if "operation_logs" not in st.session_state:
        st.session_state.operation_logs = []
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    st.session_state.operation_logs.append(log_entry)


def main():
    """主函数"""
    st.title("📋 Reallife Client 管理界面")
    st.markdown("---")
    
    # 侧边栏配置
    configuration_panel()
    auto_refresh_toggle()
    
    # 获取客户端实例
    try:
        client = get_client()
        
        # 获取状态信息
        with st.spinner("正在加载系统状态..."):
            status = client.get_status()
        
        # 显示状态
        display_status(status)
        st.markdown("---")
        
        # 显示当前任务
        display_current_task(client)
        st.markdown("---")
        
        # 任务操作
        task_operations(client)
        st.markdown("---")
        
        # 日志面板
        logs_panel()
        
        # 页脚信息
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 系统信息")
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.text(f"更新时间: {current_time}")
        st.sidebar.text(f"看板路径: {client.config.kanban_path}")
        
        # 自动刷新状态显示
        if st.session_state.get("auto_refresh", False):
            st.sidebar.success("🔄 自动刷新已启用")
        else:
            st.sidebar.info("⏸️ 自动刷新已禁用")
    
    except Exception as e:
        st.error(f"❌ 初始化客户端时发生错误: {str(e)}")
        st.info("请检查配置和依赖项是否正确安装")


if __name__ == "__main__":
    main()