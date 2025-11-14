## Context
Add multiple graph layouts and improve loading performance across FE (Vue + G6/Sigma) and BE (FastAPI `graph_router`).

## Goals / Non-Goals
- Goals: multi-layout switching; progressive loading; compact payloads; subgraph API; smooth UX
- Non-Goals: new 3D engine, full rewrite, complex clustering algorithms (future work)

## Decisions
- Layouts: Circular, Radial, Concentric, Force; Auto chooses based on node count
- Progressive load: cap initial nodes (~200), expand by neighborhood or page
- API: `/api/graph/subgraph` supports `center`, `depth`, `limit`, `page`, `fields=compact`
- Payload: compact fields default (id, label, type, degree), full via `fields=full`
- Caching: simple LRU/MRU of recent subgraphs in memory; TTL-based invalidation

## Risks / Trade-offs
- Force layout on large graphs can be slow → default to concentric/circular beyond threshold
- Caching consistency vs. freshness → keep TTL low and invalidate on writes
- Too many UI options → keep 4 layouts and Auto default

## Migration Plan
1) Add BE subgraph + compact payload; 2) Update FE with switcher + progressive load; 3) Add tests/docs; 4) Enable caching

## Open Questions
- Sector/“fan” partition by category needed now, or later?
- Exact performance budgets and target device baseline?
