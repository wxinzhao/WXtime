$watchPath = "E:\desktop\学习资料\WXtime"
$lastStatus = ""
$debounceSeconds = 10

function Get-NextVersion {
    $latestTag = git tag --list 'v*' --sort=-v:refname | Select-Object -First 1
    if ($latestTag) {
        $num = [int]($latestTag -replace 'v', '')
        return "v$($num + 1)"
    }
    return "v1"
}

function Get-GitCommitCount {
    $count = git rev-list --count HEAD 2>$null
    if ($count) { return [int]$count }
    return 0
}

Write-Host "正在监听文件变更，每 5 秒检查一次..." -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止监听" -ForegroundColor Yellow

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

    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $version = Get-NextVersion
    git commit -m "$version - 自动同步 $time"
    git tag $version
    git push --atomic origin master $version 2>&1

    Write-Host "已同步到 GitHub，版本: $version ($time)" -ForegroundColor Green
    $lastStatus = ""
}
