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
        if tool == "jawa/set_draft":            # the real tool reads Drafted back; no `drafted` leaves it unchanged (false)
            return dict(success=True, drafted=kw.get("drafted") is True)
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


# 8b'. PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON (live rerun 20261019T010244: 120 "held" 121.0 kg, 220 "held" 244.3 kg): the
#      row called jawa/set_draft with no `drafted`, which leaves the draft UNCHANGED, so each spawned colonist was undrafted
#      and wandered off the deck between reads (trail depths 4 -> 0 while covers_left stayed 6). Undrafted pawns here walk
#      off on every settle; a drafted one stays. The row must draft (and read the draft back), and a pawn found OFF the
#      deck at read time makes the row UNMEASURED, never "held".
class WanderGame(FakeCoverGame):
    def __init__(self, mass=60.9, draft_works=True):
        FakeCoverGame.__init__(self, mass)
        self.drafted, self.draft_works = set(), draft_works

    def call(self, tool, **kw):
        if tool == "jawa/set_draft":
            pid = kw.get("pawnId")
            if kw.get("drafted") is True and self.draft_works:
                self.drafted.add(pid)
            return dict(success=True, drafted=pid in self.drafted)
        return FakeCoverGame.call(self, tool, **kw)

    def settle(self, ratings):
        for pid, c in list(self.pawns.items()):
            if pid not in self.drafted:
                self.pawns[pid] = (c[0], c[1] + 2)      # wandered off the deck
        FakeCoverGame.settle(self, ratings)


def run_wander(mass, draft_works=True):
    g = WanderGame(mass, draft_works)
    s = FakeCoverSession(g)
    ratings = {"RM_PitCover_WovenScrap": 40.0, "RM_PitCover_PlankLattice": 120.0, "RM_PitCover_ReinforcedFrame": 220.0}
    for _w in L.g_cover_tiers(s):
        g.settle(ratings)
    return {r["id"]: r["status"] for r in g.rows}, g


got, g = run_wander(60.5)
check(got.get("B4_cover_120") == "PASS" and got.get("B4_cover_220") == "PASS",
      "2 x 60.5 kg give way on 120 and 4 x 60.5 on 220 when the colonists are DRAFTED onto the deck: %s" % got)
got, g = run_wander(61.0)
check(got.get("B4_cover_220") == "PASS", "4 x 61 kg give way on 220: %s" % got)
got, g = run_wander(60.7)
check(got.get("B4_cover_40") == "PASS" and got.get("B4_cover_120") == "PASS", "1 x 60.7 kg holds on 120 then 2 drop it: %s" % got)
got, g = run_wander(60.5, draft_works=False)
check(got.get("B4_cover_120") == "UNMEASURED" and got.get("B4_cover_220") == "UNMEASURED",
      "a colonist that is not drafted (left the deck) makes the row UNMEASURED, never 'held': %s" % got)

# 8c. HARNESS_ROWS (2026-10-19): B2 sea, B5 ice, B6 flood verdicts can go red, and say UNMEASURED when they could not ask
OPEN = dict(kind="limitless", text="Endless (about 2 m deep)")
OLDW = dict(kind="limitless", text="Open water, never runs dry", old_wording=True)
LIM = dict(kind="water", text="Hole 2 m, water 2 m (3,000 L)")
check(L.sea_verdict(OPEN, True, "True")[0] == "PASS", "sea: an edge lake reading Endless is PASS")
check(L.sea_verdict(OLDW, True, "True")[:2] == ("FAIL", "MOD"), "can-fail sea: the retired 'Open water' wording is FAIL (bar says Endless)")
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
check(L.ice_verdict(True, cold, 6000, None, True, 56, melt_exp=2.2)[:2] == ("UNMEASURED", "SITE"),
      "ice: no melt with only 2.2 melts expected (pass 3, 12k ticks at 26 C) is too short, not FAIL")
check(L.ice_verdict(True, cold, 6000, None, True, 56, melt_exp=5.0)[:2] == ("FAIL", "MOD"), "can-fail ice: warm enough, no melt is FAIL")
check(L.ice_cells("RM_WaterThin:16,50,7,1;ThinIce:23,50,2,1;ThinIce:23,54,3,1") == {(23, 50), (24, 50), (23, 54), (24, 54), (25, 54)},
      "ice_cells parses ThinIce runs")
check(abs(L.melt_expectation_step(26.0, 50, 500) - 500 * 50 / 1667.0 * 0.001 * 6.2) < 1e-9 and L.melt_expectation_step(1.0, 50, 500) == 0,
      "melt expectation: vanilla 0.001*(T+5)/5 per visit, none below 2 C")
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


class FakeV(object):
    def __init__(self, ready=True):
        self.ready = ready

    def prepare_site(self, B, rect, rows, rid):
        if not self.ready:
            rows.append(dict(id=rid, status="UNMEASURED", cls="SITE", detail=dict(blocked=["roof still present over the site"])))
        return self.ready


class FakeEventWalk(object):
    def __init__(self, g):
        self.g, self.V, self.B, self.reset_left = g, FakeV(getattr(g, "site_ready", True)), g, 0

    def proof(self, typ, method, arg):
        return True, "RESET cells=0 levels=0 rolled=0 left=%d" % self.reset_left

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
        self.site_bad, self.pawns, self.timing, self.notes = {}, {}, {}, []

    def call(self, tool, **kw):
        return self.g.call(tool, **kw)

    def advance(self, n):
        self.g.tick(n)

    def dig(self, c, n, fill=-1):
        return {}

    row = L.Session.row          # the REAL row(): its zone demotion is what the site checks below exercise

    def sget(self, f):           # B6 turns rain fill off for the flood row and restores it
        return getattr(self, "_settings", {}).get(f, True)

    def sset(self, f, v):
        self.__dict__.setdefault("_settings", {})[f] = v

    def say(self, s):
        pass

    def save(self):
        pass


def run_event(fn, site_ready=True, **kw):
    g = FakeEventGame(**kw)
    g.site_ready = site_ready
    s = FakeEventSession(g)
    fn(s)
    g.session = s
    return [r for r in g.rows if r["id"].startswith(("B5", "B6"))][-1]


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

# 8c'. B6 rain tail (20261022T235239: 8 canal squares +1 level across the flood): RainRate lerps out for a while after Clear
#      is set; rain fill switched back on at that moment filled the canal during the recession. The fake rains for 3,000
#      ticks after Clear and fills the canal whenever rain fill is on while it still rains.
class RainTailGame(FakeEventGame):
    def __init__(self, **kw):
        FakeEventGame.__init__(self, **kw)
        self.clear_at, self.rain_filled, self.session = None, False, None

    def rain(self):
        if self.weather == "TorrentialRain":
            return 1.0
        return 0.5 if self.clear_at is not None and self.t < self.clear_at + 3000 else 0.0

    def tick(self, n):
        FakeEventGame.tick(self, n)
        fill_on = (getattr(self.session, "_settings", {}) or {}).get("rainFillsExcavationsEnabled", True)
        if self.rain() > 0.01 and fill_on is not False and str(fill_on).lower() != "false":
            self.rain_filled = True

    def call(self, tool, **kw):
        if tool == "jawa/weather_set" and kw.get("weather") == "Clear" and self.weather == "TorrentialRain":
            self.clear_at = self.t
        if tool == "jawa/weather_get":
            return dict(success=True, weather=dict(current=self.weather, rainRate=self.rain()))
        return FakeEventGame.call(self, tool, **kw)


class RainTailWalk(FakeEventWalk):
    def cells(self, cells):
        return ({tuple(c): (2, 2 if self.g.rain_filled else 1, 1000) for c in cells}, 0)


g = RainTailGame()
s = FakeEventSession(g)
s.w = RainTailWalk(g)
g.session = s
s._settings = {"rainFillsExcavationsEnabled": True}
g.rain_filled = False
L.b6_flood(s)
r = [x for x in g.rows if x["id"] == "B6_flood_canal_kept"][-1]
check(r["status"] == "PASS" and s._settings.get("rainFillsExcavationsEnabled") is True,
      "can-fail B6: rain fill stays off through the fading rain after Clear and is restored after (%s, %s)"
      % (r["status"], r["detail"].get("rainRateAtRestore")))

# 8d. LS_FULLREAD (2026-10-19 full read): each harness fix below can go red
check(L.advance_remainder(dict(success=True, executed=500), 500) == 0, "advance: a finished safe_advance owes nothing")
check(L.advance_remainder(dict(success=False, state="stopped", executed=200), 500) == 300,
      "can-fail advance: a latch-stopped run owes only the REST (the old fallback re-advanced all 500)")
check(L.advance_remainder(dict(success=False, state="refused"), 500) == 500, "advance: a refused run owes all of it")
check(L.dig_miss(dict(success=True, depth=4), 4) is None, "dig: depth read back as asked is fine")
check(L.dig_miss(dict(success=True, depth=8), 4) and L.dig_miss(dict(success=False, error="x"), 4),
      "can-fail dig: a doubled depth (cell never reset) or a refused drive is reported")
check(L.dig_miss(dict(success=True), 4) is None, "dig: a reply with no depth field is not judged (FakeGame)")

r = run_event(L.b5_cold_snap, site_ready=False)
check(r["status"] == "UNMEASURED" and r["cls"] == "SITE" and r["detail"].get("statusIfSiteReady") == "PASS",
      "can-fail site: B5 on an ice zone that never read back clear is UNMEASURED/SITE, not PASS: %s" % r["status"])
g = FakeEventGame()
s = FakeEventSession(g)
s.w.reset_left = 3
L.b6_flood(s)
r = [x for x in g.rows if x["id"] == "B6_flood_canal_kept"][-1]
check(r["status"] == "UNMEASURED" and r["cls"] == "SITE", "can-fail site: old pits left by ProofResetRect (left=3) void B6")


class CrashGame(FakeEventGame):
    def __init__(self, *a, **kw):
        FakeEventGame.__init__(self, *a, **kw)
        self.started = set()

    def call(self, tool, **kw):
        if tool == "jawa/game_condition" and kw.get("action") == "start":
            self.started.add(kw["condition"])
        if tool == "jawa/cell_temperature":
            raise RuntimeError("bridge dropped")
        return FakeEventGame.call(self, tool, **kw)


g = CrashGame()
raised = False
try:
    L.b5_cold_snap(FakeEventSession(g))
except RuntimeError:
    raised = True
# the crash must have happened WITH the cold running, or "nothing left" proves nothing
check(raised and g.started and not g.conds,
      "can-fail B5: a crash mid-cold still ends ColdSnap + DeepFreeze (raised %s, started %s, left %s)"
      % (raised, sorted(g.started), sorted(g.conds)))
g = FakeEventGame()
L.b5_cold_snap(FakeEventSession(g))
check(g.weather == "Clear", "B5 ends with B0's locked Clear put back")

hp = L.heal_plan([dict(def_="x"), dict(**{"def": "Hypothermia", "part": None, "severity": 0.4}),
                  dict(**{"def": "Frostbite", "part": "Toe", "severity": 0.2})])
check(("remove", "Hypothermia") in hp and ("restore", "Torso") in hp, "heal: hypothermia removed, frostbite restored via Torso: %s" % hp)
check(L.heal_plan([dict(**{"def": "Hangover", "part": None})]) == [], "heal: nothing to heal is no call")


class HealGame(object):
    def __init__(self):
        self.calls, self.rows = [], []

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "rimworld/list_colonists":
            return dict(colonists=[dict(pawnId="Thing_Human1"), dict(pawnId="Thing_Human2")])
        if tool == "jawa/pawn_get":
            return dict(pawns=[dict(hediffs=[{"def": "Hypothermia", "part": None}, {"def": "Cut", "part": "Leg"}])])
        if tool == "jawa/pawn_health":     # the real tool: restore without bodyPart is REFUSED
            if kw.get("action") == "restore" and not kw.get("bodyPart"):
                return dict(success=False, error="Give a bodyPart to restore.")
            return dict(success=True)
        return dict(success=True)


hg = HealGame()
hs = FakeEventSession(hg)
healed, refused = L.heal_colonists(hs, keep=("Human2",))
check(healed == 1 and not refused and not any(kw.get("pawn") == "Thing_Human2" for t, kw in hg.calls if t == "jawa/pawn_health"),
      "can-fail heal: every heal call is one the tool accepts, and the kept (rescue) pawn is left alone: %s %s" % (healed, refused))

check(L.dig_cost_verdict("True", True, "51200")[0] == "PASS", "dig cost: 3,200 x 16 is PASS")
check(L.dig_cost_verdict("True", True, "12800")[0] == "FAIL", "can-fail dig cost: a flat 12,800 with the curve on is FAIL")
check(L.dig_cost_verdict("False", True, "12800")[0] == "UNMEASURED", "dig cost: curve setting off is UNMEASURED")
check(L.dig_cost_verdict("True", False, "REFUSED: x")[0] == "UNMEASURED", "dig cost: an unread work function is UNMEASURED")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=True, size=100)))[0] == "PASS", "fish: a body with fish PASS")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=False, size=200)))[:2] == ("FAIL", "MOD"),
      "can-fail fish: a 200-square dug body with no fish is FAIL/MOD (the game's chance is 1.0 there)")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=False, size=100)))[:2] == ("UNMEASURED", "SITE"),
      "fish: a 100-square fishless body lost a 52.5% roll (pass 2 PASS, pass 2c FAIL, same build): SITE, not a MOD fail")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=False)))[:2] == ("UNMEASURED", "SITE"),
      "fish: a fishless body of unread size is not a MOD fail")
check(L.FOOT["reservoir"][1] >= 2 + 20, "fish: the reservoir footprint holds the 10x20 (200-square) dig")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=False)))[:2] == ("UNMEASURED", "SITE"), "fish: no body is SITE")
check(L.fish_roll_verdict(dict(success=False))[:2] == ("UNMEASURED", "HARNESS"), "fish: a failed read is HARNESS")
# 20261022T235239: a 200-square fishless body on RM_TheRot (no fishTypes) read FAIL/MOD; the biome cannot roll fish
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=False, size=200)), False)[:2] == ("UNMEASURED", "SITE"),
      "fish: a fishless biome (no fishTypes) is SITE, never a mend FAIL")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=False, size=200)), None)[:2] == ("UNMEASURED", "HARNESS"),
      "fish: an unread biome is HARNESS")
check(L.fish_roll_verdict(dict(success=True, body=dict(hasBody=True, hasFish=True, size=200)), False)[0] == "PASS",
      "fish: fish seen PASS whatever the biome read")
# B0 identity (20261022T235239 ran an assembly older than the repo's and nothing said so)
check(L.assembly_identity_verdict("a" * 64, True, "a" * 64)[0] == "PASS", "identity: same sha PASS")
check(L.assembly_identity_verdict("b" * 64, True, "a" * 64)[0] == "FAIL", "can-fail identity: another build FAILs")
check(L.assembly_identity_verdict(None, None, "a" * 64)[0] == "UNMEASURED", "identity: no sha read is UNMEASURED")
check(L.assembly_identity_verdict("a" * 64, False, "a" * 64)[0] == "FAIL", "identity: a loaded image that differs from the file FAILs")
check(L.reload_verdict(True, [], []) == "PASS" and L.reload_verdict(True, [], ["pocket_covers"]) == "FAIL",
      "reload: equal is PASS, a differing key is FAIL")
check(L.reload_verdict(True, ["pocket_covers"], []) == "UNMEASURED",
      "can-fail reload: a key unread on both sides (None == None) is UNMEASURED, never PASS")


class RideGame(object):
    """g_dehydration_ride: severity rises 0.30 per 60,000 ticks; an UNDRAFTED pawn walks off (and could drink)."""
    def __init__(self, draft_works=True):
        self.t, self.drafted, self.draft_works, self.cell, self.rows = 0, False, draft_works, (183, 17), []

    def call(self, tool, **kw):
        if tool == "jawa/set_draft":
            self.drafted = self.drafted or (kw.get("drafted") is True and self.draft_works)
            return dict(success=True, drafted=self.drafted)
        if tool == "jawa/pawn_get":
            return dict(pawns=[dict(hediffs=[{"def": "RM_Dehydration", "severity": 0.3 * self.t / 60000.0}])])
        return dict(success=True)


class RideSession(FakeEventSession):
    def __init__(self, g):
        FakeEventSession.__init__(self, g)
        self.ride_stop = False

    def spawn(self, kind, c, faction="player"):
        return 7

    def now(self):
        return self.g.t

    def climb(self, pid):
        return dict(cell=self.g.cell)


def run_ride(g):
    s = RideSession(g)
    for w in L.g_dehydration_ride(s):
        g.t += w.ticks
        if not g.drafted:
            g.cell = (g.cell[0] + 1, g.cell[1])
    return g.rows[-1]


r = run_ride(RideGame())
check(r["status"] == "PASS", "ride: a drafted colonist held at thirst 0 reads the 0.30/day rate: %s" % r["detail"].get("projected60k"))
r = run_ride(RideGame(draft_works=False))
check(r["status"] == "UNMEASURED", "can-fail ride: a colonist that was never drafted is UNMEASURED, never a rate")

# 8e. SESSION_HURT_DIAGNOSE_BRUISED_AT_THE_BELL: bystanders are quenched and parked off every zone
check("RM_Thirst" in L.FEED_NEEDS and "Food" in L.FEED_NEEDS, "feed_colonists tops FlowWorks thirst too (a thirsty bystander drank channel tar)")
for size in ((250, 250), (325, 325)):      # plan_zones refuses 200-300 except 250: b0_preflight then keeps the 250 plan (row B0_zone_plan)
    zs = L.plan_zones(size)
    pc = L.park_cell(zs, size)
    check(pc is not None and 12 <= pc[0] < size[0] - 12 and 12 <= pc[1] < size[1] - 12
          and not any(L.overlaps((pc[0], pc[1], 1, 1), r, gap=6) for r in zs.values()),
          "park cell %s on a %s map is >= 6 cells from every zone" % (pc, size))
check(L.park_cell({"all": (0, 0, 250, 250)}, (250, 250)) is None, "can-fail park: a map full of zones has no park cell (None, never a zone cell)")
dl = L.census_delta({"a": {"hediffs": ["Scar"]}}, {"a": {"hediffs": ["Bruise", "Scar"], "cell": [3, 4]}, "b": {"hediffs": ["ToxicBuildup"]}})
check(dl.get("a", {}).get("new") == ["Bruise"] and dl.get("b", {}).get("spawnedDuring") is True and len(dl) == 2,
      "census_delta names each colonist's NEW hediffs and marks one spawned during the script")
check(L.census_delta({"a": {"hediffs": ["Bruise"]}}, {"a": {"hediffs": ["Bruise"]}}) == {}, "census_delta: nothing new reads empty")
check("proof_hose.py" in L.PARK_EXEMPT, "proof_hose realflow keeps the map's colonists where they stand (it drives them)")

# 9. --dry-run and --mock exit 0 offline
for flag in ("--dry-run", "--mock"):
    d = tempfile.mkdtemp(prefix="ls_selftest_")
    r = subprocess.run([sys.executable, os.path.join(HERE, "live_session.py"), flag, "--no-owner-save", "--out-dir", d],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
    check(r.returncode == 0 and "Traceback" not in r.stdout, "%s exits 0 with no traceback" % flag)

print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
