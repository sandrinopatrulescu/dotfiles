@echo off


REM autorun init 
SET init_path=%cd%\init.cmd
echo init_path=%init_path%

:: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/reg-add
reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d %init_path% 
SET init_path=



REM download UnxUtils
SET ret_dir=%CD% & :: save current loc
cd external-tools
mkdir UnxUtils && cd UnxUtils 
curl "https://deac-fra.dl.sourceforge.net/project/unxutils/unxutils/current/UnxUtils.zip" -O
tar -xf UnxUtils.zip
rm UnxUtils.zip
cd %ret_dir% & ::go back to prev loc
SET ret_dir=





PAUSE
