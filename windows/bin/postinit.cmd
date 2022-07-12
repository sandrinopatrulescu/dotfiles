@echo off & REM run this file ONLY 1, at fresh installs
:: TODO: why is this here? Why not move it to autorun.cmd or make an install.cmd which contains both autorun.cmd and this file?


IF NOT EXIST %LOGDIR%\ MD %LOGDIR% || echo "Could not create %LOGDIR%\. There's a file with that name"