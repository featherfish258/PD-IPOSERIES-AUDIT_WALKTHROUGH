import os
import streamlit
import PyInstaller.__main__

streamlit_path = os.path.dirname(streamlit.__file__)
sep = os.pathsep 

# 换成纯英文，去掉 emoji，彻底绝杀编码报错
print(f"Found Streamlit frontend path: {streamlit_path}")
print(f"Starting cross-platform build with separator '{sep}'...")

PyInstaller.__main__.run([
    'run_app.py',
    '--name=Audit_WalkThrough_System',
    '--onedir',
    '--noconfirm',
    '--clean',  
    f'--add-data={streamlit_path}{sep}./streamlit',  
    f'--add-data=audit_app.py{sep}.',                
    '--copy-metadata=streamlit'
    # '--icon=app_icon.ico'  # 如果有图标，记得去掉井号
])
