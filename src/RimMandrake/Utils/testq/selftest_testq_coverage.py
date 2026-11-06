#!/usr/bin/env python3
"""selftest_testq_coverage.py - coverage.py, the G5 measure and the filler's wired list (TESTQ_MODS_WIRE_BEYOND_FLOWWORKS).

Offline. Proves: each probe state (load, refused, offline, steve_missing from About.xml AND from a folded biome's
closure, selectable); a broken wire fails `check` and a short wire list fails `--min-wired`; TESTQ_FILL_MODS overrides
wired_mods.json, which overrides the FlowWorks fallback; the bridge backlog counts only open bridge items naming the mod;
the tick unit's fill loop reads `coverage.py wired`; and the committed wired_mods.json holds at least 6 mods, every one
of them selectable by the real probe.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage as C  # noqa: E402

FAILS = []


def check(ok, what):
    print("%s  %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def mod_dir(root, name, deps=()):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "About"))
    dl = "".join("<li><packageId>%s</packageId></li>" % p for p in deps)
    with open(os.path.join(d, "About", "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>mandrake.rm.%s</packageId><modDependencies>%s<li><packageId>Ludeon.RimWorld"
                "</packageId></li></modDependencies></ModMetaData>" % (name.lower(), dl))
    return d


def main():
    tmp = tempfile.mkdtemp(prefix="tq_cov_")
    real_chains = C.chains_of
    chains = {"Good": ["a", "b"], "Bare": [], "Off": ["x"], "Ref": ["y"], "Dep": ["z"], "Clo": ["w"]}
    C.chains_of = lambda m: (chains[m], None) if m in chains else (None, "no mod folder %s" % m)
    pv = {"Good": {"rows": ["r1", "r2"]}, "Off": {"refusal": "every selected chain of Off is offline (x): it needs no game"},
          "Ref": {"refusal": "chain y's row catalogue is incomplete"}, "Dep": {"rows": ["r"]}, "Clo": {"rows": ["r"]}}
    preview = lambda m, sel: dict({"refusal": None, "rows": None}, **pv.get(m, {}))
    minimal = {"brrainz.harmony", "neronix17.outerrim.core"}
    st = lambda m, deps=(), closure=(): C.probe(m, mod_dir(tmp, m, deps), minimal, preview, closure=list(closure))
    good = st("Good", deps=["Brrainz.Harmony", "mandrake.rm.other"])
    check(good["state"] == "selectable" and good["rows"] == 2 and good["chains"] == 2,
          "a mod whose chains preview rows, with deps on MINIMAL or ours, is selectable: %s" % good)
    check(st("Nope")["state"] == "load", "a suite modcheck cannot load is a load error")
    check(st("Bare")["state"] == "refused", "a suite with no chains is refused")
    check(st("Off")["state"] == "offline", "all-offline chains read offline, not selectable")
    check(st("Ref")["state"] == "refused", "a targeting refusal (bad_selection) reads refused")
    dep = st("Dep", deps=["sarg.alphaanimals"])
    check(dep["state"] == "steve_missing" and dep["deps_missing"] == ["sarg.alphaanimals"],
          "an About.xml dependency absent from MINIMAL is steve_missing: %s" % dep)
    clo = st("Clo", closure=["mandrake.rut.patches", "mlie.starwarsanimalcollection"])
    check(clo["state"] == "steve_missing" and clo["deps_missing"] == ["mlie.starwarsanimalcollection"],
          "a folded biome's closure donor absent from MINIMAL is steve_missing (LeaningScrub's case): %s" % clo)
    check(C.probe("Good", os.path.join(tmp, "Good"), None, preview, closure=[])["state"] == "steve_missing",
          "an unreadable MINIMAL list never reads selectable")
    C.chains_of = real_chains

    # the wired list and its precedence
    wf = os.path.join(tmp, "wired.json")
    json.dump({"mods": ["A", "B"]}, open(wf, "w"))
    check(C.read_wired(wf) == ["A", "B"], "read_wired reads the mods in order")
    check(C.read_wired(os.path.join(tmp, "absent.json")) == [], "an absent wired file reads empty")
    real_wired, saved = C.WIRED, os.environ.pop("TESTQ_FILL_MODS", None)
    try:
        C.WIRED = wf
        C.read_wired.__defaults__ = (wf,)
        check(C.fill_mods() == ["A", "B"], "without TESTQ_FILL_MODS the filler walks wired_mods.json")
        os.environ["TESTQ_FILL_MODS"] = "X Y"
        check(C.fill_mods() == ["X", "Y"], "TESTQ_FILL_MODS overrides the wired file")
        os.environ.pop("TESTQ_FILL_MODS")
        C.read_wired.__defaults__ = (os.path.join(tmp, "absent.json"),)
        check(C.fill_mods() == ["FlowWorks"], "no env and no wired file falls back to FlowWorks")
    finally:
        C.WIRED = real_wired
        C.read_wired.__defaults__ = (real_wired,)
        if saved is not None:
            os.environ["TESTQ_FILL_MODS"] = saved

    # check: a broken wire and a short list both fail
    rec = {"wired": ["A", "B"], "wired_ok": ["A"], "harnessed": 3, "scope": "wired", "counts": {},
           "probes": {"A": {"state": "selectable", "why": None}, "B": {"state": "offline", "why": "all offline"}}}
    check("BROKEN WIRES: B (offline" in C.g5_line(rec), "the G5 line names a broken wire: %s" % C.g5_line(rec))
    real_measure = C.measure
    try:
        C.measure = lambda **kw: rec
        check(C.main(["check", "--min-wired", "1"]) == 1, "check fails while a wired mod is not selectable")
        rec2 = dict(rec, wired=["A"], wired_ok=["A"])
        C.measure = lambda **kw: rec2
        check(C.main(["check", "--min-wired", "2"]) == 1, "check fails under --min-wired")
        check(C.main(["check", "--min-wired", "1"]) == 0, "check passes with every wire selectable and enough of them")
    finally:
        C.measure = real_measure

    # bridge backlog: whole-word title or id, only the items handed in (the caller filters open + needs=bridge)
    items = [("STILLSAND_DUNE_FIX", "x"), ("OTHER_1", "stillsand glare row"), ("OTHER_2", "Stillsandish thing"),
             ("FLOWWORKS_PUMP", "pump")]
    bl = C.bridge_backlog(["Stillsand", "FlowWorks", "Abyss"], items)
    check(bl == {"Stillsand": 2, "FlowWorks": 1, "Abyss": 0}, "the backlog counts items naming the mod: %s" % bl)

    # fill order rotates past the newest filler job's mod, so a mod with endless gaps cannot starve later wires
    check(C.fill_order(["A", "B", "C"], "A") == ["B", "C", "A"], "the walk starts after the last filled mod")
    check(C.fill_order(["A", "B", "C"], "C") == ["A", "B", "C"], "after the last mod the walk wraps to the first")
    check(C.fill_order(["A", "B", "C"], None) == ["A", "B", "C"], "no filler history keeps the wired order")
    check(C.fill_order(["A", "B"], "Gone") == ["A", "B"], "a last mod no longer wired keeps the wired order")

    # dated: each wired mod's newest DONE result, and its job outcomes
    recs = [{"job": {"mod": "A", "id": "J1"}, "result": {"outcome": "DONE", "finished": "2026-11-01T00:00:00Z",
                                                          "counts": {"PASS": 2}}},
            {"job": {"mod": "A", "id": "J2"}, "result": {"outcome": "DONE", "finished": "2026-11-03T00:00:00Z",
                                                          "counts": {"PASS": 1, "UNMEASURED": 1}}},
            {"job": {"mod": "B", "id": "J3"}, "result": {"outcome": "INVALID", "finished": "2026-11-04T00:00:00Z"}},
            {"job": {"mod": "Z", "id": "J4"}, "result": {"outcome": "DONE", "finished": "2026-11-04T00:00:00Z"}}]
    newest, oc = C.dated(["A", "B"], recs)
    check(newest["A"]["job"] == "J2" and newest["A"]["counts"] == {"PASS": 1, "UNMEASURED": 1},
          "dated keeps the newest DONE result: %s" % newest["A"])
    check(newest["B"] is None and oc["B"] == {"INVALID": 1}, "an INVALID job is no dated result, but is tallied")
    check("Z" not in newest, "an unwired mod's records are ignored")

    # the unit, and the real committed list (the item's done-when: >= 6 wired, each passing its probe)
    unit = open(os.path.join(HERE, "testq.py")).read()
    check("for m in $(/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/coverage.py wired)" in unit,
          "testq-tick.service's fill loop walks `coverage.py wired`")
    live = C.measure(only_wired=True)
    print(C.g5_line(live))
    check(len(live["wired"]) >= 6 and live["wired_ok"] == live["wired"],
          "the committed wired_mods.json holds >= 6 mods, each selectable: %s" % C.g5_line(live))
    check(live["wired"][0] == "FlowWorks", "FlowWorks stays first in fill order")

    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
