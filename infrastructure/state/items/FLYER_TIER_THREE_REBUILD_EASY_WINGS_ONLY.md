# FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY

## spec
Split out of `FLYER_STABLE_BODY_GATE_1`. Members: the rows with this item in `design/RimMandrake/flyer_regen_plan.json`
(`flyer_gate.py refresh` rebuilds it). Recipe and gate: `design/RimMandrake/flyer_stable_body_study.md` section 3.1,
3.2. Prefer the cut-out recipe; a set needs a reviewed annotation per facing in `src/RimMandrake/Utils/art/flyer_cutout_sets/`
and a `DEF_SETS` row in `flyer_gate.py`. Held sets stay held behind `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES`.
Install through `art.py install` only. Never test flight live.

## criteria
Each set exits 0 from `flyer_gate.py flipbook <Set>` before anyone sees it; `flyer_gate.py audit --strict` stays 0.
Flight is verified by a `Pawn_FlightTracker` state read.
