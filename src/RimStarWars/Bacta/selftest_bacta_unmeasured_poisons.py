#!/usr/bin/env python3
"""selftest_bacta_unmeasured_poisons.py -- BACTA_UNMEASURED_FIX_FALSE_FAIL_DOWNSTREAM: in a STATEFUL chain (one tank, one
pawn, one wound carried from component to component) an UNMEASURED component must end the chain's measurement: every
later component records UNMEASURED, none PASS or FAIL on a fixture that was never built. Only the content chain, whose
components each ask the game an independent question, keeps going after an UNMEASURED row.

Drives validation.py's own chain bodies through modcheck's real TestContext against a fake bridge (no game):
  * tank_scar: the fixture's permanent cut vanishes (scar0 None -> site UNMEASURED); the scar rows must not FAIL;
  * tank_heals: the Refuel job is never accepted and the tank stays dry (refuel row UNMEASURED); the rows after it
    (entering a dry tank, healing) must not FAIL;
  * content: an UNMEASURED trader row must still let the independent doctor-recipes row reach its own verdict.
Offline.

    python3 src/RimStarWars/Bacta/selftest_bacta_unmeasured_poisons.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
from modcheck.suite import TestContext  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


class FakeBridge(object):
    """Just enough of the bridge for the Bacta site helpers; `mode` plants one harness/fixture fault."""

    def __init__(self, mode):
        self.mode = mode
        self.settings = dict((k, str(v)) for k, v in V.DEFAULTS.items())
        self.hediffs = []
        self.fuel = 0.0
        self.calls = []

    def track(self, *a, **k):
        pass

    def call(self, tool, **p):
        self.calls.append(tool)
        if tool == "jawa/mod_settings_field":
            if p.get("action") == "set":
                self.settings[p["field"]] = str(p["value"])
            return {"success": True, "value": self.settings.get(p["field"])}
        if tool == "jawa/list_things":
            d = p.get("defName")
            if d == V.TANK:
                return {"success": True, "things": [{"id": "Tank1"}]}
            if d == V.FLUID:
                return {"success": True, "things": [{"id": "Bacta1"}]}
            return {"success": True, "things": []}
        if tool == "jawa/build_batch":
            return {"success": True, "placed": 1, "survived": 1}
        if tool == "jawa/power_net":
            return {"success": True, "powerOnAfter": p.get("forcePowerOn")}
        if tool == "jawa/ordered_job":
            if p.get("jobDef") == "Refuel":
                if self.mode == "refuel_refused":
                    return {"success": True, "accepted": False}
                self.fuel = float(p.get("count") or 0)
            return {"success": True, "accepted": True}
        if tool == "jawa/comp_read":
            return {"success": True, "values": {"fuel": self.fuel}}
        if tool == "jawa/inspect_string":
            return {"success": True, "things": [{"inspect": "Bacta: %d / 30" % self.fuel}]}
        if tool == "jawa/pawn_health":
            if p.get("action") == "add":
                self.hediffs.append({"def": p["hediff"], "part": p.get("bodyPart"), "severity": p.get("severity")})
            elif p.get("action") == "permanent" and self.mode == "scar_vanishes":
                self.hediffs = []
            return {"success": True}
        if tool == "jawa/pawn_get":
            return {"success": True, "pawns": [{"id": "Pawn1", "position": [1, 1], "hediffs": list(self.hediffs),
                                                "needs": [{"need": "Food", "level": 1.0}]}]}
        if tool == "jawa/get_defs":
            if "TraderKindDef" in p.get("defs", ""):
                return {"success": True, "defs": [{"defName": "Orbital_Exotic", "fields": {"stockGenerators": "<opaque>"}}]}
            return {"success": True, "defs": [{"defName": "Human", "fields": {"recipes": []}},
                                              {"defName": "Muffalo", "fields": {"recipes": ["AdministerMechSerumHealer"]}}]}
        return {"success": True}


def run(chain_name, mode, only=None):
    bridge = FakeBridge(mode)
    t = TestContext(bridge)
    t.wait_ticks = lambda n, **k: None
    t.clear_area = lambda size=40: None
    t.spawn_pawn = lambda kind, hostile=False, beyond=None: "Pawn1"
    if only is not None:   # the content chain: every row before the two under test answered as shipped
        real = bridge.call

        def call(tool, **p):
            if tool == "jawa/get_def":
                comps = [{"compClass": c} for c in ("CompBactaImmersion", "CompBactaShell", "CompPowerTrader",
                                                     "CompAffectedByFacilities", "CompFacility")]
                comps.append({"compClass": "CompRefuelable", "fields": {"fuelCapacity": 30}})
                return {"success": True, "comps": comps, "extra": {"thingClass": "Building_BactaTank", "tickerType": "Normal",
                                                                   "tradeTags": ["ExoticMisc"], "tradeability": "All"}}
            if tool == "jawa/get_defs" and "ThingDef/RSW_BactaTank" in p.get("defs", ""):
                return {"success": True, "foundCount": len(p["defs"].split(";")), "notFound": []}
            if tool == "jawa/drain_log":
                return {"success": True, "messages": []}
            return real(tool, **p)
        bridge.call = call
    dict(V.suite.chains)[chain_name](t)
    return dict((c.name, c.verdict) for c in t.components)


def main():
    rows = run("tank_scar", "scar_vanishes")
    check("sanity: the scar fixture fault makes the site row UNMEASURED", rows.get("site_ready_scar") == "UNMEASURED", repr(rows))
    later = dict((k, v) for k, v in rows.items() if k != "site_ready_scar")
    check("tank_scar: no row after an UNMEASURED site reaches PASS/FAIL", later and all(v == "UNMEASURED" for v in later.values()),
          repr(rows))

    rows = run("tank_heals", "refuel_refused")
    check("sanity: a refused Refuel job makes the refuel row UNMEASURED", rows.get("tank_refuels_via_vanilla_job") == "UNMEASURED",
          repr(rows))
    names = list(rows)
    after = names[names.index("tank_refuels_via_vanilla_job") + 1:] if "tank_refuels_via_vanilla_job" in names else []
    check("tank_heals: no row after the UNMEASURED refuel reaches PASS/FAIL",
          after and all(rows[n] == "UNMEASURED" for n in after), repr(rows))

    rows = run("content", "", only=True)
    check("sanity: the opaque trader read is UNMEASURED", rows.get("trader_stock_patch_landed") == "UNMEASURED", repr(rows))
    check("content: the independent recipes row still reaches its own verdict (FAIL: Human lacks the recipes)",
          rows.get("doctor_recipes_patch_landed") == "FAIL", repr(rows))

    print("bacta unmeasured poisons: %d failure(s) -> %s" % (len(FAILS), "OK" if not FAILS else "FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
