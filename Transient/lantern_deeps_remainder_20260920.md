# Lantern Deeps remainder — 2026-09-20

## Summary

The Lantern Deeps biome build itself is DONE and DEPLOYED (CONFIRMED). What's left
is: one behavioral live-test debt on the fauna mechanics (bridge-gated, both items'
"not deployed" claim was false and corrected), one restart-timing debt on Twilight
fish (already correctly recorded, no action needed), and adjacent cut-fallout
cleanup that is FOUNDRY's, mid-work, and outside this mission's four items.

## Ranked remainder

1. **`CAVERNS_PARITY_BUILD_1`** — CONFIRMED done/deployed, ledger still says `doing`.
   No offline work left. Gated on: nothing — a close call, flagged for BENCH rather
   than closed by this subagent.
2. **`DEEPS_FAUNA_MECHANICS_1`/`_2`** — CONFIRMED built + deployed (deploy claims on
   both items were STALE/false, now corrected). Gated on: a LIVE bridge quicktest —
   the game must be up and driven; not offline-doable. `needs` retargeted
   deploy→bridge on both.
3. **`TWILIGHT_DEEP_WATER_LAYER_1`** — CONFIRMED fully built, ruled, deployed
   correctly on disk. Gated on: one more restart — this session's restart's def
   load ran before the deploy landed (documented accurately by FOUNDRY already,
   verified true, no correction needed).
4. **`DEEPS_FAUNA_VERDICTS_1`** — CONFIRMED closed and genuinely complete. Spot-
   checked `RUT_LanternDeeps.xml`'s `wildAnimals`: exactly the 8 kept kinds present,
   all 8 cut kinds and `RSW_RoyalRhino` (pack animal) absent, matching the frozen
   decisions file. Nothing unlanded.
5. **Adjacent, not in scope**: `CUT_FALLOUT_GENERATED_DATA_1` (FOUNDRY, `doing`,
   down to one design call — port-or-cut 3 `RUT_TheForge` flora refs) and
   `CANONICAL_SAVE_CUT_RESIDUE_1` (FOUNDRY, `proposed`, thin) are cut-fallout from
   this build, not part of its own criteria. Left untouched — FOUNDRY's, one
   already claimed/mid-work.

## What was finished this run

- **`CAVERNS_PARITY_BUILD_1`**: item file was empty (confirmed — file did not exist
  at all). Reconstructed from ~30 ledger events + the scoping doc into a real
  `## spec`/`## verify`/`## criteria`/status-log item. Established the build
  actually landed: Load C (2026-09-19, donor `Biomes! Caverns` absent, 621-mod
  full list) MEASURED 17/17 new defs present, 0/11 old (BMT_) names, 489
  lanternstone walls generating — the spec's own criteria, satisfied.
- **`DEEPS_FAUNA_MECHANICS_1`/`_2`**: verified the "DLL locked / not deployed"
  claim and found it FALSE as of now. MEASURED: live Mods-folder
  `RimMandrake.CreatureBehaviors.dll` md5-identical to the repo build; traces to
  deploy commit `6be013af0` ("Overnight BELT validation... CreatureBehaviors...
  0 typeload/patch_failed/recovery on a 15-mod minimal-list restart"), which
  postdates both items' own "not deployed" notes. `mandrake.rm.creaturebehaviors`
  is active in the live 617-mod `ModsConfig.xml`; `Player.log` shows no
  CreatureBehaviors XML/typeload errors. Corrected both item files (append-only
  correction sections, did not delete the original prose), filed ledger notes,
  and retargeted `needs` from `deploy` to `bridge` on both.
- **`TWILIGHT_DEEP_WATER_LAYER_1`**: read in full; already accurately documents
  itself (owner ruling "Just make the surface fishable" executed, patch deployed
  and byte-verified, but this session's restart read the biome before the deploy
  landed — needs one more restart). No correction needed; no offline work left.
- **`DEEPS_FAUNA_VERDICTS_1`**: spot-checked against the live `RUT_LanternDeeps.xml`
  biome def — confirmed genuinely complete, nothing unlanded.

## Commits

- `f6f76e552` — CAVERNS_PARITY_BUILD_1 item file reconstruction + MECHANICS_1/_2
  deploy-claim corrections.
- `e2de9b940` — rimflow ledger sync for the above (notes + needs retarget).

Both pushed to `main`.

## Claims, marked

- CAVERNS_PARITY_BUILD_1 build complete and deployed — **CONFIRMED** (Load C
  bridge measurement in the ledger, re-verified against `RUT_LanternDeeps.xml`
  on disk).
- DEEPS_FAUNA_MECHANICS_1/_2 DLL deploy debt discharged — **CONFIRMED** (md5
  match + commit trace + active ModsConfig + clean Player.log).
- DEEPS_FAUNA_MECHANICS mechanics not yet proven live — **CONFIRMED** (the
  item's own overnight bridge test found zero of three mechanics firing in
  ~2000 ticks; not re-tested this pass, bridge untouched per mission rules).
- TWILIGHT_DEEP_WATER_LAYER_1 needs one more restart — **CONFIRMED** as of the
  item's own 06:57 post-restart check this morning; did **not** re-check
  whether a later restart already picked it up (**UNCERTAIN** whether the
  currently-running session has it — not chased further, out of budget and the
  item already correctly names the gate).
- DEEPS_FAUNA_VERDICTS_1 fully landed — **CONFIRMED** (direct read of the live
  biome def file).
- CUT_FALLOUT_GENERATED_DATA_1 down to one design call — **CONFIRMED** by
  reading the item's own 2026-09-20 status entry (not independently
  re-measured this pass — out of the mission's four-item scope).
