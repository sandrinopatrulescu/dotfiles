@echo off

set init_path=%cd%\init.cmd
echo %init_path%

reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d %init_path%

pause