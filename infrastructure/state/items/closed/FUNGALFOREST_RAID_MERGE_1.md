# FUNGALFOREST_RAID_MERGE_1 — dissolve BMT_FungalForest into its neighbors; ingest its content into the Rot

Owner ruling 2026-09-06: no basement biome — "raid this biome for its cool contents… then
merge this biome with its neighbors sensibly and in a nonbullseye manner."

## spec — the merge (MEASURED per cluster: region × 30° sector, the dominant OTHER biome in
the same region within ±6° of arc)
| cluster | tiles | arc | receiver |
|---|---|---|---|
| Sporefields, sector 2 | 85 | 94 | **the Rot** (`AB_MycoticJungle`, 130 neighbors) |
| Nightspill, sector 7 | 69 | 118 | the Rot (236) |
| South Crags, sector 8 | 62 | 119 | the Rot (38) over Wasteland (37) — split by local majority per tile |
| Sweatwood, sector 7 | 44 | 81 | the Rot (45) |
| Nightspill, sector 6 | 38 | 118 | the Rot (235) |
| Stillwood, sector 3 | 33 | 128 | the Rot (88) |
| Frostcaps, sector 3 | 30 | 122 | the Rot (129) |
| South Crags, sector 9 | 16 | 124 | **the Wasteland** (67; the dissolved ring 58 goes to its own receivers) |
| Stillwood, sector 2 | 16 | 130 | the Rot (93) |
| Blindwood 5 · Stepwood 7 · Hanging Wood 9 | 26 | — | the Rot |
- Every cluster takes its own neighbors — the merge follows the terrain map, adds no
  ring (the Rot already sits in 7 sectors as lobes; it grows by ~400 tiles). Re-count
  the Rot's sector coverage after painting and record it.
- Re-biome via world tools + `world_commit`; re-freeze; back up Saves keepers; render for
  the owner before painting (patch-a-curated-artifact rule).

## spec — the raid (`the_rot.md` §7b)
- Ingest the spore kit (DamageDefs, SporeCloud incident/condition, SporesBuildup,
  SporeFlesh, thrumbungus, mantis scythe), materials/terrains (mushroom leather, bridges,
  mycelial soil/matting), buildings (fungiponics, fungal torches), research row, drugs
  (ambrosyx), flora (marsh fungi, Skultop, morel, inkcap…) — as OUR defs under the tier
  grammar (`RSW_`/`RUT_`), art referenced by texPath per the absorption precedent;
  Cherry Picker the originals if the mod stays installed.
- 🔴 Ruled 2026-09-06: blastpod→chemfuel ingested WILD-ONLY (no sow tags for Jawa; may be
  cut later if hokey); the fungal power generator (`BMT_FungalPowerGenerator`) is CUT —
  do not ingest, Cherry Picker it if the mod stays installed.
- Fauna admission at `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (hybrid-or-out list in §7b).
- Verify the Skultop's actual defName (UNMEASURED in 1.6 defs) before citing it.

## verify
CSV re-count: 0 `BMT_FungalForest` tiles; receivers as tabled; the Rot's sector coverage
recorded; ingested defs resolve in the dump; the owner has ruled the two flagged chains.

---

## ⛔ THE CLUSTER-SPEC TABLE ABOVE IS SUPERSEDED — owner, 2026-09-07 (R29)

**Ruled: follow the paint.** The per-tile neighbour analysis wins over the
cluster-spec table. In particular the **South Crags sector 9** tiles (16) go to
**BiomeGRimond (Blue Desert)** / **AB_RockyCrags (Forsaken Crags)** — whichever
actually surrounds each — **not to Wasteland**.

🔑 **The principle: a merged tile must be continuous with its new biome.** A
16-tile Wasteland enclave with no Wasteland adjacent to it reads as an error to
anyone who opens the map later.

✅ **The 15 flagged ties are settled by the same rule** — majority adjacent
biome, broken by closest temp/rain match. No separate ruling owed.

## MEASURED plan

`design/Jawa/worldbuilding/data/fungalforest_merge_plan_2026-09-07.md` — 425
tiles carrying `BMT_FungalForest`, arc 74.0–132.9, temp −43.9 to 24.3 °C, rain
0–14 mm. Method: 216 tiles resolved by direct non-FungalForest neighbour
(majority vote, temp/rain tie-break); the 209 interior tiles by multi-source BFS
to the nearest resolved tile. **Zero unreachable, zero all-water-bounded.**

| tiles | receiving biome |
|---:|---|
| 352 | `AB_MycoticJungle` — the Rot |
| 53 | `Desert` |
| 8 | `BiomeGRimond` — the Blue Desert |
| 8 | `AB_RockyCrags` — the Forsaken Crags |
| 4 | `RUT_NightsideIce` |

## owed alongside the paint

- **[R30]** `the_rot.md`'s arc range is amended from 89–130 to the measured
  **75.3–132.9**, and its temperature line checked against the warmer dayward
  edge it now reaches.
- ⚠️ The 53 tiles going to `Desert` land on top of the already-open
  `WORLDMAP_DESERT_BAND_REPAIR_1` climate-outlier defect. **Repair before
  painting, or the outliers grow.**

---

## FOUNDRY, offline half, 2026-09-09 — the raid ingested; the merge was ALREADY painted

**🔴 Finding, second-look-verified:** this item's own note ("needs offline") and the
briefing that spawned this pass both assumed the 425-tile repaint was still gated on
an owner render review. It is not — `git log -- world/ASHKARR_WORLDMAP_tiles.csv` shows
`9897eb63 Worldmap: FungalForest merged into 5 neighbours (425 tiles)...` already
landed, and `world/ASHKARR_WORLDMAP_tiles.csv` today measures **0 `BMT_FungalForest`
tiles** (MEASURED, `csv.DictReader`, not grepped) — confirmed independently of this
session. Cross-checking the live biome at each of the 2026-09-07 plan's 425 tile IDs
against the current CSV: **366/425 (86%) match that plan's per-tile call exactly**;
the other 59 diverge because at least three later worldmap sittings (the Rot's
cold-tail repaint to `RUT_NightsideIce`, a `PoisonForest` expansion, and the Blue
Desert/`WORLDMAP_DESERT_BAND_REPAIR_1` passes — see the commit log above) touched the
same tiles again afterward. That's expected drift from later, independently-ruled
work, not a defect in either pass. Full reconciliation:
`Transient/fungalforest_render/verify_summary.json`.

**So the render below is retrospective verification, not a pre-paint gate** — built
from a reconstructed "before" (the current CSV with those exact 425 tiles set back to
`BMT_FungalForest`) against the real, live "after":
- `Transient/fungalforest_render/FUNGALFOREST_RAID_MERGE_1_before_after.png` — side-by-side composite, both panels labeled.
- `Transient/fungalforest_render/FUNGALFOREST_BEFORE.biome.equirect.png` — full-res reconstructed before.
- `Transient/fungalforest_render/ASHKARR_WORLDMAP.biome.equirect.png` — full-res live after (same render the rest of the world already uses).
- `Transient/fungalforest_render/verify_summary.json` — the tile-count reconciliation above, machine-readable.
- Regenerate via `python3 src/RimMandrake/Utils/worldview.py <bundle-or-.rws> --layer biome --out <dir> --png`.

**Done this pass — the raid (offline half), `src/RimUtinni/RotSporeKit/`:** ~70 new
`RUT_`-prefixed defs across 16 files, ported field-for-field from
`vendor/mod_sources/BiomesCaverns_src` (48 ThingDefs, 7 TerrainDefs, 6 HediffDefs, 3
RecipeDefs, 2 DamageDefs, 1 StuffCategoryDef, 1 ResearchProjectDef, 1 IncidentDef, 1
GameConditionDef), plus 98 real texture files (4.4 MB) copied from the still-installed
donor's live Workshop copy (`.../workshop/content/294100/2969748433`) at matching
texPath — not generated, not left pointing at the donor's own folder.

- **Spore kit:** `RUT_ToxicSpores`/`RUT_StunningSpores` DamageDefs, `RUT_SporeCloud`
  GameConditionDef + IncidentDef, `RUT_SporesBuildup`/`RUT_SporeFlesh` hediffs,
  `RUT_ThrumbungusShroom` (thrown weapon) + projectile, `RUT_FungalMantisScythe`.
- **Materials/terrain:** `RUT_MushroomLog`, `RUT_MushroomLeather`, `RUT_MoonlessSilk`,
  `RUT_MushroomFloor`, `RUT_MushroomBridge`/`RUT_HeavyMushroomBridge`,
  `RUT_MycelialSoil`/`RUT_MycelialMatting`, `RUT_MoonlessCarpet`.
- **Buildings:** `RUT_FungiponicsBasin`, `RUT_GlowGooTorch`, `RUT_FungalGlowGooTorch`.
  `BMT_FungalPowerGenerator` — **CUT**, not ingested, per the standing ruling.
- **Research:** `RUT_AdvancedFungi` (donor's own prereq, `BMT_ResearchMushrooms`, isn't
  in the vendored source — left with no prerequisite rather than guessing one).
- **Drugs:** `RUT_AmbrosyxShroom`; `RUT_BlastpodShroom` -> `RUT_BlastSpore` -> chemfuel
  kept **WILD-ONLY** (no sowWork/sowTags at all) per the 2026-09-06 ruling.
- **Flora (19 species + Skultop):** Skulltop, dewshrooms, fruiting bodies, nuitae
  (+marsh), wrinklecap (+marsh), arpeau (+green), nogtyl (+marsh), flakespire fungus,
  pusmelon, rustpuff, sagecrust, bleeding tooth, crimson cap, grey lady, shine cap
  (+glimmerslime), brightbell, violet wimple, mortal morel (+growable, +medicine),
  "inkcap" = moonless stripes (+leather), dulcis (+raw item, fungiponics' default
  grow target).
- **Trophies/apparel:** `RUT_CaveSpiderHead`, `RUT_Apparel_ChitinSpiderHelmet` (its
  costList substitutes a new `RUT_ChitinPlating` stuff resource for the donor's
  Royal-Rhino-Beetle byproducts, out of scope here).
- **Resolved-vs-cut calls made this pass:**
  - Skultop's real defName is `BMT_Skulltop` (verified against
    `vendor/mod_sources/BiomesCaverns_src`, matching what `RUT_TheRot.xml` already
    cited) — the item's own "verify before citing" flag is now closed.
  - "inkcap (fiber, no light)" resolved to `BMT_MoonlessStripesPlant` — no
    `BMT_Inkcap` def exists anywhere in the donor's 1.6 source; Moonless is the
    donor's only no-light fiber plant and is the source of the moonless-carpet
    material this same sheet entry names. Flagged as a judgment call, not a guess.
  - `RUT_SporeCloud`'s `conditionClass` is left pointed at the donor's own compiled
    `BiomesCaverns.GameCondition_SporeCloud` (`MayRequire`'d) — a full C# port to our
    own assembly is still owed and only matters once BiomesCaverns actually retires.
  - Fauna (thrumbungus the creature, fungal mantis, cave spider, etc.) is **not**
    ingested here — out of scope, rides `BIOME_FAUNA_ASSIGNMENT_SITTING_1`.
    `RUT_FungalMantisScythe`'s claw ingredient still names the donor's
    `BMT_FungalMantisClaw` pending that sitting.
  - Caught and fixed in passing: `RUT_TheRot.xml`'s wildPlants list cited
    `BMT_Brightbells` (plural) — that defName never existed; the real donor defName
    is singular `BMT_Brightbell`. Now `RUT_Brightbell`.
- `RUT_TheRot.xml`'s wildPlants list now points at these new `RUT_` defs instead of
  the donor's `BMT_` ones (wildAnimals is untouched — fauna sitting's call).

**Still owed (nothing live-side was touched this pass — no bridge, no world_commit,
no deploy):**
- Deploy `src/RimUtinni/RotSporeKit/` to the live Mods folder and a cold-load/quicktest
  pass to confirm the ~70 defs resolve clean (config-error sweep, not just
  `validate_patch.py` — XML well-formedness was checked this pass, cross-reference
  resolution against a live def dump was not).
- Cherry Picker `BMT_FungalForest`/its raided content out of the still-installed donor
  mod if it stays installed (per the item's own instruction) — not done this pass.
- [R30] and the `the_rot.md` arc-range/temperature amendment above.
- The `WORLDMAP_DESERT_BAND_REPAIR_1` interaction — that item closed
  (`d2f0e37d`) after this merge already painted, so re-check whether the 53
  (now ~13 net, per the divergence table) ex-FungalForest Desert tiles still read as
  outliers post-repair.
- Fauna admission sitting for the mantis/thrumbungus-creature/cave-spider roster.
