# LANTERN_DEEPS_INJECTION_1 — the crystal caverns as an injected underground layer

Owner ruling 2026-09-06 (`the_lantern_deeps.md`): `BMT_CrystalCaverns` is NOT a worldmap
biome; it is an injected cave-map layer beneath any nightside map with biome temperature
≤ −40 °C, with two entrance types.

## spec
1. **Quicktest first** (rimworld-debug-testing): confirm what `BMT_CrystalCaverns`
   generates when reached — the mod defines it `isCavern true` (enclosed, stable
   overhead mountain roof, `Calm` weather, incidents disabled) and ships NO entrance def
   in XML; find the transition mechanism in its DLL / Odyssey's layer system. Report
   MEASURED.
   ⭐ **MEASURED 2026-09-07** (static file research, `2969748433` "Biomes! Caverns",
   `.../1.6/Defs/Biomes/BMT_CrystalCaverns.xml`): confirmed `isCavern true`,
   `baseWeatherCommonalities` 100% `BMT_Calm`, and a partial `disabledIncidents` list
   (not a global disable flag). **No entrance mechanism exists in this mod at all** —
   it is an ordinary top-level world-map biome, placed by its `workerClass
   GeologicalLandforms.ConfigurableBiomeWorker` scoring `depthInCaveSystem` (min 2-3,
   i.e. deep into a chained cave-tile network) AND **temperature between −15 and 5 °C**
   — not our ≤ −40 °C nightside gate. The active mod list also carries
   `m00nl1ght.geologicallandforms.biometransitions`, which is Geological Landforms'
   generic biome-border map-blending feature (smooth transition maps between ANY two
   adjacent biome tiles) — unrelated to cave entrances specifically.
   ⇒ **Consequence for spec item 3 below**: we cannot let `BMT_CrystalCaverns` be
   auto-placed by Geological Landforms' own worldtile scoring — that would make it a
   visible, ordinarily-reachable worldmap tile, violating the owner's "NOT a worldmap
   biome" ruling, and its native temp gate (−15..5 °C) doesn't even match our ≤ −40 °C
   host requirement. The build must (a) prevent `BMT_CrystalCaverns` from entering
   ordinary biome-worker placement (strip/override its `workerClass`, or simply never
   let it worldgen-place and only ever spawn it as a generated pocket map's biome), and
   (b) reach it exclusively through our own authored entrance features (item 2) wired
   to Odyssey's pocket-map/layer system (`PocketMapParent`-style), reusing only the
   BiomeDef's generation properties (isCavern, weather, incidents) — never its own
   worker/placement path. This is now a concrete design decision, not open research;
   next step is the Odyssey `PocketMapParent` API itself.
   ⭐ **BUILT 2026-09-07**: `src/RimUtinni/LanternDeeps/` ships `RUT_LanternDeepGenerator`
   (MapGeneratorDef, pocket map biome=`BMT_CrystalCaverns`), `RUT_LanternDeepEmergence`
   (natural-emergence portal ThingDef, `thingClass MapPortal`, `CompProperties_Sealable`
   collapse hazard, placeholder art), `RUT_LanternDeepEmergence_Scatter`
   (`GenStep_ScatterCavePortal`, new C#, self-gates to `BiomeGRimond`/`RUT_NightsideIce`/
   `RUT_PropaneLake` at an 8%-per-map placeholder rarity), added globally onto
   `MapCommonBase` via patch. Builds clean, `validate_patch.py` passes 0 errors against
   both the frozen official dump and the live 599-mod set. **Ruined-mineshaft entrance
   (item spec 2b) NOT built yet** — deferred, needs KCSG/scene-composition authoring.
   ⚠️ **Quicktest attempt 2026-09-07 crashed the game**: added
   `m00nl1ght.GeologicalLandforms` + `BiomesTeam.BiomesCaverns` + `mandrake.rut.lanterndeeps`
   to the 25-mod minimal list but forgot Biomes! Caverns' own hard dependency
   **`BiomesTeam.BiomesCore`** — its absence broke `BiomesCore.DefModExtensions.*` type
   resolution (`Song_MapRestrictions` etc.), which cascaded into a NullReferenceException
   in `RecipeDefGenerator.SetIngredients` during implied-def generation and triggered
   RimWorld's own recovery-reset (mod list wiped to Core+expansions). No save/world data
   lost — only the live `ModsConfig.xml` was affected, since restored by `modlist_swap.py`.
   **Next bridge session**: add `BiomesTeam.BiomesCore` to the mod list alongside the
   other two before relaunching, then retry the quicktest.
2. **Entrances as map-transition features** (caverns sitting: same category as
   DeepRim/Z-Levels shafts): (a) **natural emergence** — lanternstone breaking the
   surface, lit from below; (b) **old mineshaft inside a ruined mining facility** —
   well-provisioned high-tech ruin (Rakatan kyber mine or later expedition), corpses in
   excellent gear. Scene-composition skill applies to both.
3. **Injection rule**: host biome temp ≤ −40 °C only (Blue Desert, ice sheet, propane
   margins); density and kyber richness per host; persistent layers (no regeneration).
4. **Roster**: evict the crystal-studded animals; keep non-crystal cave fauna for the
   sitting; the crystal-life cast (Lantern, Creep, Cleavers, Chorus, Shard-minds,
   mindstone) is authored content — art + C# scoped separately.
5. **Kyber**: the lightsaber mod's `KOTOR_*Crystal` formations + `guy762_focuscrystal_BiomeCrystal`
   as the mineables; crafting-only (Force v2).
6. Darkness mechanic + collapse hazard wired per the caverns sitting.

## verify
A quicktest reaches a Deep through each entrance type; the cave map is enclosed and
dark; kyber formations spawn; the same Deep persists across two visits.
