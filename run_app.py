import os
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    # 动态获取打包后的绝对路径
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    script_path = os.path.join(base_dir, "audit_app.py")
    
    # 模拟命令行输入，强制关闭开发者模式，固定端口
    sys.argv = [
        "streamlit", "run", script_path, 
        "--global.developmentMode=false", 
        "--server.port=8501", 
        "--browser.gatherUsageStats=false"
    ]
    sys.exit(stcli.main())