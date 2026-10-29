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
    The selftest accepts exactly this wave-1 set (Conductor and Operations may be enabled; the other four must be `false` and every seat's
    `recover_dead` false): a RED naming `must stay disabled` means a third key was flipped (review dispatcher-full #3).
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
  notes) and `... show V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE | tail -n 12` (Conductor). Healthy: on Operations' item one launch note naming mode, band and the account
  per run; on the Conductor's item one launch note naming mode and unit only (it is token-blind: no band, no account),
  then a "done" note for each; no cap note, no "ended without a good result". A dispatcher note meant for a token-blind
  item that is not on its allow-list of plain texts lands on Operations' item marked `[meant for <item>; token values
  stay off it]` (review roles r2 #1): look for those there too.
- **Alarms.** `cat $O/alarms.json | head -c 1500` (ops_watch), `python3 -c "import json;print(json.load(open('$S/state.json'))['alarms'])"` (Dispatcher),
  `python3 src/RimMandrake/Utils/deadman_check.py run`. Healthy: no `unwakeable:*`, no `role:*:scope|supervise`, no account-pick SWITCH/HOLD/UNMEASURED alarm,
  deadman says `all arms alive`. The pre-existing `RUNWAY_LOW:codex.runway` is not new.
- **First Operations run's output.** `ls -t $S/roles | head -4`; `python3 -c "import json,glob,os;f=sorted(glob.glob('$S/roles/rm-role-operations-*.json'))[-1];d=json.load(open(f));print(f,d.get('subtype'),d.get('is_error'),d.get('usage'));print((d.get('result') or '')[:1500])"`;
  the matching `.err` is empty or short (`wc -c`). Healthy: `subtype` `success`, `is_error` false, weighted tokens (role_launch.run_tokens: cache read 0.1, cache write 1.25/2, output 5) under `run_token_cap` 450,000
  (economy pass 07:30: `economy_token_cap` 550,000; ceiling `daily_token_cap` 1,650,000; 2026-10-28, ROLE_CAPS_REMEASURE_ON_REAL_RUNS), the result reads `$O/digest.md` and does not re-gather, and
  it files OPS_* items or says nothing to do. The first real Operations run (15 turns) weighed 285,538, so a run under 20k or over cap is suspect.
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
- **Live role runs, before ANY switch below that ends supervision** (dry-run, timer off, roles off; review r2 #2): a dry-run tick
  supervises only the `dry/` root and a disabled timer supervises nothing, so a live run must be stopped and VERIFIED first.
  Order: (1) PAUSE (above), so no new launch; (2) `python3 src/RimMandrake/rimflow/dispatcher.py stop-runs` from `$B`
  (TERM, KILL from 60 s, checks up to 120 s; `--wait`/`--force-after` to change) must print `ALL LIVE ROLE RUNS ENDED (verified)`
  and exit 0; exit 1 (`NOT ALL ENDED` / `UNMEASURED`) means do the by-hand stop below and re-run it until it does; (3) only then
  switch. Backstop that needs no Dispatcher at all: every run's unit and its Claude scope carry their own `RuntimeMaxSec`
  (the role's run_max_s + 600 s; KILL 30 s after the TERM), measured 2026-10-27 through `claude_bounded.sh` (a TERM-ignoring
  process bounded at 5 s was KILLed at 35.4 s, scope `Result=timeout`). A dry-run tick that still sees live runs alarms
  `dry:live_runs_unsupervised` in its journal.
- **A launched run still going:** Claude does NOT run inside the `rm-role-*` unit: `claude_bounded.sh` puts it in its own scope
  `claude-seat-<SEAT>-rm-role-<name>-<epoch>.scope`, so stopping only the `.service` leaves Claude running. Stop both, scope first:
  `systemctl --user list-units 'rm-role-*' 'claude-seat-*-rm-role-*' --no-pager`, then
  `systemctl --user stop claude-seat-BENCH-rm-role-<name>-<epoch>.scope; systemctl --user stop rm-role-<name>-<epoch>.service`.
  Every process of the run carries `RM_ROLE_UNIT=rm-role-<name>-<epoch>` in its environment. Proves: 
  `grep -lsz '^RM_ROLE_UNIT=rm-role-<name>-<epoch>$' /proc/[0-9]*/environ` prints nothing (if it prints `/proc/<pid>/environ`
  lines, `kill <pid>` each, then `kill -9` any left after 10 s). The Dispatcher keeps the run busy (it launches no other run of
  that role) until the unit and the scope are both inactive AND that scan finds none; while it cannot tell, it alarms
  `role:<name>:overtime` / `termination UNCONFIRMED` and stops again (KILL from the third try) (review dispatcher-full #1).
- **Other roles' off files** (not in wave 1; for completeness): `.../arbiter/ARBITER_OFF`, `.../auditor/AUDITOR_OFF`, `.../producer/PRODUCER_OFF`, `.../innovator/INNOVATOR_OFF` under `/mnt/d/ClaudeWork/rimmandrake/`.
- **Both roles via the schedule** (a role switched off is still supervised; stop-runs first if its run must end now)**:** set the two `"enabled": true` back to `false` in `src/RimMandrake/rimflow/dispatcher_schedule.json`, `./publish -m "Dispatcher wave 1 rollback: roles off" src/RimMandrake/rimflow/dispatcher_schedule.json`, check step 16's command shows False.
- **Wakes back to dry-run** (after the live-runs step above printed ALL ENDED)**:** `sed -i 's#dispatcher.py tick --apply$#dispatcher.py tick#' ~/.config/systemd/user/rm-dispatcher.service && systemctl --user daemon-reload`; proves
  `dispatcher.py status` shows `"apply": false` after the next tick. Fully off (also only after ALL ENDED): `systemctl --user disable --now rm-dispatcher.timer`.
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

## 9. Wave 2 setup (Arbiter ADVISORY, Fri 2026-10-30): before the Arbiter's `"enabled": true`

Wave 2 turns on the Arbiter, advisory only. Its pre_launch reads the Auditor's audit record, and the Auditor stays off, so nothing
else creates that file. Run these from `$B`, in order, and stop at the first failure. None of them enables anything.

1. **Audit record (AUDITOR_BUILD_AUDITS_FILE):** `python3 src/RimMandrake/rimflow/audits.py ensure`.
   - It creates an empty `D:\ClaudeWork\rimmandrake\auditor\audits.jsonl` if the file is absent. Empty means no audits yet.
   - It never truncates an existing file, and it validates every line against `src/RimMandrake/rimflow/audits.schema.json`.
   - Expect `... created (0 line(s))` or `... exists (N line(s))` and exit 0. Exit 2 means a torn or schema-breaking line: fix it, do not delete the file.
   - The Auditor's own pre_launch runs the same command, so this step only matters while the Auditor is off.
2. **Tiers dry run:** `python3 src/RimMandrake/rimflow/arbiter_tiers.py` must exit 0.
   - Exit 2 is UNMEASURED, and the Arbiter would never start. Read its stderr.
3. **Pending-work gate (ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK):** `python3 src/RimMandrake/rimflow/arbiter_pending.py`.
   - Before step 5 it must print `HOLD: ... no cutoff stamp` and exit 2. That is the proof that an unstamped Arbiter holds, raising `role:Arbiter:cutoff`, and never judges an undefined window.
   - The pre-enable backlog (826 closes and 489 verify items on 2026-10-27) is not the Arbiter's (ARBITER_DECIDE_BACKLOG_NEVER_DRAINS, BENCH delegated ruling). It goes to the Auditor's risk-ranked sampling and `audit_prescreen.py`'s hard flags. It is never judged in bulk and never dropped.
4. **Isolated evidence:** the Arbiter's pre_launch runs `isolated_evidence.py --run --seat DISPATCHER --since-cutoff --budget-s 900`, then `arbiter_tiers.py --since-cutoff --cap 6`.
   - Both steps have their own budget, `pre_launch_max_s` 1200 s, which is added to the Arbiter's 2700 s. The unit's limit is 3900 s.
   - Evidence that does not fit the 900 s is carried (`D:\ClaudeWork\rimmandrake\isolated_evidence\carried.json`) and runs first next batch.
   - Measured on 2026-10-27: mean 22.3 s per claim, max 171.1 s. Check that the work root has room.
5. **Cutoff stamp, last step before the Arbiter's `"enabled": true`:**
   `python3 src/RimMandrake/rimflow/arbiter_pending.py stamp --by <seat> --why "wave 2 Arbiter advisory enable"`
   - Stamp once. The command refuses (exit 2) if a stamp already exists. The stamp is never moved; to move it, a human deletes the file and records why.
   - Then rerun step 3. It must exit 0 and count only work at or after the stamp. `nothing pending` is the expected first answer.

## 10. Seat restart: enable steps (FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET; built 2026-10-28, shipped DISABLED)

What it is: a fresh FOUNDRY window per ticket.
- The seat's close-out (`infrastructure/agents/FOUNDRY.md`, "A fresh window per ticket") runs `seat_restart.py request`.
- The Dispatcher holds the request through 120 s of grace, then kills that one pid. It holds instead while any of these is true:
  - a helper is alive;
  - the bridge or driver lock is FOUNDRY's;
  - FOUNDRY's last game event is transitional;
  - PAUSE is on;
  - a ring or a recovery is in flight;
  - the owner touched the machine in the last 120 s (20 min for a backstop), or his idle clock is UNMEASURED.
  New input cancels it. Right before the kill it re-reads the session file (status must say `idle`), the transcript, the helpers, the bridge, the owner's idle clock and PAUSE. It signals through a pidfd pinned to the pid, only if that process's /proc start time is the one Claude Code registered for the session (`procStart` in `sessions/<pid>.json`, checked again when the restart is asked for), and confirms the death; a window that survives SIGKILL is never relaunched beside.
- The tile relaunches itself through `seat_loop.sh`, using the profile's own LAUNCH line (`--remote-control 'AGENT FOUNDRY'`) plus a first prompt.
- The restart is verified when the doorbell re-arms for the new session. Each step lands in `$S/journal.jsonl` (`do` = `restart_*`).
- Code: `src/RimMandrake/rimflow/seat_restart.py`, `src/RimMandrake/Utils/seat_loop.sh`; schedule key `seat_restart`.
- Selftest: `src/RimMandrake/rimflow/selftest_seat_restart.py`.

Prerequisites:
- Steps 8-9 are done: FOUNDRY's doorbell arms. A restart is only verified by a re-arm.
- The wakes are live (step 4), so the fresh window receives its ticket.

1. **[MANDRAKE confirms, WRITES]** In `src/RimMandrake/rimflow/dispatcher_schedule.json` set `"seat_restart": {"enabled": true, ...}`. Commit and `./publish`, then pull in both clones.
2. **Dry first.** The live timer already runs `--apply`, so dryness comes from the key: step 1 sets `"seat_restart": {"enabled": true, "dry": true, ...}`. With `dry` true the Dispatcher passes apply=false to the restart path only (`dispatcher.sr_apply`). When FOUNDRY closes a ticket, the request is read and held, and `restart_kill` is journalled in the LIVE journal as `would SIGTERM pid ...`. The restart state then reads `dry`. That state does not fence FOUNDRY's rings, and the same request is not retaken. Check with `grep restart_ $S/journal.jsonl | tail -n 5 | cut -c1-240`. Nothing is killed, consumed or launched.
3. **[MANDRAKE confirms]** Re-install the WT profiles so the FOUNDRY tile runs `seat_loop.sh`: `python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply`. While the key is off the profile line is unchanged, so this step must come after step 1. `restart_seats()` reads the key.
4. **[MANDRAKE: his window]** Close and reopen the FOUNDRY tile once, so it runs under `seat_loop.sh`. Until then a kill has no in-tile relaunch. The Dispatcher then falls back to `launch_fleet.ps1 -Seats FOUNDRY`, which opens a NEW tab and leaves the old one at a shell. That fallback from the systemd timer (WSL interop) is UNMEASURED.
5. Set `"dry": false` (or delete the key), then commit and `./publish`. The timer is already `--apply`. Watch the first live restart:
   - `restart_request` → `restart_kill` (result `killed pid … (SIGTERM)`) → `restart_relaunched` (`in-tile`) → `restart_verified`;
   - the phone lists `AGENT FOUNDRY` again;
   - `cat $S/armed/FOUNDRY.json` shows the NEW session_id.
6. **Rollback:** set `"enabled": false`. A pending restart is released at once (`config()` returns nothing). A restart claimed or killed in the last 17 min stays fenced from the Dispatcher's ring and recover, so a recovery cannot race its in-tile relaunch. A killed window that did not come back is relaunched with `wt.exe -w new -p "AGENT FOUNDRY"`.

Known limits (lessons filed 2026-10-28):
- The backstop (context ≥ 110k tokens, idle 30 min, no helper) only starts when the last turn ended normally. A window that was `/clear`ed and never ran a turn reads "not quiet", fails after 3 ticks and alarms; it is never killed.
- A fallback-launched window has no first prompt, so it arms only after its first turn.
- Owner presence is the machine's last-input clock. A draft typed on the phone over Remote Control is invisible to it until sent.
- A background Bash job of the window (`run_in_background`) is invisible: the close-out rule in FOUNDRY.md forbids one.
- Between the kill-time re-read and the signal there is no barrier (a few milliseconds: a /proc read, the killed-record write and the pidfd open): input landing exactly there is lost with the window.
- A second request written in the instant between the Dispatcher's read and its take of the first is taken unread: that ticket's restart simply does not happen (nothing is killed); the backstop or the next ticket's request covers it.
- A relaunch whose claimant (tile or fallback) dies or stalls before launching is not retried: it fails after 2 min with an alarm, and the owner relaunches the tile. A tile cannot claim after that deadline; a claimant stalled past it could still launch late (the Dispatcher's own recovery waits 10 min of a dead seat, so a double window needs a stall that long).
- The transcript is read from its last 4 MB; the game hold uses FOUNDRY's last `game` event within 1 h and is not re-read at the kill.
- GPT review of the build: `D:\ClaudeWork\rimmandrake\foundry_fresh\gpt\review.md` (7 HIGH, all fixed red-first); confirmation rounds `review2.md` to `review8.md` in the same folder.
- CONDUCTOR uses the same mechanism (conductor_briefing Part B): add `"CONDUCTOR": {...}` under `seat_restart.seats` once its seat and tile exist.
