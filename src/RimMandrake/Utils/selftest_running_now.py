#!/usr/bin/env python3
"""selftest_running_now.py - running_now.py offline, on fixtures (no systemd, no Windows, no ssh, no state files).

Covers: a source that cannot be read says UNMEASURED and never a 0 count; the tree accounts for every process counted;
an unmatched python process is shown under NOT RECOGNISED with its pid; a Relentless unit finds its item by the hash;
a place held with no process is called out; idle under a brake is the first, red thing on the page; the 24 h counters
count a verdict once; the page is on disk before ssh is tried and a dead ssh changes nothing but the route dots; the
write is atomic, a failed build keeps the old page and the next good page carries a STALE banner; no blank line sits
inside the details block (Typora would end the block there and spill the rest).
The fuel gauge: every account's week left and time to reset with AHEAD/EQUAL/BEHIND against the spend left; a stale or
unreadable reading, or a burn with no honest rate, says UNMEASURED.
"""
import json
import os
import re
import sys
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import running_now as R  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


NOW = 1793741698.0
ITEM = "GRAFFITI_V1_LIVE_PROOF_1"
SHORT = R.short(ITEM)
WORKER_CG = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/rm-relentless-work-%s-g1.service\n" % SHORT
DISPATCH_STATE = R.AGENT + "/dispatcher/state.json"
STEWARD = R.TESTQ + "/steward.json"
BRIDGE = R.BRIDGE_FILES[0]
SHADOW = R.RELENTLESS_STORE + "/shadow.jsonl"
JOURNAL = R.RELENTLESS_STORE + "/journal.jsonl"
STAFFING = R.RELENTLESS_STORE + "/staffing.json"
BREAKER = R.RELENTLESS_STORE + "/breaker.json"


class Fake(R.Env):
    """Every door to the world is shut unless a fixture opens it."""

    def __init__(self, ps="", units=None, timers=None, files=None, cg=None, fail=(), items=None, dirs=None):
        self.ps_text, self.units, self.timers, self.files, self.cg, self.fail = ps, units, timers, files or {}, cg or {}, fail
        self.items, self.dirs = items, dirs or {}
        self.clock = NOW
        self.bridge, self.fleet, self.mods = None, None, None
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

    def tick_show(self):
        raise R.Unmeasured("no tick in a selftest")

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

    def item_states(self):
        if self.items is None:
            raise R.Unmeasured("no item state files")
        return self.items

    def ledger_titles(self, wanted):
        return {}

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
check("no invented zero: no 'Relentless 0' and no 'bridge FREE'", "Relentless 0" not in head and "bridge FREE" not in head)
check("unreadable Dispatcher is UNMEASURED and not a green age", "Dispatcher UNMEASURED" in head or "last tick UNMEASURED" in page)
check("the tree says UNMEASURED and not 0 processes", "UNMEASURED" in fence(page) and "TOTAL 0" not in fence(page))

# 2. the tree accounts for every process counted
env = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running"}])
p = R.gather(env, {})
lines, roots = R.tree_lines(p)
check("every process counted lands in exactly one root", p["tree"]["total"] >= 5 and roots == p["tree"]["total"])
text = "\n".join(lines)
check("the tree's TOTAL line shows the same sum", "TOTAL %d Linux processes" % roots in text)
check("no tree line outgrows the code fence", max(len(x) for x in lines) <= 84)
env = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running"}])
far = R.gather(env, {})
moved = next(x for x in far["tree"]["groups"].values() if x["family"] == "relentless")
moved.update(family="seats", name="CONDUCTOR", cwd="/somewhere/else", model="o", who="CONDUCTOR", unit="x", age=1.0)
check("a Conductor sitting outside the clones is counted once", R.tree_lines(far)[1] == far["tree"]["total"])

# 3. a worker finds its item by the unit's hash, and shows it in plain words with its children
check("worker row carries the item's plain words", "Graffiti v1 live proof 1" in text and "item UNMEASURED" not in text)
check("worker row sums its child processes", re.search(r"claude 1 .*= 3", text) is not None)
check("heading counts a work unit as a Builder", "Builders 1, Judges 0" in text)

# 4. unmatched process shown with its pid; matched one not
page = page_of(Fake(ps=PS))
nr = fence(page).split("NOT RECOGNISED")[1]
check("unmatched python process listed with pid", "pid 4242" in nr and "match.py" in nr)
check("matched account page is not listed as unrecognised", "4343" not in nr)
check("the strip raises it", "NOT RECOGNISED" in before_svg(page))

# 5. a place with no process is named; one with a process is not
env = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running"}, {"item": "SOME_ITEM_NO_PROCESS", "status": "checking"}])
ghosts = R.ghost_places(R.gather(env, {}))
check("an item holding a place with no unit is a ghost", [(g if isinstance(g, str) else g.get("item")) for g in ghosts] == ["SOME_ITEM_NO_PROCESS"])
check("ghosts are unknown, not none, when the tree is unread", R.ghost_places(R.gather(Fake(fail=("ps",), items=[{"item": ITEM, "status": "checking"}]), {})) is None)
check("the strip says so", "1 place with no process" in before_svg(page_of(env)))

# 6. a Dispatcher far behind leads the strip
page = page_of(Fake(files={DISPATCH_STATE: {"last_tick": "2026-11-03T20:00:00Z"}}))
check("old Dispatcher tick raises DISPATCHER NOT TICKING", "DISPATCHER NOT TICKING" in before_svg(page))

# 6b. the breaker file keeps old counts after it closes: open means `until` is still ahead
check("breaker with an old `opens` count is clear", R.breaker_word({"breaker": {"opens": {"k": {"n": 2}}}, "now": NOW}) == "clear")
check("breaker with `until` ahead is OPEN", R.breaker_word({"breaker": {"until": NOW + 60}, "now": NOW}) == "OPEN")
check("breaker with `until` passed is clear", R.breaker_word({"breaker": {"until": NOW - 60}, "now": NOW}) == "clear")
check("unreadable breaker is UNMEASURED", R.breaker_word({"breaker": None, "now": NOW}) == "UNMEASURED")

# 7. the bridge mirror file parses both ways
held = R.collect_bridge(Fake(files={BRIDGE: "# comment\nHELD OPERATIONS since 2026-11-03T20:00:00Z\nfor a proof\n"}))
free = R.collect_bridge(Fake(files={BRIDGE: "FREE since 2026-11-03T20:00:00Z\n"}))
check("bridge HELD names who and why", held["state"] == "HELD" and held["who"] == "OPERATIONS" and held["for"] == "a proof")
check("bridge FREE has no holder (the word since is not a name)", free["state"] == "FREE" and free["who"] == "")

# 8. idle under a brake is the first, red thing on the page
files = {STEWARD: {"state": "BRAKED", "fault": True, "reason": "two filler jobs failed", "epoch": NOW - 30}}
dirs = {R.TESTQ + "/running": [], R.TESTQ + "/pending": []}
page = page_of(Fake(files=files, dirs=dirs))
head = before_svg(page)
check("braked and idle reads as trouble in the strip", "Steve BRAKED + IDLE" in head)
check("trouble comes first in the strip", "Relentless" in head and head.index("Steve BRAKED") < head.index("Relentless"))
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
check("the panel says UNMEASURED there and not 0", "DONE 24 H" in page and "UNMEASURED" in page.split("DONE 24 H")[1][:200])

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
check("a panel that cannot draw costs that panel, not the page", "SteveDesktop: UNMEASURED" in page and "SteveDesktop panel" in before_svg(page) and "RELENTLESS" in page)

# 8d. a state file that cannot be read is an UNMEASURED Relentless, not a short count
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
check("a numbered seat scope under a live Builder is that Builder, not a window", [g["label"] for g in groups if g["family"] != "upkeep" and g["procs"][0]["pid"] >= 6000] == ["worker"]
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
sv = R.collect_steve(env, state, {"by_status": {"done": [{"item": "X_ITEM", "done_at": NOW - 50}]}})
check("a job born 10 days ago and finished now counts in the 24 h", sv["jobs_known"] and sv["done"] == 1 and sv["failed"] == 0)
check("Steve's Live Testing reads that job", sv["live"]["rows"] == {"PASS": 1, "FAIL": 1} and sv["live"]["bugs"] == 1 and sv["live"]["closed"] == 1)
check("Steve's busy share is its job's minutes over 24 h", abs(sv["live"]["busy"] - 600 / 86400) < 1e-6)
check("a job finished long ago keeps only its finish time", set(state["steve_jobs"]["J1.json"]) == {"v", "f"})
env.files = {STEWARD: job_files[STEWARD]}
sv = R.collect_steve(env, state, None)
check("a result already read is not read again", sv["jobs_known"] and sv["done"] == 1)
state["steve_jobs"].pop(OLD_JOB)
state["steve_jobs"]["J1.json"] = {"f": 5}     # the shape before this change: read again, not trusted
sv = R.collect_steve(env, state, None)
check("an unreadable result leaves the day's counts unknown, not short", sv["jobs_known"] is False)
check("an unreadable result leaves Live Testing UNMEASURED, not short", sv["live"] is None)
env_ns = Fake(dirs={done_dir: [], R.TESTQ + "/running": [], R.TESTQ + "/pending": []})
sv = R.collect_steve(env_ns, {}, None)
check("a dead steward keeps the queue readings and says why", sv["state"] is None and sv["running"] == 0 and "steward UNMEASURED" in sv["reason"] and sv["age"] is None)
check("an unread history is UNMEASURED, a missing one is merely new", "UNMEASURED" in R.window_stats(R.read_history(Fake(fail=())) , NOW, 86400, "24 h")[0])
check("unread item states are no count of waiting items", R.it_waiting(None) is None and "UNMEASURED items wait" in R.game_idle_text({"idle_pct": 1, "window_min": 1, "used_min": 0, "waiting": None}))

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
items = {"by_status": {"done": [{"item": "A", "done_at": NOW - 10}, {"item": "E", "done_at": NOW - 10}, {"item": "A2", "done_at": NOW - 90000}]}}
hist = [{"t": NOW - 60, "n": 1, "f": {"game": 1}}, {"t": NOW - 120, "n": 1, "f": {"game": 0}}]
lv = R.collect_archmagi_live(env, NOW, items, hist)
check("proof rows by result count the 24 h only", lv["rows"] == {"PASS": 1, "FAIL": 2, "UNMEASURED": 1})
check("a clause failing twice is one bug", lv["bugs"] == 1)
check("closed by a live proof needs both the close and a PASS", lv["closed"] == 1)
check("Archmagi's busy share is bridge time over 24 h", abs(lv["busy"] - 1800 / 86400) < 1e-6)
check("game idle share is one minus held, per two-hour point", abs(lv["idle_trend"][-1] - (1 - 1800 / 7200)) < 1e-6 and len(lv["idle_trend"]) == R.TREND_POINTS)
check("game up share comes from the page's own samples", lv["game_up"] == 0.5)
broken = Fake(files={R.LIVE_RUNS: "{bad\n" + ROWS})
check("a broken runs.jsonl line is UNMEASURED, never a short count", R.guarded(R.collect_archmagi_live, broken, NOW, items, [])[1] is not None)
env.bridge = None
lv2 = R.collect_archmagi_live(env, NOW, items, hist)
check("no ledger: busy is UNMEASURED, not 0", lv2["busy"] is None and lv2["idle_trend"] is None)

st = {"status": "held", "hold": {"at": NOW - 100}}
check("oldest in a stage reads the field that stage writes", R.stage_since(st) == NOW - 100 and R.stage_since({"status": "game", "game": {"entered_at": 5}}) == 5)
check("a stage with no clock has no age", R.stage_since({"status": "done"}) is None)
check("oldest finds the stage's oldest item", R.oldest_in({"by_status": collections_d(queued=[{"item": "Y", "status": "queued", "enrolled_at": NOW - 9}, {"item": "Z", "status": "queued", "enrolled_at": NOW - 90}])}, "queued", NOW) == (90.0, "Z"))
check("mods accepted reads the state after the name", R.mods_status_counts("Abyss   STALE   x\nB   RED (last)  y\nC  GREEN  z\nnoise\n") == {"STALE": 1, "RED": 1, "GREEN": 1})
check("mods accepted with no line is UNMEASURED", R.guarded(R.mods_status_counts, "nothing\n")[1] is not None)

jd = json.dumps({"at": iso(NOW - 3600), "acts": [{"do": "done", "item": "I1"}, {"do": "blind_fail", "item": "I2"}]}) + "\n" + json.dumps({"at": iso(NOW - 90000), "acts": [{"do": "done", "item": "I3"}]}) + "\n"
env = Fake(files={SHADOW: "", JOURNAL: jd})
thr = R.collect_throughput(env, NOW)
check("the trend lines count the journal's closes and Judge fails", sum(thr["trend"]["closed"]) == 2 and sum(thr["trend"]["blind_fail"]) == 1)
check("a usual range needs a whole window the record reaches past", thr["usual"].get("closed") is None)
jd2 = jd + json.dumps({"at": iso(NOW - 5 * 86400), "acts": []}) + "\n"
thr = R.collect_throughput(Fake(files={SHADOW: "", JOURNAL: jd2}), NOW)
check("a usual range is the windows before this one", thr["usual"]["closed"] == (0, 1))
env.files.update({R.RELENTLESS_STORE + "/spend-%s.json" % R.time.strftime("%Y%m%d", R.time.gmtime(NOW)): {"spent": 8000000}})
day = R.time.strftime("%Y%m%d", R.time.gmtime(NOW))
tk = R.collect_tokens(env, NOW, {"closed_day": {day: 2, **{}}, } if False else {"closed_day": R.collections.Counter({day: 2})})
check("tokens per item closed is the day's spend over its closes", tk[0]["per"] == 4000000)
check("a day still running is no full day", R.full_days(tk, NOW) == [])

# the whole page, every section, on a full fixture
FLEET = {"needs": {"count": 2, "lines": [], "topics": [{"topic": "DRAW", "items": ["DRAW_A", "DRAW_B"], "q": "Look at the bridge", "others": ["<Other> line"]}, {"topic": "K", "items": ["K_X"], "q": "Keep it?", "others": []}],
                   "answered": [{"item": "ANS_ITEM", "q": "old"}]},
         "receipts": [{"item": "R1", "glyph": "✓", "title": "t", "where": "FlowWorks", "receipt": {"check": "PASS", "outcome": "Did the thing.", "commits": 2, "tokens": 5000}}],
         "mods": [{"name": "FlowWorks", "meta": "1 done", "backlog": "Backlog: 1 open", "proof": "Blind check PASS", "next": "Next thing", "waits": ["waits on you: x"],
                   "tasks": [{"mark": "✓", "kind": "pass", "title": "A task <b>", "date": "1 Nov"}], "more": 3}],
         "total_mods": 10, "t": NOW, "good_t": NOW,
         "accepted": {"green": 1, "stale": 2, "red": 3, "draft": 1, "never": 3, "total": 10}}
ITEMS = [{"item": ITEM, "status": "running", "started_at": NOW - 60}, {"item": "Q1", "status": "queued", "enrolled_at": NOW - 7200}]
full = Fake(ps=PS, cg=WORKER, items=ITEMS, files={R.FLEET_CACHE: FLEET, STEWARD: {"state": "RUNNING", "epoch": NOW}, R.LIVE_RUNS: ROWS, SHADOW: "", JOURNAL: jd})
full.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
page, sample, phone = R.build(full, {}, [])
for word in ("How to read", "Relentless-style Builder or Judge", "NEEDS YOU, 2", "RECENT EVENTS", "FINISHED TODAY, 1", "PROGRESS BY MOD, 1 MODS", "ARCHMAGI", "STEVEDESKTOP", "LIVE TESTING, LAST 24 H",
             "TRENDS, 48 H", "TOKENS PER ITEM CLOSED (TRIAL)", "MODS ACCEPTED", "1 of 10", "GAME UNMEASURED", "game idle", "live proofs", "oldest", "normal", "FALSIFIED EXPECTATIONS", "9 of 8", "Judge's FAIL", "<title>"):
    check("the page shows: " + word, word in page)
check("the page has a how-to-read line for each of its panels", page.count("How to read:") == 7)
check("CLOSED PER HOUR is gone, the 24 h histogram stays", "CLOSED PER HOUR" not in page and "LAST 24 H, EVENTS" in page)
check("the old names are gone", "blind checker" not in page.lower() and "checkers" not in page and "workers " not in page.split("<details>")[0].replace("workers can", ""))
check("Needs you folds a topic into one row and escapes it", page.count("Look at the bridge") == 1 and "DRAW, 2 items" in page and "&lt;Other&gt; line" in page and "<Other>" not in page)
check("an answered item leaves the list and says so", "1 more you already answered" in page and "ANS_ITEM" in page)
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

with tempfile.TemporaryDirectory() as d:
    real_store, R.RELENTLESS_STORE = R.RELENTLESS_STORE, d
    os.makedirs(d + "/items/a")
    os.makedirs(d + "/items/b")
    with open(d + "/items/a/state.json", "w") as f:
        f.write('{"item": "A", "status": "running"}')
    with open(d + "/items/b/state.json", "w") as f:
        f.write('{"item": "B", "sta')
    got, why = R.guarded(R.Env().item_states)
    R.RELENTLESS_STORE = real_store
check("a torn item file makes the items UNMEASURED", got is None and "1 item state files unreadable" in why)

# 8d2. a process table that cannot be attributed is UNMEASURED, not a believable zero
class NoCgroup(Fake):
    def cgroup(self, pid):
        raise PermissionError("cgroup unreadable")


page = page_of(NoCgroup(ps=PS, items=[{"item": ITEM, "status": "running"}]))
check("an unreadable cgroup makes the tree UNMEASURED, and raises no ghost place", "PROCESS TREE: UNMEASURED" in page and "with no process" not in before_svg(page))

# 8e. the Steve script omits the game when tasklist fails rather than reporting 0
check("Steve's game reading is conditional on tasklist's exit", 'if t=$(timeout 5' in R.STEVE_SCRIPT and "</dev/null" in R.STEVE_SCRIPT)

# 9. 24 h counters: one verdict with several rule rows counts once; put-backs are not called FAIL
rows = [{"at": NOW - 60, "nonce": "a", "word": "PASS", "rule": 1}, {"at": NOW - 60, "nonce": "a", "word": "PASS", "rule": 2},
        {"at": NOW - 60, "nonce": "b", "word": "FAIL", "rule": 1}, {"at": NOW - 90000, "nonce": "c", "word": "PASS", "rule": 1}]
acts = {"at": "2026-11-03T20:00:00Z", "acts": [{"do": "returned", "item": "X"}, {"do": "done", "item": "Y"}, {"do": "game_refused", "item": "Z"}]}
good_journal = json.dumps(acts)
_, why = R.guarded(R.collect_throughput, Fake(files={SHADOW: 'garbage\n{"at": 1}\n', JOURNAL: good_journal}), NOW)
check("a broken verdict record makes the counts UNMEASURED, not short", why and "shadow.jsonl line 1" in why)
_, why = R.guarded(R.collect_throughput, Fake(files={SHADOW: '{"at": 1}\n{"at": ', JOURNAL: good_journal}), NOW)
check("a last verdict line still being written is not damage", not why)
_, why = R.guarded(R.collect_throughput, Fake(files={SHADOW: "", JOURNAL: '{"acts": broken\n' + good_journal + "\n"}), NOW)
check("a broken journal record makes the counts UNMEASURED, not short", why and "journal.jsonl" in why)
check("a history line that is not a record does not stop the page", R.read_history(Fake(files={R.HIST: 'null\n[1]\n5\n'})) == [])
_, why = R.guarded(R.collect_throughput, Fake(files={SHADOW: "", JOURNAL: "no record at all\n" + good_journal + "\n"}), NOW)
check("so does one too broken to name its acts", why and "journal.jsonl" in why)
t = R.collect_throughput(Fake(files={SHADOW: "\n".join(json.dumps(r) for r in rows), JOURNAL: json.dumps(acts)}), NOW)
check("a verdict with several rule rows counts once", t["pass"] == 1)
check("older than 24 h is out", t["pass"] + t["fail"] == 2)
check("a put-back is not a check FAIL", t["blind_fail"] == 1 and t["put_back"] == 1)
check("closed and refused come from the journal", t["closed"] == 1 and t["refused"] == 1)

# 10. history honesty
hist = [{"t": NOW - 600, "n": 5}, {"t": NOW - 300, "n": 7}, {"t": NOW - 60, "n": 9}]
line, rows = R.window_stats(hist, NOW, 86400, "24 h")
check("short history says it does not yet cover 24 h", "not yet a full 24 h" in line and "min 5 / median 7 / max 9" in line)
check("empty history says no history yet", "no history yet" in R.window_stats([], NOW, 86400, "24 h")[0])

# 11. writes, in a private directory
with tempfile.TemporaryDirectory() as d:
    R.OUT_DIR, R.OUT, R.HIST, R.STATE, R.STEVE_CACHE = d, d + "/RUNNING_NOW.md", d + "/h.jsonl", d + "/s.json", d + "/steve.json"
    R.PHONE_OUT, R.FLEET_CACHE = d + "/RUNNING_NOW_PHONE.md", d + "/fleet.json"
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
    good_f = Fake(ps=PS)
    good_f.fleet, good_f.mods = {"mods": [], "receipts": [], "needs": {"count": 0, "topics": []}, "total_mods": 5}, "A  GREEN x\nB RED y\n"
    good_f.clock = NOW + 2 * R.PROBE_EVERY + 300
    R.refresh_fleet(good_f)
    saved = json.load(open(R.FLEET_CACHE))
    check("a fleet refresh caches the sections and the mods accepted", saved["accepted"] == {"green": 1, "stale": 0, "red": 1, "draft": 0, "never": 3, "total": 5} and saved["why"] is None)
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

# the game's idle share (RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS): the page and its text twin, and never an invented 100%
runs = "".join(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - m * 60)), "log": "x.log"}) + "\n"
               for m in (1, 2, 200))
page = page_of(Fake(files={R.LIVE_RUNS: runs}, items=[{"item": ITEM, "status": "game"}]))
check("the page shows the game's idle share", "idle 99% of 180 min" in page and "GAME idle 99% of the last 180 min: a proof held it in 2, 1 items wait" in page)
page = page_of(Fake(items=[{"item": ITEM, "status": "game"}]))
check("an unreadable runs file says idle UNMEASURED", "idle UNMEASURED" in page and "GAME idle UNMEASURED" in page and "game idle share" in before_svg(page))

# the owner's token pause (rules only_system_and_live): a banner above everything while on, nothing while off, never a guess
def pause_env(rules):
    env = Fake(ps=PS)
    if rules is not None:
        env.files[R.RULES_FILE] = rules
    return env


def built(env):
    page, _, phone = R.build(env, {}, [])
    return page, phone


page, phone = built(pause_env({"only_system_and_live": True}))
check("pause on: the banner is on the page, above the panels", "TOKEN PAUSE ON" in before_svg(page) and page.index("TOKEN PAUSE ON") < page.index("<svg"))
check("pause on: the phone copy leads with it", phone.splitlines()[1].startswith("TOKEN PAUSE ON") and "<" not in phone.splitlines()[1])
check("pause on: the page does not call it unmeasured", "oken pause UNMEASURED" not in page and "token pause (" not in page)
for label, rules in (("off", {"only_system_and_live": False}), ("missing key", {"enabled": True})):
    page, phone = built(pause_env(rules))
    check("pause %s: no banner on the page or the phone" % label, "TOKEN PAUSE" not in page and "oken pause" not in page and "TOKEN PAUSE" not in phone)
for label, env in (("unreadable", pause_env(None)), ("not an object", pause_env([1]))):
    page, phone = built(env)
    check("pause %s: the page says UNMEASURED, not on and not off" % label, "**Token pause UNMEASURED**" in before_svg(page) and "token pause (" in page and "TOKEN PAUSE ON" not in page)
    check("pause %s: the phone copy says UNMEASURED" % label, "TOKEN PAUSE UNMEASURED" in phone and "TOKEN PAUSE ON" not in phone)
check("the real rules path is the file relentless.py reads", os.path.realpath(R.RULES_FILE) == os.path.realpath(os.path.join(R.HERE, "..", "rimflow", "relentless_rules.json")) and os.path.isfile(R.RULES_FILE))
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
    json.dump({"only_system_and_live": True}, tmp)
real_rules, R.RULES_FILE = R.RULES_FILE, tmp.name
check("the real Env reads the rules file", R.collect_pause(R.Env()) is True)
os.unlink(tmp.name)
check("the real Env on a missing rules file is unread, not off", R.guarded(R.collect_pause, R.Env())[0] is None)
R.RULES_FILE = real_rules

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
    check("fuel: %s: the panel says UNMEASURED" % label, 'ACCOUNTS, THIS WEEK</div><b style="color:%s">UNMEASURED' % R.WARN in page and "account fuel (" in page)
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
check("fuel: the phone leads with the three accounts", lines.index("ACCOUNTS, THIS WEEK") < lines.index("RELENTLESS PIPELINE") and any(x.startswith("alpha 5% left, resets in") and "AHEAD, out " in x for x in lines) and any(x.startswith("beta 41% left") and "BEHIND, " in x for x in lines) and any(x.startswith("gamma 40% left") and x.endswith("EQUAL") for x in lines))
check("fuel: the phone copy is plain text", not any("<" in x for x in lines[lines.index("ACCOUNTS, THIS WEEK"):lines.index("ACCOUNTS, THIS WEEK") + 4]))
broken = fuel_env(three, series)
real_mod, R.account_usage_module = R.account_usage_module, lambda: 1 / 0
check("fuel: a broken account_usage.py costs the panel, not the page", "UNMEASURED" in built(broken)[0] and "account fuel (" in built(broken)[0])
R.account_usage_module = real_mod

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
