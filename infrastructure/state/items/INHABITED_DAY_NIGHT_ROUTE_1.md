## spec
§6. ROUTE is barracks → worksite → barracks across a day.
🔴 **DO NOT BUILD A StateGraph WITH TRANSITIONS.** `Lord.ExposeData_StateGraph`
serialises toils by **positional index** and re-runs `CreateGraph()` on load, so
changing toil ORDER silently corrupts existing saves. Vanilla's own graphs are
safe only because they never change; ours will be re-tuned.
⇒ **ONE `LordToil` that reassigns duty on a tick.** The schedule becomes ordinary
C# inside that toil and can be edited freely forever.
  `src/Jawa/Inhabited/Source/LordToil_InhabitedRoutine.cs`
  `src/Jawa/Inhabited/Source/JobGiver_SleepAtNight.cs`  (~30 lines, §6)

## verify
`dotnet build` clean; a save taken mid-routine reloads with the Lord intact and
the same toil index.

## criteria
watch a cast over one in-game day — they work by day and are in the barracks at
night, and a save/load mid-day does not scatter them.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

built 2026-08-20, `f0a9f6c`. Build clean. The watch-a-day half is CHECK's, filed
as `INHABITED_ROUTE_ONE_DAY_1`.
🔑 **The graph is ONE toil and must stay one forever.** `LordJob_Inhabited.
CreateGraph()` returns a `StateGraph` whose only toil is
`LordToil_InhabitedRoutine`; there are no transitions and no `LordToilData`, so
nothing in this job is index-serialised at all. The stance field is deliberately
NOT scribed — on load `CreateGraph()` rebuilds the toil, the field returns to its
default and the next reassess reassigns. Self-healing by construction.
⭐ **The ROUTE is the DUTY'S FOCUS moving, not the duty changing.** One `DutyDef`,
`Inhabited_Resident`, modelled on Core's `DefendBase` from
`Data/Core/Defs/DutyDefs/Duties_NonPlayerHome.xml`, with `JobGiver_SleepAtNight`
inserted above the `SatisfyBasicNeeds` subtree. The toil moves the focus between
the worksite (day) and the barracks (night) every 600 ticks, and pins it to the
pawn's own position while `lord.lastPawnHarmTick` is recent — a cast under fire
does not walk to the barracks because the clock said so.
⚠️ **`ThinkNode_Priority` takes its subnodes IN ORDER**, not by `GetPriority`, so
the XML order is the behaviour: fight back -> turn in at night -> eat and rest ->
keep warm -> wander. Re-tuning means moving a line in that file.
