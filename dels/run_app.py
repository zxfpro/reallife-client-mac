#!/usr/bin/env python3
"""
启动脚本 - 运行 Streamlit 应用
"""

import subprocess
import sys
import os

def check_dependencies():
    """检查依赖项"""
    required_packages = ['streamlit', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖项: {', '.join(missing_packages)}")
        print("请运行: uv add streamlit requests")
        return False
    
    print("✅ 所有依赖项已安装")
    return True

def main():
    """主函数"""
    print("🚀 启动 Reallife Client Streamlit 应用")
    
    # 检查依赖项
    if not check_dependencies():
        sys.exit(1)
    
    # 设置默认环境变量（如果未设置）
    os.environ.setdefault('REALLIFE_BASE_URL', 'http://localhost:8020')
    os.environ.setdefault('REALLIFE_TIMEOUT', '30')
    os.environ.setdefault('REALLIFE_MAX_RETRIES', '3')
    
    print("📋 配置信息:")
    print(f"  - 服务地址: {os.environ.get('REALLIFE_BASE_URL')}")
    print(f"  - 超时时间: {os.environ.get('REALLIFE_TIMEOUT')}s")
    print(f"  - 最大重试: {os.environ.get('REALLIFE_MAX_RETRIES')}")
    
    # 启动 Streamlit 应用
    try:
        print("\n🌐 启动 Streamlit 应用...")
        print("应用将在浏览器中自动打开: http://localhost:8501")
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'streamlit_app.py',
            '--server.headless', 'false',
            '--server.runOnSave', 'true'
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()