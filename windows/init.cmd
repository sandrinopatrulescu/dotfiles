@echo off

set DOTS=E:\dotfiles
set "DOTSW=E:\dotfiles\windows" & :: dotfiles windows


CALL "%DOTSW%\env.cmd"
CALL "%DOTSW%\aliases.cmd"


:: add E:\dotfiles\windows\bin to PATH
