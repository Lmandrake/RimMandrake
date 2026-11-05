#!/usr/bin/env python3
"""selftest_ops_lives: ops_lives.py (the register of lives, operations_metronome_strategy §4 / §8 step 3) on fixture
stores written to a temp dir, never the live ones: each ending and cause rule, planned exits never counted as deaths,
dead-alarm and helper_lost repeats folded, oom kills de-duplicated up the cgroup tree, an oom in a life's own commands
named as the probable cause of its later death, wanted states from the schedule, a blind source said, and the
one-generation check. Each case is a mutant a broken rule would let through."""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_lives as ol  # noqa: E402

FAILS = []
NOW = ol.parse_ts("2026-11-03T12:00:00Z")


def ok(cond, name, info=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (" -- " + str(info)) if not cond and info else ""))
    if not cond:
        FAILS.append(name)


def short(item):
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")


ITEM_LOST, ITEM_FULL, ITEM_DONE, ITEM_ACC, ITEM_STALE, ITEM_OOM = (
    "A_LOST", "B_FULL", "C_DONE", "D_ACCOUNT", "E_STALE", "F_OOMED")

DISPATCH = [
    # FOUNDRY dies once at 10:00 (alarmed three times as the same dead window), then again at 11:30
    {"at": "2026-11-03T10:11:00Z", "do": "alarm", "kind": "dead:FOUNDRY", "why": "FOUNDRY has had no session for 660 s (recovery off)"},
    {"at": "2026-11-03T10:13:00Z", "do": "alarm", "kind": "dead:FOUNDRY", "why": "FOUNDRY has had no session for 780 s (recovery off)", "note": False},
    {"at": "2026-11-03T10:31:00Z", "do": "alarm", "kind": "dead:FOUNDRY", "why": "FOUNDRY has had no session for 1860 s (recovery off)", "note": False},
    {"at": "2026-11-03T11:41:00Z", "do": "alarm", "kind": "dead:FOUNDRY", "why": "FOUNDRY has had no session for 660 s (recovery off)"},
    # a planned restart is never a death
    {"at": "2026-11-03T09:00:00Z", "do": "restart_kill", "seat": "BENCH", "result": "killed pid 1 (SIGTERM)"},
    # windows: a crash with 2 helpers mid-work (alarmed twice), a /clear (planned), a reboot
    {"at": "2026-11-03T08:05:00Z", "do": "alarm", "kind": "helper_lost:aaaa1111", "why": "window aaaa1111 of BENCH ended 2026-11-03T08:00:00Z (the transcript just stops: a quit or a crash): 2 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    {"at": "2026-11-03T09:05:00Z", "do": "alarm", "kind": "helper_lost:aaaa1111", "why": "window aaaa1111 of BENCH ended 2026-11-03T08:00:00Z (the transcript just stops: a quit or a crash): 2 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    {"at": "2026-11-03T08:06:00Z", "do": "alarm", "kind": "helper_lost:bbbb2222", "why": "window bbbb2222 of BENCH ended 2026-11-03T07:00:00Z (/clear): 0 helper(s) died mid-work, 0 report(s) unread, 1 background command(s) with no reader."},
    {"at": "2026-11-03T08:07:00Z", "do": "alarm", "kind": "helper_lost:cccc3333", "why": "window cccc3333 of BENCH ended 2026-11-03T06:00:00Z (before the last boot: the restart, or a quit or crash earlier): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # role runs: one finished, one failed with nothing spent, one stopped over its limit
    {"at": "2026-11-03T07:00:00Z", "do": "role_launch", "role": "Operations", "unit": "rm-role-operations-1"},
    {"at": "2026-11-03T07:05:00Z", "do": "role_done", "role": "Operations", "unit": "rm-role-operations-1", "blind": {"outcome": "completed"}, "why": "done: 300000 weighted tokens, success"},
    # a run of a role the schedule has disabled: its row says the schedule wants that role stopped
    {"at": "2026-11-03T07:06:00Z", "do": "role_launch", "role": "Auditor", "unit": "rm-role-auditor-off"},
    {"at": "2026-11-03T07:09:00Z", "do": "role_done", "role": "Auditor", "unit": "rm-role-auditor-off", "blind": {"outcome": "completed"}, "why": "done: 1000 weighted tokens, success"},
    {"at": "2026-11-03T07:10:00Z", "do": "role_done", "role": "Producer", "unit": "rm-role-producer-2", "blind": {"outcome": "failed"}, "why": "Producer event run rm-role-producer-2 failed: 0 weighted tokens of a 800000 budget (raw 0), model ?, success"},
    {"at": "2026-11-03T07:20:00Z", "do": "role_stop", "role": "Auditor", "unit": "rm-role-auditor-3", "why": "Auditor run rm-role-auditor-3 still unit inactive but scope x active after 2900 s (run_max_s 2700): stop #1"},
    # a timer repaired twice, its alarm naming the first failure (already counted); another with only an alarm
    {"at": "2026-11-03T04:22:10Z", "do": "unit_repair", "unit": "rm-scratch-reap.service", "how": "start", "why": "rm-scratch-reap.service failed: restart (1/2 today)"},
    {"at": "2026-11-03T04:53:20Z", "do": "unit_repair", "unit": "rm-scratch-reap.service", "how": "start", "why": "rm-scratch-reap.service failed: restart (2/2 today)"},
    {"at": "2026-11-03T05:24:07Z", "do": "alarm", "kind": "timer:rm-scratch-reap.service", "why": "rm-scratch-reap.service first failed 2026-11-03T04:22:10Z; 2 automatic repairs today did not hold"},
    {"at": "2026-11-03T05:30:00Z", "do": "alarm", "kind": "timer:rm-example.service", "why": "rm-example.service first failed 2026-11-03T05:29:00Z; no safe automatic repair for it"},
    {"at": "2026-11-03T05:40:00Z", "do": "unit_repair", "unit": "rm-harness-77-2.scope", "how": "clear", "why": "rm-harness-77-2.scope failed: clear (1/2 today)"},
    # a restart: the killed window's receipt is planned, and a failed relaunch is a death with that cause
    {"at": "2026-11-03T03:00:00Z", "do": "restart_kill", "seat": "BENCH", "result": "killed pid 2 (SIGTERM)"},
    {"at": "2026-11-03T03:30:00Z", "do": "alarm", "kind": "helper_lost:dddd4444", "why": "window dddd4444 of BENCH ended 2026-11-03T03:00:30Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # its replacement crashing two minutes later is a crash: one restart ends one window
    {"at": "2026-11-03T03:35:00Z", "do": "alarm", "kind": "helper_lost:gggg7777", "why": "window gggg7777 of BENCH ended 2026-11-03T03:02:30Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # two distinct failures of one timer six minutes apart, each alarmed with no repair: two deaths
    {"at": "2026-11-03T06:10:00Z", "do": "alarm", "kind": "timer:rm-twice.service", "why": "rm-twice.service first failed 2026-11-03T06:00:00Z; no safe automatic repair for it"},
    {"at": "2026-11-03T06:20:00Z", "do": "alarm", "kind": "timer:rm-twice.service", "why": "rm-twice.service first failed 2026-11-03T06:06:00Z; no safe automatic repair for it"},
    {"at": "2026-11-03T03:12:00Z", "do": "alarm", "kind": "dead:BENCH", "why": "BENCH has had no session for 660 s (recovery off)"},
    # a run launched before the window and still open; one launched and ended before it: absent
    {"at": "2026-10-10T07:00:00Z", "do": "role_launch", "role": "Operations", "unit": "rm-role-operations-old"},
    {"at": "2026-10-10T07:00:00Z", "do": "role_launch", "role": "Operations", "unit": "rm-role-operations-gone"},
    {"at": "2026-10-10T07:30:00Z", "do": "role_done", "role": "Operations", "unit": "rm-role-operations-gone", "blind": {"outcome": "completed"}, "why": "done"},
    # a deliberate stop, then the run's failed receipt: planned, not a death
    {"at": "2026-11-03T06:00:00Z", "do": "role_stop", "role": "Producer", "unit": "rm-role-producer-9", "why": "stopped: the owner switched it off"},
    {"at": "2026-11-03T06:01:00Z", "do": "role_done", "role": "Producer", "unit": "rm-role-producer-9", "blind": {"outcome": "failed"}, "why": "Producer run failed: 100 weighted tokens"},
    # a scope repaired after memwatch saw it killed: one death, of memory
    {"at": "2026-11-03T09:10:00Z", "do": "unit_repair", "unit": "rm-harness-88-1.scope", "how": "clear", "why": "rm-harness-88-1.scope failed: clear (1/2 today)"},
    # stopped at its limit before the window; its failed receipt lands inside it: not a death in the window
    {"at": "2026-10-19T23:59:00Z", "do": "role_stop", "role": "Auditor", "unit": "rm-role-auditor-early", "why": "Auditor run still unit inactive but scope x active after 2900 s (run_max_s 2700): stop #1"},
    {"at": "2026-10-20T12:30:00Z", "do": "role_done", "role": "Auditor", "unit": "rm-role-auditor-early", "blind": {"outcome": "failed"}, "why": "Auditor run failed: 9 weighted tokens"},
    # a role scope repaired after memwatch killed it: one death, under the role run's name
    {"at": "2026-11-03T09:20:00Z", "do": "unit_repair", "unit": "claude-seat-BENCH-rm-role-arbiter-55.scope", "how": "clear", "why": "claude-seat-BENCH-rm-role-arbiter-55.scope failed: clear (1/2 today)"},
    # a role scope killed, its failed receipt an hour later: one death at the kill
    {"at": "2026-11-03T10:20:00Z", "do": "role_done", "role": "Arbiter", "unit": "rm-role-arbiter-55", "blind": {"outcome": "failed"}, "why": "Arbiter run failed: 50 weighted tokens"},
    # two terminal records at one instant: the first in journal order wins
    {"at": "2026-11-03T06:30:00Z", "do": "role_done", "role": "Producer", "unit": "rm-role-producer-same", "blind": {"outcome": "completed"}, "why": "done"},
    {"at": "2026-11-03T06:30:00Z", "do": "role_done", "role": "Producer", "unit": "rm-role-producer-same", "blind": {"outcome": "failed"}, "why": "failed: 1 weighted tokens"},
    # a window alarmed again with a larger helper count: the count rises, the death does not
    {"at": "2026-11-03T08:10:00Z", "do": "alarm", "kind": "helper_lost:aaaa1111", "note": False, "why": "window aaaa1111 of BENCH ended 2026-11-03T08:00:00Z (the transcript just stops: a quit or a crash): 3 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # a service killed for memory and repaired a few minutes later: one death
    {"at": "2026-11-03T09:33:00Z", "do": "unit_repair", "unit": "rm-ops-watch.service", "how": "start", "why": "rm-ops-watch.service failed: restart (1/2 today)"},
    {"at": "2026-11-03T09:40:00Z", "do": "unit_repair", "unit": "rm-ops-watch.service", "how": "start", "why": "rm-ops-watch.service failed: restart (2/2 today)"},
    # a failure just before the window, repaired just inside it: before the window
    {"at": "2026-10-20T12:03:00Z", "do": "unit_repair", "unit": "rm-edge.service", "how": "start", "why": "rm-edge.service failed: restart (1/2 today)"},
    {"at": "2026-10-20T12:30:00Z", "do": "alarm", "kind": "timer:rm-edge.service", "why": "rm-edge.service first failed 2026-10-20T11:58:00Z; 1 automatic repair today did not hold"},
    # failure 10:00, kill seen 10:01, repair 10:03, alarm naming the failure: one death at 10:00, of memory
    {"at": "2026-11-03T10:03:00Z", "do": "unit_repair", "unit": "rm-three.service", "how": "start", "why": "rm-three.service failed: restart (1/2 today)"},
    {"at": "2026-11-03T10:20:00Z", "do": "alarm", "kind": "timer:rm-three.service", "why": "rm-three.service first failed 2026-11-03T10:00:00Z; 1 automatic repair today did not hold"},
    # a crash four minutes before a restart of the same seat: a crash
    {"at": "2026-11-03T04:30:00Z", "do": "restart_kill", "seat": "BENCH", "result": "killed pid 4 (SIGTERM)"},
    {"at": "2026-11-03T04:40:00Z", "do": "alarm", "kind": "helper_lost:ffff6666", "why": "window ffff6666 of BENCH ended 2026-11-03T04:26:00Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # an alarm written before its repair: one failure
    {"at": "2026-11-03T09:55:00Z", "do": "alarm", "kind": "timer:rm-early.service", "why": "rm-early.service first failed 2026-11-03T09:54:00Z; no safe automatic repair for it"},
    {"at": "2026-11-03T09:56:00Z", "do": "unit_repair", "unit": "rm-early.service", "how": "start", "why": "rm-early.service failed: restart (1/2 today)"},
    # a service killed for memory with no repair on record: its alarm (first failed a minute before the kill stamp) and
    # a throttled repeat of that alarm are the same death
    {"at": "2026-11-03T11:45:00Z", "do": "alarm", "kind": "timer:rm-alarmoom.service", "why": "rm-alarmoom.service first failed 2026-11-03T11:39:00Z; no safe automatic repair for it"},
    {"at": "2026-11-03T11:50:00Z", "do": "alarm", "kind": "timer:rm-alarmoom.service", "note": False, "why": "rm-alarmoom.service first failed 2026-11-03T11:39:00Z; no safe automatic repair for it"},
    # a failure seen only in a throttled alarm is still a death
    {"at": "2026-11-03T08:30:00Z", "do": "alarm", "kind": "timer:rm-quiet.service", "note": False, "why": "rm-quiet.service first failed 2026-11-03T08:29:00Z; no safe automatic repair for it"},
    # a role run launched long ago and killed by memory with no receipt: dead, not open, and gone from the window
    {"at": "2026-10-05T07:00:00Z", "do": "role_launch", "role": "Operations", "unit": "rm-role-operations-7777"},
    # a kill and its repair in the same second: one death whatever the order
    {"at": "2026-11-03T09:50:00Z", "do": "unit_repair", "unit": "rm-pulse.service", "how": "start", "why": "rm-pulse.service failed: restart (1/2 today)"},
    # a role scope killed just before the window, its repair inside it: before the window, not counted
    {"at": "2026-10-20T12:10:00Z", "do": "unit_repair", "unit": "claude-seat-BENCH-rm-role-auditor-4242.scope", "how": "clear", "why": "claude-seat-BENCH-rm-role-auditor-4242.scope failed: clear (1/2 today)"},
    # a run stopped twice dies once
    {"at": "2026-11-03T07:23:00Z", "do": "role_done", "role": "Auditor", "unit": "rm-role-auditor-3", "blind": {"outcome": "failed"}, "why": "Auditor run rm-role-auditor-3 failed: 9000 weighted tokens"},
    # a restart after --now cannot make an earlier crash planned
    {"at": "2026-11-03T12:30:00Z", "do": "restart_kill", "seat": "BENCH", "result": "killed pid 3 (SIGTERM)"},
    # a crash two days back: counted in the window, not in the last 24 h
    {"at": "2026-11-01T10:05:00Z", "do": "alarm", "kind": "helper_lost:iiii9999", "why": "window iiii9999 of BENCH ended 2026-11-01T10:00:00Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    # a restart 10 s after --now would plan this window (it ends within the skew): only the --now cut keeps it a crash
    {"at": "2026-11-03T12:00:10Z", "do": "restart_kill", "seat": "BENCH", "result": "killed pid 5 (SIGTERM)"},
    {"at": "2026-11-03T11:59:55Z", "do": "alarm", "kind": "helper_lost:hhhh8888", "why": "window hhhh8888 of BENCH ended 2026-11-03T11:59:50Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    {"at": "2026-11-03T11:59:00Z", "do": "alarm", "kind": "helper_lost:eeee5555", "why": "window eeee5555 of BENCH ended 2026-11-03T11:58:00Z (the transcript just stops: a quit or a crash): 0 helper(s) died mid-work, 0 report(s) unread, 0 background command(s) with no reader."},
    {"at": "2026-11-03T07:22:00Z", "do": "role_stop", "role": "Auditor", "unit": "rm-role-auditor-3", "why": "Auditor run rm-role-auditor-3 still unit inactive but scope x active after 3020 s (run_max_s 2700): stop #2"},
    # a fresh alarm reporting an old death, and a record from the future: neither counted
    {"at": "2026-11-03T06:00:00Z", "do": "alarm", "kind": "dead:OLDSEAT", "why": "OLDSEAT has had no session for 2000000 s (recovery off)"},
    {"at": "2026-11-04T06:00:00Z", "do": "alarm", "kind": "dead:LATER", "why": "LATER has had no session for 700 s (recovery off)"},
    # outside the window: never counted
    {"at": "2026-10-01T00:00:00Z", "do": "alarm", "kind": "dead:BENCH", "why": "BENCH has had no session for 700 s (recovery off)"},
    "{not json",
]

WORK = "claude-seats.slice/claude-seat-BENCH-rm-relentless-work-%s-g2.scope" % short(ITEM_OOM)
MEMWATCH = [
    # one kill, seen in the leaf and both parents at the same ts: one death, of the commands, not the window
    {"ts": "2026-11-03T02:00:00-0800", "kind": "oom_kill", "cgroup": WORK + "/claude-code-bash", "delta": 1},
    {"ts": "2026-11-03T02:00:00-0800", "kind": "oom_kill", "cgroup": WORK, "delta": 1},
    {"ts": "2026-11-03T02:00:00-0800", "kind": "oom_kill", "cgroup": "claude-seats.slice", "delta": 1},
    # a slice-level kill alone: a death of that process group
    {"ts": "2026-11-03T03:00:00-0800", "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 3},
    {"ts": "2026-11-03T03:00:00-0800", "kind": "max", "cgroup": "rm-harness.slice", "delta": 40},
    # a parent with more kills than its child explains keeps the rest
    {"ts": "2026-11-03T03:30:00-0800", "kind": "oom_kill", "cgroup": "box.slice", "delta": 3},
    {"ts": "2026-11-03T03:30:00-0800", "kind": "oom_kill", "cgroup": "box.slice/a.scope/claude-code-bash", "delta": 1},
    {"ts": "2026-11-03T03:30:00-0800", "kind": "oom_kill", "cgroup": "box.slice/b.scope/claude-code-bash", "delta": 1},
    # the scope itself killed, then its record says lost: one death, of memory
    {"ts": "2026-11-03T01:00:00-0800", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-rm-relentless-work-%s-g1.scope" % short("G_SCOPEOOM"), "delta": 2},
    # a retired seat's window killed: wanted from the schedule
    {"ts": "2026-11-03T01:10:00-0800", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-FOUNDRY-999.scope", "delta": 1},
    {"ts": "2026-11-03T01:05:00-0800", "kind": "oom_kill", "cgroup": "rm-harness.slice/rm-harness-88-1.scope", "delta": 1},
    {"ts": "2026-11-03T01:15:00-0800", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-rm-role-arbiter-55.scope", "delta": 1},
    {"ts": "2026-11-03T01:30:00-0800", "kind": "oom_kill", "cgroup": "user.slice/rm-ops-watch.service", "delta": 1},
    {"ts": "2026-10-20T04:55:00-0700", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-rm-role-auditor-4242.scope", "delta": 1},
    {"ts": "2026-11-03T01:50:00-0800", "kind": "oom_kill", "cgroup": "user.slice/rm-pulse.service", "delta": 1},
    {"ts": "2026-11-03T02:01:00-0800", "kind": "oom_kill", "cgroup": "user.slice/rm-three.service", "delta": 1},
    {"ts": "2026-11-03T03:40:00-0800", "kind": "oom_kill", "cgroup": "user.slice/rm-alarmoom.service", "delta": 1},
    # two separate kills in one life: two victims, one death
    {"ts": "2026-11-03T01:20:00-0800", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-rm-role-arbiter-55.scope", "delta": 1},
    {"ts": "2026-10-05T01:00:00-0700", "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-rm-role-operations-7777.scope", "delta": 1},
    # from the future: not counted
    {"ts": "2026-11-05T01:10:00-0800", "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1},
    # memwatch also writes oom_group_kill (memory.oom.group): a death of memory like any other kill
    {"ts": "2026-11-03T02:40:00-0800", "kind": "oom_group_kill", "cgroup": "user.slice/rm-groupkill.service", "delta": 1},
]

ATTEMPTS = {
    ITEM_LOST: [{"at": "2026-11-03T09:00:00Z", "gen": 1, "approach": "build", "start": True},
                {"at": "2026-11-03T09:40:00Z", "gen": 1, "end": "worker_lost", "detail": "unit x ended with no receipt"}],
    ITEM_FULL: [{"at": "2026-11-03T09:00:00Z", "gen": 3, "approach": "build", "start": True},
                {"at": "2026-11-03T11:00:00Z", "gen": 3, "end": "worker_full", "detail": "hit run_max_s"}],
    ITEM_DONE: [{"at": "2026-11-03T09:00:00Z", "gen": 1, "approach": "build", "start": True},
                {"at": "2026-11-03T09:30:00Z", "gen": 1, "end": "finish", "sha": "abc"},
                {"at": "2026-11-03T09:50:00Z", "end": "done", "sha": "abc"},
                {"at": "2026-11-03T10:00:00Z", "gen": 2, "end": "owner_call", "detail": "a snag: his call"}],
    ITEM_ACC: [{"at": "2026-11-03T10:00:00Z", "gen": 1, "end": "account_lost",
                "detail": "account change-over at 2026-11-03T02:54:23-08:00 closed every Claude process"},
               {"at": "2026-11-03T10:05:00Z", "gen": 2, "end": "launch_fail"},
               {"at": "2026-11-03T10:10:00Z", "gen": 3, "end": "checker_lost", "detail": "2 checkers gave no verdict"}],
    ITEM_STALE: [{"at": "2026-11-03T10:00:00Z", "gen": 1, "end": "worker_stale", "detail": "silent for 700 s"}],
    ITEM_OOM: [{"at": "2026-11-03T10:15:00Z", "gen": 2, "end": "worker_lost", "detail": "unit ended with no receipt"}],
    "G_SCOPEOOM": [{"at": "2026-11-03T09:05:00Z", "gen": 1, "end": "worker_lost", "detail": "unit ended with no receipt"}],
    "H_OPEN": [{"at": "2026-11-03T11:00:00Z", "gen": 4, "approach": "build", "start": True},
               {"at": "2026-11-03T13:00:00Z", "gen": 4, "end": "worker_lost", "detail": "after --now"}],
    "I_LONG": [{"at": "2026-10-01T00:00:00Z", "gen": 1, "approach": "build", "start": True}],
}

SCHEDULE = {"seats": {"BENCH": {"enabled": True}, "OLDSEAT": {"enabled": False}},
            "roles": [{"name": "Operations", "enabled": True}, {"name": "Auditor", "enabled": False}]}


def fixture(root):
    disp = os.path.join(root, "dispatcher")
    write_jsonl(os.path.join(disp, "journal.jsonl"), DISPATCH)
    mem = os.path.join(root, "memwatch", "events.jsonl")
    write_jsonl(mem, MEMWATCH)
    rel = os.path.join(root, "relentless")
    for item, rows in ATTEMPTS.items():
        write_jsonl(os.path.join(rel, "store", "items", item, "attempts.jsonl"), rows)
    sch = os.path.join(root, "schedule.json")
    with open(sch, "w") as f:
        json.dump(SCHEDULE, f)
    return disp, mem, rel, sch


def deaths_of(reg, tid):
    return [d for d in reg["deaths"] if d["thing"] == tid]


def thing(reg, tid):
    return next((t for t in reg["things"] if t["id"] == tid), None)


def main():
    root = tempfile.mkdtemp(prefix="ops_lives_selftest_")
    disp, mem, rel, sch = fixture(root)
    reg = ol.build(NOW, 14, disp, mem, rel, sch)

    # every ending is on the fixed list
    ok(all(d["ending"] in ol.ENDINGS for d in reg["deaths"]), "endings_fixed_list")

    # seats
    f = deaths_of(reg, "seat:FOUNDRY")
    ok(len(f) == 2, "dead_alarm_repeats_fold_to_one_death_each", [d["at"] for d in f])
    ok(f and f[0]["at"] == "2026-11-03T10:00:00Z", "dead_time_is_alarm_minus_silence", f and f[0]["at"])
    ok(thing(reg, "seat:FOUNDRY")["wanted"] == "stopped", "seat_absent_from_schedule_is_stopped")
    ok(thing(reg, "seat:BENCH")["wanted"] == "running", "enabled_seat_is_running")
    ok(thing(reg, "seat:OLDSEAT")["wanted"] == "stopped", "disabled_seat_is_stopped")
    b = deaths_of(reg, "seat:BENCH")
    ok(len(b) == 1 and b[0]["cause"] == "a planned restart did not relaunch it", "failed_relaunch_is_a_death_with_cause", b)
    ok(not deaths_of(reg, "window:BENCH:dddd4444") and any(p["thing"] == "window:BENCH:dddd4444"
       and p["how"] == "planned seat restart" for p in reg["planned"]), "restart_killed_window_is_planned")
    ok(not deaths_of(reg, "seat:OLDSEAT"), "fresh_alarm_of_old_death_outside_window")
    ok(not deaths_of(reg, "seat:LATER"), "future_record_not_counted")
    ok(any(p["thing"] == "seat:BENCH" and "planned seat restart" in p["how"] for p in reg["planned"]),
       "planned_restart_recorded")

    # windows and helpers
    w = deaths_of(reg, "window:BENCH:aaaa1111")
    ok(len(w) == 1 and w[0]["cause"] == ol.UNKNOWN and w[0]["at"] == "2026-11-03T08:00:00Z",
       "crashed_window_one_death_cause_unknown", w)
    h = deaths_of(reg, "helpers:BENCH:aaaa1111")
    ok(len(h) == 1 and h[0].get("count") == 3, "helpers_mid_work_die_with_window_largest_count", h)
    ok(len(deaths_of(reg, "window:BENCH:aaaa1111")) == 1, "repeated_receipt_one_window_death")
    hr = thing(reg, "helpers:BENCH:aaaa1111")
    ok(hr is not None and hr["wanted"] == "running" and hr["kind"] == "helper", "helpers_wanted_running", hr)
    ok(thing(reg, "role:rm-role-producer-2")["wanted"] == "done", "role_run_wanted_done")
    bad = [(t["id"], t["wanted"]) for t in reg["things"] if t["wanted"] not in ("running", "stopped", "done")]
    ok(not bad, "every_thing_wanted_on_the_fixed_list", bad[:5])
    sv = deaths_of(reg, "unit:rm-ops-watch.service")
    ok(len(sv) == 2 and sv[0]["ending"] == "out_of_memory" and sv[0].get("folded") == 2 and sv[1]["ending"] == "unit_failed",
       "service_oom_absorbs_one_repair_only", sv)
    ok(len(deaths_of(reg, "unit:rm-early.service")) == 1, "alarm_before_repair_one_failure")
    ao = deaths_of(reg, "unit:rm-alarmoom.service")
    ok(len(ao) == 1 and ao[0]["ending"] == "out_of_memory" and ao[0]["at"] == "2026-11-03T11:39:00Z",
       "oom_kill_and_unrepaired_alarm_one_death_at_failure", ao)
    q = deaths_of(reg, "unit:rm-quiet.service")
    ok(len(q) == 1 and q[0]["at"] == "2026-11-03T08:29:00Z", "throttled_alarm_still_a_death", q)
    t3 = deaths_of(reg, "unit:rm-three.service")
    ok(len(t3) == 1 and t3[0]["ending"] == "out_of_memory" and t3[0]["at"] == "2026-11-03T10:00:00Z",
       "failure_kill_repair_alarm_one_death_at_failure", t3)
    ok(len(deaths_of(reg, "window:BENCH:ffff6666")) == 1, "crash_before_restart_is_a_crash")
    ok(not deaths_of(reg, "unit:rm-edge.service"), "failure_before_window_repaired_inside_not_counted")
    ok(thing(reg, "role:rm-role-operations-7777") is None, "oom_killed_life_without_receipt_not_open")
    pu = deaths_of(reg, "unit:rm-pulse.service")
    ok(len(pu) == 1 and pu[0]["ending"] == "out_of_memory", "same_second_kill_and_repair_one_death", pu)
    ok(thing(reg, "role:rm-role-auditor-4242") is None and not any("4242" in d["thing"] for d in reg["deaths"]),
       "death_just_before_window_not_renewed_by_late_receipt")
    ok(not deaths_of(reg, "window:BENCH:bbbb2222") and any(p["thing"] == "window:BENCH:bbbb2222" for p in reg["planned"]),
       "cleared_window_is_planned")
    c = deaths_of(reg, "window:BENCH:cccc3333")
    ok(len(c) == 1 and "reboot" in c[0]["cause"], "reboot_window_cause_named", c)

    # role runs
    ok(not deaths_of(reg, "role:rm-role-operations-1"), "finished_role_run_not_a_death")
    p = deaths_of(reg, "role:rm-role-producer-2")
    ok(len(p) == 1 and p[0]["ending"] == "exit_failed" and "never ran" in p[0]["cause"], "failed_role_run_zero_tokens", p)
    a = deaths_of(reg, "role:rm-role-auditor-3")
    ok(len(a) == 1 and a[0]["ending"] == "time_limit" and a[0].get("ran_s") == 2900, "stopped_role_run_dies_once", a)
    ok(thing(reg, "role:rm-role-operations-1")["role_wanted"] == "done", "role_wanted_from_schedule")
    aoff = thing(reg, "role:rm-role-auditor-off")
    ok(aoff is not None and aoff.get("role_wanted") == "stopped", "disabled_role_run_role_wanted_stopped", aoff)
    ok(ol.role_wanted({"roles": [{"name": "Operations", "enabled": True}, {"name": "Auditor", "enabled": False}]})
       == {"Operations": "done", "Auditor": "stopped"}, "role_wanted_enabled_done_disabled_stopped")
    old = thing(reg, "role:rm-role-operations-old")
    ok(old is not None and old.get("open"), "role_run_open_since_before_window_has_row", old)
    ok(thing(reg, "role:rm-role-operations-gone") is None, "role_run_ended_before_window_absent")
    ok(not thing(reg, "role:rm-role-operations-1").get("open"), "finished_role_run_not_open")
    ok(not deaths_of(reg, "role:rm-role-producer-9"), "stopped_role_run_failed_receipt_not_a_death")
    ok(not deaths_of(reg, "role:rm-role-producer-same") and any(p["thing"] == "role:rm-role-producer-same"
       for p in reg["planned"]), "equal_time_terminals_first_in_journal_wins")
    ok(not deaths_of(reg, "role:rm-role-auditor-early"), "receipt_after_pre_window_stop_not_a_death")
    ar = deaths_of(reg, "role:rm-role-arbiter-55")
    ok(len(ar) == 1 and ar[0]["ending"] == "out_of_memory" and ar[0]["at"] == "2026-11-03T09:15:00Z"
       and ar[0].get("folded") == 4 and ar[0].get("count") == 2 and not deaths_of(reg, "unit:claude-seat-BENCH-rm-role-arbiter-55.scope"),
       "role_scope_oom_and_repair_are_one_death", ar)
    hx = deaths_of(reg, "unit:rm-harness-88-1.scope")
    ok(len(hx) == 1 and hx[0]["ending"] == "out_of_memory", "scope_oom_and_repair_are_one_death", hx)

    # timers
    s = deaths_of(reg, "unit:rm-scratch-reap.service")
    ok(len(s) == 2 and all(d["ending"] == "unit_failed" for d in s), "timer_alarm_not_double_counted_with_repair", s)
    ok(len(deaths_of(reg, "unit:rm-example.service")) == 1, "timer_alarm_alone_is_a_death")
    ok(len(deaths_of(reg, "unit:rm-twice.service")) == 2, "distinct_alarmed_failures_stay_distinct",
       deaths_of(reg, "unit:rm-twice.service"))
    ok(len(deaths_of(reg, "window:BENCH:gggg7777")) == 1, "one_restart_plans_one_window_replacement_crash_counts")
    ok(thing(reg, "unit:rm-example.service")["wanted"] == "running", "timer_wanted_running")
    ok(thing(reg, "unit:rm-harness-77-2.scope")["kind"] == "scope", "cleared_scope_is_a_scope_life")

    # relentless
    def rid(kind, item, gen):
        return "relentless:%s:%s:g%d" % (kind, short(item), gen)
    ok([d["ending"] for d in deaths_of(reg, rid("worker", ITEM_LOST, 1))] == ["window_gone"], "worker_lost_window_gone")
    ok([d["ending"] for d in deaths_of(reg, rid("worker", ITEM_FULL, 3))] == ["time_limit"], "worker_full_time_limit")
    ok([d["ending"] for d in deaths_of(reg, rid("worker", ITEM_STALE, 1))] == ["silence"], "worker_stale_silence")
    acc = deaths_of(reg, rid("worker", ITEM_ACC, 1))
    ok(len(acc) == 1 and acc[0]["ending"] == "login_or_quota" and "change-over" in acc[0]["cause"],
       "account_lost_cause_from_detail", acc)
    ok([d["ending"] for d in deaths_of(reg, rid("worker", ITEM_ACC, 2))] == ["launch_failed"], "launch_fail_ending")
    ok([d["ending"] for d in deaths_of(reg, rid("checker", ITEM_ACC, 3))] == ["window_gone"], "checker_lost_is_checker")
    ok(not any(d.get("item") == ITEM_DONE for d in reg["deaths"]), "finish_done_snag_never_deaths")
    ok(sum(1 for p in reg["planned"] if p["thing"].startswith(rid("worker", ITEM_DONE, 1)[:-3])) == 2,
       "finish_and_snag_are_planned")
    ok(not any(t["id"].endswith(":gNone") for t in reg["things"]), "item_level_done_is_no_life")
    op = thing(reg, rid("worker", "H_OPEN", 4))
    ok(op is not None and op.get("open") and not deaths_of(reg, op["id"]), "open_life_has_a_row", op)
    so = deaths_of(reg, rid("worker", "G_SCOPEOOM", 1))
    ok(len(so) == 1 and so[0]["ending"] == "out_of_memory" and so[0].get("count") == 2,
       "scope_oom_and_lost_are_one_death_count_kept", so)
    ok(not deaths_of(reg, op["id"]) if op else False, "future_end_leaves_life_open")
    lg = thing(reg, rid("worker", "I_LONG", 1))
    ok(lg is not None and lg.get("open"), "life_open_since_before_window_has_row", lg)
    ok(len(deaths_of(reg, "window:BENCH:eeee5555")) == 1, "future_restart_does_not_plan_earlier_crash")
    ok(len(deaths_of(reg, "window:BENCH:hhhh8888")) == 1 and not any(p["thing"] == "window:BENCH:hhhh8888"
       for p in reg["planned"]), "restart_after_now_within_skew_does_not_plan_crash")
    ok(thing(reg, rid("worker", ITEM_LOST, 1))["started"] == "2026-11-03T09:00:00Z", "life_start_from_attempts")
    # wanted state per thing: a Relentless life (worker or checker, dead, finished or open) is meant to run to done
    for tid, label in ((rid("worker", ITEM_LOST, 1), "lost"), (rid("checker", ITEM_ACC, 3), "checker"),
                       (rid("worker", ITEM_FULL, 3), "full"), (rid("worker", ITEM_DONE, 1), "finished"),
                       (rid("worker", "H_OPEN", 4), "open"), (rid("worker", "I_LONG", 1), "long_open")):
        row = thing(reg, tid)
        ok(row is not None and row["wanted"] == "done", "relentless_life_wanted_done_" + label, row)

    # memwatch
    oom = [d for d in reg["deaths"] if d["ending"] == "out_of_memory"]   # 12 + rm-alarmoom (its kill and its alarm: one) + rm-groupkill
    ok(len(oom) == 14, "oom_counted_once_at_the_leaf", [d["thing"] for d in oom])
    gk = deaths_of(reg, "unit:rm-groupkill.service")
    ok(len(gk) == 1 and gk[0]["ending"] == "out_of_memory" and gk[0]["at"] == "2026-11-03T10:40:00Z",
       "oom_group_kill_is_an_out_of_memory_death", gk)
    box = deaths_of(reg, "cgroup:box.slice")
    ok(len(box) == 1 and box[0]["count"] == 1, "parent_keeps_unexplained_kills", box)
    ok(deaths_of(reg, "unit:a.scope/claude-code-bash") and deaths_of(reg, "unit:b.scope/claude-code-bash"),
       "unrecognized_scopes_stay_apart")
    ok(thing(reg, "window:FOUNDRY:scope-999")["wanted"] == "stopped", "oom_window_wanted_from_schedule")
    wid = rid("worker", ITEM_OOM, 2)
    ok(deaths_of(reg, wid + "/claude-code-bash") and deaths_of(reg, wid + "/claude-code-bash")[0]["ending"]
       == "out_of_memory", "bash_child_oom_is_a_command_death")
    lost = deaths_of(reg, wid)
    ok(len(lost) == 1 and lost[0]["ending"] == "window_gone" and lost[0]["cause"].startswith("probably memory"),
       "oom_in_commands_is_probable_cause_of_later_death", lost)
    hs = deaths_of(reg, "cgroup:rm-harness.slice")
    ok(len(hs) == 1 and hs[0]["count"] == 3, "slice_oom_is_process_group_death_with_count", hs)
    ok(not deaths_of(reg, "cgroup:claude-seats.slice"), "parent_slice_oom_not_double_counted")

    # readings
    r = reg["readings"]
    ok(r["deaths"] == len(reg["deaths"]) and r["cause_unknown"] == sum(d["cause"] == "unknown" for d in reg["deaths"]),
       "readings_agree_with_lines")
    ok(r["victims"] == sum(d.get("count") or 1 for d in reg["deaths"]) and r["victims"] > r["deaths"], "victims_counted")
    ok(r["cause_unknown_share"] is not None and 0 < r["cause_unknown_share"] < 1, "unknown_share_is_a_reading")
    ok(any("torn" in b for b in reg["blind"]), "torn_line_said_not_fatal")
    ok(thing(reg, "seat:FOUNDRY")["deaths_24h"] == 2, "deaths_24h_per_thing")
    old_w = thing(reg, "window:BENCH:iiii9999")
    ok(len(deaths_of(reg, "window:BENCH:iiii9999")) == 1 and old_w is not None and old_w["deaths_24h"] == 0
       and old_w["deaths"] == 1, "death_older_than_24h_not_in_deaths_24h", old_w)
    ok(r["deaths_24h"] == r["deaths"] - 1, "readings_deaths_24h_leaves_out_the_old_death", (r["deaths_24h"], r["deaths"]))
    reg3 = ol.build(NOW, 14, disp, mem, rel, os.path.join(root, "nope.json"))
    rows = [t for t in reg3["things"] if t["kind"] in ("seat", "window")]
    ok(rows and all(t["wanted"] == "UNMEASURED" for t in rows) and any("schedule" in b for b in reg3["blind"]),
       "no_schedule_wanted_unmeasured", rows[:2])

    # a missing store is blind, never "no deaths"
    reg2 = ol.build(NOW, 14, os.path.join(root, "nope"), os.path.join(root, "nope.jsonl"), os.path.join(root, "nope"),
                    os.path.join(root, "nope.json"))
    ok(len(reg2["blind"]) >= 4 and reg2["readings"]["cause_unknown_share"] is None, "missing_stores_are_blind",
       reg2["blind"])

    # one generation, and the check
    out = os.path.join(root, "out")
    ol.publish(reg, out)
    code, msg = ol.check(out, NOW + 60, 120)
    ok(code == 0, "check_fresh_generation", msg)
    code, msg = ol.check(out, NOW + 3 * 3600, 120)
    ok(code == 1 and "old" in msg, "check_refuses_stale", msg)
    with open(os.path.join(out, "lives.md"), "w") as f:
        f.write("# another generation\n")
    code, msg = ol.check(out, NOW + 60, 120)
    ok(code == 1 and "generation" in msg, "check_refuses_mixed_generation", msg)
    t_, pid_ = reg["generation"].split("-")
    other = dict(reg, generation="%d-%s" % (int(t_) + 1, pid_))     # not a substring of the real id
    with open(os.path.join(out, "lives.md"), "w") as f:
        f.write(ol.render_md(other))
    code, msg = ol.check(out, NOW + 60, 120)
    ok(code == 1 and "generation" in msg, "check_refuses_md_of_another_generation_id", msg)
    ok(not [n for n in os.listdir(out) if n.startswith(".")], "no_temp_files_left")
    md = ol.render_md(reg)
    ok("seat:FOUNDRY" in md and "Cause unknown" in md, "md_lists_dead_things")

    print("RESULT: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
