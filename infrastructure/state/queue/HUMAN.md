# HUMAN — pending questions, and Q/A(assumed) pairs from autonomous mode. REP reads.

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
