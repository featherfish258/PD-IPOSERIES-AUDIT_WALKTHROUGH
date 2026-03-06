import os
import streamlit
import PyInstaller.__main__

streamlit_path = os.path.dirname(streamlit.__file__)

# 核心魔法：自动获取当前操作系统的路径分隔符
sep = os.pathsep 

print(f"✅ 成功找到 Streamlit 网页前端文件路径: {streamlit_path}")
print(f"🚀 正在使用系统分隔符 '{sep}' 进行跨平台打包...")

PyInstaller.__main__.run([
    'run_app.py',
    '--name=Audit_WalkThrough_System',
    '--onedir',
    '--noconfirm',
    '--clean',  
    f'--add-data={streamlit_path}{sep}./streamlit',  # ⬅️ 变成动态分隔符
    f'--add-data=audit_app.py{sep}.',                # ⬅️ 变成动态分隔符
    '--copy-metadata=streamlit'
    # '--icon=app_icon.ico'  # 如果你加了图标，把这行最前面的井号去掉
])
