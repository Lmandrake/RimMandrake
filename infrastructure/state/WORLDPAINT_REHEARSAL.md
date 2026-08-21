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
| anything on a map | no map may exist during this run — §5 |

✅ **Mutators and landmarks were added to the paint on 2026-08-21**, on the owner's order,
and they ride this run. This sheet said the opposite when it was written a few hours
earlier; see §4.

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
| **every other defName the run writes** | 6 link defs (`Creek` `River` `LargeRiver` `HugeRiver` `DirtRoad` `StoneRoad`) all in Core · `WB_MapLabelFeature` is a real `FeatureDef` in `ferny.worldbuilder`, which is active · all 9 landmark and all 11 mutator defNames are on the live census roster | ✅ **the whole silent-failure class is closed offline** |

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

### ✅ The mutator and landmark layer — added 2026-08-21, on the owner's order

`src/RimMandrake/Utils/ashkarr_populate.py` authors two more files, and `w9_run.py` gained
three stages to place them. ⛔ It is not a generator: no seed, no knobs, no way to roll a
second planet — the rules are hand-authored decisions about Ash'karr, written as code so
they are reproducible instead of re-typed.

    world/ASHKARR_WORLDMAP_mutators.csv    8,569 tiles, 9,227 placements, 11 rules
    world/ASHKARR_WORLDMAP_landmarks.csv      16 tiles   the cap from the census

**Mutators are DERIVED** — each rule restates a column the map already carries, so a mutator
is never an opinion:

| rule | from | n |
|---|---|---|
| `Sandy` | `Desert`/`AridShrubland` at hilliness ≤2 — the arid belt | 3,663 |
| `Caves` | `AB_RockyCrags` at hilliness ≥3 — the nightside floor, where rock has relief | 1,540 |
| `Dunes` | `ExtremeDesert`, flat, rain <60 mm — the rainless heart of the dayside | 1,535 |
| `Mountain` | hilliness at the top two ordinals (4, 5) | 1,459 |
| `Coast` | a land tile with ≥1 water neighbour, over the real adjacency graph | 369 |
| `River` | `river_flow` >0 — what puts the river on the LOCAL map, not just the globe | 254 |
| `Oasis` | `ZBiome_DesertOasis` inside the def's own 20–60 °C gate (39 of 227 fall outside) | 188 |
| `Cliffs` | a neighbour more than 700 m above or below | 121 |
| `HotSprings` | land bordering the volcanic province | 65 |
| `LavaFlow` | `AB_PyroclasticConflagration` | 31 |
| `RiverDelta` | a river tile touching the sea — there are exactly two mouths | 2 |

⛔ **`Marshy`, `Wetland` and `WetClimate` are deliberately absent** even though the
swampiness column would support a derivation. The census ruled them out for a planet with
no seasons and no rain, and the inventory beats a clever rule.

⭐ **This is the fix for the defect the owner named on 2026-08-17.** The world carried 5,233
`Coast`, of which 4,831 were on non-water tiles and 2,116 were deep inland — placed for the
*original* sea layout, then stranded when the repaint moved the water. Stage 3 clears them
and stage 4b recomputes them from where the water actually is.

**Landmarks are HAND-PLACED**, all 16 out of the census §7 table — `AbandonedColonyOutlander`
at The Setdown (tile 2476), `AncientQuarry` at The Ore Moot, `Valley` at The Scald Gate,
`sw_Sarlacc` at Sarlacc Ground, `AncientLaunchSite` at the Rust Cathedral, `LavaCrater` +
`LavaLake` on the Scald rim, `AncientHeatVent` ×3 on the hottest ground, `Oasis` ×6 spread
across the wells. A named place stops being a place when there are 227.

⚠️ **The salt pans are deliberately empty.** `DryLake` / `VEE_SaltPlains` may not be legal on
`Wasteland`, and a landmark that cannot fire **logs nothing** — so nothing is placed on an
unverified legality.

🔴 **Two engine facts this rests on, and the run re-proves both rather than assuming them:**

1. `AddLandmark` **ignores** `IsValidTile`. Measured 2026-08-19: on a settlement tile the
   verdict was False and it added the landmark anyway. `ashkarr_populate.py` therefore
   refuses settlement tiles *and their neighbours* itself — the first legal ring is two out,
   not the "one tile adjacent" the census assumed — and stage 4 passes `checkValid: true` so
   the engine's own verdict is recorded beside ours.
2. `AddMutator` is **expected** to ignore `biomeWhitelist` the same way. That matters because
   the shipped `Oasis` mutator whitelists `Desert`/`ExtremeDesert` only and our oasis tiles
   are `ZBiome_DesertOasis`. **Expected, not proven** — stage 4b reads the count back and §6
   carries it as decision string 8. If it reads 0, the whitelist *is* enforced and the census's
   one-line `PatchOperationAdd` is needed after all.

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
7. `python3 src/RimMandrake/Utils/ashkarr_populate.py` if either CSV is stale, then
   `python3 src/RimMandrake/Utils/ashkarr_populate.py` — only if either CSV is stale;
   it needs no game. Then
   `python.exe src/RimMandrake/Utils/w9_run.py --dry` — every stage reports, nothing writes.
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
| 6b | stage 3b leftover landmarks removed | **49** — the census counted exactly 49 in each of two savegames. A different number means this world generated differently and the figure is worth keeping |
| 7 | stage 4 landmarks `added` | **16 of 16**, across 8 defs. `validity[]` may report tiles the engine calls invalid — record them; it places them anyway |
| 7b | stage 4b mutators | **9,227 placements over 8,569 tiles**, 11 rules: Sandy 3663 · Caves 1540 · Dunes 1535 · Mountain 1459 · Coast 369 · River 254 · Oasis 188 · Cliffs 121 · HotSprings 65 · LavaFlow 31 · RiverDelta 2 |
| 8 | ⭐ Oasis read-back | **188 of 188** sampled carry it. **0 means `AddMutator` honours `biomeWhitelist`** and the one-line patch is needed — that is a finding, not a failure |
| 9 | stage 5 settlements, `refused` | **72**, refused **0** |
| 10 | stage 6 regions | **23** `WB_MapLabelFeature` labels |
| 11 | `jawa/world_commit` | `success: true` — ⚠️ without it no edit is visible |
| 12 | `jawa/world_lint` verdict | clean |
| 13 | the screenshot | exists, and the owner names no defect |

⚠️ **Absence of an error is necessary, not sufficient.** Stages 4, 5, 7 and 8 are the
expected-**present** numbers; a run that logs nothing and applies nothing also logs no error.

## 6b. 🔴 THE RIDE-ALONGS — 25 of CHECK's 37 items settle on this one load

A load is never spent on one question. Every item below has criteria that a **world screen
with no map** satisfies, so they cost nothing extra. ⚠️ Read this **before** launching, not
after: several are log strings that exist only in the log this load writes, and the previous
`Player.log` is overwritten at launch.

**Tier 1 — one grep of the log the load writes anyway. No bridge calls.**

| item | the string |
|---|---|
| `PRELOAD_PREDICTIONS_578_1` | all seven at once: 112 `jawa/` tools · `Adding mandrake.inhabited` · `DEAD MODS` both 0 · `cross-reference (def loader)` 25 · dump says 578 · `patch operations failed` 6 · `texture path failures` 2 |
| `btd-jawa-has-no-merge-to-wait-for-8c40b2` | `harvest_log.py --show scribe` — no `Could not load reference to Verse.XenotypeDef` naming a Jawa xenotype |
| `B59` (the MegafaunaYield fix) | `patch operations failed` back at baseline **5**, no `[Jawa Doctrine Patches]` among them |
| `B58` (the Jawa_Patches half) | `Jawa_Patches ops` at baseline **0**, no `Failed to find a node` naming `OuterRim_Jawa` |
| `d-chk2-magenta-heads-…-7b3e01` | `grep -c "Failed to find any textures at"` returns **0**, was 3 |
| `GRIMTERRA_JUVENILES_RENDER_1` | **0** lines for `Things/Pawn/Animal/TortoiseGRim` or `…/GRimPinkBird`; baseline 2 |
| `cherrypick-settings-actually-load-3b71ae` | no `mod settings data for 3521312241` exception |
| `INHABITED_DLL_FIX_AT_SHUTDOWN_1` | `[Inhabited] ready:` with **269** characters, and **115** `jawa/` tools |

**Tier 2 — read the def dump this load regenerates** (arm `dump_request.txt` first):
`ASH_STORM_OVER_PYRELANDS_1` (`AB_VolcanicAsh.label` = `ash storm`) · `IKEE_READS_AS_OURS_1`
(`AA_Eyeling` labelled `ikee`, in exactly 3 biomes' `wildAnimals`) · `RAKATA_SLEEPERS_LOOK_RIGHT_1`
(`AncientSoldier`/`_Leader` → `RimMandrakeRakata: 1.0`, `useFactionXenotypes: false`) ·
`B63` live half (0 `biomeConfigs` `<li>` errors, then 27 biomeConfigs / 29 biomeBlacklist, and
the world names itself `Ash'karr` with byte U+0027).

**Tier 3 — one bridge call at the world screen:**
`RT_PROBE_LOAD_ABORTS_ON_578_1` (canary only — a fresh generate does not exercise the
save-restore half) · **`B54`** 🔴 (`jawa/ideo_of` reads eleven faiths — *irreversible after the
click*) · `B40` `B41` `B42` `B43` `B52` (each faction's name and `leaderTitle`) ·
`seven-authored-factions-…-5b90c7` · `FACTION_RELATION_MATRIX_1` · `FACTION_NAMES_ARE_GENERATED_1`
(⚠️ its edit dies unless the world is saved).

✅ **`FACTION_RELATION_MATRIX_1` DOES ride.** A sweep reported its DLL as never deployed; the
deployed binary's own strings carry `jawa/faction_relations_get` and `_set`. Read the bytes.

**Tier 4 — the paint itself**, which this session performs anyway: `W9` ·
`ashkarr-map-quality-second-pass-8c31f7` · `seaice-…-2b71fd`.

⛔ **Cannot ride — they need a map or a colony**, and no map will exist:
`sixteen-authored-role-kinds-spawn-bare-handed-…` · `ROLE_KINDS_ARMED_5_OF_5_1` · `C40` ·
`CAST_ROSTER_269_LOAD_1` · `INHABITED_ROUTE_ONE_DAY_1` · `ROSTER_SOAK_100_DAYS_1` ·
`INHABITED_POOL_ROUND_TRIP_1`.

### Done in the shutdown window, 2026-08-21 — both assemblies are in sync

An assembly cannot be written while RimWorld holds it memory-mapped, so this was the window.
`Inhabited.dll` was 15 hours stale on disk (repo 45,568 B built 23:41 · deployed 43,008 B from
08:26); it is deployed and byte-verified, md5 `abd78bd73a86df1fa5dfa93cbdeacfe7` both sides.
`JawaBench.BridgeTools` needed nothing — it already byte-matches and its strings carry 115
`jawa/` tool names. **Nothing is waiting on a shutdown any more.**

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
