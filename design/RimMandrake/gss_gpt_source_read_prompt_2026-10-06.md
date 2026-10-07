# GPT source read of Gimme Some Slack - prompt (2026-10-06)

You are reading the C# source of a RimWorld 1.6 mod, "Gimme Some Slack" (packageId mandrake.rm.gimmesomeslack).
It draws messy, physically plausible power cords between conduits and devices (a Verse-free core under Core/ planned
and laid by CordGraph/CordPlanner/CordBuilder/CordLayer, adapted from the live map by CordWorldAdapter and drawn by
SectionLayer_RM_MessyCords), overhead aerial power lines between masts/wall brackets (Aerial/, CompAerialAnchor,
RM_MapComponent_Aerial, power taps), and flexible hoses carried out from hose reels by colonists (Hose/, CompHoseReel,
HoseMath, HoseCarry, jobs, RM_MapComponent_Hoses). The files attached are the whole production source except probe and
self-test files.

Find REAL DEFECTS - things that would make the mod behave wrongly for a player or corrupt a save - not style.
Specifically look for:

1. Save/load: state that is not Scribed, Scribed under the wrong mode, or rebuilt differently after a load (a reload
   that changes a cord, hose or span the player already saw); anything that writes a C# class name of ours into a save.
2. Determinism: anything whose result depends on iteration order of a HashSet/Dictionary, Thing id order, frame timing
   or Rand without a pushed seed, where the design wants the same map to draw the same cords.
3. Cache invalidation: a cached cord/hose/span that should be re-planned after a map change (wall built, conduit
   removed, roof, door, explosion) but is not, or is re-planned when it should not be.
4. Hose geometry: the reel's outlet run (HoseMath.Lay with startOutward, OutletLead, StraightenStart, LayOn). A live
   check measured the laid hose's minimum bend radius at ~0.19 cells against a 1.2-cell setting in 9 scenes, and an
   offline fuzz found bends of 0.02-0.4 inside the outlet blend in 965 of 1,445 cases. Is the cause the blend between the
   straightened outlet run and the stiffened curve? Say exactly which lines and why, and what a correct fix is.
   Also: can a laid hose exceed the hose's maximum length (the outlet lead is not counted by CheckInstall)?
5. Player interface: every gizmo (Command_Action/Toggle), float-menu option, designator and settings toggle. Find any
   that does nothing, does the wrong thing, is shown when it should not be (or hidden when it should be shown), fires
   once per selected object when it should fire once, mutates state without the MP-sync path the code says it uses, or
   leaves an order/reservation dangling (cancel, interrupted carry, reel destroyed mid-carry, pawn downed).
6. Threading / lifecycle: work on a non-main thread, MapComponent order issues, null map after despawn, events after a
   thing is destroyed, Harmony patches with wrong signatures or that throw on other mods' things.
7. Settings: a setting whose name says it does X but the code does not (for example sprawlCap does not cap cord length),
   a setting read once and never re-applied, defaults that differ between the field initializer and ExposeData/Reset.

For each finding give: a short title; file and line(s) or method; what goes wrong for the player; how confident you are
(high/medium/low); and how to check it (an offline test or an in-game step). Rank by player impact. Number them.
Do not report anything you cannot point to in the code. Say "none found" for a category you checked and found clean.
