# WASTELAND_CONTAGION_LIVE_FAILS — offline root-cause pass (2026-10-08)

Status: offline pass done; live reproduction owed (checklist below)

## 1. Tipping toggle — HARNESS (fixed)
Evidence: Wasteland_20261008T050927Z.json chain 22 `tipping_off_refuses_the_offer`: `jawa/fire_quest` made quest 2 with tippingEnabled=false.
Mechanism (RimSage): `jawa/fire_quest` -> `QuestUtility.GenerateQuestAndMakeAvailable` -> `QuestGen.Generate`, which runs RunInt and never TestRun.
The gate `QuestNode_RM_TippingContract.TestRunInt` (RM_RiteOfTipping.cs:181) is only consulted by `QuestScriptDef.CanRun`, which
`IncidentWorker_GiveQuest.CanFireNowSub` calls -- and that incident (`RM_RiteOfTipping`) is the player's only route. Mod is correct.
Fix: validation.py now dry-runs `jawa/fire_incident RM_RiteOfTipping` with an ON control (UNMEASURED if ON can't fire: earliestDay 8,
minRefireDays 30), flips the toggle, steps 2 ticks (CanFireNow and CanRun both memoise per tick), and fails on canFireNow=True.

## 2. Middenshell toggle — HARNESS (fixed)
Evidence: chain 21 `incident_is_blocked_when_the_body_is_switched_off`: canFireNow=True with middenshellEnabled=false.
Both dry-runs (ON control and OFF arm) ran at paused tick 653672. `IncidentWorker.CanFireNow` caches `CanFireNowSub` in
`lastCheckCanRunTick/lastCanRunResult` (RimSage, IncidentWorker.cs:35-154), so the OFF ask got the ON answer from cache.
Gate `RM_IncidentWorker_MiddenshellArrives.CanFireNowSub` (RM_Middenshell.cs:851) is correct. Fix: `t.wait_ticks(2)` after the flip.

## 3. Contagion placement (burn_forced/native_dives_for_roof) — HARNESS (fixed)
Evidence: Contagion_20261008T052754Z.json chain 16: Gnashling spawned at (anchor x, z+4)=(125,84); at +3300 ticks it was at (72,149)
on a Goto, (65,160) at +3900, (54,174) at +4700. `RM_SkyKernel.PressureActive` is false while burnDamageFactor=0, so no dive
can happen during arm A's 3900 ticks and nothing keeps the native beside the roof patch. The dive code (TryDive, radius 14,
first 4 sheltered cells) is fine. Fix: a fresh native is spawned beside the patch at the moment damage turns on; its position
is sampled 4 x 200 ticks; any sample under the patch is the dive. (Why the first Gnashling walked ~60 cells on a Goto in
3300 harmless ticks is unexplained -> live checklist.)

## 4. Inject timeout — HARNESS (fixed)
`_inject` sent `jawa/ordered_job waitTicks=600` with the runner's 30 s socket timeout; the server-side wait is frame-bound
and outran it. `_patient` (raise the per-reply timeout) already fixed LayDown and do_bill_now in the same chain; _inject now
uses it too (timeoutSeconds 180). Whether the inject job itself lands RM_AmoebaGestation is still unproven -> live.

## 5. Coalescence manhunter — HARNESS + REAL (both fixed)
HARNESS: the check did `"Manhunter" in json.dumps(jawa/pawn_get)`, and pawn_get has no mental-state field at all (evidence
rows carry traits/skills/apparel/hediffs/needs only), so it could never pass; it also looked only in a 24-cell rect while a
manhunter runs at the nearest human. Now: every Unfinished on the whole map that was not there before the jump is read with
`jawa/pawn_mental action=list` (currentState); FAIL distinguishes "none emitted" from "emitted, not manhunter".
REAL: `CompRandomizeUnfinished.RollLimbs` put limb hediffs on ANY leaf part. Evidence: RM_TheUnfinished193891 carries
RM_UnfinishedUselessJaw (partEfficiency 0.2) on its Brain -> Consciousness 0.2 -> downed, and `RestUtility.Awake` is false
(CanBeAwake needs >0.3), so `TryStartMentalState(Manhunter, null, forced:true)` (forceWake false) refuses silently (RimSage,
MentalStateHandler.TryStartMentalState). Fix: limbs only on depth-Outside leaf parts that are not a consciousness/blood-pumping/
breathing source (`IsLimbSite`). Def comment corrected. The emitted pawn in this run (193898, Lung+Paw, Consciousness 0.92)
read hostile=false 400 ticks after the jump, so whether THAT emission went manhunter is still unproven -> live.

## Live reproduction checklist
Deploy first (game closed): `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Contagion` plan, then `--apply`
(new RimMandrake.Contagion.dll: limb-site filter). Wasteland needs no deploy (validation.py only).

1. `modcheck run Wasteland` on acc_biomes-15 (Wasteland map). PASS bar: `middenshell_procession.incident_is_blocked_when_the_body_is_switched_off`
   and `rite_of_tipping.tipping_off_refuses_the_offer` both PASS. If tipping reads UNMEASURED ("cannot fire even with
   tippingEnabled=true"), read its canFireNow evidence: earliestDay 8 (DaysPassedSinceSettle) or minRefireDays 30 is the cause;
   that is a fixture limit, not a toggle defect.
2. `modcheck run Contagion` on the RM_Contagion map. PASS bars:
   a. `burn_forced.native_dives_for_roof` PASS; the evidence `native_track` shows a sample inside the roof patch.
   b. `genome.inject_starts_gestation` reaches a verdict (no 30 s timeout); PASS = host carries RM_AmoebaGestation.
   c. `coalescence.coalescence_emits_manhunters_and_grows_on_its_own` PASS; note "Unfinished new since the jump" shows
      currentState Manhunter. If it FAILs with "emitted ... none is a manhunter", read each new pawn's Consciousness with
      list_pawns includeHealth: <=0.3 means a vital-part roll survived the fix (bug); >0.3 means TryStartMentalState refused
      for another reason -> try `jawa/pawn_mental action=start state=Manhunter forced=true forceWake=false` on it and read `started`.
3. Spawn 20 RM_TheUnfinished (jawa/spawn_pawn count=20) and read hediffs: no RM_Unfinished* limb on Brain/Heart/Lung/any
   Inside part; none downed at birth.
4. Unexplained, observe only: in burn_forced arm A a freshly spawned RM_Gnashling walked ~60 cells on a Goto within 3300
   harmless ticks. Read its curJob/jobGiver once (`jawa/pawn_get` + list_pawns job) to learn what drives it (wander root,
   flee from drafted colonists, or seek-temperature).
Not in this item: Wasteland toxic-dose rows (handled by _wait_dose, WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1), processor
'off feed ground', flora harvest, gripper/brine 30 s timeouts (same _patient family; Wasteland has no _patient yet).
