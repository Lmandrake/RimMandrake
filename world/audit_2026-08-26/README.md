# Ash'karr adversarial audit and six-pass edit — 2026-08-26, seat CHECK

Driven live through the bridge against the running game. **Nothing here is regenerable:**
`BEFORE_*` is the only copy of the planet as it stood before the edit.

## Restore

`BEFORE_mutators.json` / `BEFORE_landmarks.json` / `BEFORE_links.json` / `BEFORE_tiles.csv`
are a complete pre-edit record. `AFTER_*.csv` is the post-edit bundle in `worldview.py`
form (render it with `python3 src/RimMandrake/Utils/worldview.py world/audit_2026-08-26/AFTER`).

## What was written

`ops.json` is the exact edit list; `apply_log.txt` is what the game reported back.

| pass | what |
|---|---|
| A-solar | `VEE_MoreSolarPower` on 4,362 tiles at arc <= 55, `VEE_LessSolarPower` on 3,900 at arc >= 125. The terminator belt is deliberately unmarked. |
| B-water | 22 dead channels traced downhill out of the named ranges: `VEE_DryRiver` -> `VEE_SaltPlains`, plus relict deltas on the Grey Sea shore and alluvial fans on the Twilight Sea. |
| C-roads | 147 dead-straight road segments re-routed A-t-B -> A-x-y-B. `AncientAsphaltHighway` untouched on purpose. |
| D-cluster | 18 landmark families grown around anchors instead of lone pins. |
| E-regions | Sinkground, Fanground, Salt Gate, Lantern Deeps, Sporefields filled. Lantern Deeps' 7 core tiles raised to Mountainous so a `Cavern` can legally exist there. |
| F-tatooine | `WildTattooinePlants` on 1,400 dayside tiles; 5 sarlacc pits and 3 dead ones, all off-road. |

## Three things measured here that the docs did not say

1. **`world_landmarks_set`'s `isValidTile` is evaluated AFTER the add**, so it reports the
   landmark it just placed. It is not a gate and not a usable pre-check — `added >= 1` plus
   a read-back showing the def is the only honest success signal.
2. **The landmark is `Ruins`; the mutator is `AncientRuins`.** Nine placements failed on the
   assumption that one name served both.
3. **Landmark `mutatorChances` rolls bypass any category guard you apply to your own writes.**
   Seven same-category mutators were displaced this way; six were correct specialisations
   (`Cavern`/`SerpentineCanyons`/`Cenotes` replacing a generic `Mountain`), one was a real
   defect — a `VEE_DryRiver` landmark landed on a live river tile (863) and displaced `River`.
   Repaired. Diff whole-planet LOSSES after any landmark pass, not just your intended gains.

## Second pass, same day — the nine empty regions, the vegetation liars, the stacked landmarks

`ops2.json` + `apply2.py`. Every one of the 72 named regions now carries at least one
landmark (was 15 with none this morning, 9 after the six passes). Thornbelt and Sunward
Scrub got cacti and succulents; Thornend got `VEE_PoisonousFlora`, because its HorrorWastes
biome is not in the cactus whitelist and the obvious fix was illegal there. The three
landmarks sitting on settlement tiles were RELOCATED, not deleted — the gravel beach at
Seabarter needed a ring-3 search to find a coastal tile.

Live world saved as `ASHKARR_ALLPASSES_2026-08-26`.

## 🔴 The 45 GL_* landforms CANNOT be placed. Measured, not assumed.

`gltest2.py` is the control. On one tile that already held mutators:

```
before: ['Cliffs', 'VEE_MoreSolarPower']
add GL_Caldera    success=True added=1  -> present after: False
add GL_Canyon     success=True added=1  -> present after: False
add GL_Sinkhole   success=True added=1  -> present after: False
add VEE_JaggedRocks success=True added=1 -> present after: True
```

All 45 resolve live (`get_defs` foundCount 45/45) and all carry a real worker
(`GeologicalLandforms.TileMutatorWorker_Landform`), no biome/hilliness/coast gates at all,
and `chanceOnNonLandmarkTile: 0` — so worldgen never rolls them either. Geological
Landforms evidently rejects the write itself; `world_mutators_set` reports `added: 1`
regardless. **This is a new entry in the silent-failure catalogue.**

⚠️ **A remove does NOT restore what an add displaced.** The probe's `VEE_JaggedRocks`
(category Mountain) displaced `Cliffs`; removing VEE_JaggedRocks left the tile with
neither. Repaired by hand. Any add/remove probe on a categorised mutator is destructive —
read the tile first and put back what you displaced.

## Correction: the GL_* landforms are map-gen content, and they are NOT unused

The blank-tile control (`blank_test.py`, `blank.json`) settles the write question. Six tiles
that were genuinely empty — no mutator, landmark, settlement, road or river — across six
biome/hilliness combinations, each given a fitting `GL_*` def AND a fitting normal control:

```
tile   biome            hilliness    def                 added  LANDED
10140  ExtremeDesert    Flat         GL_DesertPlateau      1     NO
10140  ExtremeDesert    Flat         VEE_PebbleDunes       1     YES
47     Desert           Flat         GL_DryLake            1     NO
47     Desert           Flat         DryLake               1     YES
2      Desert           SmallHills   GL_Sinkhole           1     NO
2      Desert           SmallHills   VEE_Sinkholes         1     YES
77     ZBiome_Badlands  LargeHills   GL_Canyon             1     NO
77     ZBiome_Badlands  LargeHills   Chasm                 1     YES
297    AB_RockyCrags    Mountainous  GL_Caldera            1     NO
297    AB_RockyCrags    Mountainous  Cavern                1     YES
9      Wasteland        Flat         GL_Crater             1     NO
9      Wasteland        Flat         VEE_DustBowl          1     YES
```

No category conflict was possible and nothing was logged. `Tile.AddMutator` has no early
return, so the base game cannot be refusing it — `mutator.Worker?.OnAddedToTile` is the only
remaining path, and every GL_* shares `GeologicalLandforms.TileMutatorWorker_Landform`.

🔑 **And that is correct behaviour, not a bug.** Geological Landforms does not store
landforms on the world tile at all. Its 44 landforms are NodeCanvas graphs in
`<workshop>/2773943594/1.6/Landforms-v1/*.xml`, each carrying a `World Tile Requirements`
node — Topology, Commonness, and ranges for hilliness / rainfall / temperature / elevation.
GL evaluates those **when a map generates**, from the tile properties we author. The
`GL_*` TileMutatorDefs are display shims GL owns; writing one is meaningless.

⇒ **They are not "barely used". They are invisible on the world map and fire in play.**
`landforms.txt` scores all 44 against Ash'karr's real tile distribution. The lever that
changes which landforms occur is **hilliness, elevation and topology — not mutators.**
Ash'karr is flat (8,394 Flat / 1,510 Mountainous / 56 Impassable), so the dramatic
top-of-scale landforms are the rare ones: Valley needs 3.7-4.8 (277 tiles), Crater 3.4-5.0
and Rift 3.5-5.0 (1,540 each). Caldera needs only 1.0-2.2 and Inland — 14,824 eligible
tiles, commonness 0.0168.

⚠️ The eligibility counts model Inland/Coast topology, hilliness, temperature and elevation.
They do NOT model GL's computed cliff/cave topologies (CliffValley, CliffOneSide,
CaveTunnel), so those rows are UPPER BOUNDS. The five scoring 0 require the very top of
GL's hilliness scale (5.4-6.0) and two of them are cave topologies that are not surface
tiles at all.

## The hilliness pass — making the named ranges actually mountainous

`hills.py` (derive + preview), `hills_apply.py` (write), `hills_verify.py` (prove).
`BEFORE_HILLS_tiles.csv` is the tile table immediately before it; `hills_plan.json` is the
exact per-tile plan. Live world saved as `ASHKARR_MOUNTAINS_2026-08-26`.

**The defect.** Hilliness was barely tied to the terrain under it — `corr 0.445` with
elevation, `0.555` with local relief — and the classes did not separate: Mountainous
averaged 779 m against SmallHills' 544 m, while some *Flat* tiles sat at 1,690 m. A named
range read as mountainous on only a third to a half of its tiles.

**The rule.** Hilliness is derived from `0.50 x local relief + 0.30 x neighbourhood
roughness + 0.20 x absolute elevation`, ranked planet-wide and cut at target shares, plus an
explicit authored bonus for the eleven regions NAMED for mountains — because a pure
relief rule *demoted* Fall Line and Ashfall Range and left Rimewall and Frostcaps with no
mountain at all. Intent beats noise; that trade costs some correlation (0.775 -> 0.657) and
is deliberate.

```
              before   after            named range      Mtn      Impassable
Flat            8394    9304            Ashfall Range  177->225     0->75
SmallHills      8097    6037            Scald Spine     96-> 98    39->62
LargeHills      3808    3785            Dew Horn       256->334     0->120
Mountainous     1517    2391            Gray Crags     171->380     0->65
Impassable        56     355            South Crags     38->341     0->8
                                        Twilight Crags 104->299     0->25
7,315 tiles changed                     Rimewall         0-> 28     0->0
                                        Frostcaps        0-> 29     0->0
```

**Guards that were enforced, not assumed.** 1,973 tiles are capped at Flat by their own
content (1,536 of them `Dunes`, which protects the Dune Sea for free); settlement and road
tiles are capped at Mountainous so nothing becomes Impassable under a caravan route. All
355 Impassable tiles landed inside named ranges.

**Verification.** Full re-export: live distribution matches the plan exactly, 0 tiles missed,
0 unplanned changes; 40 sampled tiles read back RAW (never `HillinessLabel`, which is
privately cached and would have confirmed writes that never landed). Passable-land
connectivity checked before and after — `NEWLY cut off by this pass: none`; the two
settlements off the main landmass (Deepwater Hold, Bitterleaf) were already so.
`tile_settleable` refuses all 96 settlement tiles only with "already have a base there",
never for terrain. `world_lint` unchanged at 22 findings.

**What it unlocks.** Geological Landforms gates its dramatic landforms on hilliness:
Crater and Rift need 3.4-5.0, Valley needs 3.7-4.8. Eligible tiles go 1,573 -> 2,746 and
1,517 -> 2,391. Caldera (1.0-2.2, Inland) was always available on ~14,800 tiles.

## Sharpened 2026-08-26, later: the GL_* defs are COMPUTED, not stored — and they ARE live

The earlier section is right that the write is refused. It was incomplete about why, and it
implied the landforms were dormant. They are not.

**The evidence.** The in-game world-tile pane for tile 18404 lists eight features:
insect megahive, bumbledrone nests, rotstink geysers, increased fish, flood plains,
increased solar exposure, **biome transitions**, marshy. `jawa/world_mutators_get` on the
same tile returns exactly seven — every one of those **except** `biome transitions`.

Tile 18404 borders two different biomes (`BiomeCypreJungle` x2,
`COMIGO_GreaterSwamp_Tropical` x2), and `GL_BiomeTransitions` — from the separate
**Biome Transitions** mod (`m00nl1ght.geologicallandforms.biometransitions`), same author,
same `GL_` prefix, which is what made it look like one family — shares
`GeologicalLandforms.TileMutatorWorker_Landform` with all 45 landform defs.

🔑 **So a `GL_*` feature is derived from the tile's real geometry at display time and never
enters `Tile.mutatorsNullable`.** That explains all three observations at once:

* `world_mutators_get` never lists them — it reads the stored list, and they are not in it.
* a write reports `added: 1` and vanishes — `AddMutator` appends, then the worker's
  `OnAddedToTile` takes it back out, because the list is not where they live.
* the histogram scored all 45 as "never used" — **that number was measuring the wrong thing.**
  ⛔ Do not quote "45 landforms unused" from the earlier section; it is an artefact of a
  read that cannot see them.

⇒ The landform system is ACTIVE on Ash'karr and driven by exactly the tile properties we
author. The hilliness pass is therefore the correct lever, and its effect is real.

⚠️ **Still unproven, and honestly so:** I have seen a `GL_*` feature appear in-game on a
real tile, which proves the mechanism. I have NOT seen the word "caldera" or "canyon" in a
mountain tile's pane, because no bridge tool selects an arbitrary world tile — `world_view`
centres the globe without selecting, and the pane keeps whatever was last clicked. Clicking
one Gray Crags tile in game would close it in two seconds.

## Closed: the landform system IS loaded; it just never shows on the world map

Player.log, after a save/load of the edited world:

```
Geological Landforms loaded. Will load compatibility patches.
[Geological Landforms v1.7.13.1] Found landform data in the following mods:
                                 Geological Landforms, Biome Transitions
[Geological Landforms v1.7.13.1] Loaded 49 landforms of which 0 are edited and 0 are custom.
```

⇒ 49 landforms registered and operational. The remaining question was only whether they
surface on the globe. **They do not.** Two different Mountainous Gray Crags tiles — one
before the owner's save/load, one after — both report `Features: Mountain` and nothing
else, with a single icon in the "Features in this tile" panel. `Valley` has
`Commonness 1.0` for hilliness 3.7-4.8 Inland and both tiles qualify, so if landforms
displayed on the world tile at least one would have named it.

🔑 **Landform assignment happens at MAP generation.** The world pane cannot prove or
disprove it, a reload does not change that, and no amount of clicking will.

⚙️ The sighting closes for free the next time anyone lands on a Crags or Ashfall Range
tile — that map IS the test. Do not build a special harness for it.

⚠️ Also confirmed here: a save/load does NOT lose the edits. Tiles 0-2999 came back with
Impassable 46 / Mountainous 310, and tile 18404 still carried `VEE_MoreSolarPower`.

## 🔴 F4 IS CLOSED BY OWNER RULING — the Scald area is not to be touched

Owner, 2026-08-26: *"Leave the scald area alone"*.

⛔ **F4 (the Scald's ten-biome collar) is not a defect to fix. Do not repaint the Scald,
its rings, the Scald Spine or Hollow Verge, and do not re-file it.** The audit's reasoning
stands as written — a one-tile rainbow collar is what it is — but the decision is made and
it is not a technical question. If a future sweep flags the Scald's biome mix, this line is
the answer.

✅ Still open and NOT covered by this ruling: F6 (the Rust Cathedral lozenge and the 42
single-tile AridShrubland islands) and the orphan trunk river.

## Terraforming scar placed at 8.02N 124.34E, and the census behind "what else can we do"

Owner asked for a second `TerraformingScar` beside the one at 6.73N 123.91E (tile 1641,
"Icylion Scar"). Placed on **tile 17126** as the LANDMARK form, matching the reference
exactly: read-back `landmark=TerraformingScar name='Witen Scar' mutators=['TerraformingScar']`,
confirmed again after `world_commit`. The target was completely empty beforehand — no
landmark, no mutators, no world objects — so nothing was displaced.

🔑 **Why that one reshapes the ground: it has a dedicated worker class**,
`RimWorld.TileMutatorWorker_TerraformingScar`. It has NO `extraGenSteps` and no
`terrainPatchMakers`, so a data-field ranking scores it zero — the shaping is in code.
`workers.txt` is the corrected census: **144 distinct worker classes** across the placeable
mutators. 65 defs have no worker at all and only change stats or the tile's label;
everything else does real work at map generation.

⇒ **The right question is not "is it unused", it is "does it have a worker".** `genpower.txt`
(the data-field ranking) is kept only as the wrong lens that made this visible.

## Five creative passes — scars, cenote relocation, Wither canyons, the Cathedral interior

`plan3.py` / `apply3.py` / `verify3.py`, `ops3.json`, and `wheretolook.txt` (coordinates).
Live world saved as `ASHKARR_SCARRED_2026-08-26`. 386 mutator writes, 39 new landmarks,
**0 failures**.

| pass | what |
|---|---|
| P1 cenotes | 12 removed from bare crags, tar pits and arid ground — 4 of those were on `AridShrubland`, which the def's own BLACKLIST forbids, so they were illegal placements. 64 added as karst chains in nine wet, dark, under-used regions. |
| P2 nightscars | 180 `TerraformingScar` laid as wandering CHAINS of adjacent tiles across Umbra, Ammonia Flats, Deadstone, Cinderdark, Ashen Wastes, Scour, Sunreach, Nightspill. |
| P3 wither | A torn line through Wither, The Verge, South Crags and Scour, plus real `VEE_SerpentineCanyons` and `Chasm` wherever the ground is Mountainous enough to carry them. |
| P4 cathedral | The 236-tile lozenge got an INTERIOR without repainting a single biome: an `AB_DerelictArchonexus` core, uplinks around it, component deposits and bio labs in the works ring, ship chunks trailing out, deadlife vents and contaminated reservoirs at the edge, and a scarred approach. |
| P5 buried | Kemetic temples in Dry Marches/Long Sand, giant fossils in the Dune Sea, tox and smoke vents at Scorch and Cinders, component deposits in The Abandoned Mines. |

🔑 **`TerraformingScar` is ILLEGAL on `HorrorWastes`**, which is Deadstone's core and the
whole of Thornend — the nightside chains route around it. Also illegal on the crystal
caverns, fungal forest, both ice biomes and the tropical swamp.

🔴 **Of the buried things, only BioLab / ComponentSpacer / ContaminatedReservoir /
DeadlifeVents / Uplink / ShipChunks / Archonexus are legal in the Rust Cathedral.**
KemeticTemple, GiantFossils, AncientToxVent and AncientSmokeVent are legal on **0** of its
236 tiles — `AB_MechanoidIntrusion` is not in their whitelists. They went where they fit.

**Losses, whole-planet diff:** 12 `VEE_Cenotes` (all intended removals), 3 `Mountain`, 1
`Caves` — the last four all tiles where `VEE_SerpentineCanyons` replaced a generic feature,
which is the correct specialisation.
⚠️ One of those went via **`overrideCategories`**, which the collision guard does not model
— it only checks `categories`. A guard built on `categories` alone will miss an override.

## The Wither canyon, stripped and rebuilt in canyon vocabulary

Owner, 2026-08-26, from tile 830 (60.86S 93.94E): *"adding a Terraforming Scar to a place
with Mountainous (or in this case also a Chasm) does not work very well"* — scar art
fighting chasm art on one hex. He asked for the whole canyon structure stripped and
repopulated from defs that speak to canyon or chasm.

**The structure** is the connected high-relief band inside Wither: 48 tiles
(37 LargeHills + 11 Mountainous), found as the graph component containing tile 830 plus
Wither's second high run. `wither_plan.json` holds the exact list.

🔴 **Every canyon and chasm def requires Mountainous or above, and they are ALL category
`Mountain`, so a tile can hold exactly one.** `VEE_SerpentineCanyons`, `Chasm`, `Cavern`
and `Hollow` all gate at `minHilliness: Mountainous`; `VEE_RockRidge`, `VEE_JaggedRocks`
and `VEE_StoneForest` gate the opposite way at `maxHilliness: Flat`, so they are useless
here. ⇒ To speak canyon at all the whole spine had to be raised to Mountainous. That is
also what a canyon system should be, so it was done deliberately rather than worked around.

**Done:** 4 landmarks removed, all mutators CLEARED off the 48, the 3 remaining
TerraformingScars pulled off the rest of Wither, spine raised to Mountainous, then one
canyon def per tile walked along the spine for variety — SerpentineCanyons 18, Chasm 12,
Cavern 12, Hollow 6 — plus non-conflicting texture: `VEE_Sinkholes` 16 (no category),
`MineralRich` 12 (exposed strata), `CaveLakes` 7 (kept off the Cavern tiles, which already
own the `Caves` category). 10 landmarks along it.

**Verified:** all 48 read Mountainous; **exactly one canyon def per tile, 0 exceptions**;
no TerraformingScar, Mountain, Cliffs, VEE_SaltPlains, DryGround or VEE_RotstinkVents left.
Tile 830 is now `Chasm` + `MineralRich` with nothing drawn over it.

⚠️ The landmarks' own `mutatorChances` rolled 6 `MixedBiome`, 2 `AnimalLife_Decreased`,
1 `Stockpile`, 1 `AnimalHabitat`, 1 `WildPlants` onto the spine. Unavoidable when placing a
landmark, and harmless — but it means "cleared" is only true until the landmarks go on.

⚙️ Two black hexes sit in the spine. They are present in the screenshot taken BEFORE this
rebuild, so they are not caused by it, and nothing in the tile data shows a missing texture.
Unexplained, benign, not chased.
