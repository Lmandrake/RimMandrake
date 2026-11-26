# Evidence for the stuck-items study (2026-11-26)

The page is `one_page.md` in this folder. Every number on the page has its row here. The window is 7 days to
2026-11-26 about 11:48 AM PST, read once between 11:48 AM and 12:05 PM PST. All times are Pacific unless they end in Z.

## How the numbers were made

| what | how | what it cannot see |
|---|---|---|
| Ledger stops | `measure_stops.py` (this folder) reads every shard in `infrastructure/state/ledger/events/` once. A **stop** is an open item with no progress event for 12 h or more. Progress events are every event except `lease home shape live raise finding seat game bridge guard`. A dated `wait` starts a new clock at its `until`. A stop that began before the window is counted from the window start. | It cannot see a stop that a ledger event did not end or show. It counts a quiet item that waited for nothing as a stop. |
| Lane items | Stops are kept only for the 595 items that the Workshop Pipeline (`list_dispatch`) has ever read: keys of `D:\ClaudeWork\rimmandrake\dispatcher\list_dispatch\state.json` and `reading.json`. | Items that the lane never read. |
| Who ended a stop | The actor of the event that ended it. **Program**: seats RUNNER and DISPATCHER; units `rm-list-*`, `rm-role-operations`, other timer roles; a detached run whose unit is named in a program record (list_dispatch, maturation, red_dispatch, work_bundle, list_effect state files) or whose brief starts `CONTINUED BY ITSELF` / `WORK BUNDLE RESTART`; a work bundle whose file says `launched_by: rm-list-dispatch.service`. **Owner**: an event that carries `ownerSaid` or `byCard`, or an OWNER-seat event. **Conductor**: every other event (the window, `rm-role-conductor`, a run that no program record names). | No run record names its launcher. A run that no program record names is read as the Conductor's [guess ~85%: a header sample of those briefs reads "detached helper of the Conductor" or "# Brief:" in the Conductor's form]. |
| Item-hours per kind | `D:\ClaudeWork\rimmandrake\dispatcher\list_dispatch\ticks.jsonl`: 471 ticks, 2026-11-23 2:59 AM to 2026-11-26 11:23 AM (81.0 h). Item-hours = count in the kind × time to the next tick (at most 1 h). No gap between ticks was over 1.5 h. | The file starts on 2026-11-23 and holds counts only. Item-hours before 2026-11-23 are UNMEASURED. Which item was in which kind at a past tick is UNMEASURED. |
| Current stops | `python3 src/RimMandrake/rimflow/list_dispatch.py status` (the 11:23 AM PST tick, 102 items) and `reading.json`. Age = hours since the item's last progress event in the ledger. | Age is not time in the current kind: a kind's start time is not recorded. |
| Mod pipeline | `design/concepts/*/version/stage_record.json` (moves, with `by` and the true local time); `python3 src/RimMandrake/rimflow/maturation_hands.py list --all` (127 acts, 65 in the window); `infrastructure/state/control/acts.jsonl` (216 acts, 145 in the window). | The duration of each hand-cleared stop. |
| His page | `D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md` and `MATURATION_DETAIL.md`, both made 11:57 AM PST. A ticket counts as shown when its id is in the file. Probe: the 2 blind tickets and 2 "Needs Mandrake" tickets are found by the same search. | Past states of the page: it is not archived. |
| Conductor log | `/mnt/d/ClaudeWork/rimmandrake/conductor/log.md`, lines dated from 2026-11-19T19:48Z. | Lines without a leading time stamp. |

The brief named `D:\ClaudeWork\rimmandrake\dashboard\MATURATION_NOW.md`. That path does not exist. The page is in
`D:\ClaudeWork\rimmandrake\conductor\`.

## Table A: ledger stops of lane items that ended in the window

`python3 design/specs/2026-11-26-stuck-items-study/measure_stops.py <out.json>`, then the lane filter and the bundle
lookup above.

| who ended it | stops | share | item-hours | share |
|---|---|---|---|---|
| a program | 309 | 84% | 27,272 | 86% |
| the Conductor | 49 | 13% | 3,659 | 12% |
| the owner | 10 | 3% | 772 | 2% |
| all | 368 | | 31,703 | |

Lengths: 12 to 24 h 76; 1 to 3 days 107; 3 to 7 days 185 (many began before the window and count from its start).
The ending event: program `claim` 77, `start` 72, `note` 63, `verify` 43, `drop` 23; Conductor `note` 16, `claim` 8,
`unblock` 8, `verify` 5, `close` 5. The longest stops that the Conductor ended (165 h each, the whole window): five
Direct Sun and tree shade tickets, unblocked or blocked by hand.

Probe for the instrument: over all 1,400 stops of every item (not only lane items) the shares are program 531,
Conductor 827, owner 42. Most of the Conductor's share there is the hand sweeps of old tickets (508 drops in the window).
The lane filter removes them.

## Table B: Workshop Pipeline item-hours per kind, 2026-11-23 2:59 AM to now (81 h)

| kind | item-hours | average items | most at one tick | a stop? |
|---|---|---|---|---|
| waiting (a dated wait) | 1,271 | 15.7 | 30 | no: a date |
| off (his hold or a pipe off) | 825 | 10.2 | 139 | no: his hold |
| slots_full | 577 | 7.1 | 55 | no: a queue for a slot |
| routed | 432 | 5.3 | 32 | yes |
| waits_on (another open item) | 267 | 3.3 | 16 | no: a named item |
| mod_work | 213 | 2.6 | 7 | yes, when the mod rests |
| chain_stop | 112 | 1.4 | 5 | yes |
| adopt_too_heavy | 78 | 1.0 | 1 | yes |
| close_refused | 62 | 0.8 | 7 | yes |
| blocked | 51 | 0.6 | 5 | sometimes |
| stopped | 27 | 0.3 | 3 | yes |
| system_wait | 20 | 0.2 | 5 | yes, short |
| blind (check could not look) | 14 | 0.2 | 3 | yes |
| account_hold | 12 | 0.1 | 16 | yes, short |
| launch_failed | 11 | 0.1 | 5 | yes |
| machine_load | 8 | 0.1 | 16 | yes, short |

Half-day averages: routed 0.7 (11-23 AM) rising to 13.9 (11-26 AM); slots_full 31.7 falling to 2.0; mod_work 0 to 4.7;
chain_stop 0 to 3.4; close_refused 0.1 to 3.4. machine_load held the lane on 11 ticks: 0.7 h on 11-25 and 1.6 h on
11-26, 2.2 h in all.

## Table C: the stops that stand now (11:23 AM PST tick, 102 items)

| kind | items | median age h | max age h | sum of ages h | on MATURATION_NOW | only on DETAIL | nowhere |
|---|---|---|---|---|---|---|---|
| routed to owner | 13 | 323 | 595 | 3,020 | 0 | 10 | 3 |
| routed to judge | 9 | 494 | 567 | 2,769 | 1 | 1 | 7 |
| routed to Conductor | 9 | 9 | 567 | 629 | 0 | 9 | 0 |
| routed to review | 1 | 18 | 18 | 18 | 0 | 1 | 0 |
| close_refused | 7 | 2 | 15 | 41 | 0 | 0 | 7 |
| mod_work | 5 | 40 | 49 | 146 | 0 | 1 | 4 |
| chain_stop | 4 | 31 | 39 | 115 | 0 | 0 | 4 |
| machine_load | 3 | 18 | 50 | 79 | 0 | 0 | 3 |
| no_bundle | 2 | 484 | 484 | 791 | 0 | 0 | 2 |
| blind | 2 | 2 | 2 | 2 | 2 | 0 | 0 |
| stopped | 1 | 17 | 17 | 17 | 0 | 0 | 1 |
| adopt_too_heavy | 1 | 17 | 17 | 17 | 0 | 0 | 1 |
| in_bundle | 4 | 567 | 567 | 1,135 | 2 | 1 | 1 |
| waiting | 24 | 14 | 17 | 281 | 0 | 3 | 21 |
| off | 16 | 58 | 567 | 3,856 | 0 | 0 | 16 |

The brief's count at 11:42 AM PST read close_refused 3, stopped 3, in_bundle 5, waiting 20. The 11:23 AM tick reads
close_refused 7, stopped 1, in_bundle 4, waiting 24. The counts move between ticks.

How his page shows these kinds:
- MATURATION_NOW "Needs Mandrake (2)" lists 2 tickets. The lane routes 13 to him.
- MATURATION_NOW shows "8 routed to judge" inside "What the 698 waiting tickets wait for", with no names and no ages.
- MATURATION_DETAIL lists "routed to conductor (8, program)" and "routed to judge (8, program)", each with its oldest
  ticket and its age since filing (67 days, for example). The word "program" is false for the judge row: no program
  starts a judge (Table F).
- The words "machine load", "chain", "close refused" and "mod_work" do not occur on either page (searched, 0 hits).

## Table D: the mod pipeline in the window

Stage moves (from each `stage_record.json`): 65. By `BENCH` (steward and helper runs) 52, `DISPATCH` (the tick) 7,
`CONDUCTOR` 4, `DESIGNER` 1, `OWNER` 1. A program made 60 of 65 (92%), the Conductor 4 (6%), the owner 1 (2%).

Hand acts (`maturation_hands.py list --all`, 65 in the window): hand_run 30, hand_move 13, clear 9, ceiling_release 6,
settings_edit 6, tick_gap 1. Of the 13 hand_move rows, 7 are moves by DISPATCH and 1 by DESIGNER: program moves that
the list counts as hand acts. True hand acts: 56. By day (PST): 11-19 3, 11-20 24, 11-21 9, 11-22 6, 11-23 7, 11-24 11,
11-25 3, 11-26 2.

Each of the 9 hand `clear` rows ended a stop that a program made after three launch refusals of one cause (a git lock, a
name over 64 characters, a model id, an account drain, a card gate). Seven were on 11-20 and 11-21.

Detached runs in the window (996 records in `D:\ClaudeWork\rimmandrake\dispatcher\detached\`): named in a program record
507; continued by `left_open_continue.py` 32; mod runs that the Conductor launched by hand 30; named by no program 426.
By day the program share rose: 11-19 7 of 78, 11-23 108 of 197, 11-26 68 of 95.

Longest stage dwell in the window: FlowWorks at the blind challenge 79.4 h, ended 2026-11-19 12:41 PM by a Conductor
move; Pyrelands at the blind challenge 77.5 h, ended 2026-11-20 10:01 AM by a steward run.

Passed mods now: Gimme Some Slack since 2026-11-24 3:01 PM (45 h), Pyrelands since 2026-11-24 7:13 PM (41 h), Explosive
Knockback since 2026-11-26 9:35 AM (2 h). MATURATION_NOW reads for each: "Waits on: Resting, passed ... opening its
next version is the Conductor's ordering call" and "Needs you: nothing", with no age. Three tickets read mod_work
"waits for the Maturation Pipeline run of GimmeSomeSlack", one of ExplosiveKnockback, one of FlowWorks.

## Table E: the seeds, each checked

| seed | record | measured | ended by | where shown |
|---|---|---|---|---|
| Two passed mods rested a day or more | stage records; MATURATION_NOW | Gimme Some Slack 45 h, Pyrelands 41 h, still resting | nobody yet | NOW names the Conductor; no age, no date |
| A `pipe off` stayed on a passed mod after its reason ended | `acts.jsonl`: mod:GimmeSomeSlack off 2026-11-24 10:57 AM, on 2026-11-26 10:30 AM ("the reason of act ct_000170 is over") | 47.5 h off; the mod passed at 3:01 PM on 11-24, so 43.5 h past its reason | the Conductor | UNMEASURED: the page is not archived |
| The same kind in the window | `acts.jsonl`: readiness holds of 2026-11-18 4:40 PM, each lifted by hand when its readiness list read READY | Explosive Knockback 105.8 h (78.6 h in the window), Pyrelands 47.9 h (20.8 h in the window), FlowWorks 23.5 h, Gimme Some Slack 12.8 h and 10.3 h | the Conductor | the control store and the log |
| The tick clone could not pull | log 2026-11-26T18:05:54Z | no pull from 9:35 AM; 60 commits behind at 9:57 AM; two uncommitted ledger lines blocked it | the Conductor launched a repair run | the log; the page read Explosive Knockback as his walk |
| Two tickets held for 6 passes, `python.exe` | log (handover 9:29 AM): "list_gate_blind_passes 6: DONOR_MUTATORS_MIGRATE_TWENTY_TWO_CAME_HOME and WORLD_STARS_REPAIR_STILL_SPINNING_FOR_NOBODY carry `cmd:python.exe` ... exit 127" | 6 passes (about 1 h at a 10-minute tick); a second blind cause at 11:23 AM (a missing file in the tick clone, 2 tickets) | an incident, then a run the Conductor launched | MATURATION_NOW counts "unmeasured 13" |
| A fix's fresh reader could not start by itself | detached records whose item reads a fix once | 6 fresh-reader runs; 5 named by no program record | the Conductor (5 of 6) | the log |
| close_refused | `state.json` close_refused records | 26 records, all with the text "nothing to publish: this command wrote no ledger or prose path"; behind it, "has not earned its close: owed still owes ..." on some | nobody yet | nowhere on either page |
| "Routed to judge" | `list_dispatch.py` lines 24 and 503 to 537; a search of `src/RimMandrake/rimflow` and `Utils` for a route with who=judge | "routed: nothing launches; the party that answers shapes the item again". No program launches a judge on a routed part. 9 tickets, median 494 h since their last event | nobody | DETAIL calls it "program" |
| Machine load over the line | ticks.jsonl | 11 ticks, 2.2 h of 81 h; up to 16 items at one tick. One sample at 12:03 PM (load 39 on 14 cores): the top CPU users were two `./publish` tree-check runs (`/home/mandrake/rm/treecheck-kept/rm-treecheck-kept-0` and `-1`) and timer checks | the load fell by itself | nowhere on either page |
| A stop order "write where you are" became a kill | `acts.jsonl` | 6 write-now stop orders in the window; 3 escalated to `--kill` when the deadline passed (the deadlines were 180 s and 300 s) | a program (the escalation) | the control store |
| The Conductor window restarted at its context limit | dispatcher `journal.jsonl` | 35 restarts relaunched, 34 verified, in the window | a program | the log |
| SteveDesktop account gate (found in this study) | work bundle files; log 2026-11-26T15:17:13Z | Archmagi switched steven to lukas at 3:35 AM. SteveDesktop still read steven draining, because its live runs were UNMEASURED and so counted live, until the Conductor switched it by hand at 7:10 AM: 3.6 h. 35 bundle launches failed in all; 27 of them on the account gate (6 named an item not on the ledger, 2 a brief with an undefined word) | the Conductor; a repair run ended success at 8:39 AM | MATURATION_NOW: "35 failed to launch", a count with no reason |

## Table F: what waits on the Conductor

`python3 src/RimMandrake/rimflow/cli.py queue CONDUCTOR --owed`: 19 owed (5 actionable, 4 of them LATE, the oldest
7 days), 10 waits that name the Conductor. The log in the window: 79 `NEEDS CONDUCTOR` lines (list_effect 52,
list_dispatch 25, red_dispatch 2) and 350 `DISPATCHER ESCALATION` lines (incident 146, restart 83, role 49, scratch 28,
timer 21). `python3 src/RimMandrake/rimflow/cli.py incidents`: 7 open.

## Faults of the instruments found on the way

- `maturation_hands.py list --all` counts 7 tick moves and 1 Designer move as hand acts (rows "moved ... by DISPATCH,
  naming no run"). The true hand count is 56 of 65.
- No detached run record names its launcher. The launcher is read from other files (Table D).
- `ticks.jsonl` keeps counts only, from 2026-11-23. No record keeps when an item entered a kind.
- MATURATION_DETAIL labels "routed to judge" as "program".
- The close_refused text is the publish's ("nothing to publish"), not the close's own reason: two causes share one text.

## What the study of 2026-11-29 can take

Tables A to D as its baseline for the stop counts and the shares; the instrument faults above, before it trusts a
count; Table E as the list of stops to check again after a week.
