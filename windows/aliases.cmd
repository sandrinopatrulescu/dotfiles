@echo off & :: https://www.makeuseof.com/what-does-the-at-sign-mean-in-echo-off/




DOSKEY alias="notepad++.exe" E:\dotfiles\windows\aliases.cmd & :: https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt
DOSKEY dots=cd E:\dotfiles
DOSKEY tmp=cd C:\Users\sandr\AppData\Local\Temp


:: Windows replaced
DOSKEY v = "%DOTSW%\bin\var.cmd" $* & :: get the value of a variable without enclosing it in % %
DOSKEY paths = %DOTSW%\bin\paths.cmd & :: print path folders on new lines




:: https://gist.github.com/PierreMage/6874814
DOSKEY cat = type $*
DOSKEY clear = cls
DOSKEY cp = copy $*
DOSKEY cpr = xcopy $*
DOSKEY grep = find $*
DOSKEY kill = taskkill /PID $*
DOSKEY ls = dir $*
DOSKEY man = help $*
DOSKEY mv = move $*
DOSKEY ps = tasklist $*
DOSKEY pwd = cd
DOSKEY rm = del $*
DOSKEY sudo = runas /user:administrator $*

DOSKEY touch = copy nul $* > nul & :: https://stackoverflow.com/questions/28662004/setup-windows-doskey-for-echo-filename-txt


DOSKEY ~=cd %USERPROFILE%

:: Programs
DOSKEY npp = "notepad++.exe" $* 
DOSKEY python = E:\Programs\python-3.10.4-embed-amd64\python $*


::UnxUtils
::DOSKEY fdate = %UU%\date +%%Y-%%m-%%d_%%H-%%M-%%S
DOSKEY fdate = %DOTSWB%\fdate.cmd


:::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Other scripts
:: 1. https://gist.github.com/PierreMage/6874814


:: Tutorials
:: (not read) 1. https://sodocumentation.net/batch-file/topic/3528/variables-in-batch-files 


:: Refs
:: 1. inline comments
::	https://stackoverflow.com/questions/11269338/how-to-comment-out-add-comment-in-a-batch-cmd
::	https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-xp/bb490954(v=technet.10)?redirectedfrom=MSDN
:: 2. https://stackoverflow.com/questions/47507185/how-to-define-a-doskey-alias-for-multiple-commands
:: 3. https://stackoverflow.com/questions/29930624/batch-files-if-directory-exists-do-something
:: 4. https://stackoverflow.com/questions/21057846/was-unexpected-at-this-time-if-exist-folder
:: 5. https://stackoverflow.com/a/2768662/17299754 from https://stackoverflow.com/questions/2768608/batch-equivalent-of-bash-backticks
:: 6. https://www.tutorialspoint.com/batch_script/batch_script_replace_string.htm