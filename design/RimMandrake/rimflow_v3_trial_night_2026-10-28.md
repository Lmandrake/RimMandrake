# RimFlow v3 trial night, 2026-10-28: one ordered runbook

**Owner's word (2026-10-28 ~17:20 PDT):** "Please build all the components of the v3 system at this time. This is disturbing. I need to know we can proceed with a real trial tonight."

**Order (his):**
1. He reaches the hotel and says **go**.
2. Account switch.
3. Cutover (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY).
4. Enable the whole system.

**Who runs it.** The Conductor (the window tiled `AGENT BENCH`) runs every command here. The owner reads the bold lines on his phone and answers only the **[MANDRAKE]** ones.

**One read-only checker answers "can we go?" at every gate:**

```
python3 src/RimMandrake/rimflow/v3_ready.py                 # GO / NO-GO / UNMEASURED table; exit 0 / 1 / 2
python3 src/RimMandrake/rimflow/v3_ready.py --expect-account <name>   # after the switch
python3 src/RimMandrake/rimflow/v3_ready.py --no-selftests  # fast (~5 s) re-look; selftest rows read UNMEASURED
```

UNMEASURED is never a pass. A row reads UNMEASURED when the checker could not tell, and it blocks until someone looks. WARN and INFO never block.

Save every run as `D:\ClaudeWork\rimmandrake\v3_trial\ready_<HHMM>.txt`, i.e. `> /mnt/d/ClaudeWork/rimmandrake/v3_trial/ready_$(date +%H%M).txt`. That makes the night's evidence a file series.

**Paths used below:**
- `$B=/home/mandrake/rm/bench`
- `$S=/mnt/d/ClaudeWork/rimmandrake/dispatcher`
- `$O=/mnt/d/ClaudeWork/rimmandrake/ops_watch`
- `$T=/mnt/d/ClaudeWork/rimmandrake/v3_trial`. Run `mkdir -p $T` first.

All commands run from `$B`.

**Log of the night:** `$T/night.md`. Write one line per step: the time, the step number, and what proved it. The account switch closes this window, so this file is how the relaunched Conductor knows where it is. **Read it first after the relaunch.**

**`[OWED: <helper>]` marks** a line that a building helper had not delivered when this was written (17:40 PDT). Fill it from that helper's progress file under `D:\ClaudeWork\rimmandrake\v3_build\` before the step runs. If it is still owed at the step, the step does not run. Say so in night.md.

---

## 0. State at writing (v3_ready, 2026-10-29T00:20Z = 17:20 PDT; `D:\ClaudeWork\rimmandrake\v3_build\ready_pre.txt`)

**Already GO:**
- Dispatcher live (`tick --apply`), ticking, timer active, no PAUSE.
- Deadman reports all arms alive.
- FOUNDRY doorbell hook installed and armed.
- FOUNDRY window live.
- All six role instruction files present.
- Goals file on origin/main.
- HOLD present, account-plan.timer off.
- FOUNDRY shard published 101 min ago.
- Operations' one real run: 285,538 / 450,000 tokens.

**Blocking at writing:**

| Row | State | Who clears it |
|---|---|---|
| Dispatcher / selftests | Cleared 18:5x: `selftest_dispatcher.py` PASS in 2.9 s against the dispatcher helper's tree (`v3_build\st3.txt`) | Dispatcher helper |
| Cutover / tool on origin/main | `v3_cutover.py` untracked | [OWED: cutover helper, `D:\ClaudeWork\rimmandrake\v3_cutover\PROGRESS.md`] |
| Conductor, Arbiter, Auditor, Producer, Innovator / last run under cap | never run | Clears through the section 5 trial runs, once `role_launch.py run-now` is published. [OWED: Arbiter helper, ETA 18:15, `v3_build\RUN_NOW_COORD.md`] |

**Warnings (non-blocking):**
- Claude runway 0.45 and Codex runway 0.14. Both are MEASURED and under 0.8, so the Codex review step is the scarce one.
- FOUNDRY clone has 21 uncommitted shard lines (filed: SEAT_SHARD_FIX_UNPUBLISHED_AT_CLOSEOUT, FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS).

---

## 1. Preflight (before his go; stop at the first failure)

1. **Every helper landed.** For each file in `D:\ClaudeWork\rimmandrake\v3_build\`, check that the last line says committed and published:
   - arbiter.md
   - auditor_innovator.md
   - conductor.md
   - dispatcher.md
   - producer.md
   - also `...\v3_cutover\PROGRESS.md`

   Then `git fetch -q origin && git status --short src/RimMandrake/rimflow/` should list no `??` for v3_cutover.py, selftest_v3_cutover.py, role_launch.py or helper_budget.py.

   **Proves:** nothing anyone needs tonight is only on a disk.

2. **The dispatch clone runs what was published.** `git -C /home/mandrake/rm/dispatch log -1 --format=%h` equals `git log -1 --format=%h origin/main` (`testq-tick` pulls each minute).

   **Proves:** v3_ready row `Dispatcher / dispatch clone current` is GO.

3. **Full check:** `python3 src/RimMandrake/rimflow/v3_ready.py > $T/ready_pre.txt; echo exit=$?`.

   **Must be:** NO-GO rows only `last run under cap` (cleared by the section 5 trial runs). Everything else GO, WARN or INFO.

   Any other NO-GO or UNMEASURED: fix it or tell him the named row and wait.

4. **No live role run, nothing half-done:**
   - `python3 src/RimMandrake/rimflow/dispatcher.py status --apply` shows no role `state: running`.
   - `systemctl --user list-units 'rm-role-*' --no-pager` lists none.

   The switch must not cut a run.

5. **Conductor tile already applied** (cutover/conductor helpers): the BENCH tile opens as the Conductor on relaunch. Check with a dry run that changes nothing: `python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --only BENCH` should plan no change.

5b. **FOUNDRY's stranded ledger must land before the cutover** (FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS). At 17:10 the FOUNDRY clone was 87 commits behind with 17 unpublished shard events since 21:48Z. v3_ready showed 21 uncommitted lines at 17:20. Ask FOUNDRY (or ring it) to commit and `./publish` its shard, then make sure the clone fast-forwards to origin/main.

   **Proves:** `git -C /home/mandrake/rm/foundry diff --numstat HEAD -- infrastructure/state/ledger/events/FOUNDRY.jsonl` prints nothing, `git -C /home/mandrake/rm/foundry rev-list --count HEAD..origin/main` prints 0 (after `git -C /home/mandrake/rm/foundry fetch -q`), and the v3_ready `FOUNDRY ledger / uncommitted lines` row reads INFO 0. The cutover reassigns into FOUNDRY's queue, so a stale clone would work on old state.

6. **Write night.md line 1:** time, ready_pre verdict, the five helpers' last lines. Commit nothing yet.

## 2. His go (**[MANDRAKE]**)

7. **[MANDRAKE] "go"** (any wording that says go). Copy his exact words into night.md.

## 3. Account switch (closes and relaunches every window)

8. **Switch:** `claude-account use steven --confirm archmagi` (his command, verbatim).

   The switching plan stays on **HOLD**. Do not touch `D:\ClaudeWork\rimmandrake\switching_plan\HOLD`. Only his word removes it.

   This window dies here. **The relaunched Conductor resumes at 8a after reading `$T/night.md`.**

   - 8a. **Account:** `claude-account --json status` → `"live": "steven"`, its state `ok`.
   - 8b. **Windows back:** `python3 src/RimMandrake/rimflow/v3_ready.py --no-selftests --expect-account steven > $T/ready_switch.txt; echo exit=$?`. Must show GO for:
     - `Account / live account` (the expected account is live and ok);
     - `Window FOUNDRY / live session` (an `AGENT FOUNDRY` session whose pid and start time are live);
     - `Window CONDUCTOR / live session` (the `AGENT BENCH` tile, which is the Conductor);
     - `Account HOLD` both rows;
     - `Doorbell FOUNDRY / hook installed`.

     `Doorbell FOUNDRY / armed or rung` may read UNMEASURED for one FOUNDRY turn. That is a new window that has not ended a turn yet. Re-run after ~5 min: it must read GO, meaning the armed file has a live pid or a ring in the last hour.
   - 8c. **If a window did not come back:** reopen that tile from Windows Terminal (`AGENT FOUNDRY` / `AGENT BENCH` profile). Do not restart the Dispatcher. It keeps ticking across the switch.
   - 8d. **Runway on the new account:** the `Runway / Claude (steven)` row. GO or WARN is fine. NO-GO (week left under 10 %) means stop and tell him.

     If that row reads UNMEASURED because ops_watch has not measured the new account yet (status older than 45 min, or no `accounts.steven.*` point), wait one ops_watch pass (15 min) and re-run.

## 4. Cutover: BENCH's lane goes to FOUNDRY

9a. **Plan:** `python3 src/RimMandrake/rimflow/v3_cutover.py plan > $T/cutover_plan.txt; tail -n 5 $T/cutover_plan.txt`.

   The counts should be near the helper's 17:12 plan (move 683, keep 40, defer 0; `D:\ClaudeWork\rimmandrake\v3_cutover\plan.txt`). Small drift is items filed since then. **defer > 0** means a BENCH window holds a live lease: wait for it, or apply now and re-run apply after (apply is idempotent).

   The rule:
   - keep = needs him live (needs=owner or next level L4) plus the cutover item itself;
   - everything else BENCH owns moves to FOUNDRY.

9b. **Apply** (only with no BENCH helper mid-work):

   ```
   python3 src/RimMandrake/rimflow/v3_cutover.py apply --owner-said "Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry" --commit && ./publish
   ```

   It writes, in this order:
   - one `reassign --to FOUNDRY` event per item (seat OWNER, his words);
   - the FlowWorks/GSS lane seat flipped to FOUNDRY;
   - the staged docs patch (CLAUDE.md / CHARTER / FOUNDRY.md / BENCH.md lines);
   - `infrastructure/state/v3_cutover/record.json`.

   `./publish` is part of the command. His words above are the cutover instruction already on the item (17:00 PDT); his go at step 7 goes in night.md. Revert: `v3_cutover.py revert --owner-said "<his words>" --commit`.

   **Proves:**
   - it prints `PUBLISHED <sha>`;
   - `python3 src/RimMandrake/rimflow/v3_ready.py --no-selftests` shows `Cutover / applied` INFO `record.json present (applied ...)`;
   - `python3 src/RimMandrake/rimflow/cli.py next --seat FOUNDRY | head` lists former BENCH items.

9c. **Helper budget follows the work:** HELPER_BUDGET_MIGRATE_INTO_DISPATCHER is published (`bce8d5a772`). The Dispatcher writes `$S/helper_budget.json` every tick and the spawn hook reads it first. Checks:
   - `$S/helper_budget.json` exists, is fresh (mtime under 5 min), and has `seats.FOUNDRY` greater than 0;
   - CONDUCTOR has a share only while he is present.

   The exact proof line: `python3 src/RimMandrake/rimflow/helper_budget.py show` prints `seats {'CONDUCTOR': <n>, 'FOUNDRY': <n>} ... (fresh: the hook uses it)`. At 17:47 it was CONDUCTOR 10 (his override until 2026-11-04 12:00) and FOUNDRY 1: the pace fit is 0.9 at a 1.78 %/h burn, and a low FOUNDRY number is the brake, not a fault. FOUNDRY's clone must be pulled before its window's hook reads the budget.

   Until it lands, use the cutover helper's staged slot line: `python3 src/RimMandrake/Utils/slot_allocator.py set --seat FOUNDRY --n 6 --owner-said "Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry"`. It is superseded once Dispatcher-owned budgets land. Without either, FOUNDRY's helper slots come from the old allocator. That allocator gave FOUNDRY 0 at 17:00 (25 % share starving FOUNDRY). Note it in night.md as a known gap; it is not a blocker for the trial.

## 5. Enable the roles (safe order: cheapest and most observed first; one flip per publish)

**How each role is flipped.** Edit only that role's `enabled` key; do not reformat the JSON. Example for the Arbiter:

```
sed -i 's/{"name": "Arbiter", "enabled": false,/{"name": "Arbiter", "enabled": true,/' src/RimMandrake/rimflow/dispatcher_schedule.json
python3 -c "import json;s=json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json'));print([(r['name'],r['enabled']) for r in s['roles']])"
git diff --stat src/RimMandrake/rimflow/dispatcher_schedule.json     # 1 line changed
```

**The go-live set widens in the same file.** `selftest_dispatcher.py` reads the allowed set from the schedule's `golive` block. It goes RED with `role <X> must stay disabled (go-live set: ...)` when a role is enabled but not named there. So the flip also adds the role's name to `golive.roles`; no test edit is needed:

```
sed -i 's/"golive": {"roles": \[\([^]]*\)\]/"golive": {"roles": [\1, "Arbiter"]/' src/RimMandrake/rimflow/dispatcher_schedule.json
python3 -c "import json;print(json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json'))['golive']['roles'])"
```

`recover_dead` works the same way: a seat's `recover_dead: true` passes only with that seat in `golive.recover_dead`.

Then:

```
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_dispatcher.py   # RESULT: GREEN
./publish -m "v3 trial: enable <Role>" src/RimMandrake/rimflow/dispatcher_schedule.json
```

**Proves:** `PUBLISHED <sha>`, then within ~1 min `git -C /home/mandrake/rm/dispatch log -1 --format=%h` equals it. v3_ready's `<Role> / enabled` then reads `ON`.

**Trial run first, then flip.** Each role gets one one-shot run before its flip, which also clears its `last run under cap` row. The run-now path works while the role is `enabled: false` and obeys the off file, busy, ops MEASURED, band, caps and account:

```
python3 src/RimMandrake/rimflow/role_launch.py run-now --role <Role> --by BENCH --why "v3 trial night: first run" [--mode weekly|quick|economy] --apply
python3 src/RimMandrake/rimflow/role_launch.py run-status --role <Role>
```

[OWED: Arbiter helper. Confirm these exact flags once role_launch.py run-now is published (ETA 18:15); add `--trial` / `--claim ITEM@SHA` usage for the Arbiter fixture run.]

The next live tick (≤2 min) launches it. Watch with `run-status`. Done means:
- `$S/roles/rm-role-<role>-<epoch>.json` has `subtype: success`;
- v3_ready's `<Role> / last run under cap` is GO.

| Step | Role | Already | Trial run | Then |
|---|---|---|---|---|
| 10 | **Operations** | enabled (wave 1) | none needed (285,538 / 450,000, GO) | keep |
| 11 | **Conductor** | enabled (wave 1), never run (08:00 slot missed) | `run-now --role Conductor --mode quick`. The conductor helper's foreground trial at 17:18 was 9 turns, 74 s, success, `v3_build\conductor_trial\log.md`. While the `AGENT CONDUCTOR` hold window is live, headless runs are held. That is fine: the tile is `AGENT BENCH`. | keep |
| 12 | **Arbiter** (ADVISORY) | off | `run-now --role Arbiter` on one real claim and one bad fixture [OWED: Arbiter helper, the exact claim/fixture lines, `v3_build\arbiter.md` steps "trial (a) real claim" and "trial (b) bad fixture"]. Healthy: verdicts land in the trial sink, not live notes. | flip |
| 13 | **Producer** | off | `run-now --role Producer --mode weekly` [OWED: Producer helper, `v3_build\producer.md` step 3]. Healthy: a plan file `D:\ClaudeWork\rimmandrake\producer\plan_<date>.md` built from `infrastructure/state/CONDUCTOR_GOALS.md`, then commit+publish. | flip |
| 14 | **Auditor** | off | `run-now --role Auditor` [OWED: Auditor/Innovator helper, `v3_build\auditor_innovator.md`]. Its pre_launch runs `audit_prescreen --days 1` fresh. | flip |
| 15 | **Innovator** | off | `run-now --role Innovator` [OWED: Auditor/Innovator helper]. | flip last |
| 16 | **Seat restart** | `seat_restart.enabled: false` | **Readiness (dispatcher helper):** the code is GO. `selftest_seat_restart` is GREEN and the new `seat_restart.dry` key makes the dry ticket possible under the live `--apply` timer. To enable, follow §10 of `design/RimMandrake/rimflow_v3_golive_wave1.md` in this order: (1) `"seat_restart": {"enabled": true, "dry": true, ...}` and publish; (2) one dry ticket, `grep restart_ $S/journal.jsonl` shows `would SIGTERM`; (3) `install_wt_seat_profiles.py --apply`; (4) he reopens the FOUNDRY tile; (5) `"dry": false`, publish, then watch `restart_request` → `restart_kill` → `restart_relaunched` → `restart_verified`. Two prerequisites: the FOUNDRY doorbell arms, and the wakes are live. | hold |
| 17 | **FOUNDRY wake cap** | 3 wakes/hour; alarm `cap:FOUNDRY` already open | Proposal: `caps.wakes_per_seat_hour` 6 and `caps.wakes_per_seat_day` 48. Measured in `$S/journal.jsonl` 22:00-00:45Z (`v3_build\wake_rows.txt`): 7 rings. Ring to lease take was 8-12 s in all 4 claimed wakes, and 2 rings got no handoff in 600 s. Uncapped, FOUNDRY asked for a wake every ~4 min. After 3 wakes in 8 min, the cap held an idle FOUNDRY for 49 min (23:23-00:12). At 6/h, a runaway wake loop still stops at 6. The day cap moves with it, because 30 would bind after 5 h at 6/h. The lines go under `caps` in `dispatcher_schedule.json` (one publish). | flip |

**Never tonight:**
- `recover_dead` true (not proved since the BG-survives proof was for role runs only);
- removing HOLD;
- any worldgen.

After step 15: `python3 src/RimMandrake/rimflow/v3_ready.py > $T/ready_enabled.txt`. **Must be GO overall.** WARN and INFO allowed.

## 6. First hour after step 15 (look every 10 min, write each look in night.md)

**Each look:**
- `python3 src/RimMandrake/rimflow/v3_ready.py --no-selftests > $T/ready_$(date +%H%M).txt; tail -n 12 $T/ready_$(date +%H%M).txt`
- `python3 -c "import json;print(json.load(open('$S/state.json'))['alarms'])"`

**Healthy per component:**

| Component | Healthy looks like |
|---|---|
| **Dispatcher** | `ticking` GO every look (last_ok_tick < 10 min). Alarms hold no `unwakeable:*`, no `role:*:scope`/`supervise`/`overtime`, no new `account:*`. (`account:unmeasured` and `cap:FOUNDRY` were open before tonight.) |
| **FOUNDRY** | Rings in `$S/journal.jsonl` each have a hand-off; no `WOKE_NO_HANDOFF` repeats. Its shard commits and publishes at each close-out: `FOUNDRY ledger / published recently` stays GO. The `uncommitted lines` WARN count falls instead of growing. It takes former BENCH items (step 9b). |
| **Conductor** | Answers him with MEASURED / ESTIMATE / UNMEASURED words. One launch note and one done note per quick check. |
| **Operations** | Each run `subtype: success` under 450,000 (economy 550,000). Files OPS_* items or says nothing to do. Reads `$O/digest.md` without re-gathering. A run under 20k or over cap is suspect. |
| **Arbiter** | Advisory only. Verdicts in its sink plus one note per judged item. No close, no reopen by itself. Run under 500,000. |
| **Producer** | One plan file per run, every line traceable to a goal in CONDUCTOR_GOALS.md (his words cited). Commits+publishes. Does not write goals. |
| **Auditor** | Its prescreen ranks blind closes (the HOSE close should rank near the top, 2/78 at build). Files audit findings as items. Under 500,000. |
| **Innovator** | Proposals filed as items with `--why`. No code edits. Under 500,000. |
| **Owner and game** | Nothing in the journal says bridge/game/deploy was taken. Owner-present rings carry "owner present: do not take the bridge". |

**Any "not healthy" line:** switch that one component off (section 7) first, investigate second, write it in night.md, and file it (`rimflow namecheck` → item).

## 7. Kill / rollback per component (narrowest first)

Each item stands alone. Do the narrowest one that stops the harm.

1. **One role, instantly** (no commit). Write its off file:

   | Role | Off file |
   |---|---|
   | Conductor | `/mnt/d/ClaudeWork/rimmandrake/conductor/CONDUCTOR_OFF` |
   | Operations | `$O/OPERATIONS_OFF` |
   | Arbiter | `/mnt/d/ClaudeWork/rimmandrake/arbiter/ARBITER_OFF` |
   | Auditor | `/mnt/d/ClaudeWork/rimmandrake/auditor/AUDITOR_OFF` |
   | Producer | `/mnt/d/ClaudeWork/rimmandrake/producer/PRODUCER_OFF` |
   | Innovator | `/mnt/d/ClaudeWork/rimmandrake/innovator/INNOVATOR_OFF` |

   Form: `mkdir -p <dir> && printf 'off: <why>\n' > <file>`. **Proves:** v3_ready's `<Role> / enabled` reads `..., off file present`, and the journal shows `role_hold ... off switch`.

   Durable form: flip `"enabled": true` back to `false` with the same sed in reverse, publish. Stop its live run first (item 3).

2. **A one-shot run not yet launched:** `python3 src/RimMandrake/rimflow/role_launch.py run-now --role <Role> --cancel` [OWED: Arbiter helper, confirm].

3. **A live role run:**
   - `python3 src/RimMandrake/rimflow/dispatcher.py stop-runs` must print `ALL LIVE ROLE RUNS ENDED (verified)`.
   - If it does not: `systemctl --user list-units 'rm-role-*' 'claude-seat-*-rm-role-*' --no-pager`, then stop the scope first and the service second.
   - **Proves:** `grep -lsz '^RM_ROLE_UNIT=rm-role-<name>-<epoch>$' /proc/[0-9]*/environ` prints nothing. Wave-1 §7 has the full form.

4. **Cutover:** `python3 src/RimMandrake/rimflow/v3_cutover.py revert --owner-said "<his words>" --commit`, then `./publish`. It undoes exactly what record.json names: reassigns back, lane seat back, docs patch reversed. Only on his word or a clear harm.

5. **FOUNDRY stops being woken:** `"wake": false` under `seats.FOUNDRY` in the schedule, publish.

   **Doorbell:**
   - delete the `hooks` block from `/home/mandrake/rm/foundry/.claude/settings.local.json` (settings change: [MANDRAKE] if he asks);
   - then `rm -f $S/inbox/FOUNDRY.json $S/armed/FOUNDRY.json`.

6. **Everything the Dispatcher does:** `printf 'v3 trial rollback: <why>\n' > $S/PAUSE`.

   **Proves:** the next tick's journal reads `PAUSE file present`, and v3_ready's `Dispatcher / no PAUSE` reads NO-GO. Remove with `rm $S/PAUSE`.

7. **Wakes back to dry-run**, only after item 3 printed ALL ENDED:
   - `sed -i 's#dispatcher.py tick --apply$#dispatcher.py tick#' ~/.config/systemd/user/rm-dispatcher.service && systemctl --user daemon-reload`.
   - Fully off: `systemctl --user disable --now rm-dispatcher.timer`.

8. **Account:** switching back is his command (`claude-account use <name> --confirm ...`). HOLD stays in every case.

9. **Whole system back to v2:** git tag `system-baseline-two-seat-2026-10-26` (design §6). Revert the cutover (item 4) before anything else.

## 8. The 48 hours to next Wednesday (2026-11-04): evidence for keep-or-kill

Gather this into `$T/`. One file per item; numbers carry MEASURED / ESTIMATE / UNMEASURED.

| # | Evidence | How it is gathered |
|---|---|---|
| a | **v3_ready series** | `ready_*.txt` at least at each 08:00/20:00 slot. The fraction of looks with OVERALL GO; every NO-GO row with its time. |
| b | **Dispatcher liveness** | `deadman_check.py run` all alive at hour 24 and 48. No gap above 10 min in `last_ok_tick`, from `$S/journal.jsonl` tick lines. |
| c | **Wakes** | Rings versus hand-offs versus `WOKE_NO_HANDOFF`, from the journal. `cap:FOUNDRY` alarm count per day. |
| d | **Role runs** | Per role: runs, `success` share, weighted tokens per run against its cap (`$S/state.json` roles[].runs and `$S/roles/*.json`), failed and overtime count. |
| e | **FOUNDRY throughput** | Items closed per day by FOUNDRY before versus after 9b (rimflow ledger); shard publish gaps (the `published recently` row). |
| f | **Owner-facing KPIs** (design §6, against the baseline tag) | Keep-going messages per day (31 → ≤26); accepted items per day; test hours that caught nothing (≤18 h/wk); failure-signal share (27.5 % → ≤25 %); process-commit share (70 % → <61 %). Keep-going, failure-signal and accepted/day are still **UNMEASURED** (OPS_KPI_MEASURE_OWED_VTHREE): never read them as 0. His own count of "keep going" messages is the stand-in. `v3_vs_v2.py` runs weekly. |
| g | **Harm log** | Every rollback used (section 7), with its trigger. Any bridge/game take while he played (must be 0). Any token number reaching the Conductor. |
| h | **Cost** | Claude week-left % per account and Codex week-used %, from `$O/status.json` points, at the start and at 48 h. |

**Kill criterion (his, design §6):** after a week of v3, if his keep-going messages have not dropped and accepted items have not risen, stop and reconsider; the baseline tag restores v2. The decision day is next Wednesday, and the decision is his. The Conductor brings rows a–h, not a recommendation dressed as a measurement.
