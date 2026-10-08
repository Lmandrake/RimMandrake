# Huge Things + Titanic Creatures: merge design pass (2026-10-07)

BENCH design pass, read-only on code (HugeThings is mid-rework in this clone: `Source/*.cs`, the DLL and its
`.srchash` are uncommitted-modified right now). Owner's ask, 2026-10-07: *"I still think they might actually be a
single mod. Please do a design pass to analyze the pro and con of combining them together or not. One less mod is
pretty nice right about now."*

## 0. Verdict

**Merge, as a packaging merge: Titanic Creatures folds INTO Huge Things.** The survivor keeps `mandrake.rm.hugethings`
and its name, the C# namespaces and type names stay exactly as they are, and only `mandrake.rm.titaniccreatures`
is retired. Do it **after** the Huge Things rework is accepted in game, not tonight. Size: about half a day of
mechanical work plus one cold load.

Why: Titanic Creatures can never run without Huge Things (a hard dependency today), the two share no code
beyond one call, and keeping every type's full name unchanged leaves existing saves loading cleanly.

## 1. Overlap (what the code actually shares)

| | Huge Things (`src/RimMandrake/HugeThings`) | Titanic Creatures (`src/RimMandrake/TitanicCreatures`) |
|---|---|---|
| packageId | `mandrake.rm.hugethings` | `mandrake.rm.titaniccreatures` |
| C# | ~2,410 lines, namespace `RimMandrake.HugeThings`, `RM_HugeThings.dll` | ~1,750 lines, namespace `RimMandrake.TitanicCreatures`, `RM_TitanicCreatures.dll` |
| Subjects | huge PLANTS (ground-contact blockers measured from art, whole-picture selection, cover and damage forwarding) and huge PAWNS (click hitbox) | titan PAWNS (tiers by bodySize, destruction wake, thick-roof avoidance, butcher yield curve, T3 corpse site, Large Pawns reconciliation) |
| Harmony | 6 patches (`CustomRectForSelector`, `ThingsUnderMouse`, `ZoneManager`, `PlantCollected`, `ExplosionDamageThing`, gravship `ClearArea`) | 4 patches (`Thing.Position` set, `CostToMoveIntoCell`, `Corpse.SpawnSetup`, `ButcherProducts`) |
| Settings | 5 fields: plant footprint on/off, plant selection on/off, footprint scale, pawn hitbox on/off, hitbox scale | 12 fields: wake (+2 tunings), roof avoidance, yield curve (+1), corpse site (+5) |
| Large Pawns | `loadAfter` only: selection postfix runs last so it wins over Large Pawns' square | soft, reflection only (`Source/Footprint/LargePawnsBridge.cs`); no compile reference; degrades to 1x1 |
| Saved types | `MapComponent_HugeFootprints`, `Building_TrunkBlocker` (def `RM_HugeTrunkBlocker`) | `Building_TitanicCorpseSite` (def `RM_TitanicCorpseSite`), `CompTitanicWake` |
| North star | walk `design/validation_walks/RimMandrake/HugeThings.md` **DRAFT** | walk `.../TitanicCreatures.md` **DRAFT** |

**The one cross-call.** `TitanicCreatures/Source/RM_TitanicCreaturesMod.cs:59` calls
`RimMandrake.HugeThings.HugeThingsApi.OptInPawn(td)` for every tiered race. It is wired by a `<Reference>` HintPath to
`..\..\HugeThings\Assemblies\RM_HugeThings.dll` in `RM_TitanicCreatures.csproj` and a hard `modDependencies` entry in
Titanic's `About.xml`. No other code is shared, and nothing is duplicated.

**Shared concepts, not shared code.**
- *Footprint* means two different things. In Huge Things it is the plant's ground-contact cells: invisible
  blocker buildings, which only plants get. In Titanic it is the pawn's occupied cells, and those come from Large
  Pawns via `GenAdj.OccupiedRect`, not from our code.
- *Selection*: only Huge Things does this, for both plants and pawns. Titanic just opts its pawns in.
- *Scale by size*: Titanic tiers on `race.baseBodySize` (`RM_TitanicTiers_Default`: T1 >= 4, T2 >= 8, T3 >= 20).
  The Huge Things hitbox scales on drawn size (`drawSize x hitboxFraction 0.6`). These are two different axes and
  both are right: one is mass, the other is the picture. They are not two ladders competing for one decision.
- *Blocking*: plant blockers are impassable buildings. The Titanic wake crushes Buildings at T2+
  (`RM_Crush_Buildings`, category match). `RM_HugeTrunkBlocker` is `<category>Building</category>`. Whether the
  crush table's ThingCategoryDef match ever reaches it, or reaches a huge plant through `RM_Crush_Plants` at T1,
  is **UNMEASURED**. No rule decides what a titan does to a giant fungus. **This is the one real design seam between
  the two mods**, and nobody owns it today.

**The Large Pawns question in the brief is moot.** Neither mod hard-depends on `neku.largepawns`. Titanic reaches
it by reflection and works without it at 1x1. Huge Things only orders itself after it. So merging forces Large
Pawns on nobody.

## 2. Pros and cons

### Merge into one mod

**Pros**
1. **One less mod, and an honest one.** Titanic already cannot be installed without Huge Things. Huge Things'
   own description already promises "huge plants and huge animals". A player sees one mod that handles size.
2. **The cross-mod seam disappears.** The HintPath reference to another mod's DLL, the hard dependency, and the
   `loadBefore`/`loadAfter` pair all go. The giant-plant-vs-titan rule (section 1) gets a single owner.
3. **One review walk and one validation script.** This is what the owner asked for. Both north stars are DRAFT,
   so no validated hash is lost.
4. **Rebuild ordering goes.** Today a Huge Things API change must rebuild Titanic against the new DLL. Inside one
   assembly the compiler catches it.

**Cons**
1. **A plant-only player gets titan behaviour on vanilla's largest animals.** Tiering auto-attaches at bodySize
   >= 4, and vanilla animals reach 4 to 5 (the test-race item records the max as 5.0). They would leave a T1 wake
   (plant trampling, rubble trail) and get the butcher yield curve. Today a player avoids this by leaving Titanic
   off. After the merge they need a **master "Titanic creatures" toggle**, or the T1 threshold raised so that no
   vanilla animal qualifies. That is question 2 below.
2. **Existing saves and test lists name `mandrake.rm.titaniccreatures`.** Measured: Autosave-4 to Autosave-10 and
   the five `MC_NS_*_20261004.rws` saves. Loading them gives a "mods changed" warning and nothing worse, *provided
   type full names do not change* (saves store `Class="RimMandrake.HugeThings.Building_TrunkBlocker"`,
   `...MapComponent_HugeFootprints`; measured in `HugeThings_RotWalk_2026-10-07.rws`).
3. **Collision with tonight's rework.** Every Huge Things `.cs` file, its DLL, `.srchash` and selftests are
   modified in this clone, and FOUNDRY is to keep builders off Huge Things until `HUGE_THINGS_FOOTPRINT_1` is
   accepted. A merge now would land on top of uncommitted work.
4. **A bigger settings page.** That is 17 settings instead of 5 + 12. It is manageable with two headed sections,
   but scrolling is mandatory (Titanic's page already scrolls).

### Keep two

**Pros**: no migration work. A plant-only player is untouched by titan mechanics without needing a new toggle.
Tonight's rework is not disturbed.
**Cons**: the owner reviews and maintains two mods that always ship together. The DLL-to-DLL reference survives,
which is a stale-build trap. The giant-plant-vs-titan rule still has no owner.

### Per-feature toggles survive either way
All 17 fields keep their names. Settings files are keyed `Mod_<mod folder>_<Mod class>.xml`
(`Verse/LoadedModManager.GetSettingsFilename`, decompiled 1.6). **Measured: no settings file for either mod exists
yet** in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config`, so settings migration
costs nothing today.

## 3. Merge plan

**Name**: keep **RimMandrake: Huge Things**, `mandrake.rm.hugethings` (free `RM_` tier, no franchise content in either
mod). Keeping the surviving id means the Rot patch, the Rot walk save, Huge Things' Harmony id and its validation
script all keep working untouched. (Alternative: a new name such as "RimMandrake: Giants", `mandrake.rm.giants`.
It reads better, but it retires *both* ids and forces the Rot patch's 10 `MayRequire` attributes to be regenerated.
Question 1 below.)

**Layout after the merge** (`src/RimMandrake/HugeThings/`):
```
About/About.xml           one description: plants, creatures, titans; deps Harmony only; loadAfter neku.largepawns
Defs/                     + TitanicCreatures' Defs/{CrushRuleDefs,JobDefs,ThingDefs,TitanicTierDefs,WorkGiverDefs}
Languages/                from TitanicCreatures
Source/                   existing Huge Things files, unchanged
Source/Titanic/           TitanicCreatures/Source/* moved as-is, namespace RimMandrake.TitanicCreatures KEPT
Source/Kernel/            + RM_TitanicKernel.cs (namespace kept)
Source/SelfTest/          one SelfTest project running both fuzzers (HugeThingsFuzz + TitanicFuzz)
Assemblies/RM_HugeThings.dll (+ .srchash)    the one DLL
validation.py             one suite: Huge Things checks + Titanic checks, sectioned
```

**Migration, in order** (each step its own commit):
1. **Gate**: `HUGE_THINGS_FOOTPRINT_1` accepted in game, and the rework committed and pushed. Nothing starts before this.
2. Move the Titanic `Defs/`, `Languages/` and `Source/` into Huge Things with `git mv`. Keep every namespace,
   type name, defName and Harmony id (`mandrake.rm.titaniccreatures` stays as a *Harmony id string*, which is
   harmless and keeps Titanic's validation checks valid).
3. Merge the two csproj files into `RM_HugeThings.csproj`, delete `RM_TitanicCreatures.csproj` and its HintPath,
   merge the two SelfTest projects, then `winbuild.py HugeThings`. That gives one DLL and one `.srchash`. Delete
   `RM_TitanicCreatures.dll` and its `.srchash`.
4. Settings: keep both `ModSettings` classes. Replace the two `Mod` subclasses with one `RM_HugeThingsMod` whose
   window draws "Huge plants", "Huge creatures (click hitbox)" and "Titanic creatures" sections. Add the master
   toggle if the owner rules for it (Q2). Fold `RM_TitanicCreaturesOptionsMod`'s `GetSettings` call into it.
5. `About.xml`: merge the descriptions, drop the self-dependency and the `loadBefore mandrake.rm.titaniccreatures`.
6. Tooling: `src/RimMandrake/Utils/modset_builder.py` lines ~607 and ~625 (`mandrake.rm.titaniccreatures` becomes
   `mandrake.rm.hugethings`). `src/RimMandrake/Utils/modcheck/required_checks.json` key `TitanicCreatures` merges into
   `HugeThings` (which has no entry today). Rename or merge `Utils/{lint,selftest,mutate}_titaniccreatures_*.py`,
   plus the deploy tool's mod-folder entry. Retire the deployed `...\RimWorld\Mods\TitanicCreatures` folder and swap
   the id in `ModsConfig.xml`.
7. Walks: merge `design/validation_walks/RimMandrake/TitanicCreatures.md` into `HugeThings.md` (both DRAFT, so no
   hash to lose). Retarget `TITANIC_CREATURES_FIRST_SCRIPT_1` and `TITANIC_BODYSIZE_TEST_RACE_1` at Huge Things.
   Fix the comment in `src/RimUtinni/Atlas/Defs/AtlasEntryDefs/RUT_Atlas_World.xml:168`; it names the packageId,
   while the `RM_TitanicCorpseSite` defName is unchanged.
8. `code_review_status`: every moved file has no record at its new path, so it is DIRTY, which it already was
   (the rework left every Huge Things file DIRTY). Full-file review once, after the move.
9. One cold load on a list with Harmony + Huge Things + `mandrake.rm.biomes` + a titan-carrying mod. Load
   `HugeThings_RotWalk_2026-10-07.rws` and one `MC_NS_*` save, and confirm no `Could not load reference` lines.

**What breaks, and how it is avoided**
- **Renaming namespaces** would orphan every saved trunk blocker, map component and corpse site, which the save
  addresses by full type name. *Avoided: namespaces are kept.*
- **Moving types to another assembly is safe**: Scribe resolves `Class=` by type name across all loaded assemblies
  (`GenTypes`), not by assembly.
- **The Rot patch** (`src/RimMandrake/TheRot/Patches/RotGiants_HugeFootprint.xml`, 10 conditional ops with
  `MayRequire="mandrake.rm.hugethings"`) is untouched if the id survives. With a new id, rerun
  `measure_huge_plant_masks.py` with the new id. Never hand-edit it; it is generated.
- **Saves listing the retired id** give the vanilla "mod list changed" dialog and load on. A save listing the retired
  id with no Huge Things at all would lose its corpse sites, the same as removing the mod today.

**Size**: steps 2 to 8 are mechanical, roughly 3 to 4 hours of agent work including the rebuild and both
selftest suites. Step 9 is one cold load (~15 min) plus checking. No design work, except the master toggle and
the plant-vs-titan rule.

### If not merging
Keep `HugeThingsApi` as the only boundary. Then: make Huge Things' `RM_HugePawnExtension` the documented opt-in, so
Titanic could depend on the API without a DLL HintPath (for example a `PatchOperationAddModExtension` in XML in
place of the C# call). Write the giant-plant-vs-titan crush rule into Titanic's `RM_CrushRules.xml` as an exact-def
row for `RM_HugeTrunkBlocker` (`crushable false`). Review both on one walk anyway (section 5).

## 4. Recommendation and questions

**Recommendation: merge Titanic Creatures into Huge Things (keep `mandrake.rm.hugethings`), after the rework is
accepted. Titanic can never run alone, so two mods only add a seam with no payoff.**

Questions for the owner:

1. **What is the combined mod called?**
   - *Keep "Huge Things"* (`mandrake.rm.hugethings`): no save warnings for the Rot walk save and no generated patch
     to rerun. The name undersells titans who smash roofs.
   - *A new name, e.g. "Giants"* (`mandrake.rm.giants`): reads better to a player. Both ids retire, every existing
     test save warns once, and the Rot patch is regenerated.
   - *Keep "Titanic Creatures"*: the punchier name, but it reads oddly for mushrooms. The Rot patch is regenerated.
2. **A player who only wants giant plants: should vanilla's biggest animals still become T1 titans?**
   - *One master switch "Titanic creatures" (default on)*: plant-only players turn it off. Simple, and one more
     toggle.
   - *Raise T1 to bodySize 6*: no vanilla animal qualifies. Our 4 to 5.5 creatures drop out too (Guzzka 5.5,
     Zakkro 5.5, Vozzik 5).
   - *Leave it*: elephants and thrumbos trample plants. That is arguably right, and it is the shipped behaviour
     today for anyone running both.
3. **What does a titan do to a giant fungus it walks into?** (Nothing decides this today.)
   - *Paths around it like a wall*: the trunk is solid ground. Safe and predictable.
   - *T3 titans smash through, damaging the plant*: dramatic and on-theme ("mass has consequences"). It needs a
     crush row and a damage route into the plant (the cover-forwarding code already exists).
   - *Decide on the walk*: look at it in game first.
4. **When?** *After the Huge Things rework passes its walk* (recommended: no collision, one clean move), or *now,
   pausing the rework* (one walk sooner, but it lands on uncommitted work).

## 5. Combined walk plan (one save, not built)

**List**: Harmony + Huge Things (+ Titanic, or the merged mod) + `neku.largepawns` + `mandrake.rm.biomes` (The Rot
giants) + `mandrake.rsw.swbestiary` (only if the war wyrm is wanted) + all five DLCs. A quicktest map, flat, Rot or
any soil biome, daylight, hostiles swept (`kill_hostiles`) at build and each visit. All titans **colony-tamed** so
nothing goes manhunter.

**Creatures** (no vanilla race is titan-sized; ours, measured from their ThingDefs and PawnKindDefs):

| Tier | Creature | bodySize | drawn size | home | why it is here |
|---|---|---|---|---|---|
| T1 (4-8) | `RM_Borehulk` (borehulk, digging-tank machine) | 6 | 5 | Rust Cathedral | T1 wake: plant trampling and rubble trail, no wall crush |
| T1 | `RM_Ulgga` (tusked engineered worm) | 6 | 8.2 | Long Shade | a long body: checks that the hitbox covers the drawn length |
| T2 (8-20) | `RM_Hwelgrue` (Rot's bone-white decomposer maggot) | 8 | 5 | The Rot | **the bridge between the mods**: a Rot titan beside Rot giants |
| T2 | `RM_Totchak` (plated colossus) | 14 | 7 | Scarlands | crushes walls and holes thin roofs |
| T2 | `RM_Gorrask` (canyon stone-crab) | 15 | 5 | Weeping Stones | big mass, small picture: hitbox vs footprint mismatch case |
| T3 (20+) | `RM_Gloomcast` (dayside grazer) | 24 | 13.2 | Long Shade | T3 wake, and the corpse-site candidate |
| T3 | `RM_Oommok` (walking mirror-plated mountain) | 36 | 15 | Stillsand | the largest land titan we have |

(Sea colossi such as the lanternwhale (40) and reefback (32) are left out because they belong on the sea floor.
`RSW_WarWyrm` (22.5, drawn 15) can stand in for the Gloomcast if the Star Wars layer is loaded.)

**Grid** (pitch 30 cells, so a 20-wide grath elder never overlaps its neighbour):
```
row A (plants)   AB_AgariluxPrime | AB_DribblingCap | RM_Nogtyl | RM_Arpeau | AB_ArbuscularMycorrhiza
row B (plants)   AB_AgaricusDomeCap | AB_GiantAgarilux | AB_WitchesOyster | RM_PaleTree | (one young giant, growth 0.3)
row C (titans)   Borehulk | Ulgga | Hwelgrue | Totchak | Gorrask
row D (titans)   Gloomcast | Oommok | Gloomcast CORPSE (killed, for the corpse site) | test strip (see below)
test strip       a thin-roofed 5x5 room, a wall line, crates, a sandbag line, and a patch of overhead-mountain roof,
                 laid across a titan's path to a food spot
```
The grid key goes in the item file with the save; the save is kept until he says delete.

**What he looks at**
- *Plants*: click the edges of each picture (cap tips, roots) and confirm it selects. Pawns path around the
  stems and walk under caps. Try to build a wall inside a stem and confirm it is refused. Shoot a trunk: partial
  cover, and the plant takes damage. The vokkun pillar's own cell is solid. The young giant blocks less than the
  full-grown one.
- *Titans*: click anywhere on each drawn body (the Ulgga's tail, the Oommok's edge). The Large Pawns square sits
  under each body. Walk the T1, T2 and T3 titans through the test strip: crates and plants crushed by T1, the
  wall breached and the thin roof holed by T2+, overhead mountain avoided. The Gloomcast corpse stands as a
  harvest site, and a hauler runs one session.
- *The seam (Q3)*: order the Totchak and the Oommok to a spot behind the grath elder and watch whether they go
  around it or through it.
- *Settings*: turn each section's toggle off, unpause, and confirm the behaviour stops.
