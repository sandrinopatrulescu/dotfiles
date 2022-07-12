@echo off
:: NOTE that "%~dp0" works w/ or w/o "." (dot) after it when only itself is used


:: %~dp0 is current dir https://stackoverflow.com/questions/112055/what-does-d0-mean-in-a-windows-batch-file
SET "DOTSW=%~dp0" & :: dotfiles windows
:: https://stackoverflow.com/a/67095861 from https://stackoverflow.com/questions/16623780/how-to-get-windows-batchs-parent-folder
FOR %%V in ("%~dp0.") DO SET "DOTS=%%~dpV"

:: uglier variant: shows ...\..\
:: SET DOTS=%~dp0..\ & :: https://stackoverflow.com/a/67095861 from https://stackoverflow.com/questions/16623780/how-to-get-windows-batchs-parent-folder


::echo DOTWS=%DOTSW%
::echo DOTS=%DOTS%


CALL "%DOTSW%\env.cmd"
CALL "%DOTSW%\aliases.cmd"
