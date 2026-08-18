#!/usr/bin/env python3
"""通用 manifest 更新脚本（数据驱动）。

遍历 bucket/*.json，依据每个 manifest 自带的 checkver / autoupdate 配置
检查最新版本并更新 version / url / hash。新增软件只需在 manifest 中写好
checkver / autoupdate（见 wiki/SPEC.md），无需为本软件编写专用脚本。

支持（与 wiki/SPEC.md 一致）：
- checkver:
    "github"                            -> 从 homepage 推断 repo，查 GitHub 最新 release tag
    {"github": "<repo 或 api url>"}     -> 显式指定 repo 或 API 地址
    {"url": ..., "regex": ...}                       -> 网页正则提取版本
    {"url": ..., "jsonpath": ..., "regex": ...}      -> JSON + 正则（regex 可省略）
- autoupdate:
    {"url": "..."}                                      -> 顶层 URL 模板
    {"architecture": {"64bit": {"url": ..., "hash": ...}, "32bit": {...}, ...}}
- 模板变量: $version $cleanVersion $match<Name>（$match<Name> 来自 checkver regex 命名组）
- hash 取值: 字符串（不更新） | {"url":..., "jsonpath":...} | {"url":..., "regex":...}
  其中 regex 为 "$sha256" 时取抓取内容整体（strip 后第一段）。

用法:
    python3 scripts/update.py [--dir bucket] [--dry-run]
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

GITHUB_API = "https://api.github.com/repos"


# ── 基础工具 ────────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = 30) -> str:
    """抓取 URL 文本。"""
    req = urllib.request.Request(url, headers={"User-Agent": "scoop-violet-updater"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def json_path(data, expr: str):
    """简化 JSONPath：仅支持 $.a.b 与 $.a['b'] / $['a'] 形式。"""
    if not expr.startswith("$"):
        raise ValueError(f"不支持的 jsonpath（需以 $ 开头）: {expr}")
    body = expr[1:]
    parts = re.findall(r"\.([A-Za-z0-9_\-]+)|\[\s*'([^']*)'\s*\]", body)
    if not parts:
        return data
    cur = data
    for dot, bracket in parts:
        cur = cur[dot if dot else bracket]
    return cur


def version_key(v: str) -> tuple:
    """版本字符串 -> 可比较元组（数字段不足补 0；忽略预发布后缀）。"""
    nums = re.findall(r"\d+", v)
    key = tuple(int(n) for n in nums)
    return key + (0,) * (6 - len(key))


def is_newer(latest: str, current: str) -> bool:
    return version_key(latest) > version_key(current)


def render(template: str, version: str, clean: str, matches: dict) -> str:
    """替换 autoupdate 模板变量。"""
    s = template.replace("$version", version).replace("$cleanVersion", clean)
    for name, val in matches.items():
        s = s.replace(f"$match{name}", val)
    return s


def clean_version(v: str) -> str:
    """去点版本号：5.0.6 -> 506。"""
    return re.sub(r"[^\d]", "", v)


# ── checkver 解析 ───────────────────────────────────────────────────────

def check_latest(manifest: dict) -> tuple:
    """返回 (最新版本号, 命名组字典)。不支持时抛 ValueError。"""
    checkver = manifest.get("checkver")
    if not checkver:
        raise ValueError("manifest 缺少 checkver")

    if isinstance(checkver, str):
        if checkver == "github":
            repo = _repo_from_homepage(manifest)
            if not repo:
                raise ValueError('checkver: "github" 但无法从 homepage 推断 repo')
            url = f"{GITHUB_API}/{repo}/releases/latest"
            data = json.loads(fetch(url))
            tag = data.get("tag_name", "")
            return tag.lstrip("v"), {}
        raise ValueError(f"不支持的 checkver 字符串: {checkver}")

    # dict 形式
    if checkver.get("github"):
        gh = checkver["github"]
        if gh.startswith("http"):
            url = gh
        else:
            url = f"{GITHUB_API}/{gh}/releases/latest"
        data = json.loads(fetch(url))
        tag = data.get("tag_name", "")
        return tag.lstrip("v"), {}

    url = checkver.get("url")
    if not url:
        raise ValueError("checkver 缺少 url")
    content = fetch(url)

    regex = checkver.get("regex")
    if regex:
        m = re.search(regex, content)
        if not m:
            raise ValueError(f"checkver regex 未匹配: {regex}")
        named = {k: v for k, v in m.groupdict().items() if v is not None}
        version = named.get("version") or (m.group(1) if m.groups() else m.group(0))
        return version, named

    # 无 regex：按 jsonpath 取值
    if checkver.get("jsonpath"):
        data = json.loads(content)
        return str(json_path(data, checkver["jsonpath"])).lstrip("v"), {}

    raise ValueError("checkver 需提供 url+regex 或 url+jsonpath")


def _repo_from_homepage(manifest: dict) -> str:
    hp = (manifest.get("homepage") or "").strip("/")
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+/[^/]+)", hp)
    return m.group(1) if m else ""


# ── autoupdate 应用 ─────────────────────────────────────────────────────

def _fetch_hash(hash_conf, version: str, clean: str, matches: dict) -> str:
    """按 hash 配置抓取校验值。url 支持 $version/$cleanVersion/$match<Name> 模板。"""
    if isinstance(hash_conf, str):
        return hash_conf  # 固定值，无法自动更新
    url = hash_conf.get("url")
    if not url:
        raise ValueError("autoupdate hash 缺少 url")
    url = render(url, version, clean, matches)
    content = fetch(url)
    if hash_conf.get("jsonpath"):
        data = json.loads(content)
        return str(json_path(data, hash_conf["jsonpath"]))
    regex = hash_conf.get("regex", "")
    if regex == "$sha256":
        return content.strip().split()[0]
    regex = render(regex, version, clean, matches)  # regex 同样支持模板变量
    m = re.search(regex, content)
    if not m:
        raise ValueError(f"autoupdate hash regex 未匹配: {regex}")
    return m.group(1) if m.groups() else m.group(0)


def _apply_entry(entry: dict, version: str, clean: str, matches: dict):
    """渲染单条 url/extract_dir/hash 配置（可能是顶层，或 architecture 下某架构）。"""
    if entry.get("url"):
        entry["url"] = render(entry["url"], version, clean, matches)
    if entry.get("extract_dir"):
        entry["extract_dir"] = render(entry["extract_dir"], version, clean, matches)
    hash_conf = entry.get("hash")
    if isinstance(hash_conf, dict):
        entry["hash"] = _fetch_hash(hash_conf, version, clean, matches)


def apply_autoupdate(manifest: dict, version: str, matches: dict):
    """按 autoupdate 配置改写 manifest 的 version/url/hash/extract_dir。

    关键：autoupdate 块是模板，渲染结果必须**写回 manifest 的顶层或
    architecture 对应块**——scoop 安装时读的是 architecture 里的 url/hash。
    """
    autoupdate = manifest.get("autoupdate")
    if not autoupdate:
        raise ValueError("manifest 缺少 autoupdate")

    clean = clean_version(version)

    def _sync(src: dict, dst: dict):
        for k in ("url", "hash", "extract_dir"):
            if k in src:
                dst[k] = src[k]

    if autoupdate.get("url") or autoupdate.get("hash") or autoupdate.get("extract_dir"):
        _apply_entry(autoupdate, version, clean, matches)
        _sync(autoupdate, manifest)

    for arch, entry in (autoupdate.get("architecture") or {}).items():
        if isinstance(entry, dict):
            _apply_entry(entry, version, clean, matches)
            arch_manifest = manifest.setdefault("architecture", {}).setdefault(arch, {})
            _sync(entry, arch_manifest)

    manifest["version"] = version


# ── 主流程 ──────────────────────────────────────────────────────────────

def update_one(path: Path, dry_run: bool) -> str:
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)

    current = manifest.get("version", "")
    try:
        latest, matches = check_latest(manifest)
    except Exception as e:  # noqa: BLE001 —— 单应用失败不应中断全部
        return f"FAIL  {path.name}: {e}"

    if not is_newer(latest, current):
        return f"OK    {path.name}: up to date ({current})"

    try:
        apply_autoupdate(manifest, latest, matches)
    except Exception as e:  # noqa: BLE001
        return f"FAIL  {path.name}: {e}"

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=4)
            f.write("\n")
    return f"UPDATE {path.name}: {current} -> {latest}"


def main(argv) -> int:
    args = [a for a in argv if not a.startswith("-")]
    target = Path(args[1]) if len(args) > 1 else Path("bucket")
    dry_run = "--dry-run" in argv

    files = sorted(target.glob("*.json"))
    if not files:
        print(f"未找到 manifest: {target}/*.json")
        return 1

    ok = fail = 0
    for path in files:
        line = update_one(path, dry_run)
        print(line)
        if line.startswith("FAIL"):
            fail += 1
        else:
            ok += 1

    print(f"\n{ok} 个应用处理完成，{fail} 个失败" + ("（dry-run，未写回）" if dry_run else ""))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
