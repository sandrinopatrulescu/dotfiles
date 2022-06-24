@echo off & REM run this file ONLY 1, at fresh installs


IF NOT EXIST %LOGDIR%\ MD %LOGDIR% || echo "Could not create %LOGDIR%\. There's a file with that name"