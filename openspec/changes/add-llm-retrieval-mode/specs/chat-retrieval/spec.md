## ADDED Requirements

### Requirement: LLM-only Retrieval Mode
The system SHALL provide a chat retrieval mode that answers using only the model’s built-in knowledge without consulting project knowledge bases or the global knowledge graph, and SHALL NOT invoke any tools in this mode.

#### Scenario: User selects LLM-only in /agent
- WHEN a user opens `http://localhost:5173/agent` and selects the retrieval option labeled “大模型知识”
- AND sends a chat message
- THEN the frontend includes `config.retrieval_mode = 'llm'` in the POST `/api/chat/agent/{agent_id}` request
- AND the backend does not attach any tools for that turn (no knowledge-base tools, no graph tools, no general tools)
- AND the response contains no citations/KB snippets, and no graph subgraph enrichment is injected

#### Scenario: Other modes remain unaffected
- GIVEN existing retrieval options “智能混合”, “语义向量”, and “知识图谱”
- WHEN a user selects one of those modes and sends a message
- THEN the behavior matches current implementation (hybrid, vector-only, or graph) with no regressions
