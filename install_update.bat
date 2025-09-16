@echo off
title Windrecorder - installing dependence and updating
mode con cols=150 lines=50

cd /d %~dp0

echo -git: updating repository
git pull

echo -setup: ensuring uv is installed
set "UV_EXE="
for /f "delims=" %%i in ('where uv 2^>nul') do set "UV_EXE=%%i"

if not defined UV_EXE (
    echo   uv not found, installing via official installer...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { iwr -useb https://astral.sh/uv/install.ps1 ^| iex } catch { exit 1 }"
    for /f "delims=" %%i in ('where uv 2^>nul') do set "UV_EXE=%%i"
)

if not defined UV_EXE (
    echo   fallback: installing uv via pip mirror...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uv
    for /f "delims=" %%i in ('where uv 2^>nul') do set "UV_EXE=%%i"
)

if not defined UV_EXE (
    echo FATAL: uv still not available. Please install manually:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    echo or: python -m pip install uv
    pause
    exit /b 1
)

set "TARGET_PY=3.11"
for /f "delims=" %%v in ('python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')" 2^>nul') do set "HOST_PY=%%v"
if defined HOST_PY (
    if "%HOST_PY%"=="3.10" set "TARGET_PY=%HOST_PY%"
    if "%HOST_PY%"=="3.11" set "TARGET_PY=%HOST_PY%"
)

echo -uv: preparing Python %TARGET_PY% interpreter (if needed)
"%UV_EXE%" python install %TARGET_PY% >nul 2>nul

echo -uv: syncing dependencies into .venv
"%UV_EXE%" sync --in-project --python %TARGET_PY%
if errorlevel 1 (
    echo   uv sync failed. Trying legacy Poetry as fallback...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple poetry
    python -m poetry config virtualenvs.in-project true
    python -m poetry install
)

color 0e
title Windrecorder - Quick Setup
"%UV_EXE%" run python "%~dp0\onboard_setting.py"

pause