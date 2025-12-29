import os
import requests
from dotenv import load_dotenv

OWNER = "HEUOpenResource"
REPO = "heu-icicles"
BRANCH = "main"
load_dotenv()

OUTPUT_DIR = "docs/resource"
# 1️⃣ 本地可直接写死；留空（None / ""）则自动从环境变量读取
GITHUB_TOKEN = ""  # 或 None

if not GITHUB_TOKEN:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 2️⃣ 可选：最终校验（没有 token 就明确失败）
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN 未设置（本地变量与环境变量均为空）")
MAX_README_COUNT = 0
DOWNLOAD_ROOT_README = 1
DOWNLOAD_FROM_GITHUB = 1

API_ROOT = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

TAIL_CONTENT = (
    "\n\n## 本科目贡献者\n"
    '<Contributors :contributors="$frontmatter.contributors" />\n'
)

ROOT_TAIL_CONTENT = (
    "\n\n## README维护者\n"
    '<Contributors :contributors="$frontmatter.contributors" />\n'
)


def get_headers():
    if GITHUB_TOKEN:
        return {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    return {"Accept": "application/vnd.github+json"}


HEADERS = get_headers()


def get_root_dirs():
    resp = requests.get(API_ROOT, headers=HEADERS)
    resp.raise_for_status()
    return [
        item["name"]
        for item in resp.json()
        if item["type"] == "dir" and item["name"] != ".github"
    ]


def find_readme(path=""):
    url = f"{API_ROOT}/{path}" if path else API_ROOT
    resp = requests.get(url, headers=HEADERS, params={"ref": BRANCH})
    if resp.status_code != 200:
        return None

    for item in resp.json():
        if item["type"] == "file" and item["name"].lower() == "readme.md":
            return item["download_url"]
    return None


def get_contributors(path, max_pages=10):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits"
    contributors = []
    seen = set()

    for page in range(1, max_pages + 1):
        params = {
            "path": path,
            "sha": BRANCH,
            "per_page": 100,
            "page": page,
        }
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            break

        commits = resp.json()
        if not commits:
            break  # 没有更多了

        for commit in commits:
            if commit.get("author") and commit["author"].get("login"):
                name = commit["author"]["login"]
            else:
                name = commit["commit"]["author"]["name"]

            if name and name not in seen:
                seen.add(name)
                contributors.append(name)

    return contributors


def write_markdown(filename, content, permalink, title=None, contributors=None, tail=None):
    frontmatter = ["---"]
    if title:
        frontmatter.append(f"title: {title}")
    frontmatter.append(f"permalink: {permalink}")
    if contributors:
        frontmatter.append("contributors:")
        for c in contributors:
            frontmatter.append(f"  - {c}")
    frontmatter.append("---\n")
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter))
        f.write(content)
        if tail:
            f.write(tail)


def load_local_file(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def create_download_link_github(path):
    return f"https://raw.githubusercontent.com/HEUOpenResource/heu-icicles/main/{path}"


def create_download_link_ghproxy(path):
    return f"https://ghproxy.net/https://raw.githubusercontent.com/HEUOpenResource/heu-icicles/main/{path}"


def create_download_link_kokomi0728(path):
    return f"https://ghproxy.kokomi0728.eu.org/https://raw.githubusercontent.com/HEUOpenResource/heu-icicles/main/{path}"


def create_download_link_heu(path):
    return f"https://ghproxy.heu.us.kg/https://raw.githubusercontent.com/HEUOpenResource/heu-icicles/main/{path}"


def format_file_size(file_size_bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while file_size_bytes >= 1024 and unit_index < len(units) - 1:
        file_size_bytes /= 1024
        unit_index += 1
    return "{:.2f} {}".format(file_size_bytes, units[unit_index])


def generate_markdown_recursive(path=""):
    """
    递归生成目录下的 Markdown 文件列表
    - 不在开头添加目录名标题
    - 子目录标题从 H3 开始
    """
    url = f"{API_ROOT}/{path}" if path else API_ROOT
    resp = requests.get(url, headers=HEADERS, params={"ref": BRANCH})
    if resp.status_code != 200:
        return ""

    items = resp.json()
    markdown_content = ""

    # 分离文件和子目录
    files = [item for item in items if item["type"] == "file" and item["name"].lower() != "readme.md"]
    dirs = [item for item in items if item["type"] == "dir"]

    # 文件表格
    if files:
        markdown_content += "资料 | 大小 | Github下载 | 备用1 | 备用2 | 备用3\n"
        markdown_content += "|:---:|:---:|:---:|:---:|:---:|:---:\n"
        for f in files:
            f_path = f"{path}/{f['name']}" if path else f['name']
            github_link = create_download_link_github(f_path)
            ghproxy_link = create_download_link_ghproxy(f_path)
            kokomi_link = create_download_link_kokomi0728(f_path)
            heu_link = create_download_link_heu(f_path)
            file_size = format_file_size(f.get("size", 0))
            markdown_content += f"{f['name']} | {file_size} | [下载]({github_link}) | [下载]({ghproxy_link}) | [下载]({kokomi_link}) | [下载]({heu_link})\n"

    # 子目录递归处理，标题从 H3 开始
    for d in dirs:
        d_path = f"{path}/{d['name']}" if path else d['name']
        level = d_path.count('/') + 1  # H3开始
        title = d['name']
        markdown_content += f"\n{'#' * level} {title}\n\n"
        markdown_content += generate_markdown_recursive(d_path)

    return markdown_content


def process_dir_readme(dir_name):
    filename = f"{dir_name}.md"
    print(f"开始处理：{dir_name}/README.md")

    if DOWNLOAD_FROM_GITHUB:
        download_url = find_readme(dir_name)
        if not download_url:
            print(f"⚠️ 未找到 {dir_name}/README.md，使用空 README\n")
            content = ""
        else:
            content = requests.get(download_url, headers=HEADERS).text
    else:
        content = load_local_file(filename)
        if not content:
            print(f"❌ 本地 {filename} 不存在\n")
            return False

    # 递归生成目录下文件 Markdown（不添加目录名作为标题）
    recursive_md = generate_markdown_recursive(dir_name)
    if recursive_md:
        content += "\n\n" + recursive_md

    contributors = get_contributors(dir_name)

    write_markdown(
        filename=filename,
        content=content,
        permalink=f"/{dir_name}/",
        contributors=contributors,
        tail=TAIL_CONTENT
    )

    print(f"✅ {filename} 写入完成\n")
    return True


def process_root_readme():
    filename = "README.md"
    print("开始处理：仓库根目录 README.md")

    if DOWNLOAD_FROM_GITHUB:
        download_url = find_readme()
        if not download_url:
            print("❌ 未找到根 README.md")
            return False
        content = requests.get(download_url, headers=HEADERS).text
    else:
        content = load_local_file(filename)
        if not content:
            print("❌ 本地根 README.md 不存在")
            return False

    contributors = get_contributors("README.md")

    write_markdown(
        filename=filename,
        content=content,
        title="介绍",
        permalink="/resource/",
        contributors=contributors,
        tail=ROOT_TAIL_CONTENT
    )

    print("✅ 根 README.md 写入完成\n")
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("===== README 处理开始 =====\n")

    if DOWNLOAD_ROOT_README:
        process_root_readme()

    count = 0
    for d in get_root_dirs():
        if MAX_README_COUNT > 0 and count >= MAX_README_COUNT:
            print("已达到 MAX_README_COUNT 限制，停止处理\n")
            break
        if process_dir_readme(d):
            count += 1

    print("===== README 处理完成 =====")


if __name__ == "__main__":
    main()
