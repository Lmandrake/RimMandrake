#!/usr/bin/env python3
"""selftest_running_now.py - running_now.py offline, on fixtures (no systemd, no Windows, no state files).

Covers: a source that cannot be read prints UNMEASURED and never a 0 count; an unmatched python process is listed under
'Not recognised' with its pid; a matched one is not; the write is atomic (no temp left, a failed build keeps the old
page and the next good page carries a STALE banner); history reports how little it covers before 24 h.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import running_now as R  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


NOW = 1793741698.0


class Fake(R.Env):
    def __init__(self, ps="", units=None, timers=None, files=None, cg=None, fail=()):
        self.ps_text, self.units, self.timers, self.files, self.cg, self.fail = ps, units, timers, files or {}, cg or {}, fail
        self.clock = NOW

    def now(self):
        return self.clock

    def ps(self):
        if "ps" in self.fail:
            raise R.Unmeasured("ps broke")
        return self.ps_text

    def cgroup(self, pid):
        return self.cg.get(pid, "0::/user.slice/user-1000.slice/user@1000.service/app.slice/x.service\n")

    def cwd(self, pid):
        return "/home/mandrake/rm/bench"

    def units_json(self):
        if "units" in self.fail:
            raise R.Unmeasured("systemctl broke")
        return self.units or []

    def timers_json(self):
        if "timers" in self.fail:
            raise R.Unmeasured("systemctl broke")
        return self.timers or []

    def tick_limit_text(self):
        return "TimeoutStartUSec=20min"

    def last_failure(self, unit):
        return ""

    def tasklist(self):
        if "tasklist" in self.fail:
            raise R.Unmeasured("tasklist.exe exited 1")
        return '"RimWorldWin64.exe","1","Console","1","4,000 K"\n"codex.exe","2","Console","1","9 K"\n"codex.exe","3","Console","1","9 K"\n'

    def read_json(self, path):
        if path in self.files:
            return self.files[path]
        if path.endswith("running_now_families.json") or path.startswith(tempfile.gettempdir()):
            return json.load(open(path))
        raise OSError("no such file " + path)

    def read_text(self, path):
        if path in self.files:
            return self.files[path] if isinstance(self.files[path], str) else json.dumps(self.files[path])
        if path.startswith(tempfile.gettempdir()):
            return open(path).read()
        raise OSError("no such file " + path)

    def mtime(self, path):
        raise OSError("no such file " + path)

    def count_dir(self, path):
        raise OSError("no dir " + path)


def build(env, state=None, hist=None):
    return R.build(env, state if state is not None else {}, hist or [])[0]


PS = "  4242  1  900  105.0 python3 python3 /somewhere/match.py --loop\n  4343  1  50  1.0 python3 python3 /home/mandrake/rm/dispatch/x/claude_account_page.py\n"

# 1. everything unreadable: UNMEASURED, and no invented zero
page = build(Fake(fail=("ps", "units", "timers", "tasklist")))
head = page.split("\n## ")[0]
check("unreadable sources say UNMEASURED in the headline", head.count("UNMEASURED") >= 4)
check("no '0 AI agent' / '0 game' invented when sources are dead", "0 AI agent" not in head and "0 game" not in head and "0 Codex" not in head)
check("unreadable Dispatcher state is UNMEASURED, not 'healthy'", "Dispatcher last tick: **UNMEASURED" in page and "healthy" not in page)

# 2. unrecognised process shown with its pid, recognised one not
page = build(Fake(ps=PS))
sec = page.split("## Not recognised")[1].split("## Busiest")[0]
check("unmatched python process listed with pid", "pid 4242" in sec and "match.py" in sec)
check("matched account page is not listed as unrecognised", "4343" not in sec)
check("headline counts it as not recognised", "1 not recognised" in page.split("\n## ")[0])

# 3. a Dispatcher far behind is a loud banner
disp = {"last_tick": "2026-11-03T20:00:00Z"}
page = build(Fake(files={R.AGENT + "/dispatcher/state.json": disp}))
check("old Dispatcher tick raises DISPATCHER NOT TICKING", "DISPATCHER NOT TICKING" in page)

# 4. history honesty
hist = [{"t": NOW - 600, "n": 5, "f": {}}, {"t": NOW - 60, "n": 9, "f": {}}]
line, rows = R.window_stats(hist, NOW, 86400, "24 h")
check("short history says it does not yet cover 24 h", "not yet a full 24 h" in line and "min 5 / median 7 / max 9" in line)
check("empty history says no history yet", "no history yet" in R.window_stats([], NOW, 86400, "24 h")[0])

# 5. atomic write + failed run leaves the old page, next good run says STALE
with tempfile.TemporaryDirectory() as d:
    R.OUT_DIR, R.OUT, R.HIST, R.STATE = d, d + "/RUNNING_NOW.md", d + "/h.jsonl", d + "/s.json"
    env = Fake(ps=PS)
    rc, _ = R.run(env)
    first = open(R.OUT).read()
    check("good run writes the page and no temp file is left", rc == 0 and "What is running" in first and not [f for f in os.listdir(d) if ".tmp." in f])
    check("good run appended one history sample", len(open(R.HIST).read().splitlines()) == 1)
    bad = Fake(ps=PS)
    bad.families = lambda: (_ for _ in ()).throw(ValueError("table broke"))
    bad.clock = NOW + 400
    rc, _ = R.run(bad)
    check("failed run returns 1 and keeps the old page byte for byte", rc == 1 and open(R.OUT).read() == first)
    check("failed run records why", "table broke" in json.load(open(R.STATE)).get("last_error", ""))
    good = Fake(ps=PS)
    good.clock = NOW + 800
    rc, _ = R.run(good)
    check("next good page carries the STALE since banner", "STALE since" in open(R.OUT).read())
    check("the page records its own update epoch for --check", "updated_epoch=%d" % int(NOW + 800) in open(R.OUT).read())

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
