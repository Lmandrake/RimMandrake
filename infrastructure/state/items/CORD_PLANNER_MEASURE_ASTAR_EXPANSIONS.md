---
state: proposed
needs: offline
---

# CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Add an A* node-expansion counter to _Shared/SlackGeometry/CordPlanner.cs (and HoseMath.CheckReplan) that the hose replay harness reports and ceilings per scenario; left out of the harness build because CordPlanner is shared by GSS and FlowWorks DLLs and a change would stale both srchashes during the live tuning

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS` history before building.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=CORD_PLANNER_MEASURE_ASTAR_EXPANSIONS` first: another commit may already do it.
