# 启动项目脚本
# 启动后端、前端服务并打开浏览器

Write-Host "开始启动微信定时消息管理系统..." -ForegroundColor Green

# 定义项目路径
$projectPath = "c:\Users\25686\Desktop\pythom"

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath\backend'; python app.py"

# 等待后端服务启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath\frontend'; npm run dev"

# 等待前端服务启动
Write-Host "等待前端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 打开浏览器
Write-Host "打开浏览器..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "项目启动完成！" -ForegroundColor Green
Write-Host "前端地址: http://localhost:5173" -ForegroundColor White
Write-Host "后端API: http://localhost:5000" -ForegroundColor White
