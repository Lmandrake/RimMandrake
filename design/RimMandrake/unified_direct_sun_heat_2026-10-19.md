# One Direct Sun, planet-wide: design pass, 2026-10-19

FOUNDRY design pass. Nothing in mod code or defs was changed. Items: `SOLAR_HEAT_EXPOSURE_1`,
`CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID`.

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
| The Scald `RM_TheScald` | substellar band, "the substellar sun" / boiling sea | **ambient** | 15 | n/a | n/a | n/a | no | `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` |
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
   (substellar), the Fever Wood (+43°) and the Greentide (+45°) are `ambient`. Shade, parasols and
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

## 3. The unified model: one Direct Sun

**Rule DS: the same arithmetic on every sun-heat map. No biome field changes it.**

- **DS1. Sun height.** E is computed from the map tile's arc to the substellar point (0,0). It is
  one planet constant and one clamp, [0°, 85°], everywhere. A pinned sky uses the same geometry,
  as it does already. Per-biome `min/maxElevationDegrees` and `substellar*` fields are deleted
  from `RM_SunHeatExtension`.
- **DS2. Sun strength.** `offset = Z × sin(E) × weatherSunFactor × daylight × bodySizeFactor ×
  strengthDial`, capped by one planet `maxHeatOffsetC`.
  - Z is **one planet number**. The default proposed is the owner's own card value, 55 °C at the
    zenith.
  - There is no per-biome `heatOffsetC` and no per-biome floor.
- **DS3. Which cover counts.** If E ≥ T, the overhead regime applies: roof, cast shade, parasol and
  tent all count. If E < T, the low-sun regime applies: only a lee shadow, rock or a shield
  counts. T is one planet threshold (55°, the value all four switching biomes already use). This
  is the card *"the cover that counts follows the sun angle"*, applied everywhere instead of only
  where a biome opted in. The per-biome `heatKind` field is deleted. The two regimes are a
  function of the sun, not of the biome.
- **DS4. Enclosed rooms** are never exposed. This is unchanged.
- **DS5. Weather.** Every weather has a sun factor. Ours stay as authored, and vanilla rain, fog
  and storm weathers get one through a patch. The numbers are invented and the owner tunes them.
  The factor dims **direct sun only**.
- **DS6. Daylight.** On a map without a pinned sky, the sun heat is multiplied by the visible sun
  (vanilla `GenCelestial` sun glow). The heat then follows the sun the player sees, and there is
  no midnight sunstroke. Pinning the sky on every dayside biome is the alternative. That is
  cosmetic, so it needs the owner's permission (decision D4).
- **DS7. Opting in stays per biome.** This follows the 2026-10-15 rule, which promises biome
  mechanics only inside our own biomes. The extension becomes a marker meaning "Direct Sun runs
  here", plus the non-heat extras: glare-blind, mirage and shade-hop tuning. Sand glare
  (`sandGlareExposureFloor`) is keyed to terrain, so it can apply wherever there is natural sand,
  including the Long Shade's. Whether it should is decision D5.

**Ambient heat (volcanic, steam, hot fog) is not sun.** It leaves the sun pipeline completely
and becomes **plain vanilla air temperature**, applied as a permanent vanilla
`GameCondition_TemperatureOffset` on the biome's map. That class exists in 1.6 and reads
`GameConditionDef.temperatureOffset`; I confirmed it with RimSage. The heat then shows on the
thermometer, rooms leak toward it and coolers fight it the vanilla way, and insulation answers it
through the vanilla comfort range. Shade does nothing against it because shade never changes air
temperature, which is *"shade won't help you (in steam)"* with no special rule.

**Does this satisfy "no different kinds"?** Yes. After this change there is one kind of heat,
vanilla temperature, and one rule that adds felt sun to it, identical on every map. "Ambient" is
no longer a kind. It is a hotter thermometer, the same as any hot biome's base temperature.

**If he means ambient sources should go entirely**, the four biomes keep only their tile
temperature plus the Direct Sun. That costs:
- the Forge loses 15 °C over the volcano, and keeps only its plume fronts as local hotter air;
- the Scald loses 15 °C over the boiling sea;
- the Fever Wood loses its 8 °C still-air heat;
- the Greentide loses 12 °C, including the wet-bulb share the owner ruled into it by card on
  2026-10-08 (`WETBULB_FOLD_INTO_HEAT_1`), so that decision would be undone.

Their tile medians (42–56 °C) still put a colonist outside the vanilla comfort range, so they stay
hot, but no longer hotter than the sun-only biomes around them.

**A second cost of the GameCondition route.** Outdoor temperature itself rises, so plants and
animal comfort feel it too. Some Forge, Fever Wood or Greentide flora may pass their growth
maximum. The offline check is a script that compares every rostered plant's
growth temperature limit against tile median + offset. The exact vanilla field is still to be
looked up in RimSage, so it is UNMEASURED here. Run the check before choosing the numbers.

### Owner rulings this changes, marked

| Change | His ruling it touches | Effect |
|---|---|---|
| ⚠️ The per-biome `heatKind` goes; cover follows E everywhere | CLAUDE.md "every extreme-heat biome declares a heat KIND" (our paraphrase); the card "cover follows the sun angle" (2026-09-30) | The card is **extended** to every biome. The CLAUDE.md sentence must be corrected once he rules. |
| ⚠️ The Long Shade (14°) becomes low-sun | Our gloss *"overhead sun here, so parasols and tents work"* (not his words) | Parasols drop to 0.35 and tents to 0.3; a shield you stand behind works fully. That changes the Long Carry play (D2). |
| ⚠️ One Z for the whole planet; the Stillsand floor goes | Card 2026-09-30 18:11 PDT: *"+55 °C at the substellar point, scaled by sun angle, about 35 °C in the far ring"* | With Z = 55 the zenith value holds. The far-ring 35 floor is dropped, so the Stillsand's low edge falls to about 55 × sin E (D1). |
| ⚠️ Greentide ambient becomes a temperature condition, or is deleted | Card 2026-10-08 (`WETBULB_FOLD_INTO_HEAT_1`), 12 °C | Kept as a +12 °C air temperature, or lost under option D3-b. |
| Forge, Scald, Fever Wood and Greentide now get Direct Sun | 2026-09-29: *"there shade won't help you (in steam)"* | Shade helps against **the sun part** there and never against the air heat. I read this as consistent with his words; he should confirm (D3). |

## 4. Migration list

**C#: `src/RimMandrake/CreatureBehaviors/Source/`**
- `RM_SunHeatExtension.cs`: delete `heatKind`, `heatOffsetC`, `maxHeatOffsetC`,
  `heatScalesWithElevation`, `minScaledHeatOffsetC`, `overheadAboveElevationDegrees`,
  `min/maxElevationDegrees` and `substellarLatitude/Longitude`. Keep glare, mirage and shade-hop
  tuning, and the body-size terms (or move them to planet constants).
- `RM_SunHeatMath.cs`: replace `RM_HeatKind` with `RM_SunCover { overhead, lowSun }` and drop
  `ambient`. Replace `KindFromElevation` with `CoverFor(E, T)`. `ElevationHeatOffset(Z, E)` loses
  its floor. Add a `Daylight` factor.
- `RM_MapComponent_ShadeGrid.cs`: `EffectiveHeatKind` becomes `CoverRegime`, and
  `EffectiveHeatOffsetC` uses Z. `ResolveSun` uses the one clamp. Delete the ambient branches (lines
  ~193, 551, 558, 755, 865, 874, 885, 918). `ExposureFor` multiplies by daylight.
- `RM_SunHeatPatches.cs`: no change in shape.
- `RM_ShadeGear.cs`, `RM_Gizmo_SunLoad.cs`, `RM_ShadeHop.cs`: drop ambient.
- `RM_WeatherSenseExtension.cs`: unchanged; it gets used more.
- `RM_CreatureBehaviorsMod.cs`: settings (§5).
- `src/RimMandrake/SolarMirrors/Source/RM_MirrorPatches.cs`: drop the ambient gate.
- New: no new class. The ambient source uses vanilla `GameCondition_TemperatureOffset` through
  each biome's existing permanent-condition bootstrap. The Sump and Miasma lock conditions already
  use this pattern.

**XML, per biome.** Each `<li>` loses its heat fields and keeps the marker. Guards are unified on
`mandrake.rm.creaturebehaviors`.
- Long Shade: drop `heatKind` and `heatOffsetC`. Keep the pinned sky.
- Stillsand: drop kind, offset, scaling, floor, threshold and cap. Keep glare, glare-blind and
  mirage.
- Cracked Lands, Weeping Stones, Pyrelands, Webwork, Rust Cathedral, Contagion: drop all heat
  fields. Add the guard to the Rust Cathedral and the Webwork. The Contagion's Bloom 0.2 stays.
- Forge, Scald: drop `heatKind ambient` and `heatOffsetC 15`. Add a `GameConditionDef`
  (`RM_ForgeAirHeat`, `RM_ScaldAirHeat`) with `temperatureOffset`, value per D3.
- Fever Wood, Greentide: the same (`RM_FeverWoodAirHeat`, `RM_GreentideAirHeat`).
- **New opt-ins**, each needing the owner's yes (D6): Scarlands `RM_Warscar` and Miasma
  `RM_Miasma` get the marker.
- `RUT_` twins: add the marker by patch in `src/RimUtinni/UtinniPatches/Patches/`, guarded with
  `PatchOperationFindMod`, because `MayRequire` on a top-level Operation is ignored.
- `src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml`: drop the ambient
  column from the header table.
- New patch: `sunExposureFactor` on vanilla overcast weathers (DS5).

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

**Docs.**
- CLAUDE.md §"One kind of heat": fix the KIND sentence.
- `SOLAR_HEAT_EXPOSURE_1` spec §2.
- `CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID`: superseded; close it into this item.
- The ⇒ paraphrase in `longshade_shade_ideation_2026-09-29.md`: delete it, per the "remove
  inaccurate material" rule.

## 5. Mod Settings (Creature Behaviors)

Defaults equal the shipped behaviour. With everything off, the game is plain vanilla temperature.

- **Direct Sun** master switch (exists as `sunHeatEnabled`), plus the **strength** dial
  (`sunHeatStrength`, exists).
- **Sun heat at the zenith (°C)** slider: Z. New.
- **Low-sun rules below (°)** slider: T. The existing `kindFromElevationEnabled` toggle becomes
  "cover follows the sun". Off means every map uses overhead rules.
- **Weather dims the sun** toggle. New.
- **Sun heat only while the sun is up** toggle (DS6). New.
- Existing toggles stay: directional shade, sun pathing, sun-load bar, sand glare, glare-blind,
  mirage.
- **Air heat** (the ambient conditions) lives in **each biome mod's own settings**: an on/off and
  a °C slider for the Forge, Scald, Fever Wood and Greentide. It no longer switches off with the
  sun setting. Each label says it affects the map's temperature, so plants feel it too.

No new cross-biome switch is built (owner, 2026-10-15).

## 6. Test plan

**Offline first.** `python3 src/RimMandrake/Utils/selftest_sun_heat.py` and the per-mod selftests.
- **Equality across biomes.** Load every BiomeDef carrying the marker, and for E ∈ {5, 14, 21, 31,
  45, 56, 79, 85} assert that offset and cover regime are identical whatever the biome.
- **Lint.** No BiomeDef or patch under `src/` may carry `heatKind`, `heatOffsetC`,
  `heatScalesWithElevation`, `minScaledHeatOffsetC` or `overheadAboveElevationDegrees`. The check
  parses XML elements; it does not grep.
- **Regime switch at T:** roof counts at E = 56 and not at 54; a lee counts at both.
- **Ambient leaves the sun pipeline:** a Forge pawn's sun offset comes only from the sun term, and
  the air-heat condition's `temperatureOffset` reads from XML.
- Weather factor and daylight multiply sun heat only.
- Long Shade at 14° uses the low-sun gear factors.
- The fuzz run mutates Z, T and E and checks the pipeline holds.

**L1 (quicktest map and bridge, state reads only, no visuals).** Use three maps: the Long Shade,
the Pyrelands and the Forge. On each, read `SunOffsetFor` and `ExposureFor` for one pawn in the
open, under a roof and in a lee. The same E must give the same numbers. On the Forge, read
outdoor `map.mapTemperature` with the air-heat condition on and off. The difference must equal the
offset.

**L2 (owner-watched sitting).** He tunes Z, T, the weather factors and the four air-heat offsets
by watching a colonist heat up. This fills the existing sitting criterion in
`SOLAR_HEAT_EXPOSURE_1`.

## 7. Recommendation and the decisions only he can make

**Recommendation.** Ship Direct Sun as DS1–DS7 on every sun-heat biome, with ambient as a vanilla
air-temperature condition (D3-a), the daylight gate (D4-a) and Z = 55 (D1-a). Then fix CLAUDE.md
and close the Contagion item into this one.

- **D1. How hot is the sun?**
  - a) 55 °C at the zenith everywhere: his Stillsand number. Pyrelands, Webwork and Rust Cathedral
    get much hotter.
  - b) A milder single number, about 25 °C. Long Shade and Stillsand get gentler.
  - c) a) but keep a far-ring floor. Every low-sun tile gets that floor, which makes the angle
    matter less.
- **D2. The Long Shade becomes low-sun.**
  - a) Yes. Shields and lees work; parasols mostly don't. This matches its long shadows.
  - b) Keep parasols working there. That reintroduces a per-biome exception, which is a "kind".
- **D3. Volcanic, steam and hot-fog heat.**
  - a) Keep it as hotter air on the thermometer. Plants feel it too; the Greentide's 12 °C card
    survives.
  - b) Delete it. Four biomes become as hot as their tiles only, and the wet-bulb card is undone.
- **D4. The sun at night on biomes without a pinned sky.**
  - a) No sun heat at night (code only).
  - b) Pin the sky on every dayside biome: no night on the dayside, which is a cosmetic change.
- **D5. Sand glare.**
  - a) Stillsand only.
  - b) Any natural sand under the sun, which includes the Long Shade.
- **D6. Add sun heat to the Scarlands and the Miasma**, both hot with none today: yes or no.
