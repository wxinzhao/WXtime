@echo off

echo Starting WeChat Message System...

:: Set project path
set projectPath=c:\Users\25686\Desktop\pythom

:: Start backend service
echo Starting backend service...
start powershell -NoExit -Command "cd '%projectPath%\backend'; python app.py"

:: Wait for backend to start
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

:: Start frontend service
echo Starting frontend service...
start powershell -NoExit -Command "cd '%projectPath%\frontend'; npm run dev"

:: Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

:: Open browser
echo Opening browser...
start http://localhost:5173

echo Project started successfully!
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:5000

pause
