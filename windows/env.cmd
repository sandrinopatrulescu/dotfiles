@echo off


set DOTSWB="%DOTSW%\bin"
set LOGDIR=%USERPROFILE%\logs


SET PATH=%DOTSWB%;%PATH% & :: https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html


:: system dependent
:: TODO: why setting UU? remove UU if not found used with grep
:: TODO: automatically download UnxUtils on install
set UU="E:\Programs\UnxUtils\usr\local\wbin"
set UU="%DOTSW%\external-tools\UnxUtils\usr\local\wbin"

SET PATH=%UU%;%PATH%
