# traps — XML patches and defs

The authoring surface itself — xpath, `PatchOperation*`, inheritance, `ParentName`, def shape and the fields the engine reads.

**Read this one before writing a patch.** These are the traps that cost a game load rather than a rerun, because a bad patch fails *silently* and you find out 25 minutes later.

What goes in, and what does not: `references/traps.md`.

---

### An animal registered into a biome from both directions crashes the biome's animal table
**Symptom:** `System.ArgumentException: An item with the same key has already been added. Key: Armadillo`, thrown from `BiomeDef.CommonalityOfAnimal`. Three unrelated mods broke at once and none was the cause: Choose Wild Animal Spawns died in its static constructor, Giddy-Up logged "error calling AllWildAnimals … Skipping", Biome Compatibility Project threw inside the post-long-event queue.
**Cause:** an animal reaches a biome two ways — the biome's `<wildAnimals>` list, or the animal's `<race><wildBiomes>` list — and both `Add()` into one dictionary keyed on PawnKindDef. Beasts of the Rim redefined vanilla `Armadillo` with `wildBiomes` entries Core already listed; separately the Titans mod listed `TropicalSwamp` **twice inside its own** `wildBiomes`.
**Fix:** remove the **animal side** (`<wildBiomes>`), never the biome side — the biome's list keeps the animal spawning at the biome's commonality, so nothing is lost. For a self-duplicate, `.../TropicalSwamp[2]` with the same predicate in the conditional test. An offline duplicate-scan of both directions across 1,168 animals takes seconds and found exactly three bad pairs.
**Recurs when:** any engine field that is a `Dictionary<Def, X>` populated from two directions — the exception names the *key*, never the mod, so the log gives no attribution.

---

---

### `Inherit="False"` makes a correct patch a silent no-op
**Symptom:** a rebalance patch aimed at an abstract base applied cleanly — zero errors in `Player.log` — yet only 7 of 15 lightsabers went to power 99 / AP 0, and 8 stayed at 26 / AP −1.
**Cause:** another mod injected a whole replacement list onto each concrete def: `<li Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="Force_Lightsaber_Curved"]</xpath><value><tools Inherit="False">…</tools></value></li>`. `Inherit="False"` discards the parent's list outright, so our operation edited a node nothing inherits from any more. The child's tool *labels* also changed (`point` → `tip`), so a re-aimed xpath built from the base's labels would have matched nothing either.
**Fix:** offline inheritance resolution cannot see this — the injection happens at *patch* time. Compare the **live** tool labels against the ones the declarer wrote; where they differ, aim at the concrete `defName` instead of the base.
**Recurs when:** partial success across a def family — that is the signature. Read the other mod's `Patches/` folder, including `AdditionalMods/` and `LoadFolders.xml`-gated directories, not just its `Defs/`.

---

---

### ParentName is LOAD-ORDER dependent, and failing it corrupts map generation
**Symptom:** `XML error: Could not find parent node named "OuterRimTestColonyPawnKind" for node "PawnKindDef"` ×12, then `Config error in Jawa_Spawn_Hutt: no race`, `Jawa_Spawn_Hutt has no combatPower.`, `NullReferenceException at Verse.PawnKindDef+<ConfigErrors>d__156.MoveNext ()`. Downstream: `NullReferenceException at Verse.RaceProperties.get_AnyPawnKind () / Verse.ThingDef.ResolveIcon ()`, and `Error in GenStep: NullReferenceException at RimWorld.ScenPart_StartingAnimal…<PossibleAnimals>b__0 / RimWorld.Scenario.GenerateIntoMap` and `at RimWorld.BiomeDef.CommonalityOfAnimal` — traces naming only vanilla classes.
**Cause:** our patch mod sat at load position 20 while the mod defining the abstract parent sat at 38. Inheritance is **not** resolved order-free after the combined document is built: a child whose parent's mod loads later does not inherit, and everything the parent supplied is simply absent. A race-less PawnKindDef is then a landmine for every vanilla routine that enumerates pawnkinds. A manager re-sort caused it after the same defs had worked for days.
**Fix:** restore the load order; nothing in the defs needed changing. Assert load order in code before every launch — pick a def your mod inherits from or patches, find its owning mod, assert your index is greater.
**Recurs when:** a `Config error … no <field>` on a def that should inherit it, or a vanilla-only stack trace — grep the log for `Could not find parent node` and `Config error in <YourPrefix>` before believing the trace.

---

---

### Retargeting a gene family is two files, and the old family must stay
**Symptom:** swapping the six `Eyes_<colour>_Feline` genes on `BTD_Hutt` for the `Eyes_<colour>_Reptile` ones looks like a six-line find-and-replace in `HuttEyes_Slitted.xml`.
**Cause:** two patches cooperate. `HuttEyes_RestoreRenderNodes.xml` puts back the `renderNodeProperties` that [LFS] Genes Expanded strips whenever Facial Animation is installed. The live dump shows them **present** on `Eyes_*_Feline` only because our own restore file put them there, and **stripped** on `Eyes_*_Reptile` — so retargeting the assigning file alone hands the xenotype six genes that draw nothing, i.e. Hutts with no eyes. Separately, editing a `XenotypeDef` never rewrites existing pawns: the save held 24 Feline eye genes on already-spawned Hutts plus one on an unrelated pawn, so deleting the old family blinds them on load.
**Fix:** restore **both** families and let the xenotype roll only the new one. Every op is guarded `[not(renderNodeProperties)]`, so the unused half costs nothing on a save with none of those pawns.
**Recurs when:** any xenotype, backstory or gene-roster change — `grep` the `.rws` for the old defNames, and re-read the *unpatched* sibling def, because a repaired state is evidence about your patch, not about the mod.

---

---

### A build-over tier ladder deadlocks if the rungs disagree on terrain affordance
**Symptom:** in a three-tier "build the next tier over the previous one" ladder, tier 1 places fine and tier 2 then refuses to place over it forever — no error, no log line, just a blueprint the game will not accept. XML is valid, every def resolves, textures load, `validate_patch.py` is happy.
**Cause:** RimWorld checks `terrainAffordanceNeeded` against the terrain *under* the cells, and **a floor cannot be built on a cell occupied by an edifice**. The moment tier 1 stands on terrain that does not satisfy tier 2, the terrain can never be upgraded, because the thing blocking the upgrade is the thing being upgraded.
**Fix:** decide before authoring, never after. Either every rung declares the same affordance — WreckedMachines keeps VFE's `FactoryFloor` on all three smelter tiers, making tier 1's placement a map-authoring constraint (lay the floor first, under the wreck) — or the ladder relaxes to the lowest affordance any rung needs, which diverges the def from the donor it copies.
**Recurs when:** copying a donor def to make a derived tier — any field the game evaluates against the cells beneath a building is a ladder invariant, not a per-tier choice. Behaviour fields are free to copy; placement fields bind the whole chain.

---

---

### Building one thing over another is vanilla in 1.6 (`replaceTags`) — and Replace Stuff forbids our case
**Symptom:** the repair ladder's whole loop is "build the working machine over the wreck", and `DESIGN.md` named **Replace Stuff - Continued** (WS 3526354009, installed) as the compatibility target for it. Nobody had opened the mod.
**Cause:** two things. Its shipped `Source/` shows `NewThingFrame.cs:75` `CanReplace` returning false when `!oldDef.building?.deconstructible`, and `CanReplaceNewThingOverOldThing.cs:17` is a Harmony **postfix** on `GenConstruct.CanReplace` forcing `__result = false` when either side is a non-deconstructible attackable building — overriding cases vanilla would allow. Our wreck was `deconstructible=false` by design. Separately, **1.6 added `replaceTags`, a top-level `ThingDef` field** (sibling of `<building>`, not inside it): Core gives `Stool` `<replaceTags><li>Chair</li></replaceTags>` so it and `DiningChair` build over one another with no mod and no C#.
**Fix:** give every tier the same `replaceTags` entry and keep them deconstructible so the third-party postfix never fires.
**Recurs when:** adopting a dependency for a mechanic — grep `Data/Core/Defs` first, since 1.6 added fields that predate everyone's memory of "how you do this", and read the mod's shipped `Source/` rather than its store page, which describes the happy path and never the guards. This failure prints **no log line at all**, so it costs a full ~25-minute load to find.

---

---

### "It is placeable" and "it can be removed" are different claims — and the do-not-place twins are one word apart
**Symptom:** planning a salvageable ground-hulk from RimWorld's shipped ruins kit, the obvious picks were the thematically perfect ones — `AncientGravEngine`, `AncientGravReactor`, `AncientTerraformer`, the three 7×7 `Ancient*Vent`s, and BTD's four purpose-made *damaged gravship engines*. **Every one of them refuses deconstruction.** A colonist simply will not take the job; the only removal route is explosives. Eight of them were in my first draft of a "place these" list.
**Cause:** two abstract parents that look identical from a texture folder (`Data/Core/Defs/ThingDefs_Buildings/Buildings_Ancient_Outdoors.xml:4-28`). `AncientBuildingBase` sets `alwaysDeconstructible true`; `NonDeconstructibleAncientBuildingBase` sets `deconstructible false`. Across the active stack **73 defs** are on the second parent. The sharpest instance: **`AncientCryptosleepPod` cannot be deconstructed, while `AncientCryptosleepCasket` is the richest salvage in the whole kit (Steel 180 + Uranium 5).** Same art family, one word apart in the defName.
**Fix:** before designing any economy around shipped props, read `building.deconstructible` from the **live merged dump**, not the XML — mods patch it, and *Vanilla Vehicles Expanded* has already rewritten the entire Core vehicle-wreck set's `costList` in this install. Then apply the second test, which is the one that actually bites: **deconstructible ≠ yields anything.** Of 181 Core+DLC ruins defs, 167 deconstruct, but only **55 have a `costList`**; 33 have `killedLeavings` only, and **89 return nothing either way.** Actual yield is `costList × resourcesFractionWhenDeconstructed` (default 0.5), and `resourcesFractionWhenDeconstructed` is itself patchable — *Salvage Rubble* ships `0.00025` over a `Steel 1000` list to make a huge pile yield a trickle.
**Generalises to:** every "reuse the shipped assets" plan. Placement, removal, and yield are three independent properties and a def can pass any one while failing the others. Two companions found the same day: **a `TerrainDef` can never yield anything on removal** — terrain has no deconstruct-for-resources route at all, so a salvage economy cannot live in a floor no matter what its `costList` says; and for gravships, **`IsSubstructure` reads `HasTag("Substructure")`, NOT the affordance list** — `BTD_QuestSiteSubstructure` grants the `Substructure` *affordance* while omitting the *tag*, so things build on it but it does not connect or count toward capacity. Reading the affordance instead of the tag inverts the answer.

---

---

### A `WorldGenStepDef` that is not listed on the layer def is loaded, valid, and never called
**Symptom:** a custom `WorldGenStep` is authored, the `WorldGenStepDef` parses, the C# class resolves, the DLL loads, `validate_patch.py` is clean — and world generation produces a completely unshaped planet. No error, no warning, no log line. It looks exactly like a step that ran and decided to do nothing.
**Cause:** `PlanetLayerDef.GenStepsInOrder` is `worldGenSteps.Where(...).OrderBy(...)` over the **layer def's own private `List<WorldGenStepDef> worldGenSteps`** — *not* over `DefDatabase<WorldGenStepDef>.AllDefs`. `Data/Core/Defs/PlanetLayerDefs/PlanetLayers.xml:14-26` lists the Surface layer's steps **by defName** (Terrain, Lakes, Rivers, Mutators, Landmarks, AncientSites, AncientRoads, Pollution, Factions, Roads, Features). Membership of that list is what makes a step run; defining the def only makes it exist.
**Fix:** `PatchOperationAdd` the defName into `/Defs/PlanetLayerDef[defName="Surface"]/worldGenSteps`. ⚠️ **Position in the list does not set execution order** — `GenStepsInOrder` sorts by the `WorldGenStepDef`'s own `<order>` field, so append and let `order` place it. ⚠️ The list is cached in `PlanetLayerDef.cachedGenSteps` on first read, so this must be a load-time patch and cannot be done at runtime.
**Recurs when:** any def type whose consumers hold their own curated list instead of querying the database — the def existing is not the same claim as the def being *reachable*. `PlanetLayerDef.worldGenSteps` and `PlanetLayerDef.worldDrawLayers` both work this way. The tell is a `List<SomeDef>` field on another def; when you see one, membership is the registration and the DefDatabase is irrelevant.

---

---

### Vanilla's river step sources its mouths from the BIOME, but paths on ELEVATION
**Symptom:** a worldgen step raises or lowers tile elevation before the river step and the rivers come out wrong — either starting inland at nothing, or ignoring a new coastline entirely.
**Cause:** the two halves read different fields. `WorldGenStep_Rivers.GetCoastalWaterTiles` selects river MOUTHS by `PrimaryBiome == BiomeDefOf.Ocean` with a non-Ocean neighbour. The pathing then uses `GetImpliedElevation(tile)` = `elevation + {Hilliness 2→15, 3→250, 4→500, 5→1000}` and terminates on `WaterCovered`, i.e. `elevation <= 0`. So a tile raised out of the sea without a biome change keeps its stale `Ocean` label and stays a river mouth on dry land; and a tile lowered without an `Ocean` label is water that no river will ever aim at.
**Fix:** write `elevation` and `PrimaryBiome` **together, both directions**, in any step that moves the coastline. Nothing re-runs biome selection after `WorldGenStep_Tiles` at order 5.
**Recurs when:** editing tiles between order 5 and order 200. Also note `hilliness` contributes up to **+1000** to implied elevation — far more than a typical elevation delta — so adjusting elevation alone can be swamped, and `AccumulateFlow` reads only `rainfall` and `temperature`, so flow volume does not follow a coastline change unless those move too.

---

---

### `xenotypeChances` is a def-keyed dictionary — the xenotype is the ELEMENT NAME, not a value
**Symptom:** a patch re-pointing a pawn kind at a different xenotype matches nothing. The xpath looks right, the def exists, `validate_patch.py` is clean, and nothing errors — the kind just keeps generating the old xenotype.
**Cause:** the block is
```xml
<xenotypeSet><xenotypeChances><OuterRim_Jawa>999</OuterRim_Jawa></xenotypeChances></xenotypeSet>
```
`<OuterRim_Jawa>999</OuterRim_Jawa>` means *this xenotype, this weight*. **There is no `<li>` and no text node naming the xenotype**, so every instinctive xpath — at a `<li>`, at a value, at a `defName` attribute — targets something that does not exist.
**Fix:** replace the whole `xenotypeChances` node. Guard with `PatchOperationConditional` testing the child element (`.../xenotypeChances/OuterRim_Jawa`) and `PatchOperationReplace` the parent; the inner/outer xpath mismatch is intentional and the validator's warning about it is expected here.
**Recurs when:** any def field RimWorld serialises as `Dictionary<Def, T>` — the def becomes a tag name. `xenotypeChances` is the one that bites, but the shape is general: **if a block's children are named after defs rather than being `<li>`, the key is the tag and you must replace the container.** ⚠️ `OuterRim_Jawa` exists as BOTH a `XenotypeDef` and a `PawnKindDef` in the same file — the `xenotypeSet` lives on the pawn kind, so patching the xenotype changes nothing.
**Timing:** `xenotypeSet` is read at PAWN GENERATION, so a patch that lands after a world exists never fixes that world's colonists. It is a pre-worldgen gate, not a tuning patch, and it fails by producing quietly wrong pawns rather than an error.

---

### `isJunk` on a scatterer lets a world-tile mutator silently multiply its count to ZERO
**Symptom:** a `GenStep_ScatterThings` with `countPer10kCellsRange 12~20` that should place 75–125 things on a 250×250 map, placing far fewer or none, with no warning — a count of 0 never enters the placement loop, so it cannot emit `could not find cell to generate at`.
**Cause:** `GenStep_Scatterer::CalculateFinalCount` is `CountFromPer10kCells(...) × GetPlacementFactor(map)`, and when `isJunk` is true `GetPlacementFactor` returns the PRODUCT of `TileMutatorDef::junkDensityFactor` over every mutator on the map's world tile. Of 337 mutators, five are **0** — `Dunes`, `Iceberg`, `VEE_DetachedIceberg`, `VEE_IceAndFire`, `VEE_QuicksandDunes` — and `Junkyard` is 15. The product is therefore 0, 1, or a power of 15; there is no gentle fraction.
**Fix:** predict the count as `range × area/10000 × junkDensityFactor product`, not the first two terms. Drop `isJunk` if the content must appear on dune or ice tiles, knowing it also stops keeping junk off the player start.
**Recurs when:** any `GenStep_Scatterer` subclass with `isJunk` — including `GenStep_ScatterGroupPrefabs`, whose `Generate` is a bare `base.Generate` call and inherits the factor unchanged.

---

### Copying defs out of a mod: `Name=` is a SECOND global namespace, and the check has to be against the mod set that SURVIVES
**Symptom:** a standalone mod built by copying another mod's defs validates clean, loads clean and renders perfectly — right up until the donor is switched off, which was the entire point of building it. Then heads, eyes and icons vanish with no error naming the copy.
**Cause:** three separate leaks, and a clean `validate_patch.py` cannot see any of them, because it resolves against the CURRENT load set where the donor is still installed and every stale reference still works.
1. **`ParentName` resolves a `Name=` attribute, never a defName**, and `Name=` is global across all mods. Leave a copied abstract with the donor's `Name` and it collides while the donor is present and disappears with it. A concrete def can carry BOTH `defName` and `Name=`, so a rename pass keyed only on `defName` misses it.
2. **A def can be reached only through an inherited one.** A closure that walks defs, then resolves abstracts in a second pass, will mark the abstract's references seen without expanding them — and the defs THOSE reach never enter the set. One queue, defs and abstracts together, or the set is quietly short.
3. **A grep for the donor's prefix only works if the rename STRIPS it.** `guy762_X` -> `RimMandrake_guy762_X` keeps the substring and the grep can never come back clean.
**Fix:** build the check the validator cannot: take the def dump, drop every def whose only owner is a departing packageId, and assert no reference in the new mod lands in that set. Do the same for texture paths against the files actually copied. Both must be zero.
**Recurs when:** any "own it outright so the donor can be removed" job — xenotype packs, retexture rescues, fork-a-mod. ⚠️ Also check `Class=` on modExtensions: a cosmetic extension can be compiled into the departing mod's own assembly (`EyeOffsetSouth.dll` ships inside Star Wars Xenotypes), and that is a C# dependency no XML grep will show you.
