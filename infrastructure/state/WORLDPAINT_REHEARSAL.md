# WORLDPAINT_REHEARSAL.md — paint the planet into a throwaway world, and LOOK at it

> 🔴 **This is NOT the one-shot run that builds the shipped world.** That is
> `infrastructure/state/WORLDGEN_RUN.md`, and two of its gates are still shut. This sheet
> exists because the owner asked, 2026-08-21, for the paint itself to be proven first:
>
> *"I would very much like to see that world painted into the game successfully. That
> would be a valuable check. So you can make that the validation: human verification."*
>
> The world generated for this run is **disposable**. Nothing outside the repo is
> precious — generate it, paint it, look at it, throw it away.

Owner: CHECK. Closes the `verify` on `ashkarr-map-quality-second-pass-8c31f7`.

---

## 1. What is being proven, and what is not

✅ **Proven by this run:** that the accepted CSV survives the trip into a running game —
21,872 tiles land on the right tile IDs, the biomes resolve, the rivers and roads attach,
the settlements place, the region labels stick, and the planet **looks like the picture
the owner accepted**.

⛔ **NOT proven, and not attempted:**

| | why |
|---|---|
| the shipped campaign world | needs a `ScenarioDef` that does not exist — §2 |
| the quest-bearing faction roster | four ratified KEEPs are zeroed in XML — §2 |
| mutators and landmarks | **the bundle has no column for either** — §4 |
| anything on a map | no map may exist during this run — §5 |

## 2. The two gates that are shut, and why neither stops this run

**a) There is no `ScenarioDef`.** Not in `src/`, not deployed, no defName authored — zero
`.rsc` files in the repo. `V1_CHAIN.md` row 12 makes it a precondition of world creation
(R-S2, reversed 2026-08-19): the engine embeds ScenParts at game creation and nothing may
edit the save afterwards. DECIDE's item
`the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07` is still `doing`, with two
ScenParts unruled.
⇒ Gates the world he **keeps**. A throwaway world needs no scenario.

**b) The faction slate zeroes four ratified KEEPs.** The deployed generated patch
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\JawaFactionSlate\Patches\OnlyOurFactions.xml`
sets both `startingCountAtWorldCreation` and `maxConfigurableAtWorldCreation` to 0 for 48
FactionDefs. Four of them are Section-4 KEEPs in the ratified
`WORLDGEN_FACTION_CHECKLIST.md`: `OuterRim_BinaryStarRaiders`, `JDSCIS_CIS_Faction`,
`OuterRim_MoistureFarmers`, and the quest-critical `guy762_KotORFaction_RogueDroids`.
🔴 `maxConfigurableAtWorldCreation 0` **deletes the row from the Configure Factions page**,
so the owner cannot put them back by hand at the screen. It must be settled in XML first.
⇒ Gates the world he **keeps**. None of the four holds a settlement in the paint bundle.

## 3. Preconditions — all four verified offline, 2026-08-21, game down

| what W9 requires | measured | verdict |
|---|---|---|
| the owner's FULL mod list, not the 13-mod minimal | live `ModsConfig.xml` activeMods = **578**, byte-identical to `ModsConfig.FULL.LATEST.xml` | ✅ no `modlist_swap --restore` needed |
| My Little Planet active | `oblitus.mylittleplanet`, index 194 of 578 | ✅ |
| subcount 7 · coverage 1 → 21,872 tiles | LocalLow preset carries `myLittlePlanetSubcount 7`, `planetCoverage 1`, `saveGenerationParameters True`; MLP's grid is 10·3ⁿ+2, n=7 → 21872 | ✅ |
| the preset survives launch | LocalLow copy 3895 B, mtime 2026-08-20 00:59, **identical to the repo copy**, and a launch happened after it (`Player.log` 2026-08-20 17:54) and left it alone. Only the workshop copy is regenerated as a 683-byte stub | ✅ the "wiped at every launch" item is closed by measurement |
| every biome defName resolves | **24 of 24** in an active mod: 5 Core · 2 Odyssey · 9 Alpha Biomes · 3 Advanced Biomes (Continued) · 3 More Vanilla Biomes · 2 Biomes! Caverns. None on Cherry Picker's 28-BiomeDef removal list | ✅ |
| the 8 Jawa factions default to ≥1 | `requiredCountAtGameStart 1` on all eight | ✅ no counter to touch |

⚠️ **Single point of failure worth naming:** `Mlie.AdvancedBiomes` alone defines
`Wasteland`, `PoisonForest` and `Volcano` — **2,348 tiles**. `Volcano` is not a vanilla
biome, despite the name.

⛔ **The save shortcut is dead.** `WORLDMAP_gen_sub7b.rws` has the right geometry, but every
save aborts on this stack — `FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()`
throws inside `ScribeLoader.FinalizeLoading` (`RT_PROBE_LOAD_ABORTS_ON_578_1`). A **freshly
generated** world never enters that path.

## 4. What the bundle actually carries

`world/ASHKARR_WORLDMAP_tiles.csv` — 21,872 rows, 14 columns:
`tile,lat,lon,arc,bearing,elev_m,temp_c,rain_mm,biome,water,river_flow,region,hilliness,swampiness`

    24 biomes          largest: AB_RockyCrags 4440, ExtremeDesert 3581, AridShrubland 2401
    1,780 water tiles  three connected seas
    254 river tiles    1,075 links: 238 river (Creek 103 · HugeRiver 113 · LargeRiver 12 · River 10)
                                    837 road  (DirtRoad 509 · StoneRoad 328)
    72 settlements     12 factions, most: Homestead Defense League 13, Deep Desert Tribes 9
    23 named regions   imported as WB_MapLabelFeature

🔴 **No mutator column. No landmark column.** `w9_run.py` runs stages 1, 2, 3, 5, 6 — there
is no stage 4. Stage 3 only *removes* the stale `Coast` the repaint stranded. So the painted
planet has no oasis landmarks and no tile mutators. Judge the picture accordingly.

## 5. The sequence

**Owner:**
1. Launch RimWorld. Full list, unchanged — nothing to swap.
2. New Colony → any scenario → **Create World**.
3. Select the **tidally locked world** preset. The preset name *is* the planet type;
   AlienWorlds force-overwrites `selectedPlanetType` to `Unknown`, so nothing else selects it.
4. On Configure Planet, read **Scale 7** and **Coverage 100%**.
   🔴 **If Scale reads 10, the preset lost its parameters — ABORT, do not generate.** The
   repair is to copy `design/Jawa/worldbuilding/TidallyLocked_Preset.xml` over the LocalLow
   path. ⚠️ `set_planet_subcount.py` writes the *workshop* path, which nothing reads.
5. Planet name arrives pre-filled `Ash'karr` — do not retype it (U+2019, not U+0027).
6. Generate. **Then stop.** Stay on the planet screen; do not pick a landing site and do not
   let a map instantiate. Say the word.

**CHECK:**
7. `python.exe src/RimMandrake/Utils/w9_run.py --dry` — every stage reports, nothing writes.
8. `python.exe src/RimMandrake/Utils/w9_run.py --apply` — about a minute.
9. The run takes the screenshot itself and names its path in the report.

**Owner:** look at it beside `world/view/ASHKARR_WORLDMAP.biome.equirect.png` and the three
ortho globes he accepted on 2026-08-20.

## 6. The decision strings — written BEFORE the run, per the load-round skill §2

A prediction invented after reading the log is a story that fits.

| # | what settles it | expected |
|---|---|---|
| 1 | bridge token in `Player.log` | present — else the game is not up |
| 2 | `jawa/world_info_get` → `tilesCount` | **21872**. Anything else and the script stops at stage 0 — a tile ID means a different PLACE on a different subdivision |
| 3 | canary: `ErrorWhileLoadingGame` in `Player.log`, read **20 s after** `game_loaded` | **absent.** A fresh world never Scribe-loads, so this must not fire. If it does, something other than the save is wrong |
| 4 | stage 1 `applied` / `unknownBiomes` | **21872** / **0** |
| 5 | stage 2 `rivers` / `roads` / `unknownDefs` | **238** / **837** / **0** |
| 6 | stage 3 offenders after | **0** |
| 7 | stage 5 settlements, `refused` | **72**, refused **0** |
| 8 | stage 6 regions | **23** `WB_MapLabelFeature` labels |
| 9 | `jawa/world_commit` | `success: true` — ⚠️ without it no edit is visible |
| 10 | `jawa/world_lint` verdict | clean |
| 11 | the screenshot | exists, and the owner names no defect |

⚠️ **Absence of an error is necessary, not sufficient.** Stages 4, 5, 7 and 8 are the
expected-**present** numbers; a run that logs nothing and applies nothing also logs no error.

## 7. What must not happen

- ⛔ **No map may be instantiated.** Repainting a planet underneath a live map killed two
  saves and about two cold loads on 2026-08-18. `Find.CurrentMap == null` throughout.
- ⛔ **Do not treat this world as the campaign start.** It has no scenario embedded and its
  faction roster is the slate's 13, not the checklist's. Saving it and keeping it would
  quietly become the shipped world with two gates skipped.
- ⛔ **Do not restart the game if the bridge stops answering.** It gets stuck, not broken,
  and recovers when the other caller finishes. A restart costs 25 minutes and fixes nothing.
- ⚠️ **Delete the throwaway saves while the game is still RUNNING.** With the game down,
  Steam Cloud restores them at the next launch, original mtimes and all.
