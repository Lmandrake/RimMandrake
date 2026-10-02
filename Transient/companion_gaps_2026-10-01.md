# NORTHSTAR_COMPANION_GAPS_1 work notes (2026-10-01)

Status: BUILT + selftested, NOT deployed, NOT live-proven. Worktree /tmp/wt_comp. BUILD + selftest only; no deploy, no live game.

## Already existing (checked against every [Tool("jawa/...")] in source)

None of the five existed. Near-misses: jawa/list_pawns (no mental/job/lord),
jawa/pawn_mental + jawa/pawn_break_thresholds + jawa/pawn_need (one pawn per call),
jawa/incident_queue_clear (all-or-nothing, GM-gated), jawa/lord_* (write tools, no read).

## Engine APIs confirmed via RimSage (1.6 source)

IncidentQueue.queuedIncidents (private List<QueuedIncident>, no per-item remove) ·
QueuedIncident.FireTick/FiringIncident/RetryDurationTicks/TriedToFire · FiringIncident.def/parms/source/sourceQuestPart ·
IncidentParms.target/points/faction/forced/quest · Storyteller.incidentQueue ·
Pawn.CurJob/CurJobDef/MentalState/MentalStateDef/InMentalState/IsColonist/IsFreeColonist/IsPrisoner(OfColony)/IsSlave(OfColony)/IsMutant/IsGhoul/IsAnimal/IsColonyMech/IsColonistPlayerControlled/IsCreepJoiner/HostFaction/Ideo ·
MentalState.def/Age/causedByMood/causedByDamage/causedByPawn/forceRecoverAfterTicks ·
Pawn_MindState.mentalBreaker/duty/enemyTarget/meleeThreat/lastAttackTargetTick/anyCloseHostilesRecently ·
MentalBreaker.Break{Minor,Major,Extreme}IsImminent · Pawn_NeedsTracker.food/rest/mood/joy · Need.CurLevelPercentage ·
LordUtility.GetLord(this Pawn) · Lord.loadID/faction/ownedPawns/Map/CurLordToil/LordJob · PawnDuty.def/focus ·
QuestUtility.IsQuestLodger/IsQuestHelper · WildManUtility.IsWildMan · CaravanUtility.IsCaravanMember · WorldPawnsUtility.IsWorldPawn ·
Ideo.GetRole(Pawn) · Pawn_RoyaltyTracker.MostSeniorTitle · Pawn_GuestTracker.GuestStatus ·
Thing.TakeDamage(DamageInfo) (non-virtual) · Pawn.Kill(DamageInfo?, Hediff) · DamageInfo.Def/Amount/Instigator/Weapon/HitPart/IntendedTarget ·
DamageWorker.DamageResult.totalDamageDealt/deflected/hediffs ·
Thing.TryAbsorbStack(Thing,bool)/SplitOff(int)/Destroy(DestroyMode)/Ingested(Pawn,float) · Thing.holdingOwner/ParentHolder/MapHeld/PositionHeld ·
IThingHolder.ParentHolder · ThingOwnerUtility.GetAllThingsRecursively · World : IThingHolder · CompRottable.RotProgress/Stage.

## Added (src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSituationalTools.cs)

- (a) `jawa/pawn_census` - G1. ungated read.
- (e) `jawa/pawn_roles` - G9. ungated read.
- (b) `jawa/incident_queue_peek` (ungated) + `jawa/incident_queue_remove` (GM-gated, dryRun default, zero-match FAILS, measured read-back).
- (c) `jawa/damage_log` - G7. Harmony postfix on Thing.TakeDamage + Pawn.Kill into a 4096 ring; refuses if not installed.
- (d) `jawa/thing_lineage` - G3+G8. live holder chain + journal (absorb/split/detach/ingest/destroy, items only).
- Recorder installed lazily from JawaBenchInit (first jawa call of a session).

## Build/selftest

- build.py --gm (no --apply) in a Windows scratch copy: Build succeeded, 0 warnings, 0 errors. DLL tool set == source tool set (355), all 6 new names present.

- rimdrive: Session wrappers (pawn_census, pawn_roles, incident_queue, incident_queue_remove, damage_log, thing_lineage; each RAISES on success:false); FakeWorld world-model support; selftest 21/21 incl. a key-contract check (every fake key must be named in the real tool's attribute text; it caught 2 real description gaps, fixed) and a sanity probe.
- run_selftests.py in the worktree: 95/104; the 8 failures are unrelated to this change (none import rimdrive; e.g. sun_heat cannot load a DLL over a \\wsl.localhost path, walklint reads untracked live indexes).
- Non-GM build also compiles (incident_queue_remove is GM-gated like the existing clear).

## Owed

- Deploy (`build.py --gm --apply` with the game DOWN) and a live proof on the minimal list: census shows a forced mental break + a predator's PredatorHunt/preyId; roles distinguishes the colony animal; peek lists a scheduled incident, remove takes exactly one; damage_log shows a jawa damage hit + a pawn_force_incapacitate kill; thing_lineage follows a meat stack through haul/merge/eat. Also confirm the bridge serialiser emits the nested anonymous rows and that the lazy recorder line appears in Player.log.
- Then switch detectors (predator_hunting, manhunter, mental_break, item_vanished) from inference to these reads.
