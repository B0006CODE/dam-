## ADDED Requirements

### Requirement: Append KG Subgraph For Selected Modes
When the user selects retrieval modes that leverage the knowledge graph, the assistant’s answer MUST include a subgraph that reflects the reasoning context if such graph data is available.

#### Scenario: Mix mode appends graph
- Given the QA interface is open
- And retrieval mode is set to "mix" (智能混合)
- When the assistant produces an answer
- And tool-call outputs contain graph triples
- Then the UI appends a knowledge-graph subgraph after the answer

#### Scenario: Global KG mode appends graph
- Given the QA interface is open
- And retrieval mode is set to "global" (知识图谱)
- When the assistant produces an answer
- And tool-call outputs contain graph triples
- Then the UI appends a knowledge-graph subgraph after the answer

#### Scenario: Graph block labeled as reasoning
- Given retrieval mode is "mix" or "global"
- And tool-call outputs contain graph triples
- When the assistant answer is rendered
- Then the appended block title reads “知识图谱推理结果” so users know the graph reflects reasoning

#### Scenario: Local mode hides graph
- Given the QA interface is open
- And retrieval mode is set to "local" (语义向量)
- When the assistant produces an answer
- Then the UI MUST NOT append any knowledge-graph subgraph

#### Scenario: No graph data available
- Given retrieval mode is "mix" or "global"
- When the assistant produces an answer
- And no graph triples can be extracted from tool-call outputs
- Then the UI does not render a graph section (no empty placeholder)

#### Scenario: Reasoning triples list rendered
- Given retrieval mode is "mix" or "global"
- And knowledge-graph triples are extracted from tool-call outputs
- When the assistant answer (e.g., “大坝存在裂缝怎么办”) is shown
- Then each triple is also displayed as a textual chain (subject → relation → object) under the graph so the reasoning steps can be reviewed
