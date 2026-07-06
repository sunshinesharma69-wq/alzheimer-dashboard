@echo off
cd /d D:\alzheimer
echo Starting Alzheimer Dashboard...
echo.
echo Dashboard will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server.
echo.
timeout /t 2
start http://127.0.0.1:5000
d:\alzheimer\.venv\Scripts\python.exe app.py
