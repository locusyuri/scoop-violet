# disable-auto-update.ps1
#
# 将 atomcode 的自更新开关（auto_update）设为 false，让 scoop 统一管理版本。
# 由 bucket/atomcode.json 的 post_install 自动调用；也可手动运行。
#
# 设计要点：
# - 只做行级修改/追加，绝不整体覆盖用户已有的 config.toml（内含 API 密钥等敏感信息）
# - 配置目录遵循 atomcode 约定：$ATOMCODE_HOME 优先，否则 %USERPROFILE%\.atomcode
# - 写回使用不带 BOM 的 UTF-8（TOML 解析器对 BOM 敏感）

$ErrorActionPreference = 'Stop'

$configDir = if ($env:ATOMCODE_HOME) { $env:ATOMCODE_HOME } else { Join-Path $env:USERPROFILE '.atomcode' }
$configFile = Join-Path $configDir 'config.toml'

New-Item -ItemType Directory -Force -Path $configDir | Out-Null

# 不带 BOM 的 UTF-8 编码
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$keyPattern = '(?m)^[ \t]*auto_update[ \t]*='
$truePattern = '(?m)^[ \t]*auto_update[ \t]*=[ \t]*true[ \t]*$'
$replacement = 'auto_update = false'

if (Test-Path $configFile) {
    $content = [System.IO.File]::ReadAllText($configFile)

    if ($content -match $truePattern) {
        $newContent = [System.Text.RegularExpressions.Regex]::Replace($content, $truePattern, $replacement)
        [System.IO.File]::WriteAllText($configFile, $newContent, $utf8NoBom)
        Write-Host 'atomcode: auto_update 已设为 false（自更新已关闭）'
    } elseif ($content -notmatch $keyPattern) {
        # 旧配置中没有该键：在末尾追加一行（TOML 顶层键位置无关）
        $newContent = $content.TrimEnd() + "`n`nauto_update = false`n"
        [System.IO.File]::WriteAllText($configFile, $newContent, $utf8NoBom)
        Write-Host 'atomcode: 已追加 auto_update = false（自更新已关闭）'
    } else {
        Write-Host 'atomcode: auto_update 已是 false，无需修改'
    }
} else {
    # 首次安装：创建最小配置，仅关闭自更新；其余字段由 atomcode 使用默认值
    [System.IO.File]::WriteAllText($configFile, "auto_update = false`n", $utf8NoBom)
    Write-Host "atomcode: 已创建 $configFile（auto_update = false）"
}
