# SUMP_FLORA_ROSTER_1 — build the 10 invented Sump flora defs

Source: `design/Jawa/worldbuilding/biomes/sump_flora_roster_2026-09-24.md`
(10 rows, all `RM_` tier, franchise-free — the doc's own collision sweep
found 0 hits on any of the 9 new names anywhere in the repo). Row 1
(wick-plant) already ships as `RUT_Plant_Wick`/`RUT_WickStem`
(`SUMP_MECHANICS_1`); this item builds rows 2-10.

## Built this pass

- `src/RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_SumpFlora.xml` — 9 new
  PlantDefs: `RM_Dorvel`, `RM_Skelver`, `RM_Korveth`, `RM_Brindeth`,
  `RM_Soffeth`, `RM_Tolleth`, `RM_Velloch`, `RM_Mirrelin`, `RM_Pallick`.
- `src/RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFloraItems.xml` —
  harvested goods `RM_RawDorvel`, `RM_RawSkelver`, `RM_KorvethPitch`
  (brindeth harvests vanilla `WoodLog` directly, no new item).
- `RM_TheSump_Biome.xml`: `<wildPlants>` rewired — `AB_TarPuddle` (donor,
  0.6) replaced 1:1 by `RM_Velloch` (0.6, doc-named); the other 8 rows added
  plus a first wild-presence row for the already-shipped `RUT_Plant_Wick`
  (0.03, "starter stock" per the doc). Also fixed `plantDensity` 0.15->0.25
  and `forageability` 0.0->0.8 — both contradicted the frozen sheet's own
  ruling (`the_sump.md` §0) and the `RUT_Sump` twin's own header comment two
  lines above its (also-wrong) fields; the twin itself is untouched.

## Assumptions (design doc did not name a number)

Only `RM_Dorvel` (0.05) and `RM_Velloch` (0.6, matching the `AB_TarPuddle`
row it replaces) have doc-named commonalities. The remaining 7 wildPlants
commonalities and every growDays/harvestYield/statBase field are
INVENTED-BUILD values following the doc's descriptive rarity/growth language
(dorvel "slow-growing by ruling" -> growDays 22; skelver "baseline green" ->
highest wild commonality 0.4; tolleth/pallick "rare marker" -> lowest, 0.03
and 0.05) — not sourced to a named figure. Full rationale is in
`RM_SumpFlora.xml`'s own header comment.

## Deferred — mechanism work, not flora defs (doc §6)

Three placement/behaviour mechanisms the doc marks NEW/PARTIAL are **not**
built here — they are gameplay-mechanism/GenStep work, out of a flora-def
item's scope, and each plant ships fully authored and inert without them:

- `RM_Pallick`'s false-floor collapse comp (on pawn entry: deep-tar terrain
  + mire, never lethal alone).
- `RM_Soffeth` placement biased to gas-seep map cells (GenStep scatter rule;
  no gas-seep layer exists yet).
- `RM_Tolleth` placement biased to dig-lottery-rich cells (GenStep reading
  `RM_LotteryTableDef`).
- `RM_Mirrelin`/`RM_Pallick` terrain-gating to a "cooled tar" vs "soft tar"
  distinction — `RM_TarPan`/`RM_TarLoam` (the doc's own §5 proposed terrain
  names) do not exist yet; terrain authoring is out of this item's scope.

These four are real follow-on work; whoever picks up Sump terrain/mechanism
work next should read `sump_flora_roster_2026-09-24.md` §6 rather than
re-deriving them.

## Art

Searched `infrastructure/artpipe/registry.jsonl`, `done/`, `_artsrc/` for all
9 new names plus "wick" as a sanity probe (0 hits on every one — nothing
pre-generated). Queued 9 `fill_queue.py` jobs
(`infrastructure/artpipe/pending/RM_<Name>_a.json`, `rimflow_item_id
SUMP_FLORA_ROSTER_1`, 256x256, single facing — plants don't need
directional art). All 9 new defs are `DEPLOY_HOLD`'d (`src/DEPLOY_HOLD.txt`)
until their art lands.

## Verify

`validate_patch.py --defs` run against the live Mods + Workshop content
roots; see commit for the result at time of close.
