# FlowWorks Hose review night log 2026-10-17 (scratch clone review_hose, base 54f5c85bf)

- scope: 22 .cs under Source/Hose (incl. Jobs); 19 already CLEAN skipped; DIRTY: RM_HoseLegacyMath.cs, HoseMath.cs, Jobs/JobDriver_CarryHoseEnd.cs
- RM_HoseLegacyMath.cs (130): read whole; nothing (TryFloat rejects NaN/Inf as the 8eeb3eaa7 fix intended; PickFile deterministic tie-break). CLEAN.
- Jobs/JobDriver_CarryHoseEnd.cs (252): read whole; nothing (global FailOn order guards Reel null before Reel.carry; OnFinish paths cover unreachable/non-carrying; setDown duration override read at start). CLEAN.
- HoseMath.cs (1489): read whole. Doubts decided NOT A BUG: RouteCells prune uses path length not cost (install passes costs=false, so exact); open-set removal key matches insert key (same expression); Dubins words are integration-verified so a wrong formula can only drop a candidate; ResampleN callers all n>=8, >=2 pts; Joints index k safe via Count check short-circuit; FiniteClamp NaN fix correct. No change. CLEAN.
- no code changed; marks recorded in infrastructure/state/code_review/FOUNDRY.jsonl
