# DEPLOY.md — 新机部署 / 迁移

仓库数据**自包含**（语料 / 图谱 / 文档全相对路径，无机器绝对路径），`git clone` 即可浏览与检索。运行**图谱查询 / 重建 / 语料转换 / 评测**需要以下**机器级**前置（不入仓库 git，各新机装一次）：

## 1. graphify（图谱检索 / 重建 skill）

graphify 本质是 **AI 编程助手的 skill**：`graphify install` 把 SKILL.md 注册到 agent 平台
（claude → `~/.claude/skills/graphify/`），agent 以 `/graphify` 触发。底层实现是 `graphifyy`
Python 包（含 `graphify` CLI + SKILL.md + install 注册器）。AGENTS.md §3 检索命令走 CLI，
skill 是其自动触发的包装。

新机装法（装实现包 + 注册 skill）：

```bash
uv tool install "graphifyy[openai]"    # [openai] extra = deepseek backend 依赖 openai 包
graphify install --platform claude     # 注册 skill 到 ~/.claude/skills/graphify（可加 --project 进仓库）
graphify --version                      # 验证
```

## 2. LLM API key（graphify 语义提取 / 图谱重建用）

图谱 `--update`（语义提取）需要 LLM key，不设会报 `no LLM API key found`。四选一即可：

```bash
export DEEPSEEK_API_KEY=<key>     # deepseek（本项目惯用）
# 或 GEMINI_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY
```

## 3. tools 工具链依赖（语料转换 / 检索评测）

仓库 `tools/` 的 Python 依赖在 `tools/pyproject.toml`（uv 管理）。`uv run --project tools ...` 首次自动装（等效 `uv sync --project tools`），无需手动。

## 4. docling 语料转换（仅新增 / 更新 PDF 时需要）

转换命令见 `README.md`「转换语料」与 `tools/backfill_pagemarks.py`：

- **推荐 NVIDIA GPU + CUDA torch**：`uv run --with "torch==2.6.0+cu124"`（须从 PyTorch 官方索引取；PyPI 默认是 CPU 版 torch，转换慢 10 倍以上）
- **无 GPU**：CPU 可跑，但 400 页级需数十分钟
- **HF 模型**：首次自动下载（大陆网络设 `export HF_ENDPOINT=https://hf-mirror.com`）

## 5. 可选：HF 缓存换盘

docling 模型缓存默认在 `~/.cache/huggingface`（约 1GB）。嫌占系统盘可迁移：

```bash
# 假设迁到 D:\hf-cache
robocopy "%USERPROFILE%\.cache\huggingface" "D:\hf-cache" /E /MOVE
setx HF_HOME "D:\hf-cache"        # 新终端生效
```

## 依赖归属说明

graphify（agent skill + graphifyy 实现包，独立于仓库安装）、LLM key（环境变量）、GPU（硬件）均**非仓库 pip 依赖**，故不入 `requirements.txt` / `pyproject.toml`；仓库内 Python 包依赖统一在 `tools/pyproject.toml`。部署类前置集中在本文件。
