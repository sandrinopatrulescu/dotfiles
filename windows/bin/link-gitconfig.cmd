@echo off
setlocal enabledelayedexpansion

SET linkDir=%userprofile%
SET linkName=.gitconfig
SET target=%DOTS%gitconfig

SET link=%linkDir%\%linkName%


IF EXIST "%link%" (
	DIR %link% | FINDSTR "<SYMLINK>[ ]+%linkName% \[%target%\]" >nul && SET "found=1" || SET "found=0"

	IF "!found!" EQU "1" (
		echo "%link%" is already a symlink to "%target%"
	) ELSE (
		echo "%link%" is NOT a symlink to "%target%".
		echo Check it's contents and eventually run:
		echo mklink "%link%" "%target%"
	)
) ELSE (
    mklink %link% %target%
)

endlocal