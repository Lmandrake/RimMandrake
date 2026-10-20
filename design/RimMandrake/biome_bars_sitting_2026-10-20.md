# Biome north-star sitting: Leaning Scrub, Cauldron, Contagion (prepared 2026-10-20)

**Purpose.** An agent seeded the draft `## north star` bars of three biome walks on 2026-10-01. Since then the mods
have grown a lot: new venomvine forms, venomvine islands, map ruins and camps, vent gas, Burn tells and more. Some
of the seeded bars now describe things the mods do not ship, or ship in another shape. This page proposes, bar by
bar, what to keep, reword or cut, and which new bars to add. **It only proposes.** The bars are his, and nothing
here edits the walk files:
`design/validation_walks/RimMandrake/LeaningScrub.md`, `Cauldron.md`, `Contagion.md` (all three: `state: DRAFT`,
no validated-hash).

**How to use it at the sitting.** For each table row he says *keep*, *reword* (his words win) or *cut*. He also
accepts, rewords or cuts each **new** row. An agent then writes his answers into each walk's `## north star`, and he
validates each section in the same sitting (`python3 src/RimMandrake/Utils/modcheck/cli.py validate <Mod>
--owner-said "<his words>"`). Validating judges the WORDING only. Whether the game meets each bar is a separate live
walk. `### the experience` is still empty in all three walks, and it is his to dictate.

**Sources read (offline, 2026-10-20).** The three walk files. The BiomeDefs, weather, plant, race, terrain and
hediff XML, plus the C# headers and Mod Settings fields under `src/RimMandrake/{LeaningScrub,Cauldron,Contagion}/`.
`design/RimMandrake/four_biomes_readiness_2026-10-19.md`. The Direct Sun ruling
(`infrastructure/state/items/DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES.md`,
`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`, `design/RimMandrake/standing_rulings.md` §Direct Sun).
Decompiled 1.6 `Plant.Print` (RimSage) and the vanilla `Overcast` WeatherDef.

**Two rulings shape every row.**
- **Direct Sun** (owner, 2026-10-19): *"no biome-specific heat, no biome-specific sun. It's a matter of geometry."*
  In Utinni, *"time of day = location, permanently."* So no bar here promises a heat, a sun angle or a time of day
  ("at noon"). A biome can promise only its own **weather** (sky tint, fog, haze). The Contagion's Burn is UV damage
  to natives, which the design doc rules out of Direct Sun scope as photosensitivity, so its bars stay.
- **Zero tiles is not a defect.** No row cites a tile count.

**Legend.** **M** = the claim behind the verdict was measured from a def or code (the "why" names it). **G** = a guess:
how it *looks* has not been seen, or a number is UNMEASURED. A bar can be M on mechanism and still G on look. Some
bars fail today (their "why" says so). That is validation state: it goes in the live walk, never into the bar text.

---

## 1. Leaning Scrub (`RM_LeaningScrub`, `src/RimMandrake/LeaningScrub/`)

10 existing bars: **5 keep, 5 edit, 0 cut; 6 new.**

| bar | verdict | new text (edit/new only) | why | M/G |
|---|---|---|---|---|
| `scrub_lean_visible` | **edit** (see Q1) | On a Leaning Scrub map every stand of fuzz and scrub leans the same way, the map's wind heading, across the whole map; no stand is drawn mirrored against it. | Nothing in the mod draws the Lean. `RM_TheLean.cs` keeps a heading only for scent and fire. Vanilla `Plant.Print` mirrors every plant mesh at random (`flipUv = Rand.Bool`, decompiled 1.6), and `BiomesShell/Source/RM_PlantDrawOrder.cs` passes that flip through. So a sprite drawn leaning faces both ways on the map. As written, the bar needs a draw patch that does not exist. | M (mechanism) |
| `scrub_gale_reads_as_gale` | **edit** (see Q2) | Under `RM_Gale` the scrub visibly thrashes harder than on an ordinary windy day, and the storm wind is heard. | `RM_LeaningScrub_Weather.xml`: the Gale has `windSpeedFactor` 1.5, `windSpeedOffset` 1.5 and `Ambient_Wind_Storm`, but **no overlay**. "Driven dust or fuzz" has nothing behind it. Vanilla plant sway follows wind speed. | M wind, G look |
| `scrub_stall_reads_still` | keep | — | `RM_WindCalendar.cs` Stall freeze (`stallFreezeMaxBodySize` 0.5); `RM_Stall` `windSpeedFactor` 0. | M |
| `scrub_fuzz_plain_reads` | keep | — | `RM_Fuzz` 0.9 heads `wildPlants`. Donor ground cover was moved under the low plants by `Patches/RM_LeaningScrub_GroundCoverDrawLayer.xml`. | G look |
| `scrub_venomvine_forms_distinct` | **edit** | Every venomvine form the biome grows (crown, dripping, twitcher, hollow, rearing, walking, hoard, quench, sworn, shedding, sleeper, strangler, weeper, lure) can be told from the plain thicket and from each other at play zoom. | The bar names 4 forms. `RM_LeaningScrub` `wildPlants` now carries 14 (`RM_VenomvineSixForms.xml`, `RM_VenomvineFourForms.xml`; owner cards 2026-10-03 and 2026-10-08). Whether each has art of its own is UNMEASURED. | M roster, G art |
| `scrub_sweetline_reads_as_landmark` | **edit** | An `RM_SweetlineTree` is the tallest thing on the plain and reads as a named landmark: its generated name is its label. | `RM_SweetlineStation.cs`: name generated at spawn and shown as the label. `RM_Barkwarden` description: *"the only thing on the plain that stands taller than a person"*. `RM_GenStep_SweetlineTrees.cs`: a map holds 0–2, so "no tree" is a normal map. | M |
| `scrub_fauna_various` | **edit** (see Q4) | Every wild kind on `RM_LeaningScrub`'s own roster reads as a distinct animal in one line-up. | "13 wild kinds" is stale: the def lists 19 `RM_` kinds (e.g. `RM_TunnelSnake`, `RM_Zellik`, `RM_Surrik`). A count in the bar would go stale again, so the bar names the roster instead. | M |
| `scrub_runway_bloom_launches_dustflutters` | keep (guess stays) | — | `RM_RunwayBloom.cs`: dustflutters erupt and fly about 40 cells. This is a flyer, so it is judged **only with the owner present** (CLAUDE.md flight law). | G |
| `scrub_never_windless` (cannot) | keep (see Q3) | — | Its own weathers carry wind (`RM_ScrubWind` +0.5, `RM_ScrubWindFog` +0.4). But the biome also rolls stock `Overcast` (5, Odyssey), `GrayPall` (1) and `DryThunderstorm` (1). Vanilla `Overcast` has no wind offset, so on those days the wind is vanilla's. | M weights, G look |
| `scrub_never_lean_mixed` (cannot) | keep (paired with Q1) | — | Fails by construction today, for the same reason as `scrub_lean_visible` (vanilla random mirroring). Keep both bars or cut both. | M (mechanism) |
| `scrub_ripple_shimmer` | **new** | Small wild creatures under the fuzz on a windy day cannot be targeted, and the player sees each one as a faint shimmer where the fuzz moves wrong. | `RM_Ripple.cs` + `RM_RippleHidden` (vanilla invisibility, `visibleToPlayer`), owner card Q9 2026-10-15 *"Hiding with a faint shimmer"*; `rippleMaxBodySize` 0.6. | M mechanism, G look |
| `scrub_venomvine_islands` | **new** | Venomvine lies in islands and hedges across the plain, with open lanes between them and a clear start; the rarer forms grow as rooms inside the islands. | `RM_VenomvineIslands.cs`, owner cards 2026-10-16 (Q1 about 15% of open ground, Q4 rooms); `venomvineStartClearance` 30. | M |
| `scrub_wardens_roost_visible` | **new** | A sweetline tree's bark-wardens are visible asleep against its trunk, and they watch a colonist who walks up without attacking. | `RM_SweetlineGuardians.cs`, owner rulings 2026-10-03: *"walk-up is NOT hostile (they watch you, visibly)"*, "Roosting in the crown of <tree>". | M |
| `scrub_ruins_and_camps` | **new** | A Leaning Scrub map can hold a dead farmstead (broken wall, a comb-row of vaporator wrecks) and a living camp of the comb holds, spread wide and away from the start. | `RM_ScrubInjections.cs` (owner: *"Lots of inhabited injections all over here from ruins to current living denizens."*; card Q10 *"Ruins plus living camps"*); `RM_Faction_CombHolds`, `RM_WindVaporator`. | M |
| `scrub_rearing_stand_tells` | **new** (guess) | A rearing venomvine stand snaps upright, a black fan, when a body pushes into it, and stands out against the leaning plain. | `RM_VenomvineSixForms.xml` description; `RM_VenomvineForms.cs` Rearing (`rearingHours` 2). | M mechanism, G look |
| `scrub_stallhawk_rises` | **new** (guess) | In the Stall the zellik takes to the air and hunts the creatures that move; in the wind it finds nothing to hunt. | `RM_StallHunt.cs`; `RM_Zellik` `MaxFlightTime` 10. Flyer: judged **only with the owner present**. | M mechanism, G look |

---

## 2. Cauldron (`RM_Cauldron`, `src/RimMandrake/Cauldron/`)

9 existing bars: **2 keep, 7 edit, 0 cut; 7 new.**

| bar | verdict | new text (edit/new only) | why | M/G |
|---|---|---|---|---|
| `cauldron_reads_wet_black_dusk` | **edit** | An `RM_Cauldron` map reads as a low, wet-black forest under a dim grey-violet sky in every one of its four weathers; it never reads as ordinary daylight. | "At noon" breaks the Direct Sun ruling: the sun is the tile's geometry, not the biome's. All the biome can promise is its weather. `RM_CauldronWeathers.xml`: day sky (0.56–0.78) grey-violet on all four weathers, and no code dims the light. | M sky, G look |
| `cauldron_vent_bloom_reads_as_gas` | **edit** | Under the vent bloom the air visibly thickens into a grey haze and the light drops below the other Cauldron weathers. | `RM_VentBloom` uses `WeatherOverlay_GrayPallFog` (grey, not "coloured"), sky (0.56,0.54,0.58), the darkest of the four. | M |
| `cauldron_no_rain_or_snow` | **edit** | No rain, snow or clear sky is ever on screen; a rare dry thunderstorm is the only stock weather. | `baseWeatherCommonalities`: Clear, Fog, Rain, RainyThunderstorm, both snows at 0; `DryThunderstorm` 1. All four of its own weathers: `rainRate` 0, `snowRate` 0. | M |
| `cauldron_trees_read_metallic` | **edit** | The twisting thornwood reads as a corkscrewed tree sweating metal, distinct from vanilla trees. | The martyr tree (`RM_TreeMartyr`) was **cut by the owner 2026-10-18** (`RM_CauldronFlora.xml` header). `RM_TwistingThornwood` carries `RM_CompMetalYield`. | M |
| `cauldron_soils_read_dark` | keep (see Q5) | — | Fails today: `RM_CauldronSoil` and `RM_CauldronSoilRich` reuse vanilla `Terrain/Surfaces/Soil` and `SoilRich` textures with no tint (`RM_Cauldron_Terrains.xml`). Meeting the bar needs new terrain art; the other route is to cut it. | M |
| `cauldron_natives_distinct` | **edit** | Every wild kind on `RM_Cauldron`'s own roster reads as a different animal in one line-up. | "The other two natives" is stale: the def lists 15 kinds (`RM_Suush`, `RM_Vexxiss`, `RM_Garsulix`, `RM_Rhossak`, `RM_Radyak`, …). | M |
| `cauldron_suush_floats` | **edit** | The suush reads as a globe drifting above the ground, never walking. Judged only with the owner present. | No longer a guess about the mechanism: `RM_Suush` is a real flyer (`MaxFlightTime` 600, `canFlyIntoMap`). The flight law makes the look an owner-present check. | M mechanism, G look |
| `cauldron_never_bright_day` (cannot) | **edit** | A Cauldron map under a clear, bright sky. | The same Direct Sun reason as the first row: "noon" and "hard shadows" are sun geometry, which belongs to the tile, not the biome. `Clear` is 0 on the def. | M |
| `cauldron_never_magenta` (cannot) | keep | — | Missing-texture guard; still right. | — |
| `cauldron_vent_gas_drifts` | **new** | Gas visibly drifts off the vents and pools against walls; set alight, it burns into toxic smoke; a gas-tap scaffold over a vent stops it. | `RM_VentGas.cs` (own gas grid, drawn by a gas section layer), `RM_GasTap.cs`; owner: *"The gas is highly flammable with toxic smoke and should be stopped."* Gas colour UNMEASURED. | M mechanism, G look |
| `cauldron_dewfall_beads` | **new** | During dewfall, beads of chemical dew appear on open ground outside the home area, and the garden briefly blooms in wrong colours. | `RM_CauldronDewfallVisuals.cs` (owner 2026-10-03: the no-green ban lifts during dewfall). The plant colour swap is **dormant until its art exists** (source header). | M beads, G bloom |
| `cauldron_vexxiss_prints` | **new** | A vexxiss leaves a trail of prints that lasts about a day, turned to its heading; hovering a print names its maker. | `RM_VexxissPrints.cs`, owner card 2026-10-03. | M |
| `cauldron_suush_bursts_when_shot` | **new** | A suush that is shot bursts in a gas explosion, and the burst reads as the creature's doing. | `RM_CauldronFauna.xml` mechanism 3 (*"he said shot, not killed"*). | M mechanism, G look |
| `cauldron_ruin_rig_site` | **new** | A Cauldron map can hold one corroded filter rig, dressed with failed tanks still holding toxic water, broken pipe and slag; studying it teaches the Filter-Works. | `RM_CauldronRuinKit.cs`, owner Q2 2026-10-15. | M |
| `cauldron_rhossak_bound_readable` | **new** | A rhossak stays near the grove tree it is bound to, and its inspect pane says which tree, or that it is unbound. A state read. | `RM_CompRhossakGrove.cs`, owner card 2026-10-19 *"Make them animals and make them bind."* | M |
| `cauldron_no_green_outside_dewfall` (cannot) | **new** (guess) | Green foliage on a Cauldron map outside dewfall. | `RM_CauldronDewfallVisuals.cs` cites a standing no-green ban that lifts only during dewfall. Whether every roster plant's art meets it is UNMEASURED. | G |

---

## 3. Contagion (`RM_Contagion`, `src/RimMandrake/Contagion/`)

10 existing bars: **3 keep, 7 edit, 0 cut; 4 new.**

| bar | verdict | new text (edit/new only) | why | M/G |
|---|---|---|---|---|
| `contagion_bloom_reads_unwholesome` | **edit** | A Contagion map under its standing Bloom reads as a sick, blood-red storm roof with red fog in the air, never an ordinary overcast day. | `RM_ContagionBloom` (70 of 80 weight) day sky (0.72,0.1,0.1), *"Donor red fog re-skinned"* (def header). | M sky, G look |
| `contagion_burn_reads_as_danger` | **edit** | Before a Burn the gawpsacks visibly sink and squash and the rattlegrope shakes; when it lands the sky turns near-white, the fog clears and the natives dive for cover. | Burn tells built by owner card Q6 2026-10-15 (`RM_ContagionTellRender.cs`); `RM_ContagionBurn` sky (1,0.98,0.95); `RM_GameCondition_ContagionBurn.cs` dive. This is UV on natives, not Direct Sun. | M |
| `contagion_repulsor_clears_sky` | **edit** | A powered `RM_CloudRepulsor` shows a violet beam into the sky and brings the Burn to the whole map while it runs; when it stops, the Bloom returns. | `CompCloudRepulsor.cs`: on a Contagion map it forces the map-wide Burn (*"a man-made local Burn"*). There is no cleared patch, and a violet beam is drawn while it is live. | M |
| `contagion_sunbeam_reads_as_beam` | **edit** (guess) | An `RM_Sunbeam` reads as a handheld lens projector, and its shot reads as a line of light, not a bullet. | `RM_Sunbeam.xml`: `ParentName="BaseGun"`, *"A handheld Helix ultraviolet projector"*. It is a weapon, not a beam striking the ground. | M weapon, G look |
| `contagion_flora_reads_as_flesh` | keep | — | `RM_Meatvine`, `RM_Toothmoss`, `RM_Eyebark` and `RM_Wombpod` are all on the roster. | G look |
| `contagion_unfinished_read_malformed` | **edit** | The Unfinished read as half-made, wrong creatures, and no two read alike. | `RM_TheUnfinished` is one race whose limbs roll per pawn (`CompRandomizeUnfinished.cs`), so "and its kin" names no defs. | M |
| `contagion_coalescence_reads_as_mass` | **edit** | An `RM_Coalescence` reads as one living mass that visibly grows through three stages and is clearly where the Unfinished come from. | `Building_RM_Coalescence.cs` (three staged forms) and `RM_Coalescence.xml` `stageGraphics`. | M stages, G look |
| `contagion_grown_limb_visible` | **edit** (drop the guess) | A colonist fitted with a Monstrous grown limb looks different from one with a natural arm. | No longer a guess that "hediffs draw nothing": `RM_PillarArm` and `RM_Lash` carry `renderNodeProperties` with their own textures (`RM_GrownLimbHediffs.xml`). | M |
| `contagion_never_vanilla_forest` (cannot) | keep | — | Still the right guard. | G |
| `contagion_never_magenta` (cannot) | keep | — | Missing-texture guard. | — |
| `contagion_zhool_haze` | **new** | A zhool trails a faint red haze, and plants inside it slowly turn into the Contagion's own flesh-plants. | `CompZhoolHaze.cs` (`RM_OcularJelly`), owner card 2026-10-15 *"Rebuild it in our code"*. | M mechanism, G look |
| `contagion_unfinished_leave_mulch` | **new** | A dead Unfinished leaves no corpse but a small heap of mulch where it fell, never vanishing without a sign. | `RM_ContagionMulch.cs`, owner Q4 2026-10-15; the planet rule *"no animal or pawn ever vanishes without a readable sign"*. | M |
| `contagion_bloody_mess_bursts` | **new** | A Bloody Mess killed in a fight bursts into acid; one that dies giving birth to the organs it grew does not. | `DeathActionWorker_RM_GenomeHostBurst.cs`, owner card 2026-10-15 *"Burst only when killed"*. | M |
| `contagion_native_dive_in_burn` | **new** | In a Burn the UV-shy natives sprint for roof, canopy or water; the armoured ones keep hunting. | `RM_GameCondition_ContagionBurn.cs` (`armoredNatives` `RM_Scaldhide`, `RM_Crispling`). | M mechanism, G look |

---

## 4. Questions for the owner

1. **The Lean is not drawn.** Today the wind heading changes only scent and fire. The game mirrors every plant sprite
   at random, so leaning art faces both ways. Keep `scrub_lean_visible` and `scrub_never_lean_mixed` (which means a draw
   patch is owed on Leaning Scrub maps), or cut both?
2. **The Gale has no dust overlay.** Should the Gale promise driven dust or fuzz on screen (art and an overlay owed), or
   only harder sway and the storm sound?
3. **Stock calm days on the Scrub.** `Overcast` (5), `GrayPall` (1) and `DryThunderstorm` (1) roll with vanilla wind.
   Is that allowed under "every ordinary day carries wind", or should they go to 0?
4. **Whose roster do the fauna bars mean?** Only the biome def's own `RM_` kinds, or also the Star Wars cast that
   UtinniPatches adds (38 kinds on the Scrub, 7 on the Cauldron)?
5. **Cauldron soils use plain vanilla soil art.** Commission dark, gassy terrain art, or cut `cauldron_soils_read_dark`?
6. **Owner-present bars.** Three bars concern fliers: the dustflutter bloom, the zellik and the suush. Judge them at a
   joint session, or keep them only as state reads?

## 5. Owner's answers (by question card, 2026-10-20)

1. **Lean:** keep `scrub_lean_visible` and `scrub_never_lean_mixed`, and build the draw. Leaning Scrub maps stop mirroring plants at random and face them with the map's wind heading.
2. **Gale:** driven dust and fuzz on screen. This needs overlay art and a weather overlay.
3. **Calm days:** give Overcast, GrayPall and DryThunderstorm the Scrub's wind as weather twins, so the rule "the wind never stops" holds.
4. **Roster:** the fauna bars cover only the biome's own `RM_` creatures. The franchise cast is checked elsewhere.
5. **Cauldron soils:** commission dark, gassy soil art for both soils, with the rich soil visibly different. This goes through the art ledger.
6. **Flyer bars:** a state read confirms each flyer can fly and launches. The owner judges the look at a joint session.
7. **Pit cover (FlowWorks):** deconstructing a pit cover drops whoever stands on it, the same as when it is destroyed.
