# BLUEDESERT_ORPHAN_LOAD_CRASH_1 — full-list load aborted, RimWorld reset ModsConfig to Core-only

## What happened, 2026-09-27 ~05:15Z

A FOUNDRY subagent working `BIOME_DEFNAME_MIGRATION_WAVE_1` took the bridge for a
live tile-count read and found RimWorldWin64 non-responsive for ~2 hours (recorded
`LOADING`, bridge never came up). This window force-killed it, harvested the dead
`Player.log`, and relaunched clean via Steam per standing FOUNDRY restart
authorization. **The relaunch also failed to load the full list**, and RimWorld's
own recovery kicked in: `Caught exception while loading play data but there are
active mods other than Core. Resetting mods config and trying again.` —
**`ModsConfig.xml` was rewritten to 6 mods (Core-only)**, live-observed and caught
within minutes.

🔴 **Recovered**: restored the full 630-mod list from
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (confirmed matching the
pre-crash count cited elsewhere in tonight's session) before anything else touched
`ModsConfig.xml`. Confirmed the restore held after killing the Core-only process.

## Root causes found, both fixed

1. **`RM_SapSuckerGuild.xml`** (FeverWood) referenced
   `RimMandrake.EnvironmentalHazards.RM_CompProperties_GatherableCalmGated` — the
   real compiled class is `CompProperties_GatherableCalmGated` (no `RM_` prefix;
   `RM_CompGatherableCalmGated.cs` never named it that way). A genuine typo, not a
   deploy-currency issue. Fixed, deployed, committed at `73c920d7a`
   (published via `shared_sync.py` as `24a75dace` — content-verified on
   `origin/main`, the replay changes the SHA).
2. **Three stray orphaned def files deployed under
   `Mods/UtinniPatches/Defs/{ThingDefs_Plants,ThingDefs_Races,HediffDefs}/
   RM_BlueDesert{Flora,Fauna,Charges}.xml`** — no repo source anywhere under
   `src/RimUtinni/UtinniPatches/` (confirmed by grep). These are leftover deploy
   debris from before BlueDesert became its own standalone `mandrake.rm.bluedesert`
   mod (the stray copies' own header comments say "RM_ tier — see
   BlueDesertLife.cs's header for why this lives here **for now**"). They referenced
   old/renamed class names (`RM_CompRuinedDetonator`,
   `HediffCompProperties_ExplodeOnPartDestroyed`, `RM_IngestionOutcomeDoer_ButaneGut`,
   `RM_HydrocarbonNativeExtension` — all of which exist correctly under
   `RimMandrake.BlueDesert.*` in the CURRENT, correct, standalone BlueDesert mod)
   and threw "Could not find type" on load. **Deleted directly from the deployed
   Mods folder** (not `--prune`, which is mod-wide and would have swept many other
   "in game, not in repo" entries under UtinniPatches that were NOT investigated —
   see follow-up item). No repo change needed; these files were never tracked.

## The ACTUAL fatal crash — a third, unrelated root cause (fixed, proven)

The two fixes above were real defects but **did not cause the reset**. The
relaunch log (harvested `Player_fulllist_recipedefgen_crash_20260927T055242Z.log`,
not tracked) dies in `RecipeDefGenerator.SetIngredients` →
`ThingFilter.SetAllow(null)`: a ThingDef with a `recipeMaker` whose `costList`
names a def that does not exist. Found offline by scanning every active mod's
Defs + Patches for costList refs to non-existent ThingDefs:

- `UtinniPatches/Patches/RUT_Bitumen_KorvethSource.xml` added a recipe to
  `RUT_Bitumen` costing `RM_KorvethPitch`, and
  `RUT_ThrummelSeepwax_RosterSource.xml` added one to `RUT_ThrummelSeepwax`
  costing `RM_Seepwax` — both defs live in `mandrake.rm.thesump`, **which is
  not in the 630-mod list**. Both shipped 2026-09-26 at `6714ad67c`.
- Their guard was `<Operation ... MayRequire="mandrake.rm.thesump">`, and
  🔴 **vanilla ignores MayRequire on a top-level `<Operation>`** (MEASURED from
  the decompiled engine: `ModContentPack.LoadPatches` builds every Operation
  unconditionally; MayRequire is honoured only on defs, def-ref fields and
  list items). So the patch applied, the costList cross-ref resolved to null,
  and the NRE tripped the corrupted-mods reset.

Fix `99776e796`: gate each Conditional on the donor def existing
(`/Defs[ThingDef/defName="RM_KorvethPitch"]/ThingDef[defName="RUT_Bitumen"]`),
MayRequire removed. Deployed. **Proved by a monitored full-list cold load
2026-09-27 06:14Z→06:32Z: `Bridge token:` reached, zero reset/recovery
strings, `ModsConfig.xml` byte-identical to `ModsConfig.FULL.LATEST.xml`**
(log harvested as `Player_fulllist_clean_after_sumpgate_20260927T063252Z.log`).
`Failed to patch VFEInsectoids 2's Creep with additional genes.` appears in the
clean load too — it was adjacent noise, not causal.

**Left for others (not this item's fix):** ~74 more top-level
`<Operation MayRequire=…>` guards in `src/` are equally inert — filed as
`PATCH_MAYREQUIRE_GUARD_INERT_1`. And `mandrake.rm.thesump` and
`mandrake.rm.bluedesert` are both built but absent from the canonical list
(so `RUT_PropaneLakeFauna.xml` and a stray deployed
`UtinniPatches/Defs/ThingDefs_Items/RM_ColdWax.xml` still log non-fatal
"Could not find type RimMandrake.BlueDesert.*" and their defs are discarded) —
whether those mods join the list is a BENCH call.

## Why this matters beyond tonight

`deploy_custom_mods.py`'s own plan output (full run, no `--mod` filter, this
session) lists a long tail of "in game, not in repo; kept" entries under
`UtinniPatches` alone — placeholders, weather defs, patches, a texture — none of
which were investigated here. **Any one of them could be the next silent
`ModsConfig.xml`-wiping landmine** if it references a class that's since been
renamed or removed. See `UTINNIPATCHES_ORPHAN_AUDIT_1` (filed alongside this item)
for the actual audit — deliberately NOT done here, to avoid a blind `--prune`
sweep deleting something still load-bearing.

## verify
Confirmed: `ModsConfig.xml` holds 630 mods again (matches
`ModsConfig.FULL.LATEST.xml`); the 3 stray files no longer exist in the deployed
Mods folder; the FeverWood fix is deployed and pushed. **Not yet confirmed**: a
clean full-list cold load — that's the next game-up window's job, and it should
be the very first thing checked (bridge/log watch for the same abort string)
before any other game-up work rides along.

## criteria
- [x] Next full-list cold load reaches `UP` cleanly (bridge token appears,
      `Player.log` shows no "Caught exception while loading play data" /
      "Recovered from incompatible or corrupted mods errors").
- [x] `ModsConfig.xml` restored to the pre-crash 630-mod list.
- [x] Both identified root causes fixed/removed.
