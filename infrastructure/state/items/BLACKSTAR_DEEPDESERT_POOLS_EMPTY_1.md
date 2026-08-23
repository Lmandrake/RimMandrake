## spec
🔴 **Eight bare-handed spawns are OUR defect, and they are concentrated in two families.**
DECIDE ruled 2026-08-22 that pool integrity is an **absolute** bar — a pawn that spawns
bare while its backstory permits violence is a defect, and the acceptable count is **zero**.
Ruling: `design/Jawa/worldbuilding/pawnkind_roster.md`, *"Who may arrive unable to fight"*.

Measured 2026-08-21, 240 spawns
(`observed/2026-08-21/armed_sweep_48/rolls.json`):

| family | rolls | bare | pacifist | unexplained |
|---|---|---|---|---|
| **Blackstar** | 20 | 5 | 0 | **5** |
| **DeepDesert** | 20 | 4 | 1 | **3** |
| the other ten families | 200 | 18 | 18 | **0** |

Six kinds carry all eight:
`Jawa_Blackstar_Heavy · _Leader · _Specialist`, `Jawa_DeepDesert_Grunt · _Leader · _Specialist`.

⭐ **Ten of twelve families are clean. Do not work this as a roster-wide tag problem.**

⚠️ **The same two families are the ones `ORPHANED_ROLE_KINDS_UNFIELDED_1` found fielded by
no FactionDef.** Suggestive, but they are different defects — unfielded is wiring, an empty
pool is tags. Fixing one leaves the other.

⚠️ `ORPHANED_ROLE_KINDS_UNFIELDED_1` reports the DeepDesert kinds spawning gaderffii sticks
and Tusken cyclers on hand-spawn. Both measurements are live. Reconcile them before
concluding the pool is empty rather than intermittently empty.

## verify
For each of the six kinds, resolve its `weaponTags` against the surviving item set
post-cut and post-patch, then spawn 20 and count bare rolls with a non-pacifist backstory.

## criteria
Zero unexplained bare rolls across the six kinds in 20 spawns each, with the other ten
families' bare counts unchanged.

## watch out
⚠️ Likely a casualty of `RESTORE_VANILLA_GUN_TAGS_1` / the vanilla firearm cut. Check the
tag→surviving-item index rather than the raw mod XML.
