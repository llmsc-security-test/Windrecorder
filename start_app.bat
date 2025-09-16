@echo off
title Windrecorder
mode con cols=70 lines=10
color 75
echo.
echo   Initializing Windrecorder, please stand by...
echo.
echo   Please stay in this window until it disappears
echo.

cd /d %~dp0
if exist "hide_CLI_by_python.txt" (
    goto begin
) else (
    goto hide
)

:hide
@REM hide CLI immediately
if "%1"=="h" goto begin
start mshta vbscript:createobject("wscript.shell").run("%~nx0"^&" h",0)^&(window.close) && exit /b

:begin
cd /d %~dp0
set "UV_EXE="
for /f "delims=" %%i in ('where uv 2^>nul') do set "UV_EXE=%%i"
if defined UV_EXE (
    "%UV_EXE%" run python "%~dp0\main.py"
    goto end
)

if exist "%~dp0\.venv\Scripts\activate.bat" (
    call "%~dp0\.venv\Scripts\activate.bat"
    python "%~dp0\main.py"
    goto end
)

for /F "tokens=* USEBACKQ" %%A in (`python -m poetry env info --path 2^>nul`) do call "%%A\Scripts\activate.bat"
python "%~dp0\main.py"

:end