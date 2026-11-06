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

    def ledger_blocks(self, wanted):
        return getattr(self, "blocks", {})

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
env_j = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running"},
                                      {"item": "SOME_ITEM_JUDGED", "status": "checking", "check": {"run": {"out": "/r/judged.json"}}}])
env_j.files = dict(getattr(env_j, "files", {}) or {}, **{"/r/judged.json": "{}"})
check("a checking item whose Judge wrote its result is no ghost: the tick reads it (PASS3_FLOOD board)",
      R.ghost_places(R.gather(env_j, {})) == [])
env_l = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running"},
                                      {"item": "SOME_ITEM_JUDGING", "status": "checking", "check": {"run": {"out": "/r/judging.json"}}}])
env_l.files = dict(getattr(env_l, "files", {}) or {}, **{"/r/judging.json": ""})
st_l = R.collect_items(env_l)["by_status"]["checking"][0]
check("a Judge's out file that systemd opened empty at launch is no verdict: a dead one is still a ghost (RUNNING_BOARD_FIX_FINISHED_JUDGES_CRY_WOLF)",
      "_judge_out" not in st_l and [(g if isinstance(g, str) else g.get("item")) for g in R.ghost_places(R.gather(env_l, {}))] == ["SOME_ITEM_JUDGING"])

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
# OWNER_REVIEW_BUILD_SHOWS_READY_BEFORE_ASKED: NEEDS YOU names the save and the time of a ready showing, or why not
SHOWN = {"items": {"K_X": {"state": "READY TO SHOW", "save": "Showing_K_X", "minutes": 6, "dir": "D:\\ClaudeWork\\rimmandrake\\showings\\K_X"},
                   "DRAW_A": {"state": "BLOCKED", "blocked_on": "DRAW_UP_FIX", "why": "on DRAW_UP_FIX: his note is not built yet"}}}
sp, _s, sphone = R.build(Fake(ps=PS, cg=WORKER, items=ITEMS, files={R.FLEET_CACHE: FLEET, R.SHOWINGS: SHOWN}), {}, [])
check("NEEDS YOU shows a ready showing's save and time", "READY TO SHOW: load save Showing_K_X, about 6 min" in sp and "Showing_K_X" in sphone)
check("NEEDS YOU says a blocked showing is BLOCKED and on what, never ready", "DRAW_A: showing BLOCKED on DRAW_UP_FIX" in sp and "Showing_DRAW" not in sp)
check("no showings file: NEEDS YOU still renders, with no showing words", "READY TO SHOW" not in page and "NEEDS YOU, 2" in page)
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
# 9b. RUNNING_BOARD_FIX_DONE_COUNT_LAGS_PASSES: Done is what is done NOW; a ledger reopen (a top-level reenrol record, no
# acts) takes one away, so 5 closes and 3 reopens moved Done by 2 and the owner read the stall as failures
flow = [{"at": "2026-11-03T20:00:00Z", "acts": [{"do": "check_passed", "item": "D%d" % i}, {"do": "done", "item": "D%d" % i}]} for i in range(5)]
flow += [{"at": "2026-11-03T20:01:00Z", "do": "reenrol", "item": "R1", "why": "reopened on the ledger after done"},
         {"at": "2026-11-03T20:01:00Z", "do": "reenrol", "item": "R2", "why": "hand", "was": "done"},
         {"at": "2026-11-03T20:01:00Z", "do": "reenrol", "item": "R3", "why": "reopened on the ledger after done", "was": "done"},
         {"at": "2026-11-03T20:01:00Z", "do": "reenrol", "item": "R4", "why": "wrongly retired", "was": "retired"},
         {"at": "2026-11-03T20:01:00Z", "do": "reenrol", "item": "R5", "why": "wrongly retired"}]
t = R.collect_throughput(Fake(files={SHADOW: "", JOURNAL: "\n".join(json.dumps(j) for j in flow) + "\n"}), NOW)
check("a close counts once, not with its check_passed", t["closed"] == 5)
check("reopens out of done are counted, retirements undone are not", t["reopened"] == 3)
check("the Done card says both, so a flat count reads as closes less reopens", R.done_flow(t) == "24 h: +5 closed, -3 reopened")
check("no stage note claims Done only grows", all("only grows" not in w for _, w in R.STAGE_NORMAL.values()))

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

# ---- every number on every instrument panel, read panel by panel and tile by tile, never as words anywhere on the page.
# The text twin, the how-to-read prose and another machine's panel cannot satisfy these. A list row (a process, an item line,
# a receipt) is a list; the numbers judged here are the instruments: the owner's "every number gets a verdict and rough normal range".
VERDICT = re.compile(r"(^|[;:] )(ok|normal|high|low|bad)\b")
RANGE = re.compile(r"\b(normal|usual|rough) \S")
LIVE_TILES = {"BUSY / IDLE", "PROOF ROWS BY RESULT", "CLOSED BY LIVE PROOF", "BUGS FOUND", "FALSIFIED EXPECTATIONS"}
EXPECTED = {
    "Relentless": {"PLACES", "TICK", "BREAKER", "LIVE GAME", "TOKENS TODAY", "TOKENS PER ITEM CLOSED (TRIAL)", "MODS ACCEPTED, GOAL IS ALL", "FAIL LOOP"}
    | {x.upper() for x in R.BELT + R.SIDE} | {"BAR " + x for x in ("CLOSED", "PASS", "WEAK", "FAIL", "GAME UNMEASURED", "REFUSED", "PUT BACK")}
    | {"TREND " + x for x in ("closed", "Judge fails", "live proofs", "game idle")},
    "Archmagi": {"UPTIME", "LOAD", "WSL RAM USED", "EXT4 FREE", "D: FREE", "GAME THIS 24 H"} | LIVE_TILES,
    "SteveDesktop": {"STATE", "ROUTES", "UPTIME", "LOAD", "WSL RAM USED", "CPU", "DISK FREE", "GPU", "GAME", "RUNNING", "QUEUED", "DONE 24 H", "FAILED 24 H", "LAST JOB", "ROWS/HOUR 24 H",
                     "STEWARD WROTE", "MACHINE READING"} | LIVE_TILES,
}
NAME_BANDS = {"NAMES " + x.upper() for x in ("running", "candidate", "checking", "closing", "held", "blocked")}
NOT_A_NUMBER = {"FALSIFIED EXPECTATIONS"} | NAME_BANDS      # nothing records the first, and a band holds names: nothing to judge in either
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
            if not (name == "Relentless" and label in NAME_BANDS):     # a band exists only while its stage overflows its card
                bad.append("%s: a reading nobody pinned: %s" % (name, label))
        inside = {id(t) for g, _ in rs.values() for t in g.iter(SVGNS + "text")}
        for t in root.iter(SVGNS + "text"):
            words = "".join(t.itertext())
            if id(t) not in inside and re.search(r"\d", words) and not FRAME.match(words):
                bad.append("%s: naked number: %s" % (name, words))
        for label, (_, texts) in rs.items():
            rowt = {id(t) for r in g_of(rs, label).iter(SVGNS + "g") if r.get("data-item") for t in r.iter(SVGNS + "text")}
            texts = [(size, w) for size, w, t in texts_with(rs, label) if id(t) not in rowt]   # an item row is a name, not a note
            notes = [w for size, w in texts if (size == "9" or label in ("FAIL LOOP", "STATE")) and not w.startswith("top ")]
            for w in notes:
                if label not in NOT_A_NUMBER and not judged(w):
                    bad.append("%s %s: note with no verdict or range: %s" % (name, label, w))
                if "…" in w:
                    bad.append("%s %s: note clipped: %s" % (name, label, w))
                if label.rstrip("#").lower() in R.BELT + R.SIDE and len(w) > 32:
                    bad.append("%s %s: note wider than its card: %s" % (name, label, w))
            value = [w for size, w in texts if w not in notes and re.search(r"\d", w)]
            if value and label not in NOT_A_NUMBER and not notes:
                bad.append("%s %s: a number with no note: %s" % (name, label, value))
            if any(w == "UNMEASURED" for _, w in texts):
                bad.append("%s %s: UNMEASURED on the full fixture" % (name, label))
    root = pans.get("Relentless")
    if root is not None:
        rs = readings_of(root)
        lines = list(root.iter(SVGNS + "polyline"))
        if len(lines) != 4 or len({x.get("stroke") for x in lines}) != 4:
            bad.append("trends: %d polylines drawn, want 4 in 4 colours" % len(lines))
        for lab in ("closed", "Judge fails", "live proofs", "game idle"):
            g = rs.get("TREND " + lab)
            if g is None or len(list(g[0].iter(SVGNS + "polyline"))) != 1:
                bad.append("trend %s: no line of its own" % lab)
            elif len(g[0].find(SVGNS + "polyline").get("points").split()) != R.TREND_POINTS:
                bad.append("trend %s: not %d points" % (lab, R.TREND_POINTS))
        for stage in R.BELT + R.SIDE:
            if stage.upper() in rs and not any(re.match(r"(ok|high|low), normal \S", w) for _, w in rs[stage.upper()][1]):
                bad.append("%s: no verdict on its count" % stage)
        if cards_have_oldest:
            for stage in ("QUEUED", "RUNNING", "CANDIDATE", "CHECKING", "CLOSING", "GAME", "HELD", "BLOCKED", "STOPPING", "RETIRING"):
                if stage in rs and not any(w.startswith("oldest ") and judged(w) for _, w in rs[stage][1]):
                    bad.append("%s: no judged oldest" % stage)
            if "DONE" in rs and not any(w.startswith("last ") and judged(w) for _, w in rs["DONE"][1]):
                bad.append("DONE: no judged last close")
    # a how-to-read line right under each panel, and the one under the Pipeline explains places
    for name, words in (("Relentless", "9 of 8"), ("Archmagi", "Busy means"), ("SteveDesktop", "Busy means"), ("Chain", "Follow an arrow")):
        hit = re.search(r'aria-label="%s[^\n]*</svg></div>\n(?:\n*)<div[^\n]*How to read:</b>([^\n]*)' % name, page)
        if not hit or words not in hit.group(1):
            bad.append("%s: no how-to-read under it saying %s" % (name, words))
    if not re.search(r'aria-label="Relentless[^\n]*</svg></div>\n<div[^\n]*How to read:</b>[^\n]*A place is ', page):
        bad.append("no how-to-read under the Pipeline says what a place is")
    if "CLOSED PER HOUR" in page:
        bad.append("CLOSED PER HOUR is back")
    return bad


def fixture_env(extreme=False):
    """Everything readable; `extreme` puts every reading out of its normal, the long way, so a note that does not fit gets clipped and shows."""
    day = lambda k: R.time.strftime("%Y%m%d", R.time.gmtime(NOW - k * 86400))  # noqa: E731
    per = 3 if extreme else 1
    rows = [{"at": iso(NOW - 50 - i), "item": "A", "criterion": "A%d" % i, "outcome": "FAIL" if extreme else "PASS"} for i in range(3)]
    rows += [{"at": iso(NOW - 80 - i), "item": "C", "criterion": "U%d" % i, "outcome": "UNMEASURED"} for i in range(40 if extreme else 1)]
    journal = [{"at": iso(NOW - 3600), "acts": [{"do": "done", "item": "A"}, {"do": "blind_fail", "item": "I2"}]}]
    journal += [{"at": iso(NOW - k * 86400 - 60), "acts": [{"do": "done", "item": "D%d" % i} for i in range(k + 1)]} for k in range(1, 5)]
    stage_item = {"queued": {"enrolled_at": 1}, "running": {"started_at": 1}, "candidate": {"candidate": {"at": 1}}, "checking": {"check": {"at": 1}}, "closing": {"tomb_since": 1},
                  "game": {"game": {"entered_at": 1}}, "held": {"hold": {"at": 1}}, "blocked": {"blocked_at": 1}, "stopping": {"stopping_since": 1}, "retiring": {"stopping_since": 1}}
    age = 30 * 3600 if extreme else 60

    def aged(d):
        return {k: (aged(v) if isinstance(v, dict) else NOW - age) for k, v in d.items()}

    items = []
    for stage, fields in stage_item.items():
        top = R.STAGE_NORMAL[stage][0]
        for i in range(top + 1 if extreme else 1):
            items.append(dict(aged(fields), item="%s_%d" % (stage.upper(), i), status=stage))
    items += [{"item": "OVER", "status": "done"}, {"item": "OUT", "status": "retired"}]
    done_dir = R.TESTQ + "/done"
    job = "J%sT000000Z-aaaaaa.json" % day(10)
    files = {R.FLEET_CACHE: FLEET, STEWARD: {"state": "BRAKED" if extreme else "RUNNING", "epoch": NOW - (900 if extreme else 10), "reason": "x", "since": iso(NOW - 9000)},
             R.LIVE_RUNS: "\n".join(json.dumps(r) for r in rows) + "\n", SHADOW: "", JOURNAL: "\n".join(json.dumps(j) for j in journal) + "\n",
             done_dir + "/" + job: {"job": {"purpose": "guard", "mod": "FlowWorks", "item": "A"},
                                    "result": {"outcome": "DONE", "started": iso(NOW - 7700), "finished": iso(NOW - (7100 if extreme else 100)), "rows": [{"chain": "c", "row": "r", "verdict": "PASS"}, {"chain": "c", "row": "s", "verdict": "PASS"}], "counts": {"PASS": 2}}},
             R.STEVE_CACHE: {"good_t": NOW - (2000 if extreme else 30), "routes": {"tailscale": True, "lan": not extreme, "wsl": True},
                             "good": {"up": "100" if extreme else "20000", "load": "99.9" if extreme else "0.5", "cores": "18", "ram": "63000 64000" if extreme else "1000 64000", "disk": "50 1000" if extreme else "900 1000",
                                      "gpu": "NVIDIA GeForce RTX 2080 Ti, %s, 4400, 11264" % ("99" if extreme else "27"), "game": "0" if extreme else "1", "cpu_pct": 99 if extreme else 3}}}
    files[R.RELENTLESS_STORE + "/queue_next.json"] = {"t": NOW - 30, "free": ["QUEUED_0"], "waiting": []}
    files.update({STAFFING: {"t": NOW - 5, "target": 8, "places": 8, "spent_today": 950e6 if extreme else 30e6}, BREAKER: {"until": NOW - 60}, BRIDGE: "FREE since 2026-11-03T20:00:00Z\n"})
    for k in range(0, 5):
        files[R.RELENTLESS_STORE + "/spend-%s.json" % day(k)] = {"spent": (900e6 if extreme and k == 0 else 50e6 * (k + 1))}
    pending = ["p%d.json" % i for i in range(25 if extreme else 1)]

    class Full(Fake):
        def local_stats(self):
            return {"up": 100.0 if extreme else 90000.0, "load": 99.9 if extreme else 7.0, "cores": 14, "ram": (34000, 35000) if extreme else (8000, 35000), "disk": 50 if extreme else 500, "disk_d": 50 if extreme else 1700}

        def tick_show(self):
            return {"ActiveState": "activating", "TimeoutStartUSec": "20min", "Result": "success", "mono": 10000.0, "ExecMainStartTimestampMonotonic": str(int((10000 - (1100 if extreme else 60)) * 1e6))}

    env = Full(ps=PS, cg=WORKER, items=items, files=files, dirs={done_dir: [job], R.TESTQ + "/running": ["r%d.json" % i for i in range(per)], R.TESTQ + "/pending": pending})
    env.bridge = [(NOW - 3600, "taken"), (NOW - 1800, "released")]
    return env, [{"t": NOW - 60, "n": 1, "f": {"game": 0 if extreme else 1}}, {"t": NOW - 120, "n": 1, "f": {"game": 1 if not extreme else 0}}]


LONG = "RUNNING_PAGE_BUILD_NAMES_ON_THE_BELT_AND_THEN_SOME"      # longer than any real name (44 measured 2026-11-03)
TWIN = LONG[:-1] + "X"                                           # the two differ only at the end: a clip makes them one


def names_env(running=6, closing=30, queued=7, done=9, next_order=None):
    """Real-length names on every stage; closing holds enough to overflow its card and running does not."""
    env, hist = fixture_env()
    items = [dict(x) for x in env.items if x["status"] not in ("running", "closing", "candidate", "checking", "queued")]
    def add(stage, name, **kw):
        items.append(dict({"item": name, "status": stage}, **kw))
    add("running", LONG, started_at=NOW - 3000)
    add("running", TWIN, started_at=NOW - 60)
    for i in range(running - 2):
        add("running", "%s_%d" % (LONG, i), started_at=NOW - 100 - i)
    add("candidate", "CANDIDATE_" + LONG, candidate={"at": NOW - 70})
    add("checking", "CHECKING_" + LONG, check={"at": NOW - 80})
    for i in range(closing):
        add("closing", "CLOSING_%d_%s" % (i, LONG), tomb_since=NOW - 90 - i)
    order = next_order or ["QUEUED_%d_%s" % (i, LONG) for i in range(queued)]
    for name in reversed(order):        # enrolled in reverse: an alphabetical or file-order list cannot pass by luck
        add("queued", name, enrolled_at=NOW - 500)
    for i in range(done):
        add("done", "DONE_%d" % i)
    env.items = items
    env.files[R.RELENTLESS_STORE + "/queue_next.json"] = {"t": NOW - 30, "free": order[:2], "waiting": order[2:]}
    env.files[JOURNAL] = "\n".join(json.dumps({"at": iso(NOW - 60 * k), "acts": [{"do": "done", "item": "CLOSED_%d_%s" % (k, LONG)}]}) for k in range(1, 7)) + "\n"
    return env, hist


def joined(texts):
    """The characters of a reading, line breaks gone: a name wrapped in full is still in here whole."""
    return "".join(w.replace(" ", "") for _, w in texts)


def names_problems():
    """The owner's ask, sentence by sentence, on real-length names: which items, at which stage, whole, in a layout that still holds."""
    bad = []
    env, hist = names_env()
    page = R.build(env, {}, hist)[0]
    root = panels_of(page)["Relentless"]
    rs = readings_of(root)
    body = lambda label: joined(rs[label][1]) if label in rs else ""  # noqa: E731
    for stage, names in (("RUNNING", [LONG, TWIN] + ["%s_%d" % (LONG, i) for i in range(4)]), ("CANDIDATE", ["CANDIDATE_" + LONG]), ("CHECKING", ["CHECKING_" + LONG])):
        for n in names:
            if n not in body(stage):
                bad.append("%s does not name %s whole" % (stage, n))
    if "NAMES CLOSING" not in rs:
        bad.append("thirty closing names have no band")
    for i in range(30):
        if "CLOSING_%d_%s" % (i, LONG) not in body("NAMES CLOSING"):
            bad.append("the closing band misses name %d" % i)
    if "all30namedbelow" not in body("CLOSING"):
        bad.append("the closing card does not point at its band")
    if "…" in "".join(w for k in rs for _, w in rs[k][1] if k.split(" ")[-1] in ("QUEUED", "RUNNING", "CANDIDATE", "CHECKING", "CLOSING", "DONE")):
        bad.append("a belt name ends in an ellipsis")
    q = body("QUEUED")
    at = [q.find("QUEUED_%d_%s" % (i, LONG)) for i in range(R.NEXT_SHOWN)]
    if -1 in at or at != sorted(at):
        bad.append("queued does not show the next few, in the tick's order: %s" % at)
    if "QUEUED_%d_%s" % (R.NEXT_SHOWN, LONG) in q or "+3more" not in q:
        bad.append("queued does not stop at the next few with a count of the rest")
    if "nextinline:" not in q or "notfreetostart:" not in q:
        bad.append("queued does not say which names may start")
    d = body("DONE")
    if not all("CLOSED_%d_%s" % (k, LONG) in d for k in (1, 2, 3)) or "CLOSED_4_" in d or "+%dearlier" % (10 - 3) not in d:
        bad.append("done does not show the latest few with a count of the rest: %s" % d[:120])
    # the layout holds: every line inside its card or band, every card level, nothing past the bottom
    cards = {}
    for label, (g, _) in rs.items():
        if label.lower() in R.BELT:
            x = min(float(t.get("x")) for t in g.iter(SVGNS + "text"))
            cards[label] = x - 10
    bottoms = {}
    rects = [r for r in root.iter(SVGNS + "rect") if r.get("width") == "152.0"]
    for label, x in cards.items():
        box = next((r for r in rects if float(r.get("x")) == x), None)
        bottoms[label] = float(box.get("y")) + float(box.get("height")) if box is not None else None
        for t in rs[label][0].iter(SVGNS + "text"):
            w = "".join(t.itertext())
            if t.get("font-family") != R.MONO or t.get("font-size") != "10.5":
                continue
            if float(t.get("x")) + len(w) * R.MONO_CHAR > x + 152:
                bad.append("%s: line past the card's right edge: %s" % (label, w))
            if box is None or float(t.get("y")) + 3 > bottoms[label]:
                bad.append("%s: line below the card's bottom: %s" % (label, w))
    if len(set(bottoms.values())) != 1:
        bad.append("the belt cards are not level: %s" % bottoms)
    side = float(next(t.get("y") for t in rs["GAME"][0].iter(SVGNS + "text")))
    if bottoms and side <= max(v or 0 for v in bottoms.values()):
        bad.append("the set-aside row runs under the belt")
    ys = [(float(t.get("y")), "".join(t.itertext())) for t in root.iter(SVGNS + "text")]
    if max(ys)[0] > float(root.get("viewBox").split()[3]):
        bad.append("the panel is shorter than what it draws: %s" % (max(ys),))
    band_ys = [float(t.get("y")) for t in rs["NAMES CLOSING"][0].iter(SVGNS + "text")] if "NAMES CLOSING" in rs else []
    trend_y = float(next(t.get("y") for t in rs["BAR CLOSED"][0].iter(SVGNS + "text"))) if "BAR CLOSED" in rs else 0
    if band_ys and not (side < min(band_ys) and max(band_ys) < trend_y):
        bad.append("the band overlaps the rows around it")
    # the plain-text twin and the process tree carry the same words in full
    chunk = page.split("-- the panels as plain text --")[-1].split("-- Archmagi --")[0]
    flat = re.sub(r"[\s│]", "", chunk)
    if not all(n in flat for n in (LONG, TWIN, "CLOSING_29_" + LONG, "QUEUED_0_" + LONG, "CLOSED_1_" + LONG)):
        bad.append("the plain-text twin does not name them whole")
    if any(len(ln) > R.FENCE_WIDTH for ln in chunk.splitlines() if "CLOSING_" in ln or "QUEUED_" in ln or "oldest" in ln):
        bad.append("a plain-text name line is wider than the fence")
    # the tree's build row and the oldest line give the whole title, the row's columns still whole and inside the fence
    words = "A build row's plain words run far past the room the counts leave, and the owner wants to read all of them to the very last word"
    env = Fake(ps=PS, cg=WORKER, items=[{"item": ITEM, "status": "running", "started_at": NOW - 60}, {"item": "GHOST_OF_A_PLACE", "status": "checking", "check": {"at": NOW - 9}}])
    env.ledger_titles = lambda wanted: {i: words + " " + i for i in wanted}
    tp = R.gather(env, {})
    tree = R.tree_lines(tp)[0]
    flat = " ".join(re.sub(r"^[│ ├└─┄]*", "", x) for x in tree)
    row = next((x for x in tree if " build " in x and "= " in x), "")
    rest = tree[tree.index(row) + 1:] if row else []
    told = re.sub(r"\s+", " ", " ".join([re.sub(r"\s{2,}.*$", "", row.split("build", 1)[1])] + [x.strip("│ ") for x in rest[:6]])).strip()
    if (words + " " + ITEM) not in told:
        bad.append("the tree's build row does not give the whole title: %s" % told[:160])
    if "…" in row or not re.search(r"= \d+$", row):
        bad.append("the tree's build row lost its columns or still clips: %s" % row)
    if max(len(x) for x in tree) > 84:
        bad.append("a wrapped tree line outgrows the fence")
    if words not in re.sub(r"\s+", " ", re.sub(r"[│]", "", "\n".join(x for x in tree if not x.startswith("TOTAL")))) or "GHOST_OF_A_PLACE" not in "".join(x.strip("│ ") for x in tree):
        bad.append("the no-process line does not give the whole title")
    twin = re.sub(r"\s+", "", R.pipeline_text(tp)).split("oldest:")[-1]    # a wrap may fall inside a name: compare without the breaks
    if re.sub(r"\s+", "", words + ITEM) not in twin:
        bad.append("the oldest line clips its title")
    # an old or missing order says so; it never passes off some other order as the next few
    for note, change in (("old", {"t": NOW - R.QUEUE_NEXT_MAX_AGE - 60, "free": ["QUEUED_0_" + LONG], "waiting": []}), ("torn", {"free": []})):
        env, hist = names_env()
        env.files[R.RELENTLESS_STORE + "/queue_next.json"] = change
        p2 = R.build(env, {}, hist)[0]
        q2 = joined(readings_of(panels_of(p2)["Relentless"])["QUEUED"][1])
        if "nextinlineUNMEASURED" not in q2 or "QUEUED_0_" in q2:
            bad.append("%s queue_next.json does not read UNMEASURED: %s" % (note, q2[:80]))
    # an item the tick named that has since moved on is no longer next
    env, hist = names_env()
    env.files[R.RELENTLESS_STORE + "/queue_next.json"]["free"] = ["GONE_ALREADY"] + env.files[R.RELENTLESS_STORE + "/queue_next.json"]["free"]
    if "GONE_ALREADY" in joined(readings_of(panels_of(R.build(env, {}, hist)[0])["Relentless"])["QUEUED"][1]):
        bad.append("queued lists a name that left the queue")
    return bad


def set_aside_problems():
    """The owner's ask 2026-11-04: held and blocked items named in boxes of their own, most expensive first, each with its reason."""
    bad = []
    env, hist = names_env()
    items = [x for x in env.items if x["status"] not in ("held", "blocked")]
    for i in range(12):     # held: spend rises with i; the dearest is the one he could not find
        items.append({"item": "HELD_%02d_%s" % (i, LONG), "status": "held", "spent": 1_000_000 * (i + 1), "returns": 0,
                      "hold": {"at": NOW - 3600 * (i + 1), "kind": "owner_call", "why": "REASON_%02d wants his yes" % i}})
    items.append({"item": "BLOCKED_ON_PRED", "status": "blocked", "spent": 500, "blocked_at": NOW - 7200})
    items.append({"item": "BLOCKED_NO_WHY", "status": "blocked", "spent": 100, "blocked_at": NOW - 60})
    env.items = items
    env.blocks = {"BLOCKED_ON_PRED": ("THE_PREDECESSOR_ITEM", "relentless snag gate_unmet: the remake is not done")}
    page = R.build(env, {}, hist)[0]
    rs = readings_of(panels_of(page)["Relentless"])
    body = lambda label: joined(rs[label][1]) if label in rs else ""  # noqa: E731
    h, b = body("NAMES HELD"), body("NAMES BLOCKED")
    if not h or not b:
        return ["held or blocked has no box of its own: %s" % sorted(rs)]
    at = [h.find("HELD_%02d_%s" % (i, LONG)) for i in (11, 10, 3)]
    if -1 in at or at != sorted(at):
        bad.append("held is not listed most expensive first: %s" % at)
    if "HELD_02_" in h or "+3more" not in h or "HELD:12" not in h:
        bad.append("held does not stop at nine with a count of the rest")
    if "owner_call:REASON_11" not in h or "12h" not in h.replace("12.0h", "12h"):
        bad.append("a held row lacks its reason or its time in state: %s" % h[:200])
    if not {"HELD_11_" + LONG, "BLOCKED_ON_PRED"} <= set(R.row_items(R.gather(env, {}, hist, False))):
        bad.append("held and blocked names do not get a mark (pass count and tokens)")
    if "waitsonTHE_PREDECESSOR_ITEM" not in b or "theremakeisnotdone" not in b:
        bad.append("a blocked row does not say what it waits on and why: %s" % b[:200])
    if "reasonUNMEASURED" not in b or b.find("BLOCKED_ON_PRED") > b.find("BLOCKED_NO_WHY"):
        bad.append("a blocked row with no reason is not marked UNMEASURED, or the blocked order is not by cost")
    envn, histn = fixture_env()
    envn.items = [x for x in envn.items if x["status"] not in ("held", "blocked")]
    rsn = readings_of(panels_of(R.build(envn, {}, histn)[0])["Relentless"])
    if "none" not in joined(rsn["NAMES HELD"][1]) or "HELD:0" not in joined(rsn["NAMES HELD"][1]):
        bad.append("an empty held box does not say none")
    if "HELD and BLOCKED" not in page or "most expensive first" not in page:
        bad.append("How to read does not explain the held and blocked boxes")
    return bad


def page_problems():
    bad = names_problems() + set_aside_problems()
    for extreme in (False, True):
        env, hist = fixture_env(extreme)
        bad += ["%s: %s" % ("extreme" if extreme else "normal", x) for x in panel_problems(R.build(env, {}, hist)[0])]
    return bad


found = page_problems()
for x in found:
    print("  " + x)
check("every instrument on all three panels carries a verdict and a rough normal, tile by tile, in normal and out-of-range states", not found)
_done = readings_of(panels_of(R.build(fixture_env()[0], {}, fixture_env()[1])[0])["Relentless"]).get("DONE")
check("the Done card names its 24 h closes and reopens (RUNNING_BOARD_FIX_DONE_COUNT_LAGS_PASSES)",
      _done is not None and any(re.match(r"24 h: \+\d+ closed, -\d+ reopened$", w) for _, w in _done[1]))
env, hist = fixture_env()
pans = panels_of(R.build(env, {}, hist)[0])
for machine in ("Archmagi", "SteveDesktop"):
    rs = readings_of(pans[machine])
    check("%s's own panel has its Live Testing tiles and its own busy figure" % machine, LIVE_TILES <= set(rs) and "UNMEASURED" not in " ".join(w for _, w in rs["BUSY / IDLE"][1]))
check("closed by a live proof says a verdict and a range on each machine", all(judged(next(w for s, w in readings_of(pans[m])["CLOSED BY LIVE PROOF"][1] if s == "9")) for m in ("Archmagi", "SteveDesktop")))
tiles = readings_of(pans["Relentless"])
for label in ("TOKENS TODAY", "TOKENS PER ITEM CLOSED (TRIAL)", "MODS ACCEPTED, GOAL IS ALL"):
    check("%s has a verdict word and a range of its own" % label, judged(next(w for s, w in tiles[label][1] if s == "9")))
check("hover text sits on the tile it explains", tiles and readings_of(pans["Archmagi"])["CLOSED BY LIVE PROOF"][0].find(SVGNS + "title") is not None)

check("a systemd duration reads whole", (R.systemd_seconds("20min"), R.systemd_seconds("1min 30s"), R.systemd_seconds("1h 5min"), R.systemd_seconds("30s")) == (1200, 90, 3900, 30))
check("infinity is no limit, not a number", R.systemd_seconds("infinity") is None and R.systemd_seconds("") is None)
env, hist = fixture_env()
env.files[STAFFING] = dict(env.files[STAFFING], t=NOW - 86400)
stale_page = R.build(env, {}, hist)[0]
check("yesterday's staffing file is no today's spend", "UNMEASURED" in readings_of(panels_of(stale_page)["Relentless"])["TOKENS TODAY"][1][1][1])
TAILED = "\n".join(json.dumps({"at": iso(NOW - k * 86400), "acts": [{"do": "done", "item": "T"}]}) for k in (1.5, 0.1)) + "\n"


class Tail(Fake):
    def read_tail(self, path, n):
        return self.read_text(path), True


tailed = R.collect_throughput(Tail(files={SHADOW: "", JOURNAL: "x\n" + TAILED}), NOW)
check("the day a cut journal tail starts in is no whole day", sum(tailed["closed_day"].values()) == 1)
check("a cut tail short of 24 h is UNMEASURED, not a short count", R.guarded(R.collect_throughput, Tail(files={SHADOW: "", JOURNAL: "x\n" + json.dumps({"at": iso(NOW - 3600), "acts": []}) + "\n"}), NOW)[1] is not None)
env, hist = fixture_env()
env.items = None
env.files[R.LIVE_RUNS] = json.dumps({"at": iso(NOW - 50), "item": "A", "criterion": "A", "outcome": "PASS"}) + "\n"
unread = R.build(env, {}, hist)[0]
check("an unread queue never reads as nothing waits", "nothing waits" not in unread.split("</svg>")[0] and "verdict UNMEASURED" in unread.split("</svg>")[0])
env, hist = fixture_env()
env.tick_show = lambda: {"ActiveState": "inactive", "TimeoutStartUSec": "10min", "Result": "success", "mono": 10000.0, "InactiveExitTimestampMonotonic": str(int(9000 * 1e6)), "InactiveEnterTimestampMonotonic": str(int(9540 * 1e6))}
slow = R.build(env, {}, hist)[0]
check("a finished tick near its limit reads high", "high, normal under 8 min" in slow)

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

hold = {BRIDGE: "HELD OPERATIONS since 2026-11-03T20:00:00Z\nfor a proof\n"}
check("a live hold reads plainly", "bridge HELD by OPERATIONS" in before_svg(page_of(Fake(files=hold))) and "silent" not in before_svg(page_of(Fake(files=hold))))
old_hold = Fake(files=hold)
old_hold.mtime = lambda path: NOW - R.HOLD_CAP - 60
check("a hold silent past the bridge's own limit says so, on the strip and the panel", "bridge HELD by OPERATIONS, silent" in before_svg(page_of(old_hold)) and "held by OPERATIONS, silent" in page_of(old_hold).split("</svg>")[0])

check("a timer with no next run does not claim to be running", "no next run" in R.timers_rows([{"unit": "rm-x.timer", "last": 0, "next": 0}], [], NOW)[0] and "running now" not in R.timers_rows([{"unit": "rm-x.timer"}], [], NOW)[0])
with tempfile.TemporaryDirectory() as d:
    real_events, R.LEDGER_EVENTS = R.LEDGER_EVENTS, d
    with open(d + "/A.jsonl", "w") as f:
        for state, tsn in (("released", 5), ("taken", 6)):
            f.write(json.dumps({"event": "bridge", "ts": iso(NOW), "tsn": tsn, "state": state}) + "\n")
    tied = R.Env().bridge_events()
    R.LEDGER_EVENTS = real_events
check("a release and a take in one second keep their order", [s for _, s in tied] == ["released", "taken"])

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
    for row in ("<b>closed</b> A</div>", "<b>a Judge failed it</b> I2</div>", "<b>Steve job done</b> FlowWorks guard</div>", "<b>your note</b> X_ITEM: a word from him</div>"):
        if row not in ev:
            bad.append("RECENT EVENTS lacks the row %s" % row)
    live = R.collect_archmagi_live(env, NOW, None, hist)
    if live["proofs"] != [0] * (R.TREND_POINTS - 1) + [5]:
        bad.append("live proofs buckets read %s, not five rows in the last bucket" % live["proofs"])
    if live["bugs"] != 1:
        bad.append("BUGS FOUND counts %s, not the one FAIL of the last 24 h" % live["bugs"])
    try:
        rs = readings_of(panels_of(page)["Relentless"])
        ys = [float(p.split(",")[1]) for p in rs["TREND live proofs"][0].find(SVGNS + "polyline").get("points").split()]
        if not (len(ys) == R.TREND_POINTS and ys[-1] < min(ys[:-1]) and len(set(ys[:-1])) == 1):
            bad.append("the live proofs line does not rise at its last point: %s" % ys)
        if "1" not in [w for _, w in readings_of(panels_of(page)["Archmagi"])["BUGS FOUND"][1]]:
            bad.append("the Archmagi BUGS FOUND tile does not read 1")
    except (KeyError, AttributeError, IndexError, ValueError) as e:
        bad.append("a trend or tile could not be read: %r" % e)
    return bad


found = content_problems()
for x in found:
    print("  " + x)
check("receipt row, feed rows of every kind, the live proofs line and today's bugs are on the page", not found)

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
    ("the belt cards lose oldest", "s.text(x + 10, y0 + 96, note_, 9, col_)\n        elif", "pass\n        elif"),
    ("the side cards lose oldest", "s.text(x + 10, sy + 72, note_, 9, col_)", "pass"),
    ("a stage count loses its verdict", 's.text(x + 10, y0 + 83, verdict, 9, col)', "pass"),
    ("the game idle trend is gone", 'live.get("idle_trend") if live else None, WARN', "None, WARN"),
    ("the trend lines are never drawn", "s.polyline([(lx +", QUIET + "[(lx +"),
    ("a trend's point has no verdict", "s.text(rx + 8, yy + 27, verdict, 9, ncol)", "pass"),
    ("a bar has no verdict", "s.text(350, yy + 11, note, 9, ncol)", "pass"),
    ("closed by live proof is a description again", "cn = versus(c, None, False, closed_rough) if c is not None else (None, DIM)", 'cn = ("closed with a PASS here", DIM)'),
    ("tokens today has no verdict", '("high," if high else "ok,") + verdict.split(",", 1)[1] + " a day"', '"UTC day"'),
    ("tokens per item has no verdict", '"%s; %s/%s: %d closed" % (verdict,', '"%s; %s/%s: %d closed" % ("days seen",'),
    ("mods accepted has no range", '"%s, normal over half; GREEN', '"%s; GREEN'),
    ("the proof rows tile has no verdict", '"%s, %d of %d measured%s; normal over 30%%" % ("low" if low else "ok", measured, total,', '"%s %d of %d measured%s" % ("", measured, total,'),
    ("the Falsified tile is gone", 'tile(s, 864, y, 162, "FALSIFIED EXPECTATIONS",', QUIET + 's, 864, y, 162, "FALSIFIED EXPECTATIONS",'),
    ("Steve loses a machine tile", 'tile_(cols[3][0], y, cols[3][1], "CPU",', QUIET + 'cols[3][0], y, cols[3][1], "CPU",'),
    ("a tile too narrow clips its verdict", 'tile_(102, y, 96, "QUEUED",', 'tile_(102, y, 60, "QUEUED",'),
    ("Steve's how-to-read is gone", 'how_to_read("The second machine', '(lambda t: "")("The second machine'),
    ("a number outside any reading", 's.reading_open("FAIL LOOP")', 's.reading_open("FAIL LOOP"); s.text(0, 0, "42", 12)'),
    ("a name row clips its names again", 'for j, ln in enumerate(wrap_name(e[1] + e[2], width, 2)):', 'for j, ln in enumerate([clip(e[1] + e[2], width)]):'),
    ("the cards stop growing", "ch = max([170] + [112 + entries_height(card_entries(lists, k)) + 6 for k in BELT])", "ch = 170"),
    ("the panel forgets its added height", "W, H = 1040, 610 + (ch - 170) + sum(b[2] + 8 for b in bands)", "W, H = 1040, 610"),
    ("the throughput rows ignore the band", "ty = by + 6 if bands else sy + sh + 18", "ty = sy + sh + 18"),
    ("closing keeps its long list in the card", 'return [k for k in BELT if sum(1 for e in lists[k] if e[0] == "name") > NAMES_IN_CARD]', "return []"),
    ("queued ignores the tick's order", 'free = [i for i in qn["free"] if i in here][:NEXT_SHOWN]', 'free = sorted(here)[:NEXT_SHOWN]'),
    ("queued lists a name that moved on", 'free = [i for i in qn["free"] if i in here][:NEXT_SHOWN]', 'free = qn["free"][:NEXT_SHOWN]'),
    ("queued loses the count of the rest", 'out["queued"].append(("note", "+ %d more" % (len(waiting) - len(free) - len(held))))', "pass"),
    ("done lists everything it knows", "recent = thr[\"recent\"][:LATEST_SHOWN]", "recent = thr[\"recent\"][:1]"),
    ("done loses the count of the rest", 'out["done"].append(("note", "+ %d earlier" % rest))', "pass"),
    ("an old order still reads as the next few", 'if now - q["t"] > QUEUE_NEXT_MAX_AGE:', "if False:"),
    ("the text twin loses the names", "for e in lists[name]:   # whole names, as on the cards, each with its band, passes and tokens", "for e in []:"),
    ("a build row clips its title again", 'cont="│  %s" % (" " if branch == "└─" else "│") + " " * 8)', "cont=None)"),
    ("the no-process line clips its title", 'L.extend(fence_wrap("! %d items hold a place with no process: %s" % (len(ghosts), title(ghosts[0])), "│  ", "│    "))', 'L.append("│  ! %d items hold a place with no process: %s" % (len(ghosts), clip(title(ghosts[0]), W - 45)))'),
    ("the oldest line clips its title", 'out += fence_wrap("%s %s: %s" % (k, ago(o[0]), title(o[1])), "  ", "      ")', 'out.append("  %s %s: %s" % (k, ago(o[0]), clip(title(o[1]), 40)))'),
    ("the page's places words are gone", "A place is one running Builder or Judge", "One running Builder or Judge"),
    ("FINISHED TODAY drops its receipt rows", '"".join(row(r) for r in rows) or "Nothing yet today."', '"Nothing yet today."'),
    ("RECENT EVENTS prints no rows", "for at, word, txt in rows[:18])", "for at, word, txt in rows[:0])"),
    ("the pipeline's acts never reach the feed", "feed.append((at, FEED_WORD[w], x.get(\"item\") or \"\"))", "pass"),
    ("the live proofs line stays flat", "proofs[b] += 1", "pass"),
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
check("fuel: the phone leads with the three accounts", lines.index("ACCOUNTS, THIS WEEK") < lines.index("RELENTLESS PIPELINE") and any(x.startswith("alpha 5% left, resets in") and "AHEAD, out " in x for x in lines) and any(x.startswith("beta 41% left") and "BEHIND, " in x for x in lines) and any(x.startswith("gamma 40% left") and x.endswith("EQUAL") for x in lines))
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
R.OUT_DIR, R.OUT, R.PHONE_OUT, R.STATE = out, out + "/RUNNING_NOW.md", out + "/RUNNING_NOW_PHONE.md", out + "/state.json"
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
for leaf in ("RUNNING_NOW.md", "RUNNING_NOW_PHONE.md"):
    if os.path.exists(out + "/" + leaf):
        with open(out + "/" + leaf) as f:
            disk[leaf] = f.read()
check("fuel real: a real write puts the three readings in RUNNING_NOW.md", wrote.returncode == 0 and all(w in disk.get("RUNNING_NOW.md", "") for w in ("41% left", "AHEAD", "EQUAL", "BEHIND")))
check("fuel real: a real write puts the three rows in RUNNING_NOW_PHONE.md", len(accounts_block(disk.get("RUNNING_NOW_PHONE.md", ""))) == 3)
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

# --- item rows wear their bounces (RUNNING_PAGE_BUILD_ROWS_WEAR_THEIR_BOUNCES): bands, flash, phone emoji ---
import ops_watch as OW  # noqa: E402
BANDS = {"passes": [2, 3], "spent": [3000000, 6000000], "age_s": {"running": [10800, 28800]}, "stuck_silent_s": 3600}
def run_st(**kw):
    st = {"status": "running", "returns": 0, "spent": 100000, "started_at": NOW - 60, "last_beat": NOW - 30}
    st.update(kw)
    return st
def row_svg(m):
    sv = R.Svg(400, 60, "t")
    R.item_row(sv, 20, 20, ("name", "1h ", "SOME_ITEM_NAME_HERE"), R.CARD_CHARS, lambda n: n, {"SOME_ITEM_NAME_HERE": m} if m else None)
    return "".join(sv.parts)

def rows_results():
    """Every row check as (name, held); the mutants below must turn at least one False."""
    out = []
    ok = lambda name, cond: out.append((name, bool(cond)))  # noqa: E731
    m = R.item_mark(run_st(), NOW, BANDS)
    ok("rows: a first pass, small spend, fresh start is cool and does not flash", m["band"] == "cool" and m["passes"] == 1 and not m["flash"] and m["age"] == 60)
    ok("rows: one return (pass 2) is warm, two returns (pass 3) is hot", R.item_mark(run_st(returns=1), NOW, BANDS)["band"] == "warm" and R.item_mark(run_st(returns=2), NOW, BANDS)["band"] == "hot")
    ok("rows: tokens band at the rule's edges (just under warm cool, at warm warm, at hot hot)",
          [R.item_mark(run_st(spent=v), NOW, BANDS)["band"] for v in (2999999, 3000000, 6000000)] == ["cool", "warm", "hot"])
    ok("rows: time in place bands by the stage's own pair", [R.item_mark(run_st(started_at=NOW - a), NOW, BANDS)["band"] for a in (10799, 10800, 28800)] == ["cool", "warm", "hot"])
    ok("rows: the worst of the three sets the band, and says which", R.item_mark(run_st(returns=1, spent=6000000), NOW, BANDS)["why"] == ["passes warm", "tokens hot"])
    u = R.item_mark({"status": "running"}, NOW, BANDS)
    ok("rows: an unread state is UNMEASURED, not cool-by-default zeros", u["passes"] is None and u["spent"] is None and u["age"] is None
          and R.mark_words(u) == "passes UNMEASURED · tokens UNMEASURED · age UNMEASURED" and R.mark_words(None) == "passes, tokens UNMEASURED")
    ok("rows: a row listed without an age (the queue) gets its time in place on the second line", R.mark_words(R.item_mark(run_st(started_at=NOW - 7200), NOW, BANDS), False).startswith(R.ago(7200).replace(" ", "") + " here") and " here" not in R.mark_words(R.item_mark(run_st(), NOW, BANDS)))
    ok("rows: a check that could not read is written on the row", R.mark_words(R.item_mark(run_st(), NOW, BANDS, unread=["churn UNMEASURED (x)"])).endswith("churn UNMEASURED (x)"))
    ok("rows: the second line names pass and tokens in human units", R.mark_words(R.item_mark(run_st(returns=3, spent=1500000), NOW, BANDS)).startswith("pass 4 · 1.5M tok"))
    for kw, word in (({"circling": True}, "CIRCLING"), ({"churn": True}, "CHURN"), ({"ghost": True}, "NO PROCESS")):
        f = R.item_mark(run_st(), NOW, BANDS, **kw)
        ok("rows: %s flashes and forces hot on an otherwise cool row" % word, f["flash"] == [word] and f["band"] == "hot" and word in R.mark_words(f))
    f = R.item_mark(run_st(last_beat=NOW - 3600), NOW, BANDS)
    ok("rows: a running item silent for stuck_silent_s flashes SILENT; one beat short does not",
          f["flash"] and f["flash"][0].startswith("SILENT") and not R.item_mark(run_st(last_beat=NOW - 3599), NOW, BANDS)["flash"])
    ck = run_st(status="checking", last_beat=NOW - 150000, check={"at": NOW - 360})
    ok("rows: a checking item is timed by its Judge's launch, not the builder's old beat (PASS3_FLOOD board)",
       not R.item_mark(ck, NOW, BANDS)["flash"] and R.item_mark(dict(ck, check={"at": NOW - 3600}), NOW, BANDS)["flash"][0].startswith("SILENT"))
    ok("rows: a Judge that wrote its result is no SILENT; unread past stuck_silent_s it is VERDICT UNREAD",
       not R.item_mark(dict(ck, check={"at": NOW - 9000}, _judge_out=NOW - 120), NOW, BANDS)["flash"]
       and R.item_mark(dict(ck, check={"at": NOW - 9000}, _judge_out=NOW - 3600), NOW, BANDS)["flash"][0].startswith("VERDICT UNREAD"))
    ok("rows: a queued item never flashes SILENT (no beat is owed)", not R.item_mark(run_st(status="queued", last_beat=NOW - 99999), NOW, BANDS)["flash"])
    d = R.item_mark(run_st(status="done", returns=5), NOW, BANDS, churn=True, circling=True, ghost=True)
    ok("rows: a done item never flashes, keeps its passes band", d["flash"] == [] and d["band"] == "hot" and d["why"] == ["passes hot"])
    ok("rows: no rule for a value gives it no level (a rules file without item_bands reads cool, never hot)", R.item_mark(run_st(returns=9, spent=9e9), NOW, {})["band"] == "cool")
    # the flash rule reuses ops_watch's churn, not a second definition
    CH = {"churn_window_h": 12, "churn_returns": 3, "churn_same_class": 2}
    ok("rows: in_churn - two fails of one class in the window is churn", OW.in_churn({"returns": 1}, [(NOW - 60, "red"), (NOW - 120, "red")], NOW, CH))
    ok("rows: in_churn - three returns of mixed classes is churn", OW.in_churn({"returns": 3}, [(NOW - 60, "a"), (NOW - 120, "b"), (NOW - 180, "c")], NOW, CH))
    ok("rows: in_churn - old fails outside the window are not churn", not OW.in_churn({"returns": 5}, [(NOW - 13 * 3600, "red"), (NOW - 14 * 3600, "red")], NOW, CH))
    ok("rows: in_churn - one fail, no repeats is not churn", not OW.in_churn({"returns": 1}, [(NOW - 60, "red")], NOW, CH))
    ok("rows: attempt_failed reads an ended, non-ok row and skips starts and kinds",
          OW.attempt_failed({"gen": 2, "end": "red", "at": "2026-11-04T10:00:00Z"}, {"done"})[1] == "red" and OW.attempt_failed({"gen": 2, "start": 1}, set()) is None
          and OW.attempt_failed({"gen": 2, "end": "done"}, {"done"}) is None and OW.attempt_failed({"gen": 2, "end": "x", "kind": "k"}, set()) is None)
    # SMIL only on flash rows, on the stripe and the metric line
    calm, hot = row_svg(R.item_mark(run_st(), NOW, BANDS)), row_svg(R.item_mark(run_st(), NOW, BANDS, churn=True))
    ok("rows: a calm row has no animation, a flash row animates twice (stripe and line)", "<animate" not in calm and hot.count("<animate") == 2 and hot.count(R.FLASH_SMIL) == 2)
    ok("rows: the row's colour is its band (cool blue, hot red), and an unmarked row is faint", R.LIVE in calm and R.BAD in hot and R.FAINT in row_svg(None))
    ok("rows: every row opens one balanced group per close", all(x.count("<g") == x.count("</g>") for x in (calm, hot, row_svg(None))))
    ok("rows: the row is tagged as an item, so page checks keep it apart from instrument notes", 'data-item="SOME_ITEM_NAME_HERE"' in calm)
    # the phone: one emoji per row, no HTML
    saved = R.stage_lists
    R.stage_lists = lambda p: {k: ([("name", "2h ", "ITEM_A"), ("name", "5h ", "ITEM_B")] if k == "running" else [("name", "1d ", "ITEM_C")] if k == "queued" else []) for k in R.BELT}
    pp = {"items": {"x": 1}, "now": NOW, "marks": {"ITEM_A": R.item_mark(run_st(), NOW, BANDS), "ITEM_B": R.item_mark(run_st(), NOW, BANDS, churn=True), "ITEM_C": R.item_mark(run_st(status="queued", returns=1), NOW, BANDS)}}
    ph = R.phone_rows(pp)
    rows = [x for x in ph if x.startswith("- ")]
    ok("rows: phone - one emoji per row: blue calm, siren cycler, amber bounce", [x.split()[1] for x in rows] == [R.BAND_EMOJI["cool"], R.FLASH_EMOJI, R.BAND_EMOJI["warm"]] or
          sorted(x.split()[1] for x in rows) == sorted([R.BAND_EMOJI["cool"], R.FLASH_EMOJI, R.BAND_EMOJI["warm"]]))
    ok("rows: phone - no HTML, the legend leads, a blank line closes the list", not any("<" in x for x in ph) and ph[1].startswith("ITEMS (") and ph[-1] == "")
    pp["marks"], pp["marks_why"] = None, "no store"
    ok("rows: phone - unread marks say UNMEASURED with the reason", R.phone_rows(pp)[1] == "ITEMS: passes, tokens and bands UNMEASURED (no store)")
    R.stage_lists = saved
    return out

ROW_MUTANTS = [
    ("a flash no longer forces hot", '"band": "hot" if flash else ("cool", "warm", "hot")[worst]', '"band": ("cool", "warm", "hot")[worst]'),
    ("a done item flashes", 'if status not in ("done", "retired"):\n        if circling:', 'if True:\n        if circling:'),
    ("passes count returns, not 1 + returns", "passes = int(rets) + 1 if", "passes = int(rets) if"),
    ("a flash row does not animate", 's.parts.append("<g>" + FLASH_SMIL)', 's.parts.append("<g>")'),
    ("the phone shows the band, never the siren", "em = FLASH_EMOJI if m and m[\"flash\"] else", "em = None or"),
    ("an unread pass count prints as a number", 'w = ["pass %d" % m["passes"] if m["passes"] is not None else "passes UNMEASURED",', 'w = ["pass %d" % (m["passes"] or 0),'),
    ("SILENT never fires", 'flash.append("SILENT %s"', 'flash.append and None and flash.append("SILENT %s"'),
]
for name, held in rows_results():
    check(name, held)
row_survivors = []
try:
    for name, old, new in ROW_MUTANTS:
        check("row mutant applies: " + name, old in SRC)
        exec(compile(SRC.replace(old, new, 1), R.__file__, "exec"), R.__dict__)
        try:
            caught = [n for n, held in rows_results() if not held]
        except Exception as e:
            caught = [repr(e)]
        if not caught:
            row_survivors.append(name)
finally:
    exec(compile(SRC, R.__file__, "exec"), R.__dict__)
    R.stage_lists = R.__dict__["stage_lists"]
check("every mutant of the item rows goes red (%d mutants)%s" % (len(ROW_MUTANTS), ": survivors " + "; ".join(row_survivors) if row_survivors else ""), not row_survivors)

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
