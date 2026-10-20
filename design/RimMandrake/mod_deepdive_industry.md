# Mod deep dive: industry and salvage (VFE Factory, Better Cremation, Bones)

On 2026-10-10 the owner rejected card C13 in `design/RimMandrake/mod_audit/OWNER_CARDS.md`. He typed: *"These are far too sophisticated of questions to resolve like this. We would need deep dives per mod."*
This document is that deep dive for the three C13 mods. It was done offline: no bridge, no game, no game-code edits and no mod-list changes. It follows the scenario in `mod_audit/SCENARIO_BRIEF.md`:
- a small crew on a cramped ship
- scarcity
- no large-scale automation
- restoring wrecked machines is the Jawa fantasy
- one salvage rule, so rewards never double.

Evidence labels: **MEASURED** means parsed from the artifact named. **RimSage** means read from decompiled 1.6 source. **INFERRED** means reasoned from measured facts. **UNMEASURED** means not established.

## 0. Method and roots

| mod | packageId | on-disk root (only copy; nothing under `…/common/RimWorld/Mods`) | load index in live `ModsConfig.xml` (550 active) |
|---|---|---|---|
| Vanilla Furniture Expanded - Factory | `VanillaExpanded.VFEFactory` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3686924415` | 331 |
| Cremation smelts apparels ("Better Cremation") | `Thumb.BetterCremation` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3212165730` | 94 |
| Rim of Madness - Bones Unofficial Fix | `sihv.rombonesPort` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3252977437` | 257 |

How the roots were found and read:
- **Roots.** All 1,377 installed `About.xml` files in both roots were parsed for `<packageId>`. A first pass missed VFE Factory: its About.xml lists two dependency packageIds before its own, so reading the first `<packageId>` in the file gets the wrong one. The second pass matched on the top-level `<packageId>`.
- **Defs and patches.** A per-mod XML parser honoured each mod's `loadFolders.xml` for v1.6 and counted defs per type and patch operations. VFE Factory's VCE and Odyssey subfolders are included: VCE (`VanillaExpanded.VCookE`) and Odyssey are both active.
- **C#.** All three DLLs were decompiled with `ilspycmd` 8.2. The decompiled copies are at `D:\ClaudeWork\rimmandrake\scratch\dd_ind\{vfef,bc,bones}`.
- **Engine facts** come from RimSage, named where used.
- **Our references.** A tokenising Python sweep covered 6,537 files under `src/`, matching on whole tokens. A sanity probe found `HideDonorSmelter` in 4 files. The sweep was then followed by reading each patch it found.
- **Save.** The canonical save is `canon.yml` `planet.start_savegame` = `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` (17,483,421 bytes, mtime 2026-10-09). It was copied and read with a streaming `iterparse`. Its meta lists 616 mods, including all three of these. Probes: `Steel` appears as stuff on 861 placed things, and 37 `Corpse_Human` things are on map 0.
- **Log.** `Player.log` (session ending 2026-10-10 17:34, 15,117 lines) was read line by line. Probes: 188 lines mention Harmony and 148 contain error words.
- **Cherry Picker.** The live config `Mod_3521312241_Mod_CherryPicker.xml` was parsed. It has 2,133 `<li>` entries (which proves it was read) and cuts nothing from VFE Factory or Bones.

## 1. VFE Factory (`VanillaExpanded.VFEFactory`)

### 1.1 What it adds (MEASURED from its 1.6 load folders)

**159 non-abstract defs.** Runtime implied defs come on top of these (see "Implied defs" below).

- **ProcessDefs (`PipeSystem.ProcessDef`): 100.** PipeSystem belongs to the Vanilla Expanded Framework (VEF), not to this mod. VEF stays installed regardless.
- **ThingDefs: 27.** 24 are buildings and 3 are items.
  - **Basic tier** (research `VFE_BasicFactories`): autofarmer (7×3), automated drill platform, automated smelter, automated biofuel refinery, automated masonry saw, automated mincer, conveyor oven, automated ammunition press, autoloom, conveyor crematorium, factory hopper, factory floor.
  - **Complex tier** (`VFE_ComplexFactories`): automated assembler (5×5, needs 6 spacer components), neutroamine synthesizer, automated alloy forge, automated distillery, medicine granulator, automated machining bay, factory booster, factory heatsink.
  - **Conditional machines**: automated cannery (VCE folder) and automated fishfarm (Odyssey folder).
  - **No research gate**: conveyor, underground conveyor entrance and exit.
  - **Items**: `VFEFactory_MassProducedMeal`, `VFEFactory_ProcessedMince` and `VCE_CannedSoup`.
- **Other defs**: 11 SoundDefs, 6 EffecterDefs, 2 ResearchProjectDefs (Basic 5000, prerequisite Machining; Complex 6000, prerequisites Basic and Fabrication) and the "Vanilla Expanded" research tab.
  - 3 process templates (autoloom, machining, fish) and the `VFEFactory_DrillableMetals` list (Steel, Gold, Silver, Plasteel, Uranium, Jade).
  - The `VFEFactory_HaulFromConveyor` JobDef, the `VFEFactory_FactoryRoom` room role, the `FactoryFloor` terrain affordance, the `VFEF_FactoryFloor` terrain, a ThingCategory, the "Factory" Architect category and 2 mince ThoughtDefs.
- **Implied defs.** A Harmony prefix on `DefGenerator.GenerateImpliedDefs_PreResolve` generates further ProcessDefs at startup:
  - one autoloom process for every apparel with a costStuffCount that the hand-tailoring bench makes
  - one machining process per machining template
  - fishing processes when Odyssey is present.
  - On the 550-mod list this is likely hundreds of generated defs. The count is **UNMEASURED** offline.

**Processes that bear on scarcity** (MEASURED from the ProcessDef XML and the decompiled result workers):

| process | in → out | scenario reading |
|---|---|---|
| `VFEFactory_DigForMetals` (drill platform) | **nothing** → one portion of a random drillable metal. Weight is `deepCommonality`, count is `deepCountPerPortion` (`ResultWorker_Metals`). Vanilla Plasteel has commonality 1 and 10 per portion (RimSage). | Metal and **plasteel from nothing**. Conflicts with scarcity and with the 2026-09-25 ruling that plasteel is never mined. |
| `VFEFactory_DigFor*Chunk` (10 kinds) | nothing → 1 stone chunk / 14,000 ticks | Free stone |
| `VFEFactory_SmeltMetalFromChunk` | 1 stone chunk → 3 steel | **Rock becomes steel**. Our Refurbished smelter tier carries this process (§1.3). |
| `VFEFactory_SmeltApparel` / `SmeltWeapon` (`ResultWorker_Smelt`) | 1 item → **one** material: its stuff (in practice metallic only; the process sets `onlySmeltable`, so non-smeltable stuff such as leather or cloth is refused at the hopper) or its largest non-component cost item, at floor(25%) with a minimum of 1 | A different salvage rule from vanilla's, which returns every smeltable cost entry (see §2.3) |
| `VFEFactory_AlloyPlasteel` | 10 steel + 7 chemfuel + 1 gold → 5 plasteel | The single sanctioned plasteel fabrication route (`canon_materials_design_2026-10-09.md` §3.3). Our `RM_WM_PlasteelAlloying` gates it. |
| `VFEFactory_AlloyGravlite` | 5 plasteel + 25 vacstone blocks → 5 gravlite panels | Bypasses Odyssey's gravtech gate (already flagged in `required_mods.md` "DESIGN TENSION 1") |
| `VFEFactory_AstrofuelFromChemfuel` | 70 chemfuel → 35 `VGE_Astrofuel` | Mirrors VGE's own 2:1 recipe; the intended fuel leash |
| `VFEFactory_MakeChemfuelFromWood` / `FromOrganics` | 50 wood → 25 chemfuel; 30 food → 15 chemfuel | Automates the vanilla refinery's numbers |
| `VFEFactory_CreateObsidian`, `AlloyBronze` | 1 stone chunk → 3 obsidian; 1 chunk + 10 steel → 20 bronze | Chunk upgrading |

**C# (MEASURED, decompiled).**
- `VanillaFurnitureExpandedFactory.dll`: 109,056 bytes, about 7,241 decompiled lines. Harmony id `com.VanillaFurnitureExpandedFactory`.
- Ten Harmony patch classes:
  - `ForbidUtility.IsForbidden` (two overloads)
  - `GenSpawn.Spawn`
  - `ResourceCounter.UpdateResourceCounts`
  - `SelectionDrawer.DrawSelectionBracketFor`
  - `Selector.Deselect`
  - `SteadyEnvironmentEffects.TryDoDeteriorate` (items riding belts still deteriorate)
  - `StoreUtility.IsGoodStoreCell`
  - `DefGenerator.GenerateImpliedDefs_PreResolve` (the implied processes above)
  - `Designator_Place.SelectedUpdate`
- A `[StaticConstructorOnStartup]` class (`Startup`) gives every substructure terrain the `FactoryFloor` affordance, plus Odyssey's `HeavyBridge`. **This is what lets factory machines stand on a gravship deck.** Any replacement must reproduce it.
- **Settings: none of its own.** There is no `ModSettings` class in the DLL (MEASURED). Overclocking is driven by VEF comps (`CompPowerTrader_Overclocked` and the booster/heatsink facilities), not by settings in this mod.

**Its own patches:** two `PatchOperationFindMod` files, Vanilla Chemfuel Expanded and VRE Android.

### 1.2 Cost profile

| measure | value | label |
|---|---|---|
| defs declared | 159 (100 ProcessDefs) plus runtime implied ProcessDefs | MEASURED / implied count UNMEASURED |
| textures | 177 PNG, 13.44 MB on disk; about 179 MB decoded (RGBA × 4/3 mipmaps from PNG headers) | disk MEASURED, decoded INFERRED |
| sound | 11 ogg sustainers and ambiences (about 1.4 MB per registry) | MEASURED count |
| DLL | 1 (109 KB), 10 Harmony patch classes, 1 static ctor class here (the registry's facts table counts 7 static ctors across the assembly) | MEASURED |
| log | 0 errors attributable in the 2026-10-10 session. 11 lines mention it, of which 4 are LoadTracer ctor lines and 2 are a dependency-URL warning raised by the *installed but inactive* "VFE Factory Integrated Rimefeller Recipes" | MEASURED |
| TPS | conveyors tick per item. Per-mod TPS UNMEASURED | UNMEASURED |

### 1.3 How our mods use it (MEASURED by parse, then each file read)

Our source references VFE Factory defNames in 23 files (123 token hits, including docs and tools) and names the packageId in 16 files. The load-bearing references:

- **`mandrake.rm.wreckedmachines`**: hard `modDependency` plus `loadAfter` (`src/RimMandrake/WreckedMachines/About/About.xml`).
  - **Shared parts.** Its four smelter tiers (`RM_WM_AutomatedSmelter_Wrecked/Kludged/Refurbished/Repaired`, `Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml`) are built from VFE Factory parts:
    - the Architect category `VFEFactory_Factories`
    - the room role `VFEFactory_FactoryRoom`
    - the facility links `VFEFactory_Booster` and `VFEFactory_Heatsink`
    - the `VFEFactory_FactoryHopper` linkable
    - the not-working key `VFEFactory_FactoryNotWorking`
    - the donor's process list by defName
  - the `FactoryFloor` terrain affordance (`terrainAffordanceNeeded` on all four tiers).
  - **Processes per tier.** Kludged runs `VFEFactory_SmeltMetalFromSlag/MechSlag/SmeltWeapon`. Refurbished and Repaired add `VFEFactory_SmeltApparel` and `VFEFactory_SmeltMetalFromChunk`, which is the rock-to-steel process.
  - **Patches.**
    - `Patches/WreckedMachines_HideDonorSmelter.xml` (1 op) strips `designationCategory` from `VFEFactory_AutomatedSmelter` (owner ruling 2026-09-16).
    - `Patches/WreckedMachines_AlloyForgeGates.xml` (2 ops) re-gates the alloy forge on `RM_WM_AlloyForgeRestoration` and adds `RM_WM_PlasteelAlloying` to `VFEFactory_AlloyPlasteel`.
    - `Source/WreckedMachinesMod.cs` looks up the donor smelter, the category, the alloy forge, `VFE_ComplexFactories` and `VFEFactory_AlloyPlasteel` by name, with silent-fail lookups.
- **`mandrake.rsw.armoury`**:
  - `Patches/RSW_Smelter_Alloys.xml` adds three alloy processes to the donor smelter and to our three working tiers. It is guarded by a Conditional on `VFEFactory_SmeltMetalFromSlag`.
  - `Patches/RSW_AlloyForge_Durasteel.xml` adds steel + zersium → durasteel to the alloy forge, inside a FindMod guard.
  - `Source/AlloyForge/RSW_AlloyOres.cs` and `RSW_AlloyForgeDurasteel.cs` look up the same defs.
- **`mandrake.rut.researchretag`**: Conditional-guarded retags. `VFE_BasicFactories` becomes Spacer, `VFE_ComplexFactories` becomes Ultra, plus tab assignment (`Patches/RUT_ResearchRetag.xml`, `RUT_ResearchTabAssign.xml`).
- **Tools**: `src/RimMandrake/Utils/rimbench/shipbuild.py` maps the ship build sheet's 18 machine names plus hopper, heatsink and booster onto VFE Factory defNames (lines 265–286).
- **Third-party dependents on the live list**: `groovytaco.beltextractors` and `reel.turretpipeline`. Owner ruling C10 cuts both.

**Finding 1.** WreckedMachines, our restoration ladder, is built from VFE Factory's own parts (category, room role, hopper, facilities, processes, floor affordance), not just next to it. So absorption is a re-basing job, not a delete. §1.6 sizes it.

### 1.4 The canonical save (MEASURED by streaming parse)

- **20 VFE Factory buildings stand on map 0:**
  - `VFEFactory_AutomatedSmelter` ×1 at (138,114)
  - `VFEFactory_AutomatedMachiningBay` ×1 at (206,114)
  - `VFEFactory_MedicineGranulator` ×1 at (201,110)
  - `VFEFactory_FactoryHopper` ×14
  - `VFEFactory_Booster` ×1
  - `VFEFactory_Heatsink` ×2
- **They are aboard the ship (MEASURED).** The ship export `design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml` holds exactly these 20: 14 hoppers, 2 heatsinks, 1 booster, the smelter, the machining bay and the granulator. Their positions (x 134–206, z 103–170) also fall around the `GravEngine` at (171,136).
- **The medicine granulator is a Complex-tier machine** (`VFE_ComplexFactories`), and that research is at 0. So the founding ship already hands over gated automation.
- **No `RM_WM_*` building is placed.** Research progress is 0 for `VFE_BasicFactories`, `VFE_ComplexFactories` and `RM_WM_AutomatedSmelterRestoration`. The VFE Factory items appear only in filters and price history.
- **Finding 2 (an unmigrated pre-ruling leftover).** The ship was exported on 2026-09-12. The owner's 2026-09-16 ruling *"remove the VFE factory, not the manual one"* was then carried out only by hiding the donor smelter from the Architect. The donor smelter is still **placed aboard the ship**, in the one artifact that survives the world remake (gravship, map and founders). It does not go through our wrecked → kludged → refurbished ladder at all. The patch header only anticipated instances that the donor spawns through quests or map generation. Nobody has ruled on this one.
- **If VFE Factory were removed today:**
  - 20 placed things would name an unloaded ThingDef. The precedent is `lumi.doorsexpanded` with placed things, which killed the load on 2026-09-09 (`memory/donor-retirement-mod-check-not-save-check.md`).
  - WreckedMachines would lose its hard dependency, and its tiers' cross-references would fail.
  - Armoury and ResearchRetag would go silent (they are guarded).
  - The ship build sheet would lose 21 name mappings.

### 1.5 Player experience

- **With it (today):**
  - A "Factory" Architect tab with 23 buildable machines and conveyors. The donor smelter is hidden.
  - Bills like "do until X" and overclocking to 500% (more heat and power).
  - Crew labour moves from benches to supervising machines.
  - On a ship with 3–8 crew, this is the design `required_mods.md` §INDUSTRIAL CORE chose on purpose: *"The ship performs routine industrial labor … Losing a production line should feel like losing a ship organ."*
  - It also hands out:
    - metal and plasteel from nothing (the drill)
    - rock-to-steel
    - a second gravlite route
    - mass-produced meals, medicine and components from feedstock
  - Those are exactly the large-scale automation and free-resource routes that `forbidden_mods.md` and the scenario brief exclude.
- **Without it:** vanilla benches and hand labour. The ship's industrial organ, the alloy-forge route that canon materials depends on, and the WreckedMachines ladder are all gone until rebuilt.

### 1.6 Replacement or absorption

- **What we would port:**
  - Machine ThingDefs on VEF PipeSystem (XML only; the comps are VEF's)
  - our own ProcessDefs, written with our numbers
  - a hopper building (`Building_FactoryHopper`, small C#)
  - the substructure `FactoryFloor` affordance (a 20-line static ctor)
  - `ResultWorker_Smelt` (about 40 lines), if we keep stuff-returning smelting
  - our own Architect category and room role.
- **What we would not port:**
  - conveyors and underground conveyors (automation; C10's direction)
  - the autofarmer
  - the drill
  - implied autoloom and machining processes.
- **Licence and source.**
  - No LICENSE file in the workshop folder (MEASURED) and no public source located (UNMEASURED; the registry says "steam-only").
  - VEF itself is public (`github.com/Vanilla-Expanded/VanillaExpandedFramework`, named in the About.xml).
  - So we re-author rather than copy.
  - Art is ours regardless under the 2026-10-05 "no donor art kept" ruling. WreckedMachines already ships 15 of our textures for the smelter tiers.
- **Effort:**
  - **S** per machine to give it a WreckedMachines ladder that still uses VFE Factory's ProcessDefs (XML, following the smelter precedent).
  - **M** to make WreckedMachines independent of VFE Factory's category, room role, hopper and facilities.
  - **L** for a full absorption that removes VFE Factory. That includes migrating the ship's placed machines, which needs ship-layout and save work.

### 1.7 Options

| option | what happens | gains | costs |
|---|---|---|---|
| **A. Keep as is** | nothing | zero work | Free-resource processes stay. The ruling-contradicting smelter stays aboard. Donor art (about 179 MB decoded) stays. |
| **B. Keep as engine; restoration gates the player** | Hide every VFE Factory machine from the Architect. Re-expose only the machines the ship needs, each as a WreckedMachines ladder (found wrecked, studied, restored). Cut the free-resource processes (`DigForMetals`, the `DigFor*Chunk` set, `SmeltMetalFromChunk`, `CreateObsidian`, `AlloyBronze`). No conveyors. | Matches C13 rec 1 and C10. Restoring is the gameplay. One XML pattern already proven. | About S per machine. VFE Factory stays a dependency. Its 10 Harmony patches and textures still load. |
| **C. Absorb fully** | B, then re-base WreckedMachines on our own category, room role, hopper and ProcessDefs, migrate the ship's 20 placed things, and untick VFE Factory | No donor code, art or implied defs. We own every number. | L. Needs the ship-layout migration and a save proof before untick. |
| **D. Remove now** | untick | none | Breaks WreckedMachines, the ship and the save. Rejected. |

**Recommendation: B now, with C as the end state.** Before anything else, rule on the donor smelter aboard the ship (Finding 2).

## 2. Better Cremation (`Thumb.BetterCremation`)

### 2.1 What it adds (MEASURED, decompiled)

- **Content:**
  - 0 defs and 0 patches, no textures beyond `Preview.png`
  - `BetterCremation.dll`, 6,144 bytes, in folders for 1.5 and 1.6
  - no settings
  - Harmony id `"TurretSharpResistance"`, an apparent copy-paste from another mod.
- **One Harmony postfix**, on `GenRecipe.MakeRecipeProducts`:
  - If `recipeDef.defName == "CremateCorpse"` and the first ingredient is a `Corpse`, then for every **worn apparel** and every **inventory item** of the inner pawn, it calls `Thing.SmeltProducts(1f)`.
  - It places each product at the **worker's** position.
- **The salvage formula** (`Thing.SmeltProducts`, RimSage):
  - 25% (`RoundRandom`) of each non-intricate, smeltable entry in the item's adjusted cost list, plus `def.smeltProducts`.
  - The efficiency argument is ignored for the cost-list part.
  - Components are intricate and never return.
- **Vanilla baseline (RimSage, `CremateCorpse`):**
  - `autoStripCorpses=false`, so cremating destroys the corpse with its apparel and inventory.
  - Vanilla returns the same 25% only if a pawn first strips the corpse and smelts each piece at an electric smelter.
- **So the mod:**
  - **removes** the strip, haul and smelt labour for apparel
  - **adds** metal back from inventory items, which vanilla destroys.
  - It does not raise the per-item rate.
- **Limits of the mod** (RimSage):
  - `SmeltProducts` ignores `efficiency` entirely.
  - The postfix skips the smelter's `Smeltable` and relic gates.
  - Raw resources in the inventory (steel, silver, components) have no cost list, so they return nothing. "Metal back from inventory" applies only to crafted items.
  - Equipped weapons (`pawn.equipment`) are not handled.
  - Ordering is safe: products are built before ingredients are consumed (`Toils_Recipe`).
- It does not touch VFE Factory's conveyor crematorium. That machine runs ProcessDefs (`VFEFactory_CremateHumanlike`, `VFEFactory_BurnApparel`, …) with no products, not the `CremateCorpse` recipe.

### 2.2 How our mods interact (MEASURED)

- **References:** zero in our source. The only hits are 5 historical northstar JSON snapshots in `src/RimMandrake/GimmeSomeSlack/northstar/`, which are mod-list captures.
- **Harmony overlap:** `src/RimMandrake/LuminousPigment/Source/GenRecipePatch.cs` also postfixes `MakeRecipeProducts`, as a pass-through enumerator. Better Cremation's postfix reads `__args` and places things directly, so the two coexist (INFERRED from both bodies).
- **The scavenge design.** `jawa_scavenge_system_design_2026-10-03.md` lists Better Cremation as a "soft" conflict. That design (a startup conflict check) is **not built**: no class or def implements it under `src/` (MEASURED by search).

### 2.3 The real "one salvage rule" problem (INFERRED from measured code)

One worn steel-and-cloth apparel can be salvaged three ways today, and each follows a different rule:

1. **Strip it and smelt it at the vanilla electric smelter:** 25% of the smeltable cost list (metal only).
2. **Smelt it on our Refurbished or Repaired smelter tier** (`VFEFactory_SmeltApparel` through `ResultWorker_Smelt`): **one** material, either its smeltable stuff or its largest non-component cost, at floor(25%) with a minimum of 1. Items with non-smeltable stuff are refused (`onlySmeltable`). **Weapons diverge the same way from the Kludged tier upward** (`VFEFactory_SmeltWeapon`), and the Repaired tier also adds `VFEFactory_SmeltMechanoid`.
3. **Cremate the corpse unstripped (Better Cremation):** rule 1, applied without labour, plus the corpse's inventory.

No path pays twice for one item, so rewards do not literally double. But the yield depends on which building you use, and that is what "one salvage rule" exists to stop.

### 2.4 Save, cost and removal

- **Save.** It owns no defs, so the save holds only its `modIds` entry (MEASURED). There are no placed things, bills or research. Removal is safe.
- **Costs:**
  - 0.08 MB on disk
  - one Harmony postfix on a hot-ish path (every recipe completion, rejected in one string compare)
  - 1 `Player.log` line (its mod-list entry), 0 errors.
- **Maintenance risk:** no source and no licence, so it cannot be patched if 1.7 breaks it.

### 2.5 Options

| option | gains | costs |
|---|---|---|
| **A. Keep** | Crematorium salvage stays convenient | A fourth, unruled salvage path. Unmaintainable. |
| **B. Retire now; fold the behaviour into our own salvage rule** | Zero save risk (MEASURED). One rule to tune. | Until our rule ships, cremation returns nothing, as in vanilla. Strip-and-smelt still works. |
| **C. Re-implement it as part of the rule** | Same convenience, our yields | About S: roughly 40 lines plus a settings toggle |

**Recommendation: B.** Retire it at the next list edit, and write the single salvage-yield rule so apparel returns the same thing wherever it is salvaged. If the owner wants "cremate without stripping" as a convenience, it comes back as a toggle of that rule (C).

## 3. Bones (`sihv.rombonesPort`)

### 3.1 What it adds (MEASURED)

**30 defs.**

- **ThingDefs: 11.**
  - `BoneItem` is **Woody stuff, commonality 1**, so anything wood-stuffed can be built from bone.
  - `Bonecrete` and `BoneChina` are Stony; `BonePlastic` ("calcium polymer") is Metallic. All three have commonality 0.
  - `ROMB_Marrow` and `ROMB_Gelatin`.
  - Buildings: `BoneWall`, `BoneChair`, `BoneThrone`.
  - Apparel: `ROMB_Apparel_SkullMask` and `Sihv_Apparel_BoneArmor` (sharp 0.45).
- **RecipeDefs: 8**, listed in the table below.
- **Other defs:** 5 bone floors, 3 dropdown groups, and 2 research projects:
  - `BoneRefine`: 1000, Industrial, prerequisite BiofuelRefining
  - `BoneRefineII`: 1500, Spacer, prerequisites MicroelectronicsBasics and BoneRefine.
- **StatDef `BoneAmount`:** default 50, scaled by body size and by natural coverage of body parts that are not missing, then put through a post-curve.

**C# (decompiled `BoneMod.dll`, 7,168 bytes, Harmony `rimworld.Sihv.bonemod`):**
- A postfix on `Pawn.ButcherProducts` adds `RoundRandom(BoneAmount × boneFactor × efficiency)` `BoneItem`, and only when the meat amount is above 1.
- A postfix on `Corpse.SpecialDisplayStats` shows the bone amount.
- **Setting:** "Multiplier" `boneFactor`, slider 0–10, **default 1**.

**Patches (22 top-level operations; FindMod blocks nest more):**

| target | change |
|---|---|
| BiofuelRefinery | + `MakeBonecrete` (70 bone → 50), `MakeBonePlastic` (40 bone → 60 polymer), **`MakeBonePlasteel` (40 polymer + 40 steel → 60 plasteel, BoneRefineII)**, **`Make_ChemfuelFromBone` (70 bone → 35 chemfuel, 200 work, BoneRefine)** |
| ElectricCrematorium, Campfire | + `MakeBoneChina` (20 → 20) |
| TableButcher | + `MakeMarrowFromBone` (40 bone → 10 marrow) |
| ElectricStove, FueledStove | + `MakeGelatinFromMarrow` |
| `ButcherCorpseRotten` | rotten corpse → 15 bone at the butcher spot or table |
| vanilla `Pila`, `Bow_Short`, `Bow_Great` | fixed cost list → **Woody-stuffed** (70/30/50), so bows are made of bone or any wood |
| `LostTribe` scenario | stuff set to WoodLog |
| insects (`BaseInsect`), Centipede, Scyther, Megafauna mod insects, Alpha Animals boneless list | `BoneAmount` 0 |
| Royalty | bone chair and skull throne become thrones |
| Yayo's Combat 3 | primitive ammo accepts bone |
| Odyssey | BoneWall linking |

**Finding 3: two fuel and plasteel routes that nobody has ruled on.**
- The body-size-1 default is about 50 bones (INFERRED from the stat). So every hunt becomes chemfuel (70 bone → 35 chemfuel, 200 work).
- After `BoneRefine` and `BoneRefineII` (which also needs `MicroelectronicsBasics`), it also becomes **plasteel** (40 bone → 60 polymer; 40 polymer + 40 steel → 60 plasteel, 6000 work). That is about 27 bone + 40 steel → 60 plasteel: in effect a steel-to-plasteel upgrader.
- `canon_materials_design_2026-10-09.md` allows plasteel only from the alloy forge (§3.3), and `canon_metal_fabrication_2026-10-09.md` does not list either bone route.
- VFE Factory's drill-for-metals plasteel (§1.1) is missing from that census too.

### 3.2 How our mods interact (MEASURED)

**21 files** in our source name its defs (2,658 token hits). Almost all of the hits are in one generated file.

- **`src/RimUtinni/Doctrine/Patches/MegafaunaYield.xml`** is generated by `Source/gen_megafauna_yield.py`. It has 31 `PatchOperationFindMod` blocks, one per donor mod. Inside them are **366 Conditional/Replace pairs on `BoneAmount`**, each with a `nomatch` **Add** of `<BoneAmount>` into the race's `statBases`. **None of them checks that Bones is loaded.** `MegafaunaYield_OwnedPorts.xml` and `MegafaunaYield_OwnedPorts_Warscar.xml` do the same.
- `src/RimUtinni/GreentideRaidAnt/Defs/ThingDefs_Races/RUT_Race_GreentideAnt.xml:20` writes `<BoneAmount>100</BoneAmount>` **with no `MayRequire`**.
- `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_Maguana.xml:39` does it correctly (`MayRequire="sihv.rombonesPort"`).
- `mandrake.rut.researchretag` retags `BoneRefine` and `BoneRefineII` (Conditional-guarded).
- `src/RimMandrake/HugeThings/Source/Titanic/Wake/Patch_ButcherYieldCurve.cs` prefixes `Pawn.ButcherProducts` and scales `efficiency`. Bones multiplies by efficiency, so bone yield follows our Titanic yield curve. The two are compatible (INFERRED).

**Finding 4: latent load-error hygiene, not a hard blocker.**
- `StatModifier.LoadDataFromXmlCustom` registers a cross-reference for `stat` by node name (RimSage).
- With Bones absent, every unguarded `<BoneAmount>` produces a "could not resolve cross-reference" load error. Each one also leaves a `StatModifier` with `stat == null` in that race's `statBases`. The engine has no pass that prunes these (RimSage search found none). **The load completes**: `WantedRefForObject.TryResolve` logs and continues, and `ThingDef.ConfigErrors` tolerates a null stat.
- How many errors: one per race actually present among the 31 donor blocks, plus the owned ports, plus the Greentide ant. The upper bound is 374 (366 + 7 ports + 1). The live count is UNMEASURED.
- Whether a null-stat entry also causes NREs (for example in info cards) is UNMEASURED.

### 3.3 The canonical save (MEASURED by streaming parse)

- **Bone china structures:** 204 placed things are **stuffed `BoneChina`**.
  - 195 walls (faction `AncientsHostile`) and 9 doors (no faction).
  - They are on map 0 at x 195–228, z 189–214, which is outside the ship.
  - 203 matching entries sit in 8 `layoutStructureSketches`. The ancient-structure generator picked the commonality-0 Stony stuff.
- **Bone items:** 1 `BoneItem` in a `GS_Gaffi`'s inventory, `BoneItem` as stuff on 1 remembered weapon and on 1 NPC contract.
- **Research:** `BoneRefine` and `BoneRefineII` are at 0.
- **Bone floors** in the terrain grid: **UNMEASURED**. The grid is shortHash-encoded and needs the save's own mod-set hash table (`savemap.py`).
- **If Bones is removed:** `Thing.ExposeData` (RimSage) logs "Could not load reference to …" and then, at PostLoadInit, "made from stuff but has no stuff set", and sets a default stuff. So the 204 walls and doors would survive in a different material, at about 2 errors per thing plus whatever the 203 sketch entries produce. **Stability is UNMEASURED.** The `lumi.doorsexpanded` precedent reached Playing and then died with no trace, so prove it on a save copy first. The single inventory `BoneItem` drops out with a load error.

### 3.4 Cost profile

| measure | value | label |
|---|---|---|
| defs | 30, plus 22 top-level patch ops (the registry counts 126 nested ops, 75 into Alpha Animals) | MEASURED |
| textures | 72 PNG, 12.61 MB on disk, about 161 MB decoded | disk MEASURED, decoded INFERRED |
| DLL | 7 KB, 2 Harmony postfixes, 1 static ctor | MEASURED |
| log | 1 error, `[Def Error]: BoneWall` "Parsed 0.3 as int". The 0.3 is not in Bones' own XML, so another mod's patch writes it (source UNMEASURED). Also 1 MeleeAnim "missing tweak" line. | MEASURED |
| licence | **MIT** ("Copyright (c) 2018 Rim of Madness Team", `LICENSE` in the root). Code and defs can be absorbed. | MEASURED |

### 3.5 Player experience

- **With it:**
  - Butchering yields bone.
  - Bone is a Woody stuff on a **desert world**, where wood is the scarce Woody material.
  - So bone walls, furniture and bows are a real and fitting option. It suits the scavenger and lore register (bone as building stock).
  - It also makes each hunt a fuel source and, later, a plasteel source (Finding 3).
- **Without it:** carcasses give meat and leather only. Woody stuff comes only from wood. The 204 ancient walls change material.

### 3.6 Replacement or absorption

- **A lean `RM_` port:**
  - an `RM_Bone` Woody stuff
  - the `BoneAmount` stat
  - the ButcherProducts postfix, with the meat > 1 gate and a settings multiplier
  - bone walls and floors, and perhaps one piece of furniture
  - our art (a few textures, not 72).
- **Leave out:** the chemfuel, polymer and plasteel chain, marrow and gelatin, the throne, and the bow restuffing.
- **Effort: S–M.** The MIT licence permits reuse of code and defs.
- **Migration:** point `MegafaunaYield` and the owned ports at the new stat. Re-stuff the 204 ancient walls, or accept the default-stuff fallback, since the world remake regenerates that map anyway (`memory/world-remake-is-the-last-step.md`).

### 3.7 Options

| option | gains | costs |
|---|---|---|
| **A. Keep as is** | none | Fuel and plasteel routes. 161 MB of donor art. |
| **B. Keep; cut the fuel and plasteel recipes now** (Cherry Picker or a patch on `Make_ChemfuelFromBone` and `MakeBonePlasteel`, perhaps also `MakeBonePlastic`) | Closes Finding 3 today, with no code | Donor art and dependency stay |
| **C. Lean port to `RM_` (§3.6), then retire** | Bone as desert building stock, our art, our numbers | S–M. The latent defect must be fixed first. |
| **D. Drop the bone economy entirely** | Less content to own | Lose a fitting desert material. Still needs the latent defect fixed and the ancient walls dealt with. |

**Recommendation:**
1. **Do B now.**
2. **Fix Finding 4 regardless.** Gate every `BoneAmount` write on the mod or on its port.
3. **Then let the owner choose C or D.** The deep dive leans to **C**: bone as a Woody stuff on a treeless world fits the scenario better than C13's default "drop".

## 4. Recommendations and tickets

| mod | recommendation | biggest risk |
|---|---|---|
| VFE Factory | **Keep as the engine. Restoration gates every machine; cut the free-resource processes; absorb later** (B → C). | Removal today breaks WreckedMachines and leaves 20 placed machines aboard the ship. The donor smelter the owner ruled out is still placed aboard. |
| Better Cremation | **Retire now. Fold it into one salvage-yield rule** (B, optionally C). | Low. There are three different apparel-salvage rules today, not double rewards. |
| Bones | **Cut the fuel and plasteel recipes now; fix the BoneAmount guards; then port lean to `RM_` or drop** (B → C/D). | Bone is a hidden chemfuel source and a steel-to-plasteel upgrader today. Removal brings up to 374 red cross-reference errors plus about 408 save errors; that load stability is unproven. |

Tickets (names passed `rimflow namecheck`; **not filed**):

- `VFEF_PROCESSES_CULL_FREE_RESOURCES`: remove `VFEFactory_DigForMetals`, the `DigFor*Chunk` set, `SmeltMetalFromChunk` (including from our Refurbished and Repaired tiers), `CreateObsidian` and `AlloyBronze`, and gate `AlloyGravlite` behind the gravtech research. Feed the result into `canon_metal_fabrication_2026-10-09.md`.
- `SHIP_DONOR_SMELTER_JUDGE_AGAINST_RULING`: needs the owner. Should the placed `VFEFactory_AutomatedSmelter` aboard The Utinni become an `RM_WM_AutomatedSmelter_*` tier, and which one?
- `SHIP_FACTORY_REDESIGN_AS_WRECKED_LADDER`: hide every VFE Factory buildable. The ship carries a smelter, a machining bay and a medicine granulator; those three are migrations. The alloy forge and biofuel refinery would be new ladders, not migrations. Follow the smelter precedent. No conveyors.
- `WRECKEDMACHINES_UNTANGLE_FROM_VFEF_CATEGORY`: give WreckedMachines its own Architect category, room role, hopper and facility defs, and the substructure `FactoryFloor` affordance, so VFE Factory becomes swappable.
- `VFEF_REMOVAL_PROVE_ON_SAVE_COPY`: the end-state gate. Migrate the 20 placed things in a save copy and in the ship layout, untick, and load clean before retiring.
- `CREMATION_SALVAGE_ONE_RULE`: one salvage-yield function shared by the smelter tiers, the crematorium and scavenging, so an apparel returns the same thing on every path.
- `BETTER_CREMATION_RETIRE_AFTER_RULE`: untick `Thumb.BetterCremation`. The save has no refs (MEASURED). It can go before the rule ships if the owner accepts vanilla cremation meanwhile.
- `BONE_RECIPES_CULL_FUEL_AND_PLASTEEL`: cut `Make_ChemfuelFromBone` and `MakeBonePlasteel`, and judge `MakeBonePlastic`.
- `MEGAFAUNA_YIELD_HARDEN_BONEAMOUNT_GUARD`: make `gen_megafauna_yield.py` emit `BoneAmount` writes only under a Bones (or port) FindMod. Add `MayRequire` in `RUT_Race_GreentideAnt.xml`. Re-run the generator.
- `BONE_ECONOMY_DECIDE_PORT_OR_DROP`: needs the owner. Port lean to `RM_` (desert building stock) or drop.
- `BONES_MOD_RETIRE_WITH_UNHOOK`: after the decision, port or unhook, prove the load on a save copy, then untick.
- `ANCIENT_BONECHINA_WALLS_MIGRATE_TO_OUR_STONE`: decide the stuff for the 204 ancient walls and doors, or accept the default-stuff fallback until the remake.

## 5. Review disposition

A fresh-context Opus reviewer with RimSage access reviewed the first draft (`4f9e2cac6`) adversarially. It confirmed the counts, the save facts, the recipe numbers and the Harmony and ctor inventory. Its findings and what was done with each:

1. **WRONG, fixed in §1.1 and §2.3.** `ResultWorker_Smelt` does not turn leather or cloth back into leather or cloth. `onlySmeltable` refuses non-smeltable stuff at the hopper. The worker returns one material at floor(25%), minimum 1.
2. **MISSING, fixed in §2.3.** Weapons follow the same divergent rule from the Kludged tier upward, and the Repaired tier also smelts mechanoids.
3. **OVERSTATED, fixed in Finding 4 and §4.** The unguarded `BoneAmount` writes produce up to 374 load errors and null-stat entries, but the load completes. Hygiene, not a hard blocker.
4. **OVERSTATED, fixed in §3.3.** Missing-stuff things log about 2 errors each, plus the sketch entries. Load stability is now marked UNMEASURED and needs a save-copy proof.
5. **OVERSTATED, fixed in Finding 2.** The placement predates the ruling (ship export 2026-09-12). The 20 things are now MEASURED aboard from the export, not inferred from coordinates.
6. **WRONG, fixed in the ticket.** The ship carries a smelter, a machining bay and a medicine granulator. It carries no alloy forge and no biofuel refinery.
7. **MISSING, added.** The Complex-tier granulator is aboard with its research at 0. Our tiers also depend on VFE Factory's `FactoryFloor` affordance.
8. **NIT, added to §2.1.** The limits of Better Cremation.
9. **NIT, added to Finding 3.** The `MicroelectronicsBasics` prerequisite, and the steel-to-plasteel upgrader framing.

All nine were accepted. None was rejected.
