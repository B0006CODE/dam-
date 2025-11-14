## 1. Implementation

- [ ] Frontend: Add `llm` option to retrieval mode selectors
  - [ ] `web/src/components/MessageInputComponent.vue`: import icon and append `llm` to `retrievalModes`
  - [ ] `web/src/components/AgentChatComponent.vue`: add standalone button for `llm`
- [ ] Backend: Treat `llm` as no-retrieval-and-no-tools mode
  - [ ] Ensure no tools (KB/graph or others) are injected when `retrieval_mode === 'llm'`
  - [ ] Implement via `src/agents/chatbot/tools.py` so tool list is empty in `llm`

## 2. Validation

- [ ] Manual: In /agent, pick “大模型知识” and send a message
  - [ ] Confirm request payload includes `config.retrieval_mode = 'llm'`
  - [ ] Confirm citations/KB results do not appear
  - [ ] Confirm graph subgraph enrichment is not injected
- [ ] Regression: Other modes (mix/local/global) work as before

## 3. Follow-ups (optional)

- [ ] Add tooltip/help doc describing each retrieval mode
- [ ] Persist last-used retrieval mode per-thread (UX)
