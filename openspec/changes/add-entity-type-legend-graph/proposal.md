# Change: Add entity type legend to Graph view (/graph)

## Why
Users exploring the Neo4j graph need a quick understanding of what kinds of entities are present. A compact legend improves scanability and sets the stage for future filtering by type.

## What Changes
- Frontend: Add an entity type legend to `/graph` showing type name and count.
- Frontend: Color nodes by inferred entity type for consistency with the legend.
- No backend changes required; if a node lacks a type, it falls back to `Entity`/`unknown`.

## Impact
- Affected specs: `graph-ui`
- Affected code: `web/src/views/GraphView.vue`, `web/src/components/GraphCanvas.vue`
