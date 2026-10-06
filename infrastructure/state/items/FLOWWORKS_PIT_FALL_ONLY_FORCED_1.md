# FLOWWORKS_PIT_FALL_ONLY_FORCED_1 — who falls into a pit, and when

## ruling (owner, 2026-10-06, typed on a question card)

*"You can't fall in by careless colonist pathing. Only if they get blown/forced in do they fall. Enemies can fall if the pit is concealed or they are forced/blown in."*

## what

- Colonists never path into a pit by accident; they fall (with fall damage) only when blown or forced in.
- Enemies fall when the pit is concealed, or when blown or forced in.

Code today: fall damage is gated on `RM_SuperdeepTrap.Captures(p)`, which excludes the player faction unless a setting is on or the pawn is a jumper (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:56-69, 211, 313`). Review key sheet stop 19 (`northstar/review/map/KEYSHEET.md:211-221`) says a colonist walks in, is hurt and climbs out, which contradicts this ruling and must be corrected. Check: forced/blown entry (knockback, explosion push) reaches the fall path for colonists; concealment (pit cover) is what lets enemies path in.

Found by the 2026-10-06 GPT playtest review, finding #7 (`design/RimMandrake/flowworks_playtest_automation_2026-10-06.md`).
