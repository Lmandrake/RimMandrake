# CRACKEDLANDS_FLORA_EXPANSION_BUILD_1 — Build 6 admitted Cracked Lands flora

From `BEDAZZLE_FLORA_EXPANSION_1`. Admitted by question card 2026-10-02, all six, Zennaq with the
full C# lightning-targeting version. Look/behaviour source:
`design/Jawa/worldbuilding/biomes/cracked_lands_flora_expansion_pitch_2026-10-02.md` §1-6.

## spec

Mod: `src/RimMandrake/FloodedCanyon/` (packageId `mandrake.rm.floodedcanyon`; BiomeDef
`RM_FloodedCanyon`, labelled "the Cracked Lands"). ALL defNames **`RM_`** (matches `RM_Veqma` in
`Defs/ThingDefs_Plants/RM_Veqma.xml`). New plants in a new
`Defs/ThingDefs_Plants/RM_CrackedLandsFlora.xml`; items in `Defs/ThingDefs_Items/`. No green on any
plant (only Veqma shows green); no columns/cacti/Earth trees.

1. **`RM_Nabbuq`** — FOOD. Indigo-violet fist bladders under lavender bracts; grows on shade-line soil,
   swells after floods. Harvest -> new **`RM_NabbuqBladder`** (RawVegetable, moderate stack).
   Sowable (`sowTags`, `fertilityMin`). Shade-line gating: reuse whatever Veqma uses (open question 3 on
   `CRACKEDLANDS_THREE_HEIGHT_FLORA_1`).
2. **`RM_Ruqqal`** — MATERIAL (textile). Coral-salmon twisted stalks, mud-striped. Harvest -> new
   **`RM_RuqqalFibre`** (Fabric stuff, Devilstrand-cloth model, coarse, moderate insulation, coral
   tint). Start with plain shade-band commonality; channel-terrain pinning is optional (M).
3. **`RM_Sevvuq`** — MATERIAL (dye). Saffron-sulfur brain-globes at the flood high-water line.
   `harvestedThingDef` = vanilla `Dye` (no new item). Favour high-water band via
   `RM_MapComponent_RecedeAftermath` wetted-cell hint, or plain shade-band commonality.
4. **`RM_Zennaq`** — HAZARD (copper broom). Verdigris-copper/silver wire filaments; high
   `Flammability`; mesa-top/bench edges. Cut -> new **`RM_ZennaqFilament`** (small conductive item) or
   a few Steel/Silver. **C# (full version, admitted):** Harmony postfix on the lightning target choice
   (`WeatherEvent_LightningStrike`) biasing the strike toward a Zennaq within range. 🔴 RimSage MUST
   confirm the exact method/signature first; do not guess. Gate on a setting. Any comp on the plant
   uses `CompTickLong`, never `CompTick`.
5. **`RM_Luqqim`** — BEAUTY (lantern cup). Magenta-amethyst tulip cups, cyan rim; deepest slot
   shade. `Beauty` statBase + `CompGlower` (magenta `glowColor`, Glowstool/cave-plant pattern, low-glow
   growth). Cut -> small plant matter.
6. **`RM_Harrovaq`** — MATERIAL (wood; the biome's own tree). Slate-blue bark, bone-white corkscrew
   branches, burgundy tassels. Vanilla tree PlantDef (`harvestTag Wood`, `harvestedThingDef WoodLog`,
   low yield, `blockAdjacentSow`); rare, roots in floor soil beside walls (NOT wall face — talus clasps
   own that).

Roster — IMPORTANT TWO-PLACE EDIT: the live `RM_FloodedCanyon_Biome.xml` `<wildPlants>` holds only
`RM_Veqma` 0.15, BUT `src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml` **Op 3
replaces that whole list** (donor grass/moss/thorns + Veqma). Rows added only to the BiomeDef are
silently wiped when the campaign layer loads. Add the six rows (shorthand
`<DefName>commonality</DefName>`) to BOTH the BiomeDef and Op 3's `<value>`. Suggested: Nabbuq 0.25,
Ruqqal 0.3, Sevvuq 0.2, Zennaq 0.1, Luqqim 0.1, Harrovaq 0.06; calibrate in test.

Mod Settings: add `floraExpansionEnabled` (default true) and `zennaqLightningPullEnabled` (default
true) to `RM_FloodedCanyonSettings` in `Source/RM_FloodedCanyonMod.cs`; all-off leaves Veqma + the
patch's original roster.

Art: `infrastructure/artpipe/art_lists/crackedlands_flora_expansion_2026-10-02.csv`; item icons owed
after defs exist.

## criteria

Script checks in `src/RimMandrake/FloodedCanyon/validation.py` (state reads, no screenshots):
- 6 plant defs + `RM_NabbuqBladder`, `RM_RuqqalFibre`, `RM_ZennaqFilament` resolve via `get_defs`
  (`success`/`foundCount`/`notFound`).
- Live `RM_FloodedCanyon` wildPlants (post-patch, i.e. under the Utinni layer too) contains all six
  rows; control: `RM_Veqma` still present.
- No new plant has green-dominant texture mean (artpipe validator) — art only, not script-judged.
- Sevvuq harvest yields vanilla `Dye`; Harrovaq yields `WoodLog`; Nabbuq yields `RM_NabbuqBladder`.
- Luqqim has `CompGlower` with magenta colour; `Beauty` > 0.
- Zennaq: spawn a Zennaq and a control Plant within range, trigger lightning target choice N times
  (deterministic seed / call the patched chooser directly) -> Zennaq hit-rate > control; setting off ->
  no bias. Read the chooser's returned cell; no flight/visual hunt.
- Plant comps use `CompTickLong` (grep the comp class, assert no `CompTick` override).
