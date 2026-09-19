# DROIDWORKS_PERSONALITY_VERIFY_1

Live-verify the chassis personality bias shipped in DROIDWORKS_CHASSIS_PERSONALITY_1
(commit a64a1022): per-family forced traits + protocol pedantry.

## Why this item exists

DROIDWORKS_CHASSIS_PERSONALITY_1 was closed 2026-09-09 with its own close-note
saying "Live verify (20 spawns/family show the bias) still owed, needs bridge/game"
— and no item carried the debt, so nothing would ever trigger the check. The same
note flags the trait pairings as FOUNDRY's unruled judgment call; if they are wrong,
this verify is the only thing that will catch it. Filed from the ultra code review
sitting, 2026-09-09.

## What a verify run is

- Bridge up, any scratch map (quicktest fine — this is not campaign-attributable).
- Spawn 20 pawns per droid family and read traits back per pawn.
- PASS: each family shows its forced trait(s)/pedantry at the designed rate.
- Record per-family counts, not an aggregate.

## Traps

- The spawn tool substitutes pawn kinds silently — verify the ACTUAL spawned kind
  per pawn, not the requested one, or the census is void (this exact confound kept
  the bare-hands defect open for days).
- One pawn proves nothing; the 20/family batch is the point.
