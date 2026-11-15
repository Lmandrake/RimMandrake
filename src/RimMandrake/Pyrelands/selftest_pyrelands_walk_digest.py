#!/usr/bin/env python3
"""Offline selftest for validation.walk_digest (RIMMANDRAKE_DROP_WALK_DIGEST_STAMPS_THE_WATCH_REBUILDS), bar walk_season_on_the_pyre.

On the full-list walk (visit_1, 2026-11-15) every count matched across the reload of pyre_walk_mid, yet the digest differed:
ProbeRegrowth's and ProbeBurnHistory's `now=` read 1101501 then 1101502, and the burn line's `burning=46;center=176,11`
read `burning=0;center=invalid` (a cache the next 60-tick watch rebuilds). Its creature fields came from list_things,
which counts RM_Ullai 0 with six on the map. A fake bridge replays the three measured probe lines (pre, mid, mid
reloaded) with list_things blind to pawns and list_pawns seeing them: mid must equal mid-reloaded, pre must differ, the
creatures must read 6 and 1, and a real change (one more history sample, one fewer ullai) must still differ.
Run: python3 <this file>   (PYRE_WALK_VALIDATION=<path to another validation.py> runs it against that copy)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

_path = os.environ.get("PYRE_WALK_VALIDATION") or os.path.join(HERE, "validation.py")
_spec = importlib.util.spec_from_file_location("validation", _path)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

# Measured probe lines, design/concepts/Pyrelands/version/in_game/visit_1/evidence/walk_state.json
REGROWTH_MID = ("now=1101501;0=596/90/72;1=802/196/193;2=551/209/205;3=5828/2775/2248;4=20264/11058/7716;"
                "5=13866/8679/5331;6=6960/4380/2203")
STATES = {
    "pre": {"Fire": 20, "fruit": 0,
            "regrowth": "now=681502;0=20/20/15",
            "burn": "now=681502;samples=1;oldestTick=680099;newestTick=680099;newest=140,24;ago=140,24;"
                    "burning=0;center=invalid"},
    "mid": {"Fire": 46, "fruit": 26,
            "regrowth": REGROWTH_MID,
            "burn": "now=1101501;samples=168;oldestTick=680099;newestTick=1100939;newest=176,11;ago=176,11;"
                    "burning=46;center=176,11"},
    "again": {"Fire": 46, "fruit": 26,
              "regrowth": REGROWTH_MID.replace("now=1101501", "now=1101502"),
              "burn": "now=1101502;samples=168;oldestTick=680099;newestTick=1100939;newest=176,11;ago=176,11;"
                      "burning=0;center=invalid"},
}
HERD = [("RM_Ullai", False)] * 6 + [("RM_FurnaceBeast", False), ("RM_Ullai", True), ("Colonist", False)]


class FakeT(object):
    def __init__(self, state, herd=HERD, truncated=False):
        self.session, self.upstream_failed = object(), False
        self.s, self.herd, self.truncated, self.notes = state, herd, truncated, []

    def _record(self, label, data):
        self.notes.append((label, data))

    def bridge_call(self, tool, **p):
        if tool == "jawa/list_things":
            n = {"Fire": self.s["Fire"], V.FRUIT_PLANT: self.s["fruit"]}.get(p.get("defName"), 0)  # blind to pawns
            return {"success": True, "things": [], "countMatched": n, "scanned": 62500}
        if tool == "jawa/list_pawns":
            rows = [{"id": i, "kindDef": k, "dead": dead, "faction": None, "intelligence": "Animal"}
                    for i, (k, dead) in enumerate(self.herd)]
            return {"success": True, "pawns": rows, "truncated": self.truncated}
        if tool == "jawa/static_call":
            return {"success": True, "result": self.s["regrowth" if p.get("method") == "ProbeRegrowth" else "burn"]}
        return {"success": True}


def main():
    probs = []
    pre, mid, again = (V.walk_digest(FakeT(STATES[k])) for k in ("pre", "mid", "again"))
    if not V.digests_match(mid, again):
        diff = dict((k, (mid.get(k), again.get(k))) for k in set(mid) | set(again) if mid.get(k) != again.get(k))
        probs.append("a correct reload of pyre_walk_mid does not match: %r" % diff)
    if V.digests_match(pre, mid):
        probs.append("pyre_walk_pre and pyre_walk_mid digest equal: the control cannot fail")
    if (mid.get("RM_Ullai"), mid.get("RM_FurnaceBeast")) != (6, 1):
        probs.append("creatures read ullai %r, furnace-beast %r (want 6, 1: list_pawns, living only)"
                     % (mid.get("RM_Ullai"), mid.get("RM_FurnaceBeast")))
    # a real loss still shows
    lost = dict(STATES["again"], burn=STATES["again"]["burn"].replace("samples=168", "samples=167"))
    if V.digests_match(mid, V.walk_digest(FakeT(lost))):
        probs.append("a reload that lost a burn-history sample still matches")
    if V.digests_match(mid, V.walk_digest(FakeT(STATES["again"], herd=HERD[1:]))):
        probs.append("a reload that lost an ullai still matches")
    if V.digests_match(mid, V.walk_digest(FakeT(dict(STATES["again"], regrowth=STATES["again"]["regrowth"]
                                                    .replace("6=6960/4380/2203", "6=6960/4380/2202"))))):
        probs.append("a reload that lost a regrowth cell still matches")
    # input kinds of the pure helpers
    strip = getattr(V, "strip_probe_fields", None)
    if strip is None:
        probs.append("validation.strip_probe_fields missing")
    else:
        for got, want in ((strip(""), ""), (strip("now=5"), ""), (strip("nowhere=1;now=2;a=b=c"), "nowhere=1;a=b=c"),
                          (strip("x=1;;center=invalid;y"), "x=1;y"), (strip(None), "")):
            if got != want:
                probs.append("strip_probe_fields: %r, want %r" % (got, want))
    try:
        V.walk_digest(FakeT(STATES["mid"], truncated=True))
        probs.append("a truncated list_pawns census was read as a count")
    except V.ExpectationFailed:
        pass
    print("selftest_pyrelands_walk_digest: %s" % ("FAIL" if probs else "PASS"))
    for p in probs:
        print("  - " + p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
