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
