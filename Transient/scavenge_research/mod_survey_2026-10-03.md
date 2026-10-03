# Salvage/recycle/repair mod survey 2026-10-03

## 1. Sweep method and sanity probe
Script: scratchpad sweep.py. Scanned **1413** About.xml files (142 local Mods + 1272 workshop dirs, both roots). Match on `<name>`+`<description>`, keywords recycl|salvag|scrap|reclaim|repair|disassembl|dismantl|deconstruct|smelt|junk|scaveng|wreck|components|mend|refurbish. Sanity probe: "gravship" matches **42** mods (instrument can see). 132 raw hits, 74 active per ModsConfig.xml (ElementTree). Most hits are noise ("mend" matches "recommend", "components" matches boilerplate); the relevant ones are curated in section 2. Activity is by packageId, case-insensitive. Source = reading shipped `1.6/Defs` and `Source/` where present; DLL-only mods (Scavenging) are read from defs only (no decompile attempted).

## 2. Hits
A = active in current ModsConfig, - = installed, inactive. Workshop id = folder name under workshop/content/294100.

| act | packageId | name | id | note |
|---|---|---|---|---|
| A || Mlie.RecycleThis | Recycle This (Continued) | 3253550009 | click-to-recycle, own WorkType |
| - || sneaks.recycle | Recycle 1.5 | 1534883539 | older recycle, same niche |
| - || SoulRetextured.RecycleThis | Retextured! Recycle This | 2978527594 | texture patch for Recycle This |
| - || arvkus.simplerecycling | Simple Apparel Recycling | 3239309389 | C# yield postfix, durability scaling |
| - || VanillaExpanded.Recycling | Vanilla Recycling Expanded | 3155781848 | trash/chempack chains, PipeSystem processes |
| - || Romyashi.Scavenging | Scavenging | 3108829323 | WorkType + scavenging spot, DLL only |
| A || moja.salvagerubble | Salvage Rubble | 3529058623 | rubble deconstruct yields via resourcesFractionWhenDeconstructed |
| - || proxyer.dismantleancientjunk | Dismantle Ancient Junk | 2871064871 | allows dismantling ancient junk |
| A || Meteores.AncientUrbanRuinsAllDeconstructible.AURAD | Ancient Ruins All Deconstructible | 3361061429 | ruins deconstruct |
| A || Meteores.AncientUrbanRuinsVanillaLoot.AURVL | Ancient Urban Ruins Hit Point | 3446989523 | ruin loot patch |
| - || Og.Repair.Your.Gear | [Og] Repair Your Gear | 3513376486 | pawn repairs HP of apparel/weapons with materials, C# |
| - || SM.MedievalRepair | Medieval Repair | 2955709750 | sound/effects only, ignore |
| - || gunseeker.repairstation | Repair Station | 3534893110 | powered building repair radius |
| - || automatic.autocleaner | Autocleaner | 2051042827 | robot, repair needs components |
| - || futurplanet.disassemblemechanoid | Disassemble Mechanoid | 3191640281 | mass-based loot pool postfix |
| - || xelnigma.mechanoidslagtoplasteel | Mechanoid slag to Plasteel | 3552644190 | smelt slag recipe |
| A || Hol.SmeltPatch | Smelt More Stuff | 2347285971 | adds smeltable items |
| A || Thumb.BetterCremation | Cremation smelts apparels | 3212165730 | |
| A || Memegoddess.ReplaceStuff | Replace Stuff - Continued | 3526354009 | replace-in-place, deconstruct refund |
| - || Mlie.SmarterDeconstructionAndMining | (Smarter Deconstruction and Mining) | 3261302741 | roof checks only, not a salvage system |
| - || OK.ScrapTek | Oktober's Scrap-Tek | 3122686960 | slag to scrap items |
| - || mosi.RebalancedAncientJunk | Rebalanced Ancient Junk | 3336109612 | |
| - || twistedpacifist.ReasonableComponents | Reasonable Components | 1542915888 | component economy |
| A || Teiwaz.TAAJG | Traders Accept All Junk Gear | 3729570505 | sell-side |
| A || Teiwaz.TACAC | Traders Accept Chunks & Corpses | 3756658373 | sell-side |
| A || Dubwise.DubsRimkit | Dubs Rimkit | 832333531 | workbench/repair-ish components |
| A || amegakull.SCVRole | Ideology Scavenger Role | 3565039115 | meme role, flavor |
| - || Farxmai2.VanillaDeconstructableVehicles | VVE Deconstructable Vehicles Junk | 3108171008 | |
| - || Woolstrand.RealRuins | Real Ruins | 1552146295 | ruin scavenge sites |
| A || mandrake.rm.wreckedmachines | Wrecked Machines | local | ours: wreck + scaveng + smelt |
| A || mandrake.rut.droidrepairjobs | Droid Repair Jobs | local | ours |
| - || mandrake.rut.assailantsalvage | Assailant Salvage | local | ours |
| - || mandrake.rut.atlas | Scavenger's Atlas | local | ours |
| A || mandrake.rut.scavengerevents | Jawa Scavenger Events | local | ours |
| A || mandrake.rsw.gizkastowaway | Gizka Stowaway | local | ours |

Active flags re-derived from ModsConfig.xml per packageId (case-insensitive). Ours are not incompatibility targets. Raw hit list kept in scratchpad only.

## 3. Mechanisms mined
All read from shipped 1.6 defs/Source unless noted. None of the surveyed mods has appraisal/identification, a salvage skill, or droid helpers specific to salvage.

**Recycle This (Mlie.RecycleThis, 3253550009; DLL only, README + defs read)**
- Orders, not bills: two designations ("Destroy", "Recycle") on selected weapons/apparel; pawns haul to nearest smelter/campfire/workbench. Removes the bill-micromanagement of post-raid cleanup.
- Gets its OWN `WorkTypeDef` (`RecycleThis_Recycle`, pawnLabel "Recycler", relevantSkills = Crafting, naturalPriority 431, workTags Commoner/ManualSkilled) with two `WorkGiverDef`s (`canBeDoneByMechs=true`!) and JobDefs carrying a `ModExtension` (`RecycleSpeed 1600`, `DestroySpeed 200`) for speed tuning. Pattern: new WorkType over existing skill, no SkillDef.
- Yield ~25% of recipe (vanilla smelt values); option to withhold components/complex items.
- README: "load after HAR race mods" (it enumerates apparel via race-aware defs).

**Simple Apparel Recycling (arvkus.simplerecycling, 3239309389; full source)**
- Plain `RecipeDef` at tailoring benches, `workSkill Crafting`, `specialProducts Smelted`; ingredients = Apparel category.
- Clever bit: Harmony Postfix on `GenRecipe.MakeRecipeProducts`, matched by recipe defName; yield = `CostListAdjusted()` x `efficiency` setting x (HitPoints/MaxHitPoints if durability setting on); `intricate` materials (components) always skipped; smeltable apparel falls through to vanilla smelt. Gives condition-scaled yield and a slider in settings in about 20 lines. Directly reusable for our yield function (add skill + quality terms).

**Vanilla Recycling Expanded (VanillaExpanded.Recycling, 3155781848; defs + source)**
- Item-chain design: junk -> trash -> trashbricks, wastepack -> reactive chempack (+ reclaimed biopack byproduct) -> chemfuel, via ordinary RecipeDefs at a CraftingSpot (low tier, manual labour, workSkill Crafting, GeneralLaborSpeed) and `PipeSystem.ProcessDef` slow passive building processes (60000 ticks) with multiple output cells (`outputCellOffset`). `TerrainConversionsDef` turns trash into floors. Research gate (`VRecyclingE_BasicRecycling`) and `constructionSkillPrerequisite` 4-8 on the machines (skill as BUILD gate).
- Idea: byproduct-in-recipe (reclaimed X) and slow passive "processing vat" for bulk scrap.

**Scavenging (Romyashi.Scavenging, 3108829323; defs, DLL not decompiled)**
- A placed 1x1 "scavenging spot" building (`Romy_ScavengingSpot`) with `ScavengableTerrainPlaceWorker` (terrain-gated placement), interaction cell, `CompProperties_Scavenging`, own WorkType `RomyScavenging` (alwaysStartActive false, no relevantSkills, mech-capable false). "chance to find something is not 100%". Per-spot comp rolls loot; no skill involvement. Good template for a "pick-over spot" at the ship.

**Salvage Rubble (moja.salvagerubble, 3529058623)**
- Pure data: rubble (Odyssey) deconstruct yields steel common, wood rare, components very rare, gold ultra rare, plasteel extremely rare via `resourcesFractionWhenDeconstructed`, with cost values scaled to huge integers (steel 1000) so fractions resolve fine-grained. Author notes future Construction-skill scaling. Trick to steal: integer-inflation of costs for rarity tables with no C#.

**Disassemble Mechanoid (futurplanet.disassemblemechanoid, 3191640281; full source)**
- Postfix on `GenRecipe.MakeRecipeProducts` for one recipe; `ItemPool.CustomDissasembleLoot((int)BaseMass)` rolls a weighted pool scaled by body mass (55% steel/slag/wastepack, 25% chemfuel/plasteel, 13% component/uranium, 7% gold/advanced component/subcore/VFE mech component). `CheckForMods` swaps in mod items. Weighted pool by source mass/tier: ideal for wreck-class appraisal.

**[Og] Repair Your Gear (Og.Repair.Your.Gear, 3513376486; full source ~720 lines)**
- WorkGiver finds worn apparel/weapons under `repairBelow`% HP; JobDriver repairs in HP-per-material chunks (`HpPerRepair = 100*MaxHP/(repairNum*fullRepairCost)`), `freePercentage` repairs free below a threshold, material pulled from cost list (`useMaterial`), `limitTech`, float-menu entry. No skill scaling at all (workSkill unused), so a Salvaging/Crafting skill term is open space.

**Others**: Repair Station (power building heals buildings in radius, stackable); Autocleaner (robot disabled until repaired with components); Dismantle Ancient Junk / Ancient Ruins All Deconstructible (flip `building.isDeconstructible`-style flags and leavings on ruin defs so ruins give yields); Smarter Deconstruction (roof-collapse guard, Harmony, settings toggles); Scrap-Tek (slag -> "scrap" tier item feeding low-tech recipes; a new material tier rather than a skill); Traders Accept All Junk Gear (sell-side: salvage value realised by trade).

## 4. Mods adding a SkillDef
**MEASURED: zero installed mods define a `<SkillDef>`** in any Defs folder across both roots (python walk of every `Defs` path, 1413 mod dirs, no match; local Mods root also zero by grep). A separate whole-tree grep for `<SkillDef` found only a Keyed translation file (workshop 2978572782) and was still running at write time; it is not a def. Instrument check: the same walk ran clean (exit 0), but it has no positive control, so treat as strong-but-not-proven. Consequence: there is no installed precedent for UI, balance, or compat handling of a new skill. Every salvage mod surveyed uses an existing skill (Crafting, Construction as a build gate) plus a custom WorkType. Feasibility lead: vanilla SkillDef is data-driven (passion, learn rate, WorkType `relevantSkills`, backstory skill gains), so the real risks are compat (every backstory/xenotype/trait mod that enumerates SkillDefs, pawn-gen balance, UI tab width) not engine capability; Vanilla Skills Expanded (VSE) is the known mod that adds skills (UNVERIFIED, not installed) and should be a lead for a Steam read.

## 5. Leads not installed (UNVERIFIED)
From memory, flagged UNVERIFIED, none checked against the install: Vanilla Expanded "Recycling" is installed (above). Possible others: Recycle It / Smelt Everything style mods, Mending/"Auto Repair" mods (apparel mend jobs), Dubs Skylights-style "Better Repair", Pharmacist-adjacent "Dismantle Gear for Parts", Combat Extended Salvage Parts, RimFactory "Scrap Recycler", Rimsenal recycling, "Mechanoid Salvage" style butchering mods, "Weapon Condition Repair". Do not cite names without a re-sweep (name/description scan with sanity probe) or a Steam search; the installed-survey above is the only measured data.

## 6. Steal list (ranked)
1. **Yield postfix on `GenRecipe.MakeRecipeProducts` keyed by recipe defName** (Simple Apparel Recycling): `CostListAdjusted() x efficiency x HP/MaxHP`, skipping `intricate`. Our appraisal/condition-scaled yield, plus a Salvaging skill term and a quality term. Smallest, proven.
2. **New WorkType over an existing skill, plus orders instead of bills** (Recycle This): designate-and-forget salvage, own WorkTypeDef with `relevantSkills`, WorkGivers with `canBeDoneByMechs=true` (droid helpers for free), JobDef ModExtension for speed constants. No mod found makes a SkillDef (pending section 4), so the safe path is: Salvaging as a WorkType first, SkillDef only if the owner insists.
3. **Weighted loot pool scaled by source mass/tier, with mod-item swap-in** (Disassemble Mechanoid): our wreck/appraisal loot table, with `CheckForMods`-style soft item substitution.
4. **Placed pick-over spot with terrain-gated PlaceWorker and per-spot loot comp** (Scavenging): the scavenger's workshop/sorting table at the ship; not-guaranteed finds.
5. **Byproduct and slow passive processing** (VRecycling): reclaimed-X byproduct on recipes, long-tick processing vats for bulk scrap, multi-cell outputs.
6. **Condition-based repair job: HP per material chunk, free-below-threshold, tech limit, float-menu entry** (Og Repair): repair half of the Salvaging loop; add skill scaling (they have none).
7. **Integer-inflated costs for rarity tables with `resourcesFractionWhenDeconstructed`** (Salvage Rubble): rarity without C#.
8. **Mod settings per mechanic**: efficiency slider, durability toggle, withhold-components toggle (Simple Recycling / Recycle This). Matches the repo Mod Settings rule.
9. **Sell-side value** (Traders Accept Junk): salvage value realised by trade as an alternate sink.

## 7. Incompatibility packageIds
Hard (replace our feature head-on; declare `incompatibleWith` in About.xml and runtime-check via ModsConfig/`ModLister.GetActiveModWithIdentifier`):
- `Mlie.RecycleThis` (ACTIVE now, so the list needs it removed or incompat-gated)
- `sneaks.recycle`
- `SoulRetextured.RecycleThis`
- `arvkus.simplerecycling`
- `futurplanet.disassemblemechanoid`
- `Romyashi.Scavenging`
- `Og.Repair.Your.Gear`

Soft (overlap partial; conflict risk on shared defs, decide per case): `VanillaExpanded.Recycling`, `moja.salvagerubble` (ACTIVE), `proxyer.dismantleancientjunk`, `Meteores.AncientUrbanRuinsAllDeconstructible.AURAD` (ACTIVE), `Hol.SmeltPatch` (ACTIVE), `Thumb.BetterCremation` (ACTIVE), `xelnigma.mechanoidslagtoplasteel`, `gunseeker.repairstation`, `Teiwaz.TAAJG` (ACTIVE).
Exact-case packageIds as in each About.xml. Caveat: three hard ones are inactive installs, and several soft ones are active in the current list, so incompat declaration will disable them on the campaign list unless the list is changed first.
