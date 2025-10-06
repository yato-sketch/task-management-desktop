#!/usr/bin/env python3
"""
Build script for creating Windows executable of Task Manager App
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_windows_app():
    """Build Windows executable using PyInstaller"""
    
    print("🚀 Building Windows Task Manager Application...")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"])
    
    # Define paths
    script_dir = Path(__file__).parent
    main_script = script_dir / "main.py"
    dist_dir = script_dir / "dist"
    build_dir = script_dir / "build"
    
    # Clean previous builds
    if dist_dir.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=TaskManager",           # Executable name
        "--icon=icon.ico",              # App icon (if exists)
        "--manifest=app.manifest",      # Include manifest file
        "--add-data=tasks.json:.",      # Include tasks.json
        "--hidden-import=customtkinter",
        "--hidden-import=tkcalendar",
        "--hidden-import=plyer",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "--hidden-import=threading",
        "--hidden-import=time",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=pathlib",
        str(main_script)
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not (script_dir / "icon.ico").exists():
        cmd.remove("--icon=icon.ico")
        print("ℹ️  No icon.ico found, building without custom icon")
    
    print("🔨 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=script_dir, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created (Linux creates without .exe extension)
        exe_path = dist_dir / "TaskManager"
        exe_path_exe = dist_dir / "TaskManager.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 File size: {size_mb:.1f} MB")
            
            # Rename to .exe for Windows compatibility
            if not exe_path_exe.exists():
                exe_path.rename(exe_path_exe)
                print("📝 Renamed to TaskManager.exe for Windows")
            
            # Copy tasks.json to dist folder if it exists
            tasks_file = script_dir / "tasks.json"
            if tasks_file.exists():
                shutil.copy2(tasks_file, dist_dir / "tasks.json")
                print("📄 Copied tasks.json to distribution folder")
            
            print("\n🎉 Windows application ready!")
            print(f"📁 Location: {dist_dir}")
            print(f"🚀 Run: {exe_path_exe}")
            
        elif exe_path_exe.exists():
            size_mb = exe_path_exe.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path_exe}")
            print(f"📏 File size: {size_mb:.1f} MB")
            
            # Copy tasks.json to dist folder if it exists
            tasks_file = script_dir / "tasks.json"
            if tasks_file.exists():
                shutil.copy2(tasks_file, dist_dir / "tasks.json")
                print("📄 Copied tasks.json to distribution folder")
            
            print("\n🎉 Windows application ready!")
            print(f"📁 Location: {dist_dir}")
            print(f"🚀 Run: {exe_path_exe}")
            
        else:
            print("❌ Executable not found in dist folder")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script"""
    installer_script = """@echo off
echo Installing Task Manager Application...
echo.

REM Create application directory
if not exist "%USERPROFILE%\\TaskManager" mkdir "%USERPROFILE%\\TaskManager"

REM Copy executable
copy "TaskManager.exe" "%USERPROFILE%\\TaskManager\\"
copy "tasks.json" "%USERPROFILE%\\TaskManager\\" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Task Manager.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\\TaskManager\\TaskManager.exe'; $Shortcut.Save()"

echo.
echo ✅ Installation completed!
echo 📁 Application installed to: %USERPROFILE%\\TaskManager
echo 🖥️  Desktop shortcut created
echo.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    print("📝 Created install.bat installer script")

if __name__ == "__main__":
    print("Task Manager - Windows Build Script")
    print("=" * 40)
    
    if build_windows_app():
        create_installer_script()
        print("\n🎯 Next steps:")
        print("1. Test the executable: dist/TaskManager.exe")
        print("2. Distribute the 'dist' folder or use install.bat")
        print("3. For advanced packaging, consider using NSIS or Inno Setup")
    else:
        print("\n❌ Build failed. Check the error messages above.")
        sys.exit(1)
