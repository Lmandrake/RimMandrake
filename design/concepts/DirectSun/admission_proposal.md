# DirectSun: admission at intake, and a PROPOSED vision and bars for Design Version 0.1.0

Written 2026-11-27 by BENCH, item `RIMMANDRAKE_ADMIT_DIRECT_SUN_WITH_TREE_AND_MOUNTAIN_SHADE`, on the Conductor's brief.
**Everything below "What exists" is a PROPOSAL for the Designer stage and the owner.** The Designer's Lock step sets the
bars; nothing here is a lock. Design inputs (written before the pipeline; input, not settled):
`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` (the ruled model DS1-DS8),
`design/RimMandrake/tree_shade_model_2026-10-19.md` (the crown model and its adopt-or-fall-back test T1-T6),
`design/RimMandrake/sun_and_shade_modularity_2026-10-19.md` (where the code lives and ships),
`design/RimMandrake/shadecraft_lessons_design_2026-10-31.md` (shade gear learned by study). The standing rule:
`design/RimMandrake/standing_rulings.md` §Direct Sun. The binding principles: `GUIDING_PRINCIPLES.md`.

## His words

- 2026-11-27 9:25 PM PST, by card (the question "What form should the tree shade project take?"; other options were
  "Design it as its own mod (Recommended)", "Concept file only", "Adapt each biome design", "Leave it parked"):
  "I'd like it to remain as part of Direct Sun, as an addition to the obvious shade induced by hard walls. We should
  also add shadows cast by mountain-covered squares that are much larger than short walls would, so you get a feel for
  said mountain on the map depending on the sun angle. Very cool! So Tree Shade + Direct sun + mountain shade should all
  receive this design attention now to bring it to a full modern design with tests, etc."
- 2026-11-27, about 9:25 PM PST, typed before that card (OWNER note on
  `RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE`): "I think making tree shade might be a timely pre-design or
  design-adaptation project, given we worked on it and it technically touches all of our biome mods".
- 2026-11-26 9:10 PM PST (OWNER event `1795756206289623411` on `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE`): "Direct Sun is
  surprising to see, but it's an essential mod that's quite welcome to develop alongside us. It's mechanics are
  integral to the setting and many Baroque Biomes, so it's a required mod for Baroque Biomes that can also stand
  alone... or can it? I want to record in the mod that we are still evaluating whether to merge it into Baroque Biomes
  or take on the potential extra work of making it stand-alone (not yet clear)."
- The standing words of the model (full text: `design/RimMandrake/standing_rulings.md` §Direct Sun): 2026-10-19,
  "a pure function of geometry, NOT biome ... low sun is less intense AND produces longer shade, high sun produces
  only covered shade and much more intense effect"; "55 C everywhere"; "Hotter air on the thermometer"; on a day/night
  world "drop sun heat (should actually be called "direct sun")"; tree shade, 2026-10-19, "If we have an excellent tree
  shade model working, then YES direct sun works the same everywhere on the day side."

## What exists (measured 2026-11-27, this clone at 7e019a237d)

### Code

All of Direct Sun's code is in Creature Behaviors (`src/RimMandrake/CreatureBehaviors`, a member of the composed
`mandrake.rm.biomes`, namespace `RimMandrake.CreatureBehaviors`), except the shade-gear defs in Environmental Hazards
(also a member of `mandrake.rm.biomes`) and the air-heat defs and rows of three biome mods.

| Part | Files (lines) | Mod |
|---|---|---|
| Shade grid: roof shade, cast shade, exposure, crown cast, cause word, overlay data, sun path cost | `Source/RM_MapComponent_ShadeGrid.cs` (1262) | CreatureBehaviors |
| Sun arithmetic, crown footprint and drawn-shadow geometry | `Source/RM_SunHeatMath.cs` (616) | CreatureBehaviors |
| The felt-heat postfix, the extension (glare, mirage, shade-hop data only) | `Source/RM_SunHeatPatches.cs` (238), `Source/RM_SunHeatExtension.cs` (118) | CreatureBehaviors |
| Hot air as a vanilla `GameCondition_TemperatureOffset` | `Source/RM_AirHeat.cs` (179); `src/RimMandrake/_Shared/AirHeat/AirHeatSetting.cs` (29), source-linked | CreatureBehaviors; rows in TheForge, TerminalBiomes, Greentide |
| The fixed sun of the shipped world | `Source/RM_PlanetSunGeometry.cs` (124), `RM_MapComponent_PinnedSun.cs` (292), `RM_PinnedSunExtension.cs` (91), `RM_PinnedSunPatches.cs` (71) | CreatureBehaviors (reads WeatherSuite's `PlanetGeometryDef`) |
| Moving shade (creatures that cast shade) | `Source/RM_MovingShadeLayer.cs` (165), `RM_MovingShadeMath.cs` (106), `RM_Comp_ShadowCaster.cs` (36), `RM_CompProperties_ShadowCaster.cs` (52) | CreatureBehaviors |
| Shade gear (parasol, tent, shade cloth), sun-load gizmo | `Source/RM_ShadeGear.cs` (166), `RM_ShadeClothExtension.cs` (20), `RM_Gizmo_SunLoad.cs` (85) | CreatureBehaviors |
| Shade-hop, the shade patch graph, glare-blind, mirage, haze | `Source/RM_ShadeHop.cs` (622), `RM_ShadePatchGraph.cs` (457), `RM_GlareBlind.cs` (102), `RM_Mirage.cs` (385), `RM_ShadeHaze.cs` (95) | CreatureBehaviors |
| Tree crowns, overlay, ground tint, drawn crown shadow | `Source/RM_TreeCrownExtension.cs` (51), `RM_TreeCrownPatches.cs` (133), `RM_ShadeOverlay.cs` (346) | CreatureBehaviors |
| **Total, the 24 core files above** | **5812 lines** | CreatureBehaviors |
| Sky and light of the fixed sun (not felt heat): tidal sun glow, sun flare behind the planet, the world-view sun | `Source/RM_TidalSunGlowMath.cs`, `RM_TidalSunGlowPatch.cs`, `RM_SunFlareOcclusionPatch.cs`, `RM_WorldSunPatch.cs` (360 together) | CreatureBehaviors |
| Consumers, not Direct Sun: shade seeking, shade wander, shadow follower, false shade, shade stagger, shade-driven severity, sun scald | 13 files, 1241 lines | CreatureBehaviors |
| Outside consumers | SolarMirrors and Sarlacc (csproj HintPath), Watchers and the JawaBench bridge tools (reflection by full type name), saves (the map component by class name): `sun_and_shade_modularity_2026-10-19.md` §1 | several |

**Mountain shade: no design and no code.** Measured: natural rock is a caster of height 1, the same as a wall (vanilla
`Granite` carries `staticSunShadowHeight 1`, read with RimSage; `RM_MapComponent_ShadeGrid.CasterHeight` reads that field
and `fillPercent 1`). A cell under an overhead mountain roof is covered (`roofShade = 1`) but casts nothing onto open
ground. So a mountain's edge throws the lee of a short wall at every sun angle. A search of `src/`, `design/`,
`skills/` and the live items for "mountain shade" or "mountain shadow" finds only his card of 2026-11-27.

### Defs and patches

- Environmental Hazards (`src/RimMandrake/EnvironmentalHazards`): `Defs/ThingDefs_Buildings/RM_ShadeGear.xml`
  (`RM_Parasol`, `RM_ShadeTent`; `RM_SunShield` is gone, as DS4 ruled), `RM_DecoyShadeTarp.xml` (`RM_DecoyShadeTarp`),
  `Defs/ResearchProjectDefs/RM_ShadeLessons_Research.xml` (`RM_Research_Parasol`, `RM_Research_ShadeTent`,
  `RM_ShadeIdea_DewOff`, `RM_ShadeIdea_PortableShade`, `RM_ShadeIdea_DeepCloth`), `RM_DecoyShadeResearch.xml`, and the
  patch `Patches/RM_ShadeLessons_Sources.xml`.
- `src/RimMandrake/CreatureBehaviors/Patches/`: `RM_DirectSun_LegacyFields.xml` (strips the removed sun fields at load),
  `RM_DirectSun_WeatherSun.xml` (a sun factor on the vanilla overcast weathers), `RM_TreeCrowns_Giants.xml` (the six
  giants' crown factors, measured from their art).
- Air heat: `RM_ForgeAirHeat` (TheForge), `RM_ScaldAirHeat` (TerminalBiomes), `RM_GreentideAirHeat` (Greentide), each a
  `GameConditionDef` named by `RM_AirHeatExtension` on its BiomeDef. The Fever Wood's waits for its hold to lift.
- `RM_SunHeatExtension` is in 9 XML files under `src/` (glare, mirage and shade-hop data only);
  `RM_PinnedSunExtension` in 4 (Long Shade biome and mirrak, Leaning Scrub, Stillsand).
- Creature Behaviors defs that serve the sun: `RM_GlareBlind`, `RM_GlareAdapted`, `RM_Mirage`, `RM_ShadeDash`,
  `RM_ThinkTree_ShadeHop`, `RM_ThinkTree_SunEscape`, `RM_ThinkTree_ShadeSeekingWander`.

### Mod Settings

In `src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs` (group 39, "Direct Sun"): `sunHeatEnabled`
(the master, labelled "Direct Sun"), `sunHeatStrength`, `directSunZenithC` (default 55), `directSunWeatherDims`,
`directionalShadeEnabled`, `treeCanopyShadeEnabled`, `canopyShadeStrength`, `shadeOverlayButton`, `canopyGroundTint`,
`renderedCrownShadows`, `sunPathingEnabled`, `sunPathCostMultiplier`, `sunLoadBarEnabled`, `parasolShadeEnabled`,
`shadeTentEnabled`, `decoyShadeEnabled`, `shadeHopEnabled`, `shadeHopRangeMultiplier`, `sandGlareEnabled`,
`sandGlareStrength`, `glareBlindEnabled`, `glareBlindRateMultiplier`, `mirageEnabled`, `mirageBreakChanceMultiplier`;
the fixed-sun rows `pinnedSunEnabled`, `pinnedSunSkyStrength`, `sunFlareHiddenBehindPlanet`, `worldSunPinned`,
`tidalSunGlowByGeometry`, `shadeGridEnabled`, `movingShadeEnabled`. Air heat: an on/off and a degrees row in each of the
Forge, Terminal Biomes and Greentide settings. Every default is on, or 1, or 55. `sunShieldEnabled` ("Standing masts and
skeletons cast shade") gates the lee that the Long Shade mast and lure awning and Stillsand's giant skeletons cast
(`RM_ShadeGear.cs`, the lee mode). No row for mountain shade.

### Tests (run 2026-11-27 in this clone)

| Test | What it decides | Reading |
|---|---|---|
| `src/RimMandrake/Utils/selftest_sun_heat.py` (C# `Source/SelfTest/Program.cs`) | the sun and crown geometry cases named on the two boundary pages | **65/65 passed** |
| `src/RimMandrake/Utils/selftest_direct_sun.py` | no biome carries a sun field; settings rows; weather; hot air | **ALL PASS**, each planted fault caught |
| `src/RimMandrake/Utils/selftest_tree_crowns.py` | no biome carries a crown field; giants' factors; canopy settings; drawn shadow | **ALL PASS**, each planted fault caught |
| `src/RimMandrake/Utils/selftest_planet_fixed_sun.py` | the fixed sun from the planet's geometry | **72/72** |
| `src/RimMandrake/Utils/selftest_shade_lessons.py` | the shade lessons, offline | **PASS** (0 fail) |
| `src/RimMandrake/Utils/selftest_tree_crowns_measured.py` | the giants' crowns measured from their art | exit 0, but this slim clone holds no textures: **UNMEASURED** here |
| `src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py "sun:"` / `"crown:"` | the C# cases go red on planted faults | not run here; 12/12 (2026-11-26) and 7/7 (2026-11-27) by the boundary pages |
| `src/RimMandrake/Utils/direct_sun_air_heat_plant_check.py` | hot-air natives still grow | not run here |
| Live scripts in `src/RimMandrake/CreatureBehaviors/`: `live_direct_sun_angle.py`, `live_tree_crowns.py`, `live_canopy_census.py`, `live_crown_shadow_experiment.py`, `live_shade_spread.py` | state reads on a live map | not run here (design text only); readings on file: `design/specs/2026-11-26-direct-sun/live_angle_result.json`, `design/specs/2026-11-26-tree-crowns/*.log`, `src/RimMandrake/CreatureBehaviors/crown_shadow_experiment_reading.json` (L2 partial: drawn, waiting for his look) |

Boundary pages (promises and their tests): `design/specs/2026-11-26-direct-sun/boundary.md`,
`design/specs/2026-11-26-tree-crowns/boundary.md`. No page covers mountain shade.

### Open tickets (ledger, 2026-11-27)

| Item | State | Home | Bearing on the design |
|---|---|---|---|
| `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE` | proposed | game:direct-sun | the move into its own compose member; waits on the merge-or-stand-alone question |
| `SUNSHADE_PROVE_EVERY_TYPE_ONE_HOME` | proposed | game:direct-sun | the offline lint that guards that move |
| `SUNSHADE_DEPLOY_RIDES_THE_SAME_TRUCK` | ready | game:direct-sun | ships the member in the same composed redeploy |
| `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME` | doing | game:direct-sun | the live rows L1 (state reads) and L2 (his tuning sitting) |
| `RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE` | doing, wait to 2026-12-04 | v1 | built (84925b0d77); his look at `D:\ClaudeWork\rimmandrake\instances\b\Saves\CROWN_SHADOW_GREATBOLE_REVIEW.rws` on ArchSmall rules keep, change or drop; two questions ride with it (the greatbole's vanilla shadow box; the trunk strip joined to the crown shadow at a low sun) |
| `RIMMANDRAKE_COUNT_CANOPY_ON_HELD_FEVER_WOOD_AND_CONTAGION` | proposed | v1 | the canopy census of two held biomes |
| `RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT` | proposed | v1 | the held biomes' old sun fields, at their lift |
| `RIMMANDRAKE_SETTLE_BULLOO_HOMING_VERSUS_SHADE_HOP_WALKS_THROUGH_SUN` | proposed | v1 | a Forge animal leaves shade by another job |
| `RIMMANDRAKE_FIX_SUNDASH_READ_WEATHER_COVER_HEAT_ALREADY_DOES` | proposed | mod:Contagion | the sun escape (`RM_ShadeHop.cs`) ignores the weather's sun factor: core code, filed under a held mod |
| `CONTAGION_SUNDASH_DECIDE_UNDER_THE_BLOOM`, `RIMMANDRAKE_BUILD_CONTAGION_BURN_REFUGE_READS_SHARED_SHADE` | proposed | mod:Contagion (held) | consumers of the grid |
| `DECOY_SHADE_TARP_1` | validated | mod:CreatureBehaviors | the decoy shade tarp |
| `SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS` | built | mod:LongShade | the shade lessons |

Closed, and the base of this design: `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`, `DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`,
`DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`, `TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT`, `TREE_SHADE_BUILD_CROWNS_ON_STILTS`,
`TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`, `DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS`, `SHADECRAFT_LESSONS_DESIGN_1`.

## The parts the design must cover

1. **Direct Sun heat.** One felt heat from the sun's angle, the weather and the strength dial, on every sunlit map of a
   fixed-sun world, into vanilla Heatstroke; off on a day/night world. Hot air stays air temperature (a vanilla
   condition). Built.
2. **The shade of hard walls and roofs.** A roof, a tent and a parasol cover at every angle; a wall, a building and a
   rock cast a lee down-sun whose length grows as the sun drops. Built.
3. **Tree shade.** A tree's crown is a parasol on a pole: its shade lies under it at a high sun and slides down-sun as
   the sun drops, sized by the tree's drawn size at its growth; a forest is mostly shade and a clearing is sunlit. Built
   (T1, T2 offline, T4-T6 green; T3, readable, is his look).
4. **Drawn crown shadows.** The greatbole's crown shadow drawn on the ground from the cells it shades. Built as his
   experiment on one tree type; his look decides keep, change or drop.
5. **Mountain shade (new).** A square under a mountain roof casts a shadow much longer than a short wall's, by the sun
   angle, so the player feels the mountain on the map. Not designed, not built.
6. Also in Direct Sun today and owed a place in the design, not new: moving shade from creatures, shade-hop and the
   shade patch graph, sand glare, glare-blind, mirage, haze, the sun-load gizmo, and the shade lessons.

## The 0.1.0 vision (PROPOSAL)

On a world where the sun stands still, the sun is a thing the player plans around on every map. Its heat follows the
sun's height alone: a high sun burns hard and leaves shade only under cover, and a low sun burns gently and throws long
shadows. Every hard thing casts shade by the same geometry: a roof, a tent or a parasol covers its ground, a wall or a
rock throws a lee, a tree's crown shades the ground under it and down-sun of it, and a mountain throws a long shadow
that reaches far out over the open ground, so its bulk shows on the map. The player can see where the shade is and why:
an overlay, the cell readout and the pawn's sun line name the cause, and what the player sees is what the pawn feels. A
dense forest is cool and its clearings are hot; the lee of a mountain is a place to camp. The same tree, wall or
mountain shades the same way on every map, and no biome changes the rule. Each part can be switched off in Mod
Settings, and with everything off the game is vanilla.

## Proposed bars (PROPOSAL; each a plain sentence about what the player sees or can do)

- **sun-follows-the-sky.** A colonist under the sun feels more heat where the sun stands higher, and none where the sun
  is down.
- **one-rule-every-map.** The same shelter at the same sun height gives a colonist the same relief on every map.
- **cover-works-at-every-angle.** A colonist under a roof, a tent or a parasol is out of the sun at any sun height.
- **walls-cast-a-lee.** Beside a wall or a rock, on the side away from the sun, a colonist stands in shade, and that
  shade is longer where the sun is lower.
- **forest-is-shade.** In a dense forest most open ground is shaded, and a clearing cut in it is sunlit at its centre.
- **trees-shade-as-they-look.** A small young tree shades a small patch, a grown giant shades a wide one, and a felled
  tree's shade is gone at once.
- **mountain-throws-a-long-shadow.** Down-sun of a mountain, a band of open ground much wider than any wall's lee is
  in shade, and it is wider where the sun is lower.
- **shade-is-readable.** The player can tell shade from sun at a glance, and the cell readout and the colonist's sun
  line name what shades the ground.
- **what-you-see-is-what-they-feel.** Every cell drawn as shaded relieves a colonist who stands in it, and every cell
  drawn as sunlit does not.
- **hot-air-is-not-sun.** A volcanic or steaming map is hotter on the thermometer, and shade does not cool it.
- **everything-can-be-switched-off.** Each part has its own switch in Mod Settings, and with every switch off the game
  loads and plays as vanilla.
- **old-saves-load.** A save made before a change loads with no error and shows the same shade as a new map with the
  same things on it.

Left to the Designer, not bars: the drawn crown shadow is his look (act 3), not a bar the Designer can lock before he
rules; the numbers (55 at the zenith, the cap of the cast, crown factors, any mountain height) are tuning.

## Offline simulation: yes, and why

**Yes.** Shade is a pure function of geometry (his words, 2026-10-19), so the whole space of sun angles can be solved
offline, and his standing preference is to solve geometry offline first and use the game only for the final look.

- **What it covers:** the felt heat at every sun height; the lee of every caster (wall, rock, tree crown, mountain) at
  every sun height and bearing; a forest's shaded share and a clearing's centre; a mountain's shadow band against its
  shape and the sun; that the overlay, the readout and the felt exposure read one array; the rebuild after a felled
  tree or a mined rock; the cost of a rebuild on a full map.
- **Its form:** the real code, not a copy. `RM_SunHeatMath` is already Verse-free and compiled into the C# SelfTest
  (65 cases today), so the mountain caster joins it as more pure functions over a fake grid, swept over E from 0 to 90
  and every bearing. Synthetic maps (a forest, a clearing, a mountain with a ridge and a cave mouth) are the fake game.
- **What stays live:** one state read per part on a real map (`live_direct_sun_angle.py`, `live_tree_crowns.py` and a
  mountain read like them) to check that the real grid matches the offline one, and his look at how it reads.

## The open question he named on 2026-11-26 (recorded, not answered)

Where Direct Sun ships is still open: merged into Baroque Biomes, or a stand-alone mod that Baroque Biomes requires.
His words are at the top of this page. Baroque Biomes requires Direct Sun in both cases. Until he decides, no work does
the work of a stand-alone mod, and no work removes that option (`design/RimMandrake/standing_rulings.md` §Direct Sun).
The three `SUNSHADE_*` tickets plan the code boundary (an own compose member inside Baroque Biomes, extractable later);
whether they run before his answer is a Designer and Conductor call, not this page's.

## Questions for the owner (each with its evidence)

1. **How tall is a mountain?** Should a mountain's height come from how far a square lies inside the mountain (deep
   rock stands taller, so a ridge throws the longest shadow), or should every mountain-covered square have one height?
   Evidence: the game keeps no height grid for a map. The map generator's `Elevation` grid lives only while the map is
   made (`MapGenerator.Elevation`, a generation variable, read with RimSage; that it is not saved is [guess ~85%]), and
   every rock has the one shadow height 1. But the saved roof grid keeps a coarse trace of it: `GenStep_RocksFromGrid`
   puts rock where elevation passes 0.70, thin rock roof above 0.728 and thick rock roof above 0.798, and clears every
   natural roof patch under 20 cells (read with RimSage 2026-11-27). So any finer mountain height is ours to invent, and the two ways look different: the
   first makes a ridge's shadow longer than a cliff edge's; the second makes every mountain edge throw the same band.
2. **Is the mountain's shadow drawn on the ground?** Should the long mountain shadow be drawn on the ground, as the
   greatbole's crown shadow is drawn, or shown only by the shade overlay and the cell readout? Evidence: vanilla draws a
   rock's shadow at height 1 only (`staticSunShadowHeight 1`), so without a drawn shadow the player sees a short shadow
   beside a long band of felt shade; the only drawn long shadow we have (the greatbole's) waits for his look on
   `RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE` (dated wait 2026-12-04). A drawn mountain shadow is the
   same kind of work, so his ruling on the crown shadow is likely to decide this one too.

Not asked, with the answer taken (the Evidence-for-Ask rule; each is the Designer's to reverse with evidence):
- The pipeline unit is named **DirectSun**, his name for the feature, not "Sun & Shade" (the 2026-10-19 working name
  and the planned folder `src/RimMandrake/SunAndShade/`).
- The 2026-10-19 "one confirm still owed" (D5/D6: Direct Sun on the Scarlands, the Miasma and the `RUT_` twins; sand
  glare keyed to sand terrain) is answered by `GUIDING_PRINCIPLES.md` §1 (a mechanic works by its conditions, owner
  2026-11-21): conditions decide, so it runs wherever the sun shines.
- A mountain shadow cools no air: shade never changes air temperature (2026-10-19, "Ambient heat is normal Rimworld
  rules").
- The caster of mountain shade is the mountain roof, by his words "mountain-covered squares", so a mined cave under
  overhead rock is still part of the mountain that casts.

## How the Designer runs while the build stages are off (measured 2026-11-27)

- The switch is `./pipe off DirectSun` (act `ct_000301`, end condition `ready:DirectSun`). It is a switch on the whole
  mod: `src/RimMandrake/rimflow/role_launch.py` admits a Designer run-now under `mod:<Mod>` (the comment at the
  `out["mod"]` line: "a `pipe off <Mod>` refuses it at its start check"), so while the switch is off the Designer
  cannot run on DirectSun either.
- `src/RimMandrake/rimflow/control.py` has no scope for one mod at some stages (`scope_of`: all, mod, stage, item,
  family, role, game, unit, each alone), and nothing gives a control switch the design-only allowance that an owner hold
  has (`mod_owner_hold.py allow-design`). That piece is missing; it is not built here.
- What keeps the build stages still without the switch: the maturation tick launches build-stage runs only for mods on
  the advancing list (`./pipe queue`), and DirectSun is not on it. The Workshop ticket lane is the other door: it built
  the drawn crown shadow from a `game:direct-sun` ticket on 2026-11-27 (`RIMMANDRAKE_SWITCH_OFF_LANE_GAME_TICKETS_CROWN_SHADOW_RAN`).
- So the commands that start the Designer, once the Conductor lifts the switch (`./pipe on DirectSun --why "..."`):
  `python3 src/RimMandrake/rimflow/maturation.py advance DirectSun --to designer --by CONDUCTOR --why "..."`, then
  `python3 src/RimMandrake/rimflow/role_launch.py run-now --role Designer --concept design/concepts/DirectSun --by
  CONDUCTOR --why "..." --apply`.

## What must happen before it runs

The mod is admitted at intake, with its Designer record (`stage.json`, `designer_stage.py init`), Design Version 0.1.0
(the pipeline's lock for a new mod), and switched OFF (`./pipe off DirectSun`). His card of 2026-11-27 asks for design
attention now; it does not start a build. Before its build stages may move, its readiness list
(`design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline) must read READY, with every
component on its path looked at and each open pipeline ticket classed BLOCKS, RARE or NOT ON PATH:
- the move from intake (`maturation.py advance --to designer`), the Designer role launch (`role_launch.py run-now
  --role Designer --concept design/concepts/DirectSun`), its exam, coverage judge and `lock-bars`;
- whether a pipeline record can span a mod whose code sits inside another member (Creature Behaviors) and whose defs sit
  in a third (Environmental Hazards) and three biome mods: UNMEASURED, and a likely BLOCKS row;
- preflight; the offline build of Creature Behaviors (`winbuild.py CreatureBehaviors`) and its deploy inside the
  composed `mandrake.rm.biomes`;
- the tests-first stage, with `selftest_sun_heat.py`, `selftest_direct_sun.py` and `selftest_tree_crowns.py`
  registered as deciders;
- the in-game stage: a small list (`design/concepts/DirectSun/version/small_list.json`, not written yet) with Baroque
  Biomes, WeatherSuite, all five DLC and the bridge, and the live scripts above;
- the walk brief and the road back.
