# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/shimamura/Documents/upwork/desktop-task-manage-app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('tasks.json', '.')],
    hiddenimports=['customtkinter', 'tkcalendar', 'plyer', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'json', 'datetime', 'threading', 'time', 'os', 'sys', 'pathlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TaskManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
    manifest='app.manifest',
)
