## 1. Implementation
- [x] 1.1 Add legend UI to `web/src/views/GraphView.vue`
- [x] 1.2 Color nodes by entity type via `nodeStyleOptions` and `GraphCanvas` support
- [x] 1.3 Infer type from `entity_type` | `type` | `labels[0]` | fallback
- [x] 1.4 Style legend consistent with app aesthetics

## 2. Validation
- [x] 2.1 Load sample nodes and confirm legend shows counts
- [x] 2.2 Confirm node colors match legend colors
- [x] 2.3 Fallback: if no types in data, legend shows single bucket

## 3. Notes
- Future: optional filtering by type can reuse the same mapping
