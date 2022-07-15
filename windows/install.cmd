@echo off


GOTO comment & :: for easier testing
cd %userprofile%\stuff && rmdir /s /q dotfiles & git clone https://github.com/sandrinopatrulescu/dotfiles && echo. && cd C:\ && %userprofile%\stuff\dotfiles\windows\install.cmd
:comment


REM run init.cmd
SET init_path=%~dp0\init.cmd
echo init_path=%init_path%

CALL %init_path%


REM autorun init 
:: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/reg-add
reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d %init_path%
echo.
SET init_path=



REM download UnxUtils
SET ret_dir=%CD% & :: save current loc
mkdir %DOTSW%\external-tools\UnxUtils
cd %DOTSW%\external-tools\UnxUtils
echo downloading UnxUtils... 
curl "https://deac-fra.dl.sourceforge.net/project/unxutils/unxutils/current/UnxUtils.zip" -O
tar -xf UnxUtils.zip
DEL UnxUtils.zip
cd %ret_dir% & ::go back to prev loc
SET ret_dir=




PAUSE
