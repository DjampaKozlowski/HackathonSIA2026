# Analyse des flux de données - Rapprochement de Variables

## Phase 1: Core Layout, State Management, and Flow Chart ✅
- [x] Create state with dataset variables, node definitions, connections, and selection logic
- [x] Build responsive two-column grid layout (40%/60%)
- [x] Implement interactive flow chart with styled nodes and arrow connections using SVG
- [x] Implement click-to-select interactivity on nodes

## Phase 2: Data Table with Sorting, Search, and Polish ✅
- [x] Build reference data table with alternating rows, sortable columns, and search
- [x] Wire up dynamic filtering based on selected node from flow chart
- [x] Add Roboto font, final styling, and responsive polish

## Phase 3: Replace Flow Chart with Sankey Diagram ✅
- [x] Install plotly and replace SVG flow chart with Plotly Sankey diagram
- [x] Map existing nodes and edges to Sankey source/target/value format with financial flow values
- [x] Style the Sankey with custom node colors (#f0f4f8 nodes, #3a86ff links), proper labels
- [x] Wire up click interactivity: clicking a Sankey node updates the selected node and detail panel
- [x] Ensure responsive layout and visual polish

## Phase 4: Redesign for Variable Reconciliation Data (from Excel) ✅
- [x] Rewrite state to load the Excel file (test_var_rapprochement.xlsx) and parse the 4 columns: data_id, data_ref, % de rapprochement, raison du rapprochement
- [x] Build Sankey diagram with 3 layers: data_id (left) → reconciliation status (middle: "Rapproché" or "Nouvelle variable") → data_ref or "À créer" (right), using confidence % as link values
- [x] Color-code links: green for high confidence (≥95%), amber for medium (80-94%), red/grey for "nouvelle variable créée"
- [x] Redesign detail panel and table to show reconciliation data: data_id, data_ref, %, raison; with click interactivity on Sankey nodes

## Phase 5: Polish, Stats Cards, and Final UX ✅
- [x] Add summary stat cards: total variables, matched count, new variables count, average confidence %
- [x] Style the detail panel with confidence badges (color-coded), expandable reason text
- [x] Final responsive polish, empty states, and visual consistency
