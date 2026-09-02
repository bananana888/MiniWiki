"""docling 转换并导出带打印页标记的 Markdown 语料（P2 页标记回补）。

P1 的 docling 重转（--to md）产出的语料无 `<!-- PDF页N / 打印页M -->` 页标记，
而 AGENTS.md §3 强制引用规范依赖打印页号。本脚本用 docling Python API 转换，
在导出时按每个元素的来源页（prov.page_no）回插页标记，打印页按模块偏移换算。

用法（需 docling 环境，CUDA torch 见 OPTIMIZATIONS.md P1）：
    uv run --python 3.13 --with "torch==2.6.0+cu124" \
        --index https://download.pytorch.org/whl/cu124 \
        --index https://pypi.org/simple \
        --index-strategy unsafe-best-match \
        --with docling \
        python tools/backfill_pagemarks.py <pdf> <outdir> [--offset N]

    --offset N  打印页 = PDF页(1基) - N（模块专属偏移，见各 CORPUS_MAP.md）
"""
import argparse
import sys
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus, DocItemLabel

# 页眉/页脚是 PDF 排版噪声，不进入语料
SKIP_LABELS = {DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER}


def render_item(item) -> str:
    """把单个 docling 元素渲染为 md 文本（不含页标记）。"""
    label = getattr(item, "label", None)
    if label in SKIP_LABELS:
        return ""
    text = getattr(item, "text", "") or ""

    if label == DocItemLabel.TITLE or label == DocItemLabel.SECTION_HEADER:
        level = getattr(item, "level", 0) or 0
        return f"{'#' * (level + 1)} {text}"
    if label == DocItemLabel.LIST_ITEM:
        return f"- {text}"
    if label == DocItemLabel.PICTURE:
        return "<!-- image -->"

    # 表格 / 图表：优先用 docling 自带 md 渲染
    export = getattr(item, "export_to_markdown", None)
    if export is not None:
        return export()
    return text


def render(doc, offset: int) -> str:
    """遍历 body 元素，按来源页回插页标记后渲染整份 md。"""
    lines = []
    cur_page = None
    for ref in doc.body.children:
        # body.children 是 RefItem 列表，resolve(doc) 得到实际元素对象
        item = ref.resolve(doc)
        if item is None:
            continue
        prov = getattr(item, "prov", None)
        page = prov[0].page_no if prov else None
        if page is not None and page != cur_page:
            lines.append(f"<!-- PDF页{page} / 打印页{page - offset} -->")
            cur_page = page
        rendered = render_item(item)
        if rendered:
            lines.append(rendered)
            lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="docling 转换并回补打印页标记")
    ap.add_argument("pdf", help="原始 PDF 路径")
    ap.add_argument("outdir", help="输出目录（自动创建）")
    ap.add_argument("--offset", type=int, default=0, help="打印页 = PDF页(1基) - offset")
    a = ap.parse_args()

    # docling 默认 auto device：CUDA torch 已装时自动用 GPU（RTX 3050 下约 7-15 分钟/份）
    converter = DocumentConverter()
    result = converter.convert(a.pdf)
    if result.status != ConversionStatus.SUCCESS:
        print(f"转换失败: {result.status}", file=sys.stderr)
        sys.exit(1)

    md = render(result.document, a.offset)
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / (Path(a.pdf).stem + ".md")
    out.write_text(md, encoding="utf-8")
    print(f"-> {out}（{len(md)} 字符，页标记已回补）")


if __name__ == "__main__":
    main()
