# PYRELANDS_NORTHSTAR_TRIAL_1 — carry Pyrelands up the north-star ladder to SHIPPED (the biome template)

**For:** FOUNDRY. **Plan (the authority):** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md`, GPT-reviewed (§8).

Owner, 2026-09-30, typed: *"Yes. Write out comprehensive northatar plans for all three and ticket
them out as trials for full completion. Use gpt reviews for their validation plan especially site
preparation that's often overlooked before a proper test setup. I'd like this to go very well. Then
use ultra fast python to drive the bridge to validate. Make it happen!"*

Pyrelands is the first biome taken end to end. About twenty others will copy its pattern (plan §6),
so record every deviation from the plan back into it.

## Dependency — BIOME_MOD_UNIFICATION_1

Pyrelands ships **inside `mandrake.rm.biomes`** (compose wave 2; `BAROQUE_BIOMES_WAVE2_FOLD_1`
closed 2026-09-28). Every rung tests the composed mod, never `mandrake.rm.pyrelands`. If
unification's packaging changes again (a compose-wave change, a renamed key, per-biome mechanic
gating), re-check plan §1.1 before running any rung.

## Rungs (child items, in order)

1. `PYRELANDS_NORTHSTAR_VALIDATE_1` — owner re-validates the 10 bars (+ proposed additions). Currently effectively DRAFT: hash mismatch since `b3457a829`.
2. `PYRELANDS_NORTHSTAR_WIRING_1` — every bar gets a `shows=` component; fix the suite bugs in plan §2.3/§2.3a; fix the stale walk header outside the hash.
3. `MODCHECK_COMPOSED_BIOMES_LIST_1` — modcheck cannot build a test list for a composed biome (shared by all biomes).
4. `PYRELANDS_GREEN_MINIMAL_1` — GREEN on the `pyrelands` tier, with pre-flight gates A/B/C.
5. `PYRELANDS_GREEN_FULL_1` — GREEN on the full list, using a freshly generated full-list site.
6. `PYRELANDS_SHIP_READINESS_1` — art, code review CLEAN, Mod Settings superb, deployed.

The shared bridge driver is built separately at `src/RimMandrake/Utils/northstar_driver/`. Plan §7
lists what Pyrelands needs from it.

## verify

- `modcheck status` shows Pyrelands GREEN on the full list, with `[stored: …]` drift absent.
- Every child item is closed against a sha.
- `code_review_status.py check` is CLEAN on every Pyrelands source file.
- No magenta (missing-texture) art on any roster creature.
