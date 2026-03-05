import os
import streamlit
import PyInstaller.__main__

# 自动定位你电脑上 Streamlit 库的真实安装路径
streamlit_path = os.path.dirname(streamlit.__file__)

print(f"✅ 成功找到 Streamlit 网页前端文件路径: {streamlit_path}")
print("🚀 正在强行挂载静态文件并开始打包...")

PyInstaller.__main__.run([
    'run_app.py',
    '--name=Audit_WalkThrough_System',
    '--onedir',
    '--noconfirm',
    '--clean',  # 自动清理上次失败的缓存
    f'--add-data={streamlit_path};./streamlit',  # 核心：强行把 HTML/JS/CSS 塞进包里
    '--add-data=audit_app.py;.',
    '--copy-metadata=streamlit'
])