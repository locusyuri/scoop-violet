# PostToolUse hook: 校验 bucket/*.json manifest 合法性
# 由 .hooks.json 调用；stdin 接收 CC 兼容 payload JSON，stdout 输出检查结果。
$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$path = $payload.tool_input.file_path
if ($path -and ($path -match '(?i)^bucket[\\/].+\.json$')) {
    try {
        Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
        Write-Output "manifest JSON OK: $path"
    } catch {
        Write-Output "manifest JSON INVALID: $path - $($_.Exception.Message)"
    }
}
