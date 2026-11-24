#!/usr/bin/env python3
"""selftest_running_now.py - running_now.py offline, on fixtures (no systemd, no Windows, no ssh, no state files).

Covers: a source that cannot be read says UNMEASURED and never a 0 count; the tree accounts for every process counted;
an unmatched python process is shown under NOT RECOGNISED with its pid; idle under a brake is the first, red thing on
the page; the page is on disk before ssh is tried and a dead ssh changes nothing but the route dots; the
write is atomic, a failed build keeps the old page and the next good page carries a STALE banner; no blank line sits
inside the details block (Typora would end the block there and spill the rest).
The fuel gauge: every account's week left and time to reset with AHEAD/EQUAL/BEHIND against the spend left; a stale or
unreadable reading, or a burn with no honest rate, says UNMEASURED.
"""
import json
import os
import re
import subprocess
import sys
import time
import tempfile
import xml.etree.ElementTree as R_ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import running_now as R  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


NOW = 1793741698.0
WORKER_CG = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/rm-role-builder-1793741600.service\n"
DISPATCH_STATE = R.AGENT + "/dispatcher/state.json"
STEWARD = R.TESTQ + "/steward.json"


def lockrow(g, state, seat="", purpose=""):
    """One game's reading in game_lock.query's shape (the fields running_now reads)."""
    name = {"a": "ArchBig", "b": "ArchSmall"}[g]
    line = {"FREE": "%s: FREE", "HELD": "%s: HELD by " + seat, "HIS_HOLD": "%s: HIS HOLD: pipe off",
            "UNKNOWN": "%s: COULD NOT LOOK: the lock is UNREADABLE"}[state] % name
    return {"game": g, "state": state, "seat": seat or None, "purpose": purpose or None, "line": line}


FREE2 = [lockrow("a", "FREE"), lockrow("b", "FREE")]


class Fake(R.Env):
    """Every door to the world is shut unless a fixture opens it."""

    def __init__(self, ps="", units=None, timers=None, files=None, cg=None, fail=(), dirs=None):
        self.ps_text, self.units, self.timers, self.files, self.cg, self.fail = ps, units, timers, files or {}, cg or {}, fail
        self.dirs = dirs or {}
        self.clock = NOW
        self.bridge, self.fleet, self.mods = None, None, None
        self.locks = None
        self.calls = []
        self.out = None
        self.names = []

    def now(self):
        return self.clock

    def self_pid(self):
        return 999999

    def run(self, argv, timeout=20):
        raise R.Unmeasured("no commands in a selftest: %s" % argv[0])

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

    def tasklist(self):
        if "tasklist" in self.fail:
            raise R.Unmeasured("tasklist.exe exited 1")
        return '"RimWorldWin64.exe","1","Console","1","4,000 K"\n"codex.exe","2","Console","1","9 K"\n"codex.exe","3","Console","1","9 K"\n'

    def read_json(self, path):
        if path in self.files:
            return self.files[path]
        if path.endswith("running_now_families.json") or path.startswith(tempfile.gettempdir()):
            with open(path) as f:
                return json.load(f)
        raise OSError("no such file " + path)

    def read_text(self, path):
        if path in self.files:
            return self.files[path] if isinstance(self.files[path], str) else json.dumps(self.files[path])
        if path.startswith(tempfile.gettempdir()):
            with open(path) as f:
                return f.read()
        raise OSError("no such file " + path)

    def read_tail(self, path, n):
        return self.read_text(path), False

    def account_names(self):
        return self.names


    def mtime(self, path):
        if path in self.files:
            return NOW - 5
        raise OSError("no such file " + path)

    def listdir(self, path):
        if path in self.dirs:
            return self.dirs[path]
        raise OSError("no dir " + path)

    def steve_probe(self):
        self.calls.append(("ssh", os.path.exists(R.OUT) and "updated_epoch=%d" % int(self.clock) in open(R.OUT).read()))
        if "ssh" in self.fail:
            raise R.Unmeasured("ssh exited 255: no route")
        return "up=100.0\nload=0.5\ncores=18\nstat=cpu 10 0 10 80 0 0 0 0 0 0\nram=1000 64000\ndisk=900 1000\ngame=0\n"

    def tailscale_status(self):
        raise R.Unmeasured("no tailscale in a selftest")

    def port_open(self, host, port=22):
        return "ssh" not in self.fail

    # the doors this page added: shut unless a test opens one, so a selftest never reads this machine
    def local_stats(self):
        raise R.Unmeasured("no machine in a selftest")

    def bridge_events(self):
        if self.bridge is None:
            raise R.Unmeasured("no ledger in a selftest")
        return self.bridge

    def conductor_helpers(self, pid):
        raise R.Unmeasured("no transcript in a selftest")

    def game_locks(self):
        if self.locks is None:
            raise R.Unmeasured("no driver lock in a selftest")
        return self.locks

    def fleet_gather(self, now):
        if self.fleet is None:
            raise R.Unmeasured("no ledger in a selftest")
        return self.fleet

    def mods_status(self):
        if self.mods is None:
            raise R.Unmeasured("no modcheck in a selftest")
        return self.mods


def page_of(env, state=None, hist=None):
    return R.build(env, state if state is not None else {}, hist or [])[0]


def before_svg(page):
    return page.split("<div><svg")[0]


def fence(page):
    return page.split("```\n")[1]


PS = ("  100  1  900  1.0 systemd /lib/systemd/systemd --user\n"
      "  4242  100  900  105.0 python3 python3 /somewhere/match.py --loop\n"
      "  4343  100  50  1.0 python3 python3 /home/mandrake/rm/dispatch/x/claude_account_page.py\n"
      "  5000  100  70  9.0 claude claude -p work\n"
      "  5001  5000  60  0.0 python3 python3 tool.py\n"
      "  5002  5000  60  0.0 bash bash -c x\n")
WORKER = {5000: WORKER_CG, 5001: WORKER_CG, 5002: WORKER_CG}

# 1. everything unreadable: UNMEASURED, and no invented zero
page = page_of(Fake(fail=("ps", "units", "timers", "tasklist")))
head = before_svg(page)
check("unreadable sources are listed as UNMEASURED at the top", "UNMEASURED this minute" in head and head.count("UNMEASURED") >= 4)
check("no invented zero: no 'bridge FREE'", "bridge FREE" not in head)
check("unreadable Dispatcher is UNMEASURED and not a green age", "Dispatcher UNMEASURED" in head or "last tick UNMEASURED" in page)
check("the tree says UNMEASURED and not 0 processes", "UNMEASURED" in fence(page) and "TOTAL 0" not in fence(page))

# 2. the tree accounts for every process counted
env = Fake(ps=PS, cg=WORKER)
p = R.gather(env, {})
lines, roots = R.tree_lines(p)
check("every process counted lands in exactly one root", p["tree"]["total"] >= 5 and roots == p["tree"]["total"])
text = "\n".join(lines)
check("the tree's TOTAL line shows the same sum", "TOTAL %d Linux processes" % roots in text)
check("no tree line outgrows the code fence", max(len(x) for x in lines) <= 84)
env = Fake(ps=PS, cg=WORKER)
far = R.gather(env, {})
moved = next(x for x in far["tree"]["groups"].values() if x["family"] == "roles")
moved.update(family="seats", name="CONDUCTOR", cwd="/somewhere/else", model="o", who="CONDUCTOR", unit="x", age=1.0)
check("a Conductor sitting outside the clones is counted once", R.tree_lines(far)[1] == far["tree"]["total"])

# 3. a role run shows its unit and sums its child processes
check("role row sums its child processes", re.search(r"claude 1 .*= 3", text) is not None)
check("heading counts the role run", "ROLE RUNS  1 running" in text)

# 4. unmatched process shown with its pid; matched one not
page = page_of(Fake(ps=PS))
nr = fence(page).split("NOT RECOGNISED")[1]
check("unmatched python process listed with pid", "pid 4242" in nr and "match.py" in nr)
check("matched account page is not listed as unrecognised", "4343" not in nr)
check("the strip raises it", "NOT RECOGNISED" in before_svg(page))

# 6. a Dispatcher far behind leads the strip
page = page_of(Fake(files={DISPATCH_STATE: {"last_tick": "2026-11-03T20:00:00Z"}}))
check("old Dispatcher tick raises DISPATCHER NOT TICKING", "DISPATCHER NOT TICKING" in before_svg(page))

# 7. who drives each game: one row per game, from its driver lock (game_lock.query_all), never a glance file
def with_locks(rows, **kw):
    e = Fake(**kw)
    e.locks = rows
    return e


rows = R.collect_bridge(with_locks([lockrow("a", "HELD", "OPERATIONS", "a proof"), lockrow("b", "FREE")]))
check("a held game names who and why", rows[0] == {"game": "ArchBig", "state": "HELD", "who": "OPERATIONS", "for": "a proof",
                                                   "line": "ArchBig: HELD by OPERATIONS"})
check("every game of the machine has its row, by name", [r["game"] for r in rows] == ["ArchBig", "ArchSmall"] and rows[1]["who"] == "")

# 8. idle under a brake is the first, red thing on the page
files = {STEWARD: {"state": "BRAKED", "fault": True, "reason": "two filler jobs failed", "epoch": NOW - 30}}
dirs = {R.TESTQ + "/running": [], R.TESTQ + "/pending": []}
page = page_of(Fake(files=files, dirs=dirs))
head = before_svg(page)
check("braked and idle reads as trouble in the strip", "SteveDesktop lane BRAKED + IDLE" in head)
check("trouble comes first in the strip", "bridge" in head and head.index("SteveDesktop lane BRAKED") < head.index("bridge"))
check("the Steve panel says it in words", "BRAKED AND IDLE" in page)
check("an unreadable Steve job count is not 'idle'", not R.steve_headline({"state": "BRAKED", "running": None})[1])
check("a working Steve under no brake is not idle", not R.steve_headline({"state": "OK", "running": 0})[1])

# 8b. a job result that cannot be read leaves the counts unknown, not short
day = "J" + R.time.strftime("%Y%m%d", R.time.gmtime(NOW))
jfiles = dict(files, **{R.TESTQ + "/done/%sA.json" % day: {"result": {"outcome": "DONE", "finished": "2026-11-03T20:00:00Z"}}})
jdirs = dict(dirs, **{R.TESTQ + "/done": [day + "A.json", day + "B.json"]})
sv = R.collect_steve(Fake(files=jfiles, dirs=jdirs), {})
check("one unreadable job result: done/failed are not known", sv["jobs_known"] is False)
page = page_of(Fake(files=jfiles, dirs=jdirs))
check("the plain-text twin says UNMEASURED there too", "done 24 h UNMEASURED, failed 24 h UNMEASURED" in page)
check("the panel says UNMEASURED there and not 0", "UNMEASURED" in page.split('data-reading="DONE 24 H"')[1].split("</g>")[0])

old = "J" + R.time.strftime("%Y%m%d", R.time.gmtime(NOW - 3 * 86400))
late = R.time.strftime("%Y-%m-%dT%H:%M:%SZ", R.time.gmtime(NOW - 100))
sv = R.collect_steve(Fake(files=dict(files, **{R.TESTQ + "/done/%sA.json" % old: {"result": {"outcome": "DONE", "finished": late}}}), dirs=dict(dirs, **{R.TESTQ + "/done": [old + "A.json"]})), {})
check("a job born days ago and finished now counts in the 24 h", sv["jobs_known"] and sv["done"] == 1)

# 8c. a bad reading in the machine cache costs its tile, not the page
env = Fake(files=dict(files, **{R.STEVE_CACHE: {"good": {"gpu": "NVIDIA X, [N/A], [N/A], 11264", "ram": "x y", "up": "n/a"}, "good_t": NOW}}), dirs=dirs)
page = page_of(env)
check("non-numeric GPU, RAM, uptime still draw the panel", "BRAKED AND IDLE" in page and "SteveDesktop panel" not in page)
broken = Fake(files=files, dirs=dirs)
real_svg, R.steve_svg = R.steve_svg, lambda p: 1 / 0
page = page_of(broken)
R.steve_svg = real_svg
check("a panel that cannot draw costs that panel, not the page", "SteveDesktop: UNMEASURED" in page and "SteveDesktop panel" in before_svg(page) and "ARCHMAGI" in page)

def collections_d(**kw):
    return R.collections.defaultdict(list, kw)


# ---- RUNNING_PAGE_FIX_REVIEW_LEFTOVERS: the review's leftovers
SEAT_CG = "0::/user.slice/user-1000.slice/user@1000.service/claude.slice/claude-seats.slice/claude-seat-BENCH-777.scope\n"
HELP_SVC = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/rm-detached-bench-draw-up-1793747127.service\n"
HELP_SCOPE = "0::/user.slice/user-1000.slice/user@1000.service/claude.slice/claude-seats.slice/claude-seat-BENCH-rm-detached-bench-draw-up-1793747127.scope\n"
under_run = ("  100  1  900  1.0 systemd /lib/systemd/systemd --user\n"
             " 6000 100  500  1.0 bash bash -c launch\n"
             " 6001 6000 500 20.0 claude claude -p --model opus --name ROLE\n")
tree = R.build_tree(Fake(cg={6000: WORKER_CG, 6001: SEAT_CG}), R.Table(R.Env().families()), R.parse_ps(under_run))
groups = list(tree["groups"].values())
check("a numbered seat scope under a live role run is that run, not a window", [g["label"] for g in groups if g["family"] != "upkeep" and g["procs"][0]["pid"] >= 6000] == ["role"]
      and not [g for g in groups if g["label"] == "window"])
tree = R.build_tree(Fake(cg={6000: "0::/init.scope\n", 6001: SEAT_CG}), R.Table(R.Env().families()), R.parse_ps(under_run))
check("a numbered seat scope under nothing that owns agents stays a window", len([g for g in tree["groups"].values() if g["label"] == "window"]) == 1)
tree = R.build_tree(Fake(cg={6000: HELP_SVC, 6001: HELP_SCOPE}), R.Table(R.Env().families()), R.parse_ps(under_run))
check("a detached helper's service and its scope are one helper", len([g for g in tree["groups"].values() if g["family"] == "helpers"]) == 1)
tree = R.build_tree(Fake(cg={6000: HELP_SVC, 6001: SEAT_CG}), R.Table(R.Env().families()), R.parse_ps(under_run))
check("a numbered scope under a detached helper is that helper", len([g for g in tree["groups"].values() if g["family"] == "helpers"]) == 1 and not [g for g in tree["groups"].values() if g["label"] == "window"])

iso = lambda t: R.time.strftime("%Y-%m-%dT%H:%M:%SZ", R.time.gmtime(t))  # noqa: E731
done_dir = R.TESTQ + "/done"
OLD_JOB = "J%sT000000Z-aaaaaa.json" % R.time.strftime("%Y%m%d", R.time.gmtime(NOW - 10 * 86400))
job_files = {done_dir + "/" + OLD_JOB: {"job": {"purpose": "guard", "mod": "FlowWorks", "item": "X_ITEM"},
                                        "result": {"outcome": "DONE", "started": iso(NOW - 700), "finished": iso(NOW - 100), "rows": [{"chain": "c", "row": "r", "verdict": "FAIL"}, {"chain": "c", "row": "s", "verdict": "PASS"}], "counts": {"PASS": 1, "FAIL": 1}}},
             done_dir + "/J1.json": {"job": {"purpose": "old"}, "result": {"outcome": "DONE", "started": iso(NOW - 20 * 86400 - 60), "finished": iso(NOW - 20 * 86400), "rows": []}},
             STEWARD: {"state": "RUNNING", "epoch": NOW - 10}}
env = Fake(files=job_files, dirs={done_dir: [OLD_JOB, "J1.json"], R.TESTQ + "/running": [], R.TESTQ + "/pending": []})
state = {}
sv = R.collect_steve(env, state)
check("a job born 10 days ago and finished now counts in the 24 h", sv["jobs_known"] and sv["done"] == 1 and sv["failed"] == 0)
check("Steve's Live Testing reads that job", sv["live"]["rows"] == {"PASS": 1, "FAIL": 1} and sv["live"]["bugs"] == 1)
check("Steve's busy share is its job's minutes over 24 h", abs(sv["live"]["busy"] - 600 / 86400) < 1e-6)
check("a job finished long ago keeps only its finish time", set(state["steve_jobs"]["J1.json"]) == {"v", "f"})
env.files = {STEWARD: job_files[STEWARD]}
sv = R.collect_steve(env, state)
check("a result already read is not read again", sv["jobs_known"] and sv["done"] == 1)
state["steve_jobs"].pop(OLD_JOB)
state["steve_jobs"]["J1.json"] = {"f": 5}     # the shape before this change: read again, not trusted
sv = R.collect_steve(env, state)
check("an unreadable result leaves the day's counts unknown, not short", sv["jobs_known"] is False)
check("an unreadable result leaves Live Testing UNMEASURED, not short", sv["live"] is None)
env_ns = Fake(dirs={done_dir: [], R.TESTQ + "/running": [], R.TESTQ + "/pending": []})
sv = R.collect_steve(env_ns, {})
check("a dead steward keeps the queue readings and says why", sv["state"] is None and sv["running"] == 0 and "steward UNMEASURED" in sv["reason"] and sv["age"] is None)
check("an unread history is UNMEASURED, a missing one is merely new", "UNMEASURED" in R.window_stats(R.read_history(Fake(fail=())) , NOW, 86400, "24 h")[0])

check("verdict: above the usual with high being bad warns", R.versus(9, (1, 5)) == ("high, usual 1-5", R.WARN))
check("verdict: below the usual with low being bad warns", R.versus(0, (1, 5), False) == ("low, usual 1-5", R.WARN))
check("verdict: inside the usual", R.versus(3, (1, 5))[0] == "normal, usual 1-5")
check("verdict: no history says so, it never guesses", R.versus(3, None)[0] == "no baseline yet")
check("verdict: a reading over its fixed top is called high", R.against(90, 85, "under 85%") == ("high, normal under 85%", R.WARN))

spans = R.bridge_intervals([(1000, "taken"), (1100, "released"), (2000, "taken")], 2000 + 5 * R.HOLD_CAP)
check("a bridge hold ends at its release", spans[0] == (1000, 1100))
check("a hold never released stops counting at the stale limit", spans[1] == (2000, 2000 + R.HOLD_CAP))
check("a share is clipped to its window", R.share_of([(0, 100)], 50, 150) == 0.5)
check("overlapping spans are one span", R.merged([(5, 8), (0, 6), (20, 21)]) == [(0, 8), (20, 21)])

ROWS = "\n".join(json.dumps(r) for r in [{"at": iso(NOW - 50), "item": "A", "criterion": "A1", "outcome": "PASS"}, {"at": iso(NOW - 60), "item": "B", "criterion": "A1", "outcome": "FAIL"},
                                         {"at": iso(NOW - 70), "item": "B", "criterion": "A1", "outcome": "FAIL"}, {"at": iso(NOW - 80), "item": "C", "criterion": "A2", "outcome": "UNMEASURED"},
                                         {"at": iso(NOW - 2 * 86400), "item": "D", "criterion": "A1", "outcome": "REFUSED"}]) + "\n"
env = Fake(files={R.LIVE_RUNS: ROWS})
env.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
hist = [{"t": NOW - 60, "n": 1, "f": {"game": 1}}, {"t": NOW - 120, "n": 1, "f": {"game": 0}}]
lv = R.collect_archmagi_live(env, NOW, hist)
check("proof rows by result count the 24 h only", lv["rows"] == {"PASS": 1, "FAIL": 2, "UNMEASURED": 1})
check("a clause failing twice is one bug", lv["bugs"] == 1)
check("Archmagi's busy share is bridge time over 24 h", abs(lv["busy"] - 1800 / 86400) < 1e-6)
check("game up share comes from the page's own samples", lv["game_up"] == 0.5)
broken = Fake(files={R.LIVE_RUNS: "{bad\n" + ROWS})
check("a broken runs.jsonl line is UNMEASURED, never a short count", R.guarded(R.collect_archmagi_live, broken, NOW, [])[1] is not None)
stale = Fake(files={R.LIVE_RUNS: json.dumps({"at": iso(NOW - 13 * 86400), "item": "A", "criterion": "A1", "outcome": "PASS"}) + "\n"})
lvs = R.collect_archmagi_live(stale, NOW, hist)
check("a run log with no row in 13 days blinds rows and bugs with its cause, never 0 rows", lvs["rows"] is None and lvs["bugs"] is None and "no writer" in lvs["rows_why"])
stale.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
lvs = R.collect_archmagi_live(stale, NOW, hist)
check("a dead run log leaves busy and game up measured", abs(lvs["busy"] - 1800 / 86400) < 1e-6 and lvs["game_up"] == 0.5)
check("the live text names the blind rows, not a 0", "proof rows UNMEASURED; bugs found UNMEASURED" in R.live_text("x", lvs))
env.bridge = None
lv2 = R.collect_archmagi_live(env, NOW, hist)
check("no ledger: busy is UNMEASURED, not 0", lv2["busy"] is None)

check("mods accepted reads the state after the name", R.mods_status_counts("Abyss   STALE   x\nB   RED (last)  y\nC  GREEN  z\nnoise\n") == {"STALE": 1, "RED": 1, "GREEN": 1})
check("mods accepted with no line is UNMEASURED", R.guarded(R.mods_status_counts, "nothing\n")[1] is not None)

# the whole page, every section, on a full fixture
FLEET = {"needs": {"count": 2, "lines": [{"item": "DRAW_A", "q": "Look at the bridge <Other> line"}, {"item": "K_X", "q": "Keep it?"}],
                   "topics": [{"topic": "DRAW", "items": ["DRAW_A"], "q": "Look at the bridge", "others": []}, {"topic": "K", "items": ["K_X"], "q": "Keep it?", "others": []}],
                   "answered": [{"item": "ANS_ITEM", "q": "old"}]},
         "receipts": [{"item": "R1", "glyph": "✓", "title": "t", "where": "FlowWorks", "receipt": {"check": "PASS", "outcome": "Did the thing.", "commits": 2, "tokens": 5000}}],
         "mods": [{"name": "FlowWorks", "meta": "1 done", "backlog": "Backlog: 1 open", "proof": "Blind check PASS", "next": "Next thing", "waits": ["waits on you: x"],
                   "tasks": [{"mark": "✓", "kind": "pass", "title": "A task <b>", "date": "1 Nov"}], "more": 3}],
         "total_mods": 10, "t": NOW, "good_t": NOW,
         "accepted": {"green": 1, "stale": 2, "red": 3, "draft": 1, "never": 3, "total": 10}}
full = Fake(ps=PS, cg=WORKER, files={R.FLEET_CACHE: FLEET, STEWARD: {"state": "RUNNING", "epoch": NOW}, R.LIVE_RUNS: ROWS})
full.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
page, sample, phone = R.build(full, {}, [])
for word in ("How to read", "NEEDS YOU, 2", "RECENT EVENTS", "FINISHED TODAY, 1", "PROGRESS BY MOD, 1 MODS", "ARCHMAGI", "STEVEDESKTOP", "LIVE TESTING, LAST 24 H",
             "MODS ACCEPTED", "1 of 10", "normal", "FALSIFIED EXPECTATIONS", "<title>"):
    check("the page shows: " + word, word in page)
check("the page has a how-to-read line for each of its panels", page.count("How to read:") == 6)
check("the old names are gone", "blind checker" not in page.lower() and "checkers" not in page and "workers " not in page.split("<details>")[0].replace("workers can", ""))
check("Needs you is the one view: a row per item, escaped, and the count not filed anywhere", page.count("Look at the bridge") == 1 and "DRAW_A" in page and "&lt;Other&gt; line" in page and "<Other>" not in page and "not filed anywhere: UNMEASURED" in page)
check("an answered item leaves the list and says so", "1 you answered; the next move is ours" in page and "ANS_ITEM" in page)
import owner_queue as OQ  # noqa: E402
import no_home as NH  # noqa: E402
VIEW = {"at": NOW - 60, "his": [{"item": "SHARED_ONE", "q": "Shared question"}], "ours": [], "home": {"no_home": 4, "by_source": {"typed words": 4}, "unmeasured": []}}
shared = R.build(Fake(ps=PS, cg=WORKER, files={R.FLEET_CACHE: FLEET, OQ.view_path(create=False): VIEW}), {}, [])[0]
check("a fresh shared view is shown in place of the fleet rows", "Shared question" in shared and "NEEDS YOU, 1" in shared and "not filed anywhere: 4" in shared and "Look at the bridge" not in shared)
stale_v = R.build(Fake(ps=PS, cg=WORKER, files={R.FLEET_CACHE: FLEET, OQ.view_path(create=False): dict(VIEW, at=NOW - OQ.VIEW_FRESH_S - 1),
                                                   NH.state_path(create=False): {"at": NOW - 60, "no_home": 7, "by_source": {"typed words": 7}, "unmeasured": []}}), {}, [])[0]
check("a stale shared view is not shown; the fleet rows carry the fresh shared count", "Shared question" not in stale_v and "Look at the bridge" in stale_v and "not filed anywhere: 7" in stale_v)
check("a task title is escaped and sits on one line", "A task &lt;b&gt;" in page)
sections = re.findall(r"^<div style=.*$", page, re.M)
check("each html section is one block, one line", len(sections) >= 8 and all(x.rstrip().endswith("</div>") for x in sections))
check("every svg stays one block", all("\n" not in x for x in re.findall(r"<svg.*?</svg>", page, re.S)))
check("the phone copy is short and plain", len(phone) < 2500 and "<" not in phone and "NEEDS YOU 2" in phone and "Archmagi: busy" in phone and "SteveDesktop" in phone)
frozen = dict(FLEET, t=NOW - R.FLEET_STALE - 1)
frozen_page = R.build(Fake(ps=PS, files={R.FLEET_CACHE: frozen}), {}, [])[0]
check("a mods count from a refresh long past reads UNMEASURED", "mods accepted (" in frozen_page.split("<div><svg")[0] and "1 of 10" not in frozen_page)
old_f = Fake(ps=PS, files={R.FLEET_CACHE: dict(FLEET, good_t=NOW - R.FLEET_STALE - 1, why="ledger broke")})
check("a fleet reading past its limit reads UNMEASURED, it never passes as today's", "FINISHED TODAY, 1" not in R.build(old_f, {}, [])[0])
young = dict(FLEET, good_t=NOW - 400, why="ledger broke")
check("a young fleet reading stays, with its age and reason", "ledger broke" in R.build(Fake(ps=PS, files={R.FLEET_CACHE: young}), {}, [])[0] and "FINISHED TODAY, 1" in R.build(Fake(ps=PS, files={R.FLEET_CACHE: young}), {}, [])[0])
bare = Fake(ps=PS)
page = R.build(bare, {}, [])[0]
check("no fleet cache: those sections read UNMEASURED", "mods, receipts and Needs you" in page.split("<div><svg")[0] and "NEEDS YOU" in page)
check("no modcheck: mods accepted reads UNMEASURED, never 0", "mods accepted (" in page.split("<div><svg")[0])

# 8d2. a process table that cannot be attributed is UNMEASURED, not a believable zero
class NoCgroup(Fake):
    def cgroup(self, pid):
        raise PermissionError("cgroup unreadable")


page = page_of(NoCgroup(ps=PS))
check("an unreadable cgroup makes the tree UNMEASURED", "PROCESS TREE: UNMEASURED" in page)

# 8e. the Steve script omits the game when tasklist fails rather than reporting 0
check("Steve's game reading is conditional on tasklist's exit", 'if t=$(timeout 5' in R.STEVE_SCRIPT and "</dev/null" in R.STEVE_SCRIPT)

check("a history line that is not a record does not stop the page", R.read_history(Fake(files={R.HIST: 'null\n[1]\n5\n'})) == [])

# 10. history honesty
hist = [{"t": NOW - 600, "n": 5}, {"t": NOW - 300, "n": 7}, {"t": NOW - 60, "n": 9}]
line, rows = R.window_stats(hist, NOW, 86400, "24 h")
check("short history says it does not yet cover 24 h", "not yet a full 24 h" in line and "min 5 / median 7 / max 9" in line)
check("empty history says no history yet", "no history yet" in R.window_stats([], NOW, 86400, "24 h")[0])

# 11. writes, in a private directory
with tempfile.TemporaryDirectory() as d:
    R.OUT_DIR, R.OUT, R.HIST, R.STATE, R.STEVE_CACHE = d, d + "/RELENTLESS_NOW.md", d + "/h.jsonl", d + "/s.json", d + "/steve.json"
    R.PHONE_OUT, R.FLEET_CACHE = d + "/RELENTLESS_NOW_PHONE.md", d + "/fleet.json"
    env = Fake(ps=PS)
    rc, _ = R.run(env)
    first = open(R.OUT).read()
    check("good run writes the page and no temp file is left", rc == 0 and "updated_epoch=" in first and not [f for f in os.listdir(d) if ".tmp." in f])
    seen, real_replace = [], os.replace

    def spy(src, dst):
        if dst == R.OUT:
            with open(src) as f:
                seen.append((f.read(), open(dst).read()))
        real_replace(src, dst)

    R.os.replace = spy
    try:
        env_a = Fake(ps=PS)
        env_a.clock = NOW + 1
        R.run(env_a)
    finally:
        R.os.replace = real_replace
    check("the page goes in whole by rename: the old page stands until the new one is complete",
          len(seen) == 1 and seen[0][1] == first and "updated_epoch=%d" % int(NOW + 1) in seen[0][0] and seen[0][0].rstrip().endswith("-->"))
    check("each good run appended one history sample", len(open(R.HIST).read().splitlines()) == 2)
    check("the page was on disk before ssh was tried", env.calls == [("ssh", True)])
    check("a good ssh reading lands in the cache", json.load(open(R.STEVE_CACHE))["good"]["load"] == "0.5")

    block = first.split("<details>")[1].split("</details>")[0]
    check("no blank line inside the details block", not re.search(r"\n\s*\n", block))
    check("the details block is the last thing before the marker", first.index("</details>") > first.rindex("<div><svg"))
    check("the tree fence comes before the details", first.index("```") < first.index("<details>"))

    again = Fake(ps=PS)
    again.clock = NOW + 30
    R.run(again)
    check("ssh is not repeated inside the probe interval", again.calls == [])

    dead = Fake(ps=PS, fail=("ssh",))
    dead.clock = NOW + R.PROBE_EVERY + 10
    rc, _ = R.run(dead)
    cache = json.load(open(R.STEVE_CACHE))
    check("a dead ssh still writes the page", rc == 0 and dead.calls == [("ssh", True)])
    check("a dead ssh turns the route off and keeps the last good numbers", cache["routes"]["wsl"] is False and cache["good"]["load"] == "0.5" and "no route" in cache["why"])

    second = Fake(ps=PS)
    second.clock = NOW + 2 * R.PROBE_EVERY + 20
    R.run(second)
    cache = json.load(open(R.STEVE_CACHE))
    check("a returning ssh clears the failure", cache["routes"]["wsl"] is True and "why" not in cache)

    check("the phone copy is written beside the page", os.path.exists(R.PHONE_OUT))
    seen_page = []
    order = Fake(ps=PS)
    order.clock = NOW + 3600
    order.fleet_gather = lambda now: seen_page.append("updated_epoch=%d" % int(order.clock) in open(R.OUT).read()) or None
    R.run(order)
    check("the page is on disk before the slow half is refreshed", seen_page == [True])
    # STATUS_PAGES_BUILD_REPLACE_RIMPULSE: the owner's board is rebuilt after each fleet refresh, and only then
    for label, age, want in (("stale", R.FLEET_EVERY + 1, ["refresh", "board"]), ("fresh", 10, [])):
        steps = []
        bd = Fake(ps=PS, files={R.FLEET_CACHE: {"t": NOW + 5000 - age}})
        bd.clock = NOW + 5000
        bd.fleet_gather = lambda now, s=steps: s.append("refresh") or None
        bd.status_board = lambda s=steps: s.append("board")
        R.run(bd)
        check("a %s fleet cache: run(write=True) %s" % (label, "refreshes the fleet, then rebuilds the status board" if want else "leaves the status board alone"), steps == want)
    real_bd = Fake(ps=PS)
    real_bd.fleet, real_bd.mods = {"mods": [], "receipts": [], "needs": {"count": 0, "topics": []}, "total_mods": 5}, "A  GREEN x\n"
    real_bd.clock = NOW + 6000
    R.run(real_bd)
    check("a stale fleet cache: the real Env.status_board writes STATUS_BOARD.html beside the page",
          os.path.exists(d + "/STATUS_BOARD.html") and "<html" in open(d + "/STATUS_BOARD.html").read().lower())
    good_f = Fake(ps=PS)
    good_f.fleet, good_f.mods = {"mods": [], "receipts": [], "needs": {"count": 0, "topics": []}, "total_mods": 5}, "A  GREEN x\nB RED y\n"
    good_f.clock = NOW + 2 * R.PROBE_EVERY + 300
    R.refresh_fleet(good_f)
    saved = json.load(open(R.FLEET_CACHE))
    check("a fleet refresh caches the sections and the mods accepted", saved["accepted"] == {"green": 1, "stale": 0, "red": 1, "draft": 0, "unmeasured": 0, "never": 3, "total": 5} and saved["why"] is None)
    down = Fake(ps=PS)
    down.clock = good_f.clock + 400
    R.refresh_fleet(down)
    saved = json.load(open(R.FLEET_CACHE))
    check("a failed modcheck read clears the old count", "accepted" not in saved and saved["accepted_why"])
    check("a failed refresh keeps the last good reading and says why", saved["mods"] == [] and saved["why"] and saved["good_t"] == good_f.clock)
    before = open(R.OUT).read()
    bad = Fake(ps=PS)
    bad.families = lambda: (_ for _ in ()).throw(ValueError("table broke"))
    bad.clock = NOW + 2 * R.PROBE_EVERY + 400
    rc, _ = R.run(bad)
    check("failed run returns 1 and keeps the old page byte for byte", rc == 1 and open(R.OUT).read() == before)
    check("failed run records why", "table broke" in json.load(open(R.STATE)).get("last_error", ""))
    good = Fake(ps=PS)
    good.clock = NOW + 2 * R.PROBE_EVERY + 800
    rc, _ = R.run(good)
    check("next good page carries the STALE since banner", "STALE since" in open(R.OUT).read())
    check("the page records its own update epoch for --check", "updated_epoch=%d" % int(good.clock) in open(R.OUT).read())

# ---- every number on every instrument panel, read panel by panel and tile by tile, never as words anywhere on the page.
# The text twin, the how-to-read prose and another machine's panel cannot satisfy these. A list row (a process, an item line,
# a receipt) is a list; the numbers judged here are the instruments: the owner's "every number gets a verdict and rough normal range".
VERDICT = re.compile(r"(^|[;:] )(ok|normal|high|low|bad)\b")
RANGE = re.compile(r"\b(normal|usual|rough) \S")
LIVE_TILES = {"BUSY / IDLE", "PROOF ROWS BY RESULT", "BUGS FOUND", "FALSIFIED EXPECTATIONS"}
EXPECTED = {
    "Archmagi": {"UPTIME", "LOAD", "WSL RAM USED", "EXT4 FREE", "D: FREE", "GAME THIS 24 H"} | LIVE_TILES,
    "SteveDesktop": {"STATE", "ROUTES", "UPTIME", "LOAD", "WSL RAM USED", "CPU", "DISK FREE", "GPU", "GAME", "RUNNING", "QUEUED", "DONE 24 H", "FAILED 24 H", "LAST JOB", "ROWS/HOUR 24 H",
                     "STEWARD WROTE", "MACHINE READING", "MACHINE SOURCE", "STEVE1", "STEVE2", "RUNNING JOBS", "QUEUED JOBS", "SERVICES", "LANE SOURCE"} | LIVE_TILES,
}
NOT_A_NUMBER = {"FALSIFIED EXPECTATIONS"}      # nothing records it: nothing to judge
# a digit outside any reading is a naked number, unless it only names a window or a stage of the axis
FRAME = re.compile(r"^(48 h ago|LIVE TESTING, LAST 24 H|LAST 24 H, EVENTS \(SEVERAL PER ITEM\)|TRENDS, 48 H, TWO-HOUR POINTS)$")
SVGNS = "{http://www.w3.org/2000/svg}"


def panels_of(page):
    """-> {first word of aria-label: svg element}; a panel that is not well-formed raises."""
    out = {}
    for raw in re.findall(r"<svg.*?</svg>", page, re.S):
        root = R_ET.fromstring(raw)
        out[root.get("aria-label").split(":")[0].split(" ")[0]] = root
    return out


def g_of(rs, label):
    return rs[label][0]


def texts_with(rs, label):
    """A reading's texts as (size, words, element), so a caller can set apart the ones inside an item row."""
    return [(t.get("font-size"), "".join(t.itertext()), t) for t in rs[label][0].iter(SVGNS + "text")]


def readings_of(root):
    """-> {label: (element, [(size, text), ...])}; a repeated label keeps every copy apart by a trailing #."""
    out = {}
    for g in root.iter(SVGNS + "g"):
        name = g.get("data-reading")
        if name:
            name = re.sub(r"^(LOAD/).*", "LOAD", name)
            name = re.sub(r"^LAST JOB.*", "LAST JOB", name)
            name = re.sub(r"^GPU.*", "GPU", name)
            while name in out:
                name += "#"
            out[name] = (g, [(t.get("font-size"), "".join(t.itertext())) for t in g.iter(SVGNS + "text")])
    return out


def judged(note):
    return bool(VERDICT.search(note) and RANGE.search(note))


def panel_problems(page, cards_have_oldest=True):
    """Every way the instrument panels can lose a verdict, a range, a tile or a trend line, as a list of plain sentences."""
    bad = []
    pans = panels_of(page)
    for name, want in EXPECTED.items():
        root = pans.get(name)
        if root is None:
            bad.append("%s: no panel" % name)
            continue
        rs = readings_of(root)
        for label in sorted(want - set(rs)):
            bad.append("%s: no reading %s" % (name, label))
        for label in sorted(set(rs) - want):
            bad.append("%s: a reading nobody pinned: %s" % (name, label))
        inside = {id(t) for g, _ in rs.values() for t in g.iter(SVGNS + "text")}
        for t in root.iter(SVGNS + "text"):
            words = "".join(t.itertext())
            if id(t) not in inside and re.search(r"\d", words) and not FRAME.match(words):
                bad.append("%s: naked number: %s" % (name, words))
        for label, (_, texts) in rs.items():
            rowt = {id(t) for r in g_of(rs, label).iter(SVGNS + "g") if r.get("data-item") for t in r.iter(SVGNS + "text")}
            texts = [(size, w) for size, w, t in texts_with(rs, label) if id(t) not in rowt]   # an item row is a name, not a note
            notes = [w for size, w in texts if (size == "9" or label == "STATE") and not w.startswith("top ")]
            for w in notes:
                if label not in NOT_A_NUMBER and not judged(w):
                    bad.append("%s %s: note with no verdict or range: %s" % (name, label, w))
                if "…" in w:
                    bad.append("%s %s: note clipped: %s" % (name, label, w))
            value = [w for size, w in texts if w not in notes and re.search(r"\d", w)]
            if value and label not in NOT_A_NUMBER and not notes:
                bad.append("%s %s: a number with no note: %s" % (name, label, value))
            if any(w == "UNMEASURED" for _, w in texts):
                bad.append("%s %s: UNMEASURED on the full fixture" % (name, label))
    # a how-to-read line right under each panel
    for name, words in (("Archmagi", "Busy means"), ("SteveDesktop", "Busy means"), ("Chain", "Follow an arrow")):
        hit = re.search(r'aria-label="%s[^\n]*</svg></div>\n(?:\n*)<div[^\n]*How to read:</b>([^\n]*)' % name, page)
        if not hit or words not in hit.group(1):
            bad.append("%s: no how-to-read under it saying %s" % (name, words))
    return bad


def fixture_env(extreme=False):
    """Everything readable; `extreme` puts every reading out of its normal, the long way, so a note that does not fit gets clipped and shows."""
    day = lambda k: R.time.strftime("%Y%m%d", R.time.gmtime(NOW - k * 86400))  # noqa: E731
    per = 3 if extreme else 1
    rows = [{"at": iso(NOW - 50 - i), "item": "A", "criterion": "A%d" % i, "outcome": "FAIL" if extreme else "PASS"} for i in range(3)]
    rows += [{"at": iso(NOW - 80 - i), "item": "C", "criterion": "U%d" % i, "outcome": "UNMEASURED"} for i in range(40 if extreme else 1)]
    done_dir = R.TESTQ + "/done"
    job = "J%sT000000Z-aaaaaa.json" % day(10)
    files = {R.FLEET_CACHE: FLEET, STEWARD: {"state": "BRAKED" if extreme else "RUNNING", "epoch": NOW - (900 if extreme else 10), "reason": "x", "since": iso(NOW - 9000)},
             R.LIVE_RUNS: "\n".join(json.dumps(r) for r in rows) + "\n",
             done_dir + "/" + job: {"job": {"purpose": "guard", "mod": "FlowWorks", "item": "A"},
                                    "result": {"outcome": "DONE", "started": iso(NOW - 7700), "finished": iso(NOW - (7100 if extreme else 100)), "rows": [{"chain": "c", "row": "r", "verdict": "PASS"}, {"chain": "c", "row": "s", "verdict": "PASS"}], "counts": {"PASS": 2}}},
             R.STEVE_CACHE: {"t": NOW - 30, "good_t": NOW - (1700 if extreme else 30), "routes": {"tailscale": True, "lan": not extreme, "wsl": True},
                             "good": {"up": "100" if extreme else "20000", "load": "99.9" if extreme else "0.5", "cores": "18", "ram": "63000 64000" if extreme else "1000 64000", "disk": "50 1000" if extreme else "900 1000",
                                      "gpu": "NVIDIA GeForce RTX 2080 Ti, %s, 4400, 11264" % ("99" if extreme else "27"), "game": "0" if extreme else "1", "cpu_pct": 99 if extreme else 3}}}
    pending = ["p%d.json" % i for i in range(25 if extreme else 1)]
    files[R.STEVE_CACHE]["good"].update({
        "locks_json": json.dumps({"out": json.dumps({"games": [lockrow("a", "HELD", "RUNNER", "testq J-run0.a1"), lockrow("b", "FREE")]})}),
        "status_json": json.dumps({"out": "Steve1 running pid 29576 port 5174\nSteve2 stopped port 5175\n"}),
        "services_json": json.dumps({"out": "testq-J-run0_a1.service loaded active running lane\ndbus.service loaded active running dbus\nlist-item-FlowWorks.service loaded active running item\n"})})
    for folder, names in (("running", ["r%d.json" % i for i in range(per)]), ("pending", pending)):
        for i, name in enumerate(names):
            lane_job = {"id": "J-%s%d" % ("run" if folder == "running" else "wait", i), "mod": "FlowWorks", "purpose": "guard", "selector": {"chains": ["water", "power"]}, "submitted": iso(NOW - 120)}
            files[R.TESTQ + "/" + folder + "/" + name] = {"job": lane_job, "sent": iso(NOW - 60), "attempt": lane_job["id"] + ".a1", "host": "stevedesktop.b" if i else "stevedesktop"} if folder == "running" else lane_job

    class Full(Fake):
        def local_stats(self):
            return {"up": 100.0 if extreme else 90000.0, "load": 99.9 if extreme else 7.0, "cores": 14, "ram": (34000, 35000) if extreme else (8000, 35000), "disk": 50 if extreme else 500, "disk_d": 50 if extreme else 1700}


    env = Full(ps=PS, cg=WORKER, files=files, dirs={done_dir: [job], R.TESTQ + "/running": ["r%d.json" % i for i in range(per)], R.TESTQ + "/pending": pending})
    env.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
    env.locks = FREE2
    return env, [{"t": NOW - 60, "n": 1, "f": {"game": 0 if extreme else 1}}, {"t": NOW - 120, "n": 1, "f": {"game": 1 if not extreme else 0}}]


def page_problems():
    bad = []
    for extreme in (False, True):
        env, hist = fixture_env(extreme)
        bad += ["%s: %s" % ("extreme" if extreme else "normal", x) for x in panel_problems(R.build(env, {}, hist)[0])]
    return bad


found = page_problems()
for x in found:
    print("  " + x)
check("every instrument on all three panels carries a verdict and a rough normal, tile by tile, in normal and out-of-range states", not found)
env, hist = fixture_env()
pans = panels_of(R.build(env, {}, hist)[0])
for machine in ("Archmagi", "SteveDesktop"):
    rs = readings_of(pans[machine])
    check("%s's own panel has its Live Testing tiles and its own busy figure" % machine, LIVE_TILES <= set(rs) and "UNMEASURED" not in " ".join(w for _, w in rs["BUSY / IDLE"][1]))
check("hover text sits on the tile it explains", readings_of(pans["Archmagi"])["BUGS FOUND"][0].find(SVGNS + "title") is not None)
midnight = time.mktime(time.localtime(NOW)[:3] + (0, 0, 0, 0, 0, -1))
late = Fake(ps=PS, files={R.FLEET_CACHE: dict(FLEET, t=midnight - 60, good_t=midnight - 60)})
late.clock = midnight + 60
check("receipts from before midnight are not FINISHED TODAY", "FINISHED TODAY, 1" not in R.build(late, {}, [])[0])

class CpuProbe(Fake):
    stats = ["cpu 100 0 0 0 0 0 0 0 0 0", "cpu 110 0 0 0 90 0 0 0 10 0"]

    def steve_probe(self):
        return "up=1\nstat=%s\n" % self.stats.pop(0)


with tempfile.TemporaryDirectory() as d:
    real_cache, R.STEVE_CACHE = R.STEVE_CACHE, d + "/s.json"
    cpu_env = CpuProbe()
    R.probe_steve(cpu_env)
    cpu_env.clock += R.PROBE_EVERY + 1
    R.probe_steve(cpu_env)
    with open(R.STEVE_CACHE) as f:
        got = json.load(f)["good"]["cpu_pct"]
    R.STEVE_CACHE = real_cache
check("Steve's CPU counts neither I/O wait as busy nor guest time twice", got == 10)

hold = [lockrow("a", "HELD", "OPERATIONS", "a proof"), lockrow("b", "HELD", "BENCH", "a visit")]
pg = page_of(with_locks(hold))
check("each game's hold reads plainly, on the strip and the panel", "ArchBig bridge HELD by OPERATIONS" in before_svg(pg)
      and "ArchSmall bridge HELD by BENCH" in before_svg(pg) and "ArchBig held by OPERATIONS; ArchSmall held by BENCH" in pg.split("</svg>")[0])
pg = page_of(with_locks([lockrow("a", "UNKNOWN"), lockrow("b", "HIS_HOLD")]))
check("a lock that could not be looked at is UNMEASURED by its cause, never FREE", "ArchBig bridge UNMEASURED" in before_svg(pg)
      and "ArchBig's driver lock (ArchBig: COULD NOT LOOK" in before_svg(pg) and "ArchBig bridge FREE" not in pg)
check("his hold on a game reads as his hold", "ArchSmall bridge HIS HOLD" in before_svg(pg) and "ArchSmall his hold" in pg.split("</svg>")[0])

check("a timer with no next run does not claim to be running", "no next run" in R.timers_rows([{"unit": "rm-x.timer", "last": 0, "next": 0}], [], NOW)[0] and "running now" not in R.timers_rows([{"unit": "rm-x.timer"}], [], NOW)[0])
with tempfile.TemporaryDirectory() as d:
    real_events, R.LEDGER_EVENTS = R.LEDGER_EVENTS, d
    with open(d + "/A.jsonl", "w") as f:
        for state, tsn in (("released", 5), ("taken", 6)):
            f.write(json.dumps({"event": "bridge", "ts": iso(NOW), "tsn": tsn, "state": state}) + "\n")
    tied = R.Env().bridge_events()
    R.LEDGER_EVENTS = real_events
check("a release and a take in one second keep their order", [s for _, s in tied] == ["released", "taken"])

LONG = "RUNNING_PAGE_BUILD_NAMES_ON_THE_BELT_AND_THEN_SOME"      # longer than any real name (44 measured 2026-11-03)
check("wrap_name keeps every character and every line fits, on names, titles and a run wider than the line",
      all("".join(R.wrap_name(t, w, h)).replace(" ", "") == t.replace(" ", "") and all(len(x) <= w for x in R.wrap_name(t, w, h)) and all(len(x) <= w - h for x in R.wrap_name(t, w, h)[1:])
          for t in (LONG, "A", "A_", "_A_", "NO_UNDERSCORES" * 9, "x" * 90, "a title, in plain words / with-a-dash and more words than one line holds"[:70], "OPS_RED_OVERDUE_CHASE_AEUZ")
          for w, h in ((21, 2), (51, 2), (84, 6), (5, 2))))
check("wrap_name breaks after an underscore when one fits", R.wrap_name("RUNNING_PAGE_BUILD_NAMES_ON_THE_BELT", 21, 2) == ["RUNNING_PAGE_BUILD_", "NAMES_ON_THE_BELT"])
# ---- the sections' own rows, not only their headings: a receipt, the feed's three kinds, the live proofs line, today's bugs
def content_env():
    env, hist = fixture_env()
    env.files[R.LEDGER_EVENTS + "/OWNER.jsonl"] = json.dumps({"event": "note", "ts": iso(NOW - 300), "id": "X_ITEM", "text": "a word from him"}) + "\n"
    env.read_tail = lambda path, n: (env.read_text(path), False)
    # one FAIL today and one two days back: BUGS FOUND counts the last 24 h only
    env.files[R.LIVE_RUNS] += "".join(json.dumps(r) + "\n" for r in ({"at": iso(NOW - 40), "item": "B", "criterion": "B1", "outcome": "FAIL"},
                                                                     {"at": iso(NOW - 2 * 86400 - 100), "item": "OLD", "criterion": "O1", "outcome": "FAIL"}))
    return env, hist


def content_problems():
    bad = []
    env, hist = content_env()
    page = R.build(env, {}, hist)[0]
    lines = page.splitlines()
    fin = next((x for x in lines if "FINISHED TODAY, 1 ITEMS" in x), "")
    if "✓ Did the thing." not in fin or "check PASS" not in fin:
        bad.append("FINISHED TODAY does not show its receipt row")
    ev = next((x for x in lines if "RECENT EVENTS" in x), "")
    for row in ("<b>Steve job done</b> FlowWorks guard</div>", "<b>your note</b> X_ITEM: a word from him</div>"):
        if row not in ev:
            bad.append("RECENT EVENTS lacks the row %s" % row)
    live = R.collect_archmagi_live(env, NOW, hist)
    if live["bugs"] != 1:
        bad.append("BUGS FOUND counts %s, not the one FAIL of the last 24 h" % live["bugs"])
    acc = next((x for x in lines if "MODS ACCEPTED, GOAL IS ALL:" in x), "")
    if "1 of 10" not in acc or not judged(re.sub(r"<[^>]+>", " ", acc.split("1 of 10", 1)[-1]).strip()):
        bad.append("the mods panel does not say MODS ACCEPTED with a verdict and a range")
    try:
        if "1" not in [w for _, w in readings_of(panels_of(page)["Archmagi"])["BUGS FOUND"][1]]:
            bad.append("the Archmagi BUGS FOUND tile does not read 1")
    except (KeyError, AttributeError, IndexError, ValueError) as e:
        bad.append("a trend or tile could not be read: %r" % e)
    return bad


found = content_problems()
for x in found:
    print("  " + x)
check("receipt row, feed rows of every kind, mods accepted and today's bugs are on the page", not found)

# ---- and the test above bites: each mutant of running_now.py is a way this page has lost a verdict, a tile or a line
SRC = open(R.__file__).read()
QUIET = "(lambda *a, **k: None)("
MUTANTS = [
    ("Steve loses its Live Testing row", 'live_row(s, 248, sv.get("live"),', QUIET + 's, 248, sv.get("live"),'),
    ("Archmagi loses its Live Testing row", "live_row(s, 130, live,", QUIET + "s, 130, live,"),
    ("a tile never draws its note", "s.text(x + 8, y + 53, clip(note, int((w - 12) / 4.7)), 9, note_colour)", "pass"),
    ("Archmagi LOAD has no verdict", '*against(d["load"], d["cores"] * 1.5, "0-%d" % (d["cores"] * 1.5)), "Processes', 'None, DIM, "Processes'),
    ("Archmagi WSL RAM has no verdict", 'TEXT, frac, *against(frac * 100, 85, "under 85%"))\n        tile(s, 428', "TEXT, frac)\n        tile(s, 428"),
    ("Steve WSL RAM has no verdict", 'TEXT, frac, *against(frac * 100, 85, "under 85%"))\n    else:', "TEXT, frac)\n    else:"),
    ("Steve UPTIME has no verdict", "*(uptime_note(upv) if upv is not None else (None, DIM))", "None, DIM"),
    ("Archmagi UPTIME has no verdict", '*uptime_note(d["up"])', "None, DIM"),
    ("mods accepted has no range", '"%s, normal over half; GREEN', '"%s; GREEN'),
    ("the proof rows tile has no verdict", '"%s, %d of %d measured%s; normal over 30%%" % ("low" if low else "ok", measured, total,', '"%s %d of %d measured%s" % ("", measured, total,'),
    ("the Falsified tile is gone", 'tile(s, 864, y, 162, "FALSIFIED EXPECTATIONS",', QUIET + 's, 864, y, 162, "FALSIFIED EXPECTATIONS",'),
    ("Steve loses a machine tile", 'tile_(cols[3][0], y, cols[3][1], "CPU",', QUIET + 'cols[3][0], y, cols[3][1], "CPU",'),
    ("a tile too narrow clips its verdict", 'tile_(114, y, 96, "QUEUED",', 'tile_(114, y, 60, "QUEUED",'),
    ("Steve's how-to-read is gone", 'how_to_read("The second machine', '(lambda t: "")("The second machine'),
    ("FINISHED TODAY drops its receipt rows", '"".join(row(r) for r in rows) or "Nothing yet today."', '"Nothing yet today."'),
    ("RECENT EVENTS prints no rows", "for at, word, txt in rows[:18])", "for at, word, txt in rows[:0])"),
    ("BUGS FOUND counts every day", 'if k == 0 and d.get("outcome") == "FAIL":', 'if d.get("outcome") == "FAIL":'),
    ("Steve's jobs never reach the feed", 'rows += [(at, "Steve job %s"', 'rows += [] and [(at, "Steve job %s"'),
    ("his notes never reach the feed", 'rows += [(at, "your note", txt)', 'rows += [] and [(at, "your note", txt)'),
]
survivors = []
try:
    for name, old, new in MUTANTS:
        check("mutant applies: " + name, old in SRC)
        exec(compile(SRC.replace(old, new, 1), R.__file__, "exec"), R.__dict__)
        try:
            caught = page_problems() + content_problems()
        except Exception as e:      # a panel that cannot parse is caught too
            caught = [repr(e)]
        if not caught:
            survivors.append(name)
finally:
    exec(compile(SRC, R.__file__, "exec"), R.__dict__)
check("every mutant of the page goes red (%d mutants)%s" % (len(MUTANTS), ": survivors " + "; ".join(survivors) if survivors else ""), not survivors)
check("the page's own source passes again after the mutants", not page_problems() and not content_problems())
def built(env):
    page, _, phone = R.build(env, {}, [])
    return page, phone


# ---- SteveDesktop's boundary: each promise has its own named, observable check.
def steve_view(env):
    sv = R.collect_steve(env, {})
    p = {"steve": sv, "steve_cache": env.files.get(R.STEVE_CACHE), "now": env.now(), "steve_why": None}
    return sv, R.steve_text(p), R.steve_svg(p)


env, hist = fixture_env()
sv, text, svg = steve_view(env)
check("steve-games-up-and-driver: both games, remote process state, driver and enriched job purpose", all(w in text for w in (
    "Steve1 UP; driver RUNNER for testq J-run0.a1; FlowWorks guard; chains water,power", "Steve2 DOWN; driver FREE"))
      and all(w in svg for w in ("Steve1 UP", "Steve2 DOWN", "RUNNER", "FlowWorks guard")))
busy, _ = fixture_env(True)
sv_busy, text_busy, svg_busy = steve_view(busy)
check("steve-jobs-by-name: running and pending names, selectors, elapsed time, services and explicit overflow", all(w in text_busy for w in (
    "Steve2: FlowWorks guard; chains water,power; ran 60 s", "waited 2 min", "lane UNMEASURED: FlowWorks guard", "J-wait0", "+ 21 more", "list-item-FlowWorks.service"))
      and "testq-J-run0_a1.service" not in text_busy and "dbus.service" not in text_busy and "+ 21 more" in svg_busy)
rs = readings_of(R_ET.fromstring(svg.removeprefix("<div>").removesuffix("</div>")))
check("steve-every-reading-has-its-age: machine, each game, services, lane folders and steward", all(
    label in rs and any(age in w for _, w in rs[label][1]) for label, age in (
        ("MACHINE SOURCE", "30 s old"), ("STEVE1", "30 s old"), ("STEVE2", "30 s old"),
        ("SERVICES", "30 s old"), ("RUNNING JOBS", "0 s old"), ("QUEUED JOBS", "0 s old"), ("LANE SOURCE", "10 s old"))))
missing, _ = fixture_env()
del missing.files[R.STEVE_CACHE]
sv_missing, missing_text, missing_svg = steve_view(missing)
check("steve-unread-is-unmeasured-with-cause: missing cache with independent lane readings", not sv_missing.get("machine")
      and all(w in missing_text for w in ("UNMEASURED", "no such file", "Steve1 UNMEASURED", "Steve2 UNMEASURED", "FlowWorks guard"))
      and "Steve1 DOWN" not in missing_text and "driver FREE" not in missing_text and "no such file" in missing_svg)
check("steve-unread-is-unmeasured-with-cause: routes nobody read are UNMEASURED, not low", "UNMEASURED, normal all green" in missing_svg and "low, normal all green" not in missing_svg)
check("steve-no-second-connection: build uses cached readings; game, driver and service commands share the one probe", not env.calls
      and all(w in R.STEVE_SCRIPT for w in ("game_lock.py", "game_instance.py", "services_json", "RM_HOST", "~/rm/runner"))
      and not re.search(r"^\s*ssh\b", R.STEVE_SCRIPT, re.M) and "Steve1" in page_of(env) and not env.calls)
strip = before_svg(page_of(env))
check("steve-panel-names-the-games-right: machine lane and both games have chips and panel rows", all(w in strip for w in (
    "SteveDesktop lane RUNNING", "Steve1 UP", "Steve2 DOWN")) and all(w in svg for w in ("STEVEDESKTOP", "Steve1", "Steve2"))
      and not re.search(r"\bSteve (RUNNING|UP|DOWN|UNMEASURED|BRAKED)", strip + svg))

env, _ = fixture_env()
env.files[R.STEVE_CACHE]["good"].update({"locks_json": json.dumps({"out": "{broken JSON"})})
sv, text, svg = steve_view(env)
check("steve-games-up-and-driver: broken game JSON blinds drivers with cause, keeps processes and machine stats", len(sv.get("games", [])) == 2
      and all("UNMEASURED" in g["who"] and "JSON" in g["who"] for g in sv["games"]) and sv["games"][0]["up"] is True and bool(sv.get("machine")))
env.files[R.STEVE_CACHE]["good"]["locks_json"] = json.dumps({"out": json.dumps({"games": "broken shape"})})
sv, text, svg = steve_view(env)
check("steve-unread-is-unmeasured-with-cause: wrong game JSON shape is not FREE", "broken game lock JSON" in text and "driver FREE" not in text)
env, _ = fixture_env()
env.files[R.STEVE_CACHE]["good"]["status_json"] = json.dumps({"out": "Steve1 running pid 29576 port 5174\n"})
sv, text, svg = steve_view(env)
check("steve-games-up-and-driver: Steve2 omitted from a successful nonempty status is DOWN", "Steve1 UP" in text and "Steve2 DOWN" in text)
for output in ({"out": ""}, {"out": "unexpected output"}, {"why": "process list denied"}):
    env.files[R.STEVE_CACHE]["good"]["status_json"] = json.dumps(output)
    sv, text, svg = steve_view(env)
    check("steve-unread-is-unmeasured-with-cause: status %r never becomes DOWN" % output, "Steve1 UNMEASURED" in text
          and "Steve2 UNMEASURED" in text and "Steve2 DOWN" not in text and ("process list denied" if "why" in output else "no game line") in text)
env, _ = fixture_env()
env.files[R.STEVE_CACHE]["good"]["services_json"] = json.dumps({"why": "systemctl exited 1: no bus"})
sv, text, svg = steve_view(env)
check("steve-jobs-by-name: failed services retain the cause rather than none", sv.get("services") is None and "systemctl exited 1: no bus" in text and "no bus" in svg)
env.files[R.STEVE_CACHE]["good"]["services_json"] = json.dumps({"out": None})
sv, text, svg = steve_view(env)
check("steve-unread-is-unmeasured-with-cause: null service output cannot claim none", sv.get("services") is None
      and "readable services_json" in text and "SERVICES: none;" not in text)
env.files[R.STEVE_CACHE]["good"]["services_json"] = json.dumps({"out": "dbus.service loaded active running bus\n"})
sv, text, svg = steve_view(env)
check("steve-jobs-by-name: successfully read services with just dbus say none", sv.get("services") == [] and "SERVICES: none;" in text)
env.files[R.STEVE_CACHE]["good"]["services_json"] = json.dumps({"out": "\n".join("mutation-%s.service loaded active running run" % i for i in range(6))})
sv, text, svg = steve_view(env)
check("steve-jobs-by-name: services have an explicit overflow count", "mutation-0.service" in text and "+ 3 more" in text and "mutation-5.service" not in text)

with tempfile.TemporaryDirectory() as d:
    cache_path = d + "/running_steve.json"
    env, _ = fixture_env()
    with open(cache_path, "w") as f:
        json.dump(env.files[R.STEVE_CACHE], f)
    os.utime(cache_path, (NOW - R.STEVE_STALE - 1, NOW - R.STEVE_STALE - 1))

    class OldCache(Fake):
        def read_json(self, path):
            return R.Env.read_json(self, cache_path) if path == R.STEVE_CACHE else super().read_json(path)

        def mtime(self, path):
            return os.stat(cache_path).st_mtime if path == R.STEVE_CACHE else super().mtime(path)

    old = OldCache(files=env.files, dirs=env.dirs)
    sv, text, svg = steve_view(old)
    check("steve-unread-is-unmeasured-with-cause: stale cache file hides even young embedded figures", not sv.get("machine")
          and "cache file 30 min old" in text and "probe stopped refreshing" in text and "Steve2 DOWN" not in text and "900 GB" not in svg)

class FailedProbe(Fake):
    def steve_probe(self):
        self.calls.append(("ssh", True))
        raise R.Unmeasured("ssh exited 255: no route")

    def write_atomic(self, path, data):
        self.files[path] = json.loads(data)


env, _ = fixture_env()
del env.files[R.STEVE_CACHE]["t"]      # the probe is due
dead = FailedProbe(files=env.files, dirs=env.dirs, fail=("ssh",))
cache = R.probe_steve(dead)
dead.clock += R.STEVE_STALE + 1
sv, text, svg = steve_view(dead)
check("steve-unread-is-unmeasured-with-cause: failed probe retains compatibility keys and stale figures become UNMEASURED", all(k in cache for k in ("good", "good_t", "routes", "why"))
      and cache["routes"]["wsl"] is False and "no route" in cache["why"] and not sv.get("machine")
      and "no route" in text and "30 min old" in text and "no route" in svg and "900 GB" not in svg)
dead.files[R.STEVE_CACHE]["t"] = dead.clock - 20
dead.mtime = lambda path: dead.clock - 20        # each attempt rewrites the file, a failed one too
sv, text, svg = steve_view(dead)
check("steve-unread-is-unmeasured-with-cause: a failed ssh keeps its fresh DOWN routes while the old figures are withheld", sv["routes"].get("wsl") is False
      and "wsl:DOWN; 20 s old" in text and not sv.get("machine"))
env, _ = fixture_env()
for lane, word in (("stevedesktop", "either game"), ("any", "any machine")):
    env.files[R.TESTQ + "/pending/p0.json"]["lane"] = lane
    sv, text, svg = steve_view(env)
    check("steve-jobs-by-name: a queued job of lane %s is not promised to one game" % lane, "%s: FlowWorks guard" % word in text and "Steve1: FlowWorks guard; chains water,power; waited" not in text)
for folder in ("running", "pending"):
    env.dirs[R.TESTQ + "/" + folder] = []
sv, text, svg = steve_view(env)
check("steve-jobs-by-name: looked and empty folders report none and zero", sv["running"] == sv["pending"] == 0
      and "RUNNING JOBS: none;" in text and "QUEUED JOBS: none;" in text)
env.dirs.pop(R.TESTQ + "/pending")
env.dirs[R.TESTQ + "/running"] = ["bad.json"]
env.files[R.TESTQ + "/running/bad.json"] = {"job": "broken"}
sv, text, svg = steve_view(env)
check("steve-unread-is-unmeasured-with-cause: broken job and missing folder cannot claim zero or idle", sv["running"] is None and sv["pending"] is None
      and "running:" in text and "pending:" in text and "UNMEASURED" in text)
env, _ = fixture_env()
env.files[STEWARD]["epoch"] = NOW - R.STEVE_STALE - 1
sv, text, svg = steve_view(env)
check("steve-every-reading-has-its-age: old steward words are withheld with age and cause", sv["state"] is None
      and "steward.json 30 min old" in text and "steward stopped refreshing" in text and bool(sv.get("machine")))
env, _ = fixture_env()
env.files[R.STEVE_CACHE] = ["broken cache"]
sv, text, svg = steve_view(env)
check("steve-unread-is-unmeasured-with-cause: broken cache object preserves lane readings", "broken probe cache" in text
      and "Steve1 UNMEASURED" in text and sv["running"] == 1)


# ---- steve-view-for-augur: the probe writes a decoded block for the Augur dashboard into the cache it already writes.
class ViewProbe(FailedProbe):
    """A due probe whose ssh returns the fixture's own readings, so the view is decoded from what a real probe reports."""
    def steve_probe(self):
        self.calls.append(("ssh", True))
        if "ssh" in self.fail:
            raise R.Unmeasured("ssh exited 255: no route")
        return "\n".join("%s=%s" % kv for kv in self.good.items()) + "\n"


def view_env(fail=()):
    env, _ = fixture_env()
    good = {k: str(v) for k, v in env.files[R.STEVE_CACHE]["good"].items() if k != "cpu_pct"}
    good["claude"] = "2"
    good["stat"] = "cpu 10 0 10 80 0 0 0 0 0 0"
    env.files[R.TESTQ + "/running/r9.json"] = {"job": dict(env.files[R.TESTQ + "/running/r0.json"]["job"], id="J-arch"), "sent": iso(NOW - 60), "attempt": "J-arch.a1", "host": "archmagi"}
    env.dirs[R.TESTQ + "/running"] = ["r0.json", "r9.json"]
    env.files[R.TESTQ + "/pending/p0.json"]["lane"] = "stevedesktop"
    del env.files[R.STEVE_CACHE]["t"]      # the probe is due
    v = ViewProbe(files=env.files, dirs=env.dirs, fail=fail)
    v.good = good
    return v


v = view_env()
view = R.probe_steve(v).get("view") or {}
vm, vg, vj = view.get("machine") or {}, view.get("games") or {}, view.get("jobs") or {}
check("steve-view-for-augur: the probe writes a schema-tagged view naming the host, dated by the write", view.get("schema") == "augur.remote_host/1"
      and view.get("host") == "SteveDesktop" and view.get("written_at") == NOW and v.files[R.STEVE_CACHE].get("view") == view)
check("steve-view-for-augur: machine figures are decoded numbers with their reading time", vm.get("observed_at") == NOW and vm.get("load1") == 0.5
      and vm.get("ncpu") == 18 and abs((vm.get("mem_free_pct") or 0) - 98.4) < 0.1 and vm.get("gpu_pct") == 27.0 and vm.get("agents") == 2 and vm.get("cpu_pct") is None
      and any("cpu_pct" in x for x in vm.get("issues") or []))
rows = {r.get("name"): r for r in vg.get("rows") or []}
check("steve-view-for-augur: each game is up or down with its driver, purpose and the job it runs", vg.get("observed_at") == NOW
      and rows.get("Steve1", {}).get("up") is True and rows["Steve1"].get("driver") == "RUNNER" and rows["Steve1"].get("for") == "testq J-run0.a1"
      and rows["Steve1"].get("job") == "FlowWorks guard; chains water,power" and rows.get("Steve2", {}).get("up") is False and rows["Steve2"].get("driver_state") == "FREE")
run_names = [(r.get("name"), r.get("where"), r.get("since"), r.get("id")) for r in vj.get("running") or []]
check("steve-view-for-augur: running and queued jobs by name, where and since; another machine's job is not this host's", vj.get("observed_at") == NOW
      and run_names == [("FlowWorks guard; chains water,power", "Steve1", NOW - 60, "J-run0")]
      and [(r.get("where"), r.get("since")) for r in vj.get("queued") or []] == [("either game", NOW - 120)])
dead = view_env(fail=("ssh",))
dead.files[R.STEVE_CACHE]["good_t"] = NOW - R.STEVE_STALE - 1
view = R.probe_steve(dead).get("view") or {}
check("steve-view-for-augur: a failed probe writes the machine and games as unknown with the cause and the last good time, jobs still read",
      "no route" in (view.get("machine") or {}).get("unknown", "") and view["machine"].get("last_at") == NOW - R.STEVE_STALE - 1
      and "load1" not in view["machine"] and "unknown" in (view.get("games") or {}) and len((view.get("jobs") or {}).get("running") or []) == 1)
for folder in ("running", "pending"):
    dead.dirs[R.TESTQ + "/" + folder] = []
dead.files[R.STEVE_CACHE].pop("t")
view = R.probe_steve(dead).get("view") or {}
check("steve-view-for-augur: looked-at empty folders are empty lists, not unknown", view["jobs"].get("running") == [] and view["jobs"].get("queued") == []
      and view["jobs"].get("running_why") is None)
dead.dirs.pop(R.TESTQ + "/pending")
dead.files[R.STEVE_CACHE].pop("t")
view = R.probe_steve(dead).get("view") or {}
check("steve-view-for-augur: an unreadable folder is null with its cause, never an empty list", view["jobs"].get("queued") is None
      and "no dir" in (view["jobs"].get("queued_why") or ""))
real_games = R.collect_steve_games
R.collect_steve_games = lambda *a, **k: 1 / 0
dead.files[R.STEVE_CACHE].pop("t")
cache = R.probe_steve(dead)
R.collect_steve_games = real_games
check("steve-view-for-augur: a view that cannot be decoded is written as unknown with the cause, and the probe still writes its file",
      "ZeroDivisionError" in (cache.get("view") or {}).get("unknown", "") and dead.files[R.STEVE_CACHE].get("t") == NOW)

# Execute only the added Python body locally, with subprocesses replaced by fixture executables: no ssh, Windows or /mnt/d.
with tempfile.TemporaryDirectory() as d:
    os.makedirs(d + "/rm/runner")
    for name, body in (("python3", "import json, sys\nprint(json.dumps({'games': []}) if 'game_lock.py' in sys.argv[1] else 'Steve1 stopped port 5174')\n"),
                       ("systemctl", "print('dbus.service loaded active running bus')\n")):
        with open(d + "/" + name, "w") as f:
            f.write("#!" + sys.executable + "\n" + body)
        os.chmod(d + "/" + name, 0o755)
    body = R.STEVE_SCRIPT.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    # Do not repurpose HOME; replace only the fixture runner path in the body being tested.
    body = body.replace("os.path.expanduser('~/rm/runner')", repr(d + "/rm/runner"))
    proc = subprocess.run([sys.executable, "-c", body], env=dict(os.environ, PATH=d), capture_output=True, text=True)
    readings = R.parse_probe(proc.stdout)
    check("steve-no-second-connection: extended probe emits all three readable envelopes", proc.returncode == 0
          and all("out" in json.loads(readings.get(k, "{}")) for k in ("locks_json", "status_json", "services_json")))
    os.rmdir(d + "/rm/runner")
    proc = subprocess.run([sys.executable, "-c", body], env=dict(os.environ, PATH=d), capture_output=True, text=True)
    readings = R.parse_probe(proc.stdout)
    check("steve-unread-is-unmeasured-with-cause: missing runner clone is a cause while service read survives", all("why" in json.loads(readings[k]) for k in ("locks_json", "status_json"))
          and "out" in json.loads(readings["services_json"]))


# --------------------------------------------------------------------------- the fuel gauge
AU = R.account_usage_module()
LATEST, SERIES = str(AU.DATA_DIR / "latest.json"), str(AU.DATA_DIR / "series.jsonl")


def fuel_rec(name, used, hours_to_reset=20.0, age_h=0.1, source="MEASURED", poll_h=None):
    return {"account": name, "source": source, "ts": AU.iso(NOW - (age_h if poll_h is None else poll_h) * 3600), "measured_at": AU.iso(NOW - age_h * 3600),
            "week_pct_used": used, "week_resets_at": AU.iso(NOW + hours_to_reset * 3600), "why": "fixture"}


def fuel_points(name, pairs, hours_to_reset=20.0, source="MEASURED"):
    """pairs: (hours ago, percent used)."""
    return [fuel_rec(name, used, hours_to_reset, age, source) for age, used in pairs]


def fuel_env(latest, series, names=("alpha", "beta", "gamma")):
    env = Fake(ps="", units=[], timers=[], files={LATEST: latest, SERIES: "\n".join(json.dumps(r) for r in series)})
    env.names = list(names)
    return env


def fuel_rows(env):
    return {r["name"]: r for r in R.collect_fuel(env, NOW)}


GOOD_LATEST = {"accounts": {"alpha": fuel_rec("alpha", 95), "beta": fuel_rec("beta", 59), "gamma": fuel_rec("gamma", 90)}}
GOOD_SERIES = (fuel_points("alpha", [(3.1, 87), (2, 90), (1, 93), (0.1, 95)])            # 8 points in 3 h with 5 left over 20 h
               + fuel_points("beta", [(5.9, 57), (3, 58), (0.1, 59)])                    # 2 points in 6 h with 41 left over 20 h
               + fuel_points("gamma", [(3.1, 88.5), (0.1, 90)]))
rows = fuel_rows(fuel_env(GOOD_LATEST, GOOD_SERIES))
check("fuel: every account's week left and hours to reset", rows["alpha"]["left"] == 5 and rows["beta"]["left"] == 41 and abs(rows["alpha"]["hours"] - 20) < 0.01)
check("fuel: a burn faster than what is left reads AHEAD", rows["alpha"]["verdict"] == "AHEAD" and abs(rows["alpha"]["burn"] - 8 / 3) < 0.01 and abs(rows["alpha"]["pace"] - 0.25) < 0.01)
check("fuel: AHEAD says when it runs out", abs(rows["alpha"]["out_in"] - 5 / (8 / 3)) < 0.01 and abs(rows["alpha"]["early"] - (20 - 5 / (8 / 3))) < 0.01)
check("fuel: a burn slower than what is left reads BEHIND", rows["beta"]["verdict"] == "BEHIND" and 30 < rows["beta"]["unused"] < 41)

# EQUAL: 12 points in 6 h is 2 points/h; 40 left over 20 h is exactly 2.
eq = {"accounts": {"alpha": fuel_rec("alpha", 60)}}
rows = fuel_rows(fuel_env(eq, fuel_points("alpha", [(6.1, 48), (3, 54), (0.1, 60)])))
check("fuel: a burn at the pace reads EQUAL", rows["alpha"]["verdict"] == "EQUAL" and rows["alpha"]["why"] is None)
check("fuel: the registry says who should be here, a missing account says UNMEASURED", rows["beta"]["why"] == "no reading on file" and rows["gamma"]["why"] == "no reading on file")
# ---- who is in use now (RUNNING_PAGE_BUILD_WHOSE_TANK_IS_THIS)
class LiveEnv(Fake):
    def __init__(self, out=None, exc=None, **kw):
        super().__init__(**kw)
        self.status, self.exc = out, exc

    def run(self, argv, timeout=20):
        if self.exc:
            raise self.exc
        return 0, self.status


LIVE_JSON = json.dumps({"ok": True, "live": "beta", "live_email": "secret.person@example.com", "interrupted_switch": False})
def live_page(**kw):
    env = LiveEnv(ps="", files={LATEST: GOOD_LATEST, SERIES: "\n".join(json.dumps(r) for r in GOOD_SERIES)}, **kw)
    env.names = ["alpha", "beta", "gamma"]
    pg, _, ph = R.build(env, {}, [])
    return pg, ph
pg, ph = live_page(out=LIVE_JSON)
check("live: the headline names the account in use", "IN USE NOW: beta" in pg and "IN USE NOW: beta" in ph)
check("live: only the in-use account's row is marked", pg.count(">IN USE<") == 1 and "> beta" in ph and "> alpha" not in ph and "> gamma" not in ph)
check("live: the email never reaches the page or the phone copy", "secret.person" not in pg and "secret.person" not in ph)
pg, ph = live_page(out="", exc=R.Unmeasured("claude-account not found"))
check("live: a failed claude-account reads UNMEASURED and marks no row", "IN USE NOW: UNMEASURED (claude-account not found)" in pg and ">IN USE<" not in pg and "IN USE NOW: UNMEASURED" in ph)
pg, ph = live_page(out=json.dumps({"ok": False, "live": "beta"}))
check("live: not ok never guesses an account", "IN USE NOW: UNMEASURED" in pg and ">IN USE<" not in pg)
pg, ph = live_page(out=json.dumps({"ok": True, "live": "beta", "interrupted_switch": True}))
check("live: an interrupted switch is said", "SWITCH INTERRUPTED" in pg and "SWITCH INTERRUPTED" in ph)
import subprocess as _sp
pg, ph = live_page(out="", exc=_sp.TimeoutExpired("claude-account", 10))
check("live: a timeout reads UNMEASURED", "timed out" in pg)
# the 15% band edges, sweeping the burn past the pace with a span big enough that the whole-percent error is narrower
for burn, want in ((2.29, "EQUAL"), (1.71, "EQUAL"), (2.5, "AHEAD"), (1.5, "BEHIND")):
    samples = [(NOW - 6 * 3600, 20.0, None), (NOW, 20.0 + burn * 6, None)]
    got = R.fuel_burn(samples, 40.0, 20.0, NOW, None)
    check("fuel: at 2 points/h pace, burn %s reads %s" % (burn, want), got["verdict"] == want)
# a flat account with little left over a long way is BEHIND at the 6 h grain, though 3 h cannot tell
flat = R.fuel_burn([(NOW - 5.9 * 3600, 95, None), (NOW - 3 * 3600, 95, None), (NOW, 95, None)], 5.0, 18.0, NOW, None)
check("fuel: a flat account widens to 6 h and reads BEHIND", flat["verdict"] == "BEHIND" and flat["span"] > 5 * 3600)
check("fuel: one point over the span cannot be told from the pace", R.fuel_burn([(NOW - 3 * 3600, 90, None), (NOW, 91, None)], 9.0, 30.0, NOW, None)["verdict"] == "EQUAL")
check("fuel: a strong 3 h rise uses 3 h, not the older calm", abs(R.fuel_burn([(NOW - 6 * 3600, 50, None), (NOW - 3 * 3600, 50, None), (NOW, 62, None)], 38.0, 10.0, NOW, None)["burn"] - 4) < 0.01)
check("fuel: nothing left and nothing burning is EQUAL", R.fuel_burn([(NOW - 6 * 3600, 100, None), (NOW, 100, None)], 0.0, 10.0, NOW, None)["verdict"] == "EQUAL")
check("fuel: nothing left and still burning is AHEAD", R.fuel_burn([(NOW - 3 * 3600, 94, None), (NOW, 100, None)], 0.0, 10.0, NOW, None)["verdict"] == "AHEAD")
# "current" burn: an account burning 0.9 points/h for 100 h, then idle the last 30 h, is idle NOW. The window may reach back
# at most 6 h (literal, not R.FUEL_FAR, so a widened constant goes red): BEHIND at 0 points/h, never AHEAD on days-old burn.
idle = [(NOW - (130 - h) * 3600, min(h, 100) * 0.9, None) for h in range(131)]
idle_got = R.fuel_burn(idle, 10.0, 20.0, NOW, None)
check("fuel: an account idle 30 h after days of burning reads BEHIND at 0 points/h",
      idle_got["verdict"] == "BEHIND" and idle_got["burn"] == 0)
check("fuel: the current burn window spans 6 h or less, never days", 0 < idle_got["span"] <= 6 * 3600)
# the same cap with readings 12 h apart: nothing inside 6 h but the newest, so there is no current rate to read
check("fuel: readings only older than 6 h give no current rate",
      R.guarded(R.fuel_burn, [(NOW - 24 * 3600, 10, None), (NOW - 12 * 3600, 40, None), (NOW, 70, None)], 30.0, 20.0, NOW, None)[1] is not None)


def fuel_refuses(samples, measured=NOW, reset=None):
    return R.guarded(R.fuel_burn, samples, 40.0, 20.0, measured, reset)[1]


check("fuel: no series points is no rate", fuel_refuses([]) is not None)
check("fuel: under an hour of readings is no rate", "of readings" in fuel_refuses([(NOW - 1800, 50, None), (NOW, 52, None)]))
check("fuel: a reset between readings cuts the rate there", "of readings" in fuel_refuses([(NOW - 5 * 3600, 90, None), (NOW - 600, 1, None), (NOW, 2, None)]))
check("fuel: a reset time an hour off cuts the rate there", "of readings" in fuel_refuses([(NOW - 5 * 3600, 1, NOW - 86400), (NOW - 600, 1, NOW + 86400), (NOW, 2, NOW + 86400)]))
check("fuel: a one-minute jitter in the reset time does not", fuel_refuses([(NOW - 5 * 3600, 1, NOW + 86400 - 60), (NOW, 2, NOW + 86400)]) is None)
check("fuel: a series that stopped before the reading is no rate", "stopped" in fuel_refuses([(NOW - 5 * 3600, 1, None), (NOW - 2 * 3600, 2, None)]))
check("fuel: a series from another week is no rate", "another week" in fuel_refuses([(NOW - 5 * 3600, 1, NOW - 3600 * 9), (NOW, 2, NOW - 3600 * 9)], reset=NOW + 3600 * 20))

# ESTIMATE points never make a rate: they repeat an old figure with a new time
mixed = fuel_points("alpha", [(5, 40)]) + fuel_points("alpha", [(4, 40), (3, 40), (0.2, 40)], source="ESTIMATE") + fuel_points("alpha", [(0.1, 50)])
got = R.fuel_series("\n".join(json.dumps(r) for r in mixed), False, AU)["alpha"]
check("fuel: the series keeps MEASURED points only", len(got) == 2 and got[0][1] == 40 and got[1][1] == 50)
torn = 'XX torn", "week_pct_used": 99}\n' + json.dumps(fuel_rec("alpha", 7)) + "\nnot json\n[1]\n" + json.dumps(dict(fuel_rec("alpha", True), account="alpha"))
check("fuel: torn, foreign and non-numeric lines are skipped", [x[1] for x in R.fuel_series(torn, True, AU)["alpha"]] == [7])
check("fuel: a truncated tail drops its first line", R.fuel_series(json.dumps(fuel_rec("alpha", 7)) + "\n" + json.dumps(fuel_rec("alpha", 8)), True, AU)["alpha"][0][1] == 8)

# every way a reading can be stale or unreadable says UNMEASURED and withholds the figures
BURN = fuel_points("alpha", [(5, 40), (0.1, 41)])
for label, rec in (("measured over 45 min ago", fuel_rec("alpha", 41, age_h=1, poll_h=0.1)),
                   ("polled over 45 min ago", fuel_rec("alpha", 41, age_h=0.1, poll_h=1)),
                   ("source UNMEASURED", dict(fuel_rec("alpha", None), source="UNMEASURED", why="no reading yet")),
                   ("an ESTIMATE too old", fuel_rec("alpha", 41, age_h=2, poll_h=0.1, source="ESTIMATE")),
                   ("no week figure", fuel_rec("alpha", None)),
                   ("no measurement time", dict(fuel_rec("alpha", 41), measured_at=None)),
                   ("measured in the future", fuel_rec("alpha", 41, age_h=-1, poll_h=0.1)),
                   ("week figure past 100", fuel_rec("alpha", 120)),
                   ("reset passed", fuel_rec("alpha", 41, hours_to_reset=-1)),
                   ("no reset time", dict(fuel_rec("alpha", 41), week_resets_at=None)),
                   ("a garbled percentage", dict(fuel_rec("alpha", 41), week_pct_used="lots")),
                   ("not even a record", ["junk"])):
    env = fuel_env({"accounts": {"alpha": rec, "beta": fuel_rec("beta", 59), "gamma": fuel_rec("gamma", 90)}}, BURN)
    rows = fuel_rows(env)
    page, phone = built(env)
    panel_ = page[page.index("ACCOUNTS, THIS WEEK"):page.index("NEEDS YOU") if "NEEDS YOU" in page else None]
    alpha = panel_[panel_.index("alpha"):panel_.index("beta")]
    check("fuel: %s says UNMEASURED with no figures" % label, rows["alpha"]["why"] and "left" not in rows["alpha"] and "UNMEASURED" in alpha and "% left" not in alpha and "resets in" not in alpha)
    check("fuel: %s says UNMEASURED on the phone" % label, any(x.startswith("alpha UNMEASURED: ") for x in phone.splitlines()))
    check("fuel: %s leaves the other accounts' figures" % label, any(x.startswith("beta 41% left") for x in phone.splitlines()))

rows = fuel_rows(fuel_env({"accounts": {"alpha": fuel_rec("alpha", 41, age_h=0.5, source="ESTIMATE")}}, fuel_points("alpha", [(6, 40), (0.5, 41)])))
check("fuel: a young ESTIMATE is shown, and marked", rows["alpha"]["estimate"] and R.fuel_left(rows["alpha"]) == "at most 59% left" and rows["alpha"]["verdict"])

# the whole panel
for label, env in (("latest.json missing", fuel_env(None, [])), ("latest.json not an object", fuel_env([1], [])), ("no accounts key", fuel_env({"updated": "x"}, []))):
    if label == "latest.json missing":
        env.files.pop(LATEST)
    page, phone = built(env)
    check("fuel: %s: the panel says UNMEASURED" % label, re.search(r'ACCOUNTS, THIS WEEK</div><div[^>]*>[^<]*</div><b style="color:%s">UNMEASURED' % R.WARN, page) is not None and "account fuel (" in page)
    check("fuel: %s: the phone says UNMEASURED" % label, any(x.startswith("ACCOUNTS UNMEASURED") for x in phone.splitlines()))
env = fuel_env(GOOD_LATEST, [])
env.files.pop(SERIES)
page, phone = built(env)
rows = fuel_rows(env)
check("fuel: an unreadable series keeps the week figures and says burn UNMEASURED", rows["alpha"]["left"] == 5 and "unreadable" in rows["alpha"]["burn_why"] and "burn UNMEASURED" in page and "AHEAD" not in page[:page.index("How to read")])
check("fuel: the same on the phone", any(x.startswith("alpha 5% left") and x.endswith("burn UNMEASURED") for x in phone.splitlines()))

# the page and the phone, all three readings at once, first thing on the page
three = {"accounts": {"alpha": fuel_rec("alpha", 95), "beta": fuel_rec("beta", 59), "gamma": fuel_rec("gamma", 60)}}
series = GOOD_SERIES[:7] + fuel_points("gamma", [(6.1, 48), (3, 54), (0.1, 60)])
page, phone = built(fuel_env(three, series))
head = page[page.index("ACCOUNTS, THIS WEEK"):page.index("How to read")]
check("fuel: the panel is above Needs you", page.index("ACCOUNTS, THIS WEEK") < page.index("NEEDS YOU"))
check("fuel: the panel holds all three accounts with figures and words", all(w in head for w in ("alpha", "beta", "gamma", "5% left", "41% left", "40% left", "resets in", "AHEAD", "EQUAL", "BEHIND", "runs out in", "unused at the reset", "lasts to about the reset")))
check("fuel: the how-to-read explains the three words", all(w in page for w in ("AHEAD: burning faster", "EQUAL: about right", "BEHIND: burning slower")))
check("fuel: no blank line inside the panel (Typora would end the block)", "\n\n" not in head)
lines = phone.splitlines()
check("fuel: the phone leads with the three accounts", lines.index("ACCOUNTS, THIS WEEK") < lines.index("LIVE TESTING, 24 H") and any(x.startswith("alpha 5% left, resets in") and "AHEAD, out " in x for x in lines) and any(x.startswith("beta 41% left") and "BEHIND, " in x for x in lines) and any(x.startswith("gamma 40% left") and x.endswith("EQUAL") for x in lines))
check("fuel: the phone copy is plain text", not any("<" in x for x in lines[lines.index("ACCOUNTS, THIS WEEK"):lines.index("ACCOUNTS, THIS WEEK") + 4]))
broken = fuel_env(three, series)
real_mod, R.account_usage_module = R.account_usage_module, lambda: 1 / 0
check("fuel: a broken account_usage.py costs the panel, not the page", "UNMEASURED" in built(broken)[0] and "account fuel (" in built(broken)[0])
R.account_usage_module = real_mod

# The real doors. Fake above overrides account_names and the file reads, so nothing above reaches the real Env; a blind
# check deleted Env.account_names and every check stayed green while the real page lost its gauge. Here a child process
# (the folders are read when account_usage is imported) uses the real Env, registry, account_usage.write() and CLI; only
# the two folders are fixtures, and the child refuses to run if they are not.
HERE = os.path.dirname(os.path.abspath(__file__))
REAL_SEED = r'''
import json, os, sys, time
sys.path.insert(0, sys.argv[1])
import account_usage as AU
root, scene = sys.argv[2], sys.argv[3]
assert str(AU.DATA_DIR).startswith(root) and str(AU.ACCOUNTS_DIR).startswith(root), "fixture folders not in force"
now = time.time()
def rec(name, used, age_h=0.1):
    t = now - age_h * 3600
    return AU.record(name, t, "MEASURED", "fixture", "fixture", {"week_pct_used": used, "week_resets_at": AU.iso(now + 20 * 3600)}, AU.iso(t))
HISTORY = {"alpha": [(3.1, 87), (2, 90), (1, 93)], "beta": [(5.9, 57), (3, 58)], "gamma": [(6.1, 48), (3, 54)]}
LAST = {"alpha": 95, "beta": 59, "gamma": 60}
if scene == "absent":
    del HISTORY["gamma"], LAST["gamma"]
for name, points in HISTORY.items():
    for age, used in points:
        AU.write({name: rec(name, used, age)}, now - age * 3600)
latest = {name: rec(name, used) for name, used in LAST.items()}
if scene == "stale":
    latest["beta"] = rec("beta", 59, 72)
AU.write(latest, now)
if scene == "noseries":
    os.remove(AU.DATA_DIR / "series.jsonl")
if scene == "nolatest":
    os.remove(AU.DATA_DIR / "latest.json")
'''
REAL_INSPECT = r'''
import json, sys, time
sys.path.insert(0, sys.argv[1])
import running_now as R
env = R.Env()
print(json.dumps({"names": env.account_names(), "rows": R.collect_fuel(env, time.time())}))
'''
REAL_WRITE = r'''
import os, sys
sys.path.insert(0, sys.argv[1])
import running_now as R
out = sys.argv[2]
R.OUT_DIR, R.OUT, R.PHONE_OUT, R.STATE = out, out + "/RELENTLESS_NOW.md", out + "/RELENTLESS_NOW_PHONE.md", out + "/state.json"
real_write = R.Env.write_atomic
def inside(self, path, text):
    assert path.startswith(out), "a fixture run tried to write " + path
    return real_write(self, path, text)
R.Env.write_atomic = inside
R.append_history = R.refresh_fleet = R.probe_steve = lambda *a, **k: None
sys.exit(R.run(write=True)[0])
'''


def real_scene(scene, accounts="# a comment line\nalpha a@fixture\nbeta b@fixture\ngamma g@fixture\n"):
    """Seed one scene through the real writer; returns (env for children, tempdir object, its path)."""
    tmp = tempfile.TemporaryDirectory()
    os.makedirs(tmp.name + "/accounts")
    with open(tmp.name + "/accounts/accounts.tsv", "w") as f:
        f.write(accounts)
    child = dict(os.environ, RM_ACCOUNTS_DIR=tmp.name + "/accounts", RM_ACCOUNT_USAGE_DIR=tmp.name + "/usage")
    seeded = subprocess.run([sys.executable, "-c", REAL_SEED, HERE, tmp.name, scene], env=child, capture_output=True, text=True, timeout=60)
    check("fuel real: %s: the real writer seeded the fixture" % scene, seeded.returncode == 0)
    return child, tmp


def real_cli(child, *flags):
    got = subprocess.run([sys.executable, os.path.join(HERE, "running_now.py")] + list(flags), env=child, capture_output=True, text=True, timeout=120)
    return got.returncode, got.stdout


def accounts_block(phone):
    lines = phone.splitlines()
    return lines[lines.index("ACCOUNTS, THIS WEEK") + 1:lines.index("ACCOUNTS, THIS WEEK") + 4] if "ACCOUNTS, THIS WEEK" in lines else []


def phone_row(block, name):
    return next((x for x in block if x.startswith(name + " ")), "")


# every account healthy: the real registry names all three, and the real CLI gives the three readings
child, tmp = real_scene("three")
got = subprocess.run([sys.executable, "-c", REAL_INSPECT, HERE], env=child, capture_output=True, text=True, timeout=60)
seen = json.loads(got.stdout) if got.returncode == 0 else {"names": None, "rows": []}
check("fuel real: Env.account_names reads accounts.tsv, comment skipped, in file order", seen["names"] == ["alpha", "beta", "gamma"])
check("fuel real: collect_fuel on the real Env reads all three with a verdict", {r["name"]: r.get("verdict") for r in seen["rows"]} == {"alpha": "AHEAD", "beta": "BEHIND", "gamma": "EQUAL"})
rc, phone = real_cli(child, "--phone")
block = accounts_block(phone)
check("fuel real: --phone exits 0 with three rows", rc == 0 and len(block) == 3)
check("fuel real: --phone alpha: % left, reset, AHEAD", re.match(r"alpha 5% left, resets in \d+(\.\d+)? h: AHEAD, out ", phone_row(block, "alpha")) is not None)
check("fuel real: --phone beta: % left, reset, BEHIND", re.match(r"beta 41% left, resets in \d+(\.\d+)? h: BEHIND, ", phone_row(block, "beta")) is not None)
check("fuel real: --phone gamma: % left, reset, EQUAL", re.match(r"gamma 40% left, resets in \d+(\.\d+)? h: EQUAL", phone_row(block, "gamma")) is not None)
rc, page = real_cli(child, "--print")
head = page[page.index("ACCOUNTS, THIS WEEK"):page.index("How to read")] if "ACCOUNTS, THIS WEEK" in page and "How to read" in page else ""
check("fuel real: --print panel holds the three accounts with figures and words", rc == 0 and all(w in head for w in ("alpha", "beta", "gamma", "5% left", "41% left", "40% left", "resets in", "AHEAD", "EQUAL", "BEHIND")))
out = tmp.name + "/out"
os.makedirs(out)
wrote = subprocess.run([sys.executable, "-c", REAL_WRITE, HERE, out], env=child, capture_output=True, text=True, timeout=120)
disk = {}
for leaf in ("RELENTLESS_NOW.md", "RELENTLESS_NOW_PHONE.md"):
    if os.path.exists(out + "/" + leaf):
        with open(out + "/" + leaf) as f:
            disk[leaf] = f.read()
check("fuel real: a real write puts the three readings in RELENTLESS_NOW.md", wrote.returncode == 0 and all(w in disk.get("RELENTLESS_NOW.md", "") for w in ("41% left", "AHEAD", "EQUAL", "BEHIND")))
check("fuel real: a real write puts the three rows in RELENTLESS_NOW_PHONE.md", len(accounts_block(disk.get("RELENTLESS_NOW_PHONE.md", ""))) == 3)
tmp.cleanup()

# an account in the registry with no reading must show as UNMEASURED, not vanish
child, tmp = real_scene("absent")
got = subprocess.run([sys.executable, "-c", REAL_INSPECT, HERE], env=child, capture_output=True, text=True, timeout=60)
seen = json.loads(got.stdout) if got.returncode == 0 else {"rows": []}
gamma = [r for r in seen["rows"] if r["name"] == "gamma"]
check("fuel real: collect_fuel: registry account absent from latest.json is UNMEASURED", len(seen["rows"]) == 3 and len(gamma) == 1 and gamma[0]["why"] == "no reading on file")
rc, phone = real_cli(child, "--phone")
block = accounts_block(phone)
check("fuel real: --phone keeps the absent account's UNMEASURED row", rc == 0 and phone_row(block, "gamma") == "gamma UNMEASURED: no reading on file" and "AHEAD" in phone_row(block, "alpha"))
tmp.cleanup()

# a stale reading, a lost series and a lost latest.json, through the real file doors
child, tmp = real_scene("stale")
rc, phone = real_cli(child, "--phone")
block = accounts_block(phone)
check("fuel real: a 3-day-old reading says UNMEASURED, figures withheld", phone_row(block, "beta").startswith("beta UNMEASURED: last poll") and "%" not in phone_row(block, "beta") and "AHEAD" in phone_row(block, "alpha"))
tmp.cleanup()
child, tmp = real_scene("noseries")
rc, phone = real_cli(child, "--phone")
block = accounts_block(phone)
check("fuel real: a missing series.jsonl keeps the figures and says burn UNMEASURED", len(block) == 3 and phone_row(block, "beta").startswith("beta 41% left") and all(x.endswith("burn UNMEASURED") for x in block))
tmp.cleanup()
child, tmp = real_scene("nolatest")
rc, phone = real_cli(child, "--phone")
check("fuel real: a missing latest.json says ACCOUNTS UNMEASURED", rc == 0 and any(x.startswith("ACCOUNTS UNMEASURED") for x in phone.splitlines()) and "ACCOUNTS, THIS WEEK" not in phone)
tmp.cleanup()


print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
