#!/usr/bin/env python3
"""selftest_artisan_now.py: plant a stale log, a dead unit and missing files, and see the sheet say so.

A planted world of loops runs through the whole page build with systemd and the machines stubbed out, and each
fault must show in the words the owner reads. Healthy loops in the same world must stay quiet. Then every check
is shown able to fail: a mutant of artisan_now.py per check, built in memory, must go red by that check's name.
No game, no bridge, no ssh, nothing outside a temp folder.
"""

import contextlib
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
            open(os.path.join(logs, "STOP"), "w").close()
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
        check("first_line_is_state", page.splitlines()[2].startswith("**9 loops:"))

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
