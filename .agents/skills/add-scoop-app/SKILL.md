---
name: add-scoop-app
description: 为本仓库（scoop-violet）新增一个 Scoop 应用。当用户要求添加新软件/新应用到本 bucket、或要求"加一个 xxx 的 manifest"时触发。按 wiki/SPEC.md 规范完成调研→manifest→脚本→验证→README 全流程，且不修改仓库外任何文件。
disable-model-invocation: true
---

# 新增 Scoop 应用（scoop-violet）

为 scoop-violet bucket 新增应用。**严格遵循 [wiki/SPEC.md](../../wiki/SPEC.md) 的 manifest 规范**，只操作本仓库内文件。

## 流程

### 1. 调研（只读）

- 若用户提供 `ref/` 下的源码克隆与本地安装位置，先分析其发布方式（`es` 可定位本地安装）：
  - 发布产物类型（单 exe / NSIS 安装器 / zip 便携包 / 其他）
  - 版本来源（GitHub Releases / latest.json / 网页正则）
  - 是否有配置文件、数据目录、自更新机制
- 用 GitHub API（或 `es` 本机搜索）确认真实资产名与 hash——**页面显示名可能 ≠ 实际下载名**（如 `WeMD Setup 1.4.4.exe` 实际链接是 `WeMD.Setup.1.4.4.exe`）。

### 2. 编写 manifest

- 文件放 `bucket/<应用名>.json`，**不要放仓库根目录**。
- 必填字段：`version`（不带 `v`）、`description`、`homepage`、`license`、`url`+`hash`。
- **`checkver` 与 `autoupdate` 必须成对出现**（通用脚本 `scripts/update.py` 依赖它们自动更新，见 SPEC 第 12 节）。
- 可用的 checkver 形式：`"github"` / `{"github": "<owner/repo>"}` / `{"url","regex"}` / `{"url","jsonpath","regex"}`。
- autoupdate 支持 `$version`、`$cleanVersion`、`$match<Name>` 模板与 hash 抓取（jsonpath / `$sha256`）。
- 路径分隔符一律 `\\`；子目录用 `\\` 连接。
- 常见决策：
  - 便携单 exe → 直接 `bin`，无需 installer。
  - NSIS 安装器 → 用 `installer.script` 静默安装；可 `/D=$dir` 装进 scoop 目录（`/D=` 必须最后、不带引号）。
  - 数据目录在用户目录（如 `%APPDATA%`）→ 不要写 `persist`，卸载自动保留。
  - 应用自带自更新且会覆盖二进制 → 用 `scripts/<应用>/` 下的 post_install 脚本关闭（参考 `bucket/atomcode.json` 与 `scripts/atomcode/disable-auto-update.ps1`）。

### 3. 配套脚本（如需要）

- 放 `scripts/<应用名>/` 下，manifest 中用 `"$bucketsdir\\$bucket\\scripts\\<应用>\\<脚本>.ps1"` 引用。
- 修改用户目录配置时**只做行级修改/追加，禁止整体覆盖**（配置文件可能含密钥）。

### 4. 验证（必须）

```bash
powershell -NoProfile -Command 'Get-Content bucket/<应用>.json -Raw | ConvertFrom-Json | Out-Null'   # JSON 合法
uv run --no-project python scripts/update.py --dry-run    # checkver/autoupdate 链路（不写回）
```

- `update.py --dry-run` 应输出 `OK <应用>: up to date (<版本>)` 或按预期更新；出现 `FAIL` 必须排查。
- 若新版本可用时，在临时目录伪造旧版本实测一次更新路径（`--dir <临时目录>`），确认 url/hash 正确生成。

### 5. 收尾

- 更新 `README.md` 的「收录应用」表格。
- 未经用户明确要求，不要提交/推送；提交时用中文 conventional commit 消息。
