# J4 / J5 — what a Jawa can actually farm. 2026-08-26, seat CHECK

Full 582-mod list, live map, a `MandrakeJawa` and a `Baseliner` spawned side by side into
`PlayerColony` and read with `jawa/pawn_get` + `jawa/pawn_stats`.

## 🔴 J4 as written is FALSE. A Jawa **will** sow — it just cannot sow anything skilled.

```
                levelRaw  levelEffective  disabled   PlantWorkSpeed  PlantHarvestYield
MandrakeJawa        5            0          false        0.100            0.60
Baseliner           4            4          false        0.648            0.85
```

🔑 **`AptitudeTerrible_Plants` takes raw skill 5 down to EFFECTIVE 0** — and that gap is only visible
because `jawa/set_pawn_skill`'s read-back reports both. `SkillRecord.Level`'s getter adds aptitudes,
so anything reading the raw number sees a competent farmer that does not exist.

⇒ The Jawa is **not forbidden** from plant work (`disabled: false`, confirming J6 on a second pawn).
It is **effective-skill 0 and works at one tenth of a Baseliner's speed**, harvesting 60% against 85%.

## What that means crop by crop — measured, 294 sowable plant defs in the dump

```
sowMinSkill:   0 -> 117 defs     3 -> 7     4 -> 3     5 -> 6
               6 -> 146 defs     7 -> 2     8 -> 9    10 -> 3    12 -> 1
```

**117 of 294 (40%) are sowable at effective skill 0. 177 are not** — and the cliff is at **skill 6,
where 146 defs sit**.

| crop | sowMinSkill | a Jawa? |
|---|---|---|
| `Plant_Rice` · `Plant_Potato` · `Plant_Corn` · `Plant_Haygrass` · `Plant_Cotton` | **0** | ✅ every staple |
| `Plant_Smokeleaf` | 4 | ❌ |
| `Plant_Psychoid` | 6 | ❌ — and 145 others at this tier |
| `Plant_Healroot` | 8 | ❌ **no herbal medicine** |
| `Plant_Devilstrand` | 10 | ❌ |
| `Plant_HydroDevilstrand_GT` | 12 | ❌ |

🔑 **A Jawa colony can feed and clothe itself — rice, potatoes, corn, hay, cotton — and cannot grow
its own medicine.** `Plant_Healroot` at skill 8 is the one that bites: herbal medicine has to be
bought, looted or grown by somebody who is not a Jawa. That is a campaign fact, not a bug, and it is
worth knowing before someone designs a self-sufficient Jawa settlement.

## J5 — **CONFIRMED, and it is the failure mode the item warned about**

Harvesting, cutting plants and chopping trees carry **no skill floor at all** — only sowing checks
`sowMinSkill`. With `disabled: false`, the Jawa does all three. At `PlantWorkSpeed 0.1` it does them
**six and a half times slower** than a Baseliner and brings home 60% of the yield.

⇒ Exactly J5's stated shape: *"the same Jawa still HARVESTS, CUTS plants and CHOPS trees."* The
design gets a Jawa that is bad at farming rather than one that is barred from it.

## The correction this item needs

⛔ **J4's criterion cannot be graded as written.** *"A Jawa will not sow"* is contradicted by the
engine's own numbers on every staple crop. The measurable, useful version is:

> A Jawa sows only `sowMinSkill 0` crops, at `PlantWorkSpeed 0.1`, and cannot sow `Plant_Healroot`.
> A Baseliner in the same colony sows anything up to its own skill, at ~6.5x the speed.

Whether *"will not sow"* was the design intent — i.e. whether the aptitude should be a hard work
disable instead — is a scope call and is filed, not decided here.

---

# The behavioural half — what I could and could not attribute

## ✅ A Baseliner in the same colony sows. Caught in the act.

`jawa/ordered_job` Sow, then the clock stepped by hand:

```
+ 700 ticks   job=CutPlant   cell=[]
+1400 ticks   job=Sow        cell=['Plant_Rice', 'Mote_ProgressBar']
```

The progress mote is the sow in progress. Unambiguous, and it is the control J4 asks for.

## ⛔ The Jawa half is NOT attributable, and here is exactly why

**With all four other colonists DRAFTED** — a drafted pawn takes no work, so the Jawa was the only
pair of hands on the map that could sow — the Jawa was ordered to sow a virgin `Soil` cell inside
the growing zone and **did not, across 7,000 ticks**:

```
order -> accepted=True  after=Wait
+500 Wait · +1000 Wait_Wander · +2000 GotoWander · +4000 GoForWalk · +6000 GotoWander   cell=[] throughout
```

🔴 **That is NOT evidence the Jawa cannot sow, because the tool cannot issue a working Sow.**
Read from source: `Verse/AI/Job.cs:63` declares `public ThingDef plantDefToSow`, and
`JobDriver_PlantSow.cs:27` opens with

```csharp
.FailOn(() => !job.plantDefToSow.CanNowPlantAt(base.TargetLocA, base.Map))
```

`jawa/ordered_job`'s whole parameter set is
`count · jobDef · jobTag · pawnId · queue · targetAId/X/Z · targetBId/X/Z · timeoutSeconds · waitTicks`
— **there is no way to set `plantDefToSow`.** A null there is dereferenced in the driver's first
toil, so the job is accepted and dies immediately. Which is precisely what the tool reported:
`accepted: true`, `nowRunningRequested: false`, `afterJobDef: Wait`, `ticksElapsed: 0`.
⇒ The Baseliner's `Sow` above was its **own AI-chosen** job off the growing zone, not my order.

Filed as `ORDERED_JOB_CANNOT_SOW_1`.

## Three more traps this cost, all real

1. **`ordered_job`'s `waitTicks` does nothing on a PAUSED game** — `ticksElapsed: 0` after asking for
   4,000. The job is enqueued and no ticks pass. Step the clock yourself.
2. **Sand has fertility 0.** The first target cell was `Sand`; nothing could ever have grown there,
   and the tool's honest `accepted / not running` split is what exposed it.
3. **A wild plant is a false positive.** My first Jawa run broke on `if things:` and
   `Plant_YellowTallGrass` had grown in the cell. Check for the crop **by name**.

## Where J4 stands

**Mechanism: settled.** Rice is `sowMinSkill 0`, the Jawa's effective Plants is 0, `disabled: false`
⇒ the engine permits it, and the item's *"a Jawa will not sow"* has no support.
**Behaviour: still owed** — it needs a route that can set `plantDefToSow`, i.e. leaving the Jawa to
pick the job itself with every other colonist unable to, and enough ticks for it to get round to it.
