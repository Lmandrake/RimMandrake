## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Polish**, bar `visitors, temperament, sits_on_wall, stories_not_tax`.

**Criterion:** T_FUZZ supports these bars (it decides none of them; their deciders are live scenes)

**Evidence:**
- planted PF_K_VISIT_CAP_FORGETS, PF_K_PSYCHOPATH_HALF_FEELS, PF_K_EDGE_ON_PAINTS, PF_K_BUDGET_UNCAPPED: T_FUZZ green, lane 1 red (lane2/planted_results.jsonl)

**Smallest fix:** add VisitCharge, Combine's numb, PaintsEdgeOn and FitBudget cases to GraffitiFuzz.cs (lane1/BlindLane1.cs has the properties)

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
T_FUZZ red on each of the four

## verify
Acceptance test: for each of PF_K_VISIT_CAP_FORGETS, PF_K_PSYCHOPATH_HALF_FEELS, PF_K_EDGE_ON_PAINTS, PF_K_BUDGET_UNCAPPED, `python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/catch_check.py --fault <id> --test T_FUZZ` rc 0 (4 passes). Fails on the base today (T_FUZZ green on each: `lane2/planted_results.jsonl`).
