@echo off
setlocal

echo =========================================
echo   VeriNews AI 2.0 — Startup Script
echo =========================================
echo.

:: ─────────────────────────────────────────
:: 1. CHECK PYTHON
:: ─────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo.
    echo  Install Python 3.9 or later from:
    echo    https://www.python.org/downloads/
    echo.
    echo  During installation, tick:
    echo    "Add Python to PATH"
    echo.
    echo  After installing, close and reopen this window.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] %PYVER% found.

:: ─────────────────────────────────────────
:: 2. CHECK NODE / NPM
:: ─────────────────────────────────────────
where node >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Node.js was not found in PATH.
    echo.
    echo  Install Node.js LTS from:
    echo    https://nodejs.org/en/download
    echo.
    echo  Choose the Windows Installer (.msi) — it installs
    echo  both Node.js and npm automatically.
    echo.
    echo  After installing:
    echo    1. Close ALL open terminals / CMD windows.
    echo    2. Open a new CMD window.
    echo    3. Run this script again.
    echo.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] npm was not found even though Node.js is present.
    echo.
    echo  Try re-installing Node.js LTS from:
    echo    https://nodejs.org/en/download
    echo.
    echo  Then open a NEW terminal and run this script again.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version 2^>^&1') do set NODEVER=%%v
for /f "tokens=*" %%v in ('npm --version  2^>^&1') do set NPMVER=%%v
echo [OK] Node.js %NODEVER%  /  npm %NPMVER% found.
echo.

:: ─────────────────────────────────────────
:: 3. BACKEND
:: ─────────────────────────────────────────
echo [1/2] Starting FastAPI backend on port 8000...
cd /d "%~dp0backend"

if not exist ".venv" (
    echo   Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
echo   Installing / verifying Python packages...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] pip install failed. Check requirements.txt and your internet connection.
    pause
    exit /b 1
)

start "VeriNews Backend" cmd /k "cd /d "%~dp0backend" && call .venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo   Backend launching at http://127.0.0.1:8000
echo   API Docs:           http://127.0.0.1:8000/docs
echo.

:: Give uvicorn a moment to bind the port
timeout /t 4 /nobreak >nul

:: ─────────────────────────────────────────
:: 4. FRONTEND
:: ─────────────────────────────────────────
echo [2/2] Starting Vite frontend on port 3000...
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo   Running npm install (first run — may take a minute)...
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Check your internet connection.
        pause
        exit /b 1
    )
)

start "VeriNews Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo   Frontend launching at http://localhost:3000
echo.

:: ─────────────────────────────────────────
:: 5. DONE
:: ─────────────────────────────────────────
echo =========================================
echo   Both servers are starting up.
echo.
echo   Wait ~5 seconds, then open:
echo     http://localhost:3000
echo.
echo   Backend health check:
echo     http://127.0.0.1:8000/api/health
echo.
echo   API docs (Swagger UI):
echo     http://127.0.0.1:8000/docs
echo =========================================
echo.
pause
endlocal
