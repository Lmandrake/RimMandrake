## spec
Owner 2026-10-18, card Q7 ("Raiders reach a trench they cannot cross → Go around, and breach if no way") and his words:
"(4) plus some may have jump packs to cross. Ladders make sense for shallower pits (they could start building them in
preparation). Siege raids still work fine with mortars."

Built offline (3f540054fa source, f56dafaf3f DLL): `src/RimMandrake/FlowWorks/Source/Superdeep/RM_RaiderTrench.cs` (Verse),
`RM_RaiderTrenchMath.cs` (pure rules), `Patches/RaiderTrench/FlowWorks_RaiderTrenchDuties.xml` (JobGiver_RM_CrossTrench
appended to AssaultColony, after JobGiver_AIBreaching in Breaching and after JobGiver_AISapper in Sapper),
`Defs/Canals/JobDefs/FlowWorks_RaiderTrench.xml`, the own-faction ladder exemption in `RM_LadderRules.LadderLetsOut` and in
`RM_PitPathing.ClosedLaddersFor`, and the "Raiders against trenches" Mod Settings section. Selftests:
`Source/SelfTest/RaiderTrenchChecks.cs` (6 cases).

Order, when NO colonist (else colony building) is reachable even through destroyable things and the target is on another
climb-band component: jump (jump pack or leaping ability, landing in range) → scaling ladders (every wall on the crossing line
within the portable ladder's reach) → breach by shovelling the least fill that makes a one-square causeway climbable. A
reachable target means vanilla goes around. Sieges (LordJob_Siege), trapped raiders, flyers and gear-wearers never use it.
A raid on a map with 20+ dug squares hands 10% (PROVISIONAL) of an industrial-or-better raid's people a jump pack.

Robust to either P2 outcome (`PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`): if raiders turn out to reach the colony, the giver
returns null and vanilla acts; if they stall (day-3 STALL_FAR), it acts.

Known limit: surface-to-surface across a trench is never one reachability hop (RelativeVeto), so after the ladders stand the
raider is sent into the trench and vanilla takes over from there. Colonists crossing by two ladders hit the same veto.

## criteria
- A1 L0: decision order, line, fill causeway, ladder slots, times, jump share and wiring pass offline (RaiderTrenchChecks, 6/6)
- A2 L2: a raid against a base ringed by a sheer 2 m trench no longer stalls: raiders set a ladder down and up and walk in
- A3 L2: a 4 m trench (past the 3 m portable reach) is breached by fill: the causeway forms and the raid crosses it
- A4 L2: a jump-pack raider jumps the trench and lands on its feet (no fall hediff), then fights
- A5 L2: a siege against the same base only builds and shells; no ladder, fill or jump job
- A6 L2: destroying a raider ladder strands the raiders below in the pit (held, trap rules apply)
- A7 L2: a colonist in the trench climbs out by a raider's ladder (your people climb any lowered ladder), and another hostile faction cannot
