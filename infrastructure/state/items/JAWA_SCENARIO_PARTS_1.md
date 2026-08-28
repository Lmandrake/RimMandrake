🔴 **OWNER, 2026-08-21 21:53 — THIS ITEM WAS OVER-BUILT AND TWO OF ITS FOUR PIECES ARE
STRUCK.** Verbatim: *"I'm afraid I'm going to disagree with the implementation of the no
planting. We should simply add a line that Jawa genetics has a disability toward farming."*
And: *"I believe the Mining Laser is actually called Drillturret and does NOT need art…
we only need to modify the skill its based on (likely shooting), NOT produce any art."*

**He is right on both, and both are now measured against `OFFICIAL-2026-08-21T22-44-59Z`
(578 mods, 24,904 ThingDefs, 3,845 GeneDefs).**

| piece | was | is now |
|---|---|---|
| no planting | a designator rule + a `Rule_DisallowBuilding` list of 14 defNames | **one gene** |
| the mining laser | *"OURS TO AUTHOR"*, plus art | **already exists**; one `workType` patch |
| the mining gene | unchanged | unchanged |
| what must still work | unchanged | unchanged |

⚠️ **The scope did not shrink because the work was hard. It shrank because two claims in
the spec were false**, and both had already produced work: a 14-def census that is now
worthless, and a plan to commission art for a building that ships with its own.

---

## spec
All rulings: `items/the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07.md`.
Four pieces.

### 1. The `ScenarioDef` — four parts, all vanilla classes

| part | why |
|---|---|
| `ScenPart_GameStartDialog` | the campaign's opening text; nowhere else can hold it |
| `ScenPart_DisableIncident` | stops the storyteller drawing an incident **while the def stays loadable for an authored quest** — cherrypicking cannot express this |
| ~~`Rule_DisallowDesignator_ZoneAdd_Growing`~~ | ⛔ **STRUCK** — owner, 2026-08-21. Replaced by the farming gene in §1a |
| ~~`Rule_DisallowBuilding` ×N~~ | ⛔ **STRUCK** — same ruling. The 14-def census below is superseded and must not be built |

🔑 **The `ScenarioDef` survives, and is now TWO parts, not four:**
`ScenPart_GameStartDialog` and `ScenPart_DisableIncident`. Nothing else.

⛔ `ScenPart_PermaGameCondition` and `ScenPart_StatFactor` are **dropped** — reasoning in the
parent. Do not reintroduce either.
⚠️ **Vanilla part classes only.** `ScenPart_Error` means a scenario naming a part from an
absent mod **degrades instead of failing the load**, so a modded part can vanish silently for
a recipient.

### 1a. ⭐ THE FARMING BAN IS A GENE, AND BIOTECH ALREADY SHIPS IT

**`AptitudeTerrible_Plants`** — Biotech, `aptitudes: [{skill: Plants, level: -8}]`. Measured:
Biotech ships a full `AptitudeTerrible_*` set across all twelve skills, and 24 GeneDefs in
the active stack carry a negative aptitude. **Nothing to author.** Add it to `MandrakeJawa`'s
gene list, or copy the one line into a Jawa-flavoured gene if the label matters.

✅ **Why this is the right shape and the designator rules were not.** A scenario rule binds
the PLAYER'S UI on one save. A gene binds the pawn — so it applies to **enemy Jawa factions
too**, it survives into any save, and it needs no list that decays every time a furniture mod
is added. It is also honest: Jawa are *bad at farming*, which reads as biology, where a
greyed-out build button reads as the game refusing you.

⚠️ **ONE FORK, AND IT IS THE OWNER'S WORD "disability" THAT DECIDES IT.**
- **Aptitude −8 (recommended, and what is written above):** bad at it, not barred from it.
  Harvesting, plant cutting and **chopping trees** all still work.
- `disabledWorkTags: PlantWork`: genuinely incapable. ⛔ But `PlantWork` covers `Growing`
  **and** `PlantCutting` — there is no `Growing`-only WorkTag — so it also stops a Jawa
  harvesting, cutting wild plants and **chopping trees**. No wood, on a scavenger clan. §4
  already warned about this and the warning still stands.

### 2. The mining gene

A `GeneDef` on `MandrakeJawa` with `disabledWorkTags: Mining`.
⭐ Per-pawn, so it delivers *"Jawa cannot, other races can"* exactly — **and it applies to
enemy Jawa factions too**, which no ScenPart buys.
⚠️ Confirmed at `Verse/GeneDef.cs:73`, applied by `Pawn_GeneTracker`.

🔴 **CORRECTED 2026-08-21 — this used to say "the def dump reports 0 of 3,847 genes using
this field. That is a dump blind spot, not absence." BOTH HALVES ARE WRONG.** Measured:
the dump carries `disabledWorkTags` on **3,845 of 3,845** GeneDefs, and **5 hold a real
value** — `ViolenceDisabled` (Biotech) `Violent`, `BS_DroneKind` `Intellectual`,
`BS_SimpleMind`, `BS_VerySimpleMind`, `Turn_Gene_Bliss`. The other 3,840 read `None`,
which is a measured zero, not a hole. ⇒ **There is no blind spot here and the dump can be
trusted for this field.** Wrongly claiming one is the inverse of the usual trap and it is
just as expensive: it teaches a reader to distrust a working instrument.

### 3. ✅ The mining laser ALREADY EXISTS. It is `DrillTurret`, it has art, and one field moves

🔴 **CORRECTED 2026-08-21 on the owner's word, then measured.** This section used to read
*"There is **no `mining laser` ThingDef in any v1.6-loaded folder** — searched the active
stack. So author it"*, and it was wrong twice over.

    DrillTurret          ThingDef       "drill turret"   MiningCo. DrillTurret (Continued)
    OperateDrillTurret   WorkGiverDef   workType = "Mining"
    OperateDrillTurret   JobDef         DrillTurret.JobDriver_OperateDrillTurret
    Blueprint_/Frame_/Techprint_DrillTurret, ResearchDrillTurret(+EfficientDrilling)

A whole shipped mod, with its own research, blueprint, frame and job driver.
⚠️ A literal `mining laser` exists too and is **not** what we want: `guy762_mininglaser`
(*Star Wars KotOR Weapons and Armor*) is a hand-held **weapon** — `category Item`,
`weaponClasses [Ranged]`, *"This industrial hand-held laser can double as a makeshift
blaster."* The earlier search missed both.

⛔ **AUTHOR NOTHING, AND COMMISSION NO ART.** Owner, 2026-08-21: *"does NOT need art…
NOT produce any art please!!!"* 🔑 And the standing rule behind it, which is why the
original claim was reached at all: **missing VIEWS are not missing art.** A
`Graphic_Multi` with no south texture, or a def whose art lives in an AssetBundle rather
than a loose PNG, renders perfectly in game. Never conclude a RimWorld asset is absent
without `reading-rimworld-graphics`; magenta in game is the evidence, a missing file on
disk is not.

**THE ENTIRE CHANGE IS ONE FIELD.** `OperateDrillTurret`'s `workType` is `Mining`, so
§2's `disabledWorkTags: Mining` gene would bar a Jawa from operating the turret as well as
from swinging a pick — which defeats the point of having it. Re-point it with a
`PatchOperationReplace`.

⚠️ **WHICH `workType`, measured rather than guessed.** The owner's instinct was *"likely
shooting"*. Across every Core/DLC `WorkTypeDef`, exactly one carries the Shooting skill:

    Hunting     relevantSkills ['Shooting','Animals']   workTags: Violent, Hunting, Shooting, ...
    Crafting    relevantSkills ['Crafting']             workTags: ManualSkilled, Crafting, ...

- **`Hunting`** matches the instinct and reads right for an aimed turret. ⚠️ But it carries
  `Violent`, so a pawn incapable of violence could not operate it, and the turret would be
  prioritised in the same column as hunting animals.
- **`Crafting`** is machine operation with no `Violent` tag and no side effects.

⇒ **Recommend `Crafting`; `Hunting` is defensible if the owner wants the shooting flavour
and accepts the Violent gate.** This is the one open question left in the item.

⛔ **Do NOT patch vanilla's `Drill` WorkGiver.** Re-typing it would change the job for every
faction in the game. A Jawa being unable to run a deep drill is **the ruling working**, not a
gap to close later — the owner accepted that asymmetry explicitly.

### 4. What must still work

⛔ **Do not reach for a gene with `disabledWorkTags: PlantWork`.** `PlantWork` covers
`Growing` **and** `PlantCutting`, so it would also stop a Jawa harvesting, cutting wild
plants and **chopping trees** — no wood, on a scavenger clan. That is why the sowing ban is a
designator rule and not a gene.

## verify
🔴 **REWRITTEN 2026-08-21 with the item. The old first bullet — "every `Rule_DisallowBuilding`
names a defName that resolves" — is struck with the rule itself.**
- `validate_patch.py --defs` clean, and every patched xpath reported as MATCHING, not merely
  well-formed. A `PatchOperationReplace` that matches nothing logs nothing.
- ⛔ ~~the `ScenarioDef` carries exactly two parts: `ScenPart_GameStartDialog` and
  `ScenPart_DisableIncident`~~ **STRUCK 2026-08-22 by BUILD — this clause is wrong on BOTH
  halves, and the rulings that overturned it are recorded inside
  `src/Jawa/Jawa_Patches/Defs/ScenarioDefs/Scenario_Utinni.xml` itself.**
  1. `ScenPart_DisableIncident` was **declined by the owner** 2026-08-22 on the fiction —
     *"keep them in, it allows the Jawa to show that even in those situations, they will be
     compelled to enslave the individual."* A wanderer is a SITUATION, not a free colonist.
     ⛔ Do not add it later "to finish the def".
  2. Two parts **cannot start a game.** The def also needs
     `ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes` (ONE part, carrying
     `xenotypeCounts` MandrakeJawa ×6 — the six founders; the plain `ConfigureStartingPawns`
     cannot set a xenotype at all) and `ScenPart_PlayerPawnsArriveMethod` (`Standing`, because
     the clan is already aboard the hull rather than dropping out of the sky).
  ✅ **The clause as it should read:** `Jawa_UtinniStart` carries exactly three AUTHORED parts —
  `ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes`, `ScenPart_PlayerPawnsArriveMethod`,
  `ScenPart_GameStartDialog` — and **no `ScenPart_DisableIncident`**.
  ⚠️ **Amended 2026-08-28 by FOUNDRY at close: FOUR authored parts.** A
  `ScenPart_StartingAnimal` (the Ikee, `AA_Eyeling` ×1, bond chance 1.0) was added on the
  owner's 2026-08-23 ruling — recorded in the def file itself. Still no
  `ScenPart_DisableIncident`; expect 6 in a dump (4 authored + 2 engine `ScenPart_PlanetLayer`).
  ⚠️ **The live def set reports FIVE, and that is not a defect.** Measured in capture
  `2026-08-23T05-05-29Z`: the game appends two `ScenPart_PlanetLayer` parts to the scenario at
  load (Odyssey's planet layers). They are engine-added, they are in no XML of ours, and a
  count taken from the dump must expect them. Count AUTHORED parts in the file; count 5 in the
  dump.
- `MandrakeJawa` carries the farming gene and the mining gene, and **no other xenotype carries
  the MINING gene**. ⚠️ **Narrowed 2026-08-22 by BUILD, and measured.** `AptitudeTerrible_Plants`
  is a **vanilla Biotech gene**, not ours, and three other authored xenotypes legitimately carry
  it for their own flavour — `RimMandrakeSithMassassi`, `RimMandrakeSullustan`,
  `RimMandrakeWeequay`. Reading the original clause literally would demand stripping a vanilla
  aptitude out of three unrelated species to satisfy a checkbox. ⇒ **Exclusivity is a real
  requirement for `RimMandrake_Jawa_MiningDisabled` (which IS ours, and is exclusive — measured
  1 of 1) and was never a requirement for the shared Biotech aptitude.**
- `OperateDrillTurret`'s `workType` reads the chosen value and **not** `Mining`, in the LIVE
  def set — the patch is against another mod's def, so a repo-only check proves nothing
- ⛔ vanilla's `Drill` WorkGiver is **unmodified**, and `DrillTurret`'s own defs are otherwise
  untouched — we patch one field of someone else's mod and nothing more
- ⛔ **no new texture, anywhere.** `git status` shows zero added files under any `Textures/`

## criteria
🔑 **Straight from the parent, and it is a six-part test.** At the campaign start a Jawa
cannot create a growing zone, cannot sow a basin, and cannot mine by hand — **but can operate
the mining laser, and can harvest, cut plants and chop trees.** A recruited non-Jawa can mine
normally.

---

## ⛔ SUPERSEDED 2026-08-21 — the `Rule_DisallowBuilding` census, kept only as a record

🔴 **DO NOT BUILD FROM THIS.** The owner struck `Rule_DisallowBuilding` entirely at 21:53;
the farming ban is §1a's gene. This section is left in place because it is measured and
because deleting it would let someone re-derive the 44-def version, but **nothing below is
work any more.**

✅ **The one part still worth carrying forward** is the trap, not the list: `building.sowTag`
non-null returns **44** defs and only **14** are sowable buildings — 29 of the extras are
`SupportPlantsOnly` SPOTS (sleeping spot, butcher spot, ritual spot). Anyone who ever needs
this population must use `thingClass = Building_PlantGrower` or a subclass, which is what
`WorkGiver_Grower.PotentialWorkThingsGlobal` actually scans.

### the superseded census follows

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

### ⚠️ ~~ONE SCOPE CALL~~ — MOOT. There is no building list, so the Autofarmer question does not arise

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
