# Change: Add LLM-only retrieval mode on /agent

## Why
Users need a retrieval option that answers using the model’s own knowledge without consulting the project knowledge bases or the knowledge graph.

## What Changes
- Add a new retrieval mode value `llm` exposed in the /agent chat UI selectors.
- Pass `retrieval_mode: 'llm'` in chat requests when selected.
- Backend agents treat `llm` as “no retrieval and no tools”: omit knowledge base, knowledge graph, and all other tools.

## Impact
- Affected specs: chat-retrieval
- Affected code:
  - Frontend: `web/src/components/AgentChatComponent.vue`, `web/src/components/MessageInputComponent.vue`
  - Backend: `src/agents/common/tools.py`
