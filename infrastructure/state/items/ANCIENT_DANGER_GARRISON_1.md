## spec
DROPPED before anyone picked it up. It was filed on a premise the owner
rejected the same day: it treated the Mechanoid FACTION as something that
might go away, and built a live-game check around protecting it.
🔴 Owner, 2026-08-20: "We're not removing Mechanoids." The faction stays, in
full. Only the vanilla `PursuingMechanoids` SCENARIO PART is removed, which is
not the faction and does not gate ancient dangers — those populate by a
predicate over pawn kinds (`allowInMechClusters`, `isFighter`, `combatPower`),
never by `pawnGroupMakers` or by the pursuit.
Keeping `Mechanoid` ticked at worldgen is already covered by
`infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`, which lists it and warns
that unticking it deletes one of our factions. Nothing here needed a load.

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

dropped — premise rejected by the owner; no live check is owed
