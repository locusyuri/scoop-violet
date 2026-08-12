# PreToolUse hook: 阻止 AI 编辑含 GitHub 令牌的 backup.yml
# 由 .hooks.json 调用；stdin 接收 CC 兼容 payload JSON，stdout 输出决策 JSON。
$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$path = $payload.tool_input.file_path
if ($path -and ($path -like '*backup.yml')) {
    Write-Output '{"action":"block","reason":"backup.yml 包含 GitHub 令牌，禁止通过 AI 编辑；如需修改请手动操作"}'
} else {
    Write-Output '{"action":"allow"}'
}
