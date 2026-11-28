# Check of the large-bundles report, 2026-11-27

Item: RIMMANDRAKE_CHECK_LARGE_BUNDLES_REPORT_RELAYED_TO_HIM_UNREAD. Checked report: the run on
RIMMANDRAKE_FILL_BUNDLES_BY_HOME_HOLD_MEDIAN_ONE_TODAY (ed14a18611, 70fc8e9f4e, 08c1a13e25, 8753303b66). Checked from
11:18 PM to 11:30 PM PST 2026-11-27, on the code of origin/main at 4341851fd3. Tags: MEASURED, ESTIMATE, UNMEASURED.

Evidence folder (agent storage, not in the repo): `D:\ClaudeWork\scratch\large_bundles_check`. It holds
`reading_2310.json` (a copy of the applied lane reading of 11:10 PM PST), `dry.json` (a dry lane pass of 11:21 PM PST),
`dry_future.json` (a dry pass with the clock set to 10:25 PM PST 2026-11-28), `replay.out`, `replay_live.out`,
`sweep_noreview.out`, `q4.json` and `q5.out`. The scripts are in `D:\ClaudeWork\scratch\large_bundles_check_scripts`.

## Short answer

The report is true of the replay and false of the live lane today. The replay's median of 5 comes from fresh-reader
tickets: 22 of the 23 replay bundles with 5 or more members are the three read homes. The code review pause holds every
reader ticket. Without the reader tickets the same replay reads a median of 1 (MEASURED). Also, the hold does not apply
to the two routes that start most of the live lane's runs: a Shape run and an onboarding run. So for the next 24 h the
likely median is 1.

## 1. The two launches of the 11:10 PM PST tick

Command: the `launched` and `items` keys of `D:\ClaudeWork\rimmandrake\dispatcher\list_dispatch\reading.json` (applied
tick, `at_pac` 2026-11-27 11:10 PM PST). Homes: `work_bundle.system_of` in a dry pass at 11:21 PM PST.

- `RIMMANDRAKE_REARM_BREAKER_BY_PROBE_KNOCKBACK_SAT_105_MIN`: the Shape route. Row: "Shape run: opus ...; filed 24.2 h
  ago with no check and no route; on SteveDesktop". Its home is `cause:RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX`.
  That home holds 1 ticket, this one (MEASURED at 11:21 PM PST; ESTIMATE for 11:10 PM PST, as no ticket of the home was
  filed between). The rules that let it start alone:
  - `list_dispatch.py:818`: a Shape row is never held (`not (judge or shape or offer or game or repair)`).
  - `work_bundle.onboard_class`: a `cause:` home has "no home of its own", so no onboarding run takes the row.
  - The boundary page promises this (`the-lane-launches-one-bundle-per-system`: "a Shape row of any other home is its
    own Shape run"). It is not a defect against the page.
- `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ`: the onboarding route. The `-onboard` row reads "onboarding runs started:
  pipeline:operations (1 member(s), led by OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ, on SteveDesktop)". Bundle
  `WB-pipeline-operations-20261128-071225` has 1 member. Its home `pipeline:operations` held 1 open ticket, this one, and
  no other lane row (MEASURED). Two rules let it start alone:
  - `work_bundle.urgent_why`: an `OPS_` id is urgent and never waits (`an-urgent-ticket-never-waits`).
  - `list_dispatch.onboard_step` does not read the hold at all. So an onboarding run starts with the old tickets that
    are ready in that tick, however few. The page does not say whether an onboarding run waits for the hold.
  So the start is what the page promises. It is not a defect.
- At 11:10 PM PST no row of the lane read `bundle_hold` (MEASURED: 0 of 157 rows). The hold held nothing in that tick.

## 2. The replay of the 2026-11-27 arrivals

Command: `python3 src/RimMandrake/rimflow/bundle_replay.py --day 2026-11-27`, then `--parent` and `--sweep`.

| form | bundles | median | singles | largest | longest wait |
|---|---|---|---|---|---|
| shipped (4 h, 5) | 45 | 5 | 17 | 6 | 4.68 h |
| parent (no hold, no reader home) | 140 | 1 | 136 | 6 | 1.64 h |
| shipped, without the code review tickets | 20 | 1 | 16 | 6 | - |

All MEASURED. The sweep is not monotonic: 3 h gives 3.5, 4 h gives 5, 6 h gives 4, 12 h gives 1. So the median of 5 at
4 h is on a knife edge: the 23rd of 45 bundles.

The bundles with 5 or more members at 4 h, by home: `pipeline:read-utils` 9, `pipeline:read-other` 7,
`pipeline:read-rimflow` 6, `pipeline:conductor-tools` 1 (MEASURED). Of the 148 arrivals filed on Nov 27, 120 match an
`id_pattern` of the code review pause (MEASURED).

What the replay leaves out that the live lane has:
- **The code review pause.** The live lane starts no reader ticket. Without those tickets the replay reads a median of 1
  on Nov 27. No hold from 0 to 24 h gives a median above 2.5 on Nov 25, 26 or 27 (MEASURED, `sweep_noreview.out`).
- **The game work pause.** Small for these numbers: 1 of the 148 Nov 27 arrivals has a `game:` home (MEASURED).
- **Parked tickets.** The fixture holds only tickets that a bundle took, plus reader tickets. A parked ticket never
  arrives in the replay, so the pause on parks does not change the replay numbers.
- **Tickets with no check (state `proposed` and unseen).** The replay makes each arrival ready at its filing. The live
  lane sees a ticket with no check only 24 h after its filing (`shape_grace_h`), as a Shape run. A Shape run is never
  held and is never bundled outside a `pipeline:` or `machine:` home. The replay holds them all.
- **The onboarding route.** The replay holds every bundle. The live onboarding step reads no hold.
- **A hold that ends with fewer than 5.** The replay does model this: the 17 singles at 4 h are such ends. The longest
  wait, 4.68 h, is more than the hold. The page allows that: a wait for room is not a wait for the hold.
- **Room.** The replay has 8 slots. The live room is 2 on Archmagi plus up to 6 on SteveDesktop, under the load and
  account gates.

## 3. The two `proposed` tickets

Command: `rimflow show <ID>`; `list_dispatch.gather` (the rows it keeps); `list_shape.due`; a dry pass with the clock
set to 10:25 PM PST 2026-11-28.

Why the lane does not list them: each was filed at 10:11 PM PST 2026-11-27 with no `--effect`, no item prose (so no
acceptance script), no route and no lane cause. `gather` keeps a ticket only with one of those, or when Shape is due
(`list_dispatch.py`, the `continue` after `lane_cause_facts`). Shape is due 24 h after filing (`list_shape.due`,
`shape_grace_h` 24). So both tickets are unseen until 10:11 PM PST 2026-11-28 (MEASURED from the code and the filing
times).

- `RIMMANDRAKE_ROUTE_GUARD_REFUSED_CLOSE_TO_A_RUN_TWO_RANG_TONIGHT`: home `item:` (no home, no cause). From 10:12 PM PST
  2026-11-28 it is a Shape run of its own, in the first lane tick with room. In the dry pass at 10:25 PM PST it read
  `slots_full` behind 10 other Shape launches (ESTIMATE: a dry pass with a moved clock does not move the live runs).
- `RIMMANDRAKE_BUILD_DESIGN_ONLY_SWITCH_DESIGNER_STOPS_WITH_BUILDS`: **no route ever started it.** `mod_work` read it
  as DirectSun's work, because the one repo path it names is `design/concepts/DirectSun/admission_proposal.md`. The
  dry pass at 10:25 PM PST read `mod_work`: "waits for the Maturation Pipeline run of DirectSun". Its work is
  `control.py` and `./pipe`, which no DirectSun run builds. This run repaired it as a fault of form. Its home is now
  `pipeline:conductor-tools` (ledger c111ece71a). After the repair, `mod_work` reads "its home is
  pipeline:conductor-tools" (MEASURED). From 10:12 PM PST 2026-11-28 it is old and Shape-due. The onboarding run of
  `pipeline:conductor-tools` then takes it, or it starts as that home's Shape row.

A ticket that is filed with `rimflow file --for BENCH` and no `--effect` does start: as a Shape run, 24 h after its
filing. No route starts it sooner, and the hold never applies to it.

## 4. Pipeline and machine tickets now

Command: `q4.py` over the ledger (`list_effect._world`) and the dry pass of 11:21 PM PST. Home by
`work_bundle.system_of`. 105 open tickets have a `pipeline:` or `machine:` home (MEASURED).

| state | count |
|---|---|
| ready (launch, slots_full, bundled) | 0 |
| held by the hold time (`bundle_hold`) | 0 |
| live (a lease or a live bundle; 7 in the FlowWorks road-back bundle `WB-mod-FlowWorks-20261128-020147`, 1 in `WB-pipeline-operations-20261128-071225`) | 8 |
| `doing` with no lane row and no bundle | 2 |
| off by the code review pause (63 in the three read homes) | 65 |
| parked (blocked) | 11 |
| waiting for a date (3 lane rows, 5 old tickets) | 8 |
| routed to the owner or the Conductor (one of them is also parked) | 5 |
| refused by a bundle since their last event (all `pipeline:bridge`) | 4 |
| stopped (`adopt_too_heavy`) | 1 |
| proposed and unseen (filed under 24 h ago, no check) | 2 |

All MEASURED (sum 106: `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP` is routed and parked). The lane's own count of
the pause agrees: 65 held (`list_dispatch.py status`, 11:10 PM PST and 11:20 PM PST). Tickets of `cause:` and `item:`
homes are not in this table, though many of them are pipeline work. The lane rows at 11:21 PM PST hold 43 `cause:` rows
and 3 `item:` rows (MEASURED).

The 11 parked tickets, from each one's last `block` event:
- A run parked 8 under the owner's full-list ruling. The citation is `--per-ruling
  RIMMANDRAKE_PROPOSE_FULL_LIST_WALK_NOT_PER_MOD_ARCHBIG_IS_THE_LINE` or the Conductor authority, the kind is `owner`,
  and the ledger seat is OWNER with BENCH as the runner. Reason class: full-list testing is retired until the integration
  phase. The 8 are HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD, OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME,
  TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS, RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP,
  EXPERIMENT_MANIFEST_BUILD_FREEZE_SIX_CELLS, HEALTH_METRICS_PROVE_EIGHT_WRITTEN_UNTESTED (all `pipeline:bridge`),
  HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE and HEAP_READ_BISECT_ROWS_NAME_THE_RETAINERS (`machine:SteveDesktop`).
  COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED has the same reason as a dated wait to 2027-05-24.
- The Conductor parked 1, SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP, on his word of 2026-11-03 ("3 hold for later").
- The Conductor's triage of 2026-11-06 parked 1, PLAYER_ROLE_DESIGN_EMPTY_CHAIR_AT_TABLE, as kind `external`. It quotes
  his park of 2026-10-31 ("Let's table that discussion for now").
- The retired seat FOUNDRY parked 1, REBOOT_BREAKGLASS_VERIFY_1, on 2026-09-25. Reason class: his hands are needed (a
  Windows reboot and his phone).

No park is an owner card: no `block` event carries `--by-card` or `--owner-said` (MEASURED). So the reason on
RIMMANDRAKE_REPAIR_ONBOARDING_LAUNCH_SO_BUNDLES_FILL_MEDIAN_ONE ("the owner-card PARKED pipeline tickets") names the
wrong authority. The parks rest on his standing rulings and his words.

Only his word can un-park these 11: the 8 full-list parks and COLDLOAD (his ruling that full-list testing waits for
integration), SEAT_BENCH_RENAME (his "hold for later"), PLAYER_ROLE_DESIGN (his "table that") and REBOOT_BREAKGLASS
(his hands). An un-park would not give a large bundle either. The 8 full-list tickets need the full mod list, which his
ruling retired, and `pipeline:bridge` would still hold only 6 of them plus 4 refused tickets.

## 5. Forecast for the next 24 h, with the pauses as they stand

Command: `q5.py` (the tickets with no check that turn Shape-due by 11:27 PM PST 2026-11-28), and the dry pass at 10:25 PM
PST 2026-11-28.

- 38 tickets turn Shape-due in the next 24 h (MEASURED). By home class: `cause:` 18, `item:` 11, `pipeline:` 5, `mod:` 3,
  `game:` 1. The 29 `cause:` and `item:` tickets each start as a Shape run of their own. A Shape row is never held, and
  no onboarding run takes a `cause:` or `item:` home. The largest `cause:` home holds 3, and those 3 still start as 3 runs.
- In the dry pass at 10:25 PM PST 2026-11-28, 10 of 10 launches were Shape runs of one ticket each. None of the 10
  waiting rows with a check shared a home with another row (ESTIMATE: a moved clock).
- The reader tickets stay off, so no read bundle starts.
- **Likely median members per bundle: 1** (ESTIMATE, about 85%).

The one change that would raise the median most: **lift the code review pause** (his order of 2026-11-27, "Let's please
pause the clean/dirty code review items for now"). Evidence: the Nov 27 replay reads a median of 5 with the reader
tickets and 1 without them (MEASURED). 63 reader tickets wait now in 3 homes (31, 16, 16; MEASURED), so the first tick
after a lift would start 3 read bundles of 16 to 31 members. This run did not make that change. The pause is his
order, and the Conductor brings it to him.

No hold length is a lever while the pause stays on. Without the reader tickets, no hold from 0 to 24 h gives a median
above 2.5 on Nov 25 to 27 (MEASURED). The lever inside his order is the 29 `cause:` and `item:` tickets with no check
that start as one Shape run each. A rule that gave them a real home, or let one Shape or onboarding run take several
tickets of one cause, would act on most of the next day's launches. Nothing measured shows that it would reach a
median of 5.

## What this run changed

- Ledger c111ece71a: home `pipeline:conductor-tools` on RIMMANDRAKE_BUILD_DESIGN_ONLY_SWITCH_DESIGNER_STOPS_WITH_BUILDS
  (question 3).
- One `risk:` line on `design/specs/2026-11-24-work-bundles/polish.md`: the replay holds Shape and onboarding arrivals,
  but the live lane does not.
- This page.

Not tested: the times in question 3 and the forecast in question 5 come from the code and a dry pass with a moved clock.
They are not from an applied tick at that time.
