# Change: Add Multi‑Layout Graph Visualization and Fast Loading

## Why
Users need multiple graph visualization styles (e.g., circular/ring, radial/fan, concentric, force) and quicker perceived/actual load times. Current experience can feel heavy on larger graphs and lacks layout choice.

## What Changes
- UI: Layout switcher to choose Circular, Radial, Concentric, Force‑Directed (and default Auto)
- UI: Smooth transitions between layouts; sensible defaults based on node count
- UI: Progressive loading: initial cap (e.g., 200 nodes) with on‑demand expansion; skeleton loader
- API: Subgraph endpoint(s) to fetch neighborhood/filtered graphs with paging and limits
- API: Compact payload mode (id, label, degree, type; optional attrs), server‑side limit/ordering
- Caching: Optional server cache for common subgraphs; client memoization of layout results

## Impact
- Affected specs: `graph` capability
- Affected code:
  - Frontend: `web` (graph view/components; G6/Sigma integration)
  - Backend: `server/routers/graph_router.py` (subgraph endpoints), relevant services
  - Models/DTO: compact graph payloads
  - Tests: UI behavior and API pagination/filters

## Open Questions
- Target layouts beyond circular/radial: concentric/dagre/grid also needed?
- Typical graph sizes (nodes/edges) and initial visible cap preference?
- Required performance budget (first paint under 1s for ≤200 nodes?)
- Need 3D layouts or 2D only?
- Grouping by category/module with sector/fan partitions desired?
