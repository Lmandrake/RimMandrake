#!/usr/bin/env python3
"""Offline selftest: the hose probe's request reaches the game by a bridge route that the companion allows.

RIMMANDRAKE_DIAGNOSE_FLOWWORKS_PUMPS_GIVE_NO_PRESSURE_FOUR_RUNS: from 2026-11-15 (b3b8f53c36) jawa/mod_settings_field `set`
refuses a type that is neither a ModSettings class nor a static *Settings class. validation_hose.H.hp posted
HoseProbe.request with it, so every probe answered "hose probe set failed": no tank could be read or filled, and four
proofs read the mod as dry. The fake below refuses as the companion does, and answers the batch tool.
"""
import json
import os
import re
import sys

FW = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(FW)
for _p in (FW, os.path.join(FW, "northstar"), os.path.join(SRC, "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import validation_hose as VH  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


class Game(object):
    """The companion's two field tools over HoseProbe's mailbox; serviced on the next call (a frame)."""
    def __init__(self):
        self.f = {"request": "", "result": "", "serial": 0}

    def frame(self):
        if self.f["request"]:
            cmd, self.f["request"] = self.f["request"], ""
            self.f["result"] = json.dumps({"success": True, "cmd": cmd, "units": 30000})
            self.f["serial"] += 1

    def raw(self, tool, kw):
        self.frame()
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "set":      # JawaBenchSafetyCore.SettingsTypeWritable
                if not kw["typeName"].endswith("Settings"):
                    return {"success": False, "error": "REFUSED: neither a Verse.ModSettings class nor a static *Settings class"}
            return {"success": True, "value": str(self.f.get(kw.get("field")))}
        if tool == "jawa/mod_settings_fields":
            vals = {k: str(self.f[k]) for k in str(kw.get("fields", "")).split(",") if k in self.f}
            out = {"success": True, "values": vals, "missing": {}, "set": None}
            if kw.get("setField"):
                self.f[kw["setField"]] = kw["setValue"]
                out["set"] = {"field": kw["setField"]}
            return out
        return {"success": False, "error": "unknown tool " + tool}


def make(cls):
    g, b = Game(), cls.__new__(cls)
    b._raw = g.raw
    return b, g


import proof_hose  # noqa: E402

for cls in (VH.H, proof_hose.PB):
    b, g = make(cls)
    r = b.hp("tank:30,28", wait_s=2.0)
    check("%s.%s.hp: the tank read is answered" % (cls.__module__, cls.__name__),
          r.get("success") is True and r.get("units") == 30000 and r.get("cmd") == "tank:30,28", r)
    r = b.hp("filltank:30,28=RM_Liquid_FreshWater,30000", wait_s=2.0)
    check("%s.%s.hp: the fill is posted" % (cls.__module__, cls.__name__), r.get("success") is True and g.f["serial"] == 2, (r, g.f))

import joint_check  # noqa: E402


class JB(object):
    def __init__(self):
        self.g = Game()

    def call(self, tool, kw):
        return self.g.raw(tool, kw)


r = joint_check._probe(JB(), "net:1,2", wait=2.0)
check("joint_check._probe: answered", r.get("success") is True and r.get("cmd") == "net:1,2", r)

import review_map  # noqa: E402

st = next(c for c in vars(review_map).values() if isinstance(c, type) and hasattr(c, "hose_probe"))


class RB(object):
    def __init__(self):
        self.g = Game()

    def call(self, tool, **kw):
        return self.g.raw(tool, kw)


o = st.__new__(st)
o.B, o.notes = RB(), []
txt = o.hose_probe("census", wait_s=2.0)
check("review_map.hose_probe: answered", '"census"' in txt and not o.notes, (txt, o.notes))

# no live script may post a probe request through the refused tool (validation_core's fallback is for a companion that lacks
# the batch tool, so it stays; so does the aerial copy of it)
BAD = re.compile(r'"jawa/mod_settings_field"[^\n]*action="set"[^\n]*field="request"')
hits = []
for base in (FW, os.path.join(SRC, "GimmeSomeSlack")):
    for dp, dn, fn in os.walk(base):
        for n in fn:
            if n.endswith(".py") and not n.startswith("selftest_") and n != "validation_aerial.py":
                with open(os.path.join(dp, n), encoding="utf-8", errors="replace") as f:
                    if BAD.search(f.read()):
                        hits.append(os.path.relpath(os.path.join(dp, n), SRC))
check("no FlowWorks or Slack script posts a probe request with mod_settings_field set", not hits, hits)

print("\n%s" % ("selftest_hose_probe_route: ALL OK" if not FAILS else "selftest_hose_probe_route: %d FAILED: %s" % (len(FAILS), FAILS)))
sys.exit(1 if FAILS else 0)
