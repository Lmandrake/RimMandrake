# FLOWWORKS_LADDER_RAISE_LOWER_1

Owner, 2026-10-06 21:40, typed into a question card (verbatim):

> Ladders should be able to be raised and lowered (two states for the ladder). Someone needing to enter the pit from
> the top will descend the ladder and access the contents. The ladder should be clickable by the user: ladder up,
> ladder down. No need to have the colonists automatically move them up and down.

## spec
- `RM_Ladder` gets two states, raised and lowered, toggled by a player gizmo (ladder up / ladder down). Colonists never toggle it themselves.
- Lowered: pawns may path down into the pit and back out by it; haulers can fetch items lying on the pit floor (Explosive Knockback throws items and corpses into pits).
- Raised: nobody climbs it; a held pawn cannot escape by it (existing hold/ladder-release behaviour keyed to the lowered state).
- Each state needs its own art (art commission 2026-10-06 queued the ladder; add a raised variant).
- Runner scenes: toggle both ways via the gizmo; a hauler fetches an item from the pit floor only when lowered.
