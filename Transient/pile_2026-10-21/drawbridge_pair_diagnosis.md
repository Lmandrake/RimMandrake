# Drawbridge pair diagnosis — 2026-10-21 (BENCH helper, read-only)

Read-only: source + the five `drawbridge_live*.json` runs (mod_hash 5bdf2170…). No game, no bridge. Vanilla read through
RimSage (DutyDef AssaultColony, JobGiver_AIFightEnemy.TryGiveJob, 1.6).

## WINCH_REACH_DIAGNOSE_CANREACH_FIBS

### Mechanism
Site A (origin 140,140): trench at x=1..4, z=0 only; granite walls at z=±1 for x=-2..9 plus caps at (-3,0)/(10,0); timber
leaf (0,0)-(5,0), winch at (-1,0); far pawn at (7,0). The **walls**, not the trench, are what close the banks off from each
other round the trench's ends.

- `WorkGiver_Drawbridge.JobOnThing` (`src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeControl.cs`) never
  checks reach itself. The scanner (and `ProofWorkJob`, mirroring it) asks `pawn.CanReach(winch, Touch, Deadly)` first.
- `CanReach` = vanilla regions AND `RM_Patch_Reachability_SuperdeepVeto` → `RM_SuperdeepTrap.RelativeVeto`.
  - **Vanilla regions** see the trench floor as walkable (depth is a mod concept): far bank → (5,0) → floor 4..1 → lip (0,0)
    → touches the winch. Says reachable.
  - **Pocket grid** is depth-only *by design*: `RM_PocketGridMath.cs` lines 16-17, *"Walkability is deliberately NOT an
    input … Vanilla reachability already accounts for walls, and the reachability seam ANDs the two."* At depth 0 the
    z=±1 wall cells join the two banks round the trench's ends, so `cs == cd`, `DestInComponent` is true and there is no veto.
  - The two answers are each true of their own projection (regions: walls but no depth; pocket grid: depth but no walls).
    Reachability is a property of the joint graph, and **the AND of two projections is not that.** The route regions
    find goes through the trench, and the route the pocket grid finds goes through the walls. A* (`FindPathNow`, cliff
    masks + walls together) sees the joint graph and finds nothing to (-2,0) or to (0,0): both `found=False` in rerun4.
- The proof's own earlier guess (in the `lower_only_from_winch` comments: *"the far pawn could reach the lip by the trench
  floor (Captures carve-out)"*) is **false**. A* refuses the floor route (lip found=False). Keep it there as an
  informative false theory.
- Side note: the cell behind the winch (-2,0) is a one-cell pocket (cap at -3, walls at ±1, the winch at -1). Only the
  winch-bank pawn standing there reaches it. That is fine for this row.

### Verdict
**MOD** (high confidence). The defect is in `RelativeVeto`'s AND-of-projections design, and the drawbridge is where it
surfaces: a wall line plus a moat at the gate is exactly the R7 layout, so in play it is common, not a test artefact. The
symptom: a far-bank colonist takes the lower job, walks, the pather fails, and the job loops. The same false yes applies
to every job giver (hauling, raider GotoNearestHostile, and so on) wherever walls and trench together, but neither alone,
cut a route. That wider root is **separate claimable work** (see below), not fixed by the narrow fix.

### Fix
Narrow, and enough for this row. `RM_DrawbridgeControl.cs`, `WorkGiver_Drawbridge.JobOnThing`: require an executable path
before handing out the job. This is the same test `RM_DrawbridgeRaid.WinchJob` already uses for raiders (R5 *"need an
executable route"*). The cost is bounded: it runs only while a leaf `NeedsHands`, and once per spot per pawn per scan.

```diff
 				if (t.Faction != pawn.Faction || (!forced && t.IsForbidden(pawn)) || !pawn.CanReserve(t, 1, -1, null, forced))
 				{
 					continue;
 				}
+				// WINCH_REACH_DIAGNOSE_CANREACH_FIBS: CanReach is regions AND the depth-only pocket grid; walls + trench can
+				// cut a route neither sees alone. Only A* sees the joint graph.
+				using (PawnPath path = pawn.Map.pathFinder.FindPathNow(pawn.Position, t,
+					TraverseParms.For(pawn, Danger.Deadly), null, PathEndMode.Touch))
+				{
+					if (path == null || !path.Found)
+					{
+						continue;
+					}
+				}
 				Job job = JobMaker.MakeJob(RM_DrawbridgeDefOf.RM_WorkDrawbridge, t);
```
(Keep the order: cheap reserve/forbid checks first, A* last.)

Root (file it as its own item, do not fold it in here): make `RelativeVeto` answer on the joint graph. One option is to
label the pocket grid on walkable cells only, re-dirtied from `RegionDirtyer.Notify_WalkabilityChanged`; that reverses
the line-16 design choice, so it is a design decision. Another is a bounded A* confirm when the veto passes but the
region path crosses a component change. It needs a design note, and the owner or GPT should weigh the cost.

### Proof row
`drawbridge_proof.py --fresh_map --only LOWER_ONLY_FROM_WINCH` after the fix:
- `farLower` = `WORK job=False spot=none raise=False why=refused_at_winch,…` (CanReach still passes and the path test refuses), and
- `winchLower` = `WORK job=True spot=winch` (the winch pawn still gets it; this proves the A* gate is not blanket-refusing), and
- `farRaise` = `job=True` with the leaf lowered (unchanged).
Optional diagnostic to add beside it, which records the fib itself: far pawn `CanReach(winch)=True` with
`ProofPath lip found=False` and the pocket-grid component equal on both banks. That proves the AND shape, and the root
item's eventual fix flips CanReach to False.

## DRAWBRIDGE_RAID_DIAGNOSE_LOITERING_AT_MOAT

### Mechanism
Scene K: island at c=(170,210), a ring at Chebyshev 5..6 dug 4 notches (2 m) all round, a steel leaf east raised, the
winch on the island, **two drafted colonists on the island at (168,210)/(169,210)**, sandbag decoy at (184,214), and 4
`Mercenary_Gunner`s spawned by bridge and put in a `LordJob_AssaultColony` (`jawa/lord_assault_spawn`).

Why each expected signal is structurally zero in this harness:
1. **WinchJobs = 0 by construction.** `Patches/RaiderTrench/FlowWorks_RaiderTrenchDuties.xml` inserts
   `JobGiver_RM_DrawbridgeWinch` only into the **Sapper** and **Breaching** duties. That is the design: R5 says
   *"sappers and breachers aim at the winch"*. An AssaultColony lord never runs it.
2. **PlanksLaid = 0 by construction.** Planks are handed out only in `IncidentWorker_Raid.PostProcessSpawnedPawns`
   (`RM_Patch_Raid_Planks`, with `raidPlankChance`). Pawns spawned by bridge and given a lord never get one.
3. **Trench rules never get a turn.** `JobGiver_RM_CrossTrench` is appended **last** to AssaultColony. In vanilla 1.6 the
   order (RimSage) is: TakeCombatEnhancingDrug, Abilities, **AIFightEnemies (65/72)**, TrashColonyClose,
   TrashBuildingsDistant, GotoNearestHostile, TrashBuildingsDistant(inert), AISapper, then ours. Drafted colonists are a
   visible threat across a 2-cell moat, so for a gunner `JobGiver_AIFightEnemy.TryGiveJob` takes
   `TryFindShootingPosition` → `CastPositionFinder` (a reachable cell on the raiders' bank with LOS). It then returns
   **`Wait_Combat` while standing at it** (`pawn.pather.StopDead()`). "3-9 cells outside the ring, standing still ~1000
   of 3000 ticks" is that exact picture: a gunner at a cast position, firing across the moat. Shooting does not require
   reach (`NeedReachableIfCantHitFromMyPos`).
4. **Site contamination.** In the rerun (scenes A, B, D, E and G also built on the same map) the raiders ended at
   (141..149, 148..166). Those are scenes B and E, where reachable colonists stand (one was *"LEFT DRAFTED"*). That is
   correct vanilla targeting of the nearest reachable enemy, not a stall.

UNMEASURED in the evidence: the samples carry position/dead/downed only. There is no `curJob`, no target and no island
colonist health, so "shooting" (3) is inferred from vanilla code and the shape of the samples, not read. One residual
MOD risk is left unproved. If the island colonists were downed, FightEnemies has no target, and `TryCross` should then
plan a ladder or fill line (`TargetFor` counts downed colonists, and CanReach is false across the full ring). "Nobody
enters the trench" would then point at `TryPlan`/`LadderJob`. The next run's job log settles this.

### Verdict
**HARNESS** (bar and staging), and the standing still is **BY-DESIGN** (vanilla gunners holding a firing position across
an uncrossable moat; vanilla raids do the same at a deep-water moat until the lord times out). Confidence: medium-high.
Points 1, 2 and 4 are certain from code and evidence; point 3 is inferred and needs the job log. The RAID_UP bar asks for
WinchJobs/PlanksLaid from a lord kind and a spawn route that cannot produce them, and it counts no legal progress
(Wait_Combat or AttackStatic across the moat, ranged fire at the winch). Not a MOD FAIL as filed.

### Fix
Change `src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py`, `raid_up` (no mod change):
```diff
-    for k in range(2):
-        spawn((c[0] - 2 + k, c[1]), draft=True)
+    # targets the raiders cannot SEE or reach: behind a closed granite box on the island (FightEnemies has no LOS target,
+    # so the duty falls through to the trench rules, as R5's hand-off intends)
+    ctx["walls"]([...box round (c-3..c-1, c-1..c+1), open only to the island...])
+    for k in range(2):
+        spawn((c[0] - 2 + k, c[1]), draft=False)
-    ids = ctx["assault"]([(c[0] + 25, c[1] + k) for k in range(4)])
+    ids = ctx["assault"]([...], lord="sapper")            # a Sapper/Breaching lord: the winch giver is in those duties
+    dproof("ProofGivePlank"-style give, or a real raid incident, so one raider carries a plank   # PostProcessSpawnedPawns never ran
     ...
-            snap.append((i, x, z, p.get("dead"), p.get("downed")))
+            snap.append((i, x, z, p.get("dead"), p.get("downed"), p.get("job"), p.get("jobTarget")))
```
- Run it `--only RAID_UP --fresh_map` so no other scene's colonists are reachable, or `jawa/kill` every colonist that is not
  on the island before the assault.
- Split the row: **RAID_UP_ASSAULT** (an assault lord, colonists out of LOS) expects the trench-rule job count to rise
  (RM_RaiderSetLadder / RM_RaiderFillTrench / CastJump), with no loop. **RAID_UP_SAPPER** (a sapper lord) expects
  `WinchJobs` to rise. Count `Wait_Combat`/`AttackStatic` aimed across the moat as legal, never as a stall.
- If `ctx["pawns"]` has no job field, the bridge read must add it first: a row that cannot see jobs cannot tell a stall
  from a fight.

### Proof row
`drawbridge_proof.py --fresh_map --only RAID_UP` with the changes above:
- ASSAULT: every sample has a job; no raider is in `Wait_Combat` with no LOS target; the RaiderSetLadder or RaiderFillTrench
  job count rises within 3000 ticks, or a raider is in the ring (`d <= 6`); `HostileJobsEnded <= 3 x raiders`.
- SAPPER: `WinchJobs` rises (melee if reachable, else `Goto` to a cast position or `AttackStatic` on the winch).
- If ASSAULT still shows nobody entering the trench while FightEnemies has no target, **that** is the MOD finding, in
  `RM_RaiderTrench.TryPlan`/`LadderJob`, to be read through `ProofDecision` per raider.
