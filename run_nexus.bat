@echo off
echo ========================================================
echo   NEXUS: Personal Intelligence & Growth Network
echo   Initializing Backend API and Web Portal...
echo ========================================================
python -m uvicorn nexus_core.main:app --host 127.0.0.1 --port 8000 --reload
pause
