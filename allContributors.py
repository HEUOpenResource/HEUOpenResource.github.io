import requests
import os
import json
import re
from pathlib import Path
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv()

# ======================
# 基本配置
# ======================
ROOT = Path(__file__).parent
OWNER = "HEUOpenResource"
REPO = "heu-icicles"
API = f"https://api.github.com/repos/{OWNER}/{REPO}/commits"

TARGET_MD = ROOT / "docs" / "resource" / "README.md"
CONFIG = ROOT / "contributors.json"

# ======================
# GitHub Token
# ======================
GITHUB_TOKEN = ""  # 建议走环境变量

if not GITHUB_TOKEN:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN 未设置")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# ======================
# 读取 contributors.json
# ======================
with open(CONFIG, "r", encoding="utf-8") as f:
    contributor_map = json.load(f)

# ======================
# Frontmatter 工具
# ======================
FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def split_frontmatter(text: str):
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def remove_field(fm: str, field: str):
    lines = fm.splitlines()
    out = []
    skip = False

    for line in lines:
        if line.startswith(f"{field}:"):
            skip = True
            continue
        if skip:
            if line.startswith("  "):
                continue
            skip = False
        out.append(line)

    return "\n".join(out)


# ======================
# 感谢块整体替换
# ======================
THANKS_BLOCK_RE = re.compile(
    r"感谢对本项目贡献的同学（排名不分先后）：.*?"
    r'<a href="https://github.com/HEUOpenResource/heu-icicles/graphs/contributors">\s*'
    r'<img src="https://contrib\.rocks/image\?repo=HEUOpenResource/heu-icicles" />\s*'
    r"</a>",
    re.S,
)

THANKS_REPLACEMENT = (
    "感谢对本项目贡献的同学（排名不分先后，非Github贡献者由自动化脚本获取，插入到末尾）：\n"
    '<Contributors :contributors="$frontmatter.allcontributors" />\n'
    "以及与我们有共同目标的你！"
)

# ======================
# GitHub Commit 贡献者（最早 → 最晚）
# ======================
def fetch_all_github_contributors():
    all_commits = []
    page = 1

    while True:
        resp = requests.get(
            API,
            params={"per_page": 100, "page": page},
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        all_commits.extend(data)
        page += 1

    users = OrderedDict()

    for c in reversed(all_commits):
        for field in ("author", "committer"):
            u = c.get(field)
            if not u:
                continue

            login = u.get("login")
            if not login:
                continue

            if login in ("dependabot[bot]", "web-flow"):
                continue

            users.setdefault(login, None)

    return list(users.keys())


# ======================
# contributors.json 中的额外贡献者
# ======================
def collect_extra_contributors(contributor_map):
    extra_github_users = OrderedDict()
    extra_non_github = OrderedDict()

    for items in contributor_map.values():
        for c in items:
            # GitHub 用户字符串
            if isinstance(c, str):
                extra_github_users.setdefault(c, None)

            # 非 GitHub 用户
            elif isinstance(c, dict):
                extra_non_github.setdefault(c["url"], c)

    return list(extra_github_users.keys()), list(extra_non_github.values())


# ======================
# allcontributors 生成
# ======================
def dump_allcontributors(github_users, extra_github_users, extra_non_github):
    seen = set()
    lines = ["allcontributors:"]

    # 1️⃣ GitHub commit 用户（最早 → 最晚）
    for u in github_users:
        if u not in seen:
            lines.append(f"  - {u}")
            seen.add(u)

    # 2️⃣ contributors.json 中的 GitHub 用户（补充）
    for u in extra_github_users:
        if u not in seen:
            lines.append(f"  - {u}")
            seen.add(u)

    # 3️⃣ 非 GitHub 用户
    for c in extra_non_github:
        lines.append(f"  - name: {c['name']}")
        lines.append(f"    avatar: {c['avatar']}")
        lines.append(f"    url: {c['url']}")

    return "\n".join(lines)


# ======================
# 主流程
# ======================
def generate():
    if not TARGET_MD.exists():
        raise RuntimeError(f"目标文件不存在：{TARGET_MD}")

    print("获取 GitHub Commit 贡献者...")
    github_users = fetch_all_github_contributors()

    extra_github_users, extra_non_github = collect_extra_contributors(contributor_map)

    allcontributors_block = dump_allcontributors(
        github_users,
        extra_github_users,
        extra_non_github,
    )

    text = TARGET_MD.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    # frontmatter
    if fm:
        fm_clean = remove_field(fm, "allcontributors").rstrip()
        fm_clean += "\n" + allcontributors_block
    else:
        fm_clean = allcontributors_block

    # 替换正文感谢块
    body = THANKS_BLOCK_RE.sub(THANKS_REPLACEMENT, body)

    TARGET_MD.write_text(
        f"---\n{fm_clean}\n---\n{body}",
        encoding="utf-8",
    )

    print("README 更新完成")


# ======================
# 执行
# ======================
generate()
