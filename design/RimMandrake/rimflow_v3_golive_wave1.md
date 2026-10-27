# RimFlow v3 go-live, wave 1 (runbook, written 2026-10-27, for Wednesday 2026-10-28 after the weekly token reset)

Item: `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` (design `design/RimMandrake/rimflow_v3_2026-10-26.md` §6 item 1-3).
Wave 1 switches on: the Dispatcher's live **wakes** (FOUNDRY only), the **Conductor**'s quick checks and **Operations**' runs.
Nothing else: Producer, Arbiter, Auditor, Innovator stay `enabled:false`; `recover_dead` stays off.

Written offline and read-only on 2026-10-27; every command below was run with `--help` or its read-only form that day,
except the ones marked WRITES. Marks: **[MANDRAKE]** = needs him (physical game launch/close is his; his own Claude
settings may be), **[WRITES]** = changes a system, run only in order. Abort rule: any step whose check fails stops the
wave; go to section 7 (rollback) if anything was already switched on.

Paths: repo clone `/home/mandrake/rm/bench`; Dispatcher state `/mnt/d/ClaudeWork/rimmandrake/dispatcher`
(`D:\ClaudeWork\rimmandrake\dispatcher`); ops_watch `/mnt/d/ClaudeWork/rimmandrake/ops_watch`. Below `$B=/home/mandrake/rm/bench`,
`$S=/mnt/d/ClaudeWork/rimmandrake/dispatcher`, `$O=/mnt/d/ClaudeWork/rimmandrake/ops_watch`.

## 0. Findings from the offline pass (2026-10-27) that change the order

- **There is no `genai-switch`** on this machine (`command not found`). The account tool is `claude-account` (`~/.local/bin`).
  Step 1 uses `claude-account status`.
- **The FOUNDRY clone is stale: `/home/mandrake/rm/foundry` has no `src/RimMandrake/rimflow/doorbell.py`** (HEAD `c837e3ddb1`, 2026-10-26 11:41).
  The hook cannot point at a file that is not there. Step 7 must precede step 8.
- `.claude/settings.json` in a clone is git-tracked and shared; the doorbell goes in the clone's **`.claude/settings.local.json`**
  (gitignored, per clone, already exists in foundry: `.gitignore:171`), so BENCH and the owner's windows never get it.
- Dispatcher has a standing dry-run alarm `unwakeable:FOUNDRY` ("FOUNDRY is idle but no doorbell is armed"). It is the expected
  state until step 8; it clearing is step 8's proof.
- The first `--apply` tick for an enabled Operations role runs once for every ALARM open at first enable
  (`alarm_runs`). On 2026-10-27 the open alarm is `RUNWAY_LOW:codex.runway` (`$O/alarms.json`), so enabling Operations launches an
  alarm run at once, not at 07:30/19:30. Expect it; do not read it as a fault.

## 1. Pre-flight (all from `$B`; stop at the first failure)

1. **Account.** `claude-account status` (use `--json` for a machine read: key `live`, `accounts`). Proves: the line marked `*` is
   the live account and it is an **owned** one. Lent accounts are the keys of `lent_accounts` in `src/RimMandrake/Utils/slot_rules.json`
   (`python3 -c "import json;print(list(json.load(open('src/RimMandrake/Utils/slot_rules.json'))['lent_accounts']))"`; today: `steven`).
   Live on a lent account (or the line is not `ok`) = **STOP and decide with Mandrake**; do not switch accounts yourself
   (`claude-account use` closes every window on the machine, DISARMED guard applies). Today: live `system`, owned, ok.
2. **Selftests green** (6 files, one command):
   `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_dispatcher.py src/RimMandrake/rimflow/selftest_account_pick.py src/RimMandrake/Utils/selftest_slot_allocator.py src/RimMandrake/Utils/selftest_ops_watch.py src/RimMandrake/rimflow/selftest_blind_view.py src/RimMandrake/Utils/selftest_deadman_check.py`
   Proves: last line `RESULT: GREEN` with `PASS 6/6`. Today: `PASS 6/6 ... GREEN`.
3. **dispatch clone current** (the Dispatcher service runs from it). It updates itself: `testq-tick.service` does
   `git -C /home/mandrake/rm/dispatch pull -q --ff-only origin main` before each tick (timer every minute).
   Check: `git -C /home/mandrake/rm/dispatch log -1 --format=%h` equals `git -C /home/mandrake/rm/bench ls-remote origin main | cut -c1-10`
   (compare 10 characters), and `git -C /home/mandrake/rm/dispatch status -sb | head -1` ends without `behind`.
   Today: both `44155dc383`.
4. **pulse-deploy clone current** (ops_watch and deadman run from it). It updates itself: `rm-pulse-update.timer`
   (every 5 min) runs `pulse.py update --restart`, a fast-forward to origin/main. Check:
   `git -C /mnt/d/ClaudeWork/rimmandrake/pulse-deploy log -1 --format=%h` equals the ls-remote sha above; if it is behind, either wait
   5 min and recheck, or confirm the missing commits touch none of the six files in step 2
   (`git diff --name-only <deploy sha> origin/main`). Today it was 2 commits behind (`32ca578faa` vs `44155dc383`), the gap touched only
   arbiter.md and its selftest, so not blocking; recheck on the day.
   Last update log: `journalctl --user -u rm-pulse-update -n 3 --no-pager`.
5. **The three arms healthy.**
   - `python3 src/RimMandrake/Utils/deadman_check.py run` (no `--file-alarms`: read only). Proves: prints `deadman: all arms alive`
     (covers ops_watch stamp < 50 min and dispatcher stamp < 15 min).
   - For each of `rm-deadman rm-ops-watch rm-dispatcher`:
     `systemctl --user show -p Result,ExecMainStatus,ActiveState <unit>.service; systemctl --user is-active <unit>.timer`.
     Proves: `Result=success ExecMainStatus=0` and the timer `active`. (Services are `inactive` between oneshot runs: normal.)
   - `systemctl --user list-timers --no-pager | grep -E 'rm-(deadman|ops-watch|dispatcher)'` shows a NEXT time for each
     (the line can read `-` for a few seconds while the service runs; recheck).
   - Dispatcher is still dry: `python3 src/RimMandrake/rimflow/dispatcher.py status` prints `"apply": false` and a recent `last_ok_tick`.
6. **`digest_blind.md` has no account numbers.**
   `grep -n -i -E 'runway|week_left|week left|lukas|steven|system@|gmail|codex|amber|floor|\bred\b|green|quota|token|burn' $O/digest_blind.md; echo rc=$?`
   Proves: no match lines and `rc=1`. Control (the instrument can see): the same words in `$O/digest.md` match
   (`grep -c -i -E 'runway|codex' $O/digest.md` printed 8 on 2026-10-27). Fresh file: its first line carries a timestamp within 15 min.
   Today: clean.

## 2. FOUNDRY must have the doorbell file

7. **[WRITES, FOUNDRY's own clone: FOUNDRY does it or tells BENCH to]** Bring `/home/mandrake/rm/foundry` to origin/main:
   `git -C /home/mandrake/rm/foundry pull --ff-only origin main` (its untracked `Transient/` files do not block an ff).
   Proves: `ls /home/mandrake/rm/foundry/src/RimMandrake/rimflow/doorbell.py` exists and `git -C /home/mandrake/rm/foundry log -1 --format=%h`
   equals the ls-remote sha. If the ff is refused (local commits or dirty tracked files), stop: FOUNDRY resolves it, BENCH does not force it.

## 3. Doorbell hook (FOUNDRY seat only)

How it was proven: Claude Code 2.1.308 runs a `Stop` hook marked `asyncRewake:true` in the background and wakes the idle window when the hook
exits 2; ledger note on `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` 2026-10-27T05:47:16Z cites
`D:\ClaudeWork\rimmandrake\dispatcher_build\wake_proof\run1.txt` and `run2.txt` (woken after 1.9 s; inbox consumed; same session). The
proof's settings file was `.../wake_proof/settings.json`. Read it: `rimflow show RIMFLOW_V3_BUILD_DISPATCHER_FIRST` (the note says "NOT yet installed in seat settings").
Open hardening items from the review (read before go-live, not blockers per the 06:02:16Z note): `DOORBELL_HARDEN_SPARE_OWNER_TYPING`,
`DISPATCHER_HARDEN_OWNER_RETURN_AFTER_RING`.

8. **[MANDRAKE confirms, WRITES]** Install the hook in `/home/mandrake/rm/foundry/.claude/settings.local.json` (merge into the existing
   JSON, which today is `{"permissions": {...}, "spinnerTipsEnabled": false}`; it is gitignored). Add:
   ```json
   "hooks": {"Stop": [{"hooks": [{"type": "command", "asyncRewake": true, "timeout": 86400,
     "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/src/RimMandrake/rimflow/doorbell.py\""}]}]}
   ```
   (the exact block in the `doorbell.py` docstring; the tracked `settings.json` already has a different `Stop` hook, `block_paste_handoff.py`; hook
   arrays from the two files both run). Validate: `python3 -c "import json;d=json.load(open('/home/mandrake/rm/foundry/.claude/settings.local.json'));print(d['hooks']['Stop'][0]['hooks'][0]['asyncRewake'])"` prints `True`.
   Mandrake mark: this is a settings change on the seat the owner runs; get his yes, or FOUNDRY's, before writing. The FOUNDRY window must then
   be a session that loads the file (settings are read at session start; a window opened before the edit may not have it): restart that
   window **[MANDRAKE: closing/relaunching his window is his; the Dispatcher never does it]**.
9. **Proof it armed.** After the FOUNDRY window's next turn ends (it goes idle): `cat $S/armed/FOUNDRY.json` shows a pid, a `session_id`,
   `owner_pid` and `armed_at` within the last few minutes, and `ps -p <pid>` is alive. Within one tick (2 min, dry) `$S/dry/journal.jsonl`
   stops adding `unwakeable:FOUNDRY`: `tail -n 3 $S/dry/journal.jsonl | cut -c1-200`. A window that never arms (no `armed/FOUNDRY.json`) means the hook did not load; do not go on.

## 4. Wakes live (timer from dry-run to `--apply`)

Flag facts: `dispatcher.py tick --apply` ("really ring/recover/record"); no flag means dry. Recover is off by the schedule key
`seats.<SEAT>.recover_dead` (both seats `false` today; `dispatcher.py` line ~392 skips recovery unless it is true). There is no CLI flag for it, so
"keep it off" = do not touch that key; also optional belt: `caps.recovers_per_seat_day` to 0. Reason (ledger 06:02:16Z):
`DISPATCHER_RECOVERY_PROVE_BG_SURVIVES` must pass first. BENCH is `wake:false` in the schedule: only FOUNDRY is woken.

10. **Confirm before flipping:** `python3 -c "import json;s=json.load(open('/home/mandrake/rm/dispatch/src/RimMandrake/rimflow/dispatcher_schedule.json'));print({k:(v['wake'],v['recover_dead']) for k,v in s['seats'].items()}, [(r['name'],r['enabled']) for r in s['roles']])"`
    Proves: FOUNDRY `(True, False)`, BENCH `(False, False)`, every role `False` (roles still off: so `--apply` can launch nothing but wakes).
    Also `ls $S/PAUSE` should be absent.
11. **[WRITES]** Edit the installed unit (the one systemd runs) and, so the repo agrees, the repo copy:
    `sed -i 's#dispatcher.py tick$#dispatcher.py tick --apply#' ~/.config/systemd/user/rm-dispatcher.service src/RimMandrake/rimflow/systemd/rm-dispatcher.service`
    then `systemctl --user daemon-reload`. Proves: `grep ExecStart ~/.config/systemd/user/rm-dispatcher.service` ends `tick --apply`
    (the two copies were identical on 2026-10-27: `diff` printed nothing). Update the file's header comment ("DRY-RUN") and `Description=` in the repo copy
    in the same commit as step 12. The deadman picks the live state by reading this ExecStart for `--apply` (it then watches `$S/state.json`, not `dry/`).
    The next run of the timer is the first live tick; no `restart` needed.
12. **Proof wakes are live** (wait 2-4 min): `python3 src/RimMandrake/rimflow/dispatcher.py status --apply` prints `"apply": true` and a fresh
    `last_ok_tick`; `tail -n 5 $S/journal.jsonl | cut -c1-250` exists (live journal, no longer under `dry/`);
    `python3 src/RimMandrake/Utils/deadman_check.py run` still says `all arms alive` (it now reads the live stamp). If a ring happens
    (FOUNDRY idle >= 240 s with a ticket): `ls $S/consumed/` gains `FOUNDRY-*.json` within `verify_s` (300 s), and FOUNDRY's shard gains a
    lease/claim/start (`rimflow next` hand-off), then a ledger note by seat `DISPATCHER` appears (`tail -n 2 infrastructure/state/ledger/events/DISPATCHER.jsonl | cut -c1-300`).
    Caps in force: 3 wakes/seat/hour, 30/seat/day, 80/day.

## 5. Roles: Conductor and Operations

Schedule file: `src/RimMandrake/rimflow/dispatcher_schedule.json` (edited in `$B`, published, read by the dispatch clone).
Both roles carry the builder's defaults `seat BENCH`, `clone /home/mandrake/rm/bench`, `model opus` flagged "confirm before enabling" in the file.

13. **[MANDRAKE]** Confirm the defaults, and the time of day. Operations' alarm run fires at first enable (see §0); the Conductor's first check
    launches only after an Operations run has finished (`after_role: Operations`), at the 08:00/20:00 slots, and a slot more than `slot_late_s` (1 h) late is missed.
    Cheapest clean start: enable shortly before 19:30 or 07:30 so the first Operations run is a scheduled one. His call, with the
    runway reading (Operations is the only role that is token-aware).
14. **[WRITES]** Flip only these two keys, nothing else (edit by hand; the file is JSON with long lines, so do not reformat it):
    in the `Conductor` and `Operations` role objects change `"enabled": false` to `"enabled": true`. Proves, before committing:
    `python3 -c "import json;s=json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json'));print([(r['name'],r['enabled']) for r in s['roles']])"`
    prints Conductor True, Operations True, the other four False; and `git diff --stat src/RimMandrake/rimflow/dispatcher_schedule.json` is 2 lines changed.
    Run `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_dispatcher.py` again (GREEN).
15. **[WRITES]** Publish (explicit paths; the repo unit file from step 11 goes in the same commit):
    `./publish -m "Dispatcher wave 1: timer --apply (wakes), Conductor + Operations enabled" src/RimMandrake/rimflow/dispatcher_schedule.json src/RimMandrake/rimflow/systemd/rm-dispatcher.service`
    Proves: prints `PUBLISHED <sha>`.
16. **Dispatch clone picked it up** (within ~1 min, `testq-tick` pulls): `git -C /home/mandrake/rm/dispatch log -1 --format=%h` equals the published sha, and
    `python3 -c "import json;s=json.load(open('/home/mandrake/rm/dispatch/src/RimMandrake/rimflow/dispatcher_schedule.json'));print([(r['name'],r['enabled']) for r in s['roles']])"`
    shows the two True. The next tick (<= 2 min) reads it. Proof of the pickup: `python3 src/RimMandrake/rimflow/dispatcher.py status --apply` `roles` gains `Operations`
    (and later `Conductor`) once launched, and `$S/roles/` gains `rm-role-operations-<epoch>.json`/`.err`.
    Pulse-deploy is not involved (ops_watch reads rules, not the schedule).

## 6. First-hour watch (from step 15 on; look every 10 min, write the time of each look)

Healthy means all of the below. Any "not healthy" line: switch the named role off (section 7) first, investigate second.

- **Launch notes.** `python3 src/RimMandrake/rimflow/cli.py show OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE | tail -n 12` (Operations' launch, done and cap
  notes) and `... show V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE | tail -n 12` (Conductor). Healthy: one launch note naming mode, band and the account per run, then a
  "done" note for it; no cap note, no "ended without a good result".
- **Alarms.** `cat $O/alarms.json | head -c 1500` (ops_watch), `python3 -c "import json;print(json.load(open('$S/state.json'))['alarms'])"` (Dispatcher),
  `python3 src/RimMandrake/Utils/deadman_check.py run`. Healthy: no `unwakeable:*`, no `role:*:scope|supervise`, no account-pick SWITCH/HOLD/UNMEASURED alarm,
  deadman says `all arms alive`. The pre-existing `RUNWAY_LOW:codex.runway` is not new.
- **First Operations run's output.** `ls -t $S/roles | head -4`; `python3 -c "import json,glob,os;f=sorted(glob.glob('$S/roles/rm-role-operations-*.json'))[-1];d=json.load(open(f));print(f,d.get('subtype'),d.get('is_error'),d.get('usage'));print((d.get('result') or '')[:1500])"`;
  the matching `.err` is empty or short (`wc -c`). Healthy: `subtype` `success`, `is_error` false, total tokens (all four usage fields) under `run_token_cap` 80,000
  (economy pass 07:30: `economy_token_cap` 100,000; ceiling `daily_token_cap` 300,000), the result reads `$O/digest.md` and does not re-gather, and
  it files OPS_* items or says nothing to do. Measured floor is 35-53k per run, so a run under 20k or over cap is suspect.
- **Token-talk series (the blind roles stay blind).** `tail -n1 $O/series/tokentalk.jsonl | python3 -c "import json,sys;d=json.loads(sys.stdin.read());[print(k,v['m'],v['v']) for k,v in d['points'].items()]"`.
  Baseline 2026-10-27: BENCH 3.0 %, FOUNDRY 1.2 %; `tokentalk.role.conductor.share` UNMEASURED until 5 reports exist. Healthy: it stays UNMEASURED or low in the first hour; any
  Conductor value above the 3.0 % BENCH baseline once measured, or an `ops_watch` flag on a tokentalk point, means the Conductor is token-talking: file it and switch it off.
  Operations is excluded from this measure by design.
- **Wakes.** Journal and DISPATCHER shard (step 12 commands). Healthy: every ring has a `consumed/` file and a hand-off; no `WOKE_NO_HANDOFF` repeats; per-seat cap not hit.
- **The game and the owner.** Nothing in the journal says `bridge`/`game`/`deploy` was taken; owner-present rings carry "owner present: do not take the bridge".

## 7. Rollback (each independent; do the narrowest one that stops the harm)

- **Stop everything now (all Dispatcher actions, roles included):** `printf 'wave1 rollback: <why>\n' > $S/PAUSE` (the Dispatcher's PAUSE file; remove with `rm $S/PAUSE`).
  Proves: next tick's journal line reads `PAUSE file present`. Running role units are supervised but not newly launched.
- **Conductor off:** `mkdir -p /mnt/d/ClaudeWork/rimmandrake/conductor && printf 'off: <why>\n' > /mnt/d/ClaudeWork/rimmandrake/conductor/CONDUCTOR_OFF`
  (instant, no commit; the dir does not exist yet). Durable form: `"enabled": false` for Conductor in the schedule, publish.
- **Operations off:** `printf 'off: <why>\n' > $O/OPERATIONS_OFF`. Durable: `"enabled": false`.
- **A launched run still going:** `systemctl --user list-units 'rm-role-*' --no-pager`, then `systemctl --user stop rm-role-<name>-<epoch>.service`.
- **Other roles' off files** (not in wave 1; for completeness): `.../arbiter/ARBITER_OFF`, `.../auditor/AUDITOR_OFF`, `.../producer/PRODUCER_OFF`, `.../innovator/INNOVATOR_OFF` under `/mnt/d/ClaudeWork/rimmandrake/`.
- **Both roles via the schedule:** set the two `"enabled": true` back to `false` in `src/RimMandrake/rimflow/dispatcher_schedule.json`, `./publish -m "Dispatcher wave 1 rollback: roles off" src/RimMandrake/rimflow/dispatcher_schedule.json`, check step 16's command shows False.
- **Wakes back to dry-run:** `sed -i 's#dispatcher.py tick --apply$#dispatcher.py tick#' ~/.config/systemd/user/rm-dispatcher.service && systemctl --user daemon-reload`; proves
  `dispatcher.py status` shows `"apply": false` after the next tick. Fully off: `systemctl --user disable --now rm-dispatcher.timer`.
- **Stop waking just FOUNDRY:** `"wake": false` under `seats.FOUNDRY` in the schedule, publish.
- **Doorbell:** delete the `hooks` block from `/home/mandrake/rm/foundry/.claude/settings.local.json` (settings: [MANDRAKE] if he asks), then withdraw any waiting ring: `rm -f $S/inbox/FOUNDRY.json $S/armed/FOUNDRY.json`. An armed doorbell dies with its window.
- **Recover stays off:** never set `recover_dead` true in wave 1.
- Whole system back to v2: git tag `system-baseline-two-seat-2026-10-26` (design §6: "the baseline tag restores v2").

## 8. The 48-hour proof and the kill criterion

From design §6 item 1: prove the Dispatcher with a **48 h unattended run**: wake an idle window; recover a dead one; never take the game while he plays.
Wave 1 covers the first and third; "recover a dead one" stays unproved (`recover_dead` off until `DISPATCHER_RECOVERY_PROVE_BG_SURVIVES` passes), so the 48 h
proof is partial and must be recorded as such, not as a pass of the whole list.

Hour 48 check (Fri 2026-10-30, same time as step 15): (a) `deadman_check.py run` all alive and no gap in `$S/state.json` `last_ok_tick`; (b) the journal
count of wakes with a hand-off versus rings (`WOKE_NO_HANDOFF`, give-ups); (c) zero events of the Dispatcher taking the bridge/game while the owner was active; (d) role runs all `success` and within caps.

Success test and kill criterion, verbatim intent of design §6: measured weekly against the baseline tag - his keep-going messages (31/day -> <= 26 after v3.0), accepted items/day, test hours that catch nothing (<= 18 h/wk), his failure-signal share (27.5 % -> <= 25 %),
process-commit share (70 % -> below 61 %; `process.share_7d` was 65.3 on 2026-10-27). **Kill criterion: after a week of v3.0, if his keep-going messages have not dropped and accepted items have not risen, stop and reconsider; the baseline tag restores v2.**
Owed instruments (UNMEASURED today, never read as 0): keep-going messages, failure-signal share, accepted items/day (`OPS_KPI_MEASURE_OWED_VTHREE`). A week of v3.0 therefore cannot trigger the kill
criterion mechanically yet; Mandrake's own count of "keep going" messages is the stand-in until the classifier lands. Decision day is one week after step 15, his.
