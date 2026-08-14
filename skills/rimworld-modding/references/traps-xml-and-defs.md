# traps — XML patches and defs

The authoring surface itself — xpath, `PatchOperation*`, inheritance, `ParentName`, def shape and the fields the engine reads.

**Read this one before writing a patch.** These are the traps that cost a game load rather than a rerun, because a bad patch fails *silently* and you find out 25 minutes later.

Entry format, admission test and the append rule: `references/traps.md`.

---

### ParentName must name an ABSTRACT def — `validate_patch.py` checks this since 2026-08-13
**Symptom:** `XML error: Could not find parent node named "EMP" for node "DamageDef"`, once per load. The whole DamageDef is **discarded**, so the weapon's `damageDef` and its stun hediff both reference nothing.
**Cause:** the def said `ParentName="EMP"`, and `EMP` is a **concrete** def (`<defName>EMP</defName>`). `ParentName` resolves only against defs declared with a `Name=` attribute, i.e. `Abstract="True"` templates. Core's own EMP uses `ParentName="StunBase"`, where `StunBase` is `<DamageDef Name="StunBase" Abstract="True">`.
**Fix:** `ParentName="StunBase"` — copy the parent the *vanilla equivalent* uses, not the vanilla def's own name. Before shipping any `Defs/` file, resolve every outward-pointing name (`ParentName`, `Class=`, `workerClass`, `thingClass`, `graphicClass`) against the live load set: `ParentName` against abstract defs, class names against loaded assemblies.
**Recurs when:** anything under `Defs/`. ✅ **Closed as a blind spot 2026-08-13:** `validate_patch.py` now dispatches on the root element and resolves every `ParentName` against `Name=` attributes across the whole load set, erroring when it resolves to nothing. It also checks `Class=` attributes and `texPath` existence. It still does **not** check field names, types or value ranges, and an internal defName cross-reference audit still never touches the GAME's abstract-def namespace.

---

### An `<li>` written into a dictionary-keyed field deleted seven biomes
**Symptom:** ~950 × `Could not resolve cross-reference: No RimWorld.BiomeDef named Desert/AridShrubland/ExtremeDesert/ZBiome_Badlands/… found to give to AnimalBiomeRecord`, plus `Failed to find RimWorld.BiomeDef named Desert. There are 59 defs of this type loaded.` The only honest evidence for the cause was seven quiet lines: `Could not resolve cross-reference: No Verse.WeatherDef named li found to give to RimWorld.WeatherCommonalityRecord`, one per patched biome.
**Cause:** the patch added weather in list form, `<li><weather>SW_Sandstorm</weather><commonality>8</commonality></li>`, but `<baseWeatherCommonalities>` is dictionary-keyed: `<Clear>18</Clear>`. The engine read the element name `li` as the WeatherDef name, failed, and discarded the entire BiomeDef, nulling everything downstream that referenced those biomes.
**Fix:** `<SW_Sandstorm>8</SW_Sandstorm>` — the shape is set by the field's C# type, so it is identical in every mod. `validate_patch.py` now compares a `<value>`'s children against the live node's existing children. Validate *every* file in the mod folder before deploying, not just the one you changed: the blast radius is the mod.
**Recurs when:** any Add or Replace whose `<value>` targets a dictionary-keyed field — a shape error there is destructive, not inert; every other patch mistake merely fails to apply.

---

### An animal registered into a biome from both directions crashes the biome's animal table
**Symptom:** `System.ArgumentException: An item with the same key has already been added. Key: Armadillo`, thrown from `BiomeDef.CommonalityOfAnimal`. Three unrelated mods broke at once and none was the cause: Choose Wild Animal Spawns died in its static constructor, Giddy-Up logged "error calling AllWildAnimals … Skipping", Biome Compatibility Project threw inside the post-long-event queue.
**Cause:** an animal reaches a biome two ways — the biome's `<wildAnimals>` list, or the animal's `<race><wildBiomes>` list — and both `Add()` into one dictionary keyed on PawnKindDef. Beasts of the Rim redefined vanilla `Armadillo` with `wildBiomes` entries Core already listed; separately the Titans mod listed `TropicalSwamp` **twice inside its own** `wildBiomes`.
**Fix:** remove the **animal side** (`<wildBiomes>`), never the biome side — the biome's list keeps the animal spawning at the biome's commonality, so nothing is lost. For a self-duplicate, `.../TropicalSwamp[2]` with the same predicate in the conditional test. An offline duplicate-scan of both directions across 1,168 animals takes seconds and found exactly three bad pairs.
**Recurs when:** any engine field that is a `Dictionary<Def, X>` populated from two directions — the exception names the *key*, never the mod, so the log gives no attribution.

---

### A field silently moved off its class in 1.6, and eight races carried the stale version
**Symptom:** `XML error: <wildness> doesn't correspond to any field in type RaceProperties`, eight times, from one mod.
**Cause:** the field moved in 1.6. The mod was carrying pre-1.6 defs. The value is dropped and the def loads anyway, so the races existed but with wrong behaviour rather than none.
**Fix:** the mod was abandoned; it was removed. Where a mod is worth keeping, a `PatchOperationRemove` on the stale node silences the error, and the real behaviour has to be re-established wherever the field went.
**Recurs when:** `doesn't correspond to any field` — that is a **version drift** report, not a typo report; it means the mod predates the game, and the count is a severity signal (eight instances = eight defs quietly wrong).

---

### `Inherit="False"` makes a correct patch a silent no-op
**Symptom:** a rebalance patch aimed at an abstract base applied cleanly — zero errors in `Player.log` — yet only 7 of 15 lightsabers went to power 99 / AP 0, and 8 stayed at 26 / AP −1.
**Cause:** another mod injected a whole replacement list onto each concrete def: `<li Class="PatchOperationAdd"><xpath>Defs/ThingDef[defName="Force_Lightsaber_Curved"]</xpath><value><tools Inherit="False">…</tools></value></li>`. `Inherit="False"` discards the parent's list outright, so our operation edited a node nothing inherits from any more. The child's tool *labels* also changed (`point` → `tip`), so a re-aimed xpath built from the base's labels would have matched nothing either.
**Fix:** offline inheritance resolution cannot see this — the injection happens at *patch* time. Compare the **live** tool labels against the ones the declarer wrote; where they differ, aim at the concrete `defName` instead of the base.
**Recurs when:** partial success across a def family — that is the signature. Read the other mod's `Patches/` folder, including `AdditionalMods/` and `LoadFolders.xml`-gated directories, not just its `Defs/`.

---

### ParentName is LOAD-ORDER dependent, and failing it corrupts map generation
**Symptom:** `XML error: Could not find parent node named "OuterRimTestColonyPawnKind" for node "PawnKindDef"` ×12, then `Config error in Jawa_Spawn_Hutt: no race`, `Jawa_Spawn_Hutt has no combatPower.`, `NullReferenceException at Verse.PawnKindDef+<ConfigErrors>d__156.MoveNext ()`. Downstream: `NullReferenceException at Verse.RaceProperties.get_AnyPawnKind () / Verse.ThingDef.ResolveIcon ()`, and `Error in GenStep: NullReferenceException at RimWorld.ScenPart_StartingAnimal…<PossibleAnimals>b__0 / RimWorld.Scenario.GenerateIntoMap` and `at RimWorld.BiomeDef.CommonalityOfAnimal` — traces naming only vanilla classes.
**Cause:** our patch mod sat at load position 20 while the mod defining the abstract parent sat at 38. Inheritance is **not** resolved order-free after the combined document is built: a child whose parent's mod loads later does not inherit, and everything the parent supplied is simply absent. A race-less PawnKindDef is then a landmine for every vanilla routine that enumerates pawnkinds. A manager re-sort caused it after the same defs had worked for days.
**Fix:** restore the load order; nothing in the defs needed changing. Assert load order in code before every launch — pick a def your mod inherits from or patches, find its owning mod, assert your index is greater.
**Recurs when:** a `Config error … no <field>` on a def that should inherit it, or a vanilla-only stack trace — grep the log for `Could not find parent node` and `Config error in <YourPrefix>` before believing the trace.

---

### "PatchOperationFindMod(X) failed" does not mean mod X is missing
**Symptom:** `[Jawa Doctrine Patches] Patch operation Verse.PatchOperationFindMod(Asimov) failed`, and nothing applied — while `Asimov` (`neronix17.asimov`) was active and its `About.xml` `<name>` matched character for character.
**Cause:** `PatchOperationFindMod` returns the **inner** result (`if (flag) { if (match != null) return match.Apply(xml); }`) while `ToString()` prints the outer FindMod, so an inner failure is reported under the wrapper's name. When the mod is genuinely absent and there is no `nomatch` it returns **true** — a missing mod is silent, and only a broken inner op ever logs. The real fault: the inner `PatchOperationReplace` targeted `FleshTypeDef/isOrganic`, and no FleshTypeDef declares `isOrganic` in XML at all — it is a C# field default (`public bool isOrganic = true`).
**Fix:** `PatchOperationConditional` — replace when the node exists, add when it does not. Reach for it by default: tools with no `armorPenetration` were skipped by Replace, leathers that already had `statFactors` were duplicated by Add, flesh types with no `isOrganic` gave Replace nothing to find.
**Recurs when:** any wrapper op (`FindMod`, `Sequence`, `Conditional`) in a patch error — the printed name is the container, not the failure. And any field left at its C# default has no node for `Replace` to reach.

---

### A def's XML element name IS its C# class — `VFEPirates.WarcasketDef` is invisible to `/Defs/ThingDef` yet lives in `ThingDef.json`
**Symptom:** `Armour_Ratings.xml` targets `/Defs/ThingDef[...]` and silently misses **every warcasket**, the single biggest armour outlier in the stack. Separately, two audits contradicted each other: "warcaskets are `VFEPirates.WarcasketDef`, not ThingDefs" versus "`VFEP_Warcasket_Hazard` is right there in `ThingDef.json`".
**Cause:** both are true. RimWorld's loader reads the **element name as the C# type**, so the XML must be matched as `<VFEPirates.WarcasketDef>` and `/Defs/ThingDef[…]` matches nothing — but that class **subclasses `ThingDef`**, so at runtime it lives in `DefDatabase<ThingDef>`, the dump files it under `ThingDef.json`, and there is **no** `WarcasketDef.json`. `…/2723801948/1.6/Defs/ThingDefs_Misc/Apparel_Various.xml` holds 30 `<VFEPirates.WarcasketDef>` and 4 `<ThingDef>` in one file; every piece *including the helmet* has a `<costList>` and no `<recipeMaker>`, so there is no crafting recipe to patch or remove.
**Fix:** `/Defs/VFEPirates.WarcasketDef[…]`. Use `/Defs/*[defName="X"]` only when the class is what varies — it hits *every* class with that defName, and `ReduceWill` is both an `InteractionDef` and a `PrisonerInteractionModeDef`.
**Recurs when:** any tool keyed on the XML element name — `gen_armour_patch.py`'s `ds.of_type("ThingDef")` skipped all 51 warcasket pieces and reported success. Absence from a dump file named after a def type is not absence from the load; look for the *base* type's file.

---

### 34. One failed op silently kills every op after it in the same sequence
**Symptom:** `Verse.PatchOperationAdd(xpath="/Defs/ThingDef[defName="DA_Taraal"]/statBases"): Failed to find a node with the given xpath`, then `Verse.PatchOperationConditional(xpath=…/statBases/MeatAmount): Error in <nomatch>`, `Verse.PatchOperationSequence: Error in the operation at position=25`, `Verse.PatchOperationFindMod(Dark Ages : Beasts and Monsters): Error in <match>`. That block held **32** operations, so positions 26–32 never ran and the log says nothing about them.
**Cause:** `DA_Taraal` has no `<statBases>` of its own — it inherits from `<ThingDef Name="DA_BaseTaraal" Abstract="True">` — and **`ParentName` inheritance is resolved AFTER patches run**, so patches see raw XML where the node is absent. Then `PatchOperationSequence` aborts at the first failure instead of log-and-continue; sibling `PatchOperationFindMod` blocks are unaffected, so the blast radius is exactly "the rest of this sequence".
**Fix:** guard on the container, not the leaf — nest a `PatchOperationConditional` on `…/statBases` whose `<nomatch>` Adds the whole element (`<value><statBases><MeatAmount>350</MeatAmount></statBases></value>`) to `/Defs/ThingDef[defName="DA_Taraal"]`, with the leaf conditional inside `<match>`. Then count the ops in the enclosing sequence: everything after the failure is *untested*, not *fine*.
**Recurs when:** a `<nomatch>` that adds a *child* — it silently assumes the parent exists, which is false on any def that inherits via `ParentName`. The live def dump will not tell you either: it shows post-resolution state and this project's dumper does not serialise `statBases` at all.

---

### 35. Retargeting a gene family is two files, and the old family must stay
**Symptom:** swapping the six `Eyes_<colour>_Feline` genes on `BTD_Hutt` for the `Eyes_<colour>_Reptile` ones looks like a six-line find-and-replace in `HuttEyes_Slitted.xml`.
**Cause:** two patches cooperate. `HuttEyes_RestoreRenderNodes.xml` puts back the `renderNodeProperties` that [LFS] Genes Expanded strips whenever Facial Animation is installed. The live dump shows them **present** on `Eyes_*_Feline` only because our own restore file put them there, and **stripped** on `Eyes_*_Reptile` — so retargeting the assigning file alone hands the xenotype six genes that draw nothing, i.e. Hutts with no eyes. Separately, editing a `XenotypeDef` never rewrites existing pawns: the save held 24 Feline eye genes on already-spawned Hutts plus one on an unrelated pawn, so deleting the old family blinds them on load.
**Fix:** restore **both** families and let the xenotype roll only the new one. Every op is guarded `[not(renderNodeProperties)]`, so the unused half costs nothing on a save with none of those pawns.
**Recurs when:** any xenotype, backstory or gene-roster change — `grep` the `.rws` for the old defNames, and re-read the *unpatched* sibling def, because a repaired state is evidence about your patch, not about the mod.

---

### 36. The comp you are designing a patch around may not exist
**Symptom:** `grep -rln "CompProperties_ShieldBelt" "…/RimWorld/Data"` returns **zero hits** on 1.6 with all DLCs included, while a patch was being scoped around exactly that comp.
**Cause:** `Apparel_ShieldBelt` is a plain `<thingClass>Apparel</thingClass>` and the whole mechanic runs off two stats in `Core/Defs/ThingDefs_Misc/Apparel_Belts.xml`: `<EnergyShieldRechargeRate>0.13</EnergyShieldRechargeRate>` and `<EnergyShieldEnergyMax>1.1</EnergyShieldEnergyMax>`. Any apparel with a non-zero `EnergyShieldEnergyMax` *is* a shield; the break event appears in no def at all and is reachable only by Harmony.
**Fix:** prove the comp exists first — `grep -rln "CompProperties_<Name>" "…/RimWorld/Data"`. Zero hits means stat-driven or hard-coded in the `thingClass`, which changes the work from one XML patch into a patch plus an assembly — and a new C# assembly rides a game load alone while a validated XML patch batches.
**Recurs when:** scoping any mechanic assumed to have an XML surface; find the XML/C# boundary during scoping, not during authoring.

---

### A build-over tier ladder deadlocks if the rungs disagree on terrain affordance
**Symptom:** in a three-tier "build the next tier over the previous one" ladder, tier 1 places fine and tier 2 then refuses to place over it forever — no error, no log line, just a blueprint the game will not accept. XML is valid, every def resolves, textures load, `validate_patch.py` is happy.
**Cause:** RimWorld checks `terrainAffordanceNeeded` against the terrain *under* the cells, and **a floor cannot be built on a cell occupied by an edifice**. The moment tier 1 stands on terrain that does not satisfy tier 2, the terrain can never be upgraded, because the thing blocking the upgrade is the thing being upgraded.
**Fix:** decide before authoring, never after. Either every rung declares the same affordance — WreckedMachines keeps VFE's `FactoryFloor` on all three smelter tiers, making tier 1's placement a map-authoring constraint (lay the floor first, under the wreck) — or the ladder relaxes to the lowest affordance any rung needs, which diverges the def from the donor it copies.
**Recurs when:** copying a donor def to make a derived tier — any field the game evaluates against the cells beneath a building is a ladder invariant, not a per-tier choice. Behaviour fields are free to copy; placement fields bind the whole chain.

---

### Building one thing over another is vanilla in 1.6 (`replaceTags`) — and Replace Stuff forbids our case
**Symptom:** the repair ladder's whole loop is "build the working machine over the wreck", and `DESIGN.md` named **Replace Stuff - Continued** (WS 3526354009, installed) as the compatibility target for it. Nobody had opened the mod.
**Cause:** two things. Its shipped `Source/` shows `NewThingFrame.cs:75` `CanReplace` returning false when `!oldDef.building?.deconstructible`, and `CanReplaceNewThingOverOldThing.cs:17` is a Harmony **postfix** on `GenConstruct.CanReplace` forcing `__result = false` when either side is a non-deconstructible attackable building — overriding cases vanilla would allow. Our wreck was `deconstructible=false` by design. Separately, **1.6 added `replaceTags`, a top-level `ThingDef` field** (sibling of `<building>`, not inside it): Core gives `Stool` `<replaceTags><li>Chair</li></replaceTags>` so it and `DiningChair` build over one another with no mod and no C#.
**Fix:** give every tier the same `replaceTags` entry and keep them deconstructible so the third-party postfix never fires.
**Recurs when:** adopting a dependency for a mechanic — grep `Data/Core/Defs` first, since 1.6 added fields that predate everyone's memory of "how you do this", and read the mod's shipped `Source/` rather than its store page, which describes the happy path and never the guards. This failure prints **no log line at all**, so it costs a full ~25-minute load to find.

---

### 48. "It is placeable" and "it can be removed" are different claims — and the do-not-place twins are one word apart
**Symptom:** planning a salvageable ground-hulk from RimWorld's shipped ruins kit, the obvious picks were the thematically perfect ones — `AncientGravEngine`, `AncientGravReactor`, `AncientTerraformer`, the three 7×7 `Ancient*Vent`s, and BTD's four purpose-made *damaged gravship engines*. **Every one of them refuses deconstruction.** A colonist simply will not take the job; the only removal route is explosives. Eight of them were in my first draft of a "place these" list.
**Cause:** two abstract parents that look identical from a texture folder (`Data/Core/Defs/ThingDefs_Buildings/Buildings_Ancient_Outdoors.xml:4-28`). `AncientBuildingBase` sets `alwaysDeconstructible true`; `NonDeconstructibleAncientBuildingBase` sets `deconstructible false`. Across the active stack **73 defs** are on the second parent. The sharpest instance: **`AncientCryptosleepPod` cannot be deconstructed, while `AncientCryptosleepCasket` is the richest salvage in the whole kit (Steel 180 + Uranium 5).** Same art family, one word apart in the defName.
**Fix:** before designing any economy around shipped props, read `building.deconstructible` from the **live merged dump**, not the XML — mods patch it, and *Vanilla Vehicles Expanded* has already rewritten the entire Core vehicle-wreck set's `costList` in this install. Then apply the second test, which is the one that actually bites: **deconstructible ≠ yields anything.** Of 181 Core+DLC ruins defs, 167 deconstruct, but only **55 have a `costList`**; 33 have `killedLeavings` only, and **89 return nothing either way.** Actual yield is `costList × resourcesFractionWhenDeconstructed` (default 0.5), and `resourcesFractionWhenDeconstructed` is itself patchable — *Salvage Rubble* ships `0.00025` over a `Steel 1000` list to make a huge pile yield a trickle.
**Generalises to:** every "reuse the shipped assets" plan. Placement, removal, and yield are three independent properties and a def can pass any one while failing the others. Two companions found the same day: **a `TerrainDef` can never yield anything on removal** — terrain has no deconstruct-for-resources route at all, so a salvage economy cannot live in a floor no matter what its `costList` says; and for gravships, **`IsSubstructure` reads `HasTag("Substructure")`, NOT the affordance list** — `BTD_QuestSiteSubstructure` grants the `Substructure` *affordance* while omitting the *tag*, so things build on it but it does not connect or count toward capacity. Reading the affordance instead of the tag inverts the answer.
