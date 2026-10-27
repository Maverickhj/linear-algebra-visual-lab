#!/usr/bin/env python3
"""Small, standard-library-only tools for independent visualization units."""
from __future__ import annotations

import argparse
from functools import partial
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
ID_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
SECTIONS = ("Topic", "Mathematical Insight", "Visualization", "Usage", "Validation")
OUTPUTS = ("figure.svg", "interactive.html")


def units(root: Path) -> list[tuple[Path, dict]]:
    """Read the on-disk catalog; never maintain another list of units."""
    folder = root / "visualizations"
    if not folder.is_dir():
        raise ValueError("缺少 visualizations/ 目录")
    found = []
    for path in sorted(folder.iterdir()):
        if not path.is_dir():
            raise ValueError(f"visualizations/ 仅放 Unit 目录：{path.name}")
        if path.is_symlink() or not ID_PATTERN.fullmatch(path.name):
            raise ValueError(f"无效 Unit 目录名：{path.name}")
        try:
            data = json.loads((path / "unit.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError(f"{path.name}/unit.json：{exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{path.name}：unit.json 必须是对象")
        if set(data) - {"title", "dimension", "status", "reference"}:
            raise ValueError(f"{path.name}：包含未约定的元数据字段")
        if not isinstance(data.get("title"), str) or not data["title"].strip():
            raise ValueError(f"{path.name}：title 必须是非空字符串")
        if type(data.get("dimension")) is not int or data["dimension"] not in (2, 3):
            raise ValueError(f"{path.name}：dimension 必须是整数 2 或 3")
        if data.get("status") not in ("draft", "ready"):
            raise ValueError(f"{path.name}：status 必须是 draft 或 ready")
        if "reference" in data and not isinstance(data["reference"], str):
            raise ValueError(f"{path.name}：reference 必须是字符串")
        readme = path / "README.md"
        if not readme.is_file():
            raise ValueError(f"{path.name}：缺少 README.md")
        text = readme.read_text(encoding="utf-8")
        for section in SECTIONS:
            if not re.search(r"^## " + re.escape(section) + r"(?:[ \t·：:]|$)", text, re.M):
                raise ValueError(f"{path.name}：README 缺少 ## {section}")
        if not any((path / name).is_file() for name in OUTPUTS):
            raise ValueError(f"{path.name}：至少需要 figure.svg 或 interactive.html")
        found.append((path, data))
    return found


def build_index(root: Path) -> Path:
    records = units(root)
    cards = []
    for path, data in records:
        prefix = "visualizations/" + path.name + "/"
        links = []
        for name, label in (("interactive.html", "打开交互实验 →"), ("figure.svg", "查看静态插图 ↗")):
            if (path / name).is_file():
                links.append(f'<a class="button" href="{prefix}{name}">{label}</a>')
        status = "已验证" if data["status"] == "ready" else "草稿 · 待完成"
        reference = html.escape(data.get("reference", ""))
        cards.append(f'''<article class="unit">
  <p class="meta">{data['dimension']}D <span> / </span> {status}</p>
  <h2>{html.escape(data['title'])}</h2>
  <p class="reference">{reference or '暂未填写教材定位'}</p>
  <div class="actions">{''.join(links)}</div>
  <a class="notes" href="{prefix}README.md">实验说明与源码目录 →</a>
</article>''')
    content = "\n".join(cards) or '<p class="empty">尚无 Unit。按约定新增第一个具体问题。</p>'
    output = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="用几何直觉理解 Strang 线性代数。静态插图与可离线使用的交互实验。">
<title>Linear Algebra Visual Lab</title>
<link rel="icon" href="data:,">
<style>
:root{color-scheme:light;--paper:#f6f7f2;--ink:#172c36;--muted:#536870;--accent:#087d79;--line:#dce3de}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.8 system-ui,"PingFang SC","Microsoft YaHei",sans-serif}
header,main,footer{max-width:1080px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid var(--line);font-size:13px}
a{color:var(--accent);text-underline-offset:4px}a:focus-visible{outline:3px solid #2563a6;outline-offset:5px}header a{text-decoration:none}
.eyebrow{font-size:12px;letter-spacing:2px;color:var(--accent);margin:0 0 12px}.intro{padding:48px 0 34px;max-width:740px}h1{font:500 clamp(30px,5vw,48px)/1.2 Georgia,serif;margin:0 0 22px}.lead{font-size:20px;margin:0 0 16px}.muted,.reference{color:var(--muted)}
.collection{border-top:1px solid var(--line);padding-top:26px}.collection>h2{font-size:19px;margin:0 0 22px}.unit{border:1px solid var(--line);padding:28px;background:white;border-radius:10px;margin-bottom:20px}.unit h2{font-size:26px;margin:4px 0 10px}.meta{margin:0;color:var(--accent);font-size:13px}.meta span{padding:0 8px;color:var(--muted)}.reference{font:14px/1.8 Georgia,serif;overflow-wrap:anywhere;max-width:700px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0 18px}.button{display:inline-block;border:1px solid var(--line);border-radius:5px;padding:9px 15px;text-decoration:none;background:#f6f9f6}.button:hover{border-color:var(--accent);background:#e6f1ec}.notes{font-size:14px}.how{margin:40px 0 16px;max-width:720px}.how h2{font-size:20px}code{font:14px ui-monospace,monospace;overflow-wrap:anywhere}footer{border-top:1px solid var(--line);font-size:13px;color:var(--muted)}
@media(max-width:540px){header,main,footer{padding:18px}.intro{padding:34px 0 24px}.unit{padding:20px}.actions{flex-direction:column}.button{text-align:center}.lead{font-size:18px}}
</style>
</head>
<body>
<header><span>线性代数 · 几何学习实验室</span><a href="README.md">项目说明 ↗</a></header>
<main>
<section class="intro"><p class="eyebrow">OBSERVE · CHANGE · UNDERSTAND</p><h1>Linear Algebra<br>Visual Lab</h1><p class="lead">从一个具体的几何关系，走向数学理解。</p><p class="muted">Strang《Introduction to Linear Algebra》第 5 版伴读。每个实验围绕一个问题，包含静态插图、交互页面，或两者。按当前学习需要逐步积累。</p></section>
<section class="collection" aria-labelledby="collection-title"><h2 id="collection-title">已有可视化 · COUNT 个 Unit</h2>
CARDS
</section>
<section class="how"><h2>下一次，仍从一个问题开始。</h2><p>先说明想建立的几何直觉，再选择图形和参数。新增实验遵循同一套命名、坐标与交互约定。</p><p><a href="docs/conventions.md">阅读可视化约定 →</a></p><p class="muted">此索引由各 Unit 的元数据生成。交互页面和插图使用相对路径，可在本地或离线浏览。</p></section>
</main><footer>Minimal First · Consistent Organization · Incremental Growth</footer>
</body></html>
'''.replace("COUNT", str(len(records))).replace("CARDS", content)
    target = root / "index.html"
    target.write_text(output, encoding="utf-8")
    return target


def create_unit(root: Path, unit_id: str, title: str, kind: str, dimension: int) -> Path:
    if not ID_PATTERN.fullmatch(unit_id):
        raise ValueError("ID 必须是英文 kebab-case，以字母开头")
    if not title.strip() or kind not in ("static", "interactive", "both") or dimension not in (2, 3):
        raise ValueError("请提供非空标题、正确的类型和维度")
    units(root)  # Refuse to add content to an already invalid catalog.
    target = root / "visualizations" / unit_id
    if target.exists():
        raise ValueError(f"目录已存在，未覆盖：{target.name}")
    template = root / "templates" / "unit"
    required = ["README.md"]
    if kind in ("static", "both"):
        required.append("figure.svg")
    if kind in ("interactive", "both"):
        required.append("interactive.html")
    if not all((template / name).is_file() for name in required):
        raise ValueError("缺少 Unit 模板文件")
    target.mkdir()
    try:
        for name in required:
            shutil.copyfile(template / name, target / name)
        metadata = {"title": title.strip(), "dimension": dimension, "status": "draft", "reference": ""}
        (target / "unit.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        readme = target / "README.md"
        entries = []
        if "figure.svg" in required:
            entries.append("- [静态插图](figure.svg)：占位 SVG，需编辑为本题图形。")
        if "interactive.html" in required:
            entries.append("- [交互实验](interactive.html)：页面骨架，需实现本题模型与控件。")
            page = target / "interactive.html"
            page.write_text(page.read_text(encoding="utf-8").replace("{{TITLE}}", html.escape(title.strip(), quote=True)), encoding="utf-8")
        readme.write_text(readme.read_text(encoding="utf-8").replace("{{VISUALIZATION_LINKS}}", "\n".join(entries)), encoding="utf-8")
        build_index(root)
    except Exception:
        shutil.rmtree(target)
        raise
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="仓库根目录；默认脚本所在项目")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="创建草稿 Unit，并更新索引")
    new.add_argument("id")
    new.add_argument("--title", required=True)
    new.add_argument("--kind", choices=("static", "interactive", "both"), default="interactive")
    new.add_argument("--dimension", type=int, choices=(2, 3), default=2)
    commands.add_parser("check", help="检查 Unit 组织与元数据，不证明数学正确性")
    commands.add_parser("index", help="校验并重新生成 index.html")
    serve = commands.add_parser("serve", help="校验、更新索引并提供静态文件")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "new":
            print("已创建草稿：", create_unit(root, args.id, args.title, args.kind, args.dimension))
        elif args.command == "check":
            print(f"结构校验通过：{len(units(root))} 个 Unit")
        else:
            print("已更新索引：", build_index(root), flush=True)
            if args.command == "serve":
                if not 0 <= args.port <= 65535:
                    raise ValueError("port 必须在 0..65535 内")
                handler = partial(SimpleHTTPRequestHandler, directory=str(root))
                with ThreadingHTTPServer((args.host, args.port), handler) as server:
                    print(f"静态服务监听 {args.host}:{server.server_port}；Ctrl+C 停止。", flush=True)
                    try:
                        server.serve_forever()
                    except KeyboardInterrupt:
                        pass
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
