@echo off
:: https://stackoverflow.com/questions/46739953/setting-permissions-to-default-on-windows-10-cmd-line-icacls-or-similar

:: usage: specify the files

:: get the datetime
for /F %%i in ('fdate') do set "exetime=%%i" $ :: exetime - execution time, https://stackoverflow.com/a/2768662/17299754 from https://stackoverflow.com/questions/2768608/batch-equivalent-of-bash-backticks

set script_name=%0
set log_file_prefix=%LOGDIR%\%script_name:.cmd=%_%exetime%



echo "Step 1"
takeown.exe /d y /r /a /f %* | tee --append %log_file_prefix%_step1.txt
REM to interpret the result:
REM sed -E '/^ *$/d; /SUCCESS/d' default-permissions_2022-04-17_23-31-00_step1.txt
REM or hide success messages using /q

echo "Step 2"
icacls %* /remove:d SYSTEM                /grant SYSTEM:(OI)(CI)(IO)F | tee --append %log_file_prefix%_step2.1.txt
icacls %* /remove:d "Authenticated Users" /grant "Authenticated Users":(OI)(CI)(IO)M | tee --append %log_file_prefix%_step2.2.txt
icacls %* /remove:d Administrators        /grant Administrators:(OI)(CI)(IO)F | tee --append %log_file_prefix%_step2.3.txt
icacls %* /remove:d Users                 /grant Users:(OI)(CI)(IO)(GR,GE) | tee --append %log_file_prefix%_step2.4.txt

echo "Step 3"
icacls %* /reset /t /l /c /q | tee --append %log_file_prefix%_step3.txt



SET "exetime="
SET "script_name="
set "log_file_prefix="
EXIT /B REM exit the script and return to the caller https://www.robvanderwoude.com/exit.php
