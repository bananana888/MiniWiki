# MiniWiki — 多模块技术文档 wiki 检索系统

把 PDF 技术文档转成**可检索语料 + 知识图谱**，供 AI 编程助手（Claude Code 等）高质量问答。
本仓库为**空系统骨架**：不含任何受版权 PDF 或转换语料，`tools/` + 规则 + 工作流可直接复用，你放入自己的文档即用。

## 快速开始（一键部署，喂给 Claude Code）

复制下面整段给 **Claude Code**（或其他 AI 编程助手）执行，自动避开系统盘、走国内镜像、检测 GPU 并自检：

<details>
<summary>📋 部署提示词 — 点开复制</summary>

```text
你是部署助手。为我在本机部署开源项目 MiniWiki（多模块技术文档 wiki 检索系统）。

【硬盘】大体积内容全程避开 C 盘（系统盘）：git clone 目录、uv 缓存、Python 环境、HuggingFace 缓存全部放非系统盘。
graphify 二进制与 Claude skill 装在用户目录（~/.local/bin、~/.claude/skills）属正常小件，不需要移动。
开始前先问我：目标盘用哪个（默认 D:/，回 D 或 E 即可）；只有我明确说用 C 盘才放 C。

【国内镜像】所有下载走国内加速：
- uv / pip 索引：用清华或阿里源（如 https://pypi.tuna.tsinghua.edu.cn/simple）
- HuggingFace 模型：export HF_ENDPOINT=https://hf-mirror.com
- CUDA PyTorch 下载较大、可能较慢，提前告知用户

【步骤】
1. 按目标盘 clone：git clone https://github.com/bananana888/MiniWiki.git <盘符>:/MiniWiki
2. 机器无 uv 则用官方脚本安装（安装目录设非系统盘）
3. 装 graphify（图谱检索 skill）：uv tool install "graphifyy[openai]"；再 graphify install --platform claude（注册到 ~/.claude/skills）
4. 让用户提供 LLM key（国内推荐 DEEPSEEK_API_KEY），写入用户级环境变量，绝不写进仓库
5. tools 依赖：cd MiniWiki && uv sync --project tools
6. 检测 GPU：nvidia-smi
   - 有 GPU → 保留 docling GPU 转换能力（后续转语料用 CUDA torch，见 README/DEPLOY）
   - 无 GPU → 语料转换走 CPU 快的 pdfplumber 脚本 tools/convert.py；docling 真表格仅必要时 CPU 慢跑

【自检】每步报结果，全过才算成功：
- graphify --version 有版本号
- ~/.claude/skills/graphify/ 存在
- uv run --project tools python -c "import pdfplumber, pymupdf" 无报错
- 用户若有现成 PDF：用 tools/pdf_page.py 抽第 1 页文本验证读取正常（整份语料转换等用户真正加文档时再做，命令见 README）
- 失败如实报告原因，不跳过不假装成功

完成后给安装摘要（组件版本/位置/GPU 情况）+ 下一步加文档指引（README「添加你的第一份文档」）。
```
</details>

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
