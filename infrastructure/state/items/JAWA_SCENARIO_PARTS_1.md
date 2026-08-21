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
