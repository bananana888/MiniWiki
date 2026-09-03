"""PDF 兜底页文本工具：按 PDF 页号抽文本，输出 stdout 并缓存到模块级 .pdfcache/。

用法（相对仓库根）：
    uv run --project tools python tools/pdf_page.py <pdf路径> <页号> [<页号>...]

- 页号 = PDF 页号（1 起）。语料页标记 `<!-- PDF页NNN / 打印页MMM -->` 里的 PDF页 即此值。
- 命中缓存(<pdf所在目录>/.pdfcache/<pdf文件名>/p<页号>.txt)直接读，不再重抽；缓存缺失才抽取并落盘。
- 输出原始页文本到 stdout，供会话直接 Read/Grep，不往仓库根落临时文件。
- 需要强制重抽加 --refresh。

为什么放这里：脚本无状态属 tools/；缓存属数据、跟源 PDF 同模块目录，gitignore 忽略。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pymupdf  # mupdf 官方绑定（旧名 fitz）


def setup_stdout() -> None:
    """Windows 控制台 GBK 会炸在私有区字符(如 )并乱码中文，强制 UTF-8。"""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except AttributeError:
        pass  # 非 TextIOWrapper（如重定向测试）无 reconfigure


def cache_path(pdf: Path, page: int) -> Path:
    return pdf.parent / ".pdfcache" / f"{pdf.name}.p{page:04d}.txt"


def extract(doc: pymupdf.Document, page: int) -> str:
    return doc.load_page(page - 1).get_text()


def main() -> None:
    setup_stdout()
    ap = argparse.ArgumentParser(description="PDF 兜底页文本抽取/缓存工具")
    ap.add_argument("pdf", type=Path, help="源 PDF 路径（相对仓库根，如 <module>/xxx.pdf）")
    ap.add_argument("pages", type=int, nargs="+", help="PDF 页号（1 起），可多个")
    ap.add_argument("--refresh", action="store_true", help="忽略缓存强制重抽")
    args = ap.parse_args()

    pdf = args.pdf
    if not pdf.is_file():
        sys.exit(f"PDF 不存在: {pdf}")

    doc: pymupdf.Document | None = None
    if args.refresh:
        doc = pymupdf.open(pdf)
    else:
        # 只要有一个页缓存缺失就开文档；全部命中则全程不动 PDF
        for p in args.pages:
            if not cache_path(pdf, p).exists():
                doc = pymupdf.open(pdf)
                break

    for page in args.pages:
        if page < 1 or (doc is not None and page > doc.page_count):
            total = doc.page_count if doc is not None else "?"
            sys.exit(f"页号越界: 请求第 {page} 页，PDF 共 {total} 页")
        cp = cache_path(pdf, page)
        text: str | None = None
        if not args.refresh and cp.exists():
            text = cp.read_text(encoding="utf-8")
        else:
            text = extract(doc, page)
            cp.parent.mkdir(parents=True, exist_ok=True)
            cp.write_text(text, encoding="utf-8")
        print(f"===== {pdf.name} PDF页{page} =====")
        print(text)


if __name__ == "__main__":
    main()
