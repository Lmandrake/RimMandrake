# One Direct Sun, planet-wide: design pass, 2026-10-19

FOUNDRY design pass. Nothing in mod code or defs was changed. The owner ruled on it the same day (§8).
§1–§2 describe the code as built today; §3 onward is the ruled model. Build items:
`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`, `DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`,
`DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`, `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME`.

The owner, today (2026-10-19), verbatim:

> "I thought we don't have different "kinds" of heat per biome. Please compare all the extreme heat
> biomes. We need to do the same Direct Sun treatment everywhere. This is now a design pass topic to
> do, right now."

Standing words this pass works under (owner typed, 2026-09-29, `SOLAR_HEAT_EXPOSURE_1` and
`SHADE_GEAR_FAMILY_1`):

> "If we implement the heat load, then places like the Deep Desert and volcanic biomes should
> absolutely roast you similarly. It can't be a new "kind" of heat."
>
> "... this MUST be applied on other biomes where heat is extreme too... and there shade won't help
> you (in steam) or sideways shade (deep desert)."
>
> "The biome takes its sun angle from its latitude ok the planet not a region description." (2026-09-30)

By card, 2026-09-30: *the cover that counts follows the sun angle.*

**Where the three heat kinds came from.** The list "overhead / lowSun / ambient", and *"overhead
sun here [the Long Shade], so parasols and tents work"*, are **our paraphrase** after a `⇒` in
`design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md` §"Rulings — volley turn
4". They are not his words, and CLAUDE.md §"One kind of heat" repeats them as if they were. He
never typed "heat kind". He typed *one* kind of heat, plus a description of which shade helps
where.

---

## 1. Every hot biome today: how its heat is computed

All sun heat runs through one engine. `RimMandrake.CreatureBehaviors.RM_SunHeatExtension`
on a BiomeDef turns it on. `RM_MapComponent_ShadeGrid` computes exposure and the sun elevation.
`RM_SunHeatMath` holds the arithmetic. `RM_SunHeatPatches.Postfix_AmbientTemperature` adds
`exposure × offset × strength × bodySizeFactor` to the temperature a pawn feels, and vanilla
`HediffGiver_Heat` (Heatstroke) does the rest. The engine is shared, but **every number and the
cover rule come from per-biome XML.**

Sun and climate figures are from each biome's sheet (`design/Jawa/worldbuilding/biomes/…`).
Elevation is the sun's height above the horizon, 90 − (arc to the substellar point at 0,0).

| Biome (def) | Sheet: sun / temperature | `heatKind` | Sun heat °C | Scales with sun angle? | Kind switch | Sun height cap | Pinned sky | Def file |
|---|---|---|---|---|---|---|---|---|
| Long Shade `RM_LongShade` | **14.4°** median / 25.5 °C (`desert.md`) | **overhead** | **30 flat** | no | none | pinned 2–30° | yes | `src/RimMandrake/LongShade/Defs/BiomeDefs/RM_LongShade.xml` |
| Stillsand `RM_Stillsand` | 47.4° / 48.3 °C (`desert.md`) | lowSun base | **55 × sin, floor 35** (owner card) | yes | 55° | 85° | yes | `src/RimMandrake/Stillsand/Defs/BiomeDefs/RM_Stillsand_Biome.xml` |
| Cracked Lands `RM_FloodedCanyon` | **21°** median (arc 17→116) / 9·27·45 °C | **lowSun** | 25 flat | no | none | default 60° | no | `src/RimMandrake/CrackedLands/Defs/BiomeDefs/RM_CrackedLands_Biome.xml` |
| Weeping Stones `RM_WeepingStones` | 31° median / 20.5·35.3·57 °C | lowSun base | 14 × sin, floor 7 | yes | 55° | 85° | no | `src/RimMandrake/WeepingStones/Defs/BiomeDefs/RM_WeepingStones_Biome.xml` |
| Contagion `RM_Contagion` | arc median 59, so sun **~31°** / 25·32·45 °C | **overhead** (set today) | 10 flat | no | none | default 60° | no | `src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml` (+ Bloom weather `sunExposureFactor 0.2`) |
| Pyrelands `RM_Pyrelands` | +56° (+21…+84) / 53.6 °C | overhead base | 10 × sin, floor 4 | yes | 55° | **default 60°** | no | `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` |
| Webwork `RM_Webwork` | +51° / 38.6·49.2·58.2 °C | overhead base | 10 × sin, floor 4 | yes | 55° | default 60° | no | `src/RimMandrake/Webwork/Defs/BiomeDefs/RM_Webwork_Biome.xml` (no `MayRequire`) |
| Rust Cathedral `RM_RustCathedral` | **+79°** / 62.5 °C | overhead | **30 (field unset; class default)** | no | none | **default 60°, so 79° reads as 60°** | no | `src/RimMandrake/RustCathedral/Defs/BiomeDefs/RM_RustCathedral_Biome.xml` (no `MayRequire`) |
| The Forge `RM_TheForge` | +51…+64° / 42–56 °C | **ambient** | 15 | n/a | n/a | n/a | no | `src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml` |
| The Scald `RM_TheScald` | arc 23–51, sun +39…+67° (median 54°) / +44..+61 °C at sea level | **ambient** | 15 | n/a | n/a | n/a | no | `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` |
| Fever Wood `RM_FeverWood` | +43° / 45.5 °C | **ambient** | 8 | n/a | n/a | n/a | no | `src/RimMandrake/FeverWood/Defs/BiomeDefs/RM_FeverWood.xml` |
| Greentide `RM_Greentide` | +45° / 45.5 °C | **ambient** | 12 (wet-bulb folded in, card 2026-10-08) | n/a | n/a | n/a | no | `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml` |
| **Scarlands `RM_Warscar`** | **+72° / 59.4 °C** | **none** | 0 | | | | no | `src/RimMandrake/Scarlands/Defs/BiomeDefs/RM_Warscar.xml` |
| **Miasma `RM_Miasma`** | +39° / 42.8 °C | **none** | 0 | | | | no | `src/RimMandrake/Miasma/Defs/BiomeDefs/RM_Miasma.xml` |
| all `RUT_` twins (`RUT_TheForge`, `RUT_ExtremeDesert`, `RUT_Desert`, …) | as their RM_ twin | **none** | 0 | | | | | `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/` |

Not extreme heat, so left out: Leaning Scrub (median 19.7 °C), Wasteland (on the terminator), and
the cold, dark and sea biomes.

**What else reads the heat kind:** `RM_ShadeGear.xml` (gear factor per kind; parasols, tents and
shields count for 0 under ambient), `RM_Gizmo_SunLoad.cs` (the label), `RM_ShadeHop.cs` and the
patch graph (off under ambient), the sun pathing grid (off under ambient), moving shade and
parasol shade (`ShadeGrid.ExposureAt`, ignored under ambient), sand glare (off under ambient),
`SolarMirrors/Source/RM_MirrorPatches.cs` (off under ambient), and
`LongShade/Source/RM_ShipfallCommons.cs`.

## 2. Where the biomes disagree

1. **The same sun height gets opposite cover rules.** At 14° the Long Shade uses `overhead`, so
   roofs and parasols protect. At 21° the Cracked Lands use `lowSun`, so only a lee protects. At
   about 31° the Contagion uses `overhead` and the Weeping Stones use `lowSun`. The Long Shade has
   the lowest sun on the dayside, with shadows 3.9 times their caster's height, yet it runs the
   high-sun rule. Our paraphrase put the overhead label on it, not the owner.
2. **Sun heat does not follow the sun.** The Long Shade (14°) adds 30 °C. The Pyrelands at 56° add
   about 8 °C (10 × sin 56°). The Stillsand at 47° adds about 40 °C. The Rust Cathedral, under the
   highest sun on the planet, adds 30 °C only because the field was never set and the class default
   applies. The heat comes from whatever number each biome's author typed, not from the angle.
3. **Sun height is capped differently.** The default cap is 60°. The Stillsand and Weeping Stones
   raise it to 85°. So the Rust Cathedral's +79° sun and the Pyrelands' sun up to +84° are both
   computed as 60°.
4. **Four biomes under a high sun get no direct sun at all.** The Forge (+51…+64°), the Scald
   (+39…+67°), the Fever Wood (+43°) and the Greentide (+45°) are `ambient`. Shade, parasols and
   shields do nothing there against the sun overhead. Their "ambient" heat also runs through the
   **sun** pipeline, which has four side effects:
   - Weather `sunExposureFactor` multiplies it, so a sun-dimming weather would cool a volcano.
   - The body-size factor applies, so small animals feel volcanic air as hotter.
   - It shows on the **sun**-load bar.
   - It switches off with the **sun** heat setting.

   That is a separate kind of heat in practice, whatever the label says.
5. **Night is ignored.** `ShadeGrid.ExposureAt` and `ExposureFor` have no time-of-day gate. On the
   10 sun-heat biomes without a pinned sky, the vanilla day/night cycle still turns, but sun heat
   applies at midnight too. This is from reading the code; I have not checked it live.
6. **Weather rarely dims the sun.** Only two weathers carry `sunExposureFactor`: the Contagion
   Bloom (0.2) and the Stillsand Dune Gale (0.2). Vanilla rain, fog and storm give full sun.
7. **Extreme heat with no sun heat at all:** the Scarlands (+72°, median 59.4 °C, the hottest sun
   of all after the Rust Cathedral) and the Miasma. No `RUT_` twin carries the extension, so no
   `RUT_` biome has sun heat.
8. **Load guards differ.** Ten biomes guard the `<li>` with `MayRequire="mandrake.rm.biomes"`. The
   extension's own header says to use `mandrake.rm.creaturebehaviors`, which is where the class
   lives. The Rust Cathedral and the Webwork have no guard at all. I have not measured what
   `mandrake.rm.biomes` resolves to at load.

**Where "ambient" really differs.** Two biomes have a heat source that is not the sun:
- **The Forge:** volcanic massif, lava, steam. Its plume fronts already add hotter air through
  their own `AmbientTemperature` postfix (`TheForge/Source/RM_ForgePlumeFronts.cs`), which is
  plain temperature.
- **The Scald:** a boiling crater sea, *"Volcanic heat rises under it"*.

Two biomes are hot, wet air rather than a heat source:
- **The Greentide:** hot fog; the wet-bulb load was folded into its offset by card 2026-10-08.
- **The Fever Wood:** *"still, shadeless heat under the crown"*.

In all four, that heat is real, but **it is air temperature, not sun.** Nothing physical stops the
sun shining on them as well.

Out of scope, and different on purpose: two species-specific sun effects, `RM_Webwork_SunScald`
(the ollathrix's hide, ruled 2026-09-11) and the Contagion's UV sunburn. They are photosensitivity
traits, the same shape as vanilla UV sensitivity, not biome heat.

## 3. The ruled model: one Direct Sun, a pure function of geometry

Ruled by the owner on 2026-10-19 (§8 has his words). **Nothing in it is built**; the build is
`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`.

**Rule DS: the same arithmetic on every map. No biome field changes it.**

- **DS1. Sun elevation.** E comes from the map tile's arc to the substellar point (0,0), with one
  clamp [0°, 90°] everywhere. E ≤ 0 means no Direct Sun. Per-biome `min/maxElevationDegrees` and
  `substellar*` fields are deleted from `RM_SunHeatExtension`.
- **DS2. Intensity.** `offset = 55 °C × sin(E) × weatherSunFactor × bodySizeFactor × strengthDial`.
  55 is one planet number (a setting). There is no per-biome `heatOffsetC`, floor or scaling switch.
  A low sun is less intense and a high sun is much more intense, by the sine alone.
- **DS3. Shade is geometry.**
  - A roofed cell is covered at every E. Any roof counts: a tent, a building, overhead rock. The
    old "only a thick roof counts under a low sun" rule goes.
  - A parasol covers its carrier at every E. The owner kept parasols in the Long Shade, whose sun is
    about 14°.
  - Structures, rock and tall plants cast a shadow down-sun of length height / tan E, capped for
    performance. A high sun leaves almost nothing but covered shade. A low sun leaves long shade.
  - There is no regime switch and no threshold T. `heatKind`, `RM_HeatKind`, `KindFromElevation`
    and `overheadAboveElevationDegrees` are deleted.
- **DS4. Shade gear is parasols and tents.** A tent is any quick roof structure. The standing sun
  shield (`RM_SunShield`) is removed as a shade item, because a wall casts the same lee. The mirrak
  shade cloth keeps one deepening value.
- **DS5. Enclosed rooms** are never exposed. This is unchanged.
- **DS6. Weather.** Every weather has a sun factor. Ours stay as authored (the Contagion Bloom 0.2,
  the Stillsand Dune Gale 0.2), and vanilla overcast weathers get one through a patch (invented
  numbers, which the owner tunes). The factor is a property of the weather, not of the biome.
- **DS7. Time of day.**
  - In Utinni, time of day = location, permanently. Every map of the shipped world has a fixed sun
    at its tile's E, decided by the world and not by a BiomeDef. Today only the Long Shade and the
    Stillsand pin it.
  - On a world with a day/night cycle, Direct Sun is off. The owner allowed this drop; following the
    clock is a later option and not the primary target.
- **DS8. Where it runs.** This is my reading of his principle, and it is the one confirm still
  owed (§8). Direct Sun runs on every sunlit map of the shipped world, with no per-biome opt-in.
  - **Conditional on tree shade** (owner, 2026-10-19): *"If we have an excellent tree shade model
    working, then YES direct sun works the same everywhere on the day side. If we do not go that
    route, we may choose to turn it off on tree-heavy maps (this would be an inferior option)."* The
    model, and the test that decides between the two, are in
    `design/RimMandrake/tree_shade_model_2026-10-19.md`.
  - The Scarlands, the Miasma and the `RUT_` twins get it like every other biome (D6).
  - Sand glare is keyed to natural sand terrain under the sun, not to the Stillsand, so the Long
    Shade's sand glares too (D5).
  - Glare-blind, mirage and shade-hop tuning become planet constants or terrain properties.

**Ambient heat is vanilla air temperature** (D3, *"Hotter air on the thermometer"*). It leaves the sun
pipeline completely. It becomes a permanent vanilla `GameCondition_TemperatureOffset` on the biome's
map. That class exists in 1.6 and reads `GameConditionDef.temperatureOffset`; I confirmed it with
RimSage. The heat shows on the thermometer, rooms leak toward it, coolers fight it and insulation
answers it, all the vanilla way. Shade never changes air temperature, so *"shade won't help you (in
steam)"* needs no special rule. The Greentide's 12 °C card (`WETBULB_FOLD_INTO_HEAT_1`) survives.

**The cost of the condition route.** Outdoor temperature itself rises, so plants and animal comfort
feel it too. Some Forge, Fever Wood or Greentide flora may pass their growth maximum. Before fixing
the numbers, run an offline script that compares every rostered plant's growth temperature limit
against tile median + offset. The vanilla field is still to be looked up in RimSage (UNMEASURED).

### Owner rulings this changes

| Change | Ruling it touches | Effect |
|---|---|---|
| Per-biome `heatKind` goes; shade is geometry | CLAUDE.md's old "every extreme-heat biome declares a heat KIND" (our paraphrase) | Corrected 2026-10-19: CLAUDE.md §"One Direct Sun" |
| The Long Shade keeps parasols, and its long low-sun shadows count too | Our gloss *"overhead sun here, so parasols and tents work"* | The gloss is deleted from `longshade_shade_ideation_2026-09-29.md`; parasols work at every angle |
| One zenith value of 55; the Stillsand's far-ring floor of 35 goes | Card 2026-09-30: *"+55 °C at the substellar point … about 35 °C in the far ring"* | The low edge falls to 55 × sin E |
| The sun shield is removed | `SHADE_GEAR_FAMILY_1` (closed), whose card listed *"simple shields you can stand behind"* | His 2026-10-19 words replace it: *"Keep only Parasols and Tents"* |
| Ambient heat becomes air temperature | Card 2026-10-08, the Greentide at 12 °C | Kept at 12 °C, now as hotter air |

## 4. Migration list (for `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`)

**C#: `src/RimMandrake/CreatureBehaviors/Source/`**
- `RM_SunHeatExtension.cs`: delete `heatKind`, `heatOffsetC`, `maxHeatOffsetC`,
  `heatScalesWithElevation`, `minScaledHeatOffsetC`, `overheadAboveElevationDegrees`,
  `min/maxElevationDegrees` and `substellarLatitude/Longitude`. Under DS8 the extension is no longer
  needed as a switch; keep it only if glare, mirage or shade-hop need per-terrain data.
- `RM_SunHeatMath.cs`: delete `RM_HeatKind`, `KindFromElevation` and `GearKindFactor`.
  `ElevationHeatOffset(Z, E)` loses its floor. Cover becomes `max(roof, parasol, castShade)` at every E.
- `RM_MapComponent_ShadeGrid.cs`:
  - `EffectiveHeatKind` goes, and `EffectiveHeatOffsetC` uses Z.
  - `ResolveSun` uses the one clamp, and a fixed sun on every map of the shipped world (DS7).
  - Delete the ambient branches (lines ~193, 551, 558, 755, 865, 874, 885, 918).
  - The cast length follows height / tan E.
- `RM_SunHeatPatches.cs`: no change in shape.
- `RM_ShadeGear.cs`, `RM_Gizmo_SunLoad.cs`, `RM_ShadeHop.cs`: drop the kind. The gizmo says
  "Direct Sun".
- `RM_CreatureBehaviorsMod.cs`: settings (§5).
- `RM_MapComponent_PinnedSun`: pin by world, not by biome (read first how it is triggered).
- `src/RimMandrake/SolarMirrors/Source/RM_MirrorPatches.cs` and
  `src/RimMandrake/LongShade/Source/RM_ShipfallCommons.cs`: drop the kind gates.
- New: no new class. Ambient heat uses vanilla `GameCondition_TemperatureOffset` through each
  biome's existing permanent-condition bootstrap. The Sump and Miasma lock conditions already work
  this way.

**XML, per biome.** Every `<li>` loses its heat fields.
- Long Shade: drop `heatKind overhead` and `heatOffsetC`. Its pinned sky stays.
- Stillsand: drop kind, offset, scaling, floor, threshold and cap. Glare, glare-blind and mirage
  stay.
- Cracked Lands, Weeping Stones, Pyrelands, Webwork, Rust Cathedral, Contagion: drop all heat
  fields. The Contagion's Bloom 0.2 stays.
- Forge, Scald: drop `heatKind ambient` and `heatOffsetC 15`. Add the `GameConditionDef`s
  `RM_ForgeAirHeat` and `RM_ScaldAirHeat`, 15 °C each, PROVISIONAL.
- Fever Wood, Greentide: the same, `RM_FeverWoodAirHeat` at 8 °C and `RM_GreentideAirHeat` at 12 °C.
- Scarlands `RM_Warscar`, Miasma `RM_Miasma` and the `RUT_` twins: nothing to add under DS8. If the
  owner says no to DS8, they keep no Direct Sun.
- `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml`: remove
  `RM_SunShield`; drop the per-kind columns.
- The arrival-letter heat lines on 10 BiomeDefs (`BIOME_ARRIVAL_LETTERS_ALL_1`): rewrite them without
  kinds.
- New patch: `sunExposureFactor` on vanilla overcast weathers (DS6).

**Tests to change in the same commit.**
- `src/RimMandrake/TheForge/validation.py` `biome_declares_ambient_heat` and
  `selftest_theforge.py:762,892`.
- `src/RimMandrake/FeverWood/validation.py:904-923` and `selftest_feverwood.py:210`.
- `src/RimMandrake/WeepingStones/selftest_weepingstones.py:118`.
- `src/RimMandrake/RustCathedral/selftest_rustcathedral_basefinish.py:74`.
- `src/RimMandrake/Stillsand/selftest_stillsand.py:349`.
- `src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs`: the Stillsand assertions at
  ~610/700/750.
- The fuzz harness, `Utils/mutate_creaturebehaviors_fuzz.py`.

## 5. Mod Settings (`DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`)

Defaults equal the shipped behaviour. With everything off, the game is plain vanilla temperature.

- **Direct Sun** master switch (`sunHeatEnabled` today, relabelled) and the **strength** dial
  (`sunHeatStrength`, exists).
- **Direct Sun at the zenith (°C)**: default 55. New.
- **Weather dims Direct Sun**: new.
- **Direct Sun on day/night worlds**: off. It is labelled unsupported, and off is the only option
  built.
- **Deleted:** `kindFromElevationEnabled` and any threshold slider.
- These toggles stay: directional shade, sun pathing, sun-load bar, sand glare, glare-blind and
  mirage.
- **Air heat** lives in each biome mod's own settings: an on/off and a °C slider for the Forge, the
  Scald, the Fever Wood and the Greentide. Each label says the setting changes the map's
  temperature, so plants feel it too.

No new cross-biome switch is built (owner, 2026-10-15).

## 6. Test plan

**Offline** (`DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`), in `selftest_sun_heat.py` and the C#
SelfTest:
- **Equality across biomes:** for E ∈ {0, 5, 14, 21, 31, 45, 56, 79, 90}, the offset and the
  exposure of an open cell, a roofed cell, a parasol and a lee are identical in every biome.
- **Intensity:** 55 × sin E, and 0 at E ≤ 0.
- **Shadow length:** height / tan E. At 85° no open cell beside a wall is shaded. At 14° the lee is
  about four times the height.
- **Lint:** no BiomeDef or patch carries a heat-kind or per-biome sun field (XML parsed as elements),
  and `RM_SunShield` is not shade gear.
- **Air heat:** the four conditions carry `temperatureOffset`, and their biomes carry no sun number.
- The fuzz run mutates Z and E.

**Live** (`DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME`):
- **L1:** state reads on Long Shade, Pyrelands and Forge maps. On each map, read an open cell, a
  roofed cell, a parasol and a lee: the same E gives the same numbers, the lee is long at a low E
  and absent at a high E, and the Forge thermometer moves by the air-heat offset.
- **L2:** an owner-watched sitting. He tunes the zenith value, the weather factors and the air-heat
  offsets, plus the rest-dash strictness inherited from `SOLAR_HEAT_EXPOSURE_1`.

## 7. Decisions

D1–D4 are ruled (§8). D5 and D6 were not asked; DS8 applies his principle to them, and it is the
one confirm still owed.

## 8. Owner rulings 2026-10-19 and what they changed

By question card on this pass, verbatim:

- **D1:** *"55 C everywhere"*.
- **D2** (asked whether the Long Shade keeps parasols): *"This is too ornate. Keep only Parasols and
  Tents, and Tents are just a quick structure (any roof structure will do the same). Then we just
  need to think about where "shade vs not shade" is for the various maps, and that's a pure function
  of geometry, NOT biome. So: no biome-specific heat, no biome-specific sun. It's a matter of
  geometry (low sun is less intense AND produces longer shade, high sun produces only covered shade
  and much more intense effect). Ambient heat is normal Rimworld rules. Do an opus 5.5 design pass now
  on all the rulings, doc changes, and queue items that need to be updated to effect this change and
  do so."*
- **D3:** *"Hotter air on the thermometer"*.
- **D4:** *"In Utinni this isn't possible: time of day = location, permanently. If these biomes are
  used on a day/night world, then of course it follows solar angle/geometry that is now a function of
  time of day. If that creates too much work, then drop sun heat (should actually be called "direct
  sun") when the day/night isn't constant anymore. That's not our primary deliverable target."*

**What they changed in this design:**
- The low-sun/overhead regime switch and its threshold T are gone. Shade is cast geometry plus covered
  cells (DS3).
- The shield is gone. The only gear is parasols and tents, and a tent is any roof (DS4).
- Ambient heat is air temperature (D3).
- The daylight multiplier is replaced by a fixed sun in Utinni and an off switch elsewhere (DS7).
- The feature is named Direct Sun.

**The one confirm still owed (D5 + D6), with my reading.** Because there is *"no biome-specific
sun"*, I read Direct Sun as running on every sunlit map of the shipped world, with no opt-in.
- The Scarlands (+72°, so about 52 °C of Direct Sun), the Miasma (under its haze's weather factor)
  and the `RUT_` twins get it.
- Sand glare comes from natural sand terrain under the sun, wherever that is, including the Long
  Shade.

If he says no, the build adds an opt-in list, which is a one-line gate.

**Queue changes** (ledger, FOUNDRY shard, `--by-card "Sun heat design pass → 55 C everywhere / pure
geometry, no biome kind"`):
- **Filed:**
  - `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` (code and XML; replaces
    `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID`)
  - `DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS` (blocked on the model)
  - `DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`
  - `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME` (bridge, blocked on the model; replaces
    `SOLAR_HEAT_EXPOSURE_1` and carries its owed rest-dash sitting)
- **Superseded:** `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID` and `SOLAR_HEAT_EXPOSURE_1`. Their prose is in
  `infrastructure/state/items/closed/`.
- **Noted and edited:** the live items in the table below.

### Every place that stated or depended on the old model

Swept with `grep -rniE "heat ?kind|heatKind|sun ?heat|lowSun|low-sun|parasol|shade gear|ambient
heat|LONG_CARRY|sun kind|direct sun|overhead sun"` over `design/`, `infrastructure/state/items`,
`infrastructure/state/facts`, `skills/`, `infrastructure/agents` and `CLAUDE.md`, plus the ledger
event files for open items. The **record** rows are dated sitting or review records: they tell the
history of a day and direct nothing now, so they were left as written.

| File / item | What it said | Action |
|---|---|---|
| `CLAUDE.md` §"One kind of heat" | every extreme-heat biome declares a heat KIND; gear works per kind | **rewritten**: "One Direct Sun, a pure function of geometry" |
| `design/RimMandrake/standing_rulings.md` | no heat ruling (0 hits) | **added** §Direct Sun with his words and a test |
| `design/RimMandrake/biome_rulings.md` | no heat ruling (0 hits) | **added** "No biome-specific sun or heat" |
| `infrastructure/state/facts/*`, `skills/*`, `infrastructure/agents/*` | 0 hits | none |
| `SOLAR_HEAT_EXPOSURE_1` | spec §2: heat kinds per biome; A2 "each biome's heat kind behaves as declared" | **superseded** by `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME`; A2 void |
| `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID` | the Contagion owes a kind | **superseded** by `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` |
| `STILLSAND_SUN_LIVE_VERIFY_1` | "above 55° a roof protects, below it only a lee" | **edited**: that clause is void; the rest stands |
| `WEBWORK_FELLED_NOON_RITE_1` | rite gate = the biome's overhead threshold | **edited**: a fixed sun is always local noon; the gate is sun above the horizon |
| `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` | §4 `heatKind overhead`; a criterion reading it | **edited**; the criterion is struck as VOID (a heatKind read would go red once the model lands) |
| `BIOME_ARRIVAL_LETTERS_ALL_1` | heat line follows the kind; shield gear | **edited**: the lines are false, and the rewrite is spec 9 of the model item |
| `WETBULB_FOLD_INTO_HEAT_1` | Greentide `ambient` kind | **edited**: 12 °C of air temperature |
| `GREENTIDE_MECHANICS_2` | `RUT_Greentide` ambient kind | **edited** (the BiomeDef is `RM_Greentide` now; the line also names `RUT_`, left as its history) |
| `SHADECRAFT_LESSONS_DESIGN_1` | three pieces; the shield is the low-sun piece | **edited**: two pieces; question 2 restated |
| `LONGSHADE_BEDAZZLE_MECHANICS_1` (Long Carry), `DECOY_SHADE_TARP_1`, `PIT_SUPERDEEP_COLLAPSE_1`, `SOLAR_MIRRORS_BUILD_1`, `STILLSAND_SUN_LANCE_1`, `STILLSAND_SOLAR_STILL_1`, `PYRELANDS_*`, `SCRUB_SETTINGS_WIRE_MASTER_CANNOT_GREY` | do not depend on a heat kind | none. Long Carry gives the dead a parasol, which stays. |
| `FEVERWOOD_CROWN_SOUND_HEAT_1`, `PYRELANDS_HEAT_KIND_BUILD_1`, `WEBWORK_HEAT_SHADE_BUILD_1`, `WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1`, `STILLSAND_SUN_FROM_LATITUDE_1`, `SHADE_GEAR_FAMILY_1`, `SHADEGRID_BRIDGE_READER_1` | closed; built the per-biome kinds | none (closed). Their code is undone by the model item. |
| `design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md` | the `⇒` paraphrase of three kinds | **deleted and replaced** with the ruling |
| `design/Jawa/worldbuilding/biomes/kits/greentide_kit_spec.md` | ambient kind and its engine route | **edited**: air heat |
| `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` | "overhead-sun biome", heat kind recorded | **edited**: sun elevation |
| `design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md` (line ~99) | mirrors inert under ambient | **edited** |
| same file, lines ~17–23 | inventory of today's code (`ExposureAt` by heat kind) | true of today's code; left |
| `design/validation_walks/_drafts/must_show_drafts_2026-10-18.md` | parasol, tent and shield bar | **edited**: the shield is dropped |
| `design/validation_walks/RimMandrake/EnvironmentalHazards.md`, `LongShade.md` | owned by `SOLAR_HEAT_EXPOSURE_1` | **repointed** to `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME` |
| `design/validation_walks/RimMandrake/Stillsand.md` | carries the sun-heat extension | true today; the model item decides it |
| `design/RimMandrake/four_biomes_readiness_2026-10-19.md` | heat-kind row; Contagion FAIL | **edited**: no kind owed |
| `stillsand_bedazzle_review_2026-09-29.md`, `stillsand_turn3_development_2026-09-30.md`, `stillsand_bedazzle_cast_2026-09-30.md`, `longshade_bedazzle_cast_2026-09-29.md`, `pyrelands_bedazzle_review_2026-10-01.md`, `webwork_bedazzle_review_2026-10-02.md`, `rustcathedral_bedazzle_review_2026-10-02.md`, `weepingstones_bedazzle_review_2026-10-02.md`, `feverwood_bedazzle_review_2026-10-02.md`, `greentide_bedazzle_review_2026-10-02.md`, `miasma_bedazzle_review_2026-10-02.md`, `gelatinousslime_bedazzle_review_2026-10-02.md`, `sump_bedazzle_review_2026-10-01.md`, `the_scald_floor_sitting_agenda_2026-10-02.md` | per-biome kind findings and recommendations | record |
| `design/RimMandrake/gpt_reviews/{DESIGN_PASS_2026-10-08,CreatureBehaviors,FeverWood,VERDICTS}.md`, `design/RimMandrake/mod_audit/records/batch_15.md` | heat-kind references | record |
| `cauldron.md`, `the_webwork.md`, `webwork_kit_spec.md`, `folk_gesture_mechanics.md`, `assailant_weapon_remnants.md`, `ship_shields_deep_design.md`, `flowworks_pits_unified_model_2026-10-02.md`, `pit_superdeep_collapse_spec.md`, `pit_exposure_to_the_elements_2026-10-11.md`, `mod_validation_runner_spec.md` | "direct sunlight" as prose, or vanilla heat | none: no kind is stated |
| `src/**` (C#, XML, selftests) | the built kinds | **not touched** (mod code is out of scope here); listed in §4 for the model item |
