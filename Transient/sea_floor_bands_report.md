# SEA_FLOOR_SINGLE_BAND_1 — Grey Sea / Twilight Sea / the Chill shallow-band pass

Status: DONE offline (XML-only, no bridge) — see headline finding below
before treating this as closing the crowncarpet-class defect for real
gameplay.

## Scope
Follow-on to `ca774b8b9` (SCALD_CROWNCARPET_NO_HABITAT_1), which split
`RM_TheScald.xml`'s single-band `terrainsByFertility` into deep/shallow.
`Transient/scald_shallow_band_report.md` flagged the identical single-band
pattern on GreySea/TwilightSea/PropaneLake(the Chill). This pass applies the
equivalent split to those three, checks each sea's flora/fauna for habitat
tags the split needs to actually serve, and re-checks
PROPANELAKE_ANIMALDENSITY_ZERO_1.

## 🔴 Headline finding — read this before trusting any of the census numbers below

**`terrainsByFertility` is DEAD CODE for the actual gravship-dive floor a
player experiences on ALL FOUR terminal seas, including tonight's Scald
fix.** Read directly from source, not inferred:

`src/RimMandrake/DivingInteraction/Defs/MapGeneration/RM_SeaDiveGenerators.xml`
lists each sea's `MapGeneratorDef.genSteps` — every one carries
`RM_SeaFloorTerrain` and **none carries vanilla `Terrain`** (the step that
reads `terrainsByFertility` at all). `RM_SeaFloorTerrain`'s own C#
(`src/RimMandrake/DivingInteraction/Source/GenStep_SeaFloorTerrain.cs`) is:

```csharp
TerrainDef floor = RM_ChillFireGate.IsChillSeabedMap(map)
    ? DefDatabase<TerrainDef>.GetNamed("RM_ChillIceBedrock")
    : DefDatabase<TerrainDef>.GetNamed("RM_SeaFloorGround");
foreach (IntVec3 cell in map.AllCells)
    map.terrainGrid.SetTerrain(cell, floor);
```

One constant `TerrainDef` per whole map, painted onto every cell
unconditionally. No fertility read, no per-cell branch. The class's own
header comment says outright: *"The vanilla `Terrain` GenStepDef paints from
the biome's own terrainsByFertility... This GenStep replaces it outright
(omitted from every RM_SeaDiveGenerator_*)."* `RM_SeaFloorGround` (the
terrain painted for Scald/GreySea/TwilightSea) carries only the tag
`RM_SeaFloorGround` — never `RM_CrowncarpetBed`, `RM_TheChillBed`,
`RM_TheChillShelf`, or any sea's shallow-habitat tag.

⇒ **`ca774b8b9`'s Scald fix does not put any `RUT_ScaldWaterOceanShallow`
cell — and therefore no `RM_CrowncarpetBed` habitat — onto the real dive
floor a player reaches through `RM_SeaDiveHatch`.** The 49,940-deep/0-shallow
census that item measured must have come from a generation path OTHER than
`RM_SeaDiveGenerator_TheScald` (most likely a bridge/quicktest tool that
force-generates a normal map on a world tile via the vanilla
`MapGeneratorDef`, which these impassable/`isBackgroundBiome` seas can never
reach in real play — ship-only, per CLAUDE.md's sea rulings). That census is
real evidence about *that* generation path, not about the one the game
actually uses for a dive.

**This pass still applies the requested `terrainsByFertility` split to
GreySea/TwilightSea/the Chill**, matching the Scald precedent exactly
(structurally correct, harmless, and it IS what any non-dive generation of
these biomes — a debug/quicktest map, or a future fixed `GenStep_SeaFloorTerrain`
that starts reading it — would use). It also fixes a second, independent
defect on the Chill (missing habitat tags — see below) that the band split
alone would not have unblocked even on the path that does read fertility.
**But none of this — the Scald fix included — currently changes what a
player sees or can grow when they actually dive.** The real fix is a
`GenStep_SeaFloorTerrain` change (or a per-sea floor-dressing GenStep, the
shape GreySea already has for its channel/apron terrain) that paints a real
minority-share shallow/habitat terrain onto the dive floor instead of one
constant per map. That is C# + DLL rebuild + live verification — out of this
item's offline, bridge-free scope — and is the follow-up this report is
flagging, not closing.

## Grey Sea

`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml` had the
single band `WaterOceanDeep -999..999` (plain vanilla, not even this mod's
own terrain). Split into `RM_WaterBrineDeep` (<0.6) /
`RM_WaterBrineShallow` (>=0.6) —
`src/RimMandrake/FlowWorks/Defs/LiquidTypes/TerrainDefs/RM_WaterBrine.xml`,
already this BiomeDef's own designated water pair (its
`RM_SeaShoreExtension` modExtension's `deepTerrain`/`shallowTerrain` fields
point at the same two defs) and a HARD `modDependency` of
`mandrake.rm.terminalbiomes`'s own About.xml (`TERMINALBIOMES_LIQUID_RETARGET_1`
comment there), so the `MayRequire` on the field is defensive, not a real
optionality risk.

**Habitat check**: ten flora rows (`RM_GreySeaFlora.xml`'s 7 crystal forms +
`RM_GreySeaUnderstorey.xml`'s 10-species understorey, 17 total minus overlap)
— only two carry `wildTerrainTags` at all (`RM_GlassVeilKelp`/
`RM_SaltChimneyVine`/`RM_Brinecomb`, tags `RM_GreyBrineChannel`/
`RM_GreyChimneySeep`), and those are painted by a SEPARATE, already-built
GenStep (`GenStep_GreySeaFloorDressing.cs`, confirmed live in source —
`RM_GreySeaTerrains.xml`'s own "NOT PAINTED YET" comment on those two tags is
now stale, out of this item's scope to fix). None of the rest is gated on
deep/shallow at all. **So this split unblocks no currently-blocked Grey Sea
roster row** — it corrects the structural single-band defect and gives the
sea a real brine deep/shallow split for whatever path reads it.

## Twilight Sea

`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml` had the
identical single band, also plain vanilla `WaterOceanDeep`. **This sea has
no bespoke deep/shallow TerrainDef pair anywhere under `src/`** — its
`RM_SeaShoreExtension` modExtension is a bare, field-less
`<li Class="..." />` (no `deepTerrain`/`shallowTerrain`/`beachTerrain` set
at all), and no `RM_TwilightSea*Terrains.xml` file exists. Per this item's
own instruction to report rather than borrow, split into plain vanilla
`WaterOceanDeep` (<0.6) / `WaterOceanShallow` (>=0.6) — confirmed real
vanilla TerrainDefs via RimSage (`search_defs query=WaterOcean
defType=TerrainDef`) — rather than reaching for the Grey Sea's brine or the
Chill's propane, neither of which is this sea's own.

**Habitat check**: all three `wildPlants` rows
(`RM_SaltBladeTwilight`/`RM_HoolimbrePlant`/`RM_NoothelmPlant`,
`RM_TwilightSeaFlora.xml`) carry **zero** `wildTerrainTags` — confirmed by
direct grep (0 hits). So this split unblocks nothing here either; same as
the Grey Sea, it is a structural correction only, and it is honest about
having no sea-specific shallow terrain to offer.

## The Chill (RM_TheChill, formerly PropaneLake)

`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheChill.xml` had the
single band `RM_TheChillDeep -999..999`. Split into `RM_TheChillDeep`
(<0.6) / `RM_SolidPropane` (>=0.6) — both already this def's own
`waterDeepTerrain`/`waterShallowTerrain`
(`src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RM_TheChillTerrains.xml`,
RimMandrake-authored, no donor dependency).

**Habitat check found a second, independent defect.** All ten
`RM_TheChillFlora.xml` plants use `wildTerrainTags` (5 `RM_TheChillShelf`:
Slackwax/Ghostpane/Keelgrass/Skyharp/Pitchpearl; 6 `RM_TheChillBed`:
Eldspar/Tarspool/Stonewater/Fuselight/ChillStillbloom/Pitchpearl — Pitchpearl
carries both) per the file's own header convention. **Neither tag existed on
`RM_TheChillDeep`/`RM_SolidPropane` before this pass** — they existed only
on FlowWorks' `RM_PropaneDeep`/`RM_PropaneShallow`
(`src/RimMandrake/FlowWorks/Defs/LiquidTypes/TerrainDefs/RM_Propane.xml`,
manually patched in under `CHILL_FLORA_BUILD_1`'s own comment, which
explicitly names those two defs — the shore-edge `<coastal>` pair, not the
biome's own `waterDeepTerrain`/`waterShallowTerrain`). So **all ten Chill
flora species had nowhere to grow at all**, independent of the single-band
defect: even with two fertility bands, neither resulting terrain carried the
tag their `wildTerrainTags` needs. Added `RM_TheChillBed` to
`RM_TheChillDeep` and `RM_TheChillShelf` to `RM_SolidPropane`
(`RM_TheChillTerrains.xml`, this commit) — now every one of the ten species
has a real match. **This is the one roster this pass genuinely unblocks**
(on whichever generation path reads `terrainsByFertility` — see headline
finding for why that is not the real dive floor today).

`PROPANELAKE_ANIMALDENSITY_ZERO_1` was already fixed before this pass
(`animalDensity>0.08</animalDensity>` on `RM_TheChill.xml`, dated
2026-09-26 in its own comment) — re-checked, confirmed still set, nothing to
do.

## PROPANELAKE_ANIMALDENSITY_ZERO_1 re-check

Covered above under the Chill — already fixed, re-confirmed, no action
needed this pass.

## RUT_ twins

`RUT_GreySea.xml`, `RUT_TwilightSea.xml` and `RUT_PropaneLake.xml`
(`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/`) each carry the identical
header the Scald's own twin did: **"🔴 FROZEN 2026-09-25 — carrying the
world until the terminal paint; content lives in `mandrake.rm.terminalbiomes`;
do not edit here."** Confirmed by direct grep, all three. None touched, same
as `RUT_TheScald.xml` in `ca774b8b9`.

## Verify

- XML parse (`xml.etree.ElementTree.parse`) on all four edited files
  (`RM_GreySea.xml`, `RM_TwilightSea.xml`, `RM_TheChill.xml`,
  `RM_TheChillTerrains.xml`) — OK.
- `python3 src/RimMandrake/Utils/run_selftests.py` — **77/79 passed**, same
  as the Scald pass: 2 skipped (human-driven art check; lupa-dependent
  package test), 1 UNMEASURED (`selftest_tool_metadata.py`, needs the
  Windows-side .NET SDK; irrelevant, no C#/DLL touched here), 1 FAILED
  (`selftest_deployed_biome_refs.py`, re-run standalone: **19** dangling
  deployed refs, all `RUT_TheRot`/`RUT_WeepingStones`/`RUT_Contagion`/
  `RUT_TheForge` rows needing `mandrake.rut.rotsporekit` — zero mention of
  GreySea/TwilightSea/Chill/PropaneLake/Scald/Crowncarpet anywhere in its
  output; pre-existing and unrelated to this change, exactly as the Scald
  pass found).
- No C# touched, no DLL/`.srchash` to rebuild — all four edits are BiomeDef/
  TerrainDef field edits only.
- No bridge/game touched — this worktree is offline per the brief.
