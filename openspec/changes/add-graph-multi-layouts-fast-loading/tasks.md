## 1. Implementation
- [ ] 1.1 FE: Add layout switcher (Circular, Radial, Concentric, Force, Auto)
- [ ] 1.2 FE: Implement smooth transitions between layouts; preserve zoom/position
- [ ] 1.3 FE: Progressive loading (initial cap ~200 nodes) + expand on demand
- [ ] 1.4 FE: Skeleton/placeholder loaders; empty/error states
- [ ] 1.5 BE: Add `GET /api/graph/subgraph` with `center`, `depth`, `limit`, `page`, `mode` (neighbors/search)
- [ ] 1.6 BE: Compact payload mode (`fields=compact`) and server-side ordering/limits
- [ ] 1.7 BE: Optional cache for hot subgraphs; invalidate on mutations
- [ ] 1.8 DTO: Define GraphNode/GraphEdge (compact vs full)

## 2. Validation & Tests
- [ ] 2.1 FE: Snapshot/behavior tests for layout toggle and expansion
- [ ] 2.2 BE: API tests for pagination, limits, compact mode, invalid params
- [ ] 2.3 Perf: Verify initial render under target budget for ≤200 nodes

## 3. Docs
- [ ] 3.1 Usage: Layout switcher and when to use which
- [ ] 3.2 API: Subgraph params, examples, compact fields
- [ ] 3.3 Perf tips: limiting, expansion, caching notes
