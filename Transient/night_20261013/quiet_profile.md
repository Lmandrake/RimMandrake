# Quiet isolated test site profile — night 2026-10-13 (BENCH helper)

## Goal
One shared "quiet isolated test site" profile that every site builder applies, replacing each builder's partial copy
(GPT review §3 rank 5 scoped quiet-world profile, rank 6 modal broker, rank 10 presets; owner 2026-10-13: two suites).

## Items in scope
TESTENV_HIVES_HARDEN_RIVER_MAP_SQUATTERS, TESTENV_QUICKTEST_HIVES_HARDEN_EMPTY_NEST, TESTENV_VITALS_HARDEN_FIXTURES_ARE_NOT_HIVES,
TESTENV_MONOLITH_HARDEN_UNINVITED_GUEST, TESTENV_MEGAPEDE_HARDEN_GATECRASHER, TESTENV_FLOODS_HARDEN_SEASON_CRASHES_PARTY,
TESTENV_FACTION_DIALOG_HARDEN_FIVE_KNOCKS, TESTENV_STRANGER_JOINS_HARDEN_LET_IT_END, TESTENV_INJURY_HARDEN_WHO_HURT_CAIT,
TESTENV_BURROW_HEAT_HARDEN_COLONISTS_COOKED, TESTENV_GOVERNOR_STOP_DIAGNOSE_NO_NOTE_LEFT.

## What already existed (reused)
- `modcheck/helpers.py`: `quiet_world` (storyteller off + threat scale 0 + queue clear, random events off, logRaidInfo,
  `jawa/wild_spawner_block`), `SettingsTransaction` (exact restore), `kill_hostiles` (Vanish), `restore_colonists`.
- Companion: `jawa/incident_queue_peek/remove` (selective removal exists; "gap G6" is closed), `jawa/damage_log`,
  `jawa/window_list_close`, the vitals monitor's threat classifier, `jawa/safe_advance` + `clockgate.GovernorStop`.

## Mechanisms read from 1.6 source (rimsage), not guessed
- **Man in Black**: `StorytellerComp_Triggered.Notify_PawnEvent` QUEUES `StrangerInBlackJoin` (+180 ticks) on the last
  colonist's death; `Storyteller.StorytellerTick` runs `incidentQueue.IncidentQueueTick()` BEFORE the
  `enableStoryteller` check. So storyteller-off alone cannot stop it: the item's unverified title claim is TRUE.
- **"Fallen monolith"** is not an incident: it is `CompProximityLetter` on the mapgen `VoidMonolith` (radius 8,
  `letterSent` field, only while `Find.Anomaly.Level == 0`).
- `StorytellerComp_MonolithMigration` is interval-based, so storyteller-off does gate it.

## The profile (controls, what each could hide)
`src/RimMandrake/Utils/modcheck/quiet_site.py` — `QuietSite(session, suite=, controls=, keep_defs=, topic=, protect_support=)`.
`suite="integration"` applies nothing and refuses controls. Every receipt lists each control's read-back AND its
"hides" column plus `helpers.QUIET_NOT_SUPPRESSED`.

| control | what | could hide |
|---|---|---|
| storyteller_off | enableStoryteller=false, threatScale 0, no big threats, queue cleared | storyteller-fired incidents incl. the mod's own (flooding, cinderfall) |
| random_events_off | mental states / diseases off | mood/disease interactions |
| wild_spawner_off | wild replenishment blocked | the mod's effect on wildlife arrival |
| threat_structures_cleared | `jawa/quiet_site` vanishes hostile threat structures (THE vitals classifier), `keep_defs` spared | hive / mech-cluster interactions |
| hostiles_removed | hostile pawns vanished | combat interactions |
| proximity_letters_sent | every CompProximityLetter marked sent | the Anomaly monolith discovery letter |
| queue_drain | `StrangerInBlackJoin` removed from the queue at every drain | the end-of-colony rescue |
| modal_broker | explicit handlers only (VEF new-faction -> "Do nothing"); unknown force-pause windows captured, never closed | the dialog's other choices |
| support_guard (opt-in) | support colonists' new injuries recorded THEN repaired each drain; refused for health/needs/damage/death rows | health/heat/death on support colonists |

`advance()` = clockgate.advance_chunk + drain per chunk; `verify()` = 0 hostiles, 0 threat structures, 0 force-pause
windows, colonists alive, damage_log rows. `enableStoryteller` is not saved: re-apply after every load.

Companion changes: new `jawa/quiet_site` (status|apply; campaign-denied, quiet-world family); `JawaBenchVitals.IsThreatStructure`
is now the ONE classifier (monitor + clear); the `hostile` faction alias prefers a HUMANLIKE hostile faction (the GSS
Battery/Conduit/Mast fixtures were built as Insect "Hive" buildings, so the monitor was right to latch them); vitals
`hurt` rows now carry the youngest hediff (`; newest hediff Cut/Torso age 0`). `clockgate.GovernorStop` writes a
`GOVERNOR_STOP {json}` line to stderr and `governor_stops.jsonl` beside `bridge_calls.jsonl` at construction.

## Wiring into site builders
- `helpers.prepare_bland_map` (every Watch): new `quiet_site_map` step (threat structures + proximity letters).
- `Pyrelands/northstar_site.py`: build_site saves the fixture with MAP_ONLY controls; settle_site applies the full
  isolated profile after every load (receipt in `mi["quietSite"]`).
- `GimmeSomeSlack/northstar/proof_all.py`: full profile after its own hostile sweep; restored in `restore()`.
- `FlowWorks/northstar/prep_site.py` (fixture build, MAP_ONLY) and `liquid_checks.py` (full profile, restored in finally).
- Not wired: other mods' quicktest helpers (bridgetools/prove_*.py, scenes) — they keep their own steps for now.

## Live probe
Bridge taken; owner ModsConfig md5 ee01dae9e30d121c78d88e474dacd8e8; `modset_builder --tier ratchet_pilot --apply` +
the 23-mod ratchet_pilot+patches file; Steam launch (pid 9876, READY 86 s); companion built from 4f015f41a2. Evidence:
`Transient/night_20261013/quiet_live/` (probe scripts, `*_out.json`, `governor_stops.jsonl`).
- Fresh quicktest BEFORE: 8 hostile threat structures (Hive x4, GlowPod x3, EggSac; faction Hive), 21 insect pawns,
  VoidMonolith + AncientExostriderRemains proximity letters unsent.
- `hostile` Battery fixture built -> faction **Pirate** (Blackstar Company), not Hive.
- Profile applied: every control read back (enableStoryteller false, threatScale 0, allowBigThreats false, wild
  spawner blocked). AFTER: 0 structures, 0 hostile pawns, both letters sent, queue empty.
- `StrangerInBlackJoin` scheduled at fireTick 901; drain at tick 598 removed it; no letter.
- 3000 ticks through safe_advance (5 chunks): vitals **0 triggers**, 0 discontinuities, 3 colonists alive, verify
  quiet=true with the hostile Pirate Battery on the map, 0 force-pause windows, 0 colonist damage events.
- Governor note: a real stop (colony_loss on the trial-site save, 360/600) wrote the GOVERNOR_STOP row naming
  its trigger. (The budget-refusal trigger I tried first did not refuse: `safe_advance budgetTicks=500` ran 600.)
- Support guard + hurt attribution: Cut/Torso + Heatstroke added to a probe colonist -> vitals row
  `health 1 -> 0.84; newest hediff Cut/Torso age 0`; guard recorded `[Cut/Torso, Heatstroke]` then repaired; 0 left.
- Modal broker on NS_FlowWorks_TrialSite_v1: first version clicked the same window repeatedly (count-based wait;
  VEF asks ONE faction at a time, so the count never drops). Fixed to track window IDs (e167f49523); reload: **18**
  new-faction dialogs (not 5) answered, each closed, none left.
- Teardown: game killed by PID 9876; `modset_builder --restore` verified, md5 ee01dae9...; `./game down`; bridge released.

## Item outcomes
- CLOSED (proven live): QUICKTEST_HIVES_EMPTY_NEST, VITALS_FIXTURES_ARE_NOT_HIVES, MONOLITH_UNINVITED_GUEST,
  STRANGER_JOINS_LET_IT_END, FACTION_DIALOG_FIVE_KNOCKS, GOVERNOR_STOP_NO_NOTE_LEFT, INJURY_WHO_HURT_CAIT (instrument +
  guard; Cait's original cause is not recoverable from that run's evidence).
- OPEN, noted: HIVES_RIVER_MAP_SQUATTERS and MEGAPEDE_GATECRASHER (same control proven on a quicktest; the FlowWorks
  river/golden-site paths were not run live); FLOODS_SEASON_CRASHES_PARTY (storyteller-off read back, flooding not
  observed either way in 3000 ticks); BURROW_HEAT_COLONISTS_COOKED (guard proven; the burrow diag script does not opt in yet).
- NEW: TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME — the trial-site save on this tier has no living colonist on its map and
  ends the game within 360 ticks.
- Code review: the five changed C# files are DIRTY (never reviewed); selftests 23/23 quiet_site, 48/48 clockgate.
