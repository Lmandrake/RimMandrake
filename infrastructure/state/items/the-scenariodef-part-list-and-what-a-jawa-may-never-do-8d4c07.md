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
