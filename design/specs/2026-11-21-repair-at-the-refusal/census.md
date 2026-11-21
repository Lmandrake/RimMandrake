# Census: refusal sites a pipeline path can reach, 2026-11-21

Item `RIMMANDRAKE_REPAIR_AT_THE_REFUSAL_NO_STOP_FOR_UNTIED_SHOES`. Rule: `design/RimMandrake/standing_rulings.md`
§A fault of form is repaired where it is found. The mechanism and its tests: `boundary.md` beside this page.

Source of the rows: `git grep -n -E "REFUSED|refused:|sys.exit\(2\)|exit 2" -- src/RimMandrake/rimflow
src/RimMandrake/Utils .claude/hooks` (tests excluded) on 2026-11-21: 1123 matching lines in all. Many matches are not
refusals (docstrings, a status word `REFUSED` in a certificate row, a regex). The rows group the sites by gate
function. Line numbers are those of origin/main at 6d31a7a8f8.

## The one principle that converts the program caller

The tick (`maturation_dispatch.py tick`) is the only program caller on the three running mods' paths (FlowWorks,
GimmeSomeSlack, Pyrelands). Since 1e91cc0953 it answers every refused launch in one place, whatever gate said no:

- a run that STARTED and DIED is substance: it counts on the fault loop (`run_void.system_cause`);
- a launch that NEVER STARTED is form: no fault, no pause, no trial; the tick starts one repair run with the refusal as
  its brief (`form_fault.owe_repair`, `maturation_dispatch.form_repair_step`), and the row reads `repairing: <what>`;
- a wait (`maturation_autonomy.wait_refusal`: a planned drain, a held bridge, control's `./pipe` stop) waits.

So the rows of section A need no edit of their own for the tick: their texts reach the tick as "never started". They
keep refusing an agent caller, who reads the brief line (`form_fault.BRIEF_LINE`, in every launched brief) and repeats
the act after the repair the text names. Column "repair named" says whether the text names that repair.

Classes: `form` | `substance` | `kept` (substance by his standing rulings: it keeps refusing) | `could-not-class`.

## A. The launch path (caller: the tick, and an agent that launches by hand)

| file:line | what it refuses | class | repair named | today (program caller) | becomes |
|---|---|---|---|---|---|
| `detached_helper.py:1212` (gate I1) | a seat not in SEATS | form | yes (the list) | repair run | converted (central) |
| `detached_helper.py:1217` (gate H4) | a model not in MODELS | form | yes (the list) | repair run | converted (central) |
| `detached_helper.py:1222` | an empty brief | form | no | repair run | converted (central) |
| `detached_helper.py:1227` | `--max-s` under the floor | form | yes (`none`) | repair run | converted (central) |
| `detached_helper.py:1232` | the ledger read 0 items | substance (blind instrument) | - | repair run (never started) | as is: the repair run meets the same blind read and names the Conductor after REPAIR_LAUNCH_MOST |
| `detached_helper.py:1234` | the item is not on the ledger | form | yes (file it) | repair run | converted (central) |
| `detached_helper.py:1239` (I6, `origin_check`) | the item is not on origin/main | form | yes (the `./publish` command); for a principal the launcher publishes itself (`origin_gate`, parallel run) | transient retry, then repair run | converted |
| `detached_helper.py:397`, `:1261` | the pool clone is held by another run | form (wait for the holder) | yes (finish/return commands) | repair run | converted (central) |
| `detached_helper.py:1068` (`card_refusal`) | a by-card brief without the card's words | form | `card_repair` adds the words itself (489968e096) | repaired in place | converted |
| `detached_helper.py:1052` (`drain_refusal`) | a launch during a planned account drain | kept (account order and leave lines) | yes (wait) | wait | kept, a wait |
| `detached_helper.py:1115` (gate F14, `launch_check_refusal`) | the item's declared launch checks refuse | could-not-class (each item declares its own) | partly (the Conductor's `--skip-launch-checks`) | repair run | converted for the tick (central); per-check class unread |
| `detached_helper.py:1355` | control's admission (`./pipe` stop, limits) | kept | - | wait (`WAIT_REFUSAL`, 1e91cc0953) | kept, a wait |
| `detached_helper.py:1236-1265` (`LAUNCH FAILED`) | systemd-run did not start the unit | substance (machine) | - | repair run (never started) | as is: the repair launch meets it too and names the Conductor |
| `maturation.py:2706`, `:2708` (`launch_mod`) | no cap, no item | form | yes | repair run | converted (central) |
| `maturation.py:2716`, `:2723` | a judge or driver below the model floor | form | yes | repair run | converted (central) |
| `maturation.py:2718`, `:2726`, `:2766` | the mod owes no blind cycle / visit / build work | substance (the state moved) | - | repair run | could be a wait; left as is (rare: the tick decides from the same state) |
| `maturation.py:2739` | the visit would drive an old JawaBench companion | form (a file the tool can make) | no | repair run | converted (central); polish: deploy the companion in place |
| `maturation.py:2755` | the visit's deploy failed | substance | - | repair run | as is |
| `maturation.py:2759` | the game copy differs from the repo | form | the visit check ignores other mods' files (2d58382ecc) | repair run | converted |
| `maturation.py:2763`, `:2768` | a stage with no build work; a batch of bars not refused | substance | - | repair run | as is |
| `maturation.py:2774`, `:2777` | run records unreadable; a twin run live | could-not-class / wait | yes (when it ends) | repair run | converted (central) |
| `maturation_dispatch.py:2025` (`file_and_publish`) | rimflow `spawn` refused the tick's item | form | names never refuse a filing (9e5768e86f) | repair run | converted |
| `maturation_dispatch.py:2421-2470` (`pilot_launch`), `:2392` (`launch_stage`), `:2492-2504` (`road_back_holder`) | a pilot launch on a wrong mod, state or a live run | could-not-class | yes for most | repair run | converted (central) |
| `maturation_dispatch.py:1547` (`cert_launch`) | the ledger launch of a red-decider builder failed | could-not-class | - | repair run | converted (central) |
| `maturation_dispatch.py` `cert_rerun_decide.wait` | a certificate rerun ended on a still-stale build, or did not start | form | - | was a Needs Conductor line and `clear` | converted at 75ababe76a: a repair run with the evidence |
| `maturation_dispatch.py` `decide_ingame` `visit_unfinished` | a visit stopped by its spend cap | form (a stop from outside) | - | was a hand resume | converted at 3bd2a545b6: `--continue-on-cap 1` |
| `maturation_dispatch.py:3970-4217` (`main`, `_pause_verb`, `_void`, `_clear`) | hand verbs with an empty `--why`, a bad unit | form | yes | agent caller only | as is (route 2: the text names the flag) |

## B. The ledger CLI (`rimflow`, `cli.py`) on the paths (caller: agents, and the tick through `spawn`)

| file:line | what it refuses | class | repair named | today | becomes |
|---|---|---|---|---|---|
| `cli.py` `_close_gate` `unchecked` (model.close_refusals) | a close with no level-tagged pass on the sha | form | - | refused every non-principal; three runs typed an L0 verify by hand | converted at 5a7ff497ad: the close goes, NOTE, `uncheckedLifted` |
| `cli.py` `_close_gate` owed / fail / guard | a criterion owed, a newest fail, a dead fix without its guard | substance | yes | refused | kept (the work is wrong or unchecked) |
| `cli.py` close `--live` | an operational close with no live line | form | yes (the three forms) | refused, route 2 | as is (route 2; seen on this run's own close, repaired at once) |
| `cli.py:152` (`resolve_seat`) | the seat cannot be told | could-not-class | yes | refused | as is |
| `cli.py:1890`, `:1930` (`_mint_or_die`, `namecheck`) | a bad item name | form | names file with a NOTE (9e5768e86f); namecheck is advisory | not refused | converted |
| `cli.py:2228` (`_card_owed_or_die`) | a by-card close whose card states work not done | substance | yes | refused | kept |
| `cli.py:2278` (`_claim_cap_check`) | a seat past its focus cap | could-not-class (a cap: its danger is not on the line) | yes | refused | left; polish: name its danger or remove it |
| `cli.py:2416-2454` (`block`), `:2490-2495` (`wait`), `:2539`, `:2545-2565` (`drop`), `:2592` (`supersede`) | an ill-formed block, a third wait, a cycle, a drop that strands dependents | form | yes | refused, route 2 | as is (route 2) |
| `cli.py:3778`, `:3841`, `:3921-3950` (bridge) | flyer flight; his OWNER hold; a delegated take of a working holder | kept | yes | refused | kept |
| `cli.py` claim lease (`REFUSED: ... is LEASED`) | an item leased to the same seat's earlier run | form | yes (the release token) | refused | as is (route 2; met by this run at 01:12 PST, repaired at once) |

## C. Hooks that can refuse a launched agent (`.claude/hooks`, caller: an agent)

| hook | what it refuses | class | repair named | becomes |
|---|---|---|---|---|
| `block_agent_over_slots.py` | a spawn past the seat's helper count | form for a detached run's own sub-runs | yes (wait) | converted at 3a5ad34924: every detached run has its own allowance (`rm-detached-` 5) |
| `block_agent_without_model.py` | a subagent with no `model`, or Haiku | form (no model) / kept (Haiku ban) | yes | as is (route 2) |
| `block_agent_coded_name.py` | a helper named by a bare code | form | yes | as is (route 2) |
| `block_unbounded_agent.py` | a spawn on an unbounded context | kept (machine-safety brake) | yes | kept |
| `block_blanket_git_stage.py`, `block_shared_tree_merge.py`, `block_worktrees.py`, `block_tmpfs_clone.py`, `block_unbounded_robocopy.py` | blanket staging, a merge in a shared tree, worktrees, a RAM-disk clone, a hanging robocopy | kept (they guard other runs' work and the machine) | yes | kept |
| `block_blind_scan.py` | a byte scan of a large artifact | form | yes (`measure`) | as is (route 2) |
| `block_ledger_lint.py`, `block_orphan_item_prose.py`, `block_dll_source_mismatch.py`, `block_unledgered_texture.py` | a push with a bad shard, orphan prose, a DLL without its source hash, an unledgered texture | form (a file a tool can make) / substance (a stale DLL) | yes | as is (route 2); polish: let `./publish` repair the lint itself |
| `block_canon_contradiction.py`, `block_forged_validation.py`, `block_hand_edited_sheet.py`, `block_delegated_cards.py`, `block_send_to_restarting.py`, `block_paste_handoff.py`, `queue_lint.py`, `role_result_before_stop.py` | canon contradiction, a hand-written validation, a hand-edited sheet, a delegated card, a message to a restarting window, a paste handoff, ledger hand edits, a role run with no result | kept (owner rulings) or substance | yes | kept |

## D. `./publish` and its tree checks (caller: every run)

| site | what it refuses | class | repair named | becomes |
|---|---|---|---|---|
| `publish.py` pipeline checks red after the commit | a change that turns a pipeline check red | substance | yes (the test) | kept |
| `publish.py` replay conflict | another run changed the same file | substance (two writers) | yes (merge by hand) | kept; this run met it four times and merged each |
| `selftest_calibration_rows_current.py` at publish | a judge brief's recorded hash is stale (`maturation_advance`) | form (a stamp a tool can make) | yes (`refusal_contract.py calibrate`) | as is (route 2; met at 03:00 PST, repaired at once); polish: publish runs the free calibrate itself |

## Counts

Counted over the rows above (one row per gate function, not per line), on the paths of the three running mods:
48 rows: form 27, substance 9, kept 6, could-not-class 6. Converted: 22 rows (section A as one principle for the
program caller, the close's `unchecked`, the detached sub-run slots, the certificate rerun's hand line, the capped
visit, and red_seen's start-up death, `judge_certificate.red_seen` at 6d31a7a8f8). Form rows left: 9, each answered by
route 2 (the text names its repair; the agent repairs and repeats at once, as the brief line says).

Left unread: the other 1123-line matches outside these paths (`designer_cleanse.py` 45, `testq.py` 37,
`regen_eligibility.py` 35, `seat_restart.py` 30, `leftovers.py` 20, `modcheck/cli.py` 19, the art tools, and the rest
of the per-file list in this run's notes). Those rows are the record for the next run.
