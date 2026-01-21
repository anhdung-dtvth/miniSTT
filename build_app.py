import PyInstaller.__main__
import os
import shutil

# Remove previous build artifacts
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

print("Starting Build Process...")

PyInstaller.__main__.run([
    'gui_app.py',
    '--name=MiniSTT_Pro',
    '--onefile',
    '--windowed',  # No console window
    '--clean',
    
    # Include Source Code
    '--add-data=src;src',
    
    # Collect minimal dependencies to ensure they work
    '--collect-all=customtkinter',
    '--collect-all=whisper',
    '--collect-all=pygame', 
    
    # Hidden imports that sometimes get missed
    '--hidden-import=os',
    '--hidden-import=threading',
    '--hidden-import=winsound',
    '--hidden-import=tkinter',
])

print("Build Complete. Executable should be in 'dist' folder.")
