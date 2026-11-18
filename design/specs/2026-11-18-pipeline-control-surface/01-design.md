# 01 - Pipeline control surface: design pass 1 (Opus)

Status: pass 1 of Deep-Design 3x2, 2026-11-18, complete. It was written blind to `02a-gpt-blind.md`, which landed at 10:44 and was not read. Design only: no code changed, nothing launched. It has not been reviewed: the GPT critique pass is next, and `code_review_status` reads DIRTY.
Evidence scratch: `D:\ClaudeWork\rimmandrake\design_pcs\` (act outputs in `acts\*.out`, the systemd-run call-site list in `systemd_run_files.txt`).
Tags: [measured: how], [guess ~N%], [assumed]. The claims the pick rests on are collected in section 6.

## 1. Problem, constraints, success measures

### 1.1 The problem restated
The owner and the Conductor must be able to steer the Maturation Pipeline with one cheap command per act: read it, pause it, switch any part off, reorder it, change or give back any allowance, void a run, release spend, and ask what will happen next. Today each of these is a hunt across about 20 stores, in 3+ git clones, through about 25 verbs. Some of those stores only take effect after a publish (tests that can refuse) plus a pull of a clone nobody types in. Some launch paths read none of them.

Two structural causes make it hard. A third makes it untrustworthy.
1. **Control state lives in the code tree.**
   - `mod_owner_hold.json`, `maturation_dispatch.json` (`enabled`, `advancing`, the `*_enabled` flags), `design/concepts/<Mod>/stage.json` (granted looks) and the journal hold lines are all repo files.
   - The live tick runs from `/home/mandrake/rm/dispatch`, not from the clone the Conductor types in [measured: `systemctl --user cat rm-maturation-dispatch.service`, WorkingDirectory and ExecStart].
   - So a control act takes effect only after edit, then `./publish` (tests), then the dispatch clone pulling.
   - Today's Graffiti hold took about 22 minutes: edited in bench ~10:20; publish refused by a test that pinned the live list; landed `b09f49ab64` at 10:38-10:39; the live reading honoured it at ~10:42 [measured: git log, reading.json].
   - Meanwhile `status` typed in bench already read "HELD BY OWNER", because `mod_owner_hold.PATH` is relative to the clone that runs it. That status was a lie about the live pipeline [measured].
2. **Admission is decided by each caller, not at the launch.**
   - The primitive most pipeline runs pass through, `detached_helper.launch`, reads no hold, no pause and no `enabled` flag [measured: grep, 0 references].
   - Each caller re-implements part of the check:
     - the tick filters `advancing` by the owner hold (`maturation_dispatch.py:2796`)
     - the autonomy seed skips held mods (`maturation_autonomy.py:155`)
     - `role_launch` checks the hold (`:2506`)
     - `designer_cleanse` checks it (`:987`)
     - `red_dispatch` reads only `enabled`
     - cert-rerun (`maturation_dispatch.py:1149`) and `designer_cleanse.py:2029` call `systemd-run` raw
   - 29 non-selftest files call `systemd-run` [measured: grep, list in `systemd_run_files.txt`].
   - This makes a paths x switches matrix where every cell is a separate bug. Today's 10:25 launch went through one of those cells: a journal hold that blocks advance but not launch.
3. **Consumption is counted in many shapes, with no notion of void.**
   - Per-mod dicts in the maturation `state.json`: steward tries per state key, fixers, blind_auto, ingame_auto, launches, pilot_launches, holder_road_back, cert_rerun, road_back, releases_used, stopped, cleared [measured: key census of state.json].
   - Plus a grant in the repo (`coverage_release_granted`), refusal counters in `refusal_contract/counters.json`, a Test Pilot streak derived from ledger events, and a chain cap in code (`role_launch.CHAIN_MAX_PER_DAY=8`).
   - Each reader computes its own count. None has a way to say "this run does not count". Giving a look back means a new grant, and a new grant needs publish.
   - Run-to-mod attribution is inferred, not declared. `maturation_now` placement counted the void and pause helpers as "live on Graffiti" [measured: reading.json at 10:39]. That protected Graffiti by accident and can charge Graffiti's stage spend for work that was not Graffiti's.

A fourth, smaller cause is overloaded words.
- "PAUSED" already means three things: past the stage ceiling, steward tries exhausted, and coverage stopped.
- Fixers still run on a "PAUSED" mod (`RIMMANDRAKE_RUN_FIX_TICKETS_WHILE_PAUSED`) [measured: maturation_autonomy.py docstrings].
- A planned owner pause must not reuse a word that today allows launches.

### 1.2 Constraints (binding on every option)
- **Weighted tokens are the scarce resource.**
  - Each tool call re-sends the caller's whole context, so the call count dominates the bill; output bytes come second.
  - A Conductor at 100k context making 15 calls to stop one unit re-sends ~1.5M input tokens [guess ~70%: cached input is weighted below fresh input, but the count is what multiplies].
  - So the measure is calls per act first, bytes per act second.
- **No agent is told its spend** (ruling 2026-11-16). Control output may print a mod's stage spend to the Conductor (it already does, in pause lines), but nothing written into a launched brief may.
- **The pipeline fixes its own defects** (ruling 2026-11-15).
  - A control the pipeline itself needs, such as voiding a run its own launch killed, must be issued by the pipeline in code (auto `void_system`), not left for a person.
  - A broken control path is a filed defect with a failing test, never a workaround in the Conductor's head.
- **"Could not look", "failed", "zero" and "empty" are four answers.**
  - An unreadable control store is "could not look" and must fail closed (nothing launches) with a named error.
  - "No act on file" is empty. A counter at 0 is zero. A run that died is failed or void, never zero.
- **An operational item is done only when it is running.** A control verb is done when the live tick (dispatch tree) honours it on its next pass, measured by a `--live` promise, not when its selftest passes in a clone.
- **Nothing frozen is an excuse** (owner, 10:30). An append-only store is overridden by a later act that every reader honours. "It is a write-only ledger" is never an answer.

### 1.3 What success looks like, and how it is measured
| Measure | Today [measured] | Target | How measured |
|---|---|---|---|
| Tool calls to stop one mod from launching | ~15 (00-problem) | 1 | count in a Conductor transcript; a selftest that the one verb blocks every launch path |
| Act to effect on the live tick | ~22 min (Graffiti hold) | <= 60 s (next tick), no publish in the path | `pipe off` timestamp vs the first `reading.json` that shows it, read in the dispatch tree |
| Output bytes per write act | n/a (file edits plus publish) | <= 300 B, <= 3 lines | the selftest asserts lines and bytes |
| Output per one-unit read | ~6 commands, ~16 KB, ~4.5k tokens [estimate bytes/3.5] | 1 command, <= 1.2 KB | `pipe show Graffiti \| wc -c` |
| Output per all-units read | `status` 6155 B, plus hold show 3082, releases 4875 | <= 2 KB, one screen | `pipe show \| wc -c` |
| Wall time per act | 0.0-3.7 s per read; writes take minutes | < 2 s writes, < 5 s forecast | the timing selftest |
| Launch paths that can bypass control | >= 6 known (section 2) | 0 | the bypass selftest over every `systemd-run` call site, plus the OS-level backstop probe |
| Counters a stopped run consumes | all of them (00-problem) | 0, with system faults counted on their own meter | the per-counter void selftest |
| Status that disagrees with the live tick | 1 seen today | 0 | `pipe show` prints the tree and the sha it read; a selftest runs status from a second clone |
| Forecast that differs from the next real tick | no forecast exists | 0 on fixtures, per launch path | the forecast-equals-tick selftest |

## 2. Survey of what exists

### 2.1 Every switch, hold, counter, verb and status
Where "repo" is written, the live value is the dispatch clone's copy, which follows origin only after a publish and a pull.

| Thing | Where | Covers | Misses |
|---|---|---|---|
| `enabled` | repo `maturation_dispatch.json` | every tick launch (tick returns early, :2803) | Dispatcher roles and chains, relentless, raw systemd-run; needs publish; all or nothing |
| `blind_enabled` / `ingame_enabled` / `steward_enabled` | repo `maturation_dispatch.json` | one launch class in the tick (:1519, :1624) | per mod; publish; other launchers |
| `advancing` list (order = launch priority) | repo `maturation_dispatch.json` | which mods the tick advances, and in what order | no edit verb; publish; one list doing two jobs (membership and order) |
| Owner hold | repo `mod_owner_hold.json`, `mod_owner_hold.py show/lift/allow-design` | tick advancing filter, autonomy seeding, role_launch, designer_cleanse | `detached_helper.launch` itself, red_dispatch, cert-rerun, relentless, stop_resume; publish (a test pinned its live contents until `b09f49ab64`); path relative to the clone, so status lies across clones |
| Journal hold line ("CONDUCTOR INTERVENED ... kind hold") | repo `design/concepts/<Mod>/journal.md` | `maturation.py gate` / advance | every launch (10:25 road-back builder launched through it) |
| Dispatcher PAUSE file | `doorbell.state_dir()/PAUSE` (shared state, env `RM_DISPATCHER_STATE`) | Dispatcher beat: roles, Designer chains | the maturation tick (grep: 0 reads) |
| Dispatcher account HOLD/SWITCH | dispatcher `state.json` | role launches whose rule lists `role_launch` (:514) | everything else |
| `timers_guard.py pause/hold` | `timers_held.json`, `systemctl stop` | timer-started units | runs already live; launches from inside live runs (chains, autonomy); manual launches |
| `relentless_owner_pause.json` | repo | Relentless pipeline only | the Maturation Pipeline |
| Stale-clone gate (`CLONE_STALE_MIN = 5`) | code | tick launches nothing while the dispatch clone is > 5 min behind | it is a hidden pause: it reads as an alarm, not a switch; nobody can set it |
| Stage ceiling (`stage_ceiling_usd` 100, about 25.0M weighted) plus `release` | repo json; `releases.jsonl` and `releases_used` in shared state | spend per stage visit | the verb wants `--stage --read-tokens N --tokens N --why`: two numbers copied from a status line; 4 mods are paused on it now |
| Per-run caps (`cap_usd` 15, blind 20, in-game 30, steward 8, fix 10) | repo json; `spend_watchdog` | one run's spend, enforced from outside | none worth listing |
| State counters: steward tries per state key, fixers, blind_auto, ingame_auto, launches, pilot_launches, holder_road_back, cert_rerun, road_back, stopped, cleared, convergence, klass_since | shared `dispatcher/maturation/state.json` | the tick's and autonomy's retry and visit allowances | no set, add or void verb; `clear <Mod>` wipes wholesale; a stopped run counts |
| Granted coverage look | repo `stage.json` `coverage_release_granted`; `coverage_judge.py release` | the one owner-granted judge look | a consumed look cannot be given back without a new grant and a publish |
| Refusal counters / alarms | shared `refusal_contract/counters.json`, `alarms.json` | advance-refusal families trip alarms; `maturation.py tag_new_since` reads them | reset only by hand edit [guess ~70%: no reset verb found] |
| Designer chain cap | code `role_launch.CHAIN_MAX_PER_DAY=8` plus `dispatcher_schedule.json` | Designer and DesignerCodex chains per day | no override; both Designer roles are `enabled: false` in the schedule today |
| Test Pilot streak ("3 non-pass in a row") | derived from ledger events | routing to `rimflow pilot` | no void; a killed run counts as non-pass [guess ~60%] |
| Hand acts | shared `hand_acts.jsonl`, `maturation_hands.py list` | recording what a person did | not linked to counters |
| Stage record / moves | repo `design/concepts/<Mod>/version/stage_record.json`; `maturation.py gate/advance` | stage, cycles visit/total, moves | publish |
| Run records | shared `dispatcher/detached/` (2042 files), `runs.json` | which unit ran which item | mod is inferred (`MN.gather`), not declared; no terminal class `void` |
| Ledger | repo `infrastructure/state/ledger/events/*.jsonl` | item history, owner words | taking effect via ledger waits on publish |
| Read verbs | `maturation_dispatch.py status` (6155 B), `maturation.py show` (1104 B) / `next` (1251 B), `mod_owner_hold.py show` (3082 B), `releases` (4875 B), `maturation_hands.py list` (507 B), `coverage_judge.py status` (90 B), dry `tick` (3.7 s, 4315 B), `cli.py show` (1.9 s, 2356 B), `systemctl list-timers` (9603 B) | parts of the picture | no single "why is X (not) running"; each reads its own clone's repo files [measured: `acts\*.out`] |
| Publish door `./publish` | bench and pool clones | lands repo-held controls | blocks a control act on any unrelated red test; tens of seconds to minutes |

### 2.2 Launch paths (what can start work on a mod with no one typing)
| Path | Primitive | Hold read? | `enabled` read? |
|---|---|---|---|
| Tick: build / blind / in-game / steward / fixer / chains / repin | `maturation.launch_mod`, autonomy `launch_brief` -> `detached_helper.launch` | via the advancing filter only | yes |
| Road-back builder (10:25 today) | tick to `detached_helper.launch` | yes once published; the journal hold is not read | yes |
| Pilot holders | tick | via advancing [guess ~70%] | yes |
| Cert rerun | raw `systemd-run` (`maturation_dispatch.py:1149`) | [unmeasured] | inside the tick, yes |
| Red dispatch | `detached_helper.launch` | no (0 refs) | yes |
| Dispatcher roles (Designer, DesignerCodex chains, Operations, Auditor, Arbiter) | `role_launch.launch` (rm-role-*) | yes | no (it has its own PAUSE) |
| Designer cleanse fleet | raw `systemd-run` (`designer_cleanse.py:2029`) | yes for builds | no |
| Relentless work units | `relentless.*` (rm-relentless-work-*) | `relentless_owner_pause.json` only | no |
| stop_resume / x-resume | `detached_helper.launch` | no | no |
| Coverage judge (rm-coverage-judge-*) | `coverage_judge.py` launch | through the grant | no |

The launch-path census owed by RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED supersedes this table when it lands. The "[unmeasured]" and "[guess]" cells are its first rows to measure.

### 2.3 Relevant skills
- `using-rimflow`: ledger and item verbs, provenance flags.
- `rimflow-operations`: `timers_guard pause`, the account HOLD.
- `relentless-pipeline`: the Relentless side and its pause.
- `clone-landing-commits`: why repo-held controls wait on publish and pull.
- `deciding-and-superseding`: retiring the journal hold as a control, without a stale doc still telling agents to use it.
- `mutate-your-checker`: the bypass selftest must be shown red on a mutant launcher.
- `resumable-batch-jobs`: run ledger with terminal classes.

### 2.4 Off-the-shelf tools and patterns
- **systemd.**
  - Hyphen-prefix drop-ins: `~/.config/systemd/user/rm-detached-.service.d/*.conf` applies to every `rm-detached-*.service`. This needs systemd >= 246; the host runs systemd 259 [measured: `systemctl --version`].
  - `ExecCondition=` skips a unit start cleanly when a command exits 1-254.
  - Slices (`--slice=rm-runs.slice`) group every run, so `systemctl --user stop rm-runs.slice` stops all live runs. `systemctl --user freeze` suspends a cgroup.
  - `systemd-run --property` sets per-unit properties.
  - Whether prefix drop-ins apply to transient `systemd-run` units is [unmeasured]. I believe yes [guess ~75%]. Probe (harmless, touches no pipeline state; the Conductor runs it, not this design pass): `mkdir -p ~/.config/systemd/user/rm-probe-.service.d && printf '[Service]\nExecCondition=/bin/false\n' > ~/.config/systemd/user/rm-probe-.service.d/x.conf && systemctl --user daemon-reload && systemd-run --user --unit rm-probe-a /bin/true; systemctl --user show rm-probe-a -p Result,ExecMainStatus`
- **One SQLite state store.**
  - Gives transactions and SQL views (`consumed = charged - voided + adjust`).
  - It is unsafe on the drvfs `/mnt/d` mount, where file locking is unreliable [assumed, widely reported for SQLite over 9p/drvfs]. It would have to live on ext4 (`~/.local/state`), which is out of sight of the Windows side.
- **Feature flags / kill switches** (in the style of LaunchDarkly or Unleash): one flag store read by every code path, with a default, a fail-closed rule and an audit log. The pattern is exactly the "on/off for mod, item, stage, role, path" need. The libraries themselves are overkill.
- **Job-queue libraries** (Celery, RQ, Sidekiq-style). Two patterns transfer: queue pause and resume, and dead-letter or retry without charging. The libraries do not, because a run here is a systemd unit, not a worker task.
- **Event sourcing with compensating events.**
  - The ledger already is an event log.
  - A void, undo, give-back or exception is a later event, and every reader folds over it.
  - This directly answers "never tell me it's a write-only ledger".
- **kubectl-style declarative reconcile.**
  - Desired state in one document; a reconciler acts on the diff; `diff` / `apply --dry-run` is the forecast.
  - Admission controllers in Kubernetes are the model for one gate that every create passes.

## 3. Solutions

Five options. A is the cheapest. B and E remove the structural causes. C changes the tick's model. D is an OS-level layer that can sit under any of them.

### Option A: a thin front door over the stores that exist
- **How it works.**
  - `./pipe <verb>` translates each act into a write to the store that already owns that thing:
    - on/off for a mod: the owner hold JSON, then auto-publish and wait for the dispatch pull
    - pause all: the Dispatcher PAUSE file plus a new `paused` key in the maturation `state.json`
    - counters: an edit of the matching `state.json` dict under `state.lock`
    - a look: the `stage.json` grant, then auto-publish
    - queue: a rewrite of `advancing`, then auto-publish
  - `show` concatenates the existing read verbs, trimmed.
- **Build effort.** About one builder day [guess ~60%]. Each verb is a small adapter.
- **Token and latency cost per act.** One call and ~3 lines. But every repo-held act still waits for publish and pull: 1-25 minutes, and the tests may refuse it [measured today: 22 min].
- **Upkeep.**
  - High. Each new counter or launcher needs a new adapter.
  - Undo needs a hand-written inverse for each store.
  - The void semantics must be known per counter.
- **Risks and failure modes.**
  - Launch paths that read none of the stores stay open (`detached_helper.launch`, red_dispatch, cert-rerun, relentless). Bypass count is unchanged at 6 or more.
  - Status still reads the local clone.
  - The auto-publish adds a new route to a red door.
  - A pause in `state.json` is overwritten by the tick's own state save unless it is locked correctly.
- **What it buys.** One-line habits today. No change to readers.
- **When it dominates.** When the next hour matters more than the next month, and the launch-path count is small and fixed. Neither is true here.

### Option B: one control store, admission at the launch primitives, and a control journal of compensating acts (removes causes 1 to 3)
- **Store.**
  - `D:\ClaudeWork\rimmandrake\control\` (`/mnt/d/ClaudeWork/rimmandrake/control/`, env `RM_CONTROL_DIR` for tests), in shared state and in no clone.
  - It holds `acts.jsonl`: append-only, one JSON line per act, written under `flock`. Each line carries id, who, at (UTC and Pacific), why, owner-said, kind, scope, before, after, and undo-of.
  - `view.json` is the fold of all acts, rewritten atomically after each act together with the hash of `acts.jsonl` it was folded from. A reader whose hash does not match refolds.
- **One reader: `control.view()`.**
  - It returns switches with until, why and who; counter adjustments; voids; grants; ceilings; queue order; and acks.
  - An unreadable or corrupt store raises `control.Unreadable`. Every gate treats that as everything OFF, and `pipe show` prints `CONTROL UNREADABLE: <cause>` [fail closed; "could not look", not "empty"].
- **Admission: `control.admit(spec)`.**
  - `spec` is the run declaration: mod, item, path, stage, role, model and cap.
  - It is called inside the three launch primitives: `detached_helper.launch`, `role_launch.launch`, and one new `launch_unit()` that the raw `systemd-run` pipeline call sites (cert-rerun, designer_cleanse, relentless work) are moved onto.
  - A refusal returns `REFUSED by control: off <scope> (<why>, <who>, until <t>)`. It is recorded as an admission refusal: nothing is consumed, and no failed-launch alarm fires.
  - The callers' own partial checks stay as early-outs, so the tick does not plan what admit would refuse. The primitive is the guarantee.
- **Run ledger.**
  - Every admitted launch writes `runs.jsonl`: run id = unit name, plus the declared mod, item, path and stage. Spend and "live on mod" then come from the declaration, not from inference.
  - At the end the run gets a terminal class: `ok`, `nonpass` (the mod's merit), `fail_system` (signal or stop, launch failure, no result file, account or harness fault, timeout), `void_hand` (a person voided it) or `void_system` (the pipeline classed it).
- **Counters.**
  - Every counter reader returns `control.adjust(mod, counter, raw)`: raw minus voided runs' charges plus set/add acts.
  - Phase 2 derives the raw counts from `runs.jsonl` too, so the scattered `state.json` dicts become caches.
  - System faults count on their own meter, `system_faults(mod)`, with its own alarm, so an endless relaunch loop is still caught without spending a trial.
- **Verbs.** One front door, `./pipe` (also `rimflow pipe`). Every write prints at most 3 lines: before -> after, act id, and the undo command. `--why` is required.
- **Mirror.**
  - A belt copies `acts.jsonl` into the repo, next to the ledger, for the record.
  - Effect never waits on it. Repo files (hold JSON, `enabled`, `advancing`, the stage.json grant) become defaults that the store overrides.
  - The owner's published hold list stays as his durable record.
- **Forecast.** `pipe next [30m]` imports the tick's own `decide`, `AUT.resolve`, `prioritise` and admit from the dispatch tree. That path is read from the systemd unit's WorkingDirectory, so the forecast runs the code that will actually run. It is a dry pass with a simulated clock.
- **Build effort.**
  - First slice in about an hour (section 4).
  - The whole design is about 3-4 builder days [guess ~50%]. The bulk is moving every counter reader onto `adjust()` and moving the raw systemd-run sites onto `launch_unit()`.
- **Cost per act.**
  - One call. Writes take < 0.5 s: append, fold and write. The fold is linear in acts, and acts are few (tens a day) [guess ~80%].
  - `show` takes < 1 s and reads `view.json` plus the live `reading.json`.
  - The effect lands on the next tick, <= 60 s, or at once at admission for a path outside the tick.
- **Upkeep.**
  - Low and checkable. A new counter must be registered in `control.COUNTERS`.
  - A selftest enumerates the counter readers and the `systemd-run` call sites. It fails on any reader that does not call `adjust()` and on any pipeline launch that does not pass `admit()`. A mutant launcher must turn it red.
- **Risks and failure modes.**
  - A primitive missed in the census: closed by the bypass selftest plus Option D's backstop.
  - Fail-closed outages: a corrupt `acts.jsonl` stops the whole pipeline. That is intended; the loud error names the line, and `pipe repair` drops a torn last line.
  - Drvfs `flock` reliability on `/mnt/d` [guess ~85% fine, since the existing dispatcher `tick.lock` and `state.lock` live there].
  - Fold drift between clones running different code versions. The view schema is versioned, and an older reader that meets a newer kind refuses (fail closed), never ignores it.
  - Concurrent builders on the same primitives: section 4 redirects.
- **What it buys.**
  - One place to look, one place to write, immediate effect, and launch bypass of 0 by construction and by test.
  - Void and undo become "a later line", which answers his 10:30 words in the data model itself.
  - Status cannot lie across clones, because it reads shared state plus the live tick's own reading.
- **When it dominates.** Whenever there is more than one launcher and more than one store. Here there are 10 launch paths and about 20 stores.

### Option C: declarative desired state, reconciled by the tick (kubectl style)
- **How it works.**
  - One document, `control/desired.json`, in shared state. It holds pipeline on/off; per mod on/off, until and why; the queue as an ordered list; per-mod allowances ("looks: 1 remaining", "blind cycles this visit: 3"); ceilings; and per-path and per-role switches.
  - Verbs are `pipe edit`, `pipe set <path> <value>`, `pipe diff` and `pipe apply`.
  - The tick becomes a reconciler. Each tick computes observed minus desired and launches only what closes the gap. `next` is `diff` projected forward on a clock.
  - The repo holds a copy of `desired.json` for review. As in B, the live copy is in shared state.
- **Build effort.** About 4-6 builder days [guess ~40%]. The tick's decision code (about 3000 lines in `maturation_dispatch.py` plus 1570 in autonomy [measured: wc]) was written as "decide from state", not "close a gap". Rewriting it is the largest risk on this list.
- **Cost per act.** One call. `set` prints the diff (2-3 lines). Effect lands on the next tick.
- **Upkeep.** Low for switches and queue. Allowances are awkward: "remaining looks" is history (charges and voids), not desired state. Either C keeps a separate event log for consumption, which turns it into B plus C, or it rewrites "remaining" by hand after every run, which loses the audit trail.
- **Risks.**
  - The rewrite touches every launch decision in one move.
  - Desired state does not by itself gate launchers outside the tick (Dispatcher roles, relentless). It needs B's admission anyway.
  - Desired-state edits by two agents race. That needs resourceVersion-style compare-and-set.
- **What it buys.**
  - The cleanest forecast (a dry reconcile) and the cleanest queue editing.
  - A state that can be reproduced from one file, and a readable diff of intent.
- **When it dominates.** When most acts are "make it so" (on/off, order, ceilings), there are few launchers, and they can all be made to reconcile. It loses on void and give-back, which are about past runs.

### Option D: OS-level kill switch and backstop (systemd prefix drop-ins plus a run slice)
- **How it works.**
  - Hyphen-prefix drop-ins for every pipeline run prefix: `rm-detached-`, `rm-role-`, `rm-coverage-judge-`, `rm-cert-rerun-`, `rm-relentless-work-`, `rm-judge`, `rm-builder`, `rm-testpilot`, `rm-consult` [measured: the unit-name census of the launch code].
  - Each drop-in carries `ExecCondition=/usr/bin/python3 -I <shared>/control/gate.py %n`. `gate.py` reads one file, `control/PAUSE` or `view.json`, and exits 1 when the unit's scope is off.
  - Runs are launched into `rm-runs.slice`, so `pipe stop all` is `systemctl --user stop rm-runs.slice`.
  - `timers_guard pause --all` stays for the timers.
- **Build effort.** About 2-4 hours, including a probe that drop-ins apply to transient units (section 2.4, [unmeasured]).
- **Cost per act.** One call. The effect is immediate for every new unit start, whatever code path made it.
- **Upkeep.** A new unit prefix must get a drop-in. A selftest compares the prefix list with the census of unit names.
- **Risks and failure modes.**
  - **The launcher thinks it launched.** With `systemd-run` (no `--wait`), a start skipped by `ExecCondition` still returns 0. The caller records a launch, may charge a counter, and later sees a run with no result. D alone therefore spends trials, which is exactly what he forbids. It must sit under B's admission, where a skip is a backstop catch and is auto-classed `void_system` by the run ledger.
  - The scope is coarse. Unit names carry the item slug, not the mod (`rm-detached-bench-rimmandrake-settle-tribute-rival-band-ne-...`), so per-mod off needs `gate.py` to look the run up in `runs.jsonl`. That is B again.
  - Freezing a slice stalls API calls mid-request, and agents may time out and fail. Use stop, not freeze.
- **What it buys.** A guarantee independent of every Python path: "launch paths that bypass control = 0" holds even for code nobody has read yet.
- **When it dominates.** As a backstop under any option. As the only mechanism, never: it cannot do counters, queue or void.

### Option E: one SQLite pipeline database for all state
- **How it works.**
  - Migrate the maturation `state.json`, the counters, `releases.jsonl`, the run records, the hold, the grants and the controls into `~/.local/state/rm/pipeline.db` (ext4, not drvfs).
  - It has tables `runs`, `charges`, `acts` and `switches`, and views `consumed`, `remaining`, `why_not_running`.
  - Every reader and writer goes through one module with transactions. `pipe` is a thin SQL front.
- **Build effort.** About 2-3 builder weeks [guess ~40%]. Every reader of `state.json` (tick, autonomy, hands, status, page) is rewritten, plus a migration and a Windows-side export for anything read from `D:\`.
- **Cost per act.** One call, sub-second.
- **Upkeep.** Lowest in the long run: one schema, and constraints enforced by the database.
- **Risks.**
  - A big-bang migration of a live pipeline.
  - drvfs locking forces ext4, so the Windows side and the other machines (Mac, SteveDesktop) see only exports.
  - It conflicts with every in-flight builder, and the selftest fixtures must all move.
- **What it buys.** It fully removes the many-stores cause, not only for controls.
- **When it dominates.** When the store count keeps growing after B, or when cross-store queries become a daily need. That is a later decision. B's `acts.jsonl` and `runs.jsonl` are shaped so they can become E's `acts` and `runs` tables without a rewrite.

### 3.6 Comparison
| | A thin door | B store + admission + journal | C declarative | D OS backstop | E SQLite |
|---|---|---|---|---|---|
| Removes the store-in-the-tree cause | no | yes | yes | n/a | yes |
| Removes the admission-in-callers cause | no | yes | partly | yes (coarse) | needs B's admit |
| Void and give-back as data | per-store hacks | native | awkward | no | native |
| Calls per act | 1 | 1 | 1 | 1 | 1 |
| Act to effect | minutes (publish) | <= 60 s | <= 60 s | immediate | <= 60 s |
| Bypass paths left | >= 6 | 0 by test (+D) | >= 3 outside the tick | 0 for new starts | 0 with admit |
| Build | ~1 day | ~1 h first slice, ~3-4 days | ~4-6 days | ~3 h | ~2-3 weeks |

### 3.7 Interaction inventory: every owner need as a one-liner (Option B's front door; D underneath)
Every write takes `--why "..."`, and `--owner-said "..."` when they are his words. Every write prints at most 3 lines: before -> after, the act id, and the undo command.

**Reading**

| Need | Command |
|---|---|
| One unit: stage, on/off, live run, every allowance used/limit, spend vs ceiling, next action and its blocker | `pipe show Graffiti` |
| All units, one screen | `pipe show` |
| Why X is or is not running | `pipe why Graffiti` (the admission and decision chain, one line per gate) |
| What will start in 30 min if nobody acts | `pipe next 30m` |
| What controls are in force, and history | `pipe log -n 20`, `pipe log Graffiti` |

**Pause and switches**

| Need | Command |
|---|---|
| Pause all, live runs finish | `pipe off all --why "..." [--until "tomorrow 09:00"\|--until-release]` |
| Pause all and stop live runs (voided) | `pipe off all --stop-live --why "..."` |
| Resume | `pipe on all --why "..."` |
| One mod off / on | `pipe off Graffiti --until "2026-11-19 09:00" --owner-said "..."` / `pipe on Graffiti --why` |
| One item, stage, role or launch path off | `pipe off item:RIMMANDRAKE_X`, `pipe off stage:blind`, `pipe off role:Designer`, `pipe off path:red_dispatch` |

**Queue and stages**

| Need | Command |
|---|---|
| Queue: list, top, bottom, move, drop, add | `pipe queue`, `pipe queue top Graffiti`, `pipe queue move FlowWorks 2`, `pipe queue drop Contagion`, `pipe queue add Cauldron` |
| Stage move by hand / re-pin | `pipe stage Graffiti in_game --why` / `pipe repin Graffiti --why` (each calls the existing `maturation.py` verb, recorded as an act) |
| Hand-act record | `pipe hand Graffiti "walked it in game: pass" --owner-said "..."` |

**Allowances and spend**

| Need | Command |
|---|---|
| Give an allowance back or make an exception | `pipe add Graffiti look +1 --why`, `pipe set Graffiti blind_cycles 0`, `pipe reset Graffiti steward` |
| Void a run (counts nothing, restores what it used) | `pipe void rm-detached-...-1795024763 --why "..."`, `pipe void Graffiti --since 09:59 --why` |
| Undo any act | `pipe undo A-0042 --why "..."` |
| Release spend past the ceiling (reads the spend itself) | `pipe release Graffiti +5M --why` |
| Change a ceiling | `pipe ceiling Graffiti 30M --why` |

**Runs and alarms**

| Need | Command |
|---|---|
| Launch one run now, through admission | `pipe launch Graffiti --why` |
| Stop a live run (void by default) | `pipe stop Graffiti --why`, `pipe stop rm-detached-... --charge` to count it |
| Ack an alarm or incident | `pipe ack OPS_MATURATION_MOD_PAUSED --why` |

**Vocabulary.**
- A switched-off thing reads `OFF (<why>, <who>, until <t>)`. It never reads PAUSED, because PAUSED already means "past the ceiling" and "steward tries exhausted", and fixers still launch under it.
- `pipe show` prints one column per meaning: `off`, `ceiling`, `exhausted`, `coverage-stopped`, `stale-clone`.

## 4. Recommendation, build order, in-flight builders

### 4.1 The pick: B (one control store, admission inside the launch primitives, a journal of compensating acts), with D as a backstop underneath and C's idea used only for the queue
The queue is a desired ordered list in the store, and it overrides `advancing` order.

**Defence.**
- **Remove the causes.** B is the only option that removes both causes found in section 1.1 without a big-bang rewrite:
  - Control state leaves the code tree: no publish and no clone pull stand between an act and its effect.
  - Admission moves from 10 callers into 3 primitives: no paths x switches matrix.
  - Void and undo are data, not per-store hacks. His 10:30 rule becomes structural: an act is a later line that every reader folds.
- **Status cannot lie across clones.** `pipe show` reads shared state and the live tick's `reading.json`, and prints which tree and sha it read.
- **It is incremental.** The first slice is useful within the hour. Each later slice moves one more family of readers onto `adjust()` or one more launcher onto `admit()`. Nothing breaks while half-migrated, because the callers' own checks stay as early-outs.
- **It satisfies the constraints.**
  - Weighted tokens: 1 call, at most 3 lines.
  - Fail-closed on "could not look".
  - The pipeline's own `void_system` classing means it fixes its own charge errors.
  - The `--live` promise is "the dispatch tick honoured `pipe off X` within 60 s".
- **C is rejected as the core.** Consumption is history, not desired state. A reconciler rewrite of about 4600 lines of decision code is the highest-risk item on the list.
- **E is deferred, not rejected.** `acts.jsonl` and `runs.jsonl` are E's first two tables.
- **D is added** because the bypass selftest proves only the paths it can see. D covers paths nobody has read, at the price of a probe and about 3 hours.

**What would change my mind.**
- The probe in section 2.4 shows prefix drop-ins do not reach transient `systemd-run` units. Then D becomes a `systemd-run` shim earlier on the pipeline's PATH, or is dropped, and the bypass selftest carries the guarantee alone.
- `flock` on `/mnt/d` proves unreliable under the tick plus three writers. Then the store moves to ext4 (`~/.local/state/rm/control/`), and a Windows-readable copy is written after each act.
- The launch-path census finds more than about 3 launchers that cannot be moved onto `launch_unit()`. Then D becomes the primary gate and B keeps counters and queue only.
- The owner wants a hand-editable, diffable intent file as his interface. Then C's `desired.json` goes on top of B's store for switches and queue only.
- Graffiti's numbers show a void-spend loop risk larger than the per-run cap bounds. Then the system-fault meter gets a spend ceiling of its own before slice 2 lands.

### 4.2 Build order (each slice lands on its own; code passes `./publish` once per slice; acts never do)
1. **Slice 1, within about an hour: the switch that would have stopped 10:25.**
   - `rimflow/control.py`: `acts.jsonl` plus fold, `view()`, `Unreadable`, and `admit(spec)` for scopes `all` and `<Mod>`.
   - `./pipe` with `show`, `off`, `on`, `log` and `undo`.
   - `admit()` is called at the top of `detached_helper.launch` and `role_launch.launch`. The tick filters `advancing` by `view()` at the same spot as the owner-hold filter (`maturation_dispatch.py:2796`), so it plans nothing for an off mod.
   - `pipe show` prints one line per mod from the live `reading.json` plus the view, plus the dispatch tree's sha and its behind-minutes. The stale-clone gate is shown as an implicit OFF.
   - Selftests watched failing on base:
     - `off all` makes both primitives refuse and charges nothing
     - `off Graffiti` makes a tick fixture launch nothing for Graffiti
     - a corrupt `acts.jsonl` makes them refuse, with the line number
     - undo restores the earlier state
     - at most 3 lines and < 2 s
     - no selftest may open the real control dir (the guard that the `b09f49ab64` lesson needed)
   - Live proof, run by the Conductor: `pipe off Graffiti --owner-said "..."`, then the next `reading.json` in the dispatch tree shows it.
2. **Slice 2: void and allowances.**
   - Admission writes a declared run record (`runs.jsonl`). Runs get terminal classes, with automatic `void_system`.
   - `control.adjust()` goes into each counter reader: granted look, blind_auto, ingame_auto, steward tries, holder_road_back, launches/launch_failed, pilot streak, refusal families, chain cap.
   - New verbs: `pipe void`, `unvoid`, `add`, `set`, `reset`. A system-fault meter with its own alarm.
   - Live proof: the Conductor voids Graffiti's three runs, and the pipeline's own readers read as before 9:59.
3. **Slice 3: bypass = 0.**
   - `launch_unit()` for the raw `systemd-run` pipeline sites (cert-rerun, designer_cleanse, relentless work).
   - The bypass selftest over every `systemd-run` call site, with an allowlist for non-pipeline units (mirror, scratch-reap, telemetry), and a mutant launcher shown red.
   - After the probe: the D drop-ins plus `rm-runs.slice`, and `pipe stop`.
4. **Slice 4: forecast.**
   - `pipe next [30m]` and `pipe why <Mod>` import the decision functions from the tick unit's WorkingDirectory, with a simulated clock.
   - The forecast-equals-next-tick selftest runs per launch path in the census, and a mutant that drops a path must fail.
5. **Slice 5: the rest of the inventory.**
   - `queue` verbs (an order list in the view overriding `advancing`).
   - `release <Mod> +N` reads the stage spend itself.
   - `ceiling`, `ack`, `hand`, `stage`, `repin`, `launch`, `stop --charge`.
6. **Slice 6: record and retirement.**
   - A belt mirrors `acts.jsonl` into the repo.
   - The Dispatcher PAUSE file is either written by the fold or read through `view()`: one switch, not two.
   - The journal hold line is retired as a control. `pipe off` writes the journal line as a record; follow `deciding-and-superseding` for every doc that tells agents to use it.
   - Docs: a 15-line section in `roles/conductor.md`, his words in `standing_rulings.md`, one CLAUDE.md pointer.
7. **Slice 7.** `pipe show` on the status page. Then decide on E, with evidence of how many stores remain.

### 4.3 In-flight builders (all three live at 10:44 as detached units [measured: `systemctl --user list-units`])
Whether a running detached builder reads a `rimflow note` mid-run is [unmeasured]. Each redirect below is therefore "note now; if its first landing shows it did not read the note, stop it and relaunch with the corrected brief".

- **Control builder: RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS (`...-1795026987`). Verdict: CONTINUE, re-brief by note.**
  - Its brief is already close to B: one store in shared state, one reader, fail closed, log and undo, no publish in the path.
  - Corrections it needs:
    1. The tick unit runs from `/home/mandrake/rm/dispatch`, not bench, as its brief assumes. `show` must read the live `reading.json` and print the tree.
    2. Admission goes inside the launch primitives. "Every reader calls one function" alone repeats today's matrix.
    3. It owns the act kinds `void`, `off all` and the forecast's admission input, so neither sibling builds a store.
    4. Its first landing is slice 1 exactly.
  - Cost: about zero if the note is read. Otherwise up to its USD 15 cap, of which [guess ~10-15 min] of work would be lost.
- **Pause builder: RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED (`...-1795026712`). Verdict: RE-BRIEF, to the census and the forecast only.**
  - Keep: the launch-path census (it fills section 2.2's unmeasured cells and feeds slice 3's bypass test); `next` through the real decision code with a simulated clock, with the forecast-equals-tick selftest (slice 4); and its evidence-based ruling on the journal hold.
  - Drop: its own pause file and the `maturation_dispatch.py pause|resume` verbs. These would be a second control store. A `pause` alias may exist only as a call that writes a control act. "Unreadable means PAUSED" becomes `control.Unreadable`.
  - Cost: any pause-file code already written is discarded [guess <= 30 min of work]. If it has already landed one, the control builder folds it into an act kind, as a one-time migration.
- **Void builder: RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT (`...-1795026704`). Verdict: CONTINUE, with a re-brief on where the verb writes.**
  - Keep: step 1 (landed `b09f49ab64`); the counters census; automatic `void_system` classing, which becomes the run ledger's terminal class; the system-fault counter; the Graffiti before/after proof; and the ceiling proposal.
  - Change: `void` and `unvoid` write a void act through the control store's function, and each counter reader honours it through `control.adjust(mod, counter, raw)`. They must not write a void record private to `maturation_dispatch.py`.
  - Split the files to avoid collisions: the void builder owns the counter readers, and the control builder owns the store and admission. Until `control.py` lands, both code against the agreed signatures `control.record_act(kind, scope, why, owner_said=None)` and `control.adjust(mod, counter, raw)`.
  - Cost: coordination only. Without the split, publish replay conflicts are likely, because all three edit `maturation_dispatch.py` [guess ~60%].

## 5. Open decisions for the owner
1. **Does a void run's spend count toward the stage ceiling?**
   - Spend already burnt stays measured; that is true.
   - Proposal: a void run's spend is shown as void spend and is not charged to the stage ceiling. It is bounded per run by the run caps and in total by the system-fault meter's own alarm.
   - Graffiti's three runs' numbers are owed by the void builder; this pass did not measure them.
2. **What does `off` do to a live run by default?**
   - Proposal: no new starts; live runs finish; `--stop-live` stops them and voids them.
   - The other choice is stop-by-default, which is what he did by hand today.
3. **Which acts need his words?**
   - Proposal: granting a look, raising a ceiling, lifting his own hold, and voiding a run that failed on the mod's merits all need `--owner-said`.
   - Pause, resume, queue moves, voiding system-caused failures, and acks are the Conductor's, with `--why`.
4. **Where does his owner hold live?**
   - Proposal: the shared control store is the truth that takes effect within 60 s. `mod_owner_hold.json` stays as the published record, and as the default on a fresh store, mirrored from the acts.
   - The other choice is to keep the published JSON as the truth, and accept publish latency on every hold.

## 6. Claims table
STAR (*) = the recommendation would change if this were wrong.

| # | Claim | Status | How |
|---|---|---|---|
| 1* | The live tick runs code and config from `/home/mandrake/rm/dispatch` | measured | `systemctl --user cat rm-maturation-dispatch.service`: WorkingDirectory and ExecStart |
| 2* | `detached_helper.launch` reads no hold, pause or `enabled` | measured | grep: 0 references in `detached_helper.py` |
| 3* | About 10 launch paths, through 3 primitive kinds (DH.launch, role_launch.launch, raw systemd-run) | estimated | grep of call sites; 29 non-selftest files call systemd-run; how many are pipeline launches is unmeasured (pause census owed) |
| 4* | The owner hold took about 22 min from edit to live effect, with publish in the path | measured | bench edit ~10:20 (Conductor); `b09f49ab64` at 10:38-10:39; reading.json owner_hold at ~10:42 |
| 5 | `status` in bench showed HELD while the live tick did not hold Graffiti | measured | bench status vs the dispatch reading at 10:39 (decision "live", owner []) |
| 6* | The maturation tick does not read the Dispatcher PAUSE file | measured | grep of the maturation_* modules |
| 7 | The journal hold blocks advance, not launch | measured | `maturation.py gate --to in_game` refused rc=1; road-back launch at 10:25 (void.md, the Conductor's measurement) |
| 8 | Stopping one mod took ~15 calls | measured by the Conductor | 00-problem.md; not re-counted here |
| 9 | Read acts: status 6155 B, show 1104, next 1251, hold show 3082, releases 4875, hands 507, coverage status 90, dry tick 3.7 s / 4315 B, `cli.py show` 1.9 s / 2356 B, list-timers 9603 B | measured | `design_pcs\acts\*.out`, wc and time |
| 10 | Reading one unit fully takes about 6 commands and 16 KB (~4.5k tokens) | estimated | sum of 9; tokens = bytes / 3.5 |
| 11 | Call count dominates the weighted-token bill of control acts | guess ~70% | each call re-sends the context; cache weighting not measured here |
| 12* | Prefix drop-ins apply to transient `systemd-run` units | unmeasured (guess ~75%) | probe command in section 2.4; affects D only |
| 13 | systemd 259 supports prefix drop-ins (>= 246) | measured (version) / assumed (feature date) | `systemctl --version` |
| 14 | A start skipped by `ExecCondition` still returns 0 to a non-waiting `systemd-run` | guess ~80% | systemd semantics; the reason D cannot stand alone |
| 15* | `flock` is reliable enough on `/mnt/d` for the control store | guess ~85% | `tick.lock` and `state.lock` already live there; not stress-tested |
| 16 | Folding acts takes < 0.5 s at the expected volume (tens a day) | guess ~80% | not built |
| 17* | Slice 1 is buildable within about an hour | guess ~60% | 2 call sites plus 1 filter plus a small module; the risk is publish-door conflicts with three live builders |
| 18 | Build effort: A ~1 day, B ~3-4 days, C ~4-6 days, D ~3 h, E ~2-3 weeks | guess ~40-60% | sizes of the affected modules (wc: dispatch 3063, autonomy 1570, DH 1401, role_launch 3563 lines) |
| 19 | 4 of 6 advancing mods are paused on the ceiling (GSS ~41.0M, Pyrelands 38.4M, EK 34.1M, FlowWorks 20.1M plus a 5M cap, against ~25.0M) | measured | `acts\disp_status.out` |
| 20 | Fixers launch on a mod shown PAUSED | measured (code) | `maturation_autonomy.py` docstrings, RUN_FIX_TICKETS_WHILE_PAUSED |
| 21 | Unit names carry the item slug, not the mod | measured | running unit names at 10:44 |
| 22* | All three in-flight builders are live as detached units | measured | `systemctl --user list-units` at 10:44 (`...1795026712`, `...1795026704`, `...1795026987`) |
| 23 | A detached builder reads a `rimflow note` mid-run | unmeasured | decides whether a redirect costs a note or a relaunch |
| 24 | The dry `tick` writes no state | measured | `state.json` mtime unchanged |
| 25 | The dispatch clone follows a publish within ~3 min | measured once | 10:39 publish, 10:42 reading |
| 26 | SQLite is unsafe on drvfs | assumed | widely reported; not tested here |
| 27 | Refusal counters have no reset verb | guess ~70% | grep found none; not exhaustive |
