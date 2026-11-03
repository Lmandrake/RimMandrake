#!/usr/bin/env python3
"""selftest_running_now.py - running_now.py offline, on fixtures (no systemd, no Windows, no ssh, no state files).

Covers: a source that cannot be read says UNMEASURED and never a 0 count; the tree accounts for every process counted;
an unmatched python process is shown under NOT RECOGNISED with its pid; a Relentless unit finds its item by the hash;
a place held with no process is called out; idle under a brake is the first, red thing on the page; the 24 h counters
count a verdict once; the page is on disk before ssh is tried and a dead ssh changes nothing but the route dots; the
write is atomic, a failed build keeps the old page and the next good page carries a STALE banner; no blank line sits
inside the details block (Typora would end the block there and spill the rest).
"""
import json
import os
import re
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
        self.calls = []
        self.out = None

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
        self.calls.append(("ssh", os.path.exists(R.OUT)))
        if "ssh" in self.fail:
            raise R.Unmeasured("ssh exited 255: no route")
        return "up=100.0\nload=0.5\ncores=18\nstat=cpu 10 0 10 80 0 0 0 0 0 0\nram=1000 64000\ndisk=900 1000\ngame=0\n"

    def tailscale_status(self):
        raise R.Unmeasured("no tailscale in a selftest")

    def port_open(self, host, port=22):
        return "ssh" not in self.fail


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

# 3. a worker finds its item by the unit's hash, and shows it in plain words with its children
check("worker row carries the item's plain words", "Graffiti v1 live proof 1" in text and "item UNMEASURED" not in text)
check("worker row sums its child processes", re.search(r"claude 1 .*= 3", text) is not None)
check("heading counts a work unit as a worker", "workers 1, checkers 0" in text)

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
check("ghosts are unknown, not none, when the tree is unread", not R.ghost_places(R.gather(Fake(fail=("ps",), items=[{"item": ITEM, "status": "checking"}]), {})))
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
check("trouble comes first in the strip", head.index("Steve BRAKED") < head.index("Relentless") if "Relentless" in head else True)
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

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
