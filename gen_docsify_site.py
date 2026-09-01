#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Docsify 站点导航(_sidebar.md)与首页(README.md)。

用法：python3 gen_docsify_site.py
- 递归遍历 docs/level_up 下全部 .md（含 sources/ 等子目录），按章节生成左侧目录；
  每个文档取首行 H1 作链接标题，子目录作为分组。
- 首页 README.md 含两个数据看板入口(新标签页打开)与各章说明。
重新运行即可在增删文档后刷新导航。
"""
import os, re, urllib.parse

ROOT = "docs/level_up"
SIDEBAR = "docs/_sidebar.md"
README = "docs/README.md"

DASHBOARDS = [
    ("深圳中考数学六年考卷分析-知识点看板.html", "📊 知识点分块看板（六年考卷·双口径对照）"),
    ("一页纸-差生提分路径.html", "📄 一页纸·差生提分路径"),
]

FOLDER_TITLE = {"sources": "📁 研究素材", "assets": "📁 素材"}


def chapter_title(d: str) -> str:
    return re.sub(r'^\d+[-_ ]*', '', d)


def folder_title(d: str) -> str:
    return FOLDER_TITLE.get(d, f"📁 {d}")


def first_h1(path: str) -> str:
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'^#\s+(.*)', line)
                if m:
                    return m.group(1).strip()
    except Exception:
        pass
    return None


def label_of(path: str, fn: str) -> str:
    return first_h1(path) or fn[:-3]


# ---- 遍历章节（递归） ----
sb = ["* [🏠 首页 / 看板入口](README.md)\n"]
chapter_summaries = []
for ch in sorted(os.listdir(ROOT)):
    cpath = os.path.join(ROOT, ch)
    if not os.path.isdir(cpath):
        continue
    title = chapter_title(ch)
    sb.append(f"* {title}\n")
    count = 0
    # 顶层 md
    for fn in sorted(os.listdir(cpath)):
        if fn.endswith(".md"):
            fp = os.path.join(cpath, fn)
            sb.append(f"  * [{label_of(fp, fn)}](level_up/{ch}/{fn})\n")
            count += 1
    # 子目录
    for dn in sorted(os.listdir(cpath)):
        dp = os.path.join(cpath, dn)
        if os.path.isdir(dp) and not dn.startswith('.'):
            sb.append(f"  * {folder_title(dn)}\n")
            for fn in sorted(os.listdir(dp)):
                if fn.endswith(".md"):
                    fp = os.path.join(dp, fn)
                    sb.append(f"    * [{label_of(fp, fn)}](level_up/{ch}/{dn}/{fn})\n")
                    count += 1
    chapter_summaries.append((title, count))

with open(SIDEBAR, "w", encoding="utf-8") as f:
    f.writelines(sb)
print("写入", SIDEBAR, "（", len(sb), "行，覆盖", sum(c for _, c in chapter_summaries), "篇文档 ）")

# ---- README.md（首页） ----
dash_html = "\n".join(
    f'  <a class="dash" href="/{urllib.parse.quote(fn)}" target="_blank" rel="noopener">{txt}</a>'
    for fn, txt in DASHBOARDS
)
chapter_lines = "\n".join(f"- **{title}**（{n} 篇）" for title, n in chapter_summaries)

readme = f"""# 深圳中考数学辅导站

> 面向学生与家长的深圳中考数学辅导资源站。所有 Markdown 文档均可**直接在线预览**：左侧目录逐章导航，右上角可**搜索**全文。

## 数据看板（点击在新标签页打开）

<div class="dash-links">
{dash_html}
</div>

## 章节目录（共 {sum(c for _, c in chapter_summaries)} 篇）

{chapter_lines}

---

### 说明
- 本站由 GitHub Pages + Docsify 驱动：纯静态托管，**改任意 `.md` 后推送即生效**，无需重新构建。
- 文档源位于仓库 `level_up/` 目录，与本地写作目录保持一致；各章 `研究素材` 子目录也一并可预览。
- 需要新增/调整文档？直接编辑后 `git commit && git push` 即可。
"""
with open(README, "w", encoding="utf-8") as f:
    f.write(readme)
print("写入", README)
