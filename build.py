import PyInstaller.__main__
import customtkinter
import os
import sys

# 1. Get the directory where THIS build.py file exists
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Construct the full path to your installer script
script_path = os.path.join(current_dir, 'tidaluna installer.py')

# 3. Get the path to customtkinter library (needed for themes)
ctk_path = os.path.dirname(customtkinter.__file__)

# 4. Define where the output .exe should go
dist_path = os.path.join(current_dir, "dist")
work_path = os.path.join(current_dir, "build")

print(f"Building from: {script_path}")

PyInstaller.__main__.run([
    script_path,                    # Full path to your script
    '--onefile',                    # Single .exe file
    '--windowed',                   # No black console window
    '--noconfirm',                  # Overwrite old builds
    '--name=TidaLuna Installer',    # Name of the exe
    f'--add-data={ctk_path};customtkinter/', # Include themes
    f'--distpath={dist_path}',      # Put .exe in "dist" folder inside project
    f'--workpath={work_path}',      # Put temp files in "build"
    f'--specpath={current_dir}',    # Put .spec file in project root
])