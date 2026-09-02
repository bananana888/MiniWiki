# MiniWiki — 多模块技术文档 wiki 检索系统

把 PDF 技术文档转成**可检索语料 + 知识图谱**，供 AI 编程助手（Claude Code 等）高质量问答。
本仓库为**空系统骨架**：不含任何受版权 PDF 或转换语料，`tools/` + 规则 + 工作流可直接复用，你放入自己的文档即用。

## 结构

```
.
├── AGENTS.md        # 检索契约（三层决策、引用规范、维护命令）
├── CLAUDE.md        # Claude Code 专属规则
├── DEPLOY.md        # 新机部署：graphify / LLM key / docling GPU 前置
├── tools/           # 转换 / 回补 / 覆盖率工具（uv 管理）
│   ├── backfill_pagemarks.py   # docling 转换 + 打印页标记回补
│   ├── convert.py              # 旧版 pdfplumber 转换（历史参考）
│   ├── check_coverage.py       # 语料覆盖诊断
│   └── pyproject.toml          # tools 依赖清单
└── .claude/skills/corpus-qa/   # 精确查值 skill（按需触发）
```

**模块约定**：运行时你添加的每个 wiki 模块 = 一个含 `CORPUS_MAP.md` 的子目录 `<module>/`：
```
<module>/
├── 原始文档.pdf          # 你的受版权 PDF（不入库，转换后删除）
├── corpus/*.md           # docling 转换语料（真 md 表格 + 页标记）
├── CORPUS_MAP.md         # 章节 → 打印页索引、offset 换算
└── graphify-out/graph.json  # 概念图谱
```

## 三层问答检索

对任意技术话题按层查（详见 `AGENTS.md`）：

1. **概念 / 架构 / 关系**：`graphify query "<问题>" --graph <module>/graphify-out/graph.json`
2. **精确值 / 表 / 位域 / 时序**：grep `<module>/corpus/*.md` → Read 上下文（可触发 `corpus-qa` skill）
3. **前两层都缺** → 读原始 PDF（页换算见 `CORPUS_MAP.md`）

引用规范：语料层标 `文档 + 章节 + 打印页`（如 `DocName §14.1.4 p.339`）；图谱层标 `source_location`；无法验证的标注"推断/无来源"。

## 添加你的第一份文档（模块）

1. `mkdir <module>`，放入 PDF（命名含 offset 说明）
2. 转换 + 页标记回补（GPU 环境见 `DEPLOY.md`）：
   ```bash
   uv run --python 3.13 --with "torch==2.6.0+cu124" \
     --index https://download.pytorch.org/whl/cu124 \
     --index https://pypi.org/simple --index-strategy unsafe-best-match \
     --with docling python tools/backfill_pagemarks.py \
     <module>/xxx.pdf <module>/corpus/xxx --offset N
   ```
3. 建概念图谱：`graphify <module>`（需 LLM key，见 `DEPLOY.md`）
4. 写 `<module>/CORPUS_MAP.md`（章节→打印页 + offset 换算）
5. 完成——`AGENTS.md` 检索决策自动适用，无需改规则

## 维护命令

- 语料转换：`python tools/backfill_pagemarks.py <pdf> <corpus目录> --offset N`（GPU/CUDA 见 `DEPLOY.md`）
- 图谱重建：`graphify <module> --update`
- 覆盖率诊断：`python tools/check_coverage.py <docling_md> <pdfplumber_md>`
- tools 依赖：`uv run --project tools ...` 自动装

## Git 约定

- 跟踪：规则文档、tools、skill、`CORPUS_MAP.md`；**建议忽略 `corpus/`（含受版权文本）与 `graphify-out/` 瞬态**（见 `.gitignore`）
- 默认忽略：graphify 瞬态产物、`tools/.venv/`、`__pycache__/`

## 版权说明

本骨架不含任何第三方受版权文档或转换文本。加入文档前请确认你有权使用；公开仓库请勿提交受保护 PDF / 转换全文。
