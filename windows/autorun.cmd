@echo off

set init_path=%cd%\init.cmd
echo init_path=%init_path%

:: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/reg-add
reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d %init_path% 

pause
