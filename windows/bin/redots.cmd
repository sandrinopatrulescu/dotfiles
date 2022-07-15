@echo off
REM reinstalls dotfiles


SET ret_dir=%CD%
cd %DOTS%\..

rmdir /S dotfiles
git clone https://github.com/sandrinopatrulescu/dotfiles 
dotfiles\windows\install.cmd

cd %ret_dir%
SET ret_dir=
