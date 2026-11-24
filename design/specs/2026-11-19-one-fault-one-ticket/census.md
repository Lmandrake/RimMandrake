# Census: the programs that file tickets with no person, and what each keys a ticket on (2026-11-19)

Item `RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET` (owner by card 2026-11-19, "One fault, one ticket"). Evidence for the
floods: `D:\ClaudeWork\rimmandrake\conductor\churn_vs_responsibility_specs_20261119.md`, Option 5.

How it was measured: a grep of `src/RimMandrake` for every program call of `rimflow file` / `spawn` (`rimflow(`,
`ing.rimflow(`, `rf(`, `cli.py` argv, `model.append` of a `file` event), less selftests. Then every `file` and `spawn`
event on the ledger (history and every shard) was grouped by filer, from its `why` and title. For each filer the count
is the largest number of filings in any 60 minutes. A flood is one cause filed as many tickets. The rule
(owner, 2026-11-19): change a filer only where a flood happened or a concrete case shows it will.

| filer | keys a ticket on | can one fault file N? | measured | verdict |
|---|---|---|---|---|
| `Utils/deadman_check.py` (`live_filer`) | one fixed id per promise subject (`LIVE_RESTORE_<NAME>`), or the fix item that holds the promise. One subject under many fixes was one death since 0197f111d3, but each fix was still reopened and raised | yes: one cause across N subjects filed N; one subject under N fixes reopened N | 23 hook tickets in 30 min on 2026-11-08 (one settings path); 45 fixes reopened by one timer; tonight's real ledger would file 4 for the stopped nightly timers | **changed**: keyed on the cause (`cause_key`: subject kind plus reason with the subject's name and digits masked). One cause is one `LIVE_RESTORE_CAUSE_<hash>` ticket; its members file nothing; a repeat reopens it. Page: `boundary.md` beside this file |
| `Utils/ops_watch.py` (`real_filer`, alarms, nightly reds through `known_reds`, incidents, `signal_watch`) | one fixed item per alarm id; `jam_classes.cause_key` blocks a duplicate on its cause's repair (`block_only`); a repeat reopens (`live --result broken`); a retired item gets one successor | no, for one alarm. One red per test, grouped by cause in `known_reds` | 39 NIGHTLY_RED tickets in one hour on 2026-11-03 were 39 distinct groups (one already lists several tests under "No space left on device"); 24 since 11-09, one per distinct red | left alone: already keys on the cause |
| `Utils/testq/ingest.py` (`repair`) | `retest.repair_base(cause)`: hash of a normalised cause; known faults through `invalid_class.cause_key` since a8e0a90faf (2026-11-14); an open repair is noted, not filed again | it did: 18 `HARNESS_REPAIR_CAUSE_*` tickets from one SteveDesktop fault (relentless failure catalog, class i) | 0 filings since 2026-11-07 | left alone: the stable cause keys of 2026-11-14 are the fix |
| `Utils/testq/steward.py` (`_escalate`) | a fresh random name per incident (`mint`); an open lane item is reused (`open_lane_item`); on recovery the item is dropped (`retire`) | yes: the same recurring cause files a new ticket each time it returns | 13 `STEVE_LANE_UNSTICK_BRAKED_*` tickets 2026-11-12..15, every one "filler brake on FlowWorks, Stillsand, …"; quiet since the lane was paused by hand 2026-11-15 | **not changed; filed** as `RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES` with the evidence. The fix is not known: a cause-keyed item must outlive `retire`, and ops_watch's `steve.incident_unclaimed_min` ages an item from its creation, so a reused old item would alarm at once. A bad key there silences the lane's only stall alarm |
| `rimflow/dispatcher.py` (`ledger_structural`) | the incident's fixed structural item; a later taming of the same cause is a note | no | 12 incident-ladder filings in all, at most 2 an hour | left alone |
| `rimflow/owed.py` (`sync-sources`, retired 2026-11-23) | the source key, written into the title; a key already filed, open or closed, is never filed again; at most N a pass | no | 8 filings since 11-09, at most 3 an hour | left alone |
| `rimflow/maturation_dispatch.py` (`file_and_publish`) | one build item per mod stage, named by the dispatcher | not a fault filer | — | out of scope |
| `Utils/art_eval/auto_judge.py` (`file_item`) | one item per render or slug | not a fault filer; one per artwork | 27 in all, none since 11-09 | out of scope |
| `rimflow/artifact.py` (`file_item`) | ONE item per artifact (`DANGLING_<AID>_1`), never one per dangling citation | no | — | left alone |
| `rimflow/audit_hardflag_file.py` | the audit's ticket names, run by hand | not unattended | 1 | out of scope |

Floods that were filed by an agent, not a program, are outside this census: for example, the 16 facing-truth sprite
tickets of 2026-11-13 ("player-truth sweep") were one ticket per distinct sprite, each with its own fix. A stopping rule
in the briefs (the card's other pick) covers that filing.
