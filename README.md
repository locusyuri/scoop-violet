# scoop-violet

个人的 Scoop bucket，收录自用软件清单（manifest）。

- **主仓库（自动化）**：<https://cnb.cool/catmono/scoop-violet>
- **备份仓库**：<https://github.com/locusyuri/scoop-violet>

## 收录应用

| 应用 | 版本 | 说明 |
| --- | --- | --- |
| [atomcode](https://atomgit.com/atomgit_atomcode/atomcode) | 5.0.6 | 开源终端 AI 编程助手（安装时自动关闭其内置自更新，交由 scoop 统一管理） |

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
- GitHub 仓库仅作备份，不做自动化；
- 两个仓库都推送时：

```powershell
git push origin main   # cnb 主仓库
git push github main   # GitHub 备份
```

## 许可

本仓库内容（manifest、脚本、文档）遵循 [MIT](LICENSE) 许可；各应用自身的许可以其 manifest 中 `license` 字段为准。
