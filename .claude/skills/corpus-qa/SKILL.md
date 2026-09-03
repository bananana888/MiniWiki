---
name: corpus-qa
description: Search the wiki corpus for EXACT values — table numbers, register/descriptor bit fields, opcodes, timing parameters, electrical characteristics. Use when a question needs precise spec text that a knowledge graph cannot return (exact values, tables, bit definitions). Complements graphify (concept/relationship level). Trigger for any spec question needing a concrete number or field layout.
---

# corpus-qa

精确查值：从已转换的语料 Markdown 里 grep 出规格的精确数值、表、位域。

## 前置

1. **发现模块**：`Glob "*/CORPUS_MAP.md"`（cwd = 仓库根）。每个含 `CORPUS_MAP.md` 的子目录是一个 wiki 模块。
2. **读对应模块地图**：选主题最相关的模块，读其 `CORPUS_MAP.md`（含章节→打印页号索引、PDF 页换算规则）。
3. 先判断问题属于哪份文档哪个章节，再决定 grep 关键词。

## 流程

1. **定文档**：按主题选语料 md（`<module>/corpus/*.md`）。
2. **定位**：在对应 corpus md 里文本检索（grep）关键词（协议名、opcode、bit 名、参数名、寄存器名），带行号。
3. **读上下文**：读该 md 的对应行段（offset/limit），把整张表或整个位域定义读全。
4. **引用**：回答里标来源文档 + 章节号 + 打印页号（对照 CORPUS_MAP 换算）。表值引用要说清是哪张表。
5. **兜底**：md 里找不到或疑似转换残缺 → 回原始 PDF：`uv run --project tools python tools/pdf_page.py <pdf> <PDF页号>`（页号取语料页标记 N；页文本缓存 `<模块>/.pdfcache/`；禁止在仓库根造 `tmp_pdf_page*.txt` 临时文件）。

## 注意

- 语料 md 由 docling 转换（真 md 表格）；跨页表格可能被拆断，值要结合上下文判断，必要时回原始 PDF 核对。
- 每页有 `<!-- PDF页N / 打印页M -->` 标记，可用它精确落页。
- docling 转换可能丢失公式文本与图表（丢为 `<!-- image -->` 占位）——公式/算例密集区搜不到时直接回原始 PDF，不自行推断。
- graphify 负责概念/关系/跨文档；corpus-qa 负责精确值。两者互补，可先 graphify 定位章节再用本 skill 查精确值。
