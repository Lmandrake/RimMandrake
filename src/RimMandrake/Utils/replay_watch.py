#!/usr/bin/env python3
"""replay_watch: the unattended supervisor of the arena replay arms (ARENA_WATCHDOG_BUILD_UNATTENDED_REPLAY). No AI.

Why: every arm stop on 2026-10-31 waited on a person noticing, and the replay runs overnight to the stop line. It lives
outside Utils/arena/ on purpose: the harness is frozen, this only reads it.

Each tick (rm-replay-watch.timer, every 3 min, from the dispatch clone) it reads, per arm: the unit
rm-arena-replay-<arm>.service, logs/<arm>.log, ctl/<arm>/runner.json, ctl/<arm>/STOP, launcher.log, the Dispatcher's
login state. It writes one state per arm:

  WAITING   no unit, an inactive unit, or a failed unit that a later FIXED/BLOCKED launcher line answered: relaunch owed,
            not a failure. No action. Holds while a person is working; this is what lets it be armed before a relaunch.
  RUNNING   the unit is up. HOLD_CAPACITY: the runner is waiting for capacity, its own loop.
  DONE      runner.json holds every task. STOPPED: <ctl>/<arm>/STOP stands, the operator's; left alone and never removed.
  LOGIN     the login is dead, or the arm died of it. login_watch owns that: no restart, no alarm. The arm is restarted
            once the login is back, by the same one-restart rule.
  RESTARTED died (signal, OOM, a machine restart, or an ERROR of a machine exception, CRASHES): one restart by the
            documented route, `systemctl --user reset-failed <unit>` + `launch_arm.sh <arm>`; the runner resumes from
            runner.json. Written to launcher.log as WATCH RESTART.
  PAGED     every other stop: the fail-loud gate or judge stops, a red start, any harness ERROR, exit 2 (start gate
            refused), an exit with no words. A restart would retry a stop that must be read, and a runner start
            deletes a loop's task STOP, so the watchdog never restarts these.
  TWICE_DEAD died again with the one restart spent, or the restart failed. STALLED: up, but see below.
  UNMEASURED no reading of the unit. Nothing is done on no reading; five in a row alarm.

  Progress is a START/work/DONE log line. STALLED is stall_quiet_min with none of them and under stall_cpu_pct of one
  core over the last stall_quiet_min (a model pass logs nothing until it ends, so the log alone cannot tell a live pass from a hung
  one; an idle claude sits under 1%, hence the low bar), or stall_hard_min with none whatever the CPU says, which is past
  the longest single step the runner allows (3 h). It is an alarm only; nothing is killed.
  The restart budget is one per arm; an `ARM RUNNING <arm>` launcher line newer than the restart (a person relaunched)
  gives it back. A unit that vanished is a death only when the boot id changed since it was seen up; on the same boot a
  person stopped it, and that reads WAITING. Past the stop line nothing is restarted or alarmed: the Conductor stops it.

Alarms (ledger note on the schedule's alarm_item as DISPATCHER, under testq ingest.lock, published by the next Dispatcher
tick; and a line in no_handoff.conductor_log) repeat every realarm_min while the condition stands; a failed sink is
retried next tick. Writes: the Trial rows of ARENA_BUILD_BOARD.md and the one-line replay_watch_status.txt.

It never touches tokens, logins, STOP files, the pool or the account picker. Its only commands are `systemctl --user
show` / `reset-failed`, launch_arm.sh, `rimflow note`.

    python3 src/RimMandrake/Utils/replay_watch.py tick [--dry]
"""
import argparse
import calendar
import datetime
import fcntl
import json
import os
import pwd
import re
import subprocess
import sys
import tempfile
import time
import zoneinfo
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARMS = ("ralph_a", "trio", "v3")
TOTAL = 29
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
# "8 AM PDT Sunday": fixed at -07:00. DST ends 02:00 that morning, so the wall clock reads 7:00 AM PST at this instant.
STOP_LINE = calendar.timegm((2026, 11, 1, 15, 0, 0))

DEFAULTS = {"replay": "/mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay", "arena": "/mnt/d/ClaudeWork/rimmandrake/arena",
            "dispatcher": "/mnt/d/ClaudeWork/rimmandrake/dispatcher", "testq": "/mnt/d/ClaudeWork/rimmandrake/testq",
            "schedule": str(REPO / "src/RimMandrake/rimflow/dispatcher_schedule.json"), "stop_line": STOP_LINE,
            "stall_quiet_min": 45, "stall_cpu_pct": 0.2, "stall_hard_min": 200, "capacity_alarm_min": 120,
            "realarm_min": 60, "blind_ticks": 5, "login_stale_s": 900, "login_settle_min": 15, "lock_wait_s": 45}

STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[-+]\d\d:?\d\d) (.*)$")
TASK_EV = re.compile(r"^\S+: task (\S+) (START|work|DONE|ERROR)\b(.*)$", re.S)
ENDS = re.compile(r"^\S+: runner ends: .*?stopped (.*)$", re.S)
ERR_TYPE = re.compile(r"^(?:error on \S+: |\S+: task \S+ ERROR )?([A-Za-z_][\w.]*): ")
# the runner's deliberate stops (arena_replay_run.unmeasured_result, the red-start STOP, the judge's missing record)
FAIL_LOUD = re.compile(r"gate all-UNMEASURED|gate verdict invalid|judge verdict invalid|judge printed no record|"
                       r"gate printed no JSON|red start|pre-check red|STOP written")
# the machine failed, not the arm: the only exceptions a restart may answer. The harness raises many deliberate ones.
CRASHES = ("OSError", "IOError", "TimeoutError", "TimeoutExpired", "ConnectionError", "ConnectionResetError",
           "BrokenPipeError", "MemoryError")
KILLED = ("signal", "core-dump", "oom-kill")
# login_watch.GONE_RX + role_launch.AUTH_RX, without their bare "please run": a restart hangs on this match
LOGIN_RX = re.compile(r"not logged in|log ?in expired|session expired|please (run /?login|log ?in)|"
                      r"failed to authenticate|authentication_failed", re.I)
ALARM_STATES = ("PAGED", "TWICE_DEAD", "STALLED")
ORDER = ("TWICE_DEAD", "PAGED", "STALLED", "UNMEASURED", "LOGIN", "RESTARTED", "HOLD_CAPACITY", "RUNNING", "WAITING",
         "STOPPED", "DONE")
SHOW = {"RUNNING": "🟡 Running", "HOLD_CAPACITY": "🟡 Holding", "WAITING": "⚪ Waiting", "DONE": "✅ Done",
        "STOPPED": "⚪ Stopped", "LOGIN": "🟠 Login lost", "RESTARTED": "🟡 Restarted", "UNMEASURED": "🟠 Unread",
        "PAGED": "🔴 Paged", "TWICE_DEAD": "🔴 Died twice", "STALLED": "🔴 Stalled"}
FOOT_ORDER = ("✅ Done", "🔵 In review", "🟠 Live proof", "🟡 Building", "🟡 Running", "🟡 Holding", "🟡 Restarted",
              "🟠 Login lost", "🟠 Unread", "🔴 Blocked", "🔴 Paged", "🔴 Stalled", "🔴 Died twice", "⚪ Queued",
              "⚪ Waiting", "⚪ Stopped")


def clock(t):
    d = datetime.datetime.fromtimestamp(t, TZ)
    return "%d:%02d %s %s" % (d.hour % 12 or 12, d.minute, "AM" if d.hour < 12 else "PM", d.tzname())


def win(path):
    p = str(path)
    return "%s:%s" % (p[5].upper(), p[6:].replace("/", "\\")) if p.startswith("/mnt/") else p


def parse_stamp(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z").timestamp()
    except ValueError:
        return None


def parse_log(text):
    """-> [(ts, body)]; a line with no stamp continues the one before it (a multi-line error)."""
    out = []
    for line in (text or "").splitlines():
        m = STAMP.match(line)
        ts = parse_stamp(m.group(1)) if m else None
        if ts is not None:
            out.append([ts, m.group(2)])
        elif out:
            out[-1][1] += "\n" + line
    return out


def log_facts(lines, since=None):
    """Facts of an arm log. Durations and progress read every line; ended/error/capacity only lines at or after `since`
    (the invocation's start): the log is append-only across runs, and yesterday's ERROR is not today's death."""
    f = {"progress": None, "task": None, "task_start": None, "durations": [], "ended": None, "error": None,
         "capacity_since": None}
    start = {}
    for ts, body in lines:
        m = TASK_EV.match(body)
        new = since is None or ts >= since
        if "runway" in body and "waiting" in body:
            if new and f["capacity_since"] is None:
                f["capacity_since"] = ts
            continue
        if m:
            tid, ev = m.group(1), m.group(2)
            f["capacity_since"] = None
            if ev == "START":
                start[tid] = ts
                f["task"], f["task_start"] = tid, ts
            elif ev == "DONE" and tid in start:
                f["durations"].append(ts - start[tid])
            if ev == "ERROR":
                if new:
                    f["error"] = body
            else:
                f["progress"] = ts
        e = ENDS.match(body)
        if e and new:
            f["ended"] = e.group(1)
    return f


def death_class(unit, facts):
    """-> (class, why): stop | ended | login | gate | refused | died. Deliberate-stop evidence is read whether or not a
    runner-ends line made it; only a kill the unit's Result proves, or an exception on CRASHES, is a death. The rest pages."""
    ended, error = facts.get("ended"), facts.get("error")
    text = "%s\n%s" % (ended or "", error or "")
    if FAIL_LOUD.search(text):
        return "gate", text.strip()[:300]
    if LOGIN_RX.search(text):
        return "login", text.strip()[:200]
    if unit.get("status") == 2:
        return "refused", "start refused (exit 2)"
    if ended is not None and ended.startswith("STOP file"):
        return "stop", ended[:200]
    if ended is not None and ended.startswith("None"):
        return "ended", "runner ended cleanly"
    if ended is None and error is None and unit.get("result") in KILLED:
        return "died", "no runner-ends line: killed (%s, exit %s)" % (unit.get("result"), unit.get("status"))
    if ended is None and error is None:
        return "refused", "exited with no words (%s, exit %s): read the log" % (unit.get("result"), unit.get("status"))
    m = ERR_TYPE.search((ended or error or "").split("\n")[0])
    if m and m.group(1).rsplit(".", 1)[-1] in CRASHES:
        return "died", text.strip()[:300]
    return "refused", text.strip()[:300]


def parse_launcher(text):
    """-> {"fix": newest FIXED/BLOCKED ts, "line": its text, "run": {arm: newest ARM RUNNING ts}}."""
    out = {"fix": 0, "line": "", "run": {}}
    for line in (text or "").splitlines():
        p = line.split(" ", 3)
        ts = parse_stamp(p[0]) if p else None
        if ts is None or len(p) < 2:
            continue
        if p[1] in ("FIXED", "BLOCKED") and ts >= out["fix"]:
            out["fix"], out["line"] = ts, line.split(" ", 1)[1][:120]
        elif p[1] == "ARM" and len(p) > 3 and p[2] == "RUNNING" and p[3].split():
            out["run"][p[3].split()[0]] = ts
    return out


def done_facts(runner):
    """runner.json dict -> (done ids, last verdict) | (None, None) when it does not read."""
    if not isinstance(runner, dict) or not isinstance(runner.get("done"), dict):
        return None, None
    recs = [r for r in runner["done"].values() if isinstance(r, dict)]
    recs.sort(key=lambda r: r["ts"] if isinstance(r.get("ts"), (int, float)) else 0)
    last = (recs[-1].get("judge") or {}) if recs else {}
    return set(runner["done"]), (last.get("verdict") if isinstance(last, dict) else None)


def project(now, done, total, facts):
    """-> finish epoch from this arm's own START->DONE durations (the last ten), or None with none yet."""
    d = facts["durations"][-10:]
    if done is None or not d:
        return None
    mean = sum(d) / len(d)
    into = min(mean, now - facts["task_start"]) if facts.get("task_start") else 0
    return now + max(0.0, (total - done) * mean - into)


def cpu_pct(samples, since):
    """Mean % of one core from the first sample near `since` to the last; None when the samples do not span it."""
    use = [s for s in samples if s[0] >= since]
    if len(use) < 2 or use[-1][0] - use[0][0] < 0.8 * (use[-1][0] - since):
        return None
    dt = use[-1][0] - use[0][0]
    return 100.0 * (use[-1][1] - use[0][1]) / (dt * 1e9) if dt > 0 else None


def assess(arm, rd, s, cfg, now):
    """Pure: one arm's reading + its saved state `s` (updated in place) -> (row, actions).
    rd keys: unit (dict|None), lines, runner, stop (bool), launcher, login (True dead|False alive|None unknown), boot,
    total. Actions: {"do": "restart", "why"} | {"do": "alarm", "kind", "why", "first"}."""
    unit, total, acts = rd["unit"], rd["total"], []
    live = bool(unit) and unit.get("active") in ("active", "activating", "reloading", "deactivating")
    since = unit.get("start") if unit else None
    facts = log_facts(rd["lines"], since if (unit and unit.get("load") == "loaded") else None)
    ids, verdict = done_facts(rd["runner"])
    done = len(ids) if ids is not None else None
    row = {"arm": arm, "state": None, "done": done, "total": total, "verdict": verdict, "progress": facts["progress"],
           "finish": None, "note": ""}
    over = now >= cfg["stop_line"]
    inv = (unit or {}).get("inv") or s.get("inv") or "none"

    def alarm(kind, why, first):
        if not over:
            acts.append({"do": "alarm", "kind": "%s:%s:%s" % (kind, arm, inv[:8]), "why": why, "first": first})

    def finish(state, note=""):
        row["state"], row["note"] = state, note
        return row, acts

    def dead(cls, why):
        """A death of class `cls`, after the login, stop and done checks."""
        settled = now - (unit.get("exit") or 0) >= cfg["login_settle_min"] * 60
        if rd["login"] is True or (cls == "login" and (rd["login"] is None or not settled)):
            return finish("LOGIN", "the login is out; login_watch owns it")
        if cls == "login":
            cls = "died"                     # alive, and read long enough after the death to mean it
        if cls in ("gate", "refused"):
            alarm("paged", "arm %s stopped on purpose at task %s: %s" % (arm, facts["task"], why),
                  "Replay arm %s is down on a fail-loud stop: read %s, fix, relaunch." % (
                      arm, win(rd.get("log", "the arm log"))))
            return finish("PAGED", why[:160])
        if s.get("restart_at", 0) > rd["launcher"]["run"].get(arm, 0):
            alarm("twice_dead", "arm %s died again after its one restart at %s: %s" % (
                arm, clock(s["restart_at"]), why), "Replay arm %s died twice: relaunch by hand." % arm)
            return finish("TWICE_DEAD", why[:160])
        if over:
            return finish("WAITING", "past the stop line, not restarted")
        acts.append({"do": "restart", "why": why})
        return finish("RESTARTED", why[:160])

    if unit is None:
        s["blind"] = s.get("blind", 0) + 1
        if s["blind"] >= cfg["blind_ticks"] and rd["login"] is not True:
            alarm("blind", "arm %s: unit unreadable %d ticks running" % (arm, s["blind"]),
                  "The replay watchdog cannot read arm %s." % arm)
        return finish("UNMEASURED", "no reading of the unit; nothing done")
    s.pop("blind", None)
    if live:
        if unit.get("inv") != s.get("inv"):
            s["cpu"], s["seen_at"] = [], now
        s["inv"], s["boot"] = unit.get("inv"), rd["boot"]
        if isinstance(unit.get("cpu"), int):
            s.setdefault("cpu", []).append([now, unit["cpu"]])
            s["cpu"] = [c for c in s["cpu"] if c[0] >= now - (cfg["stall_hard_min"] + 15) * 60]
        row["finish"] = project(now, done, total, facts)
        if over:
            return finish("RUNNING", "past the stop line")
        if rd["login"] is True:
            return finish("LOGIN", "the login is out; login_watch owns it")
        if facts["capacity_since"] is not None:
            held = now - facts["capacity_since"]
            if held >= cfg["capacity_alarm_min"] * 60:
                alarm("stalled", "arm %s held for capacity %d min" % (arm, held / 60),
                      "Replay arm %s has waited for capacity %d min." % (arm, held / 60))
                return finish("STALLED", "held for capacity %d min" % (held / 60))
            return finish("HOLD_CAPACITY", "waiting for capacity, %d min" % (held / 60))
        last = max(facts["progress"] or 0, unit.get("start") or 0) or s.get("seen_at") or now
        quiet = now - last
        pct = cpu_pct(s.get("cpu") or [], now - cfg["stall_quiet_min"] * 60)
        stalled = quiet >= cfg["stall_hard_min"] * 60 or (
            quiet >= cfg["stall_quiet_min"] * 60 and pct is not None and pct < cfg["stall_cpu_pct"])
        if stalled:
            why = "no progress %d min, CPU %s" % (quiet / 60, "unread" if pct is None else "%.1f%% of a core" % pct)
            alarm("stalled", "arm %s at task %s: %s" % (arm, facts["task"], why),
                  "Replay arm %s is stalled: nothing was restarted." % arm)
            return finish("STALLED", why)
        return finish("RUNNING")
    if ids is not None and done >= total:
        return finish("DONE")
    if rd["stop"]:
        return finish("STOPPED", "STOP file stands; left alone")
    if unit.get("active") != "failed":
        seen = s.get("inv")
        if seen and s.get("boot") and s["boot"] != rd["boot"]:
            return dead("died", "the machine restarted under the arm")
        return finish("WAITING", "not started; relaunch owed")
    if (unit.get("exit") or 0) and rd["launcher"]["fix"] > unit["exit"]:
        return finish("WAITING", "relaunch owed after: %s" % rd["launcher"]["line"])
    cls, why = death_class(unit, facts)
    if cls == "stop":
        return finish("STOPPED", "the runner stopped on a STOP file")
    if cls == "ended":
        return finish("WAITING", "runner ended cleanly with tasks left")
    return dead(cls, why)


def summary_row(rows, now, cfg):
    """-> (overall state, Day 1 status cell, sentence)."""
    overall = min((r["state"] for r in rows), key=ORDER.index)
    if all(r["state"] == "DONE" for r in rows):
        cell = "✅ Done"
    elif overall in ALARM_STATES:
        cell = "🔴 Blocked"
    elif all(r["state"] in ("WAITING", "STOPPED", "DONE") for r in rows):
        cell = "⚪ Waiting"
    else:
        cell = "🟡 Running"
    done = [r["done"] for r in rows if r["done"] is not None]
    text = "Watchdog at %s: %d of %d arm-tasks finished, overall %s." % (
        clock(now), sum(done), rows[0]["total"] * len(rows), overall.lower().replace("_", " "))
    return overall, cell, text


def arm_note(r, now, cfg):
    bits = ["%s of %d done" % ("?" if r["done"] is None else r["done"], r["total"]),
            "last verdict %s" % (r["verdict"] or "none yet"),
            "last progress %s" % ("none yet" if not r["progress"] else "%d min ago" % ((now - r["progress"]) / 60))]
    if r["finish"]:
        lead = (cfg["stop_line"] - r["finish"]) / 3600.0
        bits.append("projected finish %s, %.1f h %s the stop line" % (
            clock(r["finish"]), abs(lead), "before" if lead >= 0 else "AFTER"))
    elif r["state"] in ("RUNNING", "HOLD_CAPACITY"):
        bits.append("no finish estimate until a task completes")
    if r["note"]:
        bits.append(r["note"])
    return "; ".join(bits).replace("|", "/").replace("\n", " ") + "."


def update_board(text, rows, now, cfg):
    """The Trial rows of the board: the Day 1 row and rows 1a.. per arm, then the footer count without the arm rows.
    -> new text, or None when the table is not there (the board was rewritten: left alone)."""
    lines = text.split("\n")
    day = next((i for i, x in enumerate(lines) if re.match(r"\| 1 \| Day 1:", x)), None)
    if day is None:
        return None
    _, cell, sentence = summary_row(rows, now, cfg)
    c = [x.strip() for x in lines[day].strip().strip("|").split("|")]
    if len(c) != 5:
        return None
    keep = re.search(r"Closing day 0[^|]*", c[4])
    lines[day] = "| 1 | %s | %s | %s | %s |" % (c[1], cell, c[3], (sentence + (" " + keep.group(0).strip() if keep else "")))
    lines = [x for x in lines if not re.match(r"\| 1[a-z] \|", x)]
    day = next(i for i, x in enumerate(lines) if re.match(r"\| 1 \| Day 1:", x))
    for i, r in enumerate(rows):
        lines.insert(day + 1 + i, "| 1%s | Arm %s | %s | Watchdog | %s |" % (
            "abcdefg"[i], r["arm"], SHOW[r["state"]], arm_note(r, now, cfg)))
    count = {}
    for x in lines:
        p = [y.strip() for y in x.strip().strip("|").split("|")]
        if len(p) == 5 and x.startswith("|") and p[2] != "Status" and not p[0].startswith("-") and \
                not re.fullmatch(r"1[a-z]", p[0]):
            count[p[2]] = count.get(p[2], 0) + 1
    foot = next((i for i, x in enumerate(lines) if re.match(r"[✅🔵🟠🟡🔴⚪][^|]* \d+( · |$)", x)), None)
    if foot is not None:
        keys = sorted(count, key=lambda k: FOOT_ORDER.index(k) if k in FOOT_ORDER else 99)
        lines[foot] = " · ".join("%s %d" % (k, count[k]) for k in keys)
    return "\n".join(lines)


def status_line(rows, now, cfg):
    overall = summary_row(rows, now, cfg)[0]
    parts = ["%s %s %s/%d last %s %s %s" % (
        r["arm"], r["state"], "?" if r["done"] is None else r["done"], r["total"], r["verdict"] or "none",
        ("-" if not r["progress"] else "%dm" % ((now - r["progress"]) / 60)),
        ("eta " + clock(r["finish"]) + (" LATE" if r["finish"] > cfg["stop_line"] else "")) if r["finish"] else "eta none")
        for r in rows]
    return " ".join(("%s replay %s | %s | stop line %s" % (
        clock(now), overall, " | ".join(parts), clock(cfg["stop_line"]))).split())


# ------------------------------------------------------------------------------------------------ the real world
class World:
    """Every side effect. The selftest replaces this class's methods; nothing else touches the machine."""

    def __init__(self, cfg):
        self.cfg = cfg

    def now(self):
        return time.time()

    def boot(self):
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()

    def unit(self, arm):
        try:
            r = subprocess.run(["systemctl", "--user", "show", "rm-arena-replay-%s.service" % arm, "--timestamp=unix",
                                "-p", "LoadState,ActiveState,Result,ExecMainStatus,ExecMainStartTimestamp,"
                                "ExecMainExitTimestamp,InactiveEnterTimestamp,InvocationID,CPUUsageNSec"],
                               capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0:
            return None
        return parse_show(r.stdout)

    def login(self):
        """True dead, False alive, None unknown (no state, or one too old to speak for now)."""
        p = Path(self.cfg["dispatcher"]) / "state.json"
        try:
            if self.now() - p.stat().st_mtime > self.cfg["login_stale_s"]:
                return None
            return bool((json.loads(p.read_text("utf-8")).get("login") or {}).get("dead_since"))
        except (OSError, ValueError, AttributeError, RecursionError):
            return None

    def restart(self, arm):
        """The documented route. -> (ok, text)."""
        home = pwd.getpwuid(os.getuid()).pw_dir
        env = dict(os.environ, PATH="%s/.local/bin:%s/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                   ":/usr/games" % (home, home))
        subprocess.run(["systemctl", "--user", "reset-failed", "rm-arena-replay-%s.service" % arm],
                       capture_output=True, text=True, timeout=30)
        try:
            r = subprocess.run(["/bin/bash", str(Path(self.cfg["replay"]) / "launch_arm.sh"), arm], env=env,
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as e:
            return False, "%s: %s" % (type(e).__name__, e)
        return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()[-200:]

    def note(self, text):
        """A ledger note as the Dispatcher does it. -> (ok, why)."""
        sch = json.loads(Path(self.cfg["schedule"]).read_text("utf-8"))
        item = sch.get("alarm_item")
        env = dict(os.environ, RIMFLOW_SEAT="DISPATCHER", CLAUDE_PROJECT_DIR=str(REPO))
        with open(Path(self.cfg["testq"]) / "ingest.lock", "w") as lk:
            t0 = time.time()
            while True:
                try:
                    fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() - t0 > self.cfg["lock_wait_s"]:
                        return False, "ingest.lock busy"
                    time.sleep(2)
            r = subprocess.run([sys.executable, str(REPO / "src/RimMandrake/rimflow/cli.py"), "note", item, "--text",
                                text, "--seat", "DISPATCHER"], cwd=str(REPO), env=env, capture_output=True, text=True,
                               timeout=90, stdin=subprocess.DEVNULL)
        return r.returncode == 0, ((r.stdout or "") + (r.stderr or "")).strip()[-200:]

    def conductor(self, line):
        sch = json.loads(Path(self.cfg["schedule"]).read_text("utf-8"))
        with open((sch.get("no_handoff") or {}).get("conductor_log"), "a", encoding="utf-8") as f:
            f.write(line)


def parse_show(text):
    d = dict(x.split("=", 1) for x in text.splitlines() if "=" in x)

    def ts(k):
        m = re.fullmatch(r"@(\d+)", (d.get(k) or "").strip())
        return int(m.group(1)) if m else None

    def num(k):
        return int(d[k]) if (d.get(k) or "").isdigit() else None

    if "LoadState" not in d or "ActiveState" not in d:
        return None
    if d["LoadState"] != "loaded":
        return {"load": d["LoadState"], "active": "absent"}
    return {"load": "loaded", "active": d["ActiveState"], "result": d.get("Result"), "status": num("ExecMainStatus"),
            "start": ts("ExecMainStartTimestamp"), "exit": ts("ExecMainExitTimestamp") or ts("InactiveEnterTimestamp"),
            "inv": d.get("InvocationID") or None, "cpu": num("CPUUsageNSec")}


def read_text(p, tail=1 << 20):
    try:
        with open(p, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - tail))
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def write_atomic(p, text):
    p = Path(p)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".%s." % p.name)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def state_ok(d):
    def num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v < 1e20

    if not (isinstance(d.get("arms"), dict) and isinstance(d.get("alarms"), dict)):
        return False
    for a in d["arms"].values():
        if not isinstance(a, dict) or ("restart_at" in a and not (num(a["restart_at"]) and a["restart_at"] < 4e9)) or \
                ("seen_at" in a and not num(a["seen_at"])) or ("blind" in a and not num(a["blind"])):
            return False
        if any(k in a and not isinstance(a[k], (str, type(None))) for k in ("inv", "boot")):
            return False
        cpu = a.get("cpu", [])
        if not (isinstance(cpu, list) and all(isinstance(c, list) and len(c) == 2 and num(c[0]) and num(c[1]) for c in cpu)):
            return False
    for r in d["alarms"].values():
        if not isinstance(r, dict) or any(k in r and not num(r[k]) for k in ("standing", "conductor", "ledger")):
            return False
        if "why" in r and not (isinstance(r["why"], str) and isinstance(r.get("first"), str)):
            return False
    return True


def load_state(p):
    """-> (state, readable). No file: a first tick. An unreadable one is NOT a first tick: it holds the restart budget."""
    if not Path(p).exists():
        return {"arms": {}, "alarms": {}}, True
    try:
        d = json.loads(Path(p).read_text("utf-8"))
        if state_ok(d):
            return d, True
    except (OSError, ValueError, AttributeError, RecursionError):
        pass
    return {"arms": {}, "alarms": {}}, False


def read_arm(w, arm, cfg, launcher, login, boot, total):
    rp = Path(cfg["replay"])
    log = rp / "logs" / ("%s.log" % arm)
    try:
        runner = json.loads((rp / "ctl" / arm / "runner.json").read_text("utf-8"))
    except FileNotFoundError:
        runner = {"done": {}}                 # a fresh attempt writes it at its first finished task
    except (OSError, ValueError, RecursionError):
        runner = None
    return {"unit": w.unit(arm), "lines": parse_log(read_text(log)), "runner": runner, "log": log,
            "stop": os.path.lexists(rp / "ctl" / arm / "STOP"), "launcher": launcher, "login": login, "boot": boot,
            "total": total}


def send_alarms(w, st, acts, now, cfg):
    """Standing alarms repeat every realarm_min per sink. An alarm keeps its text in the state until both sinks took it
    once, so a failed sink is retried next tick even when the condition has gone. -> [sink failures]."""
    bad = []
    for a in acts:
        rec = st["alarms"].setdefault(a["kind"], {})
        rec.update(why=a["why"], first=a["first"], standing=now)
    for kind, rec in st["alarms"].items():
        if "why" not in rec:
            continue
        for sink in ("conductor", "ledger"):
            sent = rec.get(sink)
            sent = sent if isinstance(sent, (int, float)) else None
            owed = rec.get("owed_" + sink)
            if not owed and sent is not None and (rec.get("standing") != now or
                                                  now - sent < cfg["realarm_min"] * 60):
                continue
            try:
                if sink == "conductor":
                    w.conductor("\n%s — REPLAY WATCH ESCALATION (%s): %s\n  RAISE FIRST: %s\n" % (
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), kind, rec["why"], rec["first"]))
                    ok, out = True, ""
                else:
                    ok, out = w.note("replay watch %s: %s" % (kind, rec["why"]))
            except Exception as e:  # noqa: BLE001 - a failed sink must not cost the other sink or the board
                ok, out = False, "%s: %s" % (type(e).__name__, str(e)[:160])
            if ok:
                rec[sink] = now
                rec.pop("owed_" + sink, None)
            else:
                rec["owed_" + sink] = True
                bad.append("%s %s: %s" % (sink, kind, out))
    return bad


def still_owed(w, arm, cfg):
    """Re-read just before a restart: an earlier arm's launch can take a minute. -> why not, or None."""
    if w.now() >= cfg["stop_line"]:
        return "past the stop line"
    if os.path.lexists(Path(cfg["replay"]) / "ctl" / arm / "STOP"):
        return "a STOP file appeared"
    if w.login() is True:
        return "the login went out"
    u = w.unit(arm)
    if u is None or u.get("active") in ("active", "activating", "reloading", "deactivating"):
        return "the unit is up or unread"
    return None


def restart_arm(w, st, sp, arm, s, row, a, cfg, now, alarms, kind):
    late = still_owed(w, arm, cfg)
    if late:
        row["state"], row["note"] = "WAITING", "restart held: %s" % late
        return
    s["restart_at"] = w.now()             # the launch's own time, not the tick's; saved before the launch: a killed tick cannot restart twice
    s["restart_why"] = a["why"][:300]
    write_atomic(sp, json.dumps(st, indent=1, sort_keys=True))
    try:
        ok, out = w.restart(arm)
    except Exception as e:  # noqa: BLE001
        ok, out = False, "%s: %s" % (type(e).__name__, str(e)[:160])
    if not ok:
        row["state"], row["note"] = "TWICE_DEAD", "restart failed: %s" % out[:120]
        alarms.append({"kind": kind, "why": "arm %s: the one restart failed: %s" % (arm, out),
                       "first": "Replay arm %s is down and its restart failed: relaunch by hand." % arm})
    try:
        with open(Path(cfg["replay"]) / "launcher.log", "a", encoding="utf-8") as f:
            f.write("%s WATCH RESTART %s %s: %s\n" % (
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now)), arm, "launched" if ok else "FAILED",
                a["why"][:200].replace("\n", " ")))
    except OSError:
        pass                              # the record of a restart must not cost its alarm or the other arms


def tick(cfg=None, world=None, dry=False):
    cfg = dict(DEFAULTS, **(cfg or {}))
    w = world or World(cfg)
    home = Path(cfg["arena"]) / "replay_watch"
    home.mkdir(parents=True, exist_ok=True)
    with open(home / "tick.lock", "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return None, []                   # another tick holds the decisions; two could restart one arm twice
        return locked_tick(cfg, w, home, dry)


def locked_tick(cfg, w, home, dry):
    now = w.now()
    sp = home / "state.json"
    st, readable = load_state(sp)
    launcher = parse_launcher(read_text(Path(cfg["replay"]) / "launcher.log"))
    try:
        plan = json.loads(read_text(Path(cfg["replay"]) / "plan.txt"))
        total = len(plan) if isinstance(plan, list) and plan else TOTAL
    except (ValueError, RecursionError):
        total = TOTAL
    login, boot = w.login(), w.boot()
    rows, alarms = [], []
    for arm in ARMS:
        s = st["arms"].setdefault(arm, {})
        if not readable:                      # the budget is lost: spent until a person relaunches
            s["restart_at"] = now
        rd = read_arm(w, arm, cfg, launcher, login, boot, total)
        row, acts = assess(arm, rd, s, cfg, now)
        for a in acts:
            if a["do"] == "alarm":
                alarms.append(a)
            elif not dry:
                inv = ((rd["unit"] or {}).get("inv") or s.get("inv") or "none")[:8]
                restart_arm(w, st, sp, arm, s, row, a, cfg, now, alarms, "twice_dead:%s:%s" % (arm, inv))
        rows.append(row)
    if not dry:
        bad = send_alarms(w, st, alarms, now, cfg)
        for k in [k for k, r in st["alarms"].items()
                  if r.get("standing", now) < now - 86400 and "conductor" in r and "ledger" in r and
                  not r.get("owed_conductor") and not r.get("owed_ledger")]:
            del st["alarms"][k]
        write_atomic(sp, json.dumps(st, indent=1, sort_keys=True))
        line = status_line(rows, now, cfg)
        write_atomic(Path(cfg["arena"]) / "replay_watch_status.txt", line + "\n")
        board = Path(cfg["arena"]) / "ARENA_BUILD_BOARD.md"
        old = read_text(board)
        new = update_board(old, rows, now, cfg) if old else None
        if new and new != old:
            write_atomic(board, new)
        with open(home / "ticks.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now, "line": line, "rows": rows, "alarms": [a["kind"] for a in alarms],
                                "sink_failures": bad, "board": bool(new)}) + "\n")
    return rows, alarms


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("tick",))
    ap.add_argument("--dry", action="store_true", help="read and print; write and restart nothing")
    a = ap.parse_args(argv)
    try:
        rows, alarms = tick(dry=a.dry)
    except Exception as e:  # noqa: BLE001 - a silent watchdog is the failure this exists to end
        write_atomic(Path(DEFAULTS["arena"]) / "replay_watch_status.txt", "%s replay WATCHDOG BROKEN: %s: %s\n" % (
            clock(time.time()), type(e).__name__, str(e)[:160].replace("\n", " ")))
        raise
    if rows is None:
        print("another tick is running")
        return 0
    now = time.time()
    print(status_line(rows, now, DEFAULTS))
    for x in alarms:
        print("ALARM", x["kind"], x["why"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
