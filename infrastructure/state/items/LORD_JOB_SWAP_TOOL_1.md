# LORD_JOB_SWAP_TOOL_1 — rewrite what an AI group is doing, mid-flight

Row 1 of 5 split out of `BRIDGE_TOOLS_HARD_BLOCK_1`. 🔑 **The only one of the five that pays
for itself soon** — it is what raid scripting needs and there is no other route to it.

## spec
`Lord.SetJob(LordJob newJob, bool loading)` then `Lord.GotoToil(lord.Graph.StartingToil)`.

⚠️ **The two calls are ONE operation and neither is safe alone.** A Lord is a running state
machine with a graph, transitions and per-pawn duties; `SetJob` swaps the graph but every pawn
keeps a duty issued by the OLD one until a toil is re-entered. A tool that calls only `SetJob`
leaves a group visibly obeying orders that no longer exist.

## What the tool must do that the engine will not
- Read back **which Lord** was changed, its pawn count, and the toil it landed in — a Lord id
  alone is not evidence.
- Name the halfway state in the result: if `GotoToil` throws after `SetJob` succeeded, the group
  is in the new graph with old duties, and the tool must SAY so rather than return a failure that
  reads as "nothing happened".
- Refuse a Lord with zero pawns, and a `LordJob` whose graph does not build.

## verify
`build.py --gm` clean, the new name in the built tool list, no existing `[Tool]` name changed.
Then live: swap a raid Lord's job and read back that every pawn's `duty` comes from the NEW graph.

## criteria
- [ ] Both calls in one tool; a partial application is reported, never silently returned as failure.
- [ ] Read-back names the Lord, its pawns and the resulting toil.

---

# ✅ WRITTEN AND COMPILED 2026-08-27, seat BUILD. ⛔ NOT DEPLOYED — the game is up.

`jawa/lord_set_job`, in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchLordJobTools.cs`.
Gated behind `JAWA_GM_TOOLS` on `lord_poke`'s test. Build `--gm`: **0 warnings, 0 errors**;
built tool surface 237, `jawa/lord_set_job` present, none lost.
Evidence: `infrastructure/state/evidence/BRIDGE_TOOLS_BATCH_2026-08-27.txt`.

## Against this item's criteria
- **Both calls in one tool; a partial application is reported.** `SetJob` then
  `GotoToil(Graph.StartingToil)`. Three separate failure points after `SetJob` succeeds —
  `Graph.StartingToil` throwing, a graph with no starting toil, and `GotoToil` throwing —
  each return `partiallyApplied: true` with the sentence *"the Lord is in the NEW graph
  with pawns still carrying duties from the OLD one"*, never a bare failure.
- **Read-back names the Lord, its pawns and the toil.** `lordIndex`, `lordLoadID`,
  `faction`, `pawnCount`, `jobBefore`/`jobAfter`, `toilBefore`/`toilAfter`,
  `graphToilCount`, and per-pawn `dutyBefore`/`dutyAfter` with `dutiesChanged`.
- **Refuses a zero-pawn Lord** (LordManager removes an empty Lord on its own tick, so a
  job set there is discarded) **and a LordJob whose graph does not build** — `CreateGraph`
  and `graph.ErrorCheck` both run inside `SetJob`, so that failure lands before anything
  is disturbed and the refusal says the Lord still holds its old job.

## 🔑 Two decisions a reviewer should see, not infer
- **Constructor args bind BY NAME**, and a name matching no parameter is **refused with
  the accepted names listed** — never dropped. Supported conversions: string, bool, int,
  float, enum, `Faction` (screen name or FactionDef), `IntVec3` (bounds-checked), `Map`,
  any `Def`. Anything else is refused **by type name**.
- **It will not fall back to a parameterless constructor.** `LordJob_AssaultColony` has
  one, for Scribe loading, and it leaves `assaulterFaction` null — read `CreateGraph` and
  every flee, kidnap and steal transition is inside `if (assaulterFaction != null && ...)`.
  So the easy construction gives a graph that builds, error-checks clean, and behaves like
  a different job. That is the trap this refusal exists for.

## Validation plan — run it in the deploy window
```
ITEM     jawa/lord_set_job — hand a landed raid a new state machine
SEE      One raid Lord's jobAfter reading LordJob_ExitMapBest where jobBefore read
         LordJob_AssaultColony, and every pawn's dutyAfter differing from dutyBefore
ROUTE    Minimal list. Start a quicktest map, fire a raid, then:
           jawa/lord_pawn_move {action:"list"}            -> pick the raid's lordIndex
           jawa/lord_set_job {lordIndex:N, loadID:<its loadID>,
                              lordJob:"LordJob_ExitMapBest"}
PREDICT  success true, dutiesChanged == pawnCount, toilAfter naming a LordToil_ExitMap
CLOSE    One swap that changes duties, AND one deliberate refusal — pass
         lordJob:"LordJob_AssaultColony" with no args and confirm it REFUSES with the
         signature list rather than silently building the faction-null version
RIDE     batch — companion DLL, rides the same game-down window as bridge_arg_report
LIES     🔴 dutiesChanged == 0 is NOT proof of failure: a toil may legitimately re-issue
         the same duty def, which is why the result carries dutiesUnchangedNote. Read
         toilAfter and jobAfter to settle it.
         🔴 And a deployed DLL registers NOTHING until the game restarts, so "tool not
         found" after a load that predates the deploy is not a failure of the tool.
```

## Watch out
- ⚠️ **`lordIndex` is positional and shifts** as groups form and die. Pass `loadID` too —
  it is checked and the call is refused on a mismatch. This is the only identity assertion
  available; a Lord has no defName.
- ⚠️ **Modded LordJobs work** (`GenTypes.GetTypeInAnyAssembly`), and their constructors
  have no compatibility promise at all. The signature list in a refusal is the instrument.
- 🔴 **Gated.** A build without `--gm` does not contain this tool, and its absence from a
  tool list means the gate, not a failed deploy.
