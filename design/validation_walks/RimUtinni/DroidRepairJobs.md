# RimUtinni: Droid Repair Jobs — validation walk
subject: src/RimUtinni/DroidRepairJobs  (packageId `mandrake.rut.droidrepairjobs`)
deps: `mandrake.rsw.droidworks` (modDependencies; itself needs HumanoidAlienRaces and Harmony)
list: a tier carrying HumanoidAlienRaces + Droidworks + Droid Repair Jobs, all five DLCs, plain open map on a world with a visitable non-hostile settlement within 36 tiles
status-hint: DROID_REPAIR_FOR_PROFIT_EVENTS_1 — a quest in which a local friendly walks a broken droid to the Jawa shop and pays by the quality of part you fit. Script: `src/RimUtinni/DroidRepairJobs/validation.py`, first script DROID_REPAIR_JOBS_FIRST_SCRIPT_1. NEVER RUN LIVE.

Sources: `About/About.xml`, `Source/DroidRepairJobsMod.cs` (2 settings), `Source/QuestNode_DroidRepairJob.cs`, `Source/QuestPart_DroidRepairJobOutcome.cs`, `Defs/QuestScriptDefs/Quest_DroidRepairJob.xml`, `Defs/HediffDefs/HediffDefs_DroidRepairJob.xml`, `Defs/HistoryEventDefs/HistoryEvents_DroidRepairJob.xml`.

## must be true
- Every def the mod ships (the quest, the fault hediff, the six goodwill history events) resolves in the running game; a nonexistent control reads absent so the probe can say no. → defs_resolve.shipped_defs_resolve, defs_resolve.control_absent_def_reads_absent
- Every Droidworks def the quest names (five part-effect hediffs per tier, three tiers, and the four droid kinds) resolves; otherwise the quest cannot grade the work or generate a droid. → defs_resolve.droidworks_defs_the_quest_names_resolve
- Every Mod Settings field the C# declares round-trips (`paymentMultiplier`, `wealthAndReputationScaling`). → flip_paymentMultiplier.paymentMultiplier_round_trips, flip_wealthAndReputationScaling.wealthAndReputationScaling_round_trips
- A run leaves every setting at its shipped default. → settings_restored.all_settings_at_shipped_defaults
- With wealth/reputation scaling off and the multiplier at 1, the offered quest quotes 320 silver for honest work, 512 for a better part (x1.6) and 128 for a worn part (x0.4). → payment_scaling.flat_payment_quotes_320_512_128
- `paymentMultiplier` scales all three tiers (x2 quotes 640 / 1024 / 256, and no longer the flat base). → payment_scaling.payment_multiplier_scales_every_tier
- With scaling on, a richer or friendlier customer pays more and a poorer or cooler one less (tech-level and goodwill factors). → UNCOVERED: the scaled amount depends on the faction of whichever settlement the generator picks and no bridge read names it; chain payment_scaling.wealth_and_reputation_arm_of_the_payment records UNMEASURED
- The customer's droid arrives broken: `RUT_DroidJobFault` is on its hediff list, and a droid never touched by the quest does not carry it. → fault_hediff.fault_lands_on_a_droid_and_only_that_droid
- At pickup the quality of part fitted decides the outcome: a superior part is fine work (pays more, earns goodwill), a standard part is honest, an inferior part is shoddy (pays little, costs goodwill), no part is neglected. → UNCOVERED: needs the PickupDue signal after a 5-9 day job timer and no bridge tool fires a quest signal; chain pickup_grading.fitted_part_tier_decides_fine_honest_shoddy_neglected records UNMEASURED
- Each outcome changes the customer's goodwill with its own history event line. → UNCOVERED: needs a finished job and a faction-tab read; chain pickup_goodwill.each_outcome_changes_goodwill_with_its_history_event records UNMEASURED
- The graded silver arrives for the tier earned. → UNCOVERED: needs a finished job; chain pickup_payout.silver_arrives_at_the_landing_spot_for_the_graded_tier records UNMEASURED
- A droid the player arrests or lets die is reported with its own event (kept versus destroyed are distinct). → UNCOVERED: needs the lodgers.Arrested / .Destroyed signals live; chain droid_kept_or_destroyed.kept_and_destroyed_droid_outcomes_are_distinct_events records UNMEASURED
- The storyteller offers the quest on its own (weight 1.1, progress score 4, refire 15 days) and never with a paired incident. → UNCOVERED: pool selection over days, bypassed by fire_quest; chain random_pool_firing.quest_is_offered_by_the_storyteller_with_progress_score_4 records UNMEASURED
- The job's fiction and its look (letters, the walk-in, the customer's lines). → UNCOVERED: text and visual, judge pass or owner

## anti-guessing notes
RULED OUT: "a paired IncidentDef gives a deterministic trigger" — the engine refuses a quest run from both an incident and the random pool (`IncidentDef.ConfigErrors`, Quest_DroidRepairJob.xml header); the script forces the quest with `jawa/fire_quest`, never an incident.
RULED OUT: "the quoted fees can be read from the slate" — they are resolved into the quest description at generation, so the script reads the description of the quest the engine just generated, with settings armed BEFORE the fire.
RULED OUT: "reading a quest row that lacks a description proves the fee is wrong" — a row with no description text is UNMEASURED, never FAIL.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
