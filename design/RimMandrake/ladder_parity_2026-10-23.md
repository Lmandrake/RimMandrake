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
| use each other's ladders ("no keys") | A LOWERED wall ladder or any standing portable ladder is a held-open door (Q4 below): every creature that can climb a ladder (Q1 below) climbs it — colonists, raiders, prisoners, wild animals. Kept: a RAISED wall ladder is climbed by nobody (his 2026-10-18 jail ruling). | `ladderNoKeys` on |
| pick up each other's ladders, move them | Portable ladder is `alwaysUninstallable`: a colonist uninstalls a raider's ladder like his own and reinstalls it anywhere. A raider who needs a ladder and carries none takes a standing portable ladder (anyone's, not one his raid set) within reach, into its inventory, then sets it. | `raiderTakeLadders` on, radius 25 squares |
| build ladders on demand, both sides | Colonists: the Architect portable ladder (unchanged), now also placeable against a wall. Raiders, in order (Q2 below): a carried one is SET (4 s + 0.5 s/m); else one standing is TAKEN; else one is BUILT from 12 wood in the inventory (10 s + 1 s/m); else the raider FELLS the nearest grown tree within 30 squares (vanilla cut time: harvestWork / PlantWorkSpeed; the stump stays), keeps the logs, then builds. No tree in reach: no ladder — breach by fill, or jump. | ladder speed (existing), `raiderChopRadius` 30 |
| raiders show up with ladders sometimes, not every raider | Per raid (not a siege, humanlike tool-users, any tech level) a stable roll: the raid brings ladders with chance P; then a share S of its people carry one minified portable ladder in their inventory, at least one, never all (a raid of n ≥ 2 has at most n−1). Dropped on death like any inventory. | P 35 %, S 25 % (PROVISIONAL sliders) |
| digging should be slow | The breach causeway fill: default speed ×0.5 (a gunner ~5,600 ticks a level, up to three to a square). | `raiderFillSpeed` 0.5 (PROVISIONAL) |
| repair damage from digging in | Every level a raider shovels in is remembered per square (the depth before the first fill: a "breach scar", scribed). Designator "Repair breach" (Orders): on a scarred square it places an ordinary dig-to order back to the scar depth; colonists dig it out at the normal (slow) dig cost. A scar clears when the square is that deep again. | `breachRepairEnabled` on |
| one-way over single unroofed walls | A portable ladder stands on open ground against a built wall (wall/fence by def flags, never a door or rock) and faces it. A pawn on the ladder's square climbs over ONE wall square to the far side (one way: back needs a ladder on that side), when the wall and both sides are unroofed (the climbing-gear rule). Colonists: right-click the wall. Raiders with no way in who carry a ladder set it at the wall and go over (the gear seams). Ladder climb: 4 of the pawn's own steps (gear is 20). | `ladderOverWalls` on, slow factor 4 |

What changes: raiders — may use, take and carry ladders; arrive with some; dig slower. Colonists — may use and uninstall
raider ladders, set portable ladders on walls, repair breaches. A trapped enemy now walks out up any lowered ladder: the
jail is the RAISED wall ladder (his rule), and a pit with a portable ladder in it is open to everyone.

Not auto-routed: gear-wearers' "route over walls when shorter" planner does not plan ladder crossings (an order or a
raider with no way in uses them).

## The owner's answers (2026-10-23, 06:03 PDT, recorded on the item) and what was built

**Q1 — who climbs.** *"Needs a per-creature evaluation, unfortunately. Many mechs, droids, humans, animals should be able to
climb, jump up alone, or slither along a ladder as long as they fit in a 1x1 cell area. Bigger things no, wheeled things no,
and many creatures without arms no."* Rule (`RM_LadderParityMath.ClimbEligible`, traits read once per race by
`RM_LadderParity.TraitsOf` from the body, never a name list): a per-def `RM_LadderClimber` extension wins; else the pawn's body
size ≤ 1.2 (`ladderMaxClimberBodySize`, PROVISIONAL), no part named wheel/tread/track, and a way up — arms (a
`ManipulationLimbCore` part that is not a mouth: vanilla tags `SnakeMouth` EatingSource + ManipulationLimbCore), a jump
(`RM_PitTravelExtension.jumps`), or a body that is its own moving limb (the core part is `MovingLimbCore`, vanilla `SnakeBody`:
slithers). Everyone, colony animals too. Census of all 2,309 race defs and the 435 borderline rows for a judge:
`design/RimMandrake/ladder_climbers_2026-10-23.md` (a judge's ruling becomes an `RM_LadderClimber` extension).

**Q2 — ladder cost.** *"They don't carry wood, they look for something to chop down, get the wood, then build it.
Destructive."* Built as in the table (chop → build); "or a wooden thing" (furniture, walls) is NOT taken apart: trees only.

**Q3 — numbers.** Kept (35 %, 25 %, ×0.5, 4 steps; 1.2 body size and 30-square chop radius are new and provisional).

**Q4 — prisoners.** *"A prison ladder left down is equivalent to a prison door left open... same game rules apply."* Vanilla
1.6 (decompiled): `Building_Door.CanPhysicallyPass(p)` is `FreePassage || PawnCanOpen(p)` (else only a hostile through an open
door); `FreePassage` is an open door held open; `PawnCanOpen` refuses a prisoner of the door's faction
(`GenAI.MachinesLike`: `p.IsPrisoner && p.HostFaction == machineFaction` → false). So a held-open door lets EVERY pawn through,
prisoners included, and `JobGiver_PrisonerEscape.ShouldStartEscaping` sends a secure prisoner out when its district reaches
the map edge through regions whose door is null or `FreePassage` (≤ 25 regions), going to `RCellFinder.TryFindBestExitSpot`,
which checks `pawn.CanReach`. Built: a lowered ladder (no keys) is climbable by every climber, prisoners included, so the pit
pathing's reachability now lets that vanilla escape job through a lowered ladder exactly as through a held-open door; a RAISED
ladder is still nobody's (his 2026-10-18 jail ruling: a raised ladder is no closed door a colonist opens, it is gone). During a
prison break vanilla lets prisoners open any door (`LordJob_PrisonBreak.CanOpenAnyDoor`); a raised ladder still holds them.
With "no keys" off, the old prison-door rule returns.

## Still open
1. The 435 judge rows in the climber census (a judge agent, not him: delegated taste/fact calls).
2. Whether a raider should also tear down wooden structures for ladder wood when no tree is in reach (built: trees only).
