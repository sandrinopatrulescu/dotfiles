@echo off


set DOTSWB="%DOTSW%\bin"
set LOGDIR=%USERPROFILE%\logs

:: TODO deal with duplicate path values due to calls to "src"
SET PATH=%DOTSWB%;%PATH% & :: https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html


:: system dependent
set UU="%DOTSW%\external-tools\UnxUtils\usr\local\wbin"

SET PATH=%UU%;%PATH%
