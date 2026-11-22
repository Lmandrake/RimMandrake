# RIMMANDRAKE_PROVE_HUGETHINGS_BARS_LIVE_SIXTEEN_TICKETS_ONE_RUN

Filed 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`).
Sweep record: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\HugeThings.md`.

**Version: current.** HugeThings has no Design Version and no stage record yet (`maturation.py show HugeThings`). By the
obvious reading its first version is the north star that he validated by card on 2026-11-14
(`design/validation_walks/RimMandrake/HugeThings.md`), which the pipeline locks at 0.1.0 when it admits the mod.

## spec

Prove live the six must-show bars that he validated on 2026-11-14, and the two cannot-show bars:

- giant plants (`src/RimMandrake/HugeThings/northstar/showcase_plants_live.py`): `plant_trunk_solid_where_art_meets_ground`,
  `plant_cap_space_open`, `plant_click_selects_picture`, `plant_growth_seals_door_until_cut`;
- titans (`src/RimMandrake/HugeThings/northstar/showcase_titan_live.py`): `titan_crossing_destroys`, then
  `titan_dies_into_remains`;
- cannot show: `one_demo_for_both_promises`, `showcase_out_of_order`.
- `titan_crowd_comes_for_remains` is held by him (card 2026-11-14) and is not a row here. It is in
  `RIMMANDRAKE_BUILD_HUGETHINGS_CROWD_AT_REMAINS_BAR_HELD`.

What is known, and what the run must repair first:

1. **The door row runs again.** The plants showcase ran `--no-door` because the door seal was blocked on his
   question 1. His answer 4 (2026-11-11) removed that block, so the door row is owed. Run the plants showcase without
   `--no-door`.
2. **The door harness never reached a full chain.** `northstar/trunk_doors_live.py` (778 lines, about 60 `require()`s,
   an exact 17-mod tier, a mid-cut save/reload identity) died twice: after6 at "cutting work/targets changed across
   occupied reload"; after9 before the scene, when its observation save held 32 NUL bytes (SteveDesktop) and restoration
   then raised `KeyError('baseline')`. The mod works (Test Pilot sitting 2026-11-14, measured: S/W/E doors seal at growth
   >= 0.25, and inside and outside cutters reopen them at 0.30). Split the harness into a short seal-and-cut row on any
   quicktest map (the exp5/exp6 shape) and separate save/reload rows. Make restoration tolerate a missing baseline.
   Evidence: `D:\ClaudeWork\rimmandrake\conductor\ht_door_20261114\FINDINGS.md`.
3. **The selection row has its instrument.** `HugePlantSelectionProbe.ClickPicture` was built in `b72e5aa81dda`. Deploy
   the HugeThings DLL before the row counts: the testq job `J20261112T153603Z-bcc5ae` ended INVALID DEPLOY (stale
   companion DLL), with no verdict on the mod.
4. **The titan showcase has its CONTROL phase**: the same-mass untiered `RM_TestTitanT2Control` is sent at the sealed
   goal and must leave the 24-wall ring whole, so `titan_crossing_destroys` is credited to the titan's tier.
5. **Two must-be-true lines are owed live by his card of 2026-11-13** ("Unproven → prove hitbox + save/load relink (not
   mapgen trunks)"): `not_driven.huge_pawn_hitbox_covers_drawn_body` and `not_driven.trunk_relinks_after_save_load`.
   Both read UNMEASURED today. Mapgen trunks are not owed.
6. Exit codes: 0 PASS, 1 MOD FAIL, 2 UNMEASURED (`showcase_common.Showcase.exit_code`). A site or harness fault is never
   charged to the mod.

Where it runs: any free game that loads the tier
`mods__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_biomes__neku_largepawns` (ArchSmall, Steve1 or
Steve2). Not ArchBig, while his walk hold stands. He asked to see this live (2026-11-13): keep the staged scene as a save
for his next sitting. Do not hold a game for him.

The live rows of the superseded built items (list below) are owed only where one of the bars above needs them. Their
code is on origin/main (each fix's marker found by `git grep` on 2026-11-22). The flying gate of `TITAN_WAKE_FIXES_1`
(B3.8) is proven by a `Pawn_FlightTracker` state read, never by a live flight.

When HugeThings enters the Maturation Pipeline, these rows feed its test table. This ticket alone does not run the mod
forward.

## Acceptance test

None offline: this is live-app behaviour. The deciding commands, run on a free game named in the note:
`python.exe src/RimMandrake/HugeThings/northstar/showcase_plants_live.py` and
`python.exe src/RimMandrake/HugeThings/northstar/showcase_titan_live.py`. Pass: both exit 0 on the deployed build; a row
with exit 2 stays UNMEASURED, never PASS.

## Merged into this ticket (2026-11-22)

| item | class | one line |
|---|---|---|
| `RIMMANDRAKE_PROVE_HUGETHINGS_DENSE_SCENES` | KEEP, current | the live proof itself; its `--no-door` spec was stale after answer 4 |
| `RIMMANDRAKE_SPLIT_DOOR_SEAL_PROOF_ONE_HICCUP_KILLS_ALL` | KEEP, current | the door harness repair, point 2 above |
| `RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES` | DUPLICATE | the split is in the validated north star; its live half is this ticket |
| `RIMMANDRAKE_MEASURE_HUGETHINGS_PLANT_PICTURE_SELECTION` | DUPLICATE | instrument built `b72e5aa81dda`; only this ticket's live read remains |
| `RIMMANDRAKE_ALLOW_HUGETHINGS_TRUNKS_TO_SEAL_DOORS` | DONE | built `f6b1435d0c67`, measured working live 2026-11-14; its deciding row is point 2 |
| `TITANIC_CREATURES_FIRST_SCRIPT_1` | DONE | the script is the titan half of `HugeThings/validation.py`; verify pass 2026-10-07 |
| `PLANT_INTERACTION_GUARDS_1` | DONE | code on origin (`questTags`, `InteractionCellsWhenAt`, `ignoredThings` guards) |
| `PLANT_FOOTPRINT_HARDENING_1` | DONE | code on origin (the `Plant.TickLong` growth postfix and the other hardening) |
| `TITAN_BREAKTHROUGH_CLEARING_1` | DONE | code on origin (`Patch_StartPath_TitanClearing`) |
| `TITAN_ROOF_AVOIDANCE_1` | DONE | code on origin (route exclusion on `PathGridDoorsBlockedJob`) |
| `LARGEPAWNS_BRIDGE_HARDENING_1` | DONE | code on origin (`largePawnsClearingOff`) |
| `TITAN_WAKE_FIXES_1` | DONE | code on origin (the `Pawn.Flying` gate and the other four fixes, inspected 2026-11-11) |
| `CORPSE_SITE_SAFETY_1` | DONE | code on origin (the `PostLoadInit` reconcile and the deferred conversion) |
| `TITAN_TRENCHES_WIRE_MIND_THE_GAP` | DONE | code on origin (`TrenchStrideHook`, `StepsOverTrench`); not a HugeThings bar |
| `HUGETHINGS_DESIGN_FIRST_TOUCH` | STALE | the design pass is done (north star validated 2026-11-14); Relentless is retired; Lock is the pipeline's |
| (this sweep's count) | | 15 items superseded here; with this ticket, sixteen tickets become one run |

## His words on the merged items (word for word)

- 2026-09-09, card #1 of `TITANIC_CREATURES_MOD_1` (quoted in `TITAN_BREAKTHROUGH_CLEARING_1` and `TITAN_ROOF_AVOIDANCE_1`):
  *"a titan … smashes through anything built"*; *"thick roofs (overhead mountain) are AVOIDED — a titan never paths under
  rock"*.
- 2026-10-19, by card (`TITAN_TRENCHES_WIRE_MIND_THE_GAP`): "Six §8 questions → step over trenches < B/4".
- 2026-11-10 (`RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND`): "Ask GPT to do a deep review of HugeThings".
- 2026-11-11, by card: "HugeThings: Promise -> Two promises; First scene -> B: crossing, then remains; Warning ->
  (written in) Two hours." and "Doorway -> (written in) To be honest I don't really like the safety rule. I think they
  have to cut it down to get in or out after it grows."
- 2026-11-13 (`HUGETHINGS_DESIGN_FIRST_TOUCH`): "Do the test live with me so I can see what's going on. OR Conductor
  should peek in on one of those games to see live what the heck is going on". Card: "HT bars → Sit the pass now
  (validate or fix the 7 agent-drafted north-star bars with him); Crowd → 3+ pawns within 1 in-game day of the death;
  Destruction → walls, trees and crates in its path count; Unproven → prove hitbox + save/load relink (not mapgen trunks)".
- 2026-11-14 (`HUGETHINGS_DESIGN_FIRST_TOUCH`): "Validate all four. I wanted to see it live to find out why it was having
  a hard time passing." Card: "Plant bars 1-4 → all four validated (his typed answer); Titan bars → Validate 5-6, hold
  the crowd".
