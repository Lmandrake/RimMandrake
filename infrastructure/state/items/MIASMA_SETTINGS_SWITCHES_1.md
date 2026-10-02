# MIASMA_SETTINGS_SWITCHES_1 — Mod Settings switches for plant predation, the pollination gate and the stranded deformation

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (e), §4 row 0a. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Under the standing Mod Settings law (owner, 2026-09-12; `MOD_OPTIONS_RETROFIT_1`), not a card pick.

## What exists
`RM_MiasmaMod.cs`: rarity, warden succession, self-tame chance; the shared kit's screen has surge, weather pulse, hazard damage.

## spec
On/off for `RM_CompPlantPredator`'s predation, the pollination gate (after `MIASMA_SWARM_COMPOSTER_PORT_1` moves it here) and the
stranded deformation (with its chance as a slider). Defaults are shipped behaviour; all off degrades gracefully.

## criteria
- Each switch off: the mechanic does not fire in a quicktest; no error.
