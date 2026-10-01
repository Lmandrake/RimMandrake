# FLOWWORKS_NORTHSTAR_WIRE_1

Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §2.

`src/RimMandrake/FlowWorks/validation.py` is the OLD Pits suite moved in unchanged (`Suite("Pits")`,
four PitsSettings toggles, building-pit chains) — MEASURED 2026-09-30. No canal/depth/stock/superdeep
component exists. FlowWorks ships 27 boolean toggles (MEASURED).

## acceptance
- `validation.py` rewritten: `Suite("FlowWorks")`, `suite.toggles` = all 27 toggles, one component per
  visual bar (§2.3/§2.4, after REVALIDATE) and per toggle (§2.5 predicate table), on the plot scheme.
- `python3 -m modcheck.cli floor --all` FlowWorks row: 0 uncovered must-show, 0 orphan `shows=`, toggle floor met.
- The three `(change)` bars captured as a diptych/four-panel composite (§2.1); each component nominates exactly one evidence frame.
- Walk steps 4–6 rewritten against `jawa/flowworks_excavation_drive` / `_report` (`canal_dig` is a stub that always fails).
- `run_selftests.py` green; new/changed files reviewed full-file and `mark-clean`ed.
- Never calls the live game; wiring is offline.
