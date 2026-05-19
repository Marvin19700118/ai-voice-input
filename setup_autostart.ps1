# setup_autostart.ps1
# 將 AI 語音輸入工具加入 Windows 開機自動啟動
# 執行方式：右鍵 → 以 PowerShell 執行

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue)?.Source

if (-not $pythonw) {
    # 嘗試常見路徑
    $candidates = @(
        "C:\Python313\pythonw.exe",
        "C:\Python312\pythonw.exe",
        "C:\Python311\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $pythonw = $c; break }
    }
}

if (-not $pythonw) {
    Write-Error "找不到 pythonw.exe，請確認 Python 已安裝"
    pause
    exit 1
}

$startupFolder = [System.Environment]::GetFolderPath("Startup")
$shortcutPath  = "$startupFolder\AI語音輸入.lnk"

$shell    = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath      = $pythonw
$shortcut.Arguments       = "`"$scriptDir\main.py`""
$shortcut.WorkingDirectory = $scriptDir
$shortcut.Description     = "AI 語音輸入工具"
$shortcut.WindowStyle     = 7
$shortcut.Save()

Write-Host "✅ 開機自動啟動已設定！" -ForegroundColor Green
Write-Host "   捷徑位置：$shortcutPath"
Write-Host ""
Write-Host "立即啟動中..."
Start-Process $pythonw -ArgumentList "`"$scriptDir\main.py`"" -WorkingDirectory $scriptDir
Write-Host "✅ 程式已在背景執行，請查看系統匣。" -ForegroundColor Green
pause
