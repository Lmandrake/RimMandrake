# GRAFFITI_NORTHSTAR_TRIAL_1

Owner, typed 2026-09-30: *"Yes. Write out comprehensive northatar plans for all three and ticket them out as trials for full completion. Use gpt reviews for their validation plan especially site preparation that's often overlooked before a proper test setup. I'd like this to go very well. Then use ultra fast python to drive the bridge to validate. Make it happen!"*

**The plan is `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`.** Read it first. It has been GPT-reviewed: 59 findings, accepted and rejected
findings listed in its §7. Prompt and answer are in `Transient/northstar_trials_gpt/graffiti.*.md`.

Graffiti is the **pipeline pilot**, the first mod meant to reach GREEN. Rungs, each its own item:
1. `GRAFFITI_NORTHSTAR_WIRED_1`
2. `GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1`
3. `GRAFFITI_NORTHSTAR_GREEN_FULL_1`
4. `GRAFFITI_NORTHSTAR_SHIP_1`

VALIDATED is already done (2026-09-16, hash matches; MEASURED 2026-09-30).

## State, MEASURED 2026-09-30
- The floor reads VALIDATED, 8 must-show ids uncovered → REFUSED.
- `validation.py` counts only `RM_Graffiti_Vandal`, but the spree paints from a weighted pool. That
  is a false-fail.
- 38 mark defs have **no texture** in `Textures/`. Their art sits generated in
  `infrastructure/artpipe/_artsrc/` (graffiti_*, glyph_*) and is not wired.
- The DLL has no `.srchash`.
- All 19 `.cs` + `validation.py` are CLEAN.

## Open question for the owner (from GPT #59; do not implement without his word)
Should the one-time owner sheet review lapse when the art, DLL, walk or judge changes?

## Hashed-prose correction owed (needs his word, same sitting)
The plan's §5.7 proposes replacement text for the north-star subsection "what this checklist refuses
today", which is stale state-dependent prose. **No bar text changes.**

## close when
All four rung items are closed.
