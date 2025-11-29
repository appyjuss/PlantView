@echo off
REM PlantView - Self-Hosted Auth Quick Start Script

echo.
echo ========================================
echo PlantView - Self-Hosted Authentication
echo ========================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo Error: Run this script from the PlantView root directory
    exit /b 1
)

REM Activate venv and start backend from root directory
echo Starting Flask backend...
start "Flask Backend" cmd /k "venv\scripts\activate && python -m backend"

REM Wait a moment for Flask to start
timeout /t 3 /nobreak

REM Start frontend dev server
echo Starting React frontend...
start "React Frontend" cmd /k "cd plantViewFrontend && npm run dev"

echo.
echo ========================================
echo Services starting:
echo - Backend: http://localhost:5000
echo - Frontend: http://localhost:5173
echo ========================================
echo.
echo Frontend will open in a moment...
timeout /t 3 /nobreak

REM Open frontend in browser
start http://localhost:5173

echo Done! Check the opened windows for logs.
