# Scoop Bucket Manifest（应用清单）JSON 格式规范

> 本文档参考 [ref/scoop-cn](https://github.com/duzyn/scoop-cn)（`ref/scoop-cn/bucket/` 下的应用清单）归纳总结，适用于本个人 bucket（scoop-violet）中的 manifest 编写。
>
> 每个应用对应一个 `<应用名>.json` 文件，放在 bucket 仓库根目录（即 `bucket/` 同级的 manifest 目录）下，文件名即安装时的应用名（不区分大小写）。

## 1. 顶层字段总览

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `version` | string | ✅ | 应用版本号，如 `"26.02"`、`"1.0.517"` |
| `description` | string | ✅ | 一句话应用描述 |
| `homepage` | string | ✅ | 应用官网 |
| `license` | string \| object | ✅ | SPDX 许可证标识，或 `{ identifier, url }` 对象 |
| `url` | string \| string[] | ✅ | 下载地址，可用 `#/文件名` 重命名 |
| `hash` | string \| string[] | ✅ | 与 `url` 一一对应的 SHA256 校验值 |
| `architecture` | object | 条件 | 按架构区分下载地址；无此字段时使用顶层 `url`/`hash` |
| `extract_dir` | string | 可选 | 解压后需进入的子目录 |
| `bin` | string \| array | 可选 | 加入 PATH 的可执行文件 |
| `shortcuts` | array | 可选 | 开始菜单快捷方式 |
| `persist` | string \| string[] | 可选 | 需要持久化的目录/文件（更新时保留） |
| `depends` | string \| string[] | 可选 | 安装本应用前必须先安装的依赖 |
| `suggest` | object | 可选 | 建议安装的可选应用 |
| `env_add_path` | string \| string[] | 可选 | 追加到 PATH 的目录 |
| `env_set` | object | 可选 | 设置的环境变量 |
| `notes` | string \| string[] | 可选 | 安装后展示给用户的提示 |
| `innosetup` | boolean | 可选 | `true` 表示用 Inno Setup 解包方式安装 |
| `installer` | object | 可选 | 自定义安装器（`script` 或 `file`+`args`） |
| `uninstaller` | object | 可选 | 自定义卸载器（`script`） |
| `pre_install` | string \| string[] | 可选 | 安装前执行的 PowerShell 脚本 |
| `post_install` | string \| string[] | 可选 | 安装后执行的 PowerShell 脚本 |
| `pre_uninstall` | string \| string[] | 可选 | 卸载前执行的 PowerShell 脚本 |
| `post_uninstall` | string \| string[] | 可选 | 卸载后执行的 PowerShell 脚本 |
| `checkver` | string \| object | 推荐 | 检查新版本的规则（配合 `autoupdate` 自动更新） |
| `autoupdate` | object | 推荐 | 自动更新时生成 url/hash 的模板 |

## 2. 基础字段

### 2.1 version

应用版本号。纯字符串，不要带 `v` 前缀，不要使用数学表达式。

```json
"version": "26.02"
```

### 2.2 description / homepage

```json
"description": "A multi-format file archiver with high compression ratios.",
"homepage": "https://www.7-zip.org"
```

### 2.3 license

两种写法：

**简写**（SPDX 标识，参考 <https://spdx.org/licenses/>）：

```json
"license": "GPL-2.0-or-later"
```

**完整对象**（含许可证原文链接）：

```json
"license": {
    "identifier": "BSD-2-Clause, BSD-3-Clause, LGPL-2.1-or-later",
    "url": "https://www.7-zip.org/license.txt"
}
```

专有/免费软件用 `"Proprietary"`、`"Freeware"`、`"Shareware"` 等非 SPDX 标识：

```json
"license": {
    "identifier": "Proprietary",
    "url": "https://www.sweetscape.com/010editor/manual/License.htm"
}
```

### 2.4 url 与 hash

单文件下载：

```json
"url": "https://3rvx.com/releases/3RVX-2.9.2.zip",
"hash": "7d6c0d3c94d4ff1755cbdf3eb9b235a16084588c1e31759bd221617e5ac166d3"
```

多文件下载（`url` 与 `hash` 数组一一对应）：

```json
"url": [
    "http://www.7ztm.de/download.php?file=7zTM_2.1.7z#/main.7z",
    "http://www.7ztm.de/download.php?file=7zTM_2.1.1_hotfix.7z#/hotfix.7z"
],
"hash": [
    "d1bb8aa1b5f49c39c606604964fe616009b4598c4f3c02e6fff808fa9d4da15e",
    "09eb32ccfed696ec2030dd87779ac03a1233897c7ef83e5c7f81f1f696b811e0"
]
```

要点：

- 默认 SHA256（64 位十六进制小写）。其他算法需加前缀，如 `"sha1:bd311b6891449678ac69da698674e68bc1557fb4"`（见 `0ad.json`）。
- 下载地址后跟 `#/文件名` 可把下载的文件重命名为安装脚本中使用的名字，例如：

```json
"url": "https://gadgetpack.net/dl_420/GadgetPackSetup.msi#/setup.msi_",
```

（`_` 结尾避免 Scoop 自动识别为可安装格式，由 `installer.script` 自行处理。）

- 国内加速镜像（如本参考库使用的 `https://gh-proxy.org/`）可直接拼在原始地址前。

### 2.5 architecture（按架构区分）

当不同架构下载不同文件时使用。支持 `64bit`、`32bit`、`arm64` 等键，每个键内部包含 `url`、`hash`、可选 `extract_dir` / `pre_install`：

```json
"architecture": {
    "64bit": {
        "url": "https://download.sweetscape.com/010EditorWin64Portable16.0.4.zip",
        "hash": "f4512b246c5629fd080d41b5c866ced86a1400480c10fda0f5240008b2cd2675",
        "extract_dir": "010EditorWin64Portable"
    },
    "32bit": {
        "url": "https://download.sweetscape.com/010EditorWin32Portable16.0.4.zip",
        "hash": "addac0a09e359c92b5ce5818c4147eb6c36cbcc15a4019e4df6a57c03a1461f3",
        "extract_dir": "010EditorWin32Portable"
    }
}
```

注意：**不能用 `x64`/`x86`，必须用 `64bit`/`32bit`**。无 `architecture` 字段时顶层 `url`/`hash` 对所有架构生效。

## 3. 可执行文件与快捷方式

### 3.1 bin（加入 PATH）

单个可执行文件：

```json
"bin": "3RVX.exe"
```

多个可执行文件：

```json
"bin": [
    "7z.exe",
    "7zG.exe",
    "7zFM.exe"
]
```

重命名命令（`[原文件, 命令名]`）：

```json
"bin": [
    ["AppData\\010Editor.exe", "010editor"]
]
```

支持 `.bat` / `.cmd` / `.ps1` 脚本（如 `"bin\\allure.bat"`），也支持子目录路径。

### 3.2 shortcuts（开始菜单快捷方式）

格式为 `[可执行文件路径, 快捷方式名称（可用 `\\` 分层级）]`：

```json
"shortcuts": [
    ["7zFM.exe", "7-Zip\\7-Zip File Manager"],
    ["7-zip.chm", "7-Zip\\7-Zip Help"]
]
```

### 3.3 persist（持久化目录/文件）

更新应用时保留这些目录或文件（首次安装时从安装目录复制到 `persist` 目录并做链接）：

```json
"persist": [
    "AppData\\Config",
    "AppData\\Data",
    "010 Scripts",
    "010 Templates"
]
```

```json
"persist": "Settings.xml"
```

注意路径用 `\\` 分隔子目录，支持带空格的目录名。

## 4. 依赖与建议

### 4.1 depends（强制依赖）

```json
"depends": "ffmpeg"
```

多个依赖用数组：

```json
"depends": ["git", "7zip"]
```

### 4.2 suggest（建议安装）

键为提示文字，值为应用名：

```json
"suggest": {
    "86Box ROMs": "86box-roms"
}
```

## 5. 环境变量

### 5.1 env_add_path（追加 PATH）

```json
"env_add_path": "Scripts"
```

```json
"env_add_path": ["bin", "lib"]
```

值为安装目录（`$dir`）下的相对路径；`"."` 表示安装目录本身。

### 5.2 env_set（设置环境变量）

```json
"env_set": {
    "ALLURE_HOME": "$dir"
}
```

值支持 `$dir`、`$persist_dir` 等变量占位符。

## 6. 安装与卸载脚本

### 6.1 installer / uninstaller

**script 方式**（直接执行 PowerShell 片段，`$dir` 为安装目录）：

```json
"installer": {
    "script": "Start-Process -FilePath \"$dir\\setup.exe\" -ArgumentList \"/S\", \"/D=$dir\" -Wait"
}
```

script 也可为多行数组：

```json
"installer": {
    "script": [
        "Start-Process msiexec -ArgumentList @('/i', \"`\"$dir\\setup.msi_`\"\", '/qn') -Wait -Verb RunAs | Out-Null"
    ]
}
```

**file + args 方式**（指定安装程序与参数，`$dir` 作为工作目录）：

```json
"installer": {
    "file": "setup.exe",
    "args": ["/S", "/D=$dir"]
}
```

卸载同理：

```json
"uninstaller": {
    "script": "Start-Process msiexec -ArgumentList @('/x', \"`\"$dir\\setup.msi_`\"\", '/qn') -Wait -Verb RunAs | Out-Null"
}
```

### 6.2 innosetup

`true` 表示下载的是 Inno Setup 安装器，Scoop 用内置解包方式提取内容，无需执行安装程序：

```json
"innosetup": true,
"extract_dir": "{code_GetDestDir}"
```

### 6.3 pre_install / post_install / pre_uninstall / post_uninstall

均为字符串或字符串数组（每行一段 PowerShell）：

```json
"pre_install": [
    "if (!(is_admin)) { error \"$app requires admin rights to $cmd\"; break }",
    "Start-Process \"$dir\\setup.exe\" -Wait -Verb 'RunAs' -WindowStyle 'Hidden' -Args '/silent'"
],
"pre_uninstall": [
    "if (!(is_admin)) { error \"$app requires admin rights to $cmd\"; break }",
    "Start-Process \"$dir\\setup.exe\" -Wait -Verb 'RunAs' -WindowStyle 'Hidden' -Args @('/silent', '/uninstall'); Start-Sleep -Seconds 2"
]
```

```json
"post_install": "Remove-Item \"$dir\\$fname\""
```

```json
"post_uninstall": "Remove-Item \"$env:APPDATA\\aider-desk\" -Recurse -Force"
```

### 6.4 脚本中可用的变量

| 变量 | 含义 |
| --- | --- |
| `$dir` | 应用安装目录 |
| `$persist_dir` | 持久化目录 |
| `$fname` | 当前下载文件名 |
| `$version` | manifest 中的版本号 |
| `$app` | 应用名 |
| `$global` | 是否为全局安装（`scoop install -g`） |
| `$cmd` | 当前执行命令（install/uninstall 等） |
| `$bucketsdir` | buckets 根目录 |
| `is_admin` | 是否管理员权限（函数） |
| `error` | 输出错误并终止（函数） |
| `appdir <app> <global>` | 获取指定应用的安装目录（函数） |

## 7. checkver 与 autoupdate（自动更新）

配合使用：`checkver` 用于检测新版本号，`autoupdate` 用新版本号重写 `url`/`hash`。运行 `scoop update <应用名>`（或 `checkver.ps1` 全库检查）触发。

### 7.1 checkver 常见写法

**GitHub Releases 简写**（自动匹配 GitHub 最新 release 的版本号）：

```json
"checkver": "github"
```

**GitHub 仓库页**：

```json
"checkver": {
    "github": "https://github.com/ip7z/7zip"
}
```

**抓取网页 + 正则**：

```json
"checkver": {
    "url": "https://www.sweetscape.com/download/010editor/",
    "regex": "(?s)Portable Version.*Version: ([\\d.]+)"
}
```

**GitHub API + jsonpath + 正则**（匹配 release 资源名并捕获多个版本片段）：

```json
"checkver": {
    "github": "https://api.github.com/repos/86Box/86Box/releases/latest",
    "jsonpath": "$.assets[*].browser_download_url",
    "regex": "v(?<version>[\\d.]+)/86Box-Windows-64-b(?<build>\\d+)\\.zip"
}
```

捕获组会生成 `$matchVersion`、`$matchBuild` 等变量供 `autoupdate` 使用。

### 7.2 autoupdate

`url` 模板中用 `$version` 占位新版本号：

```json
"autoupdate": {
    "url": "https://3rvx.com/releases/3RVX-$version.zip"
}
```

`$cleanVersion` 为去点版本号（如 `26.02` → `2602`）：

```json
"autoupdate": {
    "url": "https://gadgetpack.net/dl_$cleanVersion/GadgetPackSetup.msi#/setup.msi_"
}
```

按架构区分（与 `architecture` 结构对应）：

```json
"autoupdate": {
    "architecture": {
        "64bit": {
            "url": "https://gh-proxy.org/https://github.com/ip7z/7zip/releases/download/$version/7z$cleanVersion-x64.msi"
        },
        "32bit": {
            "url": "https://gh-proxy.org/https://github.com/ip7z/7zip/releases/download/$version/7z$cleanVersion.msi"
        }
    }
}
```

使用 `checkver` 捕获的命名组：

```json
"autoupdate": {
    "architecture": {
        "64bit": {
            "url": "https://gh-proxy.org/https://github.com/86Box/86Box/releases/download/v$matchVersion/86Box-Windows-64-b$matchBuild.zip"
        }
    }
}
```

自动计算 hash（从网页/文件抓取，`$sha256` 匹配抓取内容中的校验值）：

```json
"autoupdate": {
    "architecture": {
        "64bit": {
            "url": "https://download.sweetscape.com/010EditorWin64Portable$version.zip",
            "hash": {
                "url": "https://www.sweetscape.com/download/010EditorWin64Portable.zip.SHA256.txt",
                "regex": "$sha256"
            }
        }
    }
}
```

## 8. notes（安装提示）

安装完成后展示给用户：

```json
"notes": "This is a free 30-day trial version. Please buy a copy of it for furthur evaluation."
```

多条提示用数组：

```json
"notes": [
    "To register the context menu entry, please execute the following command:",
    "reg import \"$dir\\install-context.reg\""
]
```

## 9. 完整示例

### 9.1 最简单形式（单文件、单架构）

```json
{
    "version": "2.9.2",
    "description": "Skinnable volume controller and OSD.",
    "homepage": "https://3rvx.com/",
    "license": "BSD-2-Clause",
    "url": "https://3rvx.com/releases/3RVX-2.9.2.zip",
    "hash": "7d6c0d3c94d4ff1755cbdf3eb9b235a16084588c1e31759bd221617e5ac166d3",
    "bin": "3RVX.exe",
    "shortcuts": [
        ["3RVX.exe", "3RVX"]
    ],
    "persist": "Settings.xml",
    "autoupdate": {
        "url": "https://3rvx.com/releases/3RVX-$version.zip"
    }
}
```

### 9.2 多架构 + 自动更新

```json
{
    "version": "16.0.4",
    "description": "Professional text and hex editor with Binary Templates technology.",
    "homepage": "https://www.sweetscape.com/010editor/",
    "license": {
        "identifier": "Proprietary",
        "url": "https://www.sweetscape.com/010editor/manual/License.htm"
    },
    "architecture": {
        "64bit": {
            "url": "https://download.sweetscape.com/010EditorWin64Portable16.0.4.zip",
            "hash": "f4512b246c5629fd080d41b5c866ced86a1400480c10fda0f5240008b2cd2675",
            "extract_dir": "010EditorWin64Portable"
        },
        "32bit": {
            "url": "https://download.sweetscape.com/010EditorWin32Portable16.0.4.zip",
            "hash": "addac0a09e359c92b5ce5818c4147eb6c36cbcc15a4019e4df6a57c03a1461f3",
            "extract_dir": "010EditorWin32Portable"
        }
    },
    "bin": [
        ["AppData\\010Editor.exe", "010editor"]
    ],
    "shortcuts": [
        ["AppData\\010Editor.exe", "010 Editor"]
    ],
    "persist": [
        "AppData\\Config",
        "AppData\\Data",
        "AppData\\Plugins",
        "010 Scripts",
        "010 Templates",
        "AppData\\Temp"
    ],
    "checkver": {
        "url": "https://www.sweetscape.com/download/010editor/",
        "regex": "(?s)Portable Version.*Version: ([\\d.]+)"
    },
    "autoupdate": {
        "architecture": {
            "64bit": {
                "url": "https://download.sweetscape.com/010EditorWin64Portable$version.zip",
                "hash": {
                    "url": "https://www.sweetscape.com/download/010EditorWin64Portable.zip.SHA256.txt",
                    "regex": "$sha256"
                }
            },
            "32bit": {
                "url": "https://download.sweetscape.com/010EditorWin32Portable$version.zip",
                "hash": {
                    "url": "https://www.sweetscape.com/download/010EditorWin32Portable.zip.SHA256.txt",
                    "regex": "$sha256"
                }
            }
        }
    }
}
```

## 10. 编写约定与校验

1. **JSON 必须合法**：无注释、无尾逗号，使用 UTF-8 编码，2 空格缩进（参考仓库的 `.editorconfig`）。
2. **hash 与 url 严格对应**：顶层数组时一一对应；`architecture` 下各架构自洽。
3. **版本号不带 `v` 前缀**；但下载 URL 中的 `v` 由 `autoupdate` 模板自行保留。
4. **路径分隔符**：manifest 内子目录一律用 `\\`（如 `"AppData\\Config"`）。
5. **校验命令**：
   ```powershell
   scoop install <应用名>   # 实际安装验证
   scoop update <应用名>    # 触发 checkver/autoupdate 验证
   ```
   也可用任何 JSON 解析器做静态校验（如 `bunx jsonlint`、PowerShell 的 `ConvertFrom-Json`）。

## 11. 本仓库目录结构约定

本仓库（scoop-violet）按 scoop bucket 标准布局组织：

| 目录 | 用途 | 说明 |
| --- | --- | --- |
| `bucket/` | **manifest（`<应用名>.json`）存放目录** | 新增应用时在此目录写 JSON，文件名即应用名 |
| `scripts/` | 安装辅助脚本 | 供 manifest 的 `pre_install`/`post_install` 等字段调用，按应用分子目录（如 `scripts/atomcode/`） |
| `bin/` | 本仓库自带的辅助可执行文件/脚本 | 仓库维护工具等 |
| `wiki/` | 文档 | `SPEC.md` 即本规范 |
| `ref/` | 参考材料（只读） | 外部仓库克隆（scoop-cn、atomcode 源码），仅作调研参考，不纳入 bucket |

约定：

1. **新应用一律在 `bucket/` 下写 manifest**，不要放在仓库根目录。
2. **脚本引用路径**：manifest 中引用 `scripts/` 下的脚本时，用 `"$bucketsdir\\$bucket\\scripts\\<应用>\\<脚本>.ps1"` 形式（`$bucket` 为安装时的 bucket 名，如 `scoop bucket add violet <url>` 后 `$bucket` 为 `violet`）。示例（见 `bucket/atomcode.json`）：
   ```json
   "post_install": "& \"$bucketsdir\\$bucket\\scripts\\atomcode\\disable-auto-update.ps1\""
   ```
3. **应用自带脚本**：每个应用若有配套脚本，放在 `scripts/<应用名>/` 下，与 manifest 同名应用对应。
4. **post_install 中的用户态配置修改**：如需修改 `%USERPROFILE%` 下的用户配置（如关闭应用自更新），务必只做行级修改/追加，禁止整体覆盖（配置文件可能含 API 密钥等敏感信息），并优先遵循应用自身的 `$ATOMCODE_HOME` 等环境变量约定。
5. **卸载行为**：manifest 默认不写 `uninstaller`/`post_uninstall` 清理用户数据（如 `~/.atomcode`），交由用户自行决定；如官方卸载脚本会删除用户数据，切勿在 manifest 中调用。
