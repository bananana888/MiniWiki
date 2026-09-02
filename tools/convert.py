"""PDF → Markdown 语料转换器。

布局模式提取，保留文本层排版；表格以列对齐文本输出（非真 md 表格）。
每页写 `<!-- PDF页N / 打印页M -->` 标记，页号换算规则见各 CORPUS_MAP.md。

用法：
    uv run --project tools python tools/convert.py <pdf> <outdir> [--offset N]

    <pdf>      原始 PDF 路径
    <outdir>   输出目录（自动创建）
    --offset N 打印页 = PDF页(1基) - N（模块专属偏移，见 CORPUS_MAP.md）

输出文件名为 PDF 同名 .md。首次运行 `uv sync` 或直接 `uv run` 自动装依赖。
"""
import argparse
import io
import os
import sys

import pdfplumber
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def convert(pdf: str, outdir: str, offset: int) -> None:
    os.makedirs(outdir, exist_ok=True)
    name = os.path.splitext(os.path.basename(pdf))[0] + ".md"
    out = os.path.join(outdir, name)

    doc = pymupdf.open(pdf)
    toc = doc.get_toc()
    doc.close()

    lines = [f"# {os.path.basename(pdf)}", "",
             f"> pdfplumber 转换（layout 模式）。打印页 = PDF页(1基) - {offset}。",
             "", "## 目录（打印页号）"]
    for lvl, title, pg in toc:
        lines.append(f"{'  ' * (lvl - 1)}- p.{pg - offset} {title}")
    lines.append("")

    with pdfplumber.open(pdf) as p:
        n = len(p.pages)
        for i, pg in enumerate(p.pages):
            lines.append(f"<!-- PDF页{i + 1} / 打印页{i + 1 - offset} -->")
            t = pg.extract_text(layout=True) or pg.extract_text()
            lines.append(t or f"<!-- p.{i + 1 - offset} 无文本层（需OCR） -->")
            lines.append("")
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{n}", flush=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"-> {out}（{n} 页，{len(toc)} 条目录）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PDF → Markdown 语料转换器")
    ap.add_argument("pdf", help="原始 PDF 路径")
    ap.add_argument("outdir", help="输出目录（自动创建）")
    ap.add_argument("--offset", type=int, default=0,
                    help="打印页 = PDF页(1基) - offset")
    a = ap.parse_args()
    convert(a.pdf, a.outdir, a.offset)
