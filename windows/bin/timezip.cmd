@echo off

FOR /F %%i IN ('fdate') DO SET "zip_name=%1_%%i"
ECHO zipping to %zip_name%


zip -r %zip_name% %1


:: cleanup
SET "zip_name="

ECHO "WARN: It is NOT working for .git/ dirs"