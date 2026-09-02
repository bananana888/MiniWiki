# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

通用契约（结构 / 检索决策 / 纪律 / skill 触发表 / 维护命令）见 `AGENTS.md`，本文件只放 Claude 专属补充，不重复。

## 路径约定

- 所有命令与路径**相对仓库根**执行（本仓库无绝对路径硬编码，可放任意位置）。当前工作目录不是仓库根时，先 `cd` 到根再执行。
- 模块发现一律用 `Glob "*/CORPUS_MAP.md"`（相对仓库根），不写死模块名。

## 检索顺序（Claude 专属执行细则）

遵循 AGENTS.md §3 检索决策，Claude 专属执行细则：

- **精确值 / 表 / 位域 / 寄存器字段 / 时序参数 → 语料优先**：直接 grep `corpus/*.md` 定位行号后 Read 上下文。语料层是精确值唯一可靠层；可触发 `corpus-qa` skill。
- **概念 / 架构 / 关系 / 跨文档 → 图谱定位**：`graphify query "<问题>" --graph <module>/graphify-out/graph.json`。但图谱节点标题**无章节号**，引用必须回语料取（拿不到 `13.4.17` 这类章节号）。
- **中文概念查询图谱常失效**（"No matching nodes"，节点是英文标题）→ 直接走语料层。
- 两层都缺 → 原始 PDF 兜底（PDF 页 ↔ 打印页换算见各 `CORPUS_MAP.md`）。

**引用规范（强制）**：语料层标 文档 + 章节 + 打印页（如 `DocName §14.1.4 p.339`）；图谱层引用 `source_location`。给不出可验证引用时明确标注"推断/无来源"。

## 工具偏好

- 检索用 Grep/Glob，读文件用 Read，查外网用 WebFetch/WebSearch；Bash 仅在专用工具做不到时用。
