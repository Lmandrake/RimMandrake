# BLUEDESERT_FLORA_EXPANSION_BUILD_1 — Build 4 admitted Blue Desert flora

From `BEDAZZLE_FLORA_EXPANSION_1`. Admitted by question card 2026-10-02 (decision taken by
question card). Source of truth for look/behaviour:
`design/Jawa/worldbuilding/biomes/bluedesert_flora_expansion_pitch_2026-10-02.md` §1, §3, §4, §6.
Not admitted: Uzhmek, Oskelloth (no work owed).

## spec

Mod: `src/RimMandrake/BlueDesert/` (packageId `mandrake.rm.bluedesert`; ships composed in
`mandrake.rm.biomes`). ALL defNames use **`RM_`** (the tier of this mod's four built plants
`RM_Palefloss/Glassfern/Chimeglobe/Virr`). Defs go in
`Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml`; new items in `Defs/ThingDefs_Items/`.

Common recipe — copy `RM_Palefloss` exactly: `ParentName="PlantBase"`, no `sowTags` (never sowable),
`completelyIgnoreFertility`, −90…−1 °C band, `growMinGlow 0`, `dieIfNoSunlight false`,
`Flammability 0.05`, `MaxHitPoints` ≤ 40, `CompProperties_PlantCharge`
(`RimMandrake.BlueDesert`; radius/damage/fireChance per plant). No blue anywhere up close, glassy
translucent bodies, hydrocarbon only. Any NEW yield item carries `RM_ColdWax`'s comp stack
(`CompTemperatureRuinable` + `RM_CompRuinedDetonator` + `CompExplosive`) — except char-lace.

1. **`RM_Qeshra`** — FOOD (animal feed). Knee-low cushion of scarlet-to-tangerine glassy beads. Slow,
   dense `Nutrition`; sparse clumps in drift lees. Harvest -> new item **`RM_QeshraRoe`** (copy
   `RM_ColdWax` comps; `ingestible` animal-feed only, preferability `RawBad`, foodType matched to
   utikka/ossivel/dorrak; stored on the cold-sink rack). Add `RM_Qeshra` 0.15 to `<wildPlants>`.
2. **`RM_Kethevar`** — MATERIAL (char-lace). Chartreuse-gold pleated coil. Harvest/cut ->
   `RM_ColdWax` x1. Killed by fire/blast -> new **`RM_CharLace`** (pure carbon, warm-safe stuffable
   material, NO cold-wax comps) via `killedLeavings`. ⚠️ UNMEASURED: whether `killedLeavings` also
   fires on `KillFinalizeLeavingsOnly` (harvest/cut). Check decompiled `Thing.Destroy`/`GenLeaving`
   (RimSage) first; if it fires on cut, gate it inside `CompPlantCharge`'s KillFinalize branch (~10 lines
   C#). `<wildPlants>` `RM_Kethevar` 0.05 (rare singles).
3. **`RM_Lisqueth`** — BEAUTY. Flat smoky-violet rosette, rib edges fluoresce magenta-pink. Vanilla
   `CompGlower` (static cool-pink, glowstool precedent, NO pulse), high plant `Beauty`. Cut ->
   `RM_ColdWax` x1. `<wildPlants>` `RM_Lisqueth` 0.1 (hollows).
4. **`RM_Vashpuk`** — MATERIAL (fuel well). Squat honey-amber bladder. `harvestAfterGrowth` regrow
   idiom (berry-bush style): tap -> `RM_ColdWax` x6, plant survives, refills ~10 days. Large
   `PlantCharge` radius (second only to Chimeglobe). `<wildPlants>` `RM_Vashpuk` 0.05 (solitary).

Roster: edit `Defs/BiomeDefs/RM_BlueDesert.xml` `<wildPlants>` (shorthand
`<DefName>commonality</DefName>`, currently 4 rows) — add the four rows above. Commonalities are
proposals; calibrate to Palefloss 1.0 / Glassfern 0.5.

Engine notes: any plant comp that ticks overrides **`CompTickLong`, never `CompTick`** (Plant has no
Tick). Reuse existing `PlantCharge`, add no new ticker. Collision-swept names (0 hits); sweep game
`Data/`, local `Mods/` and workshop before shipping.

Mod Settings: one toggle in `RM_BlueDesertMod.cs` settings, `floraExpansionEnabled` (default true) gating
the four wildPlants rows (via the same mechanism the mod already uses for feature gating) and
Kethevar's char-lace drop; all-off degrades to the four original plants.

Art: queued by `infrastructure/artpipe/art_lists/bluedesert_flora_expansion_2026-10-02.csv`
(plant sprites; item icons for QeshraRoe/CharLace owed after the defs exist). Wire `texPath`s
`Things/Plant/RM_<Name>/RM_<Name>` when art lands; ship with a placeholder until then.

## criteria

Every criterion is a state read in `src/RimMandrake/BlueDesert/validation.py` (append to its
def-resolution list, which parses the mod's own Defs/ at import):
- All 4 `RM_` plant defs + `RM_QeshraRoe` + `RM_CharLace` resolve live via `get_defs` (read
  `success`/`foundCount`/`notFound`, never substring).
- `RM_BlueDesert` `<wildPlants>` contains all four new rows (parse as XML element, not `<li>`).
- No new plant has `sowTags`; each carries `CompProperties_PlantCharge` and `MaxHitPoints <= 40`.
- Qeshra harvest yields `RM_QeshraRoe`; roe has the three cold-wax comps. Vashpuk harvest yields 6
  `RM_ColdWax` and the plant is still alive afterwards (control: Palefloss cut is destroyed).
- Kethevar: cut -> `RM_ColdWax` and NO `RM_CharLace`; killed by fire/blast -> `RM_CharLace`
  (both arms in one chain). `RM_CharLace` has no `CompExplosive`.
- Lisqueth has `CompGlower` with fixed colour; no pulse comp.
- Toggle off -> the four rows absent from the live roster.
- Visual look is NOT judged by the script (owner reviews art sheet).
