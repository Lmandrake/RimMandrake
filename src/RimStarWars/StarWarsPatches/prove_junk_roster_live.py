"""prove_junk_roster_live.py -- FASCINATING_WORLD_JUNK_1 clauses A1 and A2, read-only against the running game.

A1, the map: on the current map (made fresh on this build by the lane's quicktest), `jawa/list_things` over the whole
map for every def that junk_roster.json names (kept, cut or re-texted). The clause holds when
  * no def that the roster cuts stands on the map,
  * every junk def found is in a kept kind (and no Ancient* building of a def that the roster does not name stands), and
  * no found junk thing's in-game label says car, truck, tank, jeep or APC (the player's screen).
A map with fewer than MIN_JUNK junk things decides nothing: that is UNMEASURED, never a PASS (the sanity floor).

A2, the Fall Line: `jawa/static_call` FallLineOldJunk.Report must read junkDensityFactor=0, preventStepListed=True and
noOldJunk=True. Also: no Player.log line names an AncientJunk_Roster patch failure.

    python.exe src/RimStarWars/StarWarsPatches/prove_junk_roster_live.py [A1|A2]   (no argument: both)
    python3 src/RimStarWars/StarWarsPatches/prove_junk_roster_live.py --selftest   (offline: judge() on planted maps)

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no bridge, no game, mod not loaded, too little junk).
It writes Transient/junk_roster_live_<clause>.json, the reading, after the verdict is known.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROSTER = os.path.join(REPO, "design", "Jawa", "worldbuilding", "junk", "junk_roster.json")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

FALL_TYPE = "RimMandrake.Utinni.FallLineArrivals.FallLineOldJunk"
EARTH = re.compile(r"\b(car|cars|truck|trucks|tank|tanks|jeep|apc)\b", re.I)
PATCH_ERR = re.compile(r"AncientJunk_Roster(Cut|Text)", re.I)
# The sanity floor: a vanilla quicktest map with Ideology carries dozens of AncientJunkClusters things; under 5 the
# map (or the instrument) saw too little to decide anything.
MIN_JUNK = 5


def roster():
    with open(ROSTER, encoding="utf-8") as f:
        d = json.load(f)
    kept = {x for k in d["kinds"] for x in k["defs"]}
    cut = {c["def"] for c in d["cut"]}
    return kept, cut, kept | cut | set(d.get("text") or {})


def judge(things, kept, cut):
    """things: list_things rows ({def, label}). -> (verdict, lines). Pure."""
    lines, bad = [], []
    n = len(things)
    if n < MIN_JUNK:
        return "UNMEASURED", ["only %d junk things on the map (floor %d): this map decides nothing" % (n, MIN_JUNK)]
    by = {}
    for t in things:
        by.setdefault(t.get("def"), []).append(t)
    for d, rows in sorted(by.items()):
        if d in cut:
            bad.append("CUT def on the map: %s x%d" % (d, len(rows)))
        elif d not in kept:
            bad.append("junk def in no kept kind: %s x%d" % (d, len(rows)))
        labels = sorted({str(r.get("label") or "") for r in rows if EARTH.search(str(r.get("label") or ""))})
        if labels:
            bad.append("earth noun on screen: %s labels %s" % (d, labels[:3]))
    lines.append("junk things %d, defs %d: %s" % (n, len(by), ", ".join("%s=%d" % (d, len(r)) for d, r in sorted(by.items()))))
    return ("FAIL" if bad else "PASS"), lines + bad


def write(clause, verdict, lines):
    out = os.path.join(REPO, "Transient", "junk_roster_live_%s.json" % clause)
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"clause": clause, "verdict": verdict, "lines": lines}, f, indent=1)
    except OSError as e:
        print("note: reading not written (%s)" % e)


def a1(b):
    kept, cut, family = roster()
    r = b.call("jawa/list_things", defName=",".join(sorted(family)), limit=20000) or {}
    if not isinstance(r, dict) or "scanned" not in r:
        return "UNMEASURED", ["list_things gave no reading: %r" % (r,)][:1]
    if not r.get("scanned"):
        return "UNMEASURED", ["list_things scanned 0 things: no map is up"]
    if r.get("isCompleteList") is False:
        return "UNMEASURED", ["list_things returned a cut list (%s of %s)" % (r.get("countReturned"), r.get("countMatched"))]
    things = list(r.get("things") or [])
    # Junk the roster does not name at all: any artificial building whose def starts with Ancient and is in no kind.
    g = b.call("jawa/list_things", group="BuildingArtificial", limit=20000) or {}
    if not isinstance(g, dict) or g.get("isCompleteList") is False:
        return "UNMEASURED", ["the BuildingArtificial sweep gave no complete reading: %r" % (str(g)[:200],)]
    things += [t for t in g.get("things") or [] if str(t.get("def") or "").startswith("Ancient") and t.get("def") not in family]
    v, lines = judge(things, kept, cut)
    return v, ["scanned %s" % r.get("scanned")] + lines


def a2(b):
    r = b.call("jawa/static_call", type=FALL_TYPE, method="Report", args="x")
    text = str((r or {}).get("result") or "") if isinstance(r, dict) else ""
    if not text:
        return "UNMEASURED", ["no Report result (is FallLineArrivals loaded with its DLL?): %r" % (r,)]
    lines = [text]
    ok = ("junkDensityFactor=0 " in text + " " and "preventStepListed=True" in text and "noOldJunk=True" in text)
    try:
        import game_paths
        with open(game_paths.PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            errs = [ln.strip()[:300] for ln in fh if PATCH_ERR.search(ln)]
    except Exception as e:  # noqa: BLE001 - an unreadable log is no verdict
        return "UNMEASURED", lines + ["Player.log unreadable: %s" % e]
    lines += ["LOG  " + e for e in errs[:10]]
    return ("PASS" if ok and not errs else "FAIL"), lines


def selftest():
    kept, cut, _ = roster()
    k = sorted(kept)
    c = sorted(cut)
    ok = lambda n: [{"def": k[i % len(k)], "label": "rusted hulk"} for i in range(n)]
    cases = [
        ("a clean map passes", ok(8), "PASS"),
        ("too little junk is UNMEASURED", ok(MIN_JUNK - 1), "UNMEASURED"),
        ("a cut def fails", ok(8) + [{"def": c[0], "label": "x"}], "FAIL"),
        ("an unknown junk def fails", ok(8) + [{"def": "AncientMysteryThing", "label": "x"}], "FAIL"),
        ("a car label fails", ok(8) + [{"def": k[0], "label": "rusted car"}], "FAIL"),
        ("a 'tank' label fails", ok(8) + [{"def": k[1], "label": "Ancient Tank"}], "FAIL"),
        ("'tankard' is not an earth noun", ok(8) + [{"def": k[2], "label": "old tankard"}], "PASS"),
    ]
    bad = 0
    for name, things, want in cases:
        got = judge(things, kept, cut)[0]
        print("%s  %s (got %s)" % ("ok  " if got == want else "FAIL", name, got))
        bad += got != want
    print("selftest %s" % ("passed" if not bad else "FAILED"))
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    want = [a for a in argv if a in ("A1", "A2")] or ["A1", "A2"]
    try:
        import validation_core as vc
        b = vc.Bridge()
    except Exception as e:  # noqa: BLE001 - no bridge is no verdict
        print("UNMEASURED: no bridge: %s" % str(e)[:300])
        return 2
    codes = []
    for cl in want:
        try:
            v, lines = (a1 if cl == "A1" else a2)(b)
        except Exception as e:  # noqa: BLE001 - a failed call is no verdict
            v, lines = "UNMEASURED", ["bridge call failed: %s" % str(e)[:300]]
        for ln in lines:
            print("%s  %s" % (cl, ln))
        print("%s %s" % (cl, v))
        write(cl, v, lines)
        codes.append({"PASS": 0, "FAIL": 1}.get(v, 2))
    return 1 if 1 in codes else (2 if 2 in codes else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
