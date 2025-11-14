## ADDED Requirements

### Requirement: Multiple Graph Layouts
The system SHALL provide multiple graph display layouts and allow runtime switching.

#### Scenario: Layout switcher options
- **WHEN** the user opens the graph view
- **THEN** the UI SHALL offer Circular, Radial, Concentric, Force, and Auto layout options

#### Scenario: Smooth layout transitions
- **WHEN** the user switches layouts
- **THEN** the graph SHALL animate to the new layout while preserving zoom/center where reasonable

### Requirement: Fast Graph Loading
The system SHALL load graph data quickly with progressive loading and compact payloads.

#### Scenario: Initial render under budget
- **WHEN** the graph loads with ≤ 200 nodes in compact mode
- **THEN** the first render SHOULD occur within an acceptable budget on typical dev hardware (target ≤ 1s perceived), with a skeleton shown within ~200ms

#### Scenario: Progressive loading and expansion
- **WHEN** the full graph exceeds the initial cap
- **THEN** the UI SHALL fetch and render a limited subgraph and allow on-demand expansion (e.g., by node neighborhood)

#### Scenario: Subgraph API with paging
- **WHEN** the client requests `/api/graph/subgraph` with `center`, `depth`, `limit`, and `page`
- **THEN** the server SHALL return a compact node/edge payload for that window, honoring limits and ordering

#### Scenario: Compact payload mode
- **WHEN** the client requests `fields=compact`
- **THEN** the server SHALL return minimal fields (id, label, type, degree), omitting heavy attributes by default

#### Scenario: Caching hot subgraphs
- **WHEN** the same subgraph window is requested repeatedly
- **THEN** the system SHOULD serve responses faster via a short‑lived cache, invalidated on mutations
