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
   ⭐ **BUILT 2026-09-09** (offline pass, bridge unavailable — game mid-reboot, third
   restart of the night per another agent's save-compatibility fix; no live
   confirmation attempted this pass): `RUT_LanternDeepEvictCrystalFauna.xml`
   (`PatchOperationFindMod` on "Biomes! Caverns") removes the six crystal-tagged
   `wildAnimals` entries from `BMT_CrystalCaverns` — `BMT_CrystalBeetleLarvae`,
   `BMT_CrystalBeetle`, `BMT_Crystalope`, `BMT_CrystalFairyMole`, `BMT_CrystalCrab`,
   `BMT_CrystalMantis` — plus `BMT_CrystalCrab`'s `allowedPackAnimals` entry, per the
   frozen sheet's HARD BAN #3 (owner: "a bit hokey... I'd rather have crystals AS
   creatures"). "The rat" needed no patch: the donor's own file already ships its
   `Rat` line inside an XML comment (`<!-- <Rat>1.3</Rat> -->`, line 271), so vanilla
   `Rat` is already absent from this biome's spawn table — confirmed by direct read of
   `.../2969748433/1.6/Defs/Biomes/BMT_CrystalCaverns.xml`. All 7 xpaths confirmed to
   match exactly 1 node each by direct `lxml` query against that file (the repo
   validator's `--defs` mode reads the CURRENT 6-mod reboot `ModsConfig.xml` as its
   load set, which doesn't include Biomes! Caverns right now, so it false-positives
   "0 matches" — not a defect in the patch); `validate_patch.py --live` against both
   the frozen `OFFICIAL-2026-08-29` dump and the live `2026-09-09T01-54-07Z` capture
   passes 0 errors. **Spec item 4 (crystal-studded eviction half) is done.** The other
   half — "non-crystal cave fauna... judged at the assignment sitting" — is
   explicitly deferred to that sitting, not invented here.
   ⭐ **VERIFIED 2026-09-09 — spec item 5 (kyber formations) already satisfied, no
   build needed**: `RUT_LanternDeepGenerator`'s own `genSteps` list already includes
   `BMT_CrystalsGenerator` (line 22 of the generator def, present since the
   2026-09-07 build). That GenStepDef is patched by our own already-shipped
   `src/RimStarWars/Armoury/Patches/Absorbed_AdditionalMods/kotorweapons/BiomesCaverns/
   Absorbed_Kotorweapons_BiomesCaverns_Patch_KotORCrystalFormationInjector.xml`
   (absorbed from `guy762.KotORWeapons`, `WEAPONS_DONOR_RETIREMENT_1`) to scatter all
   7 `KOTOR_SmallCrystal_*` colors + 3 `KOTOR_MediumCrystal_*` + `KOTOR_StygiumCrystal`
   + 2 `KOTOR_LargeCrystal_*` mineable formations into every map that runs
   `BMT_CrystalsGenerator` — which every Lantern Deep pocket map does, by inheritance,
   with zero extra work. Cross-checked against `design/Jawa/mods/crystal_mods_inventory.md`
   (BENCH research, 2026-09-08), which independently confirms this wiring and also
   confirms the spec's other named source — `guy762_focuscrystal_BiomeCrystal` — **does
   not exist under that defName in the current 596-mod dump** (measured 0, full
   coverage); the spec's citation is imprecise, not a build gap. The lightsaber mod's
   *actual* kyber (`Force_CrystalFormation_*` → `Force_KyberCrystal`, `lee.theforce.
   lightsaber`) is NOT yet gated to Lantern Deeps maps specifically — that unification
   is `CRYSTAL_MODS_INGEST_1`'s scope, a separate, larger, already-filed item; not
   duplicated here.
   ⚠️ **Still owed, NOT built this pass (offline-buildable-but-large, or
   quicktest-dependent — see reasoning below)**:
   - **Spec item 2b, the ruined-mineshaft entrance.** This needs a KCSG
     `StructureLayoutDef` (the `VaultDungeons` sibling mod's pattern —
     `src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/` — is the template to
     follow: a generator script writing a large hand-scaled grid, `SymbolDef`
     wrappers for any third-party thing/pawn used bare in a cell, a `GenStepDef`
     wiring it in). That same sibling mod's own history records a live-quicktest
     crash from an unwrapped mechanoid pawn symbol (null-faction NRE) that only
     surfaced in play — i.e. `rimworld-scene-composition`'s own process (`SKILL.md`
     §7: "build offline first... prove it live on a quicktest") assumes a quicktest
     loop is available to catch exactly this class of defect. With the bridge down
     this pass, authoring a full structure blind risks shipping the same kind of
     silent defect with no way to catch it before the next real load. Left owed
     rather than guessed.
   - **Spec item 1's live quicktest itself is still not run.** The 2026-09-07 attempt
     crashed (missing `BiomesTeam.BiomesCore` hard dependency); the fix (add it to the
     mod list) is recorded but was never retried. The design conclusion it was meant
     to confirm was reached anyway via static file research (measured 2026-09-07,
     above) and the build proceeded on that basis — but end-to-end proof that a
     player can actually walk into a natural-emergence portal and reach a working
     Deep has never been observed live.
   - **Spec item 6, the darkness mechanic** (beyond the collapse hazard already on
     `RUT_LanternDeepEmergence`'s `CompProperties_Sealable`) — "wired per the caverns
     sitting" points at `underground_caverns_deep_design.md`'s own darkness-as-mechanic
     ruling, which is a real gameplay system (not just cave-map ambient dark, which
     `isCavern`/enclosed roofing already gives for free) and needs its own C#/design
     pass, not something to invent here without re-reading that spec in full.

⭐ **BUILT 2026-09-12** (offline pass, bridge held by another FOUNDRY window for an
unrelated GIZKA hook test — not stale, not taken; built and deployed to completion
without a live quicktest, per this pass's own instruction to document what's owed
rather than force the bridge):

- **Spec item 2b, the ruined-mineshaft entrance — BUILT.** `RUT_LanternDeepMineshaft`
  (new ThingDef, `thingClass MapPortal`, same shape as `RUT_LanternDeepEmergence`:
  `CompProperties_Sealable` + `CompProperties_LeaveFilthOnDestroyed`, portal wired to
  the same `RUT_LanternDeepGenerator`). PLACEHOLDER ART reuses vanilla `PitGate`'s
  texture (a large ground-set hole reads as "collapsed shaft," distinct from the
  emergence's crystal-geode look) — real art still owed, same as the emergence.
  New `GenStep_ScatterMineshaftPortal.cs` (self-gated to the same three host biomes
  as the emergence, its own 4%-per-map placeholder rate and its own Mod Settings
  toggle) scatters it and then dresses the site per the spec's "well-provisioned
  high-tech ruin... corpses in excellent gear": one `AncientSoldier` pawn generated
  and killed in place (the same `PawnGenerator.GeneratePawn` + `GenSpawn.Spawn`
  pattern vanilla's own `UndercaveMapComponent` uses for its fleshbeast corpses —
  deliberately NOT the KCSG-symbol pawn path that crashed the sibling
  `StructureInjectionsRUT` mod's mechanoid symbol, a different code path this never
  touches) plus a handful of `Filth_RubbleRock` patches. `RUT_LanternDeepMineshaft_
  MapGenPatch.xml` adds the new GenStep to `MapCommonBase`, same mechanism as the
  emergence's own patch.
  ⚠️ **ASSUMPTION recorded, not guessed silently**: the task brief's "near existing
  mine/ruin sites rather than random biome scatter" is NOT implemented — ruin/mine
  placement is a world-layer (WorldObjects/Sites) concept with no clean hook from a
  GenStepDef at map-gen time, and building one is a larger world-authoring feature
  than this pass's budget. Left as ordinary qualifying-biome scatter at a lower rate
  than the emergence; a real site-linked placement rule is owed at the caverns
  sitting, same as the emergence's own density number.

- **Spec item 6, the darkness mechanic — BUILT** (the shared "ambient light level"
  signal `underground_caverns_deep_design.md` §8 calls for, ruled v1 by the owner's
  2026-09-02 sitting). New `MapComponent_LanternDeepDarkness.cs`, registered via
  `RUT_LanternDeepGenerator.xml`'s `customMapComponents` (confirmed via
  `Verse.Map.FillComponents`: a `CustomMapComponent` subclass is added ONLY to a map
  whose `MapGeneratorDef` lists it — never auto-added to every map, unlike a plain
  `MapComponent`). Every 250 ticks it samples `GlowGrid.GroundGlowAt` at each
  colonist's position on the Deep map; sustained bright light accumulates an
  "exposure" value (darkness lets it decay), and once exposure crosses a threshold
  (its own Mod Settings multiplier) a `BMT_CaveSpider` — an already-resident
  non-crystal predator, NOT a new creature; the crystal-studded roster stays evicted
  per HARD BAN #3 and the rest of the cast is still "the sitting"'s call — is
  generated near the brightest colonist and set to `Manhunter`. This is scoped
  deliberately narrow: the doc's much larger map-chain/vault-layer infrastructure is
  explicitly OUT of this item's reach; only the light-draws-things signal itself,
  applied to the one pocket map Lantern Deeps already has.
  Both new `.cs` files added to the csproj's explicit `Compile` list
  (`EnableDefaultCompileItems` is `false` in this project); `dotnet build -c
  Release` succeeded, 0 warnings/0 errors. Both new toggles (mineshaft entrance,
  darkness mechanic) plus their tuning sliders added to `LanternDeepsSettings`
  alongside the existing emergence toggle (MOD_OPTIONS_RETROFIT_1 convention).

- **Validated, not just built**: `validate_patch.py` against the frozen
  `OFFICIAL-2026-08-29` dump over the whole `LanternDeeps/` tree — 15 files, 0
  errors, 6 warnings, every one of which has an exact twin already shipping on the
  emergence entrance (texPath-in-AssetBundle false positives on both portals'
  placeholder art, the "class not resolvable from static Defs scan" info-line on
  both new C# GenStep classes — the actual build already proved these classes
  compile and link against `Assembly-CSharp.dll`, and the unwrapped
  `PatchOperationAdd` against Core's `MapCommonBase`, same as the existing pattern).
  Deployed via `deploy_custom_mods.py --mod LanternDeeps --apply` (mod was not in
  the currently-active `ModsConfig.xml`, so no OS-lock risk to the assembly write;
  `VERIFIED in sync` afterward).

⚠️ **Still owed, NOT provable this pass**:
  - **No live quicktest of either entrance or the darkness mechanic.** The bridge
    was held by a concurrent FOUNDRY window for an unrelated test and was not stale
    (idle ~5 min, well under the 45-min staleness bar) — not taken, per doctrine.
    Everything above is offline-built and statically validated only. Next bridge
    session: add this mod (already deployed) to a qualifying-biome minimal list,
    reach a host map, confirm both portals CAN appear, walk into each, confirm the
    Deep generates, and hold a light source near colonists long enough to trigger
    the darkness ambush without a crash.
  - **Spec item 1's own live quicktest** (recorded owed since 2026-09-07) is still
    not run, unrelated to this pass's additions.
  - **Mineshaft placement is not tied to actual ruin/mine world sites** — see the
    ASSUMPTION note above.
  - **Real art** for both entrances, and for the darkness predator's warning/
    feedback (the "visibly rewarded for playing dark" half of the ruling is
    mechanically true — no ambush without exposure — but has no distinct UI/FX
    signal yet, only silence).
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
