@echo off


set DOTSWB="%DOTSW%\bin"
set LOGDIR=%USERPROFILE%\logs

:: system dependent
:: TODO: why set UU instead od adding it to the path?
:: TODO:  add the bin folder to the path and maybe remove UU if not found used with grep
:: TODO: even better, inside windows/ add a folder called "external-tools" and automatically download it on install
set UU="E:\Programs\UnxUtils\usr\local\wbin"
set UU="%DOTSW%\external-tools\UnxUtils\usr\local\wbin"

SET PATH=%UU%;%PATH% & :: https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html
