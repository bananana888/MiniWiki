"""对比 docling 与 pdfplumber 语料的每打印页文本量，定位 docling 失分页（P8 诊断）。

用法：python tools/check_coverage.py <docling_md> <pdfplumber_md>

输出 docling 文本量明显低于 pdfplumber 的打印页（doc/pdf < 0.6），供 P8 补文本参考。
"""
import re
import sys
from pathlib import Path

PAGE_RE = re.compile(r"<!-- PDF页(\d+) / 打印页(-?\d+) -->")


def pages_of(path):
    pages = {}
    cur = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = PAGE_RE.search(line)
        if m:
            cur = int(m.group(2))
            pages.setdefault(cur, [])
            continue
        if cur is not None and line.strip():
            pages[cur].append(line)
    return {k: "\n".join(v) for k, v in pages.items()}


def clean_len(t):
    return len(re.sub(r"\s", "", t))


def main():
    docling_md, pdfplumber_md = sys.argv[1], sys.argv[2]
    doc = pages_of(docling_md)
    pdf = pages_of(pdfplumber_md)
    loss = []
    for p in sorted(pdf):
        if p not in doc:
            continue
        dl, pl = clean_len(doc[p]), clean_len(pdf[p])
        if pl > 300 and dl < pl * 0.25:
            loss.append(p)
            print(f"打印页 {p:>4}: docling {dl:>6} / pdfplumber {pl:>6} = {dl/pl:>5.2f}  <丢失>")
    print(f"\n失分页共 {len(loss)} 个: {loss}")
    if loss:
        print("补法参考：docling 该页公式/图表文本退化，见 OPTIMIZATIONS.md P8")


if __name__ == "__main__":
    main()
