#!/usr/bin/env python3
"""selftest_artisan_now.py: plant a stale log, a dead unit and missing files, and see the sheet say so.

A planted world of loops runs through the whole page build with systemd and the machines stubbed out, and each
fault must show in the words the owner reads. Healthy loops in the same world must stay quiet. Then every check
is shown able to fail: a mutant of artisan_now.py per check, built in memory, must go red by that check's name.
No game, no bridge, no ssh, nothing outside a temp folder.
"""

import contextlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = os.path.join(HERE, "artisan_now.py")
SOURCE = open(SOURCE_PATH, encoding="utf-8").read()

LOOP_SH = """#!/bin/bash
LOGS=%s
REVIEW_AT=${REVIEW_AT:-10000000}
OFFLINE_AT=${OFFLINE_AT:-3000000}
game_busy() {
  systemctl --user is-active --quiet rm-ralph-healthy
}
"""

# name -> whether the planted model process is alive
MODEL_ALIVE = {"healthy": True, "stale": True, "nopasslog": True, "stopflag": True, "nolog": True}


def load(source):
    mod = types.ModuleType("artisan_now_under_test")
    mod.__file__ = SOURCE_PATH
    exec(compile(source, SOURCE_PATH, "exec"), mod.__dict__)
    return mod


def hms(t):
    return time.strftime("%H:%M:%S PST", time.localtime(t))


def usage_line(mid, inp=1000, out=100, cw=0, cr=0):
    return json.dumps({"type": "assistant", "message": {"id": mid, "usage": {
        "input_tokens": inp, "output_tokens": out, "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr}}})


class World:
    def __init__(self, mod, root):
        self.mod, self.root = mod, root
        self.units = {}
        self.logs_root = os.path.join(root, "logs")
        os.makedirs(self.logs_root)
        mod.OUT_DIR = os.path.join(root, "out")
        os.makedirs(mod.OUT_DIR)
        mod.LOG_ROOT = self.logs_root
        mod.CLONE_GLOB = os.path.join(root, "scratch", "*", "ralph_*")
        mod.PROJECTS = os.path.join(root, "projects")
        mod.QHOME = os.path.join(root, "no_testq")
        mod.ACCOUNTS = os.path.join(root, "no_accounts")
        mod.LEARNED = os.path.join(root, "no_learned.md")
        mod.BRIDGE_FILES = [os.path.join(root, "no_bridge")]

    def loop(self, name, events, unit="active", result="success", events_file=True, pass_n=None, pass_age=20,
             pass_log=True, progress="fine so far\n\n## Count\n- bar_a: true\n- bar_b: unseen\n", stop=False, done=False):
        now = time.time()
        clone = os.path.join(self.root, "scratch", "BENCH", "ralph_" + name)
        rd = os.path.join(clone, "ralph")
        os.makedirs(rd)
        logs = os.path.join(self.logs_root, "ralph_" + name)
        os.makedirs(logs)
        open(os.path.join(rd, "loop.sh"), "w").write(LOOP_SH % logs)
        open(os.path.join(rd, "PROMPT.md"), "w").write("%s is a planted mod.\n" % name)
        if progress is not None:
            open(os.path.join(rd, "PROGRESS.md"), "w").write(progress)
        if done:
            open(os.path.join(rd, "DONE.md"), "w").write("I would show this.\n")
        if stop:
            with open(os.path.join(logs, "STOP"), "w") as f:
                f.write(stop if isinstance(stop, str) else "")
        if events_file:
            path = os.path.join(logs, "events.log")
            with open(path, "w") as f:
                for ago_s, text in events:
                    f.write("%s %s\n" % (hms(now - ago_s), text))
            os.utime(path, (now - events[-1][0], now - events[-1][0]))
        if pass_n and pass_log:
            path = os.path.join(logs, "pass_%03d.jsonl" % pass_n)
            with open(path, "w") as f:
                f.write(usage_line("m1", inp=500_000) + "\n")
            os.utime(path, (now - pass_age, now - pass_age))
        pdir = self.mod.project_dir(clone)
        os.makedirs(pdir)
        tx = os.path.join(pdir, "session.jsonl")
        with open(tx, "w") as f:
            f.write(json.dumps({"type": "assistant", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - pass_age)),
                                "message": {"usage": {"input_tokens": 9, "cache_read_input_tokens": 100_000}, "content": [
                                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"description": "Build the planted mod", "command": "true"}},
                                    {"type": "text", "text": "Working on the planted thing."}]}}) + "\n")
        os.utime(tx, (now - pass_age, now - pass_age))
        if unit:
            uname = "rm-ralph-" + name
            self.units[uname] = {"Id": uname + ".service", "WorkingDirectory": clone, "ActiveState": unit, "SubState": "running",
                                 "Result": result, "ControlGroup": "", "ExecStart": "ralph/loop.sh", "Environment": "LOGS=%s" % logs,
                                 "ActiveEnterTimestampMonotonic": "1000000", "_model": MODEL_ALIVE.get(name, False)}
        return clone


def plant(mod, root):
    """The world: healthy loops that must stay quiet, and one planted fault per loop."""
    w = World(mod, root)
    start = "LOOP start, 2 passes on record, 2000000 tokens"
    w.loop("healthy", [(1800, start), (1800, "PASS 3 start, 2000000 tokens so far")], pass_n=3)
    w.loop("stale", [(10800, start), (10800, "PASS 3 start, 2000000 tokens so far")], pass_n=3, pass_age=7200)
    w.loop("deadun", [(9000, start), (9000, "PASS 3 start, 2000000 tokens so far")], unit=None, pass_n=3, pass_age=9000)
    w.loop("failedun", [(9000, start), (8000, "PASS 3 end, rc 1, 2100000 tokens, head abc")], unit="failed", result="exit-code")
    w.loop("nolog", [], events_file=False, progress=None)
    w.loop("nopasslog", [(1800, start), (1800, "PASS 3 start, 2000000 tokens so far")], pass_n=3, pass_log=False)
    w.loop("stopflag", [(1800, start), (1800, "PASS 3 start, 2000000 tokens so far")], pass_n=3, stop=True)
    w.loop("claimed", [(3600, start), (600, "LOOP DONE_CLAIMED, 5000000 tokens")], unit=None, done=True)
    w.loop("waiter", [(3600, start), (1800, "GAME_WAIT: a loop ahead has the game, no model running, 3000000 tokens")])
    mod.list_units = lambda sources: w.units
    mod.cgroup_processes = lambda props: (bool((props or {}).get("_model")), [])

    def read_machine(name):
        if name == "SteveDesktop":
            raise mod.Unmeasured("ssh: planted refusal")
        return {"read_at": time.time(), "game": False, "tps_roots": 1, "wsl_free_mb": 4096}

    mod.read_machine = read_machine
    mod.read_tailscale = lambda: (_ for _ in ()).throw(mod.Unmeasured("planted tailscale failure"))
    mod.read_background = lambda sources: {"detached": [], "failed": [], "watchers": 0, "claude": __import__("collections").Counter()}
    with open(mod.state_path(), "w") as f:
        json.dump({"machines": {"SteveDesktop": {"read_at": time.time() - 3600, "game": True, "tps_roots": 1, "win_free_mb": 2048}}}, f)
    return w


def section(page, name):
    m = re.search(r"(?ms)^## %s: .*?(?=^## |\Z)" % name, page)
    return m[0] if m else ""


def glance(page, name):
    m = re.search(r"(?m)^\| \*\*%s\*\* \|.*$" % name, page)
    return m[0] if m else ""


def stamp_iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def plant_pass(w, name, n, lines, session=None, garbage=False):
    """A pass log whose first line names the transcript, and that transcript. `lines`: (seconds ago or None, kind, message)."""
    logs = os.path.join(w.logs_root, "ralph_" + name)
    session = session or "%s-pass-%d" % (name, n)
    with open(os.path.join(logs, "pass_%03d.jsonl" % n), "w") as f:
        f.write("this is not json\n" if garbage else json.dumps({"type": "system", "subtype": "init", "session_id": session}) + "\n")
    clone = os.path.join(w.root, "scratch", "BENCH", "ralph_" + name)
    with open(os.path.join(w.mod.project_dir(clone), session + ".jsonl"), "w") as f:
        for ago_s, kind, msg in lines:
            row = {"type": kind, "message": msg}
            if ago_s is not None:
                row["timestamp"] = stamp_iso(time.time() - ago_s)
            f.write(json.dumps(row, separators=(",", ":")) + "\n")     # the transcript's own spacing: the reader filters on it


def tool_call(tid, command):
    return {"content": [{"type": "tool_use", "id": tid, "name": "Bash", "input": {"command": command}}]}


def tool_done(tid):
    return {"content": [{"type": "tool_result", "tool_use_id": tid, "content": "ok"}]}


def plant_verdict(w, name, n, rows, answer, age):
    path = os.path.join(w.logs_root, "ralph_" + name, "blind_judge_verdict_pass%d.md" % n)
    with open(path, "w") as f:
        f.write("# Verdict\n\n| Line | Verdict | Sure |\n|---|---|---|\n")
        for line, verdict in rows:
            f.write("| `%s` | %s | High |\n" % (line, verdict))
        f.write("\n## Overall call\n\n%s, I would not show this.\n" % answer)
    os.utime(path, (time.time() - age, time.time() - age))


def plant_picture(mod, root):
    """A world for the picture: a good pass beside a broken log, a live pass with no times, a loop with no history, stops with and
    without a reason, loops at their limit, thin and thick judge history, two games on one machine, a watcher that is no loop."""
    w = World(mod, root)
    start = "LOOP start, 0 passes on record, 0 tokens"
    w.loop("goodloop", [(7200, start), (7200, "PASS 1 start, 0 tokens so far"), (3600, "PASS 1 end, rc 0, 800000 tokens, head abc"),
                        (3600, "PASS 2 start, 800000 tokens so far"), (1800, "PASS 2 end, rc 0, 900000 tokens, head def"),
                        (1800, "LOOP DONE_CLAIMED, 900000 tokens")], unit=None)
    plant_pass(w, "goodloop", 1, [(7100, "assistant", tool_call("a", "python.exe play.py step 3000")), (6500, "user", tool_done("a")),
                                  (6400, "assistant", tool_call("b", "sleep 300; tail run.log")), (6100, "user", tool_done("b")),
                                  (5700, "assistant", {"content": [{"type": "text", "text": "the model went quiet before this"}]}),
                                  (3700, "assistant", tool_call("c", "ls")), (3650, "user", tool_done("c"))])
    plant_pass(w, "goodloop", 2, [], garbage=True)
    w.loop("notimes", [(1800, start), (1800, "PASS 7 start, 0 tokens so far")], pass_n=None)
    plant_pass(w, "notimes", 7, [(None, "assistant", tool_call("a", "ls")), (None, "user", tool_done("a"))])
    w.loop("nohist", [(600, start)])
    w.loop("queuer", [(7200, start), (6000, "GAME_WAIT: a loop ahead has the game, no model running, 0 tokens"), (4800, "LOOP stopped: STOP file")],
           unit=None, stop="Conductor: planted\n")
    w.loop("stopwhy", [(3000, start), (2000, "LOOP stopped: STOP file")], unit=None, stop="Conductor: held for the two-game trial\nmore\n")
    w.loop("stopbare", [(3000, start), (2000, "LOOP stopped: STOP file")], unit=None, stop=True)
    w.loop("pausedoff", [(3000, start), (2000, "LOOP PAUSED_FOR_REVIEW at 10000000 tokens")], unit=None)
    w.loop("pausedon", [(3000, start), (2000, "LOOP PAUSED_FOR_REVIEW at 10000000 tokens")])
    w.loop("stoplimit", [(3000, start), (2000, "LOOP stopped: STOP file, 12000000 tokens")], unit=None, stop="Conductor: enough\n")
    w.loop("twojudges", [(9000, start), (2000, "LOOP DONE_CLAIMED, 5000000 tokens")], unit=None)
    plant_verdict(w, "twojudges", 1, [("bar_a", "TRUE"), ("bar_b", "FALSE")], "No", 5000)
    plant_verdict(w, "twojudges", 2, [("bar_a", "CANNOT TELL FROM THESE"), ("bar_b", "FALSE")], "No", 3000)
    w.loop("threejudges", [(9000, start), (2000, "LOOP DONE_CLAIMED, 5000000 tokens")], unit=None)
    plant_verdict(w, "threejudges", 1, [("bar_a", "FALSE"), ("bar_b", "FALSE"), ("bar_c", "FALSE")], "No", 7000)
    plant_verdict(w, "threejudges", 2, [("bar_a", "FALSE"), ("bar_b", "TRUE"), ("bar_c", "FALSE")], "No", 5000)
    plant_verdict(w, "threejudges", 3, [("bar_a", "FALSE"), ("bar_b", "TRUE"), ("bar_c", "TRUE")], "No", 3000)
    w.units["rm-pyre-relaunch-at-limit"] = {"Id": "rm-pyre-relaunch-at-limit.service", "WorkingDirectory": "!/home/x", "ActiveState": "active", "SubState": "running",
                                            "Result": "success", "ControlGroup": "", "ExecStart": "bash -c 'ralph/loop.sh'", "Environment": "",
                                            "ActiveEnterTimestampMonotonic": "1000000"}
    mod.list_units = lambda sources: w.units
    mod.cgroup_processes = lambda props: (False, [])
    now = time.time()

    def read_machine(name):
        if name == "SteveDesktop":
            return {"read_at": now, "game": True, "ports": ["5174"], "games": [{"pid": "1", "ports": ["5174"]}, {"pid": "2", "ports": ["5175"]}], "tps_roots": 1,
                    "wsl_free_mb": 4096, "sessions": [{"start": now - 7000, "end": now - 100, "pid": "1", "stalls": [[now - 3000, 2.5]]}, {"start": now - 6000, "end": now - 100, "pid": "2", "stalls": []}]}
        return {"read_at": now, "game": False, "tps_roots": 1, "wsl_free_mb": 4096}

    mod.read_machine = read_machine
    mod.read_tailscale = lambda: []
    mod.read_background = lambda sources: {"detached": [], "failed": [], "watchers": 0, "claude": __import__("collections").Counter()}
    return w


def picture_words(picture):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", picture)))


def scenarios(mod):
    """Run every check on this module; return the names of those that failed."""
    fails = []

    def check(name, ok):
        if not ok:
            fails.append(name)

    # An empty ControlGroup is an ended unit. Walking from the root would list the whole machine.
    check("empty_cgroup_guard", mod.cgroup_processes({"ControlGroup": ""}) == (False, []))

    root = tempfile.mkdtemp(prefix="artisan_now_test_")
    try:
        plant(mod, root)
        page, phone, state = mod.build()
        # fault: a stale log. The unit is up and the model alive, and nothing has been written for two hours.
        stale = section(page, "stale")
        check("stale_log_is_stuck", stale.startswith("## stale: STUCK") and "Nothing written for 2.0 h" in stale)
        check("stale_log_needs_you", re.search(r"(?m)^\d+\. \*\*stale looks stuck", page) is not None)
        check("stale_source_age_shown", re.search(r"(?m)^\| live pass log, stale \| 2\.0 h \|", page) is not None)
        # fault: a dead unit, whose log stops mid-pass; and a failed one.
        check("dead_unit_said", section(page, "deadun").startswith("## deadun: DEAD") and "**deadun is dead:**" in page)
        check("failed_unit_said", section(page, "failedun").startswith("## failedun: DEAD") and "**failedun is dead:** its unit rm-ralph-failedun failed (exit-code)" in page)
        # fault: missing files say UNMEASURED with the reason, never 0.
        nolog = section(page, "nolog")
        check("missing_events_unmeasured", nolog.startswith("## nolog: UNMEASURED") and "events.log" in nolog)
        check("missing_events_source", re.search(r"(?m)^\| events log, nolog \| \*\*UNMEASURED\*\* \| missing", page) is not None)
        check("missing_events_tokens", "UNMEASURED" in glance(page, "nolog").split("|")[5])
        check("missing_progress_unmeasured", "Progress: UNMEASURED" in nolog and "PROGRESS.md" in nolog)
        nopass = section(page, "nopasslog")
        check("missing_pass_log_tokens", "**Tokens:** UNMEASURED (pass 3 log" in nopass and "2.00M" not in nopass.split("### Doing")[0])
        check("missing_pass_log_phone", "nopasslog: working, Archmagi, tokens UNMEASURED" in phone)
        for label, needle in (("accounts", "Account readings: UNMEASURED"), ("fault", "CPU fault monitor: UNMEASURED"),
                              ("bridge", "Bridge lock: UNMEASURED"), ("tailscale", "Tailscale: UNMEASURED (planted")):
            check("missing_%s_unmeasured" % label, needle in page)
        # fault: an old reading must not pass for now.
        check("old_machine_read_labelled", "**UNMEASURED now:** ssh: planted refusal" in page and "last good read, 60 min ago, not now" in page)
        check("old_machine_read_kept_old", state["machines"]["SteveDesktop"]["read_at"] < time.time() - 3000)
        # fault: a stale flag.
        check("stop_with_unit_warned", "STOP is set" in section(page, "stopflag") and "stopflag has STOP set" in page)
        # stays green.
        healthy = section(page, "healthy")
        check("healthy_stays_working", healthy.startswith("## healthy: working") and "**healthy" not in page.split("## Loops at a glance")[0])
        check("healthy_tokens_add_up", "2.50M of 10.00M (25%); this pass 500k" in healthy)
        check("healthy_bars_counted", "**1 true, 0 false, 1 unseen**" in healthy)
        check("healthy_doing_now", "Build the planted mod" in healthy and "Working on the planted thing" in healthy)
        check("waiter_names_who", section(page, "waiter").startswith("## waiter: waiting for game") and "gives way to rm-ralph-healthy, which is active" in page)
        check("claim_is_not_acceptance", section(page, "claimed").startswith("## claimed: DONE CLAIMED") and "blind judge owed" in page)
        check("stamp_present", re.search(r"Generated \w+ \d+, \d\d:\d\d:\d\d \w+", page) is not None)
        check("first_line_is_state", page.splitlines()[4].startswith("**9 loops:"))
        # the headline's two figures with nothing to read them from (no learned.md, a loop with no log): UNMEASURED, never 0
        head = page.splitlines()[4]
        check("headline_figures_unmeasured", "Accepted: UNMEASURED." in head and "Accepted: 0" not in head and "Waited for a game: UNMEASURED" in head)

        # the tally is tally.py's arithmetic, read in pieces, with a half-written last line left for later
        path = os.path.join(root, "tally.jsonl")
        with open(path, "w") as f:
            f.write(usage_line("a", inp=100, out=10, cw=20, cr=1000) + "\n" + usage_line("a", inp=100, out=20, cw=20, cr=1000) + "\n")
        cache = {}
        check("tally_weighs_cache_reads", mod.tally_file(path, cache) == 100 + 20 + 20 + 100)
        torn = usage_line("b", inp=7, out=0)
        with open(path, "a") as f:
            f.write(usage_line("c", inp=3, out=0) + "\n" + torn[:20])
        before = mod.tally_file(path, cache)
        with open(path, "a") as f:
            f.write(torn[20:] + "\n")
        check("tally_keeps_torn_line", before == 243 and mod.tally_file(path, cache) == 250)

        # dates walk back over midnight
        ev = os.path.join(root, "ev.log")
        with open(ev, "w") as f:
            f.write("23:50:00 PST PASS 1 start, 5 tokens so far\n00:10:00 PST PASS 1 end, rc 0, 9 tokens, head a\n")
        stamp = time.mktime(time.strptime(time.strftime("%Y-%m-%d") + " 00:10:02", "%Y-%m-%d %H:%M:%S"))
        os.utime(ev, (stamp, stamp))
        rows = mod.read_events(ev)
        check("events_cross_midnight", round(rows[1][0] - rows[0][0]) == 1200)

        # a pass killed under its shell, with a fresh LOOP start after it
        rows, cur, _ = mod.passes_from_events([(1, "PASS 1 start, 5 tokens so far"), (2, "LOOP start, 1 passes on record, 9 tokens"), (3, "PASS 2 start, 9 tokens so far")])
        check("lost_pass_marked", rows[0]["lost"] and rows[0]["t_end"] == 9 and cur["n"] == 2)

        # the reader finds a repeating freeze, with Windows out of reach
        tps = os.path.join(root, "tps")
        os.makedirs(tps)
        utc = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        with open(os.path.join(tps, "tps_x_y_1_000.jsonl"), "w") as f:
            for i in range(12):
                f.write(json.dumps({"kind": "sample", "utc": utc, "state": "run", "speed": "Superfast", "ratio": 0.9, "tps": 300,
                                    "worst": [{"tg": 1000 + 250 * i, "ms": 900, "top": "mapComp"}, {"tg": 1001 + 250 * i, "ms": 5, "top": "x"}]}) + "\n")
        reader = mod.READER.replace('W = "/mnt/c/Windows/System32/"', 'W = "/nonexistent/"')
        check("reader_patch_applied", reader != mod.READER)
        p = subprocess.run([sys.executable, "-"], input=reader, capture_output=True, text=True, timeout=30,
                           env=dict(os.environ, ARTISAN_TPS_ROOT=tps))
        d = json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else {}
        check("reader_finds_freeze", (d.get("period") or {}).get("ticks") == 250 and d["period"]["ms"] == 900)
        check("reader_no_tasklist_is_none", "game" in d and d["game"] is None and d.get("errors"))
        lines = mod.machine_lines("x", {"fresh": True, "data": d})
        check("page_says_freeze", any("Repeating freeze: about 900 ms every 250 ticks" in x for x in lines))
        check("page_says_no_tasklist", any(x.startswith("Game: UNMEASURED") for x in lines))
        # a real but even load is not a freeze
        with open(os.path.join(tps, "tps_x_y_1_000.jsonl"), "w") as f:
            for i in range(12):
                f.write(json.dumps({"kind": "sample", "utc": utc, "state": "run", "ratio": 1.0, "tps": 60,
                                    "worst": [{"tg": 1000 + 250 * i, "ms": 20, "top": "x"}]}) + "\n")
        p = subprocess.run([sys.executable, "-"], input=reader, capture_output=True, text=True, timeout=30,
                           env=dict(os.environ, ARTISAN_TPS_ROOT=tps))
        d = json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else {"period": "no reading"}
        check("reader_quiet_on_smooth_game", not d.get("period"))

        # the page's age check, and an atomic write leaving no litter
        target = os.path.join(mod.OUT_DIR, "ARTISAN_NOW.md")
        mod.write_atomic(target, page)
        check("atomic_write_clean", open(target, encoding="utf-8").read() == page and not [n for n in os.listdir(mod.OUT_DIR) if ".tmp." in n])
        with contextlib.redirect_stdout(io.StringIO()):
            fresh = mod.check()
            os.utime(target, (time.time() - 600, time.time() - 600))
            old = mod.check()
            os.unlink(target)
            gone = mod.check()
        check("check_flags_dead_timer", (fresh, old, gone) == (0, 1, 1))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # the picture: what it knows it draws, what it can't read it says, and it never draws a trend it hasn't earned
    root = tempfile.mkdtemp(prefix="artisan_now_pic_")
    try:
        plant_picture(mod, root)
        mod.LEARNED = os.path.join(root, "learned.md")
        with open(mod.LEARNED, "w") as f:
            f.write("**Acceptances: 3, as of 2026-11-07,** across two pieces of work.\n")
        page, phone, state = mod.build()
        lines = page.splitlines()
        pic_line = lines[2]
        # the headline's figures: the Scoreboard's own count, and the one 20 min queue the picture draws, on page and phone alike
        check("headline_figures", "Accepted: 3. Waited for a game: 0h 20m, all loops added." in lines[4] and "Scoreboard: Acceptances: 3, as of 2026-11-07" in page
              and phone.splitlines()[1] == lines[4].strip("*"))
        # overlapping queue stretches count once per loop, loops add, a loop that can't be read blanks the sum, and 7h 05m is written so
        real_gaps = mod.gaps_of
        try:
            mod.gaps_of = lambda rec: [(0, 100, "queue"), (50, 200, "queue"), (500, 600, "queue"), (0, 999, "claimed")]
            check("headline_waited_adds_once", mod.wait_total([{"unmeasured": {}}]) == 300 and mod.wait_total([{"unmeasured": {}}, {"unmeasured": {}}]) == 600
                  and mod.wait_total([{"unmeasured": {"events": "gone"}}]) is None and mod.hm(25500) == "7h 05m")
        finally:
            mod.gaps_of = real_gaps
        pic = picture_words(pic_line)
        check("pic_under_title", lines[0] == "# Artisan now" and pic_line.startswith("<div><svg") and pic_line.endswith("</svg></div>"))
        block = page[page.index("<div><svg"): page.index("</svg></div>")] if "</svg></div>" in page else "\n"
        check("pic_typora_no_blank_line", "\n" not in block and not lines[1].strip() and not lines[3].strip() and "<details" not in page)
        # a broken pass log is hatched and named, with no layers drawn for it
        check("pic_broken_log_said", "Can't draw pass 2: its log can't be read" in pic and "url(#arcHatch)" in pic_line)
        check("pic_broken_log_no_false_data", re.search(r"pass 2, \S+ \S+ to ", pic) is None)
        check("pic_good_pass_drawn", "pass 1, " in pic and "game 10 min" in pic and "waiting 5 min" in pic)
        # a live pass whose transcript has no times
        check("pic_no_times_said", "Can't draw pass 7: no times in its log" in pic)
        check("pic_no_times_no_false_data", re.search(r"pass 7, \S+ \S+ to ", pic) is None)
        # no history at all
        check("pic_empty_history_said", "No passes on record yet." in pic and "nothing to judge by yet" in pic)
        # thin history gets words, not a trend
        check("pic_two_judges_no_trend", "Judge said no: 1 of 2, then 0 of 2 lines passed." in pic and "Two judgements are no trend." in pic and "1 line refused both times." in pic)
        check("pic_three_judges_trend", "Refusals shrinking over 3 judgements." in pic)
        def said(*trues):
            return mod.better_words({"open_pass": None, "verdicts": [], "arc": [{"n": i, "end": 0, "bars": {"true": t, "false": 0, "unseen": 9 - t}} for i, t in enumerate(trues)]})[0]
        check("pic_one_count_no_trend", said(3) == "too few to say" and said(3, 4) == "too few to say")
        check("pic_own_rise_says_whose", said(3, 4, 5) == "only by its own count" and said(5, 5, 5) == "not by its own count" and said(5, 4, 3) == "not by its own count")
        # a stall: the model silent past the limit with nothing open
        g = next(a for a in mod.read_arc({"logs": os.path.join(mod.LOG_ROOT, "ralph_goodloop"), "clone": os.path.join(root, "scratch", "BENCH", "ralph_goodloop"), "gate": {},
                                          "passes": [{"n": 1, "start": time.time() - 7200, "end": time.time() - 3600, "head": None}]}, {}, time.time() + 9))
        check("arc_stall_is_idle", g["sec"].get("idle", 0) >= 1900)
        check("arc_game_and_wait", 590 <= g["sec"].get("game", 0) <= 610 and 290 <= g["sec"].get("wait", 0) <= 310)
        check("arc_adds_up", abs(sum(g["sec"].values()) - 3600) <= 2)
        # a finished pass is kept: its transcript can go and the picture still draws it
        key = "%s#1" % os.path.join(mod.LOG_ROOT, "ralph_goodloop")
        check("arc_finished_kept", state["arc"].get(key, {}).get("done") and "walker" not in state["arc"][key])
        # STOP's first line is its reason, and a reason is not a call for him
        needs = page.split("## Needs you")[1].split("## Loops at a glance")[0]
        check("stop_reason_shown", "Conductor: held for the two-game trial" in section(page, "stopwhy") and "Conductor: held for the two-game trial" in pic)
        check("stop_reason_not_needs", "stopwhy" not in needs)
        check("stop_bare_needs", "**stopbare has stopped:**" in needs)
        # a loop at its limit always wants him, whatever its log calls the stop
        check("limit_paused_off_needs", "**pausedoff reached its limit" in needs and section(page, "pausedoff").startswith("## pausedoff: PAUSED FOR REVIEW"))
        check("limit_paused_on_needs", "**pausedon reached its limit" in needs)
        check("limit_stop_needs", "**stoplimit reached its limit" in needs)
        # two games on one machine, both ports, on page, phone and picture
        check("two_games_page", "**2 games running**, ports 5174 and 5175." in page)
        check("two_games_phone", "SteveDesktop: 2 games up, ports 5174 and 5175" in phone)
        check("two_games_picture", "2 games running, ports 5174 and 5175" in pic and "Red: 1 freeze of 1 s or more." in pic)
        check("watcher_not_a_loop", "relaunch" not in pic and "## pyre-relaunch" not in page)
        # the classifier, on what the logs really hold
        k = mod.bash_kind
        check("kind_heredoc_body_ignored", k("cat > probe.py <<'EOF'\nbridge take; python.exe; sleep 100\nEOF") == "code")
        check("kind_wait", k("sleep 240; cat out.log") == "wait" and k("timeout 590 tail --pid=12 -f /dev/null") == "wait" and k("python3 - <<'E'\nwhile time.time()-t<400: pass\nE") == "wait")
        check("kind_game", k("python.exe src/play.py step 300") == "game" and k("ralph/steve.sh run 'x'") == "game")
        check("kind_build", k("python3 src/Utils/winbuild.py Mod 2>&1 | tail -1") == "build" and k("python3 deploy_custom_mods.py --mod X --apply") == "build" and k("python.exe src/x/selftest_y.py") == "build")
        check("kind_think", k("grep -n foo bar.cs | head") == "think" and k("cat notes.md") == "think")
        # verdict parsing
        v = mod.parse_verdict(os.path.join(mod.LOG_ROOT, "ralph_twojudges", "blind_judge_verdict_pass2.md"))
        check("verdict_parsed", v["lines"] == 2 and v["passed"] == 0 and v["answer"] == "no" and v["short"] == ["bar_a", "bar_b"])
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return fails


# Each mutant blinds one check; (source fragment, replacement, the check that must go red).
MUTANTS = [
    ('quiet > QUIET_STUCK_S and not rec["procs"]', 'False', "stale_log_is_stuck"),
    ('self.rows.append((name, now_s() - m, None))', 'self.rows.append((name, 0, None))', "stale_source_age_shown"),
    ('return "dead", "no unit is running it', 'return "stopped", "no unit is running it', "dead_unit_said"),
    ('if failed:\n            return "dead"', 'if False:\n            return "dead"', "failed_unit_said"),
    ('un["events"] = "cannot read', 'un["ignored"] = "cannot read', "missing_events_unmeasured"),
    ('            rec["total"] = None\n', '            rec["total"] = op["t_start"]\n', "missing_pass_log_phone"),
    ('un["live tokens"] = "pass %d log', 'un["ignored"] = "pass %d log', "missing_pass_log_tokens"),
    ('un["progress"] = "no %s" % path', 'pass', "missing_progress_unmeasured"),
    ('out[name] = {"why": r["why"], "fresh": False, "data": saved.get(name)}',
     'out[name] = {"why": "", "fresh": True, "data": saved.get(name)}', "old_machine_read_labelled"),
    ('w.append("STOP is set', 'str("STOP is set', "stop_with_unit_warned"),
    ('+ u.get("cache_read_input_tokens", 0) // 10', '+ u.get("cache_read_input_tokens", 0)', "tally_weighs_cache_reads"),
    ('c["offset"] += end + 1', 'c["offset"] += len(raw)', "tally_keeps_torn_line"),
    ('            day -= dt.timedelta(days=1)\n', '            day -= dt.timedelta(days=0); break\n', "events_cross_midnight"),
    ('cur.update(lost=True, end=t, t_end=int(hit[2]))\n                cur = None', 'cur = None', "lost_pass_marked"),
    ('    if not cg:\n        return False, []\n', '', "empty_cgroup_guard"),
    ('if p >= 2 and fit >=', 'if False and fit >=', "reader_finds_freeze"),
    ('big = sorted(k for k, x in wr.items() if x["ms"] >= 150)', 'big = sorted(wr)', "reader_quiet_on_smooth_game"),
    ('return 1 if age > STALE_PAGE_S else 0', 'return 0', "check_flags_dead_timer"),
    ('"".join(self.parts)))', '"\\n\\n".join(self.parts)))', "pic_typora_no_blank_line"),
    ('raise Unmeasured("its log can\'t be read")\n    if not sid', 'return "x"\n    if not sid', "pic_broken_log_said"),
    ('row["broken"] = str(e)\n', 'row.update(sec={"game": 600}, bins="G")\n', "pic_broken_log_no_false_data"),
    ('word = "not by its own count" if recent[-1] <= recent[0] else', 'word = "only by its own count" if recent[-1] <= recent[0] else', "pic_own_rise_says_whose"),
    ('if walker["lines"] and not walker["stamped"]:', 'if False:', "pic_no_times_said"),
    ('if not arc and not rec.get("arc_why"):', 'if False:', "pic_empty_history_said"),
    ('if len(js) < 3:', 'if False:', "pic_two_judges_no_trend"),
    ('if len(pts) >= 3:', 'if len(pts) >= 1:', "pic_one_count_no_trend"),
    ('if gap > STALL_S:', 'if False:', "arc_stall_is_idle"),
    ('outer = HEREDOC.sub(" ", command)', 'outer = command', "kind_heredoc_body_ignored"),
    ('elif r["state"] == "stopped" and not r.get("stop_reason"):', 'elif r["state"] == "stopped":', "stop_reason_not_needs"),
    ('if line.strip():\n                return short(line, 140)', 'if False:\n                return short(line, 140)', "stop_reason_shown"),
    ('return bool(r.get("limit") and r.get("total") is not None and r["total"] >= r["limit"])', 'return False', "limit_stop_needs"),
    ('    if text.startswith("LOOP PAUSED_FOR_REVIEW"):\n        return "paused for review", "it reached its token limit and waits for your word"\n    if rec["unmeasured"]', '    if rec["unmeasured"]', "limit_paused_on_needs"),
    ('if len(games) > 1:', 'if False:', "two_games_page"),
    ('continue    # a watcher', 'pass    # a watcher', "watcher_not_a_loop"),
    ('row["done"] = True\n            if p.get("head")', 'row["done"] = False\n            if p.get("head")', "arc_finished_kept"),
    ('"UNMEASURED" if accepted is None else accepted', '0 if accepted is None else accepted', "headline_figures_unmeasured"),
    ('if (rec.get("unmeasured") or {}).get("events") or (rec.get("unmeasured") or {}).get("loop"):', 'if False:', "headline_figures_unmeasured"),
    ('return int(acceptance_line()[1])', 'return 0', "headline_figures"),
    ('for g in gaps_of(rec) if g[2] == "queue"):', 'for g in gaps_of(rec)):', "headline_figures"),
    ('a = a if reach is None else max(a, reach)', 'a = a', "headline_waited_adds_once"),
    ('return "%dh %02dm" % (h, m)', 'return "%dh %dm" % (h, m)', "headline_waited_adds_once"),
]


def run_mutants(names=None):
    bad = []
    for old, new, expect in MUTANTS:
        if names and expect not in names:
            continue
        if old not in SOURCE:
            bad.append("mutant no longer applies: %s" % expect)
            continue
        mutated = SOURCE.replace(old, new)
        try:
            fails = scenarios(load(mutated))
        except Exception as e:  # a crash is not the check's red
            bad.append("mutant crashed instead of failing %s: %s: %s" % (expect, type(e).__name__, e))
            continue
        if expect not in fails:
            bad.append("mutant survived, %s stayed green (red were: %s)" % (expect, fails))
    return bad


def main():
    # The control: unmutated must be fully green, or every mutant result means nothing.
    fails = scenarios(load(SOURCE))
    for f in fails:
        print("FAIL %s" % f)
    if fails:
        print("selftest_artisan_now: %d checks red on the unmutated sheet" % len(fails))
        return 1
    bad = run_mutants()
    for b in bad:
        print("FAIL %s" % b)
    if bad:
        return 1
    print("selftest_artisan_now: OK (all checks green, %d mutants each caught by name)" % len(MUTANTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
