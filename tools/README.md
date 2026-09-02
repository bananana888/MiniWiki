# MiniWiki 工具

语料转换工具集：PDF → 结构化 Markdown（docling 真表格），供 agent 精确查值。

> 推荐 docling 转换（真 md 表格 + 页标记，GPU 环境见 `DEPLOY.md`），入口 `tools/backfill_pagemarks.py`；`convert.py`（pdfplumber）为旧版，仅历史参考。完整用法见 `README.md`。

## 依赖

`pyproject.toml` 为唯一依赖清单（pdfplumber + pymupdf）。用 uv 管理，无需全局 Python 环境：

```bash
uv sync --project tools     # 可选：显式装依赖；不跑也会自动装
```

## 转换用法（docling，GPU）

```bash
uv run --python 3.13 --with "torch==2.6.0+cu124" \
  --index https://download.pytorch.org/whl/cu124 \
  --index https://pypi.org/simple --index-strategy unsafe-best-match \
  --with docling python tools/backfill_pagemarks.py \
  <pdf> <outdir> [--offset N]
```

- `<pdf>`：原始 PDF 路径
- `<outdir>`：输出目录，输出文件 = PDF 同名 `.md`
- `--offset N`：打印页换算（打印页 = PDF页1基 − N），模块专属值见各 `CORPUS_MAP.md`
- 需要 CUDA 版 torch（`--with "torch==2.6.0+cu124"` 从 PyTorch 索引，PyPI 默认是 CPU 版），否则回退 CPU 极慢
- 输出带 `<!-- PDF页N / 打印页M -->` 页标记（AGENTS.md §3 引用依赖）

### 使用示例（每份文档 offset 不同，见各 CORPUS_MAP.md）

```bash
# 复用 CUDA 转换环境
D="uv run --python 3.13 --with torch==2.6.0+cu124 --index https://download.pytorch.org/whl/cu124 --index https://pypi.org/simple --index-strategy unsafe-best-match --with docling python tools/backfill_pagemarks.py"

$D "<module>/你的文档.pdf" "<module>/corpus/xxx" --offset N
```

## 质量说明

- 依赖 PDF **文本层**（无文本层扫描件需另配 OCR）
- 转换可重复执行，覆盖同名输出
- corpus 是否入 git 由你定：公开仓库建议忽略（含受版权文本），见 `.gitignore`
