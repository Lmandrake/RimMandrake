# ORDERED_JOB_CANNOT_SOW_1 — the job is accepted and dies in its first toil

Measured live 2026-08-26 and confirmed against 1.6 source, not inferred.

```
jawa/ordered_job {pawnId: <jawa>, jobDef: "Sow", targetAX: 124, targetAZ: 192}
  -> accepted: true, afterJobDef: "Wait", nowRunningRequested: false, ticksElapsed: 0
  cell after 7,000 stepped ticks, with every other colonist DRAFTED: empty
```

## Why, from the source

`Verse/AI/Job.cs:63` — `public ThingDef plantDefToSow;`
`RimWorld/JobDriver_PlantSow.cs:27` — the driver's **first toil**:

```csharp
.FailOn(() => PlantUtility.AdjacentSowBlocker(job.plantDefToSow, base.TargetA.Cell, base.Map) != null)
.FailOn(() => !job.plantDefToSow.CanNowPlantAt(base.TargetLocA, base.Map))
```

`jawa/ordered_job`'s entire parameter set is
`count · jobDef · jobTag · pawnId · queue · targetAId/X/Z · targetBId/X/Z · timeoutSeconds · waitTicks`.
**Nothing sets `plantDefToSow`**, so it is null, and the driver dereferences it before doing anything.

⇒ **Every `Sow` this tool issues is accepted and immediately dead.** The same applies to `Replant`
and `PlantSeed`, which read the same field (`WorkGiver_Replant.cs:69`, `WorkGiver_PlantSeed.cs:59`).

## ✅ The tool is honest about it, and that is why this was findable

It reports `accepted` separately from `nowRunningRequested`, gives `beforeJobDef`/`afterJobDef`, and
says in its own note: *"Job was accepted (enqueued) but curJob after N tick(s) is 'Wait', not 'Sow'."*
⛔ A tool that had returned a bare `success: true` would have produced a confident wrong finding about
whether a Jawa can farm.

## What to add

An optional `plantDef` (and more generally a way to set the handful of `Job` fields that drivers
require: `plantDefToSow`, `count`, `haulMode`, `bill`). Refuse a `Sow` with no `plantDef` **at the
tool**, naming the field, rather than letting the engine fail silently in a toil.

⚠️ **Related, same session, worth fixing together:** `waitTicks` does nothing while the game is
PAUSED — `ticksElapsed` comes back `0` however long you ask for, because no ticks pass. Either step
internally or say so in the refusal.

Found while trying to grade `LIVE_HALF_OF_LOAD_1` J4.
