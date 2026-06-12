$watchPath = "E:\desktop\学习资料\WXtime"
$lastStatus = ""
$debounceSeconds = 10

Write-Host "正在监听文件变更，每 5 秒检查一次..." -ForegroundColor Cyan
Write-Host "每次变更将自动: git add → commit → tag → push" -ForegroundColor Cyan
Write-Host "回滚命令: git checkout v<版本号>" -ForegroundColor Yellow
Write-Host "查看版本: git tag -l" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 停止监听`n" -ForegroundColor Magenta

while ($true) {
    Start-Sleep -Seconds 5
    Set-Location -LiteralPath $watchPath

    $status = git status --porcelain
    if (-not $status) { continue }
    if ($status -eq $lastStatus) { continue }
    $lastStatus = $status

    Write-Host "`n检测到文件变更:" -ForegroundColor Green
    $status

    Start-Sleep -Seconds $debounceSeconds

    $files = git status --porcelain | ForEach-Object { $_.Substring(3) } | Where-Object { $_ -notmatch 'auto-sync\.ps1$' }
    $files | ForEach-Object { git add $_ 2>$null }

    $hasChanges = git diff --cached --name-only
    if (-not $hasChanges) { Write-Host "无有效变更，跳过提交" -ForegroundColor DarkGray; continue }

    $lastTag = git tag --sort=-creatordate | Select-Object -First 1
    if (-not $lastTag) { $nextVer = 1 } else { $nextVer = [int]$lastTag.Substring(1) + 1 }

    $ver = "v$nextVer"
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $msg = "[$ver] 自动同步 $time"

    git commit -m $msg
    git tag -a $ver -m $msg
    git push --follow-tags 2>&1

    Write-Host "已同步 → $ver ($time)" -ForegroundColor Green
    $lastStatus = ""
}
