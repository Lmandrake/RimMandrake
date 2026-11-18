# FLYER_TIER_TWO_REBUILD_KEPT_NEW_WINGS

## spec
Split out of `FLYER_STABLE_BODY_GATE_1`. Members: the rows with this item in `design/RimMandrake/flyer_regen_plan.json`
(`flyer_gate.py refresh` rebuilds it). Recipe and gate: `design/RimMandrake/flyer_stable_body_study.md` section 3.1,
3.2. Prefer the cut-out recipe; a set needs a reviewed annotation per facing in `src/RimMandrake/Utils/art/flyer_cutout_sets/`
and a `DEF_SETS` row in `flyer_gate.py`. Held sets stay held behind `FLIER_FRAMES_AUDIT_BODY_NOT_WING_EXTREMES`.
Install through `art.py install` only. Never test flight live.

## criteria
Each set exits 0 from `flyer_gate.py flipbook <Set>` before anyone sees it; `flyer_gate.py audit --strict` stays 0.
Flight is verified by a `Pawn_FlightTracker` state read.

Known: Sketto east fails exact equality on 1 px, a master pixel of alpha 251 at the hinge. Fix the master pixel or the rule, do not repaint.

## proof (corrected 2026-11-17, drain of the retired judge)
Both legs of the `## criteria` above, run with the CV interpreter (the gate imports numpy/pillow/cv2; under a
bare system python3 it crashes on the import before reaching any check, which is an interpreter artifact and
not a defect):

    "$RM_CV_PYTHON" src/RimMandrake/Utils/art/flyer_gate.py flipbook <Set>     # once per set
    "$RM_CV_PYTHON" src/RimMandrake/Utils/art/flyer_gate.py audit --strict

## what it reads, measured 2026-11-17
All NINE flipbooks exit 0 — PASS. `audit --strict` exits 1 on exactly one line:

    BAD Aiwha: in the plan, no longer a flyer

Aiwha is a donor-bundle row whose defs live in Steam workshop mod 3497316713 under C:\, which is absent on
this host, so the census cannot see the def and reports it as no-longer-a-flyer. That is the instrument
failing to look, not a flyer that regressed: UNMEASURED, not a fail. No other row is red.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/FLYER_TIER_TWO_REBUILD_KEPT_NEW_WINGS.txt

Next worker: run `audit --strict` on the Windows bench, where the donor mod is installed, and confirm the
Aiwha row reads. The criteria say audit --strict STAYS 0, so one unread row is not a pass. Flight itself is
never live-tested (standing ruling).
