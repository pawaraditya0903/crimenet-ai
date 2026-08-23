@echo off
echo Starting CrimeNet AI Platform...
start "CrimeNet Backend" powershell -NoExit -Command "cd 'c:\Users\Aditya\Downloads\SIH 2026\backend'; python -m uvicorn app.main:socket_app --reload --port 8000"
start "CrimeNet Frontend" powershell -NoExit -Command "cd 'c:\Users\Aditya\Downloads\SIH 2026\frontend'; npm run dev"
timeout /t 3
start http://localhost:5173
echo CrimeNet AI is live on http://localhost:5173 !
