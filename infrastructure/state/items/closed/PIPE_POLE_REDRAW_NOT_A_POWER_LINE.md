---
state: proposed
needs: offline
---

# PIPE_POLE_REDRAW_NOT_A_POWER_LINE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Pipe poles read as an electric line: GSS AerialMast placeholder art (insulators), span drawn as GSS's dark aerial cord instead of the look's pipe, and ground pipes stop with end caps short of the pole (pole is not a join partner, no riser). Fix: own PipePole/<Look> art, span in the look's pipe atlas at pipe girth, pole as PartnerAt + base elbow/riser. Defect D5 in Transient/pile_2026-10-22/joints_study.md; shot joints/sheet_F.jpg

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show PIPE_POLE_REDRAW_NOT_A_POWER_LINE` history before building.

## latest ledger notes

- 2026-10-23: Area F 2026-10-23 status: span half DONE (per-look FlowWorks PipePole/<Look>/PipeSpan.png; span follows the pole's drawn style since 2ae04e1509). Still owed, all FlowWorks files: own PipePole/<Look>/PipePole art (RM_PipePoles.xml texPaths still point at GSS Aerial/Styles/<Look>/AerialMast, insulators) and the base riser/join = MAST_PIPE_MEND_STOPS_SHY.
- 2026-10-29: Done when: pipe poles use own PipePole/<Look> art (not GSS mast), spans follow the look, and ground pipes reach the pole base via an inset/riser; judged in game.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify PIPE_POLE_REDRAW_NOT_A_POWER_LINE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=PIPE_POLE_REDRAW_NOT_A_POWER_LINE` first: another commit may already do it.
