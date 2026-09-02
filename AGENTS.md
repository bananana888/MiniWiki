# AGENTS.md — MiniWiki 通用工作契约

本文件被所有 agent（Claude Code / opencode / mimocode / omo 等）读取。**只含工具无关的稳定规则**。Claude Code 专属 skill 规则见仓库 `CLAUDE.md`。**本仓库为骨架**，示例中 `<module>`、`corpus/*.md`、`graphify-out/` 均为你按 `README.md` 加入文档后形成的结构。

## 1. 术语

- **模块**：一个自包含 wiki 子目录，标识 = 含 `CORPUS_MAP.md`。
- **语料**：`<module>/corpus/*.md`，PDF 转换出的文本，精确查值用。
- **图谱**：`<module>/graphify-out/graph.json`，概念/关系检索用。
- **打印页**：文档印刷页码；PDF 页 ↔ 打印页换算规则在各 `CORPUS_MAP.md`。

## 2. 路径基准

所有命令与文件路径**相对仓库根**。当前工作目录不是仓库根时先 `cd` 到根。模块发现：`Glob "*/CORPUS_MAP.md"`。

## 3. 问答检索（决策分支）

| 问题类型 | 层 | 动作 |
|---|---|---|
| 概念 / 架构 / 关系 / 跨文档 | 图谱 | `graphify query "<问题>" --graph <module>/graphify-out/graph.json` |
| 精确值 / 表 / 位域 / 寄存器字段 / 时序参数 | 语料 | grep `<module>/corpus/*.md` 定位行号 → 读上下文 |
| 前两层都缺，或疑似转换残缺 | 原始 PDF | 读 `<module>/` 下 PDF（页号换算见 `CORPUS_MAP.md`） |

**实测检索指引**：
- 精确值 / 表 / 位域 / 时序 → **语料优先**（语料层是精确值唯一可靠层）。
- 概念 / 枚举 / 关系 → 图谱定位；但**图谱节点标题无章节号，引用必须回语料取**。
- 中文概念查询图谱可能失效（"No matching nodes"）→ 直接走语料层。
- 公式 / 算例 / 图表密集区域：docling 转换可能丢失公式文本或图表，语料搜不到完整公式/表时**直接原始 PDF 兜底**，不得自行推断。

**skill 触发**（若 agent 支持 skill 机制）：文档类 `pdf`/`docx`/`pptx`/`xlsx`、飞书 `lark-*`、精确查值 `corpus-qa`、知识图谱 `graphify`、笔记 `summarize-note`、画图 `mermaid-diagrams`。graphify 是 agent skill（`/graphify`），CLI 是其实现，任何 agent 可直接运行上表命令。

**引用规范（强制）**：
- 图谱层引用 `source_location`（章节号）；语料层引用 **文档 + 章节 + 打印页**（如 `DocName §14.1.4 p.339`）。
- 无法给出可验证引用的断言 → 明确标注"推断/无来源"，不得冒充规范结论。

**自检（回答提交前必过）**：
1. 每个关键断言有引用？
2. 层选择正确（该给精确值没只给概念）？
3. 跨页表被拆断处已回原始 PDF 核对？

## 4. 通用工作纪律

- 文本检索用 grep/Glob，读文件用 Read，专用工具做不到才用 shell。
- 改动前先读目标文件；删除/覆盖前看内容，与描述不符即停。
- 不可逆或对外操作（删数据、发外部消息、推送）先确认再执行。
- **证据先于结论**：声称完成/修好/通过前必须实际运行验证命令并确认输出；失败如实报告。
- 多步骤任务拆小，一次只做一件事，每步确认结果。
- 公式 / 图表缺失时立即回原始 PDF，不臆测内容。

## 5. 仓库维护

- 语料转换：`python tools/backfill_pagemarks.py <pdf> <corpus目录> --offset N`（GPU / CUDA 见 `DEPLOY.md`）
- 图谱重建：`graphify <module> --update`
- 覆盖率诊断：`python tools/check_coverage.py <docling_md> <pdfplumber_md>`
- 新增模块：见 `README.md`「添加你的第一份文档」——转换 → 建图 → 写 `CORPUS_MAP.md` → 自动被发现
- 工具依赖：`tools/pyproject.toml`（uv 管理，`uv run --project tools` 自动装）
- 部署前置（graphify / LLM key / GPU）：`DEPLOY.md`

## 6. Agent 专属规则

- **Claude Code**：`CLAUDE.md`（仓库级）
- **其他 agent**：各自的 `.xxx/` 配置目录
