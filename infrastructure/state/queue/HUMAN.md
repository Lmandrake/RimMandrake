# HUMAN — pending questions, and Q/A(assumed) pairs from autonomous mode. REP reads.

## Q (CHECK, 2026-08-14): four companion-DLL tools the thruster move proved we need
Owner's standing instruction, given this session: **always raise DLL capabilities as an
option and let the owner judge.** These four are not speculative — each one is a gap that
cost real calls or left a claim unverifiable while relocating the thruster bank.

Ranked. 1 is the one that actually blocks CHECK from closing items.

1. **`jawa/inspect_string`** — `Thing.GetInspectString()` for any `thingId`. Already asked
   for by C13. **CHECK currently cannot answer "is this thruster functional" at all.**
   `get_cell_info` returns `className: "Verse.Building"` and stops; `list_alerts` carries
   nothing about it; the red-slash overlay was proved non-discriminating today (see
   `facts/LIVE.md`). Everything about thruster function is presently geometry + inference.
2. **`jawa/gravship_status`** — the engine's own launch validation in one call: thruster
   count, computed `GravshipRange`, fuel, and the blocking reason strings
   (`CannotLaunchNoThrusters`, `ThrusterBlockedBy`, …). This is the tool that would turn
   "the geometry mirrors a known-good thruster" into "the ship reports it can fly."
   Note `LIVE.md`: buildings from `spawn_batch` arrive **factionless** and the engine
   offers no Launch gizmo on a pawnless map, so this may need a claimed engine to answer.
3. **`jawa/set_thing_rotation`** — rotate a spawned building in place. Today the only way
   to change a thruster's facing is destroy + respawn, which discards hitpoints, stuff and
   quality. Harmless on a scratch map; **destructive on a colony that matters.**
4. **`jawa/can_place`** — `GenConstruct.CanPlaceBlueprintAt` with an **explicit rotation**,
   returning the `AcceptanceReport` text. Measured today: the stock
   `apply_architect_designator` `dryRun` returned `ok=true` for 25/25 cells under god
   mode, **including a cell already occupied by a thruster**. It is not a validator.

All four need the game DOWN to deploy, so they batch into one shutdown window with any
other BUILD companion work. item: (raised from the thruster relocation, no queue ID)

## Q (BUILD, 2026-08-14): B6 was deleted from `queue/BUILD.md` by `f249d67`
`f249d67` ("Every queue item carries a row:") added a `row:` field to every item and
removed `## B6 Deploy the MandrakeJawa xenotype + Jawa_IndigenousTribes set` outright.
It is the only item that commit dropped, and the subject does not claim a deletion, so
this reads as an accident rather than a ruling.

No work was lost: B6 is DONE — the four PawnKindDefs were repaired (`c06e89e`) and
`Jawa_Patches` is deployed `-> VERIFIED in sync`. The live half is carried forward as
`queue/CHECK.md` C31. Flagging it because if the deletion WAS deliberate, C31 should be
withdrawn; and because a mechanical field-adding pass that silently drops an item is
worth knowing about before the next one runs.
