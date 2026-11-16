#!/usr/bin/env python3
"""Offline guard for live_stub_joins.py's probe path (RIMMANDRAKE_SHOW_SLACK_FIXES_LIVE_WHEN_BUILDERS_END, measured 2026-11-16).

The angle-rule builder's live run got "no answer in three tries" after loading GSS_OWNER_LOOK_20261116 and blamed the mod.
The mod was never silent: the companion's single-field `jawa/mod_settings_field set` REFUSES GimmeSomeSlackProbe ("neither a
Verse.ModSettings class nor a static *Settings class"), live_stub_joins ignored that refusal and polled a serial nothing would
move. The batched `jawa/mod_settings_fields` (validation_core.probe_of) is the path that posts. This fake bridge answers the
way the live game did: single-field set refused, batched set served on the next read. Red on the base script, green on the fix.

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_live_stub_joins_probe.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_stub_joins as L  # noqa: E402
import validation_core as vc  # noqa: E402

REFUSAL = ("REFUSED: 'RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe' is neither a Verse.ModSettings class nor a static "
           "*Settings class of a running mod's assembly; set writes only a mod's settings (list and get still read any type).")
CLEAN = {"success": True, "stubs": 40, "taken": 40, "offLine": 0, "offSlope": 0, "empty": 0, "liveTails": 3, "liveOffSlope": 0,
         "livePinched": 0, "wallTerminalsLoose": 0, "bad": []}


class FakeGame(vc._BridgeBase):
    """The live companion's two field tools, as measured: single-field set refused, batched set posts; the probe answers at
    the next read (a frame passed)."""

    def __init__(self, answer):
        self.serial, self.result, self.pending, self.answer, self.seen = 0, "", None, answer, []

    def _frame(self):
        if self.pending is not None:
            cmd, self.pending = self.pending, None
            self.result = json.dumps(self.answer if cmd.startswith("joins:") else {"success": True, "cmd": cmd})
            self.serial += 1

    def _raw(self, tool, kw):
        self.seen.append(tool)
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "set":
                return {"success": False, "message": REFUSAL}
            self._frame()
            return {"success": True, "value": str({"serial": self.serial, "result": self.result, "request": ""}[kw["field"]])}
        if tool == "jawa/mod_settings_fields":
            self._frame()
            vals = {f: str(getattr(self, f)) for f in kw["fields"].split(",")}
            out = {"success": True, "values": vals, "ticksGame": 1}
            if kw.get("setField"):
                self.pending, out["set"] = kw["setValue"], True
            return out
        return {"success": True}


def main():
    fails = []

    def check(ok, msg):
        print(("PASS " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    g = FakeGame(CLEAN)
    try:
        rc = L.main(["--rect", "0,0,10,10"], bridge=g)
    except TypeError as ex:
        rc = "no bridge injection (%s)" % ex
    check(rc == 0, "a clean probe answer through the batched field tool PASSes (rc=%r)" % (rc,))
    check("jawa/mod_settings_fields" in g.seen, "the request is posted with jawa/mod_settings_fields, the tool that is not refused")

    bad = dict(CLEAN, offSlope=3)
    g2 = FakeGame(bad)
    try:
        rc2 = L.main(["--rect", "0,0,10,10"], bridge=g2)
    except TypeError as ex:
        rc2 = "no bridge injection (%s)" % ex
    check(rc2 == 1, "3 off-slope cords FAIL (rc=%r)" % (rc2,))

    class Refuses(FakeGame):
        def _raw(self, tool, kw):
            if tool == "jawa/mod_settings_fields":
                return {"success": False, "message": REFUSAL, "values": {"serial": "0"}, "set": False}
            return FakeGame._raw(self, tool, kw)

    g3 = Refuses(CLEAN)
    try:
        r3 = L.probe_of(g3, "joins:0,0,1,1", wait_s=1.0)
    except (TypeError, AttributeError) as ex:
        r3 = {"error": "no probe_of (%s)" % ex}
    check("set failed" in str(r3.get("error")), "a refused post says 'probe set failed', never waits out a timeout (%s)" % r3.get("error"))

    print("%d/%d" % (4 - len(fails), 4))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
