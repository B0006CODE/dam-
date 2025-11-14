## ADDED Requirements

### Requirement: Graph Page Entity Type Legend
The system SHALL display an entity type legend on the `/graph` page that lists each entity type present in the currently displayed graph and the count of nodes for that type. Nodes SHALL be colored consistently with the legend.

#### Scenario: Types present
- WHEN the `/graph` page displays nodes with known or inferred types
- THEN a legend appears listing each type and the node count per type
- AND node colors match the legend color chips

#### Scenario: Unknown or missing types
- WHEN nodes do not provide a type field
- THEN nodes are grouped under a default type (e.g., `Entity` or `unknown`)
- AND the legend shows a single bucket with a default color
