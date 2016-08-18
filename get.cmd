@echo off
for /f %%i in (list.txt) do (
echo %%i
"C:\programs\Python 3.5\python.exe" getComic.py -p s:\tx\comic -u http://ac.qq.com/Comic/comicInfo/id/%%i
echo return code : %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 echo %%i >>error2.txt
TIMEOUT /T 5
)