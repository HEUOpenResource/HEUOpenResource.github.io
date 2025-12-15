import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
MD_DIR = ROOT / "docs" / "resource"
CONFIG = ROOT / "contributors.json"

with open(CONFIG, "r", encoding="utf-8") as f:
    contributor_map = json.load(f)

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

def split_frontmatter(text: str):
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]

def parse_contributors(fm: str):
    lines = fm.splitlines()
    result = []
    i = 0

    while i < len(lines):
        if lines[i].startswith("contributors:"):
            i += 1
            while i < len(lines) and lines[i].startswith("  -"):
                line = lines[i].strip()
                if line.startswith("- "):
                    value = line[2:]
                    if value.startswith("name:"):
                        name = value.split(":", 1)[1].strip()
                        avatar = lines[i + 1].split(":", 1)[1].strip()
                        url = lines[i + 2].split(":", 1)[1].strip()
                        result.append({
                            "name": name,
                            "avatar": avatar,
                            "url": url,
                        })
                        i += 3
                        continue
                    else:
                        result.append(value)
                i += 1
        else:
            i += 1

    return result

def remove_contributors_block(fm: str):
    lines = fm.splitlines()
    out = []
    skip = False

    for line in lines:
        if line.startswith("contributors:"):
            skip = True
            continue
        if skip:
            if line.startswith("  "):
                continue
            skip = False
        out.append(line)

    return "\n".join(out)

def merge_contributors(old, new):
    seen_users = {c for c in old if isinstance(c, str)}
    seen_urls = {c["url"] for c in old if isinstance(c, dict)}

    merged = old[:]

    for c in new:
        if isinstance(c, str):
            if c not in seen_users:
                merged.append(c)
        else:
            if c["url"] not in seen_urls:
                merged.append(c)

    return merged

def dump_contributors(contributors):
    lines = ["contributors:"]
    for c in contributors:
        if isinstance(c, str):
            lines.append(f"  - {c}")
        else:
            lines.append(f"  - name: {c['name']}")
            lines.append(f"    avatar: {c['avatar']}")
            lines.append(f"    url: {c['url']}")
    return "\n".join(lines)

changed = 0

for md in MD_DIR.rglob("*.md"):
    key = md.stem
    if key not in contributor_map:
        continue

    text = md.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if not fm:
        continue

    old = parse_contributors(fm)
    merged = merge_contributors(old, contributor_map[key])

    if merged == old:
        continue

    fm_clean = remove_contributors_block(fm).rstrip()
    fm_clean += "\n" + dump_contributors(merged)

    md.write_text(f"---\n{fm_clean}\n---\n{body}", encoding="utf-8")
    changed += 1

print(f"添加非Github贡献者完成，更新 {changed} 个文件")
