# Graph Report - MediKiosk  (2026-08-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 49 nodes · 44 edges · 17 communities (7 shown, 10 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.75)
- Token cost: 273 input · 171 output

## Graph Freshness
- Built from commit: `a1851c03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Project Architecture and Requirements
- Package Metadata
- Core React Dependencies
- Project Scripts
- Linting Dependencies
- React Application Components
- ESLint Core Configuration
- React Hooks Linting
- React Refresh Linting
- Frontend Entry and Documentation
- Global Variables Configuration
- React Type Definitions
- React DOM Type Definitions
- Vite Build Tool
- Vite React Plugin

## God Nodes (most connected - your core abstractions)
1. `Project Requirement` - 7 edges
2. `scripts` - 5 edges
3. `App()` - 2 edges
4. `globals` - 2 edges
5. `@types/react` - 2 edges
6. `@types/react-dom` - 2 edges
7. `vite` - 2 edges
8. `@vitejs/plugin-react` - 2 edges
9. `react` - 2 edges
10. `react-dom` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Hero Image` --conceptually_related_to--> `Project Requirement`  [INFERRED]
  frontend/src/assets/hero.png → PROJECT_REQUIREMENT.md
- `Frontend Entry Point` --references--> `Frontend README`  [INFERRED]
  frontend/index.html → frontend/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Clinical Intake Flow** — identity_provider_abstraction, ai_clinical_assistant, ocr_extraction_pipeline [EXTRACTED 0.95]

## Communities (17 total, 10 thin omitted)

### Community 0 - "Project Architecture and Requirements"
Cohesion: 0.25
Nodes (7): AI Clinical Assistant, Cloudinary Document Pipeline, Hero Image, Identity Provider Abstraction, OCR & Extraction Pipeline, PostgreSQL Schema, Project Requirement

### Community 1 - "Package Metadata"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 2 - "Core React Dependencies"
Cohesion: 0.40
Nodes (5): dependencies, react, react-dom, react, react-dom

### Community 3 - "Project Scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 4 - "Linting Dependencies"
Cohesion: 0.67
Nodes (3): eslint, devDependencies, eslint

## Knowledge Gaps
- **27 isolated node(s):** `name`, `private`, `type`, `version`, `globals` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `Linting Dependencies` to `Package Metadata`, `ESLint Core Configuration`, `React Hooks Linting`, `React Refresh Linting`, `Global Variables Configuration`, `React Type Definitions`, `React DOM Type Definitions`, `Vite Build Tool`, `Vite React Plugin`?**
  _High betweenness centrality (0.367) - this node is a cross-community bridge._
- **Why does `scripts` connect `Project Scripts` to `Package Metadata`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `dependencies` connect `Core React Dependencies` to `Package Metadata`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Project Requirement` (e.g. with `CLAUDE.md` and `Hero Image`) actually correct?**
  _`Project Requirement` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `type` to the rest of the system?**
  _27 weakly-connected nodes found - possible documentation gaps or missing edges._