# Sweep: pipeline single-source consolidation (census and plan)

Item `RIMMANDRAKE_SWEEP_PIPELINE_FOR_SINGLE_SOURCE_SCRIPTS_KLUDGES_KEEP_STACKING`. A census and a plan. This run edited
no machinery, hook, brief or test. Tree read: `a1d3079d1b`, 2026-11-22 about 11:25 to 11:45 AM PST.

The owner's words, 2026-11-22 about 11:15 AM PST: "I would also like a detailed sweep of the whole pipeline to look for
opportunities to make more things into single source python scripts rather than llm prose or (worse) multiply
implemented competing systems. We keep finding that pattern. Kludging fixes together. It's time to consolidate into
real solid efficiency. Extract, simplify, generalize, prove coverage, retire old cruft"

Each claim is tagged `[measured]` or `[guess ~N%]`. UNMEASURED means the instrument could not see.

## What this builds on

`RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES` (`design/specs/2026-11-21-generalize-pipeline-repairs/`)
named nine principles and fixed four cases. This report does not repeat these cases:

- one definition of a test process (`test_process.py`, `fa04fa200c`);
- the selftest deadline (`4b996a6a74`);
- the mod an item names (`item_identity.py`, `1f5dd16429`);
- the stage a run ran, read from its launch record (`2e226ed330`);
- the game in the run record. That item owns it, and it waits for the game rename.

Its principle 2 ("one home for a fact") is the frame of candidates 1 to 6 below. Its principle 9 ("a rule that a tool
can do is done by the tool") is the frame of candidates 7, 9 and 11. `HOOKS_MERGE_ONE_DISPATCHER_PER_TOOL` (done)
measured hook latency as NOT_MATERIAL `[measured: hook_latency.py, run again in this sweep]`. Candidate 6 is not about
latency: it is about three hooks that split a command line three ways.

## Scope and counts

- Scope: the 85 `pipeline_files` patterns of `src/RimMandrake/Utils/pipeline_tests.json` match 168 tracked files. Add
  `src/RimMandrake/rimflow/roles/*.md`, `.claude/agents/`, `.claude/hooks/`, every `rm-*` unit under a `systemd/`
  folder, and the wrappers `pipe`, `game`, `bridge`, `publish`, `mirror` and `sync`. That gives 322 files, 256 of them
  not tests `[measured]`.
- How I searched: one `git grep` for each fact family (game driver, next step, spend, live account, model alias, item
  age, hold, local time, shell split, unit definition). I read the code of each match that computes the fact. I
  compared the answers live, or on one planted input, where the code could run. I also ran a dead-code scan over every
  top-level def in scope against all non-test files.
- Note: candidates 2, 5 and 10 reach files outside `pipeline_files` (`Utils/account_*.py`, `slot_allocator.py`,
  `switching_plan.py`, `running_now.py`, installers). The pipeline calls these files, or `rm-*` units run them. I name
  each one where it is cited.

| bin | files | what it means |
|---|---|---|
| in a candidate | 43 | named under a candidate below |
| single home already | 272 | the family greps found no second implementation in the file: 53 code, 59 unit files, 24 role and agent files, 70 boundary pages, 66 tests |
| could not look | 7 | large data and corpus files (three `modledger_readings/*.json`, `judge_calibration.json`, `evidence_gate_corpus.json`, the two `block_delegated_cards_*.json`). A grep for rules does not apply to records. I did not read their contents. |

"Single home already" is a grep-level verdict. A rival implementation that uses none of the searched words is not
excluded `[guess ~75% that the 53 code files hold no further rival of the families above]`. I read the 24 role files
only by keyword. The two prose candidates are what that read found.

## Ranked candidates

Rank is by failures on record first (a stall, a per-case repair item, hand acts), then by the number of places that
compete. Effort is in weighted tokens (`weighted_v2`) for one Opus fixer run. Each effort is a `[guess ~50%]` within a
factor of two, made by comparing with the generalize item's runs.

### 1. What a mod does next, and whether it may run now — HIGH

**The fact.** For one mod: may the pipeline run it now (yes, held by the owner, OFF by a control act, paused at a
ceiling, waiting, or UNMEASURED), and what is the next act and who does it.

**Every place today** `[measured: read and run]`:

- `src/RimMandrake/rimflow/maturation.py:1957` `next_step`: the gate verdict from the stage record only. It knows no
  hold, no control act and no tick decision.
- `maturation.py:1920` `dispatch_overlay`: replaces an "automatic" claim with the tick's reading. Only the CLI
  `maturation.py next` (line 5253) applies it.
- `src/RimMandrake/rimflow/maturation_dispatch.py:911` `decide` (the tick) and `:3848` `forecast`.
- `src/RimMandrake/rimflow/control.py:2777` `why` (`./pipe why`): control acts, holds, game holds and the tick's last
  decision.
- `src/RimMandrake/Utils/maturation_now.py:309,314` (the status page): "Waiting on" and "Next" come from journal prose
  (`j.get("next")`). The stage comes from the record (`:283`).
- Callers of the raw `next_step`, with no overlay: `maturation_autonomy.py:1727` (`steward_brief` writes the raw text
  into a launched brief) and `owed.py:449` (`live_rows`).
- Who is held: `mod_owner_hold.held` (`mod_owner_hold.py:179`) is the reader. `owed.py:452-463` (`held_names`,
  `not_held`) matches item ids by upper-cased words instead. `maturation_rescue.py:642` and `ops_watch.py:2951` take
  `set(load())` by exact key.

**Where they disagree today** `[measured, 2026-11-22 11:30 AM PST]`:

| mod | `./pipe why` | `maturation.next_step` | status page "Next" |
|---|---|---|---|
| LeaningScrub | BLOCKED HELD BY OWNER (2026-11-16) | "NEXT (automatic: the Dispatch tick launches a capped builder)" | "fresh Stage 4 exam of the rewritten artifacts, then coverage/Lock" |
| ExplosiveKnockback | BLOCKED OFF (act `ct_000026`, 2026-11-18) | "NEXT (automatic: the Dispatch tick launches it): blind cycle 6" | UNMEASURED |
| Graffiti | BLOCKED HELD BY OWNER (2026-11-18) | "PAUSED: a Conductor hold stands on stage 4+5" | "on his word, the Designer reopens" |
| 9 other mods | — | an answer | UNMEASURED |

**Failures on record.** `RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS`: `next_step` said "automatic" for
six hours while the tick had paused the mod. The repair (`dispatch_overlay`) covers one caller of three. Also `1b79ae76b0`
(`pipe next` had its own forecast). `maturation_hands.py list --all`: 96 hand acts. 71 of them are a person deciding
what the tick decides: 35 `hand_run` (18 "a fix on the tick's own ticket", 9 blind judges, 8 in-game drivers), 15 stop
`clear`, 12 `coverage_release` and 9 `ceiling_release`. 11 of them are open `[measured]`. Whether one module would
remove those hand acts is a `[guess ~40%]`. The hand runs may come from slow ticks, not from a wrong answer.

**Proposed single home.** `src/RimMandrake/rimflow/mod_next.py`, one function `next_for(root, mod, now)`. Inputs: the
stage record, the control store's acts and holds (`control.py`), `mod_owner_hold.held`, and the tick's last reading.
One output: `{stage, may_run: probe_result(yes | held | off | paused | ceiling | waiting | UNMEASURED, why),
next_act, by}`. `maturation.next_step` stays as the gate part that `next_for` calls. Callers: `./pipe why`,
`maturation.py next`, `steward_brief`, `owed.live_rows`, and the status page's Next and Waiting-on boxes. The journal
stays as history, and the page no longer reads its `next` line.

**How coverage is proved.** An equivalence script replays the recorded inputs through the old paths and the new one:
the tick readings that the dispatch step keeps, `infrastructure/state/ledger/events/*.jsonl`, and the control acts export
(`rm-control-acts-export`, 95 acts at rev 95). For each (mod, tick time), it compares the old `pipe why` verdict class
with `next_for().may_run`, and the old CLI `next` with `next_for().next_act`. They must agree wherever the old CLI was
right. Each disagreement is listed and classed by hand once. Planted faults, each red on the new code: a held mod, an
OFF act, a tick reading older than `DISPATCH_READING_MAX_AGE_S`, a ceiling pause, and an unreadable control store
(which must give UNMEASURED, never "yes").

**Deleted when the proof passes:** `dispatch_overlay`, the journal `next`/`waits_on` reads in `maturation_now.py`,
`owed.held_names`/`not_held` (it uses `mod_owner_hold.held`), and the overlay branch of the CLI `next`.

**Size:** about 7 files. About 1.5M weighted tokens. It comes first: candidate 3's stage-spend box reads the same page.

### 2. Which Claude account this machine is logged in as — HIGH

**The fact.** The account that this machine's sessions use now, or UNMEASURED with its cause.

**Every place today** `[measured: git grep '"--json", "status"' and 'oauthAccount']`. All are outside `pipeline_files`:

- `src/RimMandrake/Utils/account_failover.py:148` `live_account`: `raw_decode` loop, timeout 120 s.
- `src/RimMandrake/Utils/switching_plan.py:849` `switcher_status`: the same `raw_decode` loop, copied, 120 s.
- `src/RimMandrake/Utils/slot_allocator.py:391` `live_login_name`: `json.loads` of the whole stdout, 20 s.
- `src/RimMandrake/Utils/running_now.py:1486` `collect_inuse`: `json.loads`, and it also needs `ok`, 10 s.
- `src/RimMandrake/Utils/account_handover.py:104`: bare `json.loads(...)["live"]`, no guard, no timeout.
- `src/RimMandrake/Utils/account_usage.py:205` `live_email`: reads the login JSON file's email, not `claude-account`.
  `:376` reads a remote machine with `claude-account status --json` over ssh.
- The same constant twice: `STALE_PENDING_S = 2400` at `account_failover.py:63` and `switching_plan.py:64`.

**Where they disagree.** Today all read `lukas` `[measured]`. On a planted output with one warning line before the
JSON: `slot_allocator` gives None and `switching_plan` gives `lukas` (acceptance ACCOUNT, red). `account_handover`
raises on the same input. `running_now` gives UNMEASURED.

**Failures on record.** `account_failover.py:150`: "the old 2000-char tail cut its opening brace -> None -> stage 2
never fired". Also `d8a52e54c4` and `dd37ba2758` (an unmeasured login was paced on the previous account) and
`551b86c17d` (a hand switch attributed by a time window) `[measured: review.md, principle 2 and 5 lists]`.

**Proposed single home.** `src/RimMandrake/Utils/account_live.py` `live_login(machine=None) ->
probe_result(name | UNMEASURED cause)`. It parses once (tolerant of text around the JSON), with one deadline and one
staleness constant. All seven places import it. The ssh reader passes `machine`.

**How coverage is proved.** Recorded inputs: `~/.claude-accounts/log.jsonl` (each switch), and status outputs captured
into a fixture folder: clean, warning-prefixed, truncated at 2,000 characters, empty `live`, rc ≠ 0, timeout. Each old
reader and the new one run on each fixture. The new one must equal the most tolerant old answer on every clean or
prefixed case, and give UNMEASURED on the broken cases, where today two readers give None and one raises. Planted
faults: the truncation and the prefix must be red on `slot_allocator`'s old parser.

**Deleted when the proof passes:** five parsers, one duplicate constant, and the `RM_SLOT_LIVE_LOGIN` seam (the new
module carries one seam).

**Size:** 7 files. About 0.6M weighted tokens. No dependency.

### 3. What a run spent, and in which unit — MEDIUM

**The fact.** One run's spend in `weighted_v2` tokens, and the stage and version that it counts against.

**Every place today** `[measured]`:

- Unit of a stored figure: `role_launch.py:870` `tokens_v2` (no `token_unit` = v1, weighed up); `role_launch.py:993`
  `run_spend` (no `token_unit` = v2, taken as it is); `maturation.py:228-252` `row_unit` (no `token_unit` = v1 or v2
  by a hard-coded switch time `V2_SWITCH`).
- Where a run's spend is stored: the control store's run record (`role_launch.py:1283`), the detached record
  (`detached_helper.py:1654` `outcome`), a mod record's `spend` list (`maturation.py:1639` `add_spend`), and
  `version/run_spend.jsonl` (`maturation_dispatch.py:3128` `record_spend`, `maturation.py:1669`). Merged by
  `maturation.py:1682` `spend_rows` and `:1694` `version_spend_rows`.
- Readers that compute it again: `detached_helper.py:1756-1846` (`result_cost`, `recover_cost`, `measured_cost`,
  `backfill_cost`, in dollars), `spend_watchdog.py:89` (from the transcript), `run_void.py:683` `void_spend`
  (dollars), `coverage_judge.py:826` `spend`, `control_agent_drill.py:149` `spend`, and `maturation.py:255`
  `_spend_row` (from the status page's run view).

**Where they disagree** `[measured]`: one Fable record of 2026-11-15, 1,000 tokens, no `token_unit`. `run_spend`
counts 1,000. `tokens_v2` counts 2,000 (`v1_bound`). `row_unit` names it `weighted_v1`, so the stage total leaves it out
(acceptance SPEND, red). The daily cap reads only today's records, and all of them carry a unit. So the cap is right
today. Only history and stage totals differ `[guess ~85%]`.

**Failures on record.** Three per-case repairs are named in the code: `RIMMANDRAKE_STAMP_STAGE_SPEND_ROWS_ONE_UNIT`,
`RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER`, `RELABEL_SPEND_PRINTERS_STILL_V1`. Also `1a51e02130` (a
spend field with no reading read 0).

**Proposed single home.** `role_launch.tokens_v2` is already the one weigher. Make it the only function that reads a
stored figure: `run_spend` and `row_unit` call it, and `V2_SWITCH` goes. One store holds a run's spend: the control
store's run record (unit, model, mod, stage). `run_spend.jsonl` and the mod record's `spend` list become views that a
program builds from it.

**How coverage is proved.** Recorded inputs: the 1,791 detached records under `D:\ClaudeWork\rimmandrake\dispatcher\detached`
(715 Opus, 80 Sonnet, 55 Fable with tokens; 629 with no model), every `run_spend.jsonl`, and each mod's stage record
`[measured counts]`. For each run, the old stage total and the new one must be equal for every stamped record. Each
unstamped record is listed with both figures. Planted faults: an unstamped Fable record (must give one answer
everywhere), and a model not in `MODEL_PRICES` (must give UNMEASURED, never 0).

**Deleted when the proof passes:** `V2_SWITCH`, `_unit_by_time`, the unit branch of `run_spend`, and the
`run_spend.jsonl` writer and its lander (`maturation_dispatch.py:3104` `land_spend`), once the view is built.

**Size:** about 6 files. About 1.0M weighted tokens. Do it after candidate 1 (both touch `maturation_now.py`) and with
candidate 4 (the model of a record).

### 4. Which model an alias means — MEDIUM

**The fact.** The full model id for an alias (`fable`, `opus`, `sonnet`) and for a tier name.

**Every place today** `[measured]`: `role_launch.py` `MODEL_VARS` with `resolve_model` (`:761`; opus, sonnet and haiku
from the environment; no `fable`); `detached_helper.py:107` `MODEL_IDS = {"fable": "claude-fable-5-2"}`, hard-coded;
`detached_helper.py:97` `model_tier`; `mod_model.py:36` `pinnable` and `:44` `pin_id`;
`Utils/install_wt_seat_profiles.py:213`, a hard-coded `claude-fable-5-2` for the BENCH profile.

**Where they disagree** `[measured]`: `resolve_model('fable')` raises "unknown model 'fable'", while `pin_id('fable')`
gives `claude-fable-5-2` (acceptance MODEL, red). `pin_id('opus')` raises "pinnable are fable". In this shell
`ANTHROPIC_DEFAULT_FABLE_MODEL` is set and the opus and sonnet variables are not, so `resolve_model('opus')` also
raises.

**Failures on record.** One detached record carries `unknown_model: model alias 'opus': its env var
ANTHROPIC_DEFAULT_OPUS_MODEL ...`: its spend is UNMEASURED `[measured]`. On 2026-11-21 a full id was refused three
times and FlowWorks paused (`maturation_autonomy.py:1131`, repaired by `model_tier`). Also `839d7e1393` and
`29c5f7491e`.

**Proposed single home.** `role_launch.resolve_model`, with `fable` added to `MODEL_VARS` (`ANTHROPIC_DEFAULT_FABLE_MODEL`),
and a `tier()` beside it. `MODEL_IDS`, `model_tier` and `pinnable` read it. The profile installer reads the
environment (user rule: read the environment, never a hard-coded account or prefix).

**How coverage is proved.** Recorded inputs: the `model` and `model_id` fields of the 1,791 detached records and of the
control store's runs. Old `model_tier` and old `pin_id` against the new functions on each value. They must agree where
the old one answered. Planted faults: an unset variable (must raise by name), and a Haiku id (must stay refused).

**Deleted when the proof passes:** `MODEL_IDS`, the private tier list, and the hard-coded id in the profile installer.

**Size:** 4 files. About 0.4M weighted tokens. Do it with candidate 3.

### 5. Who drives a game: two readers still read the BRIDGE glance file — MEDIUM

**The fact.** Who holds each game's driver lock.

**Every place today** `[measured]`: the home is `rimflow/game_lock.py` with its per-game `DRIVER_LOCK.json`
(`design/specs/2026-11-21-one-game-lock/boundary.md`). Two readers still read the glance file
`infrastructure/state/BRIDGE` instead: `Utils/preflight_bridge.py:54,199` (`c_bridge_lease`, its own clone's file,
ArchBig only), and `Utils/running_now.py:66,541` (`collect_bridge`, the files of two fixed clones,
`/home/mandrake/rm/dispatch` and `/home/mandrake/rm/bench`). The writer is `model.py:1252,1326`.

**Where they disagree** `[measured]`: in this helper clone there is no BRIDGE file, and `/home/mandrake/rm/dispatch` has
none either. `game_lock.py query all` says "ArchBig: HELD by BENCH since 11:22 PST". `c_bridge_lease` in this clone
gives UNMEASURED ("cannot read"). `running_now` reads only bench's file, and it never shows ArchSmall.

**Failures on record.** `RIMMANDRAKE_BUILD_ONE_GAME_LOCK_CLAIM_FOUR_RECORDS_DISAGREE` (four records disagreed); this is
what is left of it. `b5c602d88d` and `98ba034b57` (a gate read Archmagi's bridge for a SteveDesktop act).

**Proposed single home.** `game_lock.query()` (already there). The two readers call it for each game by name.

**How coverage is proved.** `fake_two_games.py` (exists) stages a held ArchBig and a free ArchSmall, with no BRIDGE file.
The old readers read UNMEASURED or one game. The new ones must read both games and equal `game_lock.py query all`.
Planted fault: an unreadable lock must give UNMEASURED, never FREE.

**Deleted when the proof passes:** `BRIDGE_FILES`, `BRIDGE_FILE` in `preflight_bridge.py`, and (after a grep that finds
no other reader) the glance-file writer in `model.py`, with its false header (see "False statements").

**Size:** 3 files. About 0.3M weighted tokens. No dependency.

### 6. How a hook splits a shell command line — MEDIUM

**The fact.** The simple commands that one Bash command line runs.

**Every place today** `[measured]`: `block_blanket_git_stage.py:203` `segments` (quote-aware, heredoc-aware, unwraps
`bash -c`); `block_blind_scan.py:207` `segments` (its own `_commands`, unwraps `bash -c`); `block_tmpfs_clone.py:71`
`segments` (`shlex` with punctuation, no `bash -c`); `block_unbounded_robocopy.py:40` `_words`. The other Bash hooks
(`queue_lint`, `block_shared_tree_merge`, `block_canon_contradiction`, `warn_unclosed_queue_item`, `block_worktrees`)
define no splitter function of their own `[measured: grep for a segments or words function]`. How each of them reads
the line was not read.

**Where they disagree** `[measured]` on `cat > notes.md <<'EOF' / git add -A / EOF` (a file write, nothing staged):
`block_blanket_git_stage` sees one command. `block_blind_scan` sees two, one of them `git add -A`. `block_tmpfs_clone`
sees three, `EOF` included (acceptance SHELL, red). On `bash -c 'git add -A'`, `block_tmpfs_clone` does not unwrap. On
`echo $(git add -A)`, only `block_tmpfs_clone` splits it. On `git add -A && echo hi`, all three agree (green control).

**Failures on record.** `block_blind_scan.py:211`: "a scan hidden one quote deep... Found by red team 2026-08-21". No
false refusal from a heredoc body was found in the ledger `[measured: not searched in transcripts; UNMEASURED]`. So
this ranks below the candidates with failures.

**Proposed single home.** `.claude/hooks/shell_words.py`, one function `commands(line) -> [argv]`, with the heredoc
rule of `block_blanket_git_stage` (a body counts only when a shell reads it) and the `bash -c` unwrap. Each Bash hook
imports it and keeps only its own decision.

**How coverage is proved.** Recorded inputs: `src/RimMandrake/Utils/hook_latency_corpus.json` (166 real tool calls,
harvested 2026-11-06) and the Bash calls in `hook_latency_transcripts.json`. Each hook's allow or deny verdict on each
call, before and after. They must be equal, and each changed verdict is listed and classed. The hook selftests
(`selftest_block_*.py`) must stay green. Planted faults: a heredoc that writes text, `bash -c`, `$( )`, and a backslash
newline.

**Deleted when the proof passes:** three `segments` functions and `_words`.

**Size:** 6 hook files. About 0.8M weighted tokens. No dependency.

### 7. A ledger note lands its own shard — MEDIUM (prose that should be a script)

**The act.** After a `rimflow note` (or any ledger write) in a helper clone, the event file is landed on origin/main.

**Every place today** `[measured]`: the detached brief tells every helper to run `./publish -m "ledger: <ID> note"
infrastructure/state/ledger/events/BENCH.jsonl` after each note, and to publish `OWNER.jsonl` too after a
`--per-ruling`, `--owner-said` or `--by-card` event (`detached_helper.py`, brief lines 28 and 146). `publish_command`
(`detached_helper.py:276`) prints the command and says: "seven lessons said 'publish the shard first' and agents kept
meeting the refusal. Printed, never run: no auto-publish."

**Evidence.** 6,465 of 10,531 commits since 2026-11-13 have a `ledger:` subject, and 1,513 of them are notes `[measured:
git log --oneline]`. The choice of which shard to land is a fixed rule (the seat, plus `OWNER.jsonl` when the
provenance flag says so).

**Proposed single home.** `rimflow note|file|close ... --publish`. The CLI knows the shard it wrote, and it lands
exactly that shard with `./publish`. The brief lines go. "No auto-publish" was a decision: the Conductor confirms that
an opt-in flag does not break it.

**How coverage is proved.** In a temp repo with a bare remote: a note with `--per-ruling` and `--publish` must land both
shards, and a plain note must land only the seat shard. Compare with the commands that `publish_command` prints for the
same events.

**Deleted when the proof passes:** two brief paragraphs, sent to every detached run.

**Size:** 2 files. About 0.4M weighted tokens.

### 8. Unit definitions live in two homes, and some live only on the machine — MEDIUM-LOW

**The fact.** The text of each `rm-*` systemd unit.

**Every place today** `[measured]`: 59 unit files under `src/RimMandrake/Utils/systemd/`,
`src/RimMandrake/Utils/telemetry/systemd/` and `src/RimMandrake/rimflow/systemd/`. Unit text also sits inside Python
installers: `Utils/deadman_check.py:646-654`, `Utils/timers_guard.py:352-360`, `Utils/switching_plan.py:1200-1207`,
`Utils/account_usage.py` (`install`), `ops_watch.py`, `testq/testq.py`, `steve_cpu_retest.py`. On Archmagi,
`rm-deadman`, `rm-account-usage`, `rm-ops-watch`, `timer-guard` and `account-plan` exist only as installed files: no
repo unit file holds them. `rm-harness.slice` sits in `src/RimMandrake/Utils/`, not in a `systemd/` folder. 13
retired units are masked symlinks (`rm-relentless*`, `rm-pulse`, `rm-whittle-now*`, `rm-artisan-now*`,
`rm-store-ledger-diff*`).

**Where they disagree** `[measured]`: `deadman_check.py`'s text says `OnCalendar=*:03/15`, and the installed timer
agrees. `ops_clocks.json` lists `rm-ops-watch.timer` and `rm-dispatcher.timer` as live Operations clocks, but both are
disabled. Since 2026-11-05 and 2026-11-06 their work runs as metronome phases (`deadman_check.py:60-63`).

**Proposed single home.** Every unit as a file in one `systemd/` folder. One installer (`ops_clocks.py`, which already
checks the clocks) installs and compares them. The Python installers keep no unit text.

**How coverage is proved.** For each unit: render the embedded text, diff it against the installed file and the new
folder file, and list every difference. `ops_clocks.py check` must be green after the move. Planted fault: a changed
`OnCalendar` in the folder must read red at check.

**Deleted when the proof passes:** seven embedded unit texts, the two disabled clock rows in `ops_clocks.json`, and the
13 masked symlinks (each is `/dev/null` and runs nothing).

**Size:** about 9 files. About 0.6M weighted tokens.

### 9. Stale items: 990 open items have no event in 14 days, and no rule says what stale is — LOW

**The fact.** Which open items are idle, and what happens to an idle item.

**Every place today** `[measured]`: none. No item reader (`priority.py`, `owed.py`, `cli.py`, `render.py`,
`ops_health.py`, `rimflow_metrics.py`) has an age rule for an item. `designer_stage.stale_stage` covers Designer stages
only.

**Evidence** `[measured: model.read() + model.replay(), last event time over each item's history]`: of 1,933 open items,
990 have had no event in 14 or more days: 470 `proposed`, 330 `built`, 135 `validated`, 54 `ready`, 1 `doing`. The
`doing` one is `TAR_LOOK_TUNE_THICK_AND_SLOW`, idle 37 days. The oldest are `KINETIC_BLAST_WEAPONS_1` (validated, 43
days) and `MESSY_CONDUIT_MOD_1` (built, 43 days). I did not show that any of them steers a tool today. That is why this
candidate is LOW. (My first count, 1,377, used creation time by mistake; I measured again with the event times.)

**Proposed single home.** `rimflow/item_idle.py`: fixed classes (`built` not verified, `validated` not closed,
`proposed` with no owner, `doing` with no live lease), one list, read by `rimflow next` and the Auditor. A drop or close
stays an agent's act.

**How coverage is proved.** A fixture ledger with one item of each class plus a fresh one. The script lists exactly the
four, and on the real ledger its count equals the measured 990 (within the events of the hours between).

**Size:** 2 files. About 0.3M weighted tokens. Acceptance test: none yet, because the class list is the Conductor's
decision. After that decision, the fixture test above.

### 10. The four push guards run twice — LOW (cruft)

`block_ledger_lint.py`, `block_dll_source_mismatch.py`, `block_orphan_item_prose.py` and `block_unledgered_texture.py`
are registered as PreToolUse Bash hooks on the text `git push`. They also run as git's pre-push
(`infrastructure/githooks/pre-push`, `core.hooksPath` is set) `[measured]`. `./publish` pushes through git, so only
pre-push fires on the normal path. A literal `git push` fires both. No disagreement is known. Proposed: remove the four
PreToolUse registrations. Proof: the four hooks' selftests drive real pushes through pre-push already
(`selftest_block_orphan_item_prose.py`, `selftest_block_ledger_lint.py`). Note: pre-push "fails open" on a crashed guard
(exit > 1). That is principle 5 of the generalize item, so it is listed there, not here. Size: 1 file, about 0.1M
weighted tokens.

### 11. Two role-file steps that a tool already does or could do — LOW

- `src/RimMandrake/rimflow/roles/operations.md:248`: "For each open flag older than one run, find its kind: band, run,
  silent, or target". `ops_watch.py:3281-3333` already computes the kind, and `digest.md` prints it as the first word
  of each flag line (`- silent testing.steve_nothing_h_7d ...`) `[measured]`. Change the step to "the kind is the first
  word of the flag line". Principle 9 of the generalize item.
- `src/RimMandrake/rimflow/roles/producer.md:139-143`: "find your last run": the newest earlier folder whose `plan.md`
  ends in `RUN COMPLETE <stamp>`, else the goals block's date. This is a fixed rule. Proposed:
  `producer_last_run.py`, which prints the stamp, plus one line in the role file. No failure on record.

Size: 3 files, about 0.2M weighted tokens together.

### 12. Local time is printed five ways — LOW

`control.py:298` `pac`, `maturation_dispatch.py:267` `pac`, `pipeline_control.py:198` `pac_str`, `pipeline_pause.py:165`
`pac`, `red_dispatch.py:83` `pac`, `maturation.py:160` `pac_heading`, `maturation_now.py:140,455`,
`account_usage.py:734` `_pacific`. For the same instant `[measured]`: "2026-11-22 06:13:20 PM PST", "2026-11-22 6:13 PM
PST", "2026-11-22 6:13 PM" (no zone, `pipeline_pause`), and "Sun Nov 22 18:13 PST". `maturation_now.pac` takes a
datetime, not epoch seconds. Proposed: `rimflow/pactime.py`, with one short and one long form. Proof: each old function
and the new one run on a fixed list of instants (DST edges included), and each changed string is listed. No failure on
record. Size: 9 files, about 0.3M weighted tokens.

## Build order

Each group is one fixer run: same cause or same files. Each acceptance test is a line of
`design/specs/2026-11-22-pipeline-single-source-sweep/acceptance.sh`. All lines read RED on `a1d3079d1b` `[measured]`.
Run one line with `bash design/specs/2026-11-22-pipeline-single-source-sweep/acceptance.sh <NAME>`. Must-stay-green
checks seen in this sweep: ACCOUNT on clean output reads GREEN, and SHELL on `git add -A && echo hi` reads GREEN.

| order | group | candidates | acceptance (expected: 1 GREEN line each) | effort `[guess]` |
|---|---|---|---|---|
| 1 | next step and may-run | 1 | `acceptance.sh NEXT` | ~1.5M |
| 2 | live account | 2 | `acceptance.sh ACCOUNT` | ~0.6M |
| 3 | spend and model of a run record | 3, 4 | `acceptance.sh SPEND`, `acceptance.sh MODEL` | ~1.4M |
| 4 | game driver readers | 5 | `acceptance.sh BRIDGE` | ~0.3M |
| 5 | hook shell splitter, and push guards once | 6, 10 | `acceptance.sh SHELL`, `acceptance.sh PUSH` | ~0.9M |
| 6 | ledger write lands its shard | 7 | `acceptance.sh PUBLISH` | ~0.4M |
| 7 | units in one folder | 8 | none in the script; the fixer writes `ops_clocks.py check` red on an embedded unit text first | ~0.6M |
| 8 | role steps and local time | 11, 12 | `acceptance.sh TIME`; role steps: none, a prose edit | ~0.5M |
| — | stale items | 9 | waits for the Conductor's class list | ~0.3M |

Groups 2, 4, 5 and 6 are independent of each other and of group 1. Group 7 comes after group 2, because both edit
`switching_plan.py` and `account_usage.py`. Group 3 comes after group 1, because both edit
`maturation_now.py` and `maturation.py`. The NEXT line is red only while LeaningScrub is held. The fixer adds a fixture
case (a held mod, and an OFF act), so the test does not depend on the live hold.

Total for the eight groups: about 6.2M weighted tokens for Opus fixer runs `[guess ~50%]`.

Duplicate check (one pass over this list): no two candidates name the same fact. Candidates 3 and 4 share the run
record, so they are one group. Candidates 2 and 8 share two files, so they are ordered. Candidate 5 is not the
generalize item's open step (the game in the run record): that step is about a run's game, and candidate 5 is about
who holds a game's lock.

## False statements found in docs

- `src/RimMandrake/rimflow/owed.py:446`: `live_rows` "-> [next_step row] for every versioned mod not held by the
  owner". It returns every versioned mod. The hold filter is `not_held`, applied later.
- `src/RimMandrake/rimflow/mod_model.py:36`: "detached_helper.MODEL_IDS, the one alias table". `role_launch.MODEL_VARS`
  is a second alias table (opus, sonnet, haiku), and the two do not overlap (candidate 4).
- `src/RimMandrake/rimflow/model.py:1307,1310` (the BRIDGE file header): "Mirror of the rimflow ledger" and "rimflow
  bridge who (re-derives this from the ledger)". The home is the driver lock: "nothing decides from them [the ledger's
  bridge events] where a lock is readable. The BRIDGE glance file is printed from the lock."
  (`design/specs/2026-11-21-one-game-lock/boundary.md:20-21`).
- `src/RimMandrake/Utils/systemd/ops_clocks.json` (`clocks`): it lists `rm-ops-watch.timer` and `rm-dispatcher.timer`
  as Operations clocks. Both are disabled on Archmagi. Their work runs as metronome phases (`deadman_check.py:60-63`).

## Polish (no ticket)

- Dead code reached only by tests or by nothing `[measured: name count over all non-test files]`: 6 defs, 48 lines:
  `refusal_contract.py:462` `prejudge`, `control.py:1556` `install_dropin`, `control.py:1570` `remove_dropin`,
  `modledger.py:232` `cited_file_exists`, `run_void.py:382` `_void_items`, `modledger_backfill.py:262` `_closed_like`.
  Three of the files dispatch by name (`getattr`), so a string may still reach them `[guess ~60% dead]`.
- 260 of the 1,791 files in the detached records folder do not parse as JSON. I did not class them; they may be result
  files that are not records.
- `account_failover.py`: its stage-2 text says "retire the timer" once the reset date passes. I did not check whether
  that date has passed.
- Every `maturation_now.py` import prints a `SyntaxWarning` for an invalid escape sequence (`<unknown>:2344`).

## Could not look

- The seven data files named in the counts table.
- SteveDesktop's units, hooks and clones: not reached in this sweep.
- Transcripts: I did not search them for false refusals by a hook (candidate 6) or for hand repeats of a role step
  (candidate 11). UNMEASURED.
- The tick readings: I did not open their files. Candidate 1's equivalence run must find their path
  (`maturation.dispatch_reading`).
