# SWEETLINE_WOOL_HARVEST_1 — the harvest the sweetline trees exist for is not built

## what is wrong

`design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4 defines the sweetline trees around a
specific reward:

> Giants rub against them, so the bark snags shed giant-wool — a rare hanging harvest for
> whoever dares the traffic.

MEASURED 2026-09-21 (found while designing the tree guardian): **there is no giant-wool def
anywhere in `src/`.** The only occurrence of the phrase is the prose above, quoted in a
comment in `src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml`.

Worse, `RUT_SweetlineTree` inherits `TreeBase`'s **wood** harvest with `HarvestDestroys`
true — so the only way to get anything off a sweetline tree today is to **fell it**. The
tree is a named, ancient landmark that roads follow. Felling it is the opposite of the
design.

## why this blocks something

🔴 The owner ruled on 2026-09-21 that the sweetline trees get a **generic guardian species**
(`SHRUBLAND_TREE_GUARDIAN_1`). The guardian's entire purpose is to make the harvest
dangerous — *"dares the traffic"*. **A guardian protecting a harvest that does not exist
guards nothing**, so this is a prerequisite, not a sibling.

## spec

1. A giant-wool item def. Precedent on disk: `RSW_WoolBantha`
   (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_Bantha_Items.xml`) — follow how we
   already do a wool item rather than inventing a shape.
2. A **non-destructive** harvest on `RUT_SweetlineTree` that yields it. ⛔ The tree must
   survive being harvested — override `TreeBase`'s `HarvestDestroys`.
3. Decide whether the wool accumulates over time (it is *shed* by passing giants, not grown
   by the tree) or is a flat plant yield. The fiction says the former; the cheaper build is
   the latter. Say which and why.
4. 🔑 Naming: the label is provisional either way — the giants themselves are under
   `ARIDSHRUBLAND_SHIPPING_NAMES_1`, awaiting the owner's pick from
   `Transient/shrubland_name_drafts_2026-09-21.md`. **Do not ship a wool name that hardcodes
   a giant name he has not chosen.**

## Watch out

- ⚠️ `RUT_SweetlineTree` already shipped (`TREE_GRAPHICS_OWNERSHIP_1`) as a `wildOrder: 4`,
  `wildClusterWeight: 0.05` plant. It is NOT hand-placed one-per-named-instance yet, so
  "every one has a name" is still aspirational — do not build anything that assumes named
  instances exist.
- ⛔ Check `infrastructure/artpipe/done/`, `_artsrc/` and `registry.jsonl` by subject before
  concluding any art is owed.

## criteria

A sweetline tree can be harvested for giant-wool without being destroyed, and the guardian
item has something real to guard.

## BUILT 2026-09-21

1. **`RUT_SweetlineWool`** (`src/RimUtinni/AshkarrFlora/Defs/ThingDefs_Items/RUT_SweetlineTree_Items.xml`,
   new file), `mandrake.rut.ashkarrflora`, `ParentName="WoolBase"`, shaped directly on
   `RSW_WoolBantha` (only texPath/color/statBases/stuffProps overridden, everything else — comps,
   thingCategories, stackLimit — inherited). Label "giant-wool" (matches the source fiction's own
   term verbatim). MarketValue 5.5, insulation stats set above vanilla's best (muffalo wool) —
   flavoured as a rare luxury hide.
2. **Non-destructive harvest**, on `RUT_SweetlineTree` itself
   (`RUT_AshkarrFlora_Plants.xml`): `harvestedThingDef` → `RUT_SweetlineWool` (was TreeBase's
   inherited `WoodLog`), `harvestYield` 160 → 20, and — the actual mechanism —
   `harvestAfterGrowth` 0.05 added (TreeBase never sets it, so it defaults to 0). MEASURED via
   RimSage against the decompiled engine: `PlantProperties.HarvestDestroys => harvestAfterGrowth
   <= 0f`, and `Plant.PlantCollected` checks `HarvestDestroys` FIRST — when false it never reaches
   `Destroy()`/`TrySpawnStump()` at all, for EITHER the Harvest or the Cut Plant job (both route
   through the same method), it only resets `growthInt = harvestAfterGrowth`. So this one field
   makes the tree unfellable by any normal player action, not just "safe from the harvest button" —
   exactly the spec's "the tree must survive being harvested." Also added `harvestTag="Standard"`
   (off the inherited "Wood") + `forceIsTree="true"` (since `PlantProperties.IsTree` is
   `harvestTag == "Wood"` with no other test) so the tree keeps registering as a tree everywhere
   else in the engine (wind-block, roof interference, etc.) despite no longer yielding wood.
3. **Accumulate, not flat — decided and recorded.** Chosen because (a) it is the literal fiction:
   wool is *shed* by passing giants over time, not grown by the tree, and (b) it was the CHEAPER
   build here specifically, not the more expensive one — `harvestAfterGrowth` is a single existing
   `PlantProperties` field with two precedents already in this same mod file (`RUT_Fuzz`,
   `RUT_Staggerseed`), so "accumulate" cost zero new code against "flat" costing nothing less.
   Regrow pace: `growDays * (harvestMinGrowth − harvestAfterGrowth)` = `240 * (0.40 − 0.05)` =
   **84 in-game days (~1.4 years)** before a stripped tree is harvestable again — reads as "rare."
   ⚠️ `sweetline_guardian_spec.md` §11.3 separately suggested pacing this to a future guardian
   roost's 8–14-day respawn; that ruling did not exist yet when this was built (only as an open
   question), so the two are NOT reconciled — flagged on that spec for whoever picks up
   `SHRUBLAND_TREE_GUARDIAN_1` next.
4. **Visual-size check (not assumed):** `RUT_SweetlineTree`'s `visualSizeRange` (7.7~10.0) already
   has a high floor for the "never small trees" ruling — `Plant.cs` interpolates draw size across
   the WHOLE 0→1 growth range (`LerpThroughRange`), so a freshly-stripped tree at growth 0.05
   renders at ~7.8 of 10.0 tiles, not a shrunken sapling. Confirmed via RimSage before committing
   to the low `harvestAfterGrowth` value, not assumed.
5. **Naming**: provisional, built off "sweetline" (the tree's own already-shipped, stable name)
   and the fiction's own generic term "giant-wool" — never off a giant species name, since the
   giants are still unnamed (`ARIDSHRUBLAND_SHIPPING_NAMES_1`). No rename owed when that lands.
6. **Art: owed, not filed.** Checked `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl`
   and `art_status.json` by subject first — no "wool"/"giant-wool"/"sweetline wool" hits anywhere
   (the only "giant*" art on disk is unrelated giant-fungus/flower plant renders). Codex is
   quota-blocked until ~2026-09-26, and this item's brief scopes pending/active/registry files as
   out of touch for this pass — so no job was filed. `texPath` points at
   `Things/Item/Resource/RUT_SweetlineWool` (will read as missing until a job is filed and lands),
   the same "job not yet filed, texPath points at the future location" convention already used
   twice in this mod (`RUT_Fuzz`, `RUT_StaggerseedFruit`).
7. **Corrected two stale docs found while touching this ground** (each was asserting the pre-change
   field values as current): `src/RimUtinni/AshkarrFlora/validation.py`'s `EXPECT_FIELDS` (also
   fixed an unrelated pre-existing drift, `visualSizeRange` still said "5.0~6.5" though the def has
   read "7.7~10.0" since `ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1`) and
   `design/validation_walks/RimUtinni/AshkarrFlora.md`'s walk steps 3/5 (same two facts). Also
   corrected `sweetline_guardian_spec.md` §11.3, which said the harvest "is not built" — see #3
   above for the reconciliation flag left in its place.
8. **Selftests**: `run_selftests.py` — see commit for N/N result.
9. **`SHRUBLAND_TREE_GUARDIAN_1`** unblocked: the harvest it needs to guard now exists.
