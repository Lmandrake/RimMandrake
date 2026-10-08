# CORPSE_SITE_SAFETY_1 — Titan corpse-site conversion and harvest safety

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`), checked on code and on the 1.6 decompile (RimSage). The policy questions (body identity, rotten eligibility, extra products, toggle-off, damage, auto-harvest) are owner questions Q1–Q5 in the triage. Do not decide them here.

- **B3.1**: `Patch_Corpse_SpawnSetup_TitanicSite.Postfix` (`Patch_CorpseSiteConversion.cs:40`) runs `ConvertToSite`, which calls `corpse.Destroy()` (`TitanicCorpseSiteUtility.cs:75`) inside the corpse's own SpawnSetup. In 1.6, `Pawn.Kill` keeps using that corpse after placement (forbid, CompRottable, `lord.AddCorpse`, `DeathActionWorker.PawnDied`, `Notify_PawnDied`). Fix: queue the conversion on a map component for a later tick, then revalidate the corpse, map, tier and settings, and dedup.
- **B3.3 (mechanical half)**: `ConvertToSite` destroys the corpse and then ignores the `GenSpawn.Spawn` result (`:75-79`). In 1.6 the site is an edifice by default (`isEdifice` true), and `SpawningWipes` destroys any destroyable edifice under the 4×4. Fix: preflight the rect (in bounds, no edifice to wipe); on failure keep the corpse; destroy the corpse only after the site spawned.
- **B3.11**: `HarvestOneSession` decrements the pool (`Building_TitanicCorpseSite.cs:112,121`) before placement, and `JobDriver_HarvestTitanicCorpse.cs:211` ignores `GenPlace.TryPlaceThing`. In 1.6 that can return false with an unspawned remainder. Fix: commit only what was delivered and return the remainder to the pool.
- **B3.12**: `HasYield` (`:41`) is count-only, but a null `meatDef`/`leatherDef` (a removed mod) never drains. Fix: reconcile in `PostLoadInit` (zero the null pools, destroy an empty site) and log once.

## verify
Kernel/fuzz still pass. A save→load of a mid-harvest site preserves counts. Code reading shows Destroy is never reached before a successful spawn.

## criteria
A1: the four bullets are fixed. A2: the walk-plan corpse lane records conversion happening one or more ticks after death, with no wiped building under the footprint.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
