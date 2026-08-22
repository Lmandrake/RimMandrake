## spec
🔴 **`infrastructure/state/items/the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07.md`
is DECIDE's, is closed at `50e74d4`, and now carries four claims the owner has overtaken.**
BUILD cannot edit it — the seat guard refuses. Everything below is measured or verbatim.

⚠️ **All four have already been corrected in `JAWA_SCENARIO_PARTS_1`**, which is BUILD's.
But that file cites this one as its source of rulings, and **nobody reads backwards** — a
reader arriving here gets the dead version.

**1. The no-planting row (~line 18) is STRUCK.** Owner, 2026-08-21 21:53: *"I'm afraid I'm
going to disagree with the implementation of the no planting. We should simply add a line
that Jawa genetics has a disability toward farming."* Then, on the fork: *"Correct on the
aptitude decision."* ⇒ `Rule_DisallowDesignator_ZoneAdd_Growing` and the
`Rule_DisallowBuilding` list are dead. Shipped instead: `AptitudeTerrible_Plants` on
`MandrakeJawa` (`56d2b4d`, `JAWA_CANNOT_FARM_GENE_1`). The row's own reasoning against a
`PlantWork` gene is still correct and is why an APTITUDE was chosen over `disabledWorkTags`.

**2. The `disabledWorkTags` blind-spot claim (~line 20 and repeated at the foot) is FALSE,
both halves.** It reads *"The def dump reports 0 of 3,847 genes using `disabledWorkTags`.
That is a dump blind spot, not absence."* Measured against
`OFFICIAL-2026-08-21T22-44-59Z`: the dump carries the field on **3,845 of 3,845** GeneDefs,
and **5 hold a real value** — `ViolenceDisabled` (Biotech) `Violent`, `BS_DroneKind`,
`BS_SimpleMind`, `BS_VerySimpleMind`, `Turn_Gene_Bliss`. The rest read `None`, a measured
zero. 🔑 **Claiming a blind spot that is not there is the inverse of the usual trap and
costs the same thing: it teaches a reader to distrust a working instrument.**

**3. "There is nothing to re-point… no `mining laser` ThingDef exists in any v1.6-loaded
folder" is FALSE** — the whole *"⭐ One wrinkle that makes this EASIER"* section. Owner,
2026-08-21: *"I believe the Mining Laser is actually called Drillturret and does NOT need
art."* He is right. `DrillTurret` (*MiningCo. DrillTurret (Continued)*, `mlie.miningcodrillturret`)
ships with `ResearchDrillTurret`, `Blueprint_`/`Frame_`/`Techprint_DrillTurret`, a `JobDef`,
`DrillTurret.JobDriver_OperateDrillTurret` — and its own art. A literal `guy762_mininglaser`
exists too, as a hand-held weapon. **The original search missed both.**

**4. Final spec point 2 is superseded.** *"The mining laser is a new ThingDef of ours… `Crafting`
is the natural home"* → nothing was authored. `OperateDrillTurret`'s `workType` was
re-pointed `Mining` → **`Hunting`** (`fe0064c`, `DRILLTURRET_IS_A_SHOOTING_JOB_1`). Owner,
2026-08-22: *"And I still like shooting for the laser, please make it so."* `Hunting` is the
only Core/DLC work type carrying the Shooting skill; its `Violent` tag is the accepted cost.
⛔ Do not "correct" it back to `Crafting`.

✅ **Points 1 and 3 of that final spec still stand and shipped as written:** the
`disabledWorkTags: Mining` gene (`JAWA_CANNOT_DIG_GENE_1`), and *do not touch vanilla's
`Drill` WorkGiver*.

## verify
The file carries a correction at the head naming all four, or the four passages are struck
in place. A reader arriving cold cannot conclude that a mining laser must be authored, that
the dump has a `disabledWorkTags` blind spot, or that the planting ban is a ScenPart.

## criteria
No file in the repo still instructs anyone to author a mining laser or to build the
`Rule_DisallowBuilding` list.
