@echo off
echo Installing Task Manager Application...
echo.

REM Create application directory
if not exist "%USERPROFILE%\TaskManager" mkdir "%USERPROFILE%\TaskManager"

REM Copy executable
copy "TaskManager.exe" "%USERPROFILE%\TaskManager\"
copy "tasks.json" "%USERPROFILE%\TaskManager\" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Task Manager.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\TaskManager\TaskManager.exe'; $Shortcut.Save()"

echo.
echo ✅ Installation completed!
echo 📁 Application installed to: %USERPROFILE%\TaskManager
echo 🖥️  Desktop shortcut created
echo.
pause
