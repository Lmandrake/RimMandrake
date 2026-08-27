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
