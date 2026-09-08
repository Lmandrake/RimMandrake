# RimMandrake Pits — validation walk
subject: src/RimMandrake/Pits  (packageId `mandrake.rm.pits`)
deps: none (Ludeon.RimWorld only)
list: minimal
status-hint: species-agnostic covered-pit-trap framework — dig a pit in stages, arm a terrain-mimic cover, mass crossing it springs the trap and drops the walker in; a gated pit-cell variant doubles as prisoner holding

## must be true
- A `Building_PitDigSite` (e.g. `RM_PitDigSite_Shallow_Bare`) advances through dig stages via `CompPitDigStage` and, on completion, becomes/spawns its paired `Building_OpenPit` (e.g. `RM_OpenPit_Bare`).
- An armed `Building_OpenPit`'s `CompPitCoverTrigger` springs (`Sprung=true`) only once the summed mass of pawns standing on it, EXCLUDING pawns sharing the pit's own faction, reaches `CoverTier.TriggerMassKg()` — a same-faction colonist crossing an armed pit must NOT spring it.
- A pawn held in a sprung pit accrues `RM_PinnedInPit`, and depending on the fitting tier, `RM_PitExposure` or `RM_PitDrowning` hediffs, with escape scored by `PitEscapeUtility.EscapeChance` off bodysize/health/manipulation (not a coin flip).
- `Building_PitCell` (prisoner holding variant: `RM_PitCell_Single`/`RM_PitCell_Double`) can be assigned a prisoner, placed into the cell, and its gate toggled (`GateClosed`) — closing the gate is protective, leaving it open under the sun is not.
- Oiled fitting (`CompPitFitting` with `PitFittingType.Oiled`) can ignite once soaked, independent of the Sprung gate.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.pits" and no XML error naming `Pit_DigSites.xml`/`Pit_OpenPits.xml`/`Pit_Hediffs.xml`   # load-time
2. [D] def read-back: `ThingDef` `RM_PitDigSite_Shallow_Bare` exists; its `CompProperties_PitDigStage` names `openPitDef` = `RM_OpenPit_Bare`, `depthTier` = `Shallow`
3. [D] def read-back: `HediffDef` `RM_PinnedInPit` exists, label "pinned in pit"; `RM_PitExposure` exists, label "pit exposure"; `RM_PitDrowning` exists, label "drowning"
4. [D] def read-back: `WorkGiverDef` `RM_DigPitDeeper` exists; `giverClass` = `RimMandrake.Pits.WorkGiver_DigPitDeeper`; `workType` = `Mining`
5. [B] jawa/spawn_batch `defName=RM_PitDigSite_Shallow_Bare` at a known cell on the current map → expect the thing to appear (confirm with jawa/list_things `defName=RM_PitDigSite_Shallow_Bare`)
6. [B] rimworld/execute_debug_action `{path naming "RMPits/Advance dig stage", x, z}` on the dig-site cell → Player.log line `[RMPitsDebug] DIG was[...] nowAt=...` names the site advancing stages
7. [B] rimworld/execute_debug_action `{path naming "RMPits/Arm cover: woven scrap (40kg)", x, z}` on the resulting open pit → Player.log line `[RMPitsDebug] ARM ... covered=True coverTier=WovenScrap triggerMassKg=40.0`
8. [B] jawa/spawn_pawn a hostile-faction pawn onto the armed pit cell, then rimworld/execute_debug_action `{path naming "RMPits/Force trigger scan now", x, z}` → Player.log line `[RMPitsDebug] SCAN_DONE ... sprung=True` (when the spawned pawn's mass clears the tier threshold)
9. [B] rimworld/execute_debug_action `{path naming "RMPits/Report pit state (RAW)", x, z}` on the sprung pit → Player.log shows `WOULD_SPRING=True`, a `HELD` block for the caught pawn with non-empty `hediffs=[...]` including `RM_PinnedInPit:...`
10. [B] repeat step 8-9 with a PLAYER-faction pawn instead of hostile → expect `counted=False` for that pawn in the REPORT_PIT `STANDING` line and no spring from that pawn alone (faction-exclusion check named in the .cs as a fixed bug)

## anti-guessing notes
- `RMPits`/`Report pit state (RAW)` etc. are DebugActionType.ToolMap leaves — not separately named jawa/ tools — so they are reached through the verbatim tool `rimworld/execute_debug_action`, which the tool list documents as executing "including ToolMap actions targeted by cell". The exact `path` string was not independently confirmed against a live `rimworld/search_debug_actions` call in this authoring pass; resolve it with that tool before running the walk (category constant is literally `"RMPits"` in `src/RimMandrake/Pits/Source/Debug/PitDebugActions.cs`).
- No [S] line: the mass-trigger and escape mechanics are the whole point and are fully script-checkable; nothing here is visual-only.
