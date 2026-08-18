# scoop-violet

个人的 Scoop bucket，收录自用软件清单（manifest）。

- **主仓库（自动化）**：<https://cnb.cool/catmono/scoop-violet>
- **备份仓库**：<https://github.com/locusyuri/scoop-violet>

## 收录应用

| 应用 | 版本 | 说明 |
| --- | --- | --- |
| [atomcode](https://atomgit.com/atomgit_atomcode/atomcode) | 5.0.6 | 开源终端 AI 编程助手（安装时自动关闭其内置自更新，交由 scoop 统一管理） |
| [wemd](https://wemd.app) | 1.4.4 | 更优雅的 Markdown 公众号排版工具（NSIS 安装到 scoop 目录，数据保存在 %APPDATA%\WeMD） |
| [fanqie-novel-downloader](https://github.com/POf-L/Fanqie-novel-Downloader) | 2026.8.18-538-r672 | 番茄小说下载器（免费番茄小说转 TXT/EPUB GUI 工具，Tauri 应用） |
| [dbx](https://github.com/t8y2/dbx) | 0.5.88 | 轻量级跨平台数据库客户端（80+ 数据库，数据保存在 scoop persist 目录） |

## 使用方法

添加本 bucket：

```powershell
scoop bucket add violet https://cnb.cool/catmono/scoop-violet.git
```

安装应用：

```powershell
scoop install violet/atomcode
```

更新应用：

```powershell
scoop update atomcode
```

> 说明：bucket 名（上例中的 `violet`）可自行指定，manifest 内 `post_install` 等脚本引用 `scripts/` 目录时依赖该名字，请保持一致。

## 目录结构

```
scoop-violet/
├── bucket/       # 应用 manifest（<应用名>.json），新增应用写在这里
├── scripts/      # 安装辅助脚本，按应用分子目录（如 scripts/atomcode/）
├── bin/          # 仓库维护工具（预留）
├── wiki/         # 文档，SPEC.md 为 manifest JSON 格式规范
├── ref/          # 参考材料（外部仓库只读克隆，不纳入 bucket）
├── AGENTS.md     # AI 助手安全边界与协作约定
└── README.md
```

## 新增应用

1. 参考 [wiki/SPEC.md](wiki/SPEC.md) 的 JSON 格式规范，在 `bucket/` 下新建 `<应用名>.json`；
2. 如需配套安装脚本，放入 `scripts/<应用名>/` 并在 manifest 中引用；
3. 本 bucket 约定：`checkver`/`autoupdate` 尽量配齐，便于自动更新；应用自更新与 scoop 冲突时，用 `post_install` 脚本关闭（参考 `bucket/atomcode.json`）；
4. 修改后请更新本 README 的「收录应用」表格。

## 仓库说明

- 主仓库托管在 CNB（cnb.cool），自动化（CI/更新任务）均在此配置（`.cnb.yml`）；
- GitHub 仓库仅作**备份**：CNB 定时任务更新 manifest 后自动同步到 GitHub，`push` 到 cnb 也会自动同步；
- 手动推送两个仓库：

```powershell
git push origin main   # cnb 主仓库
git push github main   # GitHub 备份
```

## GitHub 备份自动化（需配置一次）

`.cnb.yml` 中的自动同步依赖 CNB **密钥仓库**注入 GitHub 访问令牌（`GH_TOKEN`），不会明文写入本仓库。首次配置步骤：

1. **创建 GitHub PAT**：<https://github.com/settings/tokens>，勾选 `repo` 权限，生成后复制（只显示一次）。
2. **创建 CNB 密钥仓库**：在 CNB 新建一个私有仓库（如 `scoop-secrets`），添加文件 `backup.yml`，内容：
   ```yaml
   GH_TOKEN: <你的 GitHub PAT>
   ```
3. **授权本仓库引用**：在 `backup.yml` 顶部加入（CNB 密钥引用范围控制）：
   ```yaml
   allow_slugs: "catmono/scoop-violet"
   allow_branches:
     - main
   ```
4. **更新 `.cnb.yml`**：把文件头注释与两处 `imports` 中的占位符 `<你的组织>/<密钥仓库>` 替换为实际值，如：
   ```yaml
   imports:
     - https://cnb.cool/catmono/scoop-secrets/-/blob/main/backup.yml
   ```
5. 推送 `.cnb.yml` 后，手动触发一次流水线验证：更新任务或 `push` 事件应能成功推到 `github.com/locusyuri/scoop-violet`。

## 许可

本仓库内容（manifest、脚本、文档）遵循 [MIT](LICENSE) 许可；各应用自身的许可以其 manifest 中 `license` 字段为准。
