🔴 **OVERTAKEN 2026-08-21/22. FOUR CLAIMS BELOW ARE DEAD — read this header before
acting on anything in this file.** All four were ruled by the owner and executed; the
corrections are recorded here on his instruction to propagate them.

**1. The no-planting row is STRUCK.** Owner, 2026-08-21: *"I'm afraid I'm going to disagree
with the implementation of the no planting. We should simply add a line that Jawa genetics
has a disability toward farming."* Then, on the fork: *"Correct on the aptitude decision."*
⇒ `Rule_DisallowDesignator_ZoneAdd_Growing` and the `Rule_DisallowBuilding` list are dead.
Shipped instead: **`AptitudeTerrible_Plants`** on `MandrakeJawa` (`56d2b4d`). ✅ The row's
own argument against a `PlantWork` gene still stands and is exactly why an APTITUDE was
chosen over `disabledWorkTags`.

**2. The `disabledWorkTags` blind-spot claim is FALSE, both halves.** It reads *"the def dump
reports 0 of 3,847 genes using `disabledWorkTags`. That is a dump blind spot, not absence."*
Measured: the dump carries the field on **3,845 of 3,845** GeneDefs and **5 hold a real
value** — `ViolenceDisabled` (Biotech), `BS_DroneKind`, `BS_SimpleMind`, `BS_VerySimpleMind`,
`Turn_Gene_Bliss`. The rest read `None`, a measured zero. 🔑 **Claiming a blind spot that is
not there is the inverse of the usual trap and costs the same: it teaches a reader to
distrust a working instrument.**

**3. "There is nothing to re-point… no `mining laser` ThingDef exists" is FALSE** — the whole
*"⭐ One wrinkle that makes this EASIER"* section. Owner, 2026-08-21: *"I believe the Mining
Laser is actually called Drillturret and does NOT need art."* He is right. **`DrillTurret`**
(*MiningCo. DrillTurret (Continued)*, `mlie.miningcodrillturret`) ships with its own
research, blueprint, frame, techprint, `JobDef`, job driver **and art**. A literal
`guy762_mininglaser` exists too, as a hand-held weapon. The original search missed both.

**4. Final spec point 2 is superseded.** *"The mining laser is a new ThingDef of ours…
`Crafting` is the natural home"* → nothing was authored. `OperateDrillTurret`'s `workType`
was re-pointed `Mining` → **`Hunting`** (`fe0064c`). Owner, 2026-08-22: *"And I still like
shooting for the laser, please make it so."* `Hunting` is the only Core/DLC work type
carrying the Shooting skill; its `Violent` tag is the accepted cost. ⛔ Do not "correct" it
back to `Crafting`.

✅ **Points 1 and 3 of that final spec stand and shipped as written:** the
`disabledWorkTags: Mining` gene (`13c6dd8`), and *do not touch vanilla's `Drill` WorkGiver*.

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

## 🔴 OWNER'S ANSWER, 2026-08-21 — lever (b): re-point the laser off `Mining`

Gene stays as specced — `disabledWorkTags: Mining` on `MandrakeJawa`, so **no Jawa digs by
hand and no Jawa operates a deep drill.** The laser is taken out of the `Mining` work type
so a Jawa can run it.

He accepted the asymmetry explicitly: *the laser works, the drill beside it does not, and
nothing in the fiction explains why.*

### ⭐ One wrinkle that makes this EASIER, not harder

**There is nothing to re-point.** No `mining laser` ThingDef exists in any v1.6-loaded
folder — searched the whole active stack. ⇒ **the laser is ours to author**, and it should be
written with a non-`Mining` work type **from the start** rather than patched afterwards.

That is strictly better than lever (b) as described:
- ⛔ no `PatchOperationReplace` on another mod's `WorkGiverDef` — which would have re-typed
  the job for **every faction in the game**, not just ours
- ✅ the work type is a property of our own def, so nothing else in the stack changes
- ✅ and it is honest: the fiction is *"a tech you can learn from the ship"*, so a
  ship-taught machine having its own discipline is the explanation the asymmetry wanted

**⇒ Spec for whoever builds it:**
1. `MandrakeJawa` gains a `GeneDef` with `disabledWorkTags: Mining`.
   ⚠️ `GeneDef.disabledWorkTags` is confirmed at `Verse/GeneDef.cs:73` and applied per-pawn
   by `Pawn_GeneTracker`. ⛔ **The def dump reports 0 of 3,847 genes using it — that is a
   dump blind spot, not absence.** Do not conclude it cannot be done.
2. The mining laser is a **new ThingDef of ours**, with a `WorkGiverDef` whose `workType` is
   **not** `Mining`. `Crafting` is the natural home — it is machine operation, not digging.
3. ⛔ **Do not touch vanilla's `Drill` WorkGiver.** A Jawa not being able to run a deep drill
   is the ruling working, not a bug to fix later.

✅ **The sowing half is untouched and was always correct** —
`Rule_DisallowDesignator_ZoneAdd_Growing` plus `Rule_DisallowBuilding`, and the reasoning
against a `PlantWork` gene (it would also stop harvesting and tree-chopping) stands.

## the last two ScenParts — DECIDE, 2026-08-21: ⛔ DROP BOTH

This item said *"DECIDE brings a candidate or drops them."* I looked for candidates and
there are none worth taking.

🔑 **The test both of the KEPT parts pass, and neither of these does: a ScenPart earns its
place when it expresses something no def, biome, weather or difficulty setting can.**
`ScenPart_GameStartDialog` is the only place the campaign's opening text can live at all.
`ScenPart_DisableIncident` stops the storyteller drawing an incident **while leaving the def
loadable for an authored quest** — cherrypicking genuinely cannot express that. Both are
unique capabilities.

**`ScenPart_PermaGameCondition` — dropped.** A condition that never ends is the heaviest
always-on modifier the game has, and nothing in this design asks for one. The planet's
character is already carried by authored biome, temperature, rainfall and weather, per tile.
⚠️ **The one candidate that looked real does not survive inspection:** `GameConditionDef` has
a `preventRain` flag (`WeatherDecider.cs:167`), so a permanent condition would be a second
belt on the rain ban. ⛔ But the ban is already exact — `rain_mm 0` multiplies rain
commonality by zero — so it would add nothing, and it would also kill the **violent mountain
rain** that is parked in `V2_DREAMS.md`. A part that forecloses a v2 idea to duplicate a v1
one is a clear no.

**`ScenPart_StatFactor` — dropped.** A global stat multiplier is a thumb on the scale with no
fiction behind it, and this campaign's difficulty shape already lives in the custom
difficulty fields (`SCENARIO_SETTINGS_SPEC.md`). ⭐ The project's own rule is *"flavour
without mechanics will not survive contact with play"* — a StatFactor is the exact inversion,
**mechanics with no flavour**, and it is the easier mistake to make because it always
"works".

⇒ **Four parts, final:** `ScenPart_GameStartDialog` · `ScenPart_DisableIncident` ·
`Rule_DisallowDesignator_ZoneAdd_Growing` · `Rule_DisallowBuilding` (per banned basin/pot,
**by defName, never by label**).
⚠️ **Prefer vanilla part classes throughout.** `ScenPart_Error` means a save whose scenario
names a part from an absent mod **degrades rather than failing the load** — so a modded part
can silently vanish for a recipient and nothing will say so.

⇒ Everything this item owed is now ruled. The build is `JAWA_SCENARIO_PARTS_1`.
