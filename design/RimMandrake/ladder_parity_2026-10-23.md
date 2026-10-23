# Ladder parity — design (LADDER_PARITY_BUILD_NO_KEYS_REQUIRED)

Owner by card 2026-10-23, option (4) "Full parity both ways", his words: *"It's (4). We need a way to repair damage
caused by people digging their way into a pit. Digging should be slow. Building ladders available to both sides on
demand. Both sides should be able to use each other's ladders: makes NO sense otherwise (what are they locked with a
key?). Can pick up each other's ladders too and move them. Raiders should show up with ladders sometimes but not always,
and certainly not on every raider. Ladders should work to climb one-way over single walls without roofs as well."*

Pure rules: `FlowWorks/Source/Superdeep/RM_LadderParityMath.cs` (selftested, `SelfTest/LadderParityChecks.cs`).
Settings: one screen section, "Ladders: no keys" (`RM_LadderParitySettings`), defaults = this ruling; all off = the
behaviour before 2026-10-23.

| his clause | mechanic | default / setting |
|---|---|---|
| use each other's ladders ("no keys") | A LOWERED wall ladder or any standing portable ladder is climbed by every pawn of a faction, hostile or not. The faction lock (`ClimbsOwnLadder`, the "trapped enemies cannot" half of the prison-door rule) goes. Kept: a RAISED wall ladder is climbed by nobody (his 2026-10-18 jail ruling); prisoners only in a prison break; wild animals never. | `ladderNoKeys` on |
| pick up each other's ladders, move them | Portable ladder is `alwaysUninstallable`: a colonist uninstalls a raider's ladder like his own and reinstalls it anywhere. A raider who needs a ladder and carries none takes a standing portable ladder (anyone's, not one his raid set) within reach, into its inventory, then sets it. | `raiderTakeLadders` on, radius 25 squares |
| build ladders on demand, both sides | Colonists: the Architect portable ladder (unchanged), now also placeable against a wall. Raiders: one carried is SET (4 s + 0.5 s/m); none carried and none to take: BUILT on the spot from scrap, no materials (10 s + 1 s/m, the 2026-10-18 time). | ladder speed slider (existing) |
| raiders show up with ladders sometimes, not every raider | Per raid (not a siege, humanlike tool-users, any tech level) a stable roll: the raid brings ladders with chance P; then a share S of its people carry one minified portable ladder in their inventory, at least one, never all (a raid of n ≥ 2 has at most n−1). Dropped on death like any inventory. | P 35 %, S 25 % (PROVISIONAL sliders) |
| digging should be slow | The breach causeway fill: default speed ×0.5 (a gunner ~5,600 ticks a level, up to three to a square). | `raiderFillSpeed` 0.5 (PROVISIONAL) |
| repair damage from digging in | Every level a raider shovels in is remembered per square (the depth before the first fill: a "breach scar", scribed). Designator "Repair breach" (Orders): on a scarred square it places an ordinary dig-to order back to the scar depth; colonists dig it out at the normal (slow) dig cost. A scar clears when the square is that deep again. | `breachRepairEnabled` on |
| one-way over single unroofed walls | A portable ladder stands on open ground against a built wall (wall/fence by def flags, never a door or rock) and faces it. A pawn on the ladder's square climbs over ONE wall square to the far side (one way: back needs a ladder on that side), when the wall and both sides are unroofed (the climbing-gear rule). Colonists: right-click the wall. Raiders with no way in who carry a ladder set it at the wall and go over (the gear seams). Ladder climb: 4 of the pawn's own steps (gear is 20). | `ladderOverWalls` on, slow factor 4 |

What changes: raiders — may use, take and carry ladders; arrive with some; dig slower. Colonists — may use and uninstall
raider ladders, set portable ladders on walls, repair breaches. A trapped enemy now walks out up any lowered ladder: the
jail is the RAISED wall ladder (his rule), and a pit with a portable ladder in it is open to everyone.

Not auto-routed: gear-wearers' "route over walls when shorter" planner does not plan ladder crossings (an order or a
raider with no way in uses them).

## Open questions for the owner (built on the most literal reading; flip in settings)
1. Does "no keys" include a hostile raid's animals and mechs? Built: yes, any pawn with a faction (wild animals still no).
2. Raiders build a ladder with no materials (scrounged). Should they need wood they carry?
3. Numbers: raid-brings-ladders 35 %, carriers 25 %, causeway fill ×0.5, ladder wall climb 4 steps — all provisional.
4. Should prisoners also lose the prison-door rule (built: no — prisoners still only climb in a prison break)?
