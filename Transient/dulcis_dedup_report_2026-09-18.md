# DEEP_DULCIS_DEDUP_1 — LanternDeeps stops shipping RUT_DeepRawDulcis

## Changes

- `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Items/RUT_LanternstoneItems.xml` — deleted the `RUT_DeepRawDulcis` ThingDef outright; rewrote the file-header comment to drop the now-false claims about it.
- `src/RimUtinni/LanternDeeps/Defs/ThingDefs_Plants/RUT_DeepFlora.xml` — `RUT_DeepDulcisPlant.harvestedThingDef` now `RUT_RawDulcis`; updated header comment note 2.
- `src/RimUtinni/LanternDeeps/Defs/Biomes/RUT_LanternDeeps.xml` — `foragedFood` now `RUT_RawDulcis`.
- `src/RimUtinni/LanternDeeps/About/About.xml` — added `mandrake.rut.rotsporekit` ("RimUtinni: Rot Spore Kit") to `modDependencies` and `loadAfter`; existing entries kept.
- No `.cs` change needed: `GenStep_DeepFloraGate.cs` only references the plant defName `RUT_DeepDulcisPlant`, not the raw item.

Stat comparison RUT_DeepRawDulcis vs RotSporeKit's RUT_RawDulcis: identical (MarketValue 1.2, Mass 0.027, same CompProperties_Rottable 16-day rot, same ingestible RawTasty/Fungus, same ingredient mergeCompatibilityTags). Only differences were texPath and flavor-text description — no mechanical/balance change from the swap.

## Deploy

Dry run (`deploy_custom_mods.py --mod LanternDeeps`) showed only XML drift, no DLL line:
```
LanternDeeps     mandrake.rut.lanterndeeps
    ~  About/About.xml
    ~  Defs/Biomes/RUT_LanternDeeps.xml
    ~  Defs/ThingDefs_Items/RUT_LanternstoneItems.xml
    ~  Defs/ThingDefs_Plants/RUT_DeepFlora.xml
```
Since the DLL was untouched, ran `--apply`. Result: "Deployed 4 file(s). VERIFIED in sync." Requires a RimWorld restart to take effect (defs parse at startup only).

## Verification

- `validate_patch.py` against the 3 edited Defs files with `--live` pointed at the `2026-09-18T21-57-04Z` dump: 0 errors, 14 warnings — all pre-existing `texPath` advisories on unrelated plants (this mod's loose textures aren't scanned that way); nothing new from this change.
- Confirmed `RUT_RawDulcis` is present in the live dump's `ThingDef.json` (grep hit).
- `xml.etree.ElementTree.parse()` succeeded on all 4 edited files (2 ThingDef/plant files, biome file, About.xml).
- Grepped the whole repo (`src design infrastructure skills`) for `RUT_DeepRawDulcis`: only remaining hits are outside scope — ledger/queue/handoff docs describing this very item (historical record, not touched) — no other mod or design doc references the removed def.
- `GenStep_DeepFloraGate.cs` only references the plant defName `RUT_DeepDulcisPlant` (unchanged), no raw-item reference to fix.

## Open

- Requires a game restart before the swap is live (deploy tool's own note).
- Ledger/queue docs referencing `RUT_DeepRawDulcis` (EXPECTED_FAILURES_next_load.md, BENCH/FOUNDRY handoffs, BENCH.md queue, events.jsonl) are historical record and out of this item's file scope (`src/RimUtinni/LanternDeeps/` only) — left untouched; closing DEEP_DULCIS_DEDUP_1 in the ledger is a separate rimflow action, not done here.
- No stat/gameplay change from the item swap (identical stats/comps); only flavor-text description differs.
