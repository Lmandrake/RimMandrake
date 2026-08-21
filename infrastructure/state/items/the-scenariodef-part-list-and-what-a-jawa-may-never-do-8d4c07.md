## spec
**RULED SO FAR — owner, 2026-08-19, in Q/A.**

🔑 **THE PRINCIPLE, in his words:** *"anything that makes YOU know how to sow
should not work. Jawas can only allow tech to farm for them."* and *"Jawa should
not be able to mine ore, though some other races still can. And the mining laser
should be able to do this very well."* Later, confirming: *"the mining laser
should no longer be banned, **it makes sense as a tech you can learn from the
ship**."*
⇒ **A Jawa may not personally sow or dig. A MACHINE may do both on their behalf,
and the ship is where that machinery is learned.** That last clause is the
justification and it should show up in the research tree's fiction, not only in
a prohibition.

**THE MECHANISM IS A HYBRID, and the split is measured, not stylistic:**
| rule | lever | why not the other one |
|---|---|---|
| no personal sowing | `Rule_DisallowDesignator_ZoneAdd_Growing` + `Rule_DisallowBuilding` on every manual-sow basin/pot | 🔴 a gene with `disabledWorkTags: PlantWork` is TOO BROAD — `PlantWork` covers `Growing` **and** `PlantCutting`, so it would also stop a Jawa harvesting, cutting wild plants and **chopping trees**. No wood, on a scavenger clan. Confirmed in `Data/Core/Defs/WorkTypeDefs/WorkTypes.xml` |
| no personal digging | a **GeneDef on `MandrakeJawa`** with `disabledWorkTags: Mining` | ⭐ a ScenPart designator ban is colony-wide and would block a recruited non-Jawa too. The gene is per-pawn, so it delivers *"Jawa cannot, other races can"* exactly — **and it applies to enemy Jawa factions as well**, which nothing else buys. `WorkTags.Mining` covers only the `Mining` work type. `GeneDef.disabledWorkTags` CONFIRMED at `Verse/GeneDef.cs:73`, applied per-pawn by `Pawn_GeneTracker` (`:414-419`) |
⚠️ **The def dump reports 0 of 3,847 genes using `disabledWorkTags`. That is a
DUMP BLIND SPOT, not absence** — the field is in the decompiled assembly. Do not
conclude from the dump that this cannot be done.
🔴 **OPEN RISK, must be measured before building the gene:** if the mining laser
is operated as a **`Mining` work-type job**, the gene would block Jawa from using
it — which directly contradicts the owner's ruling. Measure the laser's mechanism
FIRST; if it is a Mining job, the gene is the wrong lever for digging too and the
rule needs a different expression.

**THE HYDROPONICS TEST — owner's exact criterion:** *"If hydroponics doesn't
actually use the pawn's planting skill to sow crops, then it can stay viable for
Jawa."* ⇒ Ban is by MECHANISM, not by name:
· a basin a colonist SOWS as a Plants job → banned. Vanilla `HydroponicsBasin`
  fails this test.
· flowerpots → banned, same reason (owner named them).
· an automated farm that produces without a sow job → **allowed**. Owner names
  the **VFE factory** as something that must still work.
⛔ Do not ban by label. Two things called "hydroponics" can fall on opposite sides.

**REMAINING SCENPART DECISIONS:**
· ⭐ `ScenPart_GameStartDialog` — take it. Highest-leverage text in the campaign.
· ⭐ `ScenPart_DisableIncident` — take it. Stops the storyteller drawing an incident
  while leaving the def loadable for an authored quest. Cherrypicking cannot
  express this.
· `ScenPart_PermaGameCondition`, `ScenPart_StatFactor` — **owner has not ruled.**
  DECIDE brings a candidate or drops them.
· `ScenPart_DisableQuest`, `ScenPart_CreateIncident` — not v1.
⚠️ Prefer VANILLA part classes. `ScenPart_Error` means a save whose scenario
names a part from an absent mod **degrades rather than failing the load** — so a
modded part can silently vanish for a recipient and nothing will say so.

## verify
a `ScenarioDef` exists carrying the ruled parts; `validate_patch.py --defs` clean;
every banned building is named by defName rather than by label; the Jawa mining
gene is on `MandrakeJawa` and the mining laser has been confirmed usable by a
pawn carrying it.

## criteria
at the owner's campaign start, a Jawa cannot create a growing zone, cannot sow a
basin, and cannot mine by hand — but CAN operate the mining laser, and CAN harvest,
cut plants and chop trees. A recruited non-Jawa can mine normally.

## notes
**from:** DECIDE, 2026-08-19. Created by the R-S2 reversal — the ScenarioDef went from
"do not author" to "the only door", so its contents are now owed work.
⏱️ **DEADLINE: it must exist BEFORE the owner starts his campaign.** The engine
embeds the parts at game creation and nothing may edit the save afterwards. A
part missing then is missing from every player's game forever.

**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

doing — DECIDE owes the def-level list; the enumeration of every manual-sow
building and the mining laser's mechanism is in flight.

## the open risk is MEASURED, and it is real — DECIDE, 2026-08-21

This item said: *"if the mining laser is operated as a `Mining` work-type job, the gene
would block Jawa from using it… Measure the laser's mechanism FIRST."*

🔴 **Measured. Operating a drill IS a `Mining` job.** Vanilla's `Drill` WorkGiver —
the one a pawn uses to run a deep drill — reads
`<workType>Mining</workType>` (`Core/Defs/WorkGiverDefs/WorkGivers.xml:964-967`), and the
`Mining` work type's own description is literally **"Digging and drilling."**
(`WorkTypes.xml:195-199`).

⇒ **A gene with `disabledWorkTags: Mining` stops a Jawa operating a drill or a laser, not
just swinging a pick.** As specced, the gene contradicts the owner's own ruling that *"the
mining laser should be able to do this very well."*

⚠️ **There is no `mining laser` ThingDef in any v1.6-loaded folder** — searched the active
stack; the only "mining laser" string is in a 1.5 tree the game does not load. So the laser
is a thing we intend, not a thing we have, and the rule must be written for the machine we
build rather than one we can inspect.

### The fork, and it is the owner's — three levers, none free

| | lever | what it costs |
|---|---|---|
| **(a)** | **gene `disabledWorkTags: Mining`**, and the digging machines are **UNMANNED** — a powered building that yields with no pawn job at all | ⭐ **most faithful to *"Jawas can only allow tech to farm for them"*** — a Jawa standing at a drill for six hours is not tech doing it for them. ⚠️ Needs an unmanned miner to exist; the quarry and drill mods in this stack are all pawn-operated |
| **(b)** | gene, plus **re-point the laser's WorkGiver off `Mining`** onto another work type | keeps a pawn at the machine. ⚠️ Re-typing work is invasive and changes the job for every faction, not just ours |
| **(c)** | **`Rule_DisallowDesignator_Mine`** instead of the gene — ban the *designator*, so nobody hand-mines but machines are untouched | ⛔ **breaks the ruling in the other direction:** a ScenPart designator ban is **colony-wide**, so a recruited non-Jawa could not mine either, and the owner said *"some other races still can"* |

🔑 **(a) is DECIDE's recommendation** — it is the only one that keeps both halves of what he
said, and it turns the constraint into content: **the Jawa mining tech is a thing you switch
on, not a thing you stand at.** That is also the fiction the research tree wanted:
*"it makes sense as a tech you can learn from the ship."*

⛔ **Do not build the gene until this is answered.** Shipping (a)'s gene without (a)'s
unmanned machine leaves the clan unable to mine at all.

✅ **The SOWING half is unaffected and still correct as specced.** That side uses
`Rule_DisallowDesignator_ZoneAdd_Growing` plus `Rule_DisallowBuilding`, and the reasoning
against a `PlantWork` gene — that it would also stop harvesting and tree-chopping — stands
untouched.
