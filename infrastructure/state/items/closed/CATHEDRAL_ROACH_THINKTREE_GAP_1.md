# CATHEDRAL_ROACH_THINKTREE_GAP_1 — RUT_CathedralRoach's land-cleaning node likely never fires

## 2026-09-12 (FOUNDRY, offline subagent, descended from RUST_CATHEDRAL_MECHANICS_1 §3)

Found while building §3's `RUT_LivingBolt` (own ThingDef, mechanoid flesh):
`RUT_LivingBolt` needed its own main `ThinkTreeDef` because
`BaseMechanoidWalker` (vanilla `Mechanoid`'s think-tree base) carries **no
`insertTag` at all** — the `Animal_PreMain` insertion route
`mandrake.rm.creaturebehaviors` uses to graft custom animal behavior nodes
(e.g. `RM_ThinkNode_EatCleanable`) has nowhere to attach on a
mechanoid-tree pawn.

`RUT_CathedralRoach` (§6 of the same kit) is built the same way — a
mechanoid-fleshed wild-fauna race — and is **already deployed and ENABLED
live**, `mandrake.rut.rustcathedralroaches` confirmed present in the
running `ModsConfig.xml`'s 592/593 active mods. If it relies on the same
`Animal_PreMain`/`RM_ThinkNode_EatCleanable` route for its land-cleaning
wastepack-eating behavior (the mechanic's whole point per the design doc,
§6: "roaches... seek and eat wastepack"), that behavior is plausibly dead
in the shipped game right now — built, deployed, and silently doing
nothing, exactly the class of failure this repo's own doctrine warns about
("plausible answers nobody disbelieved").

**Not confirmed live** — this is inference from the think-tree structure,
not an observed failure. Confirming needs a live check (see below).

## spec
Confirm whether `RUT_CathedralRoach` pawns actually execute
`RM_ThinkNode_EatCleanable` (or whatever its land-cleaning node is) in a
live/quicktest game. If confirmed dead, give the roach the same fix
`RUT_LivingBolt` got: its own main `ThinkTreeDef` (or another insertTag-
compatible route) so the eat-cleanable behavior actually reaches the pawn's
think tree.

## verify
A live quicktest map with `RUT_CathedralRoach` spawned and wastepack
present shows the roach actually pathing to and eating the wastepack
(behavior log or direct observation), not just spawning and idling/wandering.

## criteria
`RUT_CathedralRoach`'s land-cleaning behavior is confirmed either already
working (this note is wrong, close as a non-issue) or fixed and confirmed
working live.
