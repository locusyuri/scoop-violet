---
name: manifest-reviewer
description: 按 wiki/SPEC.md 规范审查本仓库 bucket/ 下的 Scoop manifest（新增或修改后）。当用户要求"审查 manifest"、"检查 bucket 规范"、"review 应用清单"时触发。只读审查，不修改任何文件。
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash
---

# Manifest 审查（scoop-violet）

按 [wiki/SPEC.md](../../wiki/SPEC.md) 逐项审查 `bucket/*.json`，输出 pass/fail 清单。**只读，不修改文件**。

## 审查清单

### 结构与格式

- [ ] JSON 合法（无注释、无尾逗号、UTF-8、2 空格缩进）
- [ ] 文件名 = 应用名（`bucket/<应用>.json`）
- [ ] 必填字段齐全：`version`、`description`、`homepage`、`license`、`url`+`hash`
- [ ] `version` 不带 `v` 前缀；含 `architecture` 时键为 `64bit`/`32bit`/`arm64`（不是 x64/x86）

### 更新链路（第 12 节约定）

- [ ] `checkver` 与 `autoupdate` 成对出现，缺一不可
- [ ] `autoupdate.url` 模板使用 `$version` / `$cleanVersion` / `$match<Name>`，与 checkver 捕获一致
- [ ] `autoupdate.hash` 配置正确（jsonpath 或 `$sha256`），与最新版 hash 对齐
- [ ] 若顶层有 `url`/`hash` 数组，两数组一一对应

### 路径与引用

- [ ] manifest 内子目录用 `\\` 分隔
- [ ] `bin`/`shortcuts`/`persist` 引用的文件存在于下载包内（或备注说明）
- [ ] 脚本引用形如 `"$bucketsdir\\$bucket\\scripts\\<应用>\\..."`，对应文件存在于 `scripts/<应用>/`
- [ ] `persist` 不指向用户目录（`%APPDATA%`、`~` 等）——数据目录在用户主目录时应留空 persist

### 行为安全

- [ ] `post_install` 若修改用户配置，是行级修改/追加而非整体覆盖（防密钥丢失）
- [ ] 未调用会删除用户数据的官方卸载脚本（如 atomcode 的 uninstall.ps1）
- [ ] 无明文密钥/令牌写入 manifest 或脚本
- [ ] 应用自带自更新与 scoop 冲突时已用 post_install 关闭（参考 atomcode）

## 输出格式

每个文件输出：

```
<应用>.json: PASS/FAIL（n 项不通过）
- [x] 项 1 …
- [ ] 项 2 …   ← 不通过项给出具体说明与修复建议
```

全部 PASS 时输出 `全部 manifest 通过审查`。若用户要求，可顺带运行：

```bash
powershell -NoProfile -Command 'Get-ChildItem bucket -Filter *.json | ForEach-Object { Get-Content $_.FullName -Raw | ConvertFrom-Json | Out-Null }; "JSON 全部合法"'
```
