$watchPath = "E:\desktop\学习资料\WXtime"
$lastStatus = ""
$debounceSeconds = 10
$versionFile = "$watchPath\.version"

function Get-NextVersion {
    $lastTag = git tag --sort=-v:refname | Select-Object -First 1
    if (-not $lastTag -or $lastTag -notmatch '^v(\d+)$') { return "v1" }
    $num = [int]($matches[1]) + 1
    return "v$num"
}

function Get-VersionHistory {
    Write-Host "`n====== 版本历史 ======" -ForegroundColor Cyan
    git tag --sort=v:refname | ForEach-Object {
        $msg = git log --oneline -1 $_
        Write-Host "$_  -  $msg" -ForegroundColor White
    }
    Write-Host "=====================`n" -ForegroundColor Cyan
}

Write-Host "正在监听文件变更，每 5 秒检查一次..." -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止监听" -ForegroundColor Yellow
Write-Host "使用 'git log' 查看历史，使用 'git checkout v1' 回滚到指定版本" -ForegroundColor DarkGray

Get-VersionHistory

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

    git status --porcelain | ForEach-Object {
        $file = $_.Substring(3)
        if ($file -match 'auto-sync\.ps1$') { Write-Host "跳过 auto-sync.ps1 自身变更" -ForegroundColor DarkGray; return }
        git add $file 2>$null
    }

    $hasChanges = git diff --cached --name-only
    if (-not $hasChanges) { Write-Host "无有效变更，跳过提交" -ForegroundColor DarkGray; continue }

    $version = Get-NextVersion
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "$version - 自动同步 $time"
    git tag -a $version -m "版本 $version - $time"
    git push --follow-tags 2>&1

    Write-Host "已同步到 GitHub ($version - $time)" -ForegroundColor Green
    Write-Host "回滚命令: git checkout $version" -ForegroundColor Yellow
    $lastStatus = ""
}
