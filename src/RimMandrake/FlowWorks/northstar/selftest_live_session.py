"""Offline selftest of live_session.py: the shared-clock scheduler, the zone plan, the verdict folding, and that --dry-run
and --mock both exit 0.  python3 src/RimMandrake/FlowWorks/northstar/selftest_live_session.py"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_session as L  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Clock(object):
    def __init__(self, stall_after=None):
        self.t, self.steps, self.stall_after = 0, [], stall_after

    def advance(self, n):
        self.steps.append(n)
        if self.stall_after is None or self.t < self.stall_after:
            self.t += n

    def now(self):
        return self.t


def waiter(n, log, name):
    yield L.Wait(n)
    log.append((name, "woke")),


def poller(clock, at, log):
    w = L.Wait(5000, until=lambda: clock.t >= at, every=100)
    yield w
    log.append(("poll", clock.t, w.timed_out))


def crasher():
    yield L.Wait(10)
    raise RuntimeError("boom")


# 1. three blocks each waiting 1,500 ticks cost 1,500 ticks, not 4,500 (the compression the session is built on)
c, log = Clock(), []
res, spent = L.run_shared({k: waiter(1500, log, k) for k in ("a", "b", "c")}, c.advance, c.now, log=lambda s: None)
check(spent == 1500 and all(v == "done" for v in res.values()), "parallel waits share one clock (%d ticks)" % spent)

# 2. a poll wakes as soon as its condition holds (within one poll period), and does not time out
c, log = Clock(), []
res, spent = L.run_shared({"p": poller(c, 730, log)}, c.advance, c.now, log=lambda s: None)
check(log and 730 <= log[0][1] <= 830 and log[0][2] is False, "until-poll wakes near its condition: %s" % log)

# 3. a poll whose condition never holds times out at its budget and says so
c, log = Clock(), []
res, spent = L.run_shared({"p": poller(c, 10 ** 9, log)}, c.advance, c.now, log=lambda s: None)
check(log and log[0][2] is True and spent == 5000, "never-true poll times out at 5000: %s spent %d" % (log, spent))

# 4. one crashing block never stops the others
c, log = Clock(), []
res, spent = L.run_shared({"x": crasher(), "a": waiter(300, log, "a")}, c.advance, c.now, log=lambda s: None)
check(res["x"].startswith("crashed") and res["a"] == "done", "a crash is isolated: %s" % res)

# 5. a clock that stops moving (live day 4: 0-tick steps) voids every waiting block instead of spinning
c, log = Clock(stall_after=0), []
res, spent = L.run_shared({"a": waiter(1000, log, "a")}, c.advance, c.now, log=lambda s: None)
check(res["a"].startswith("clock stalled"), "a stalled clock is reported: %s" % res)

# 5b. a block that FINISHES early never shrinks the later steps to 1 tick (live 2026-10-19: a finished block's stale
#     deadline left in `due` made B4 crawl one tick per call)
c, log = Clock(), []
res, spent = L.run_shared({"short": waiter(10, log, "s"), "long": waiter(3000, log, "l")}, c.advance, c.now, log=lambda s: None)
check(spent == 3000 and len(c.steps) <= 4, "a finished block leaves big steps: %d steps %s" % (len(c.steps), c.steps[:6]))

# 6. the zone plan: shared zones disjoint from each other and from the owner zone, all inside the map margins
z = L.plan_zones((250, 250))
shared = [z[n] for n in L.SHARED]
ok = all(not L.overlaps(a, b, 2) for i, a in enumerate(shared) for b in shared[i + 1:])
ok = ok and all(not L.overlaps(a, z["owner"], 2) for a in shared)
inside = all(r[0] >= 15 and r[1] >= 15 and r[0] + r[2] <= 235 and r[1] + r[3] <= 235 for n, r in z.items() if n != "readout")
check(ok and inside, "zones disjoint and inside the 15-cell margin (readout excepted: edge-flush by design)")
rx, rz, rw, rh = z["readout"]
check(rx + rw == 250 and rz >= 15 and not L.overlaps(z["readout"], z["owner"], 2),
      "B2 sea: the readout zone is flush with the east map edge, clear of the 216-wide owner zone: %s" % (z["readout"],))
try:
    L.plan_zones((150, 150))
    check(False, "a too-small map refuses the plan")
except ValueError:
    check(True, "a too-small map refuses the plan")

# 7. verdict folding: any FAIL fails; all PASS passes; PASS + UNMEASURED is partial; OWED/SKIP give nothing
rows = [dict(id="r1", item="I", criterion="A1", status="PASS", cls="MOD"),
        dict(id="r2", item="I", criterion="A1", status="UNMEASURED", cls="HARNESS"),
        dict(id="r3", item="J", criterion="A2", status="PASS", cls="MOD"),
        dict(id="r4", item="J", criterion="A2", status="FAIL", cls="MOD"),
        dict(id="r5", item="K", criterion="A3", status="UNMEASURED", cls="OWED"),
        dict(id="r6", item="M", criterion="A4", status="PASS", cls="MOD")]
v = L.verdicts(rows)
check(v.get(("I", "A1"), ("",))[0] == "partial" and v.get(("J", "A2"), ("",))[0] == "fail"
      and ("K", "A3") not in v and v.get(("M", "A4"), ("",))[0] == "pass", "verdict folding: %s" % v)

# 8. every catalog row names a block the driver knows (or an explicit out-of-load bucket)
known = {b["id"] for b in L.BLOCKS} | {"OUT", "LATER", "P10"}
check(all(c["block"] in known for c in L.C), "catalog blocks are all known")

# 8b. PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON: the cover rows judge "gave way" by the COVER, never by ProofClimb's depth.
#     ProofClimb's depth is the cell's dug depth (RM_PocketGrid.ProofPocket -> ClimbDepthAt), deck-blind: a colonist
#     standing on an INTACT cover over a 2 m cell reads depth 4 (live 2026-10-19 run 20261018T233414: 120/220 kg covers
#     "gave way" under one ~60 kg colonist). The fake game below collapses a deck exactly when its load reaches the rating
#     and always reports depth 4 on a dug cell, as the live proof does.
class FakeCoverGame(object):
    def __init__(self, mass=60.9, depth_blind=True):
        self.covers, self.ratings, self.pawns, self.mass, self.depth_blind = {}, {}, {}, mass, depth_blind
        self.dug, self.rows = set(), []

    def call(self, tool, **kw):
        if tool == "jawa/build_batch":
            for op in kw["ops"].split(";"):
                d, xz = op.split(":")
                x, z = (int(v) for v in xz.split(","))
                self.covers[(x, z)] = d
            return dict(success=True)
        if tool == "jawa/list_things":
            x, z, w, h = (int(v) for v in kw["rect"].split(","))
            got = [dict(defName=d, x=c[0], z=c[1]) for c, d in self.covers.items() if x <= c[0] < x + w and z <= c[1] < z + h]
            return dict(things=got, countMatched=len(got), countReturned=len(got))
        if tool == "jawa/pawn_stats":
            return dict(stats=[dict(stat="Mass", value=self.mass)])
        return dict(success=True)

    def settle(self, ratings):
        """The mod's rule, per 4-way deck: gives way (whole deck destroyed) once the summed mass reaches the rating."""
        seen = set()
        for c in list(self.covers):
            if c in seen or c not in self.covers:
                continue
            deck, todo = [], [c]
            while todo:
                q = todo.pop()
                if q in seen or q not in self.covers:
                    continue
                seen.add(q)
                deck.append(q)
                todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
            load = sum(self.mass for p in self.pawns.values() if p in deck)
            if load >= min(ratings[self.covers[q]] for q in deck):
                for q in deck:
                    del self.covers[q]


class FakeCoverSession(object):
    mock = False

    def __init__(self, g):
        self.g, self.w = g, g
        self.zones = dict(covers=(15, 15, 26, 10))
        self.rows = g.rows

    def call(self, tool, **kw):
        return self.g.call(tool, **kw)

    def dig(self, c, n, fill=-1):
        self.g.dug.add(tuple(c))

    def spawn(self, kind, c, faction="player"):
        pid = len(self.g.pawns) + 1
        self.g.pawns[pid] = tuple(c)
        return pid

    def climb(self, pid):
        c = self.g.pawns[pid]
        under = c not in self.g.covers
        return dict(cell=c, depth=4.0 if (c in self.g.dug and (self.g.depth_blind or under)) else 0.0)

    def row(self, rid, item, cid, status, cls, detail, block, eyes=False):
        self.rows.append(dict(id=rid, status=status, cls=cls, detail=detail))


def run_cover_rows(mass, depth_blind=True):
    g = FakeCoverGame(mass, depth_blind)
    s = FakeCoverSession(g)
    ratings = {"RM_PitCover_WovenScrap": 40.0, "RM_PitCover_PlankLattice": 120.0, "RM_PitCover_ReinforcedFrame": 220.0}
    for _w in L.g_cover_tiers(s):
        g.settle(ratings)
    return {r["id"]: r["status"] for r in g.rows}


got = run_cover_rows(60.9)
check(got.get("B4_cover_120") == "PASS" and got.get("B4_cover_220") == "PASS" and got.get("B4_cover_40") == "PASS",
      "a 60.9 kg colonist on an intact 120/220 kg cover (ProofClimb depth 4, deck-blind) is not 'gave way': %s" % got)
got = run_cover_rows(60.9, depth_blind=False)
check(all(v == "PASS" for v in got.values()) and len(got) == 3, "the same rows pass with a deck-aware depth read: %s" % got)


class EarlyCollapseGame(FakeCoverGame):
    def settle(self, ratings):          # can-fail: a mod that drops ANY load (the defect the row exists to catch)
        if self.pawns:
            for c in [c for c in self.covers if c in self.pawns.values()]:
                d = self.covers[c]
                for q in [q for q in self.covers if self.covers[q] == d]:
                    del self.covers[q]


g = EarlyCollapseGame(60.9)
s = FakeCoverSession(g)
for _w in L.g_cover_tiers(s):
    g.settle(None)
got = {r["id"]: r["status"] for r in g.rows}
check(got.get("B4_cover_120") == "FAIL" and got.get("B4_cover_220") == "FAIL",
      "can-fail: a cover that really gives way under 60.9 kg still reads FAIL: %s" % got)


class BlindListGame(FakeCoverGame):
    def call(self, tool, **kw):         # list_things answers nothing at all after the build: the read is blind
        if tool == "jawa/list_things" and self.pawns:
            return {}
        return FakeCoverGame.call(self, tool, **kw)


g = BlindListGame(60.9)
s = FakeCoverSession(g)
for _w in L.g_cover_tiers(s):
    pass
got = {r["id"]: r["status"] for r in g.rows}
check(all(v == "UNMEASURED" for v in got.values()) and len(got) == 3, "a blind cover read is UNMEASURED, never 'gave way': %s" % got)

# 8c. HARNESS_ROWS (2026-10-19): B2 sea, B5 ice, B6 flood verdicts can go red, and say UNMEASURED when they could not ask
OPEN = dict(kind="limitless", text="Open water: never runs dry")
LIM = dict(kind="water", text="Hole 2 m, water 2 m (3,000 L)")
check(L.sea_verdict(OPEN, True, "True")[0] == "PASS", "sea: an edge lake reading limitless is PASS")
check(L.sea_verdict(LIM, True, "True")[:2] == ("FAIL", "MOD"), "can-fail sea: an edge lake reading limited is FAIL/MOD")
check(L.sea_verdict(LIM, False, "True")[:2] == ("UNMEASURED", "SITE"), "sea: paint short of the edge is UNMEASURED/SITE")
check(L.sea_verdict(LIM, True, "False")[:2] == ("UNMEASURED", "SITE"), "sea: sticky-limitless off is UNMEASURED/SITE")
check(L.sea_verdict(None, True, "True")[0] == "UNMEASURED", "sea: an unread lake is UNMEASURED")

warm = [1.4] * 24                     # pass 1: ColdSnap alone bottomed out at 1.4 C
cold = [-2.0, -6.0, -12.0] + [-17.0] * 32       # 16k ticks at -17 C, 56 squares
check(L.ice_verdict(True, warm, None, None, True, 56)[:2] == ("UNMEASURED", "SITE"), "ice: never below -7 C is UNMEASURED/SITE (pass 1)")
check(L.ice_verdict(True, warm, 500, 500, True, 56)[:2] == ("UNMEASURED", "SITE"), "ice: ice above -7 C is still not judged")
check(L.ice_verdict(True, cold, None, None, True, 56)[:2] == ("FAIL", "MOD"),
      "can-fail ice: cold for 16k ticks (%.1f freezes expected) and no ice is FAIL/MOD" % L.freeze_expectation(cold, 56, 500))
check(L.ice_verdict(True, [-8.0, -8.0], None, None, True, 56)[:2] == ("UNMEASURED", "SITE"), "ice: barely cold, briefly, is too short to judge")
check(L.ice_verdict(True, cold, 6000, 3000, True, 56)[0] == "PASS", "ice: froze below -7 C and thawed intact is PASS")
check(L.ice_verdict(True, cold, 6000, None, True, 56)[:2] == ("FAIL", "MOD"), "can-fail ice: never thawed is FAIL")
check(L.ice_verdict(True, cold, 6000, 3000, False, 56)[:2] == ("FAIL", "MOD"), "can-fail ice: litres changed is FAIL")
check(L.ice_verdict(False, cold, 6000, 3000, True, 56)[0] == "UNMEASURED", "ice: conditions refused is UNMEASURED")
check(L.ice_verdict(True, [None, None], None, None, True, 56)[:2] == ("UNMEASURED", "HARNESS"), "ice: no temperature read is UNMEASURED/HARNESS")

check(L.flood_verdict(True, True, True, True)[0] == "PASS", "flood: reached, receded, canal intact is PASS")
check(L.flood_verdict(True, True, True, False)[:2] == ("FAIL", "MOD"), "can-fail flood: a canal changed by the flood is FAIL/MOD")
check(L.flood_verdict(True, False, False, True)[:2] == ("UNMEASURED", "SITE"), "flood: never reached the canal is UNMEASURED/SITE")
check(L.flood_verdict(True, True, False, True)[:2] == ("UNMEASURED", "SITE"), "flood: not receded is UNMEASURED/SITE")
check(L.flood_verdict(False, False, False, True)[0] == "UNMEASURED", "flood: weather refused is UNMEASURED")


class FakeEventGame(object):
    """B5/B6 wiring: a clock, a temperature that follows the cold conditions, ice/flood terrain on cue, readouts."""
    def __init__(self, base=21.0, offset=-20.0, freezes=True, floods=True, flood_changes=False):
        self.t, self.base, self.offset, self.freezes, self.floods, self.flood_changes = 0, base, offset, freezes, floods, flood_changes
        self.conds, self.weather, self.ice, self.flood, self.flood_end = set(), "Clear", False, False, None
        self.rows = []

    def temp(self):
        return self.base + self.offset * len(self.conds) * min(1.0, self.t / 12000.0)

    def tick(self, n):
        for _ in range(int(n) // 100):
            self.t += 100
            if self.freezes and self.temp() <= -7:
                self.ice = True
            if self.ice and self.temp() >= 2 and not self.conds:
                self.ice = False
            if self.floods and self.weather == "TorrentialRain" and self.t > self.flood_start + 4000:
                self.flood = True
            if self.flood_end is not None and self.t > self.flood_end:
                self.flood = False

    def call(self, tool, **kw):
        if tool == "jawa/game_condition":
            (self.conds.add if kw["action"] == "start" else self.conds.discard)(kw["condition"])
            return dict(success=True)
        if tool == "jawa/cell_temperature":
            return dict(success=True, temperature=self.temp())
        if tool == "jawa/get_terrain_batch":
            return dict(ops=("ThinIce:1,1,1,1;" if self.ice else "") + ("ShallowFloodwater:1,1,1,1" if self.flood else "Soil"))
        if tool == "jawa/weather_set":
            if kw.get("weather") == "TorrentialRain":
                self.weather, self.flood_start = "TorrentialRain", self.t
            else:
                self.weather = kw.get("weather") or self.weather
                if self.flood:
                    self.flood_end = self.t + 2500
            return dict(success=True, after=self.weather)
        if tool == "jawa/weather_get":
            return dict(success=True, weather=self.weather)
        return dict(success=True)


class FakeEventWalk(object):
    def __init__(self, g):
        self.g = g

    def clear_site(self, rect):
        return True

    def readout(self, c):
        return dict(kind="water", dl=1000)

    def cells(self, cells):
        return ({tuple(c): (2, 2 if (self.g.flood_changes and self.g.t > 5000) else 1, 1000) for c in cells}, 0)


class FakeEventSession(object):
    mock = False

    def __init__(self, g):
        self.g, self.w, self.rows = g, FakeEventWalk(g), g.rows
        self.zones, self.size = L.plan_zones((250, 250)), (250, 250)

    def call(self, tool, **kw):
        return self.g.call(tool, **kw)

    def advance(self, n):
        self.g.tick(n)

    def dig(self, c, n, fill=-1):
        return {}

    def row(self, rid, item, cid, status, cls, detail, block, eyes=False):
        self.rows.append(dict(id=rid, status=status, cls=cls, detail=detail))


def run_event(fn, **kw):
    g = FakeEventGame(**kw)
    fn(FakeEventSession(g))
    return g.rows[-1]


r = run_event(L.b5_cold_snap, offset=-10.0)     # ColdSnap-strength alone: 21 - 2 x 10 = 1 C, the pass-1 bottom
check(r["status"] == "UNMEASURED" and r["cls"] == "SITE", "B5 wired: a canal that stays above -7 C is UNMEASURED/SITE: %s" % r["detail"].get("why"))
r = run_event(L.b5_cold_snap)
check(r["status"] == "PASS", "B5 wired: ColdSnap + DeepFreeze reach -7 C, ice forms and thaws: PASS (%s)" % r["detail"].get("why"))
r = run_event(L.b5_cold_snap, freezes=False)
check(r["status"] == "FAIL" and r["cls"] == "MOD", "can-fail B5 wired: cold enough and dug water never ices is FAIL/MOD: %s" % r["detail"].get("why"))
r = run_event(L.b6_flood)
check(r["status"] == "PASS", "B6 wired: torrential flood reaches the canal banks, recedes, canal intact: PASS (%s)" % r["detail"].get("why"))
r = run_event(L.b6_flood, floods=False)
check(r["status"] == "UNMEASURED" and r["cls"] == "SITE", "B6 wired: a flood that never reaches the canal is UNMEASURED/SITE")
r = run_event(L.b6_flood, flood_changes=True)
check(r["status"] == "FAIL" and r["cls"] == "MOD", "can-fail B6 wired: the flood changed the canal's fill: FAIL/MOD")

# 9. --dry-run and --mock exit 0 offline
for flag in ("--dry-run", "--mock"):
    d = tempfile.mkdtemp(prefix="ls_selftest_")
    r = subprocess.run([sys.executable, os.path.join(HERE, "live_session.py"), flag, "--no-owner-save", "--out-dir", d],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
    check(r.returncode == 0 and "Traceback" not in r.stdout, "%s exits 0 with no traceback" % flag)

print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
