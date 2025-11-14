# Append KG Subgraph For Selected Retrieval Modes

Summary: In the QA interface, when users select retrieval modes "知识图谱" (global) or "智能混合" (mix), append a knowledge-graph subgraph that reflects the reasoning context directly after the assistant answer. This makes the reasoning path visible and auditable.

Motivation:
- Users want to see the graph-based reasoning context when graph-centric modes are active.
- Today, the UI already parses tool-call outputs to extract triples, but it isn’t guaranteed to render them and is not gated by the selected retrieval mode.
- Recent demo prompts（如“⼤坝存在裂缝怎么办”）要求回答后明确展示“推理知识图谱”，需要更清晰的标题与可读的三元组链条列表。

Scope:
- Frontend only, minimal change. Gate subgraph attachment/rendering by retrieval mode, and ensure rendering is enabled when data is present.
- Label the rendered block as “知识图谱推理结果”，并在图谱下方增加三元组文本列表（推理链）以帮助复核。
- No backend contract changes. Reuse existing tool-call extraction of triples.

Out of scope:
- Generating subgraphs when no graph data is present in tool calls.
- Picking a specific KB/graph DB when multiple exist.

Risks:
- None material; changes are additive and gated by mode.

Success criteria:
- When retrieval mode is mix or global, the last AI message shows a KG subgraph (when available) after the answer content。
- The block标题为“知识图谱推理结果”，并列出来自工具调用的三元组链条（例如“坝体裂缝 -> 需要 -> 加固监测”），确保回答“⼤坝存在裂缝怎么办”这类问题时可直接看到推理依据。
- When retrieval mode is local (vector), no KG subgraph is appended.
