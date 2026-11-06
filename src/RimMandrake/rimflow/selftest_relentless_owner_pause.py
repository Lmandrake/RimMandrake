#!/usr/bin/env python3
"""The owner's pipeline-only pause (relentless_owner_pause.json). Owner 2026-11-05 ~22:55 PST: "I'd like to pause content
work for now on Archmagi and work entirely on the pipeline working on pipeline items." Planted: switch on, content_pause
is a global owner pause whatever the verdict or holding; content is refused, an expedited or listed content item too;
a system item (fx.first) and a LIGHTSPEED_ item start, also behind held content; the start loop says content_paused with
the owner's why; staffing does not count held content as ready; the reading shows the switch; no 6 h alarm. Switch off:
the old answers. The real switch file carries his words; no file reads off, a broken one reads on. No units, no network."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=1.0,
             max_workers=3, enrol_per_tick=50, max_queued=50, staffing=None, one_builder_per_mod=False)
ON = {"pipeline_only": True, "pipeline_prefixes": ["LIGHTSPEED_"]}
OFF = dict(ON, pipeline_only=False)
NOW = 1_000_000.0


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


class Fx:
    """What enrol, lease and the pause read (selftest_relentless_scoped_pause's Fx). paused() True stops a start at
    admission, said "paused": the proof an item got past the content pause."""
    def __init__(self, order=(), first=None, pause=None, published=(), plan=None, sw=None):
        self.order, self.first, self.plan = list(order), first or {}, plan or {}
        self.degraded, self.pause_scope = pause is not None, pause
        self.published = set(published)
        self.told = []
        if sw is not None:
            self.owner_pause_rule = sw

    def pool_order(self, r):
        return list(self.order), None

    def item_state(self, item, fresh=False):
        return {"state": "doing", "needs": "offline", "block_holds": False} if item in self.published else None

    def owner_ruled_at(self, item):
        return None

    def mem_gb(self):
        return 64.0

    def paused(self):
        return True

    def conductor_attention(self, text):
        self.told.append(text)
        return None


def q(item, status="queued", **kw):
    return dict(R.new_state(item, 1.0, ""), status=status, **kw)


def store(states=()):
    d = tempfile.mkdtemp(prefix="rlowner-")
    s = R.Store(d)
    for st in states:
        s.save(st)
    return d, s


def lease(fx, states, r=RULES, now=NOW):
    d, s = store(states)
    acts = []
    R.lease(s, fx, r, now, acts)
    return d, s, acts


def reached(acts):
    """An item got past the pause to admission: paused() said "paused" (the content_pause.json record names who was held)."""
    return any(a.get("why") == "paused" for a in acts)


# --- the switch file: his words on it; no file is off, a broken file is on
real = R.owner_pause_rule()
ok(isinstance(real, dict) and isinstance(real.get("pipeline_only"), bool) and "work entirely on the pipeline" in real.get("owner_said", "")
   and "LIGHTSPEED_" in real.get("pipeline_prefixes", ()), "file: the switch carries his words and counts Lightspeed as pipeline", real)
tmp = tempfile.mkdtemp(prefix="rlowner-f-")
ok(R.owner_pause_rule(os.path.join(tmp, "none.json")) is None, "file: no file reads off")
with open(os.path.join(tmp, "bad.json"), "w") as f:
    f.write("{not json")
bad = R.owner_pause_rule(os.path.join(tmp, "bad.json"))
ok(bad and bad["pipeline_only"] and "unreadable" in R.owner_pause(Fx(sw=bad))["why"], "file: a broken file reads on, said", bad)
shutil.rmtree(tmp, ignore_errors=True)
ok(R.owner_pause(Fx()) is None, "file: an Fx with no switch (every other test's) reads off")

# --- content_pause: on is global whatever the verdict; off is unchanged
p = R.content_pause(Fx(first={"S1": 0}, sw=ON), [q("S1", status="running")], now=NOW)
ok(p and p["mode"] == "global" and p.get("owner") and p["why"] == R.OWNER_PAUSE_WHY,
   "on: healthy verdict and no system item waiting -> still a global owner pause", p)
ok(R.content_pause(Fx(first={}, sw=ON), [], now=NOW) is not None, "on: no system item at all -> still paused")
ok(R.content_pause(Fx(first={"S1": 0}, sw=OFF), [q("S1")], now=NOW) is None, "off: healthy verdict -> no pause, as before")
p = R.content_pause(Fx(first={"S1": 0}, pause={"global": None, "lanes": ["game"]}, sw=OFF), [q("S1")], now=NOW)
ok(p and p["mode"] == "scoped" and not p.get("owner"), "off: a degraded verdict -> the scoped pause, as before", p)

# --- pause_stops: on lets only pipeline items through
op = R.content_pause(Fx(first={"S1": 0}, sw=ON), [], now=NOW)
fx = Fx(first={"S1": 0}, plan={"C_LIST": 0})
ok(R.pause_stops(op, fx, {"item": "C1"}, now=NOW) == R.OWNER_PAUSE_WHY, "on: content refused")
ok(R.pause_stops(op, fx, {"item": "C_X", "expedite": {"level": "normal"}}, now=NOW) == R.OWNER_PAUSE_WHY,
   "on: expedited content refused")
ok(R.pause_stops(op, fx, {"item": "C_LIST"}, fx.plan, NOW) == R.OWNER_PAUSE_WHY, "on: listed content refused")
ok(R.pause_stops(op, fx, {"item": "S1"}, now=NOW) is None, "on: system item passes")
ok(R.pause_stops(op, fx, {"item": "LIGHTSPEED_FOO_BAR_BAZ"}, now=NOW) is None, "on: LIGHTSPEED item passes")
gp = {"mode": "global", "why": "x", "holding": ["S1"], "lanes": []}
ok(R.pause_stops(gp, fx, {"item": "C_X", "expedite": {"level": "normal"}}, now=NOW) is None
   and R.pause_stops(gp, fx, {"item": "LIGHTSPEED_FOO_BAR_BAZ"}, now=NOW), "off: expedite passes a health pause; Lightspeed is content to it")

# --- enrol: on walks past content to pipeline items behind it
d, s = store()
took = R.enrol(s, Fx(["S1", "C1", "LIGHTSPEED_A_FIX_B", "C2"], {"S1": 0}, sw=ON), RULES, NOW)
ok(took == ["S1", "LIGHTSPEED_A_FIX_B"], "on: enrol takes the system and Lightspeed items, no content", took)
shutil.rmtree(d, ignore_errors=True)
d, s = store()
took = R.enrol(s, Fx(["S1", "C1", "LIGHTSPEED_A_FIX_B", "C2"], {"S1": 0}, sw=OFF), RULES, NOW)
ok(took == ["S1", "C1", "LIGHTSPEED_A_FIX_B", "C2"], "off: healthy enrol takes everything, as before", took)
shutil.rmtree(d, ignore_errors=True)

# --- lease: expedited content at the head of the line is held, said; a system and a Lightspeed item behind it start
pub = {"C_EXP", "C1", "S1", "LIGHTSPEED_A_FIX_B"}
st = [q("C_EXP", enrolled_at=0.1, expedite={"level": "normal", "rank": 0}), q("C1", enrolled_at=0.2),
      q("S1", enrolled_at=0.3), q("LIGHTSPEED_A_FIX_B", enrolled_at=0.4)]
d, s, acts = lease(Fx(first={"S1": 0}, published=pub, sw=ON), st)
cp = [a for a in acts if a.get("do") == "content_paused"]
ok(len(cp) == 1 and cp[0]["why"] == R.OWNER_PAUSE_WHY, "on: content_paused said once with the owner's why", cp)
rec = json.load(open(s.p("content_pause.json")))
ok(reached(acts) and rec.get("why") == R.OWNER_PAUSE_WHY and rec["stopped"] == ["C_EXP"],
   "on: expedited content at the head refused, the system item behind it placed", (acts, rec))
shutil.rmtree(d, ignore_errors=True)
d, s, acts = lease(Fx(first={"S1": 0}, published=pub, sw=ON), [x for x in st if x["item"] != "S1"])
ok(reached(acts) and json.load(open(s.p("content_pause.json")))["stopped"] == ["C_EXP", "C1"],
   "on: with no system item, the Lightspeed item behind held content is placed", acts)
shutil.rmtree(d, ignore_errors=True)
d, s, acts = lease(Fx(first={"S1": 0}, published=pub, sw=OFF), st)
ok(reached(acts) and not any(a.get("do") == "content_paused" for a in acts) and not os.path.exists(s.p("content_pause.json")),
   "off: expedited content at the head reaches admission, nothing paused", acts)
shutil.rmtree(d, ignore_errors=True)

# --- no 6 h alarm for his own pause
d, s = store()
with open(s.p("content_pause.json"), "w") as f:
    json.dump({"since": NOW - 7 * 3600}, f)
fx = Fx(first={"S1": 0})
acts = []
R.pause_alarm(s, fx, {"known": True, "stopped": ["C1"], "pause": op}, NOW, acts)
ok(not acts and not fx.told, "on: content held 7 h by his pause is not alarmed", acts)
R.pause_alarm(s, fx, {"known": True, "stopped": ["C1"], "pause": gp}, NOW, acts)
ok(any(a.get("do") == "content_paused_alarm" for a in acts), "off: a health pause 7 h old still alarms (the row can see)", acts)
shutil.rmtree(d, ignore_errors=True)

# --- the reading shows the switch
d, s = store()
ok((R.reading(s, RULES, NOW, [], fx=Fx(sw=ON)).get("owner_pause") or {}).get("why") == R.OWNER_PAUSE_WHY, "on: reading shows owner_pause")
ok(R.reading(s, RULES, NOW, [], fx=Fx(sw=OFF)).get("owner_pause") is None, "off: reading shows no owner_pause")
shutil.rmtree(d, ignore_errors=True)

print("selftest_relentless_owner_pause: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
