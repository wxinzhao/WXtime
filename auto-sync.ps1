$watchPath = "E:\desktop\学习资料\WXtime"
$lastStatus = ""
$debounceSeconds = 10

Write-Host "Watching for file changes (every 5s)..." -ForegroundColor Cyan
Write-Host "Auto: git add -> commit -> tag -> push" -ForegroundColor Cyan
Write-Host "Rollback: git checkout v<number>" -ForegroundColor Yellow
Write-Host "List versions: git tag -l" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Magenta

while ($true) {
    Start-Sleep -Seconds 5
    Set-Location -LiteralPath $watchPath

    $status = git status --porcelain
    if (-not $status) { continue }
    if ($status -eq $lastStatus) { continue }
    $lastStatus = $status

    Write-Host "`nChanges detected:" -ForegroundColor Green
    $status

    Start-Sleep -Seconds $debounceSeconds

    $files = git status --porcelain | ForEach-Object { $_.Substring(3) } | Where-Object { $_ -notmatch 'auto-sync\.ps1$' }
    $files | ForEach-Object { git add $_ 2>$null }

    $hasChanges = git diff --cached --name-only
    if (-not $hasChanges) { Write-Host "No valid changes, skip" -ForegroundColor DarkGray; continue }

    $lastTag = git tag --sort=-creatordate | Select-Object -First 1
    if (-not $lastTag) { $nextVer = 1 } else { $nextVer = [int]$lastTag.Substring(1) + 1 }

    $ver = "v$nextVer"
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $msg = "[$ver] auto sync $time"

    git commit -m $msg
    git tag -a $ver -m $msg
    git push --follow-tags 2>&1

    Write-Host "Synced -> $ver ($time)" -ForegroundColor Green
    $lastStatus = ""
}
