## spec
All rulings: `items/the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07.md`.
Four pieces.

### 1. The `ScenarioDef` — four parts, all vanilla classes

| part | why |
|---|---|
| `ScenPart_GameStartDialog` | the campaign's opening text; nowhere else can hold it |
| `ScenPart_DisableIncident` | stops the storyteller drawing an incident **while the def stays loadable for an authored quest** — cherrypicking cannot express this |
| `Rule_DisallowDesignator_ZoneAdd_Growing` | no personal sowing |
| `Rule_DisallowBuilding` ×N | every manual-sow basin and pot, ⛔ **by defName, never by label** |

⛔ `ScenPart_PermaGameCondition` and `ScenPart_StatFactor` are **dropped** — reasoning in the
parent. Do not reintroduce either.
⚠️ **Vanilla part classes only.** `ScenPart_Error` means a scenario naming a part from an
absent mod **degrades instead of failing the load**, so a modded part can vanish silently for
a recipient.

### 2. The mining gene

A `GeneDef` on `MandrakeJawa` with `disabledWorkTags: Mining`.
⭐ Per-pawn, so it delivers *"Jawa cannot, other races can"* exactly — **and it applies to
enemy Jawa factions too**, which no ScenPart buys.
⚠️ Confirmed at `Verse/GeneDef.cs:73`, applied by `Pawn_GeneTracker`. ⛔ **The def dump
reports 0 of 3,847 genes using this field. That is a dump blind spot, not absence.**

### 3. 🔴 The mining laser is OURS TO AUTHOR, and its work type is the whole point

There is **no `mining laser` ThingDef in any v1.6-loaded folder** — searched the active
stack. So author it, with a `WorkGiverDef` whose `workType` is **not** `Mining`. `Crafting`
is the natural home: it is machine operation, not digging.

⛔ **Do NOT patch vanilla's `Drill` WorkGiver.** Re-typing it would change the job for every
faction in the game. A Jawa being unable to run a deep drill is **the ruling working**, not a
gap to close later — the owner accepted that asymmetry explicitly.

### 4. What must still work

⛔ **Do not reach for a gene with `disabledWorkTags: PlantWork`.** `PlantWork` covers
`Growing` **and** `PlantCutting`, so it would also stop a Jawa harvesting, cutting wild
plants and **chopping trees** — no wood, on a scavenger clan. That is why the sowing ban is a
designator rule and not a gene.

## verify
- `validate_patch.py --defs` clean; every `Rule_DisallowBuilding` names a defName that resolves
- the gene is on `MandrakeJawa` and nowhere else
- the laser's `WorkGiverDef` has `workType` != `Mining`, and vanilla's `Drill` WorkGiver is
  **unmodified**

## criteria
🔑 **Straight from the parent, and it is a six-part test.** At the campaign start a Jawa
cannot create a growing zone, cannot sow a basin, and cannot mine by hand — **but can operate
the mining laser, and can harvest, cut plants and chop trees.** A recruited non-Jawa can mine
normally.

---

## MEASURED 2026-08-21 by BUILD — the `Rule_DisallowBuilding` list, and the criterion that gets it wrong

Source: `DefDump/defs.sqlite`, capture `2026-08-21T22:44:59Z`, 578 mods, 24,904 ThingDefs.
Frozen as `OFFICIAL-2026-08-21T22-44-59Z`.

🔴 **THE OBVIOUS CRITERION IS WRONG AND OVER-REPORTS BY 3×.** `building.sowTag` non-null
returns **44** defs. Only **14** are sowable buildings. The other 30 are a different
mechanic: 29 carry `sowTag = SupportPlantsOnly`, which means *"a grow zone may be sown on
the cell this thing occupies"* — sleeping spots, butcher and crafting spots, marriage,
ritual, party and meditation spots, the drop spot, the duel spot. ⛔ Disallowing those would
ban the player from placing a **sleeping spot**, and it would look like the rule working.

✅ **The criterion is `thingClass` = `Building_PlantGrower` or a subclass of it** — the class
vanilla's `WorkGiver_Grower.PotentialWorkThingsGlobal` actually scans, so it is what routes
a pawn to sow. Ground truth: `HydroponicsBasin` → `RimWorld.Building_PlantGrower`, sowTag
`Hydroponic`; `PlantPot` → same class, sowTag `Decorative`. The 14 are a strict subset of
the 44 — sowTag is **necessary but not sufficient**.

⚠️ Three subclasses do not carry `PlantGrower` in their name and would be missed by a name
match: `VFEF.Building_PlantGrower_NoEmptyLines`, `Caveworld_Flora_Unleashed.Building_FungiponicsBasin`,
`VanillaGravshipExpanded.Building_Agrocell`. Each was confirmed against the typeref in its
own assembly, not inferred.

**The 14, by defName as the spec requires — never by label:**

```
BMT_AdvancedFungiponicsBasin   advanced fungiponics basin      Biomes! Caverns
BMT_FungiponicsBasin           fungiponics basin               Biomes! Caverns
HydroponicsBasin               hydroponics basin               Core
PlantPot                       plant pot                       Core
PlantPot_Bonsai                bonsai pot                      Ideology
VFE_LongPlantPot               long plant pot                  Vanilla Furniture Expanded
VFE_DecorativePlantPot         decorative plant pot            VFE - Art
VFE_Ecosystem                  artificial ecosystem            VFE - Farming
VFE_Ecosystem_Tilable          tilable artificial ecosystem    VFE - Farming
VFE_Hydroponics_Tilable        tilable hydroponics basin       VFE - Farming
VFE_PlanterBox                 planter box                     VFE - Farming
VFE_PlanterBox_Tilable         tilable planter box             VFE - Farming
VGE_Agrocell                   agrocell                        Vanilla Gravship Expanded
VQEA_AncientGreenbed           ancient greenbed                VQE - Ancients
```

### ⚠️ ONE SCOPE CALL, FLAGGED NOT DECIDED — DECIDE or the owner owns it

`VFEFactory_Autofarmer` (*Vanilla Furniture Expanded - Factory*) is **excluded from the 14**
and it is genuinely borderline. It does not derive from `Building_PlantGrower`, implements
its own `IPlantToGrowSettable`, and a pawn does not sow *into* it — *"a large, automated
machine that combines the functions of a sower and harvester, moving back and forth across
a designated outdoor zone."* The machine sows the ground itself.

- If the ruling is **"no personal sowing"** (which is what §1 says, and what the designator
  rule expresses), the Autofarmer stays legal and the list is **14**.
- If the ruling is **"no building may produce crops"**, add it and the list is **15**.

🔑 It is worth deciding rather than defaulting: an automated farm a Jawa never touches is
arguably exactly the kind of scavenged machine this clan *should* be able to run.

⚠️ This list is measured against the 578-mod frozen capture. **Re-measure if the mod list
moves** — a new furniture mod adds sowable buildings and a stale list is a silent hole.
