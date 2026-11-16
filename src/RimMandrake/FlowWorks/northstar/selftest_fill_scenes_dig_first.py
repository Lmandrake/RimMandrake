#!/usr/bin/env python3
"""RIMMANDRAKE_PIN_FLOWWORKS_FILL_SCENE_FIXES_RED_BEFORE_GREEN: pins the two harness fixes FlowWorks visit 1 made live
(3ed7c2c5c0) with no red-before test.

1. Every cell a concept scene fills is dug first. RM_FluidIdentityProof.ProofFillWithFluid refuses a cell that is not
   excavated (visit 1, sc_fill_front row 0: "REFUSED: (59, 0, 60) not excavated or holds another fluid (none)"), so a
   head cell left undug turned the whole scene into one staging UNMEASURED row. Every STAGE3 scene runs against a fake
   bridge that records digs and answers a fill on an undug cell with that same refusal; no scene may fill an undug
   cell, and the fill-front scene must reach its fills (the instrument can see).
2. plot_B_fill_tiers has no component hard-wired UNMEASURED. Its under-25 cm look read UNMEASURED "no bridge tool sets
   a fill under one notch" (row 18) though ProofFillWithFluid takes metres; the chain runs against a fake engine that
   stores decilitres and every component must come out PASS.

Red at 8caccd561c, green after 3ed7c2c5c0. The fakes prove the harness's staging, never the game; the live half is
visit 2's sc_fill_front and sc_fill_tiers rows.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_fill_scenes_dig_first.py
"""
import inspect
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(MOD), "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import concept_scenes as C  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


# ---------------------------------------------------------------------------------------------- 1. concept scenes
class SceneFake(object):
    """Answers every bridge call with success; records excavation_drive digs and ProofFillWithFluid fills in order."""

    def __init__(self):
        self.dug, self.fills, self.undug = set(), [], []

    def call(self, tool, **kw):
        if tool == "jawa/flowworks_excavation_drive":
            if kw.get("deepenLevels", 0) > 0:
                self.dug.add((kw["x"], kw["z"]))
            return {"success": True}
        if tool == "jawa/static_call":
            if kw.get("method") == "ProofFillWithFluid":
                x, z = (int(v) for v in kw["args"].split(",")[:2])
                self.fills.append((x, z))
                if (x, z) not in self.dug:
                    self.undug.append((x, z))
                    return {"success": True, "result": "REFUSED: (%d, 0, %d) not excavated or holds another fluid (none)"
                                                       % (x, z)}
                return {"success": True, "result": "FILLED (%d,%d)" % (x, z)}
            return {"success": True, "result": ""}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "P1"}]}
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": True}
        return {"success": True}

    def ticks(self, n):
        return None


def scene_probes():
    reached = {}
    for name, scene in sorted(C.STAGE3_SCENES.items()):
        B = SceneFake()
        kw = {"save_mid": lambda: None, "load_mid": lambda: None} if "save_mid" in inspect.signature(scene).parameters else {}
        try:                   # the scene's own wrapper turns an AssertionError into a staging row; anything that escapes
            scene(B, lambda: None, lambda: None, {"calls": []}, **kw)      # is a fake reply it cannot parse: named, not hidden
            escaped = None
        except Exception as e:
            escaped = e
        check(escaped is None, "%s runs to its end against the fake (%r)" % (name, escaped))
        reached[name] = len(B.fills)
        check(not B.undug, "%s fills only dug cells (filled %d, undug %s)" % (name, len(B.fills), sorted(set(B.undug))))
    # the instrument can see: the scenes the visit-1 fixes touched reach their fills against this fake
    for name in ("scene_fill_front", "scene_one_surface", "scene_walk_moat_season"):
        check(reached.get(name, 0) > 0, "%s reaches its fills (%d)" % (name, reached.get(name, 0)))
    # and the guard can reject: a head cell left undug is caught
    B = SceneFake()
    S = C._Stage(B, {"calls": []}, "probe")
    S.dig([(1, 1)], 4)
    try:
        S.fill([(0, 1)], 2.0, C.WATER)
    except AssertionError:
        pass
    check(B.undug == [(0, 1)], "a fill on an undug head cell is caught (%s)" % B.undug)


# ------------------------------------------------------------------------------------------ 2. plot_B_fill_tiers
U = 10000          # decilitres in one notch of one square (extensions.UNITS_PER_LEVEL)


def tiers_handler():
    g = {"d": {}, "dl": {}}

    def h(tool, p):
        if tool == "jawa/flowworks_excavation_drive":
            c = (p["x"], p["z"])
            g["d"][c] = g["d"].get(c, 0) + p.get("deepenLevels", 0)
            m = p.get("setBodyWaterM", -1)
            if m is not None and m >= 0:
                g["dl"][c] = int(round(m / 0.5 * U))
            return {"success": True}
        if tool == "jawa/flowworks_excavation_rect":
            return {"success": True, "sinkTransferredTotal": 0,
                    "rows": [{"x": x, "z": z, "dEff": g["d"].get((x, z), 0), "dl": g["dl"].get((x, z), 0), "isSink": False}
                             for x in range(p["x"], p["x"] + p["w"]) for z in range(p["z"], p["z"] + p["h"])]}
        if tool == "jawa/static_call":
            m = p.get("method")
            if m == "ProofResetRect":
                return {"success": True, "result": "RESET left=0"}
            if m == "ProofFillWithFluid":
                x, z, metres = p["args"].split(",")[:3]
                c = (int(x), int(z))
                if g["d"].get(c, 0) <= 0:
                    return {"success": True, "result": "REFUSED: not excavated"}
                g["dl"][c] = int(round(float(metres) / 0.5 * U))
                return {"success": True, "result": "FILLED"}
            if m == "ProofPitWater":
                x, z = (int(v) for v in p["args"].split(",")[:2])
                return {"success": True, "result": "PITWATER dl=%d" % g["dl"].get((x, z), 0)}
            return {"success": True, "result": ""}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": 1000, "sizeZ": 1000}
        return {"success": True}
    return h


def tiers_probes():
    import extensions as EXT
    import selftest_extensions as SX
    fn = dict(EXT.suite.chains)["plot_B_fill_tiers"]
    hard = re.findall(r"_unmeasured_if\(\s*t\s*,\s*['\"]|_owed\(", _source(fn))
    check(not hard, "plot_B_fill_tiers wires no component UNMEASURED in its source (%d found)" % len(hard))
    keep = []
    got = SX._ext_run(EXT, "plot_B_fill_tiers", tiers_handler(), keep=keep, settings={})
    check(bool(got) and "<setup>" not in got, "plot_B_fill_tiers ran against the fake (%s)" % got.get("<setup>", len(got)))
    check("fill_tier_under_quarter_metre_look" in got, "the under-25 cm component is declared")
    for name, v in sorted(got.items()):
        why = next((c.detail for c in keep if c.name == name), "")
        check(v == "PASS", "plot_B_fill_tiers %s is PASS (%s %s)" % (name, v, str(why)[:160]))


def _source(fn):
    return inspect.getsource(getattr(fn, "__wrapped__", fn))


def main():
    scene_probes()
    tiers_probes()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
