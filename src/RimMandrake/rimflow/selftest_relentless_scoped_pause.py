#!/usr/bin/env python3
"""The scoped content pause (DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE). Owner, by card 2026-11-05: "What should happen
to mod work while the system is unhealthy? -> Pause only what it touches"; spec
design/RimMandrake/relentless_recovery_plan_2026-11-05.md section 3. Planted: a global pause only when a shared integrity
resource is impaired (assessment unmeasured, storage SLI spent, account circuit open, store suspect, no scopes named);
otherwise only content in a spent SLI's lane waits, a place is kept for each queued system item, content he ruled on
within 48 h passes and takes a kept place, and runnable content held over 6 h is told to the Conductor naming the
system items holding it. Also: the real rules file gives every SLI a valid scope and ops_health publishes spent_scope.
No units, no network."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import ops_health  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=1.0,
             max_workers=3, enrol_per_tick=50, max_queued=50, staffing=None, one_builder_per_mod=False)
NOW = 1_000_000.0


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


class Fx:
    """What enrol, lease and the pause read. `published` items have a ledger row (needs per `needs`); the rest are
    unpublished, so lease walks past them without starting. paused() True stops a start at admission, said."""
    def __init__(self, order=(), first=None, pause=None, published=(), needs=None, ruled=None, plan=None):
        self.order, self.first, self.plan = list(order), first or {}, plan or {}
        self.degraded = pause is not None and not (pause.get("global") == "health assessment unmeasured")
        self.pause_scope = pause
        self.published, self.needs, self.ruled = set(published), needs or {}, ruled or {}
        self.told = []

    def pool_order(self, r):
        return list(self.order), None

    def item_state(self, item, fresh=False):
        if item not in self.published and item not in self.needs:
            return None
        return {"state": "doing", "needs": self.needs.get(item, "offline"), "block_holds": False}

    def owner_ruled_at(self, item):
        return self.ruled.get(item)

    def mem_gb(self):
        return 64.0

    def paused(self):
        return True     # admission's own "paused": proves a content item got past the health pause and the reserve

    def conductor_attention(self, text):
        self.told.append(text)
        return None


def q(item, status="queued", **kw):
    return dict(R.new_state(item, 1.0, ""), status=status, **kw)


def store(states=()):
    d = tempfile.mkdtemp(prefix="rlscoped-")
    s = R.Store(d)
    for st in states:
        s.save(st)
    return d, s


def lease(fx, states, r=RULES, now=NOW, pre=None):
    d, s = store(states)
    if pre:
        pre(s)
    acts = []
    R.lease(s, fx, r, now, acts)
    return d, s, acts


def why_of(acts):
    return [a.get("why", "") for a in acts if a.get("do") in ("wait", "content_paused")]


GAME = {"global": None, "lanes": ["game"]}
SYSTEM_ONLY = {"global": None, "lanes": []}

# --- pause_scope: what a verdict pauses
ps = R.pause_scope({"state": "unmeasured"})
ok(ps["global"] and "unmeasured" in ps["global"], "scope: an unmeasured assessment pauses globally", ps)
ps = R.pause_scope({"state": "degraded", "spent": ["root_headroom"], "spent_scope": {"root_headroom": "integrity"}})
ok(ps["global"] and "root_headroom" in ps["global"], "scope: a spent storage SLI pauses globally", ps)
ps = R.pause_scope({"state": "degraded", "spent": ["infra_share"], "spent_scope": {"infra_share": "game"}})
ok(ps == {"global": None, "lanes": ["game"]}, "scope: a spent game SLI pauses only the game lane", ps)
ps = R.pause_scope({"state": "degraded", "spent": ["nightly_reds"], "spent_scope": {"nightly_reds": "system"}})
ok(ps == {"global": None, "lanes": []}, "scope: a spent system SLI pauses no content lane", ps)
ps = R.pause_scope({"state": "degraded", "spent": ["x"]})
ok(ps["global"] and "no SLI scope" in ps["global"] and "x" in ps["global"], "scope: a verdict naming no scopes keeps the old global pause, said", ps)
ps = R.pause_scope({"state": "degraded", "spent": ["a", "b"], "spent_scope": {"a": "game", "b": "all"}})
ok(ps["global"] and "b (all)" in ps["global"], "scope: one wide SLI among narrow ones makes it global", ps)
h = R.health_order({"state": "healthy", "system_items": ["S1"], "why": "ok"}, "fresh", lambda: [])
ok(h["pause"] is None, "scope: a healthy verdict pauses nothing", h)
h = R.health_order({"state": "degraded", "system_items": ["S1"], "spent": ["infra_share"],
                    "spent_scope": {"infra_share": "game"}, "why": "spent"}, "fresh", lambda: [])
ok(h["pause"] == GAME and h["degraded"], "scope: health_order carries the verdict's pause", h)

# --- content_pause: mode, holders, and Relentless's own integrity readings
ok(R.content_pause(Fx(first={"S1": 0}), [q("S1")]) is None, "pause: healthy (no pause scope) never pauses")
p = R.content_pause(Fx(first={"S1": 0}, pause=GAME), [q("S1")], now=NOW)
ok(p and p["mode"] == "scoped" and p["lanes"] == ["game"] and p["holding"] == ["S1"], "pause: a game-scope verdict is scoped", p)
ok(R.content_pause(Fx(first={"S1": 0}, pause=GAME), [q("S1", status="running")], now=NOW) is None,
   "pause: every system item worked -> no pause at all")
d, s = store()
s._write(s.p("breaker.json"), json.dumps({"until": NOW + 600, "why": "429 wave"}))
p = R.content_pause(Fx(first={"S1": 0}, pause=GAME), [q("S1")], now=NOW, store=s)
ok(p and p["mode"] == "global" and "account circuit open" in p["why"], "pause: an open account circuit makes it global", p)
shutil.rmtree(d, ignore_errors=True)
d, s = store()
s._write(R.relentless_integrity.record_path(s), json.dumps({"blocked": True}))
p = R.content_pause(Fx(first={"S1": 0}, pause=SYSTEM_ONLY), [q("S1")], now=NOW, store=s)
ok(p and p["mode"] == "global" and "store suspect" in p["why"], "pause: a blocking integrity record makes it global", p)
shutil.rmtree(d, ignore_errors=True)

# --- pause_stops: who waits
gp = {"mode": "global", "why": "w", "holding": ["S1"], "lanes": []}
sp = {"mode": "scoped", "why": "lanes game", "holding": ["S1"], "lanes": ["game"]}
fx = Fx(first={"S1": 0}, pause=GAME, needs={"C_GAME": "bridge"}, ruled={"C_RULED": NOW - 3600, "C_OLD": NOW - 49 * 3600},
        plan={"C_LIST": 0})
ok(R.pause_stops(gp, fx, {"item": "C_OFF"}, now=NOW), "stops: global stops offline content")
ok(R.pause_stops(gp, fx, {"item": "C_RULED"}, now=NOW), "stops: global stops even freshly ruled content")
ok(not R.pause_stops(gp, fx, {"item": "S1"}, now=NOW) and not R.pause_stops(gp, fx, {"item": "C_X", "expedite": {"level": "normal"}}, now=NOW)
   and not R.pause_stops(gp, fx, {"item": "C_LIST"}, fx.plan, NOW), "stops: system, expedited and listed items never wait")
ok(R.pause_stops(sp, fx, {"item": "C_GAME"}, now=NOW) == "lane game paused", "stops: scoped stops content needing the game (ledger needs)")
ok(R.pause_stops(sp, fx, {"item": "C_K", "contract": {"game": ["A1"]}}, now=NOW) == "lane game paused",
   "stops: scoped stops content whose contract has a game clause")
ok(R.pause_stops(sp, fx, {"item": "C_OFF"}, now=NOW) is None, "stops: scoped passes offline content")
ok(R.pause_stops(sp, Fx(needs={"C_RULED": "bridge"}, ruled=fx.ruled), {"item": "C_RULED"}, now=NOW) is None,
   "stops: scoped passes game content he ruled on within 48 h")
ok(R.pause_stops(sp, Fx(needs={"C_OLD": "bridge"}, ruled=fx.ruled), {"item": "C_OLD"}, now=NOW),
   "stops: a ruling 49 h old no longer passes")
ok(R.ts_epoch("1970-01-01T00:01:40Z") == 100.0 and R.ts_epoch(None) is None, "ts_epoch reads a ledger ts as UTC")

# --- enrol: scoped skips only the paused lane; global stops the walk
d, s = store()
took = R.enrol(s, Fx(["S1", "C_GAME", "C_OFF"], {"S1": 0}, pause=GAME, needs={"C_GAME": "bridge"}), RULES, NOW)
ok(took == ["S1", "C_OFF"], "enrol: scoped enrols the system item and offline content, not game content", took)
shutil.rmtree(d, ignore_errors=True)
d, s = store()
took = R.enrol(s, Fx(["S1", "C_GAME", "C_OFF"], {"S1": 0}, pause={"global": "x", "lanes": []}), RULES, NOW)
ok(took == ["S1"], "enrol: global enrols only the system item", took)
shutil.rmtree(d, ignore_errors=True)

# --- lease: the 2026-11-05 shape. One red nightly class (scope system) once stopped every mod item.
# S_Q waits for a place; 3 places, 1 running: 2 free, 1 kept for S_Q (unpublished here, so it stays queued) -> content goes
run = q("C_RUN", status="running")
st = [q("S_Q", enrolled_at=0.1), q("C_OFF", enrolled_at=0.5), run]
d, s, acts = lease(Fx(first={"S_Q": 0}, pause=SYSTEM_ONLY, published={"C_OFF"}), st)
ok(not any(w.startswith(R.PAUSED_WHY) for w in why_of(acts)) and any(a.get("why") == "paused" for a in acts),
   "lease: system-scope SLI spent, a free place beyond the kept one -> offline content reaches admission", acts)
ok(s.load("C_RUN")["status"] == "running", "lease: running content is never stopped")
shutil.rmtree(d, ignore_errors=True)

# 2 running of 3: 1 free, kept for S_Q -> content waits on the reserve, said once
st = [q("S_Q", enrolled_at=0.1), q("C_OFF", enrolled_at=0.5), q("C_OFF2", enrolled_at=0.6), run, q("C_RUN2", status="running")]
d, s, acts = lease(Fx(first={"S_Q": 0}, pause=SYSTEM_ONLY, published={"C_OFF", "C_OFF2"}), st)
w = [x for x in why_of(acts) if "reserved" in x]
ok(len(w) == 1 and w[0].startswith(R.PAUSED_WHY) and "S_Q" in w[0] and not any(a.get("why") == "paused" for a in acts),
   "lease: the last free place is kept for the queued system item, said once", acts)
ok(json.load(open(s.p("content_pause.json")))["holding"] == ["S_Q"], "lease: the held content starts the alarm clock, naming the holder")
shutil.rmtree(d, ignore_errors=True)

# same, but C_RULED carries a ruling 1 h old -> it takes the kept place
st = [q("S_Q", enrolled_at=0.1), q("C_RULED", enrolled_at=0.5), run, q("C_RUN2", status="running")]
d, s, acts = lease(Fx(first={"S_Q": 0}, pause=SYSTEM_ONLY, published={"C_RULED"}, ruled={"C_RULED": NOW - 3600}), st)
ok(not any("reserved" in x for x in why_of(acts)) and any(a.get("why") == "paused" for a in acts),
   "lease: content he ruled on within 48 h takes a kept place (and still meets admission)", acts)
shutil.rmtree(d, ignore_errors=True)

# game SLI spent: game content waits, offline content behind it still goes
st = [q("S_Q", enrolled_at=0.1), q("C_GAME", enrolled_at=0.4, contract={"game": ["A1"]}), q("C_OFF", enrolled_at=0.5)]
d, s, acts = lease(Fx(first={"S_Q": 0}, pause=GAME, published={"C_GAME", "C_OFF"}), st)
ok(any(a.get("do") == "content_paused" and a.get("item") == "C_GAME" for a in acts)
   and any(a.get("why") == "paused" for a in acts), "lease: game lane paused, offline content behind it reaches admission", acts)
shutil.rmtree(d, ignore_errors=True)

# global: the line stops at the first content item, as before
d, s, acts = lease(Fx(first={"S_Q": 0}, pause={"global": "health assessment unmeasured", "lanes": []}, published={"C_OFF"}),
                   [q("S_Q", enrolled_at=0.1), q("C_OFF", enrolled_at=0.5)])
ok(any(x.startswith(R.PAUSED_WHY) and "global" in x for x in why_of(acts)) and not any(a.get("why") == "paused" for a in acts),
   "lease: an unmeasured assessment pauses all content, said", acts)
shutil.rmtree(d, ignore_errors=True)

# --- the 6 h alarm
fx = Fx(first={"S_Q": 0}, pause={"global": "x", "lanes": []}, published={"C_OFF"})
st = [q("S_Q", enrolled_at=0.1), q("C_OFF", enrolled_at=0.5)]
d, s = store(st)
R.lease(s, fx, RULES, NOW, [])
R.lease(s, fx, RULES, NOW + 5 * 3600, [])
ok(fx.told == [], "alarm: held 5 h -> nothing told yet", fx.told)
acts = []
R.lease(s, fx, RULES, NOW + 6 * 3600 + 60, acts)
ok(len(fx.told) == 1 and "S_Q" in fx.told[0] and "C_OFF" in fx.told[0] and "> 6 h" in fx.told[0]
   and any(a.get("do") == "content_paused_alarm" for a in acts), "alarm: held over 6 h -> one Conductor line naming the holders", fx.told)
R.lease(s, fx, RULES, NOW + 6 * 3600 + 120, [])
ok(len(fx.told) == 1, "alarm: told once, not every tick", fx.told)
R.lease(s, Fx(first={"S_Q": 0}, pause=None, published={"C_OFF"}), RULES, NOW + 7 * 3600, [])
ok(not os.path.exists(s.p("content_pause.json")), "alarm: a tick with nothing held clears the clock")
shutil.rmtree(d, ignore_errors=True)
d, s = store(st)
R.lease(s, fx, RULES, NOW, [])
R.lease(s, fx, dict(RULES, share=0), NOW + 3600, [])      # an early return knows nothing of the pause: the clock stands
ok(os.path.exists(s.p("content_pause.json")), "alarm: a lease that never read the pause leaves the clock alone")
shutil.rmtree(d, ignore_errors=True)

# --- the real ledger reader: Effects.owner_ruled_at (the fakes above stub it; this drives the shipped method)
class Led:
    """Only what Effects.owner_ruled_at reads: ledger_items() -> (events, world). The method is the real one, unbound."""
    owner_ruled_at = R.Effects.owner_ruled_at
    first = {}

    def __init__(self, evs):
        self.evs = evs

    def ledger_items(self):
        return self.evs, None

    def item_state(self, item, fresh=False):
        return {"state": "doing", "needs": "bridge", "block_holds": False}


T0 = R.ts_epoch("2026-11-05T05:37:35Z")
H = 3600.0
evs = [{"seat": "OWNER", "verb": "note", "id": "C_CARD", "byCard": "q -> a", "ts": "2026-11-05T05:37:35Z"},
       {"seat": "OWNER", "verb": "note", "id": "C_SAID", "ownerSaid": "do it", "ts": "2026-11-03T05:37:35Z"},
       {"seat": "OWNER", "verb": "note", "id": "C_SAID", "ownerSaid": "again", "ts": "2026-11-05T05:37:35Z"},
       {"seat": "OWNER", "verb": "note", "id": "C_REF", "perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM",
        "ts": "2026-11-05T05:37:35Z"},
       {"seat": "BENCH", "verb": "note", "id": "C_SEAT", "ownerSaid": "relayed", "byCard": "q -> a",
        "ts": "2026-11-05T05:37:35Z"},
       {"seat": "OWNER", "verb": "note", "id": "C_OLD", "ownerSaid": "long ago", "ts": "2026-11-01T05:37:35Z"}]
led = Led(evs)
ok(T0 is not None and led.owner_ruled_at("C_CARD") == T0, "reader: an OWNER byCard event is a ruling at its ts",
   led.owner_ruled_at("C_CARD"))
ok(led.owner_ruled_at("C_SAID") == T0, "reader: the newest OWNER ownerSaid wins", led.owner_ruled_at("C_SAID"))
ok(led.owner_ruled_at("C_REF") is None, "reader: a perRuling citation is not a ruling on the item")
ok(led.owner_ruled_at("C_SEAT") is None, "reader: an agent seat's ownerSaid/byCard is not his ruling")
ok(led.owner_ruled_at("C_NONE") is None, "reader: an item with no event has no ruling")
ok(R.fresh_ruling(led, "C_CARD", T0 + 47 * H) and not R.fresh_ruling(led, "C_CARD", T0 + 49 * H),
   "reader: fresh_ruling flips between 47 h and 49 h after a card")
ok(R.fresh_ruling(led, "C_SAID", T0 + 47 * H), "reader: an older ownerSaid does not shadow a newer one")
ok(not R.fresh_ruling(led, "C_OLD", T0 + 1 * H), "reader: an ownerSaid 4 days old is not fresh")
ok(R.pause_stops(sp, led, {"item": "C_CARD"}, now=T0 + H) is None
   and R.pause_stops(sp, led, {"item": "C_CARD"}, now=T0 + 49 * H) == "lane game paused"
   and R.pause_stops(sp, led, {"item": "C_REF"}, now=T0 + H) == "lane game paused",
   "reader: through the real reader a fresh card passes the scoped pause, a stale one or a citation waits")
led.evs = evs + [{"seat": "OWNER", "verb": "note", "id": "C_LATE", "byCard": "q -> b", "ts": "2026-11-05T06:00:00Z"}]
ok(led.owner_ruled_at("C_LATE") is not None, "reader: a new ledger read is re-indexed")

# --- the real rules and the collector
with open(os.path.join(os.path.dirname(HERE), "Utils", "ops_watch_rules.json"), encoding="utf-8") as f:
    hr = json.load(f)["health"]
bad = [x.get("name") for x in hr["slis"] if x.get("scope") not in ops_health.SCOPES]
ok(not bad and hr["slis"], "rules: every health SLI names a valid scope", bad)
ok({x["name"]: x["scope"] for x in hr["slis"]}.get("infra_share") == "game"
   and all(x["scope"] == "integrity" for x in hr["slis"] if x["name"].endswith("_headroom")),
   "rules: infra_share reaches the game lane, every headroom SLI is integrity")
ok(any("scope must be one of" in pr for pr in ops_health.sli_problems(dict(ops_health.DEFAULTS, slis=[
    {"name": "a", "key": "k", "unit": "u", "op": ">", "x": 1, "scope": "nonsense"}]))), "rules: an unknown scope makes the rules unusable")
c = dict(ops_health.DEFAULTS, slis=[{"name": "a", "key": "k.a", "unit": "u", "op": ">", "x": 1, "scope": "game"},
                                    {"name": "b", "key": "k.b", "unit": "u", "op": ">", "x": 1}])
v = ops_health.verdict({}, {}, None, {"health": c}, "/nonexistent", NOW, stamp={"collector_sha": None})
ok(v.get("spent_scope") == {} and v["state"] == "healthy", "collector: nothing spent -> empty spent_scope", v.get("spent_scope"))
print("selftest_relentless_scoped_pause: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
