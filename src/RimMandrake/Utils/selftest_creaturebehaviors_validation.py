#!/usr/bin/env python3
"""Selftest for src/RimMandrake/CreatureBehaviors/validation.py's LIVE suite, run offline against a fake game.

What it guards: perceived_beauty sets perceivedBeautyEnabled False for its off arm and restores the old value in a
finally. If the off-arm probe is unreadable, _unmeasured sets t.upstream_failed, and every t.bridge_call after that is a
no-op (TestContext._guard), so a restore through _setting never reached the game and left the mechanic OFF for every
later chain (the same trap the toggle arm already documents for tracksEnabled). The restore must go straight through
the session. A planted probe checks the fake really saw the False write, so a vacuous pass cannot hide.

    python3 src/RimMandrake/Utils/selftest_creaturebehaviors_validation.py [path/to/validation.py]
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from modcheck import TestContext  # noqa: E402

VALIDATION = os.path.join(HERE, "..", "CreatureBehaviors", "validation.py")
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def load(path):
    spec = importlib.util.spec_from_file_location("creaturebehaviors_validation_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeGame(object):
    """Answers what perceived_beauty reads. With the mechanic off the Probe reply is unreadable (off_arm='dead')."""

    def __init__(self, off_arm="ok"):
        self.off_arm = off_arm
        self.settings = {"perceivedBeautyEnabled": "True"}
        self.writes = []
        self.n = 0

    def track(self, *a, **k):
        pass

    def call(self, tool, **kw):
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 100, "sizeZ": 100}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            kind = kw.get("kindDef")
            return {"success": True, "pawns": [{"id": "%s_%d" % (kind, self.n), "name": kind, "kindDef": kind}]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "%s_%d" % (k, i), "kindDef": k}
                                               for i, k in ((1, "RSW_Ollopom"), (2, "Muffalo"))]}
        if tool == "jawa/mod_settings_field":
            f = kw.get("field")
            if kw.get("action") == "set":
                self.writes.append(kw.get("value"))
                self.settings[f] = kw.get("value")
                return {"success": True}
            return {"success": True, "value": self.settings.get(f)}
        if tool == "jawa/static_call":
            on = str(self.settings["perceivedBeautyEnabled"]).lower() == "true"
            if not on and self.off_arm == "dead":
                return {"success": False, "error": "probe channel dead"}
            ollo = str(kw.get("args", "")).startswith("RSW_Ollopom")
            return {"success": True, "result": "%s|True|%s" % ("1.5" if (on and ollo) else "0", "3.0" if on else "1.5")}
        return {"success": True}


def run(v, game):
    t = TestContext(game, anchor=(50, 50))
    fn = dict(v.suite.chains)["perceived_beauty"]
    fn(t)
    return t


def main(argv):
    v = load(argv[0] if argv else VALIDATION)
    g = FakeGame()
    t = run(v, g)
    ok(t.components and t.components[-1].verdict == "PASS", "readable arms: the component PASSes (%s %s)"
       % (t.components[-1].verdict if t.components else None, t.components[-1].detail if t.components else ""))
    ok("False" in g.writes and g.settings["perceivedBeautyEnabled"] == "True", "readable arms: off written, then restored")
    g = FakeGame(off_arm="dead")
    t = run(v, g)
    ok(t.components and t.components[-1].verdict == "UNMEASURED", "dead off arm reads UNMEASURED (%s)"
       % (t.components[-1].verdict if t.components else None))
    ok("False" in g.writes, "planted probe: the off arm really wrote False (writes %s)" % g.writes)
    ok(g.settings["perceivedBeautyEnabled"] == "True",
       "dead off arm: perceivedBeautyEnabled restored to True, not left off (now %r)" % g.settings["perceivedBeautyEnabled"])
    # a None map_info reply is UNMEASURED (the map cannot be read), never an AttributeError that the component reads as FAIL
    t = TestContext(type("NoMap", (FakeGame,), {"call": lambda self, tool, **kw: None})(), anchor=(50, 50))
    try:
        v._need_surface_map(t)
        got = "returned"
    except v._Unmeasured:
        got = "UNMEASURED"
    except Exception as ex:                                                   # noqa: BLE001
        got = type(ex).__name__
    ok(got == "UNMEASURED", "map_info None -> UNMEASURED, not a crash (got %s)" % got)
    print("%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
