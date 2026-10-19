# Sun & Shade: standalone mod or part of Baroque Biomes? Design pass, 2026-10-19

**Owner ruling, 2026-10-19 (question card):** "Where does Sun & Shade live? -> Own piece inside Baroque Biomes, standalone later (Recommended)". Alternative C stands; items filed from section 6 (C list), with `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE` ordered before the DIRECT_SUN_* and TREE_SHADE_* build items.

FOUNDRY design pass. No mod code, defs, game or bridge were touched. This doc files nothing: the
items in §6 are a list to file once the owner has picked.

The owner, 2026-10-19, verbatim:

> "I would like a design pass now to ask the question 'is this best as a standalone mod called Sun &
> Shade or is it best baked into Baroque Biomes only?' It seems like it might actually benefit from
> being modular outside the biomes and include the direct sun angle logic, the effect of being in
> direct sunlight, parasols, tents, structure shade, large tree/object shade, etc. There's also the
> Huge Things mod to consider too. Advise me, and present three alternatives and their relative
> tradeoffs for development as well as later re-use."

Already ruled today, and the same under every alternative below: one Direct Sun model that depends
only on geometry (`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`, DS1–DS8), and tree
shade from the projected crown (`design/RimMandrake/tree_shade_model_2026-10-19.md`). **This pass
decides only where that code lives and ships, not how it behaves.**

---

## 0. The short answer

**Sun & Shade is already baked into Baroque Biomes.** All of it lives in the Creature Behaviors
engine, and that engine ships inside `mandrake.rm.biomes`. Because Baroque Biomes is *composed*
(each member keeps its own source folder and DLL; `src/RimMandrake/Biomes.compose.json`), "standalone
or baked in" is mostly a **packaging flag**. The **code boundary** is the part that matters, and it can
be drawn now whichever way the mod ships.

**Recommendation: C.** Draw the boundary now. Give Sun & Shade its own source folder, DLL and settings
section, and keep shipping it inside Baroque Biomes. Extract it as a standalone mod (A) only when
Direct Sun can do something on an ordinary day/night world. Today it cannot: the ruling DS7 turns it
off there.

## 1. Where every piece lives today (measured this pass)

| Piece | Where it is | Ships in |
|---|---|---|
| Shade grid (roof shade, cast shade, exposure, the sun path-cost grid, light-source hook `IRM_LightLayer`) | `src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs` (1062 lines) | `mandrake.rm.biomes` (CB engine member) |
| Sun arithmetic, heat extension, ambient-temperature postfix | `RM_SunHeatMath.cs`, `RM_SunHeatExtension.cs` (plus `RM_SunDashExtension`), `RM_SunHeatPatches.cs` (same folder) | same |
| Pinned (fixed) sun, rendered-shadow vector | `RM_MapComponent_PinnedSun.cs`, `RM_PinnedSunExtension.cs`, `RM_PinnedSunPatches.cs` | same |
| Moving shade (creatures that cast shade) | `RM_MovingShadeLayer.cs`, `RM_MovingShadeMath.cs`, `RM_Comp_ShadowCaster.cs` | same |
| Shade gear comp, sun-load gizmo, shade-hop, patch graph, glare | `RM_ShadeGear.cs`, `RM_ShadeClothExtension.cs`, `RM_Gizmo_SunLoad.cs`, `RM_ShadeHop.cs`, `RM_ShadePatchGraph.cs`, `RM_GlareBlind.cs` | same |
| **Total sun core to move** | **15 files, 3833 lines**, out of CB's ~22,450 lines and 171 `Compile Include`s | |
| Parasol, shade tent and sun shield ThingDefs | `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml` (`RM_Parasol`, `RM_ShadeTent`; `RM_SunShield` is to be deleted under DS4) | `mandrake.rm.biomes` (EH engine member) |
| Sun settings (about 20 fields: `sunHeatEnabled`, `sunHeatStrength`, `directionalShadeEnabled`, `sunPathingEnabled`, `sunLoadBarEnabled`, `shadeHopEnabled`, `shadeGridEnabled`, …) | `RM_CreatureBehaviorsSettings` in `RM_CreatureBehaviorsMod.cs` | CB's settings page |
| Per-biome sun XML (`RM_SunHeatExtension`, `RM_PinnedSunExtension` `<li>`s) | 13 BiomeDefs: LongShade (8 class refs), Stillsand (5), Greentide, Webwork, TheForge, TerminalBiomes, RustCathedral, Pyrelands, FeverWood, CrackedLands, Contagion, WeepingStones | `mandrake.rm.biomes` |
| **Planet geometry (where the sun angle comes from)** | `PlanetGeometryDef` and `WeatherGeometryUtility.ArcFromSubstellar` in `src/RimMandrake/WeatherSuite/Source/WeatherSuiteHook.cs` (namespace `RimMandrake.StarWars.WeatherSuite`, a legacy name). Ash'karr's instance is `src/RimUtinni/AshkarrWeatherSuite/Defs/WeatherGeometryDefs/WeatherGeometryDefs_Ashkarr.xml` | `mandrake.rm.weathersuite` (needs Core only) + `mandrake.rut.weathersuite` |
| Huge Things | `src/RimMandrake/HugeThings/` (8594 lines): solid trunks from contact masks measured from the art, drawn-size hitboxes, titans. **No shadow or shade code.** Pure drawn-quad kernel `Source/Kernel/RM_HugeFootprintKernel.cs` (`side = drawSize.x × visualSizeRange.Lerp(growth)`, with jitter). 10 opt-in plants, all Rot giants (`src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml`), so **all on the night side, where Direct Sun is off** | standalone `mandrake.rm.hugethings` (loads before `mandrake.rm.biomes`) |
| Settings framework | `src/RimMandrake/_Shared/SettingsKit/` is **source-linked** into each mod (`<Compile Include … Link=…>`), so it costs nothing in any placement | n/a |

**Two premises in the brief that the code does not bear out:**
- **FlowWorks has no shade grid.** No FlowWorks source file references `ShadeGrid`, `ExposureAt` or sun
  elevation. The words "shade" and "sun" there are shader names. The pit design docs mention direct
  sunlight only as prose.
- **PyrelandsMechanics (`src/RimUtinni/PyrelandsMechanics`) has no sun code.** Its sun heat is the
  `RM_SunHeatExtension` `<li>` on `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`.

**Who consumes the sun core from outside it:**

| Consumer | How | Breaks if a type moves or is renamed? |
|---|---|---|
| CB's own creature AI: shade seeking, shade-grid wander, false shade, shadow follower, shade stagger, dung seeder, heat-burst predator, weather sense | compile-time, same DLL | becomes a cross-DLL reference to the new DLL |
| `src/RimMandrake/SolarMirrors` | csproj `HintPath` to `RimMandrake.CreatureBehaviors.dll`; About.xml **hard-depends on `mandrake.rm.biomes` just for the shade grid** | yes: the HintPath |
| `src/RimStarWars/Sarlacc` (`RSW_SwimmerRoad.cs`, the patch graph) | csproj `HintPath`; loads after `mandrake.rm.biomes` | yes: the HintPath |
| `src/RimMandrake/Watchers/Source/RM_WatcherCues.cs` | **reflection by the string** `"RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid"` | **silently**, if the full type name changes |
| `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchShadeGridTools.cs`, `JawaBenchShadeProbeTools.cs` | reflection by the full names of ShadeGrid and PinnedSun | silently: the bridge reader goes blind |
| `src/RimStarWars/SWBestiary`, 13 biome folders | XML `Class="RimMandrake.CreatureBehaviors.…"` | yes: a config error at load |
| Saves | the map's component list stores `RM_MapComponent_ShadeGrid` and `RM_MapComponent_PinnedSun` **by class name**, even though ShadeGrid has no `ExposeData` | a red "could not find class" error on every existing save if renamed |
| `src/RimMandrake/OasisMaker`, `src/RimMandrake/MovingDunes` | comments only | no |

**The rule that settles naming:** RimWorld resolves `Class=` and saved component classes by **full type
name across all loaded assemblies**, not by DLL. A type can move to a new DLL **without changing its
full name**. If it does, no XML, save or reflection string changes. Only the two csproj HintPaths do.

## 2. The three alternatives

The three share the build already filed (`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`, its settings,
selftest and live items, and the three tree-shade items). The cost columns below are the **extra**
work on top of that.

### A. Standalone mod "Sun & Shade" (`mandrake.rm.sunshade`)

Its own packageId, About.xml, folder `src/RimMandrake/SunAndShade/`, assembly `RimMandrake.SunShade.dll`
and settings page. It holds the sun core (§1 table), parasol and tent defs, crown shade, the overlay
and mouseover, and glare. Baroque Biomes, SolarMirrors and Sarlacc hard-depend on it.

- **Sun angle provider:** Sun & Shade hard-depends on `mandrake.rm.weathersuite` and reads
  `PlanetGeometryDef`. **That def already is the pluggable provider**: WeatherSuite is generic and inert
  without one, and Utinni plugs in Ash'karr's. It needs one new field, `fixedSun` (time of day =
  location). With no def, or `fixedSun` false, DS7 applies: Direct Sun is off. A new
  provider interface would only rebuild this.
- **Dependency graph:** Core, Harmony → WeatherSuite → **Sun & Shade** → Baroque Biomes (CB's AI
  consumers and 13 biomes' XML), SolarMirrors, Sarlacc; Watchers and JawaBench by reflection.
  Huge Things has no edge (§4).
- **Load order:** after Harmony and WeatherSuite, before `mandrake.rm.biomes` and
  `mandrake.rm.hugethings`. One new entry in every player's mod list.
- **Tier:** RM. The model is generic. The planet-specific part is data (Ash'karr's `PlanetGeometryDef`,
  already RUT). Namespace `RimMandrake.SunShade` for new types. Moved types keep their
  `RimMandrake.CreatureBehaviors.*` full names (§1 rule), which the naming scheme tolerates as a
  save-compatibility exception.
- **Mod Settings:** its own page. On it: the Direct Sun master, strength, zenith °C, weather dimming,
  the day/night mode, directional shade, sun pathing, the sun-load bar, shade-hop, canopy shade and
  strength, the overlay button, and glare. The per-biome air-heat rows stay with each biome in
  Baroque Biomes (D3: air heat is a biome's temperature, not sun).
- **Dev cost:** **+5 to +7 agent-days.**
  - The move itself: 1.5.
  - Its own About, mod-list tiers (`src/RimMandrake/Utils/modset_builder.py` closures pick it up through
    the dependency), a standalone minimal-list load-proof, and its first functional script and
    `validation.py` (debug process rule): 1.5.
  - Splitting the settings page: 0.5.
  - To be worth a separate download for anyone off Ash'karr, the **follow-the-clock mode**
    (`DIRECT_SUN_WIRE_FOLLOW_THE_CLOCK`): 2–3. Vanilla already computes a sun shadow vector for its
    building shadows (`GenCelestial`; the exact 1.6 API is UNMEASURED and to be checked in RimSage).
- **Tests:** the existing CB SelfTest and fuzz sun assertions move with the code. New:
  - a load-proof on Core + Harmony + WeatherSuite + Sun & Shade (22 s on the minimal-list regime);
  - a vanilla-world row: Direct Sun off, parasols harmless, no errors.
- **Re-use by others:** highest. Any planet mod ships a `PlanetGeometryDef` and gets fixed-sun shade;
  with the clock mode, any vanilla colony gets parasols that matter. Our SolarMirrors and Sarlacc stop
  dragging all 31 Baroque Biomes members in for one grid.
- **If a player disables it:** they cannot remove it while Baroque Biomes, SolarMirrors or Sarlacc is
  loaded, because those are hard dependencies. Its master switch is the off switch, and with it off
  the game is vanilla temperature. A third-party user who removes it loses placed parasols and tents
  with the usual "could not load reference" for a removed mod.
- **Save migration:** safe if moved types keep their full names. The settings file is keyed by mod
  folder and class, so players' sun settings reset to defaults once (shipped defaults).
- **Donor-free load risk:** **highest.** A new packageId must be on the live ModsConfig and in the
  donor-off tier closure. It goes there at the same deploy as the composed `mandrake.rm.biomes`
  redeploy, which `DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS` and the `donor_off_phase0` tier are
  already waiting on.

### B. Kept in Baroque Biomes, inside Creature Behaviors (today's layout)

Build the ruled model and the crowns in place, in `src/RimMandrake/CreatureBehaviors/`. Parasol and
tent stay in EnvironmentalHazards.

- **Dependency graph:** unchanged. SolarMirrors and Sarlacc keep needing all of Baroque Biomes.
- **Load order and packageId:** unchanged. No new mod.
- **Tier:** RM. Namespace `RimMandrake.CreatureBehaviors`, as today.
- **Mod Settings:** a "Direct Sun" group on CB's page, as `DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`
  already plans.
- **Dev cost:** **+0.** The filed estimates stand.
- **Tests:** as filed (`DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`,
  `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`, `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME`).
- **Re-use by others:** none without taking all 31 members. Our own re-use means depending on the whole
  of Baroque Biomes, as SolarMirrors does today.
- **If a player disables it:** the master switch makes the game vanilla. There is nothing separate to
  remove.
- **Save migration:** none.
- **Donor-free load risk:** lowest. It rides the Baroque Biomes redeploy that is already owed.
- **Cost later:** the sun core keeps growing inside a 171-file csproj. The ruled build roughly doubles
  it, with crowns, overlay and readout. Extracting it later means untangling more code. CB's sun and
  creature-AI halves are compiled together, so every sun edit dirties CB's `.srchash` and its review
  state.

### C. Its own member, composed into Baroque Biomes, extractable later (recommended)

A new compose entry, `{"key": "SunAndShade", "source": "SunAndShade", "group": "engine", …}`, listed
**before** CreatureBehaviors in `src/RimMandrake/Biomes.compose.json` (Assemblies load in LoadFolders
order, and CB's AI compiles against it). It has:
- its own folder `src/RimMandrake/SunAndShade/`;
- its own csproj and DLL `RimMandrake.SunShade.dll`, with its own `.srchash` and review unit;
- its own `Mod` subclass and settings page (ExplosiveGrowth already does this inside Baroque Biomes);
- the parasol and tent defs, moved from EH.

It still ships as `mandrake.rm.biomes`.

- **Sun angle provider:** as in A. A hard dependency of `mandrake.rm.biomes` on
  `mandrake.rm.weathersuite`, which is already in the closure through `mandrake.rut.patches`, plus the
  `fixedSun` field. It replaces the per-biome `substellar*` fields that DS1 deletes anyway.
- **Dependency graph:** inside Baroque Biomes, Sun & Shade comes before CB, which comes before the
  biomes. The outside edges are as in B. Only the two HintPaths change.
- **Load order and packageId:** unchanged. No new mod-list entry.
- **Tier:** RM. Naming as in A.
- **Mod Settings:** its own page, "Sun & Shade", with exactly A's rows. So extraction later moves no
  settings code.
- **Dev cost:** **+1.5 to +2 agent-days.**
  - The pure move: 1.0. Behaviour is unchanged, proven by identical selftest output before and after.
  - The type-home lint: 0.25.
  - The compose entry and collision sweeps: 0.25.
  - The settings page split: 0.5.
- **Tests:** A's offline tests, plus the compose sweeps
  (`src/RimMandrake/Utils/biomes_compose_sweeps.py`). There is no standalone load-proof yet, because
  it never loads alone.
- **Re-use by others:** our own mods compile against one small DLL, not CB. Third parties have to wait
  for the extraction, which is a packaging step.
  - **Extraction later:** about 1.5 days (About, tiers, load-proof), plus the clock mode if it is wanted.
  - **What extraction involves:** deleting a compose entry and adding an About.xml. No type, def or
  XML changes, because the full names never moved.
- **If a player disables it:** as B.
- **Save migration:** none, because the full names are unchanged. Sun settings reset once, because the
  values move from CB's settings file to the new page's.
- **Donor-free load risk:** low. It needs the Baroque Biomes redeploy that is already owed, plus the
  compose sweeps.

### Considered and not offered: a thin core library with features in consumers

This was the brief's example C: geometry and the shade-grid API in a core mod, while crowns, parasols,
tents and heat ship in Baroque Biomes and Huge Things. I set it aside for three reasons:
1. **Crowns cannot live in Huge Things.** The ruled caster test is anything drawn 1.5 cells or more
   (owner card, 2026-10-19). That is every tree on the day side. Huge Things opts in 10 plants, all on
   the night side.
2. **Splitting the effect from the grid creates a cycle.** Exposure needs parasol cover, the grid needs
   crowns, and the gizmo needs both.
3. **A library with no effect is the part nobody re-uses.** A third party wants parasols that matter.

C gives the same code boundary without spreading one feature across three mods.

### Side by side

| | A standalone | B in CB | **C own member, composed** |
|---|---|---|---|
| Extra agent-days | 5–7 (incl. clock mode) | 0 | **1.5–2** |
| New mod-list entry | yes | no | no |
| Save risk (full names kept) | settings reset once | none | settings reset once |
| Load order risk | new edge before `rm.biomes` | none | intra-mod order only |
| Donor-off load risk | highest | lowest | low |
| Re-use by our mods without Baroque Biomes | yes | no | no, until extracted |
| Re-use by third parties | yes (useful off Ash'karr only with the clock mode) | no | after extraction |
| Cost to change your mind later | to B: re-fold, cheap | to A: an untangle that grows with every build | to A: about 1.5 days, no code changes |
| Review and srchash unit | own | shared with all of CB | own |

## 3. Recommendation: C now; A when the clock runs

1. **The architecture work is the same for A and C, and it is cheap only now.** The ruled build is about
   to rewrite the shade grid and roughly double the sun code. If it lands in its own folder, it is
   reviewed, hashed and tested as its own unit from day one. If it lands inside CB, B's untangle cost
   grows with every item.
2. **Shipping standalone today buys nothing for anyone off Ash'karr.** DS7 (owner: *"drop sun heat …
   when the day/night isn't constant anymore"*) means a separate Sun & Shade on a vanilla planet does
   nothing but stand parasols up. A is worth its mod-list entry, its tier and its load-proof only once
   `DIRECT_SUN_WIRE_FOLLOW_THE_CLOCK` exists.
3. **It keeps the donor-off path clear.** C adds no packageId at the moment Phase 0 is waiting on a
   Baroque Biomes redeploy. It rides that same redeploy.
4. **Extraction stays a packaging step.** C keeps every full type name, its own settings page and its
   own DLL. A later "make it standalone" deletes a compose entry and writes an About.xml.

**Trigger to revisit (A):** the clock mode is built and passes, or one of our mods must ship without
Baroque Biomes. SolarMirrors would qualify the day it is meant to work outside our biomes. Today it
does not have to (owner, 2026-10-15: biome mechanics are promised inside our biomes only).

**The single biggest risk:** a moved type that changes its full name. Watchers and the JawaBench shade
readers find the grid **by a string** and would go blind with no error. Every existing save would log a
missing-class error for the map components. The move must keep full names, and a lint must prove it
(§6, item 2).

## 4. How Huge Things fits

- **No runtime edge in either direction.** Sun & Shade never references Huge Things and Huge Things
  never references Sun & Shade. Both load before Baroque Biomes, and neither has to be present for the
  other to work.
- **One ruler for drawn size.** Both need what the player sees: `drawSize.x × visualSizeRange.Lerp(growth)`,
  with the plant's position jitter. Huge Things already has the pure kernel
  (`RM_HugeFootprintKernel.Quad`). Move that pure part to `src/RimMandrake/_Shared/DrawnExtent/` and
  source-link it into both, the way SettingsKit is linked, so a tree's hitbox and its crown can never
  disagree (`DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS`).
- **Crown data from the art, not a guess.** The tree design invents crown factor 0.8. Huge Things'
  offline tool `src/RimMandrake/HugeThings/measure_huge_plant_masks.py` already measures each giant's
  ground-contact mask from its sprite. The same pass can measure the crown's opaque extent and height
  and write `RM_TreeCrownExtension` values (a Sun & Shade type, on the plant's own ThingDef) for the six
  day-side giants (`TREE_CROWN_MEASURE_FROM_THE_ART`). This is offline data, not a dependency.
- **Huge animals.** CB's moving shade already lets a creature cast shade through
  `RM_CompProperties_ShadowCaster.castShadeHeight` (2 XML users today). Making a titan cast shade by its
  tier is a later, optional row. It is not part of this decision.
- **"Huge things cast huge shadows"** therefore holds through drawn size alone. A greatbole casts by its
  sprite whether or not it opts into Huge Things.

## 5. What has to move (alternatives A and C)

- **Out of `src/RimMandrake/CreatureBehaviors/Source/`:** the 15 files in §1. Their tests go with them:
  the sun assertions of `SelfTest/Program.cs` (around lines 610, 700 and 750), the sun families of
  `SelfTestFuzz`, and `src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py`'s sun mutations. The
  ThinkTree `RM_ThinkTree_ShadeHop.xml` and `RM_GlareBlind_Hediffs.xml` defs go too.
- **Stays in CB** (creature behaviours that *read* shade): seek-shade, shade-grid wander, false shade
  (and EH's decoy tarp), shadow follower, shade stagger and shade-driven severity, dung seeder,
  heat-burst predator, weather sense, `RM_Hediff_SunScald` (a species trait), the heat soundscape, and
  the mirage. The mirage is a Stillsand desert condition; whether it moves too is a later call.
- **Out of EnvironmentalHazards:** `RM_Parasol` and `RM_ShadeTent`, with unchanged defNames (save-safe).
- **Settings fields** move from `RM_CreatureBehaviorsSettings` to the new page. CB's AI reads
  `shadeGridEnabled` through the new class.
- **Outside:** the HintPaths in `src/RimMandrake/SolarMirrors/Source/RM_SolarMirrors.csproj` and
  `src/RimStarWars/Sarlacc/Source/Sarlacc.csproj`.
- **Deploy:** the folder name `SunAndShade` is unique across all three tiers (measured; the
  duplicate-folder guard in `src/RimMandrake/Utils/deploy_custom_mods.py` would refuse otherwise). Old
  and new DLL must change in **one** deploy, so the same full type name never sits in two loaded DLLs.
- **Order:** do the move **before** `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` starts. It is a pure move
  checked by identical selftest output. The geometry rewrite then lands in the new folder, rather than
  being written in CB and moved afterwards.

## 6. Items to file once he picks (listed only, NOT filed; names pass `rimflow namecheck`)

**If C (recommended):**
1. `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE`: create the compose member `src/RimMandrake/SunAndShade/` with
   its own csproj, DLL and Mod settings page. Move the §5 files and defs without changing full type
   names. Done when the CB SelfTest and fuzz output is byte-identical before and after. Blocks the
   DIRECT_SUN_* and TREE_SHADE_* build items.
2. `SUNSHADE_PROVE_EVERY_TYPE_ONE_HOME`: an offline lint. Every XML `Class=`, every reflected type string
   (Watchers, JawaBench) and every saved MapComponent class resolves to exactly one csproj. It runs in
   the selftest set.
3. `PLANET_GEOMETRY_WIDEN_SUN_STANDS_STILL`: add `fixedSun` to `PlanetGeometryDef` (WeatherSuite), set it
   true in Ash'karr's def, and have Sun & Shade read E and the bearing from it. This feeds DS1 and DS7 in
   the model item.
4. `DRAWN_EXTENT_UNIFY_ONE_RULER_TWO_MODS`: move Huge Things' drawn-quad kernel to `_Shared/DrawnExtent`,
   source-linked into Huge Things and Sun & Shade. The Huge Things fuzz must stay green.
5. `TREE_CROWN_MEASURE_FROM_THE_ART`: extend `measure_huge_plant_masks.py` to emit crown radius and
   height for the six day-side giants (replacing the invented 0.8 there).
6. `SUNSHADE_DEPLOY_RIDES_THE_SAME_TRUCK`: ship the member in the same composed `mandrake.rm.biomes`
   redeploy that Phase 0 is already waiting on. Do not deploy it separately.
7. `SUNSHADE_EXTRACT_DECIDE_WHEN_CLOCK_TICKS` (needs owner, deferred): revisit A when the clock mode
   exists or a non-Baroque mod needs the grid.

Notes on existing items: repoint `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`,
`DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`, `DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`,
`TREE_SHADE_BUILD_CROWNS_ON_STILTS` and `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE` at
`src/RimMandrake/SunAndShade/`. Mark them blocked on item 1.

**If A:** items 1–5 above, with item 1 creating `mandrake.rm.sunshade` as its own mod, plus:
- `DIRECT_SUN_WIRE_FOLLOW_THE_CLOCK` (day/night worlds);
- a standalone minimal-list load-proof;
- About and tier edits (`modset_builder.py`, and SolarMirrors and Sarlacc dependencies).

**If B:** none. The filed items stand as written.

## 7. The decision he must make

**Where does Sun & Shade live?**
- **A:** a standalone mod now (+5–7 days, a new mod in the list, re-usable).
- **B:** stays inside Creature Behaviors (+0, not re-usable, the costliest to change later).
- **C (recommended):** its own unit inside Baroque Biomes now (+1.5–2 days), extracted to A when the
  clock mode makes it worth a separate download.
