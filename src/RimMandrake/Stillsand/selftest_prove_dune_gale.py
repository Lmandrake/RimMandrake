"""Offline selftest for STILLSAND_DUNE_GALE_LIVE_1: prove_dune_gale.py's verdict reading, and the offline half of
the item (the water skin, the track-grid hook, the gale proof probes).

prove_dune_gale.py: modcheck is faked (subprocess.call writes a results JSON the way runner.write_sheet does). PASS ->
0; FAIL, UNMEASURED, a missing row, an unknown clause -> 1; no JSON -> 2. A fresh JSON holding all three gale rows is
reused (no second gale); a stale one is not. It pins that modcheck is asked for exactly the three gale rows.

Static: RM_CaravanWaterSkin carries RM_CompProperties_WaterVolume and sits in the mummifiedCaravan row; the eraser
subscribes TracksWiped and clears through TrackGrid.ClearCell; the probes validation.py calls exist in the proof class,
and every row the proof judges is a _comp in validation.py.
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prove_dune_gale", os.path.join(HERE, "prove_dune_gale.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def _summary(verdicts):
    comps = [{"name": "gale_incident_fires", "verdict": "PASS", "detail": ""}]
    for name, v in verdicts.items():
        if v is not None:
            comps.append({"name": name, "verdict": v, "detail": "x"})
    return {"chains": [{"name": "gale", "components": comps}]}


def run_case(clause, verdicts, write=True, preexisting_age=None):
    """-> (exit code, argv modcheck was called with or None)."""
    root = tempfile.mkdtemp(prefix="prove_dune_gale_")
    out = os.path.join(root, "Transient", "modcheck")
    os.makedirs(out)
    seen = {}

    def write_json(name, when=None):
        p = os.path.join(out, name)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"mod": "Stillsand", "stamp": "x", "summary": _summary(verdicts)}, f)
        if when is not None:
            os.utime(p, (when, when))

    if preexisting_age is not None:
        write_json("Stillsand_old.json", when=time.time() - preexisting_age)

    def fake_call(argv, **kw):
        seen["argv"] = argv
        if write:
            write_json("Stillsand_new.json")
        return 0

    old_root, old_call = P.ROOT, P.subprocess.call
    P.ROOT, P.subprocess.call = root, fake_call
    try:
        return P.main(["--clause", clause]), seen.get("argv")
    finally:
        P.ROOT, P.subprocess.call = old_root, old_call
        shutil.rmtree(root, ignore_errors=True)


ALL_PASS = dict((r, "PASS") for r in P.ROWS)


def static_checks(check):
    defs = os.path.join(HERE, "Defs")
    skin = ET.parse(os.path.join(defs, "ThingDefs_Items", "RM_CaravanWaterSkin.xml")).getroot()
    td = [d for d in skin.iter("ThingDef") if d.findtext("defName") == "RM_CaravanWaterSkin"]
    check("water skin ThingDef exists", len(td) == 1)
    comps = [li.get("Class") for li in td[0].find("comps")] if td and td[0].find("comps") is not None else []
    check("water skin carries RM_CompProperties_WaterVolume", "RimMandrake.Stillsand.RM_CompProperties_WaterVolume" in comps)
    litres = td[0].findtext("comps/li/litres") if td else None
    check("water skin has positive litres", litres is not None and float(litres) > 0)
    gale = ET.parse(os.path.join(defs, "WeatherDefs", "RM_DuneGale.xml")).getroot()
    rows = [li for li in gale.iter("li") if li.findtext("key") == "mummifiedCaravan"]
    things = rows[0].find("things") if rows else None
    check("mummifiedCaravan row lists the water skin",
          things is not None and any(c.tag == "RM_CaravanWaterSkin" and int(c.text) > 0 for c in things))
    src = os.path.join(HERE, "Source")
    eraser = open(os.path.join(src, "RM_DuneTrackEraser.cs"), encoding="utf-8").read()
    check("eraser subscribes TracksWiped", "RM_GameCondition_DuneGale.TracksWiped += OnGaleWiped;" in eraser)
    sub = eraser[eraser.find("public static int OnGaleWipedCount"):]
    check("the subscriber clears through ClearCell", "grid.ClearCell(cells[i])" in sub[:900])
    ctor = eraser[eraser.find("static RM_DuneTrackEraser()"):]
    check("subscribed before any early return in the static ctor",
          ctor.find("TracksWiped += OnGaleWiped") < ctor.find("return;"))
    proof = open(os.path.join(src, "RM_GaleTakenPolicy.cs"), encoding="utf-8").read()
    val = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    for m in sorted(set(re.findall(r'_gale_probe\(t, "(\w+)"', val))):
        check("probe %s exists" % m, ("public static string %s(string arg)" % m) in proof)
    for r in P.ROWS:
        check("validation row %s exists" % r, ('_comp(t, "%s"' % r) in val)


def main():
    fails = []

    def check(label, ok):
        print("%-4s %s" % ("ok" if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    def expect(label, got, want):
        check("%s: exit %s (want %s)" % (label, got, want), got == want)

    rc, argv = run_case("A1", ALL_PASS)
    expect("A1 all PASS", rc, 0)
    check("asks modcheck for exactly the gale rows",
          bool(argv) and "Stillsand" in argv and "--rows" in argv and argv[argv.index("--rows") + 1] == ",".join(P.ROWS))
    for clause, row in sorted(P.CLAUSES.items()):
        v = dict(ALL_PASS)
        v[row] = "FAIL"
        expect("%s row FAIL" % clause, run_case(clause, v)[0], 1)
        v[row] = "UNMEASURED"
        expect("%s row UNMEASURED" % clause, run_case(clause, v)[0], 1)
    v = dict(ALL_PASS)
    v["gale_dims_sun_exposure"] = None
    expect("A2 row missing", run_case("A2", v)[0], 1)
    expect("unknown clause", run_case("A9", ALL_PASS)[0], 1)
    expect("no results JSON", run_case("A2", ALL_PASS, write=False)[0], 2)
    rc, argv = run_case("A4", ALL_PASS, write=False, preexisting_age=60)
    expect("fresh JSON reused", rc, 0)
    check("fresh JSON reused without a second run", argv is None)
    expect("stale JSON not reused", run_case("A4", ALL_PASS, write=False, preexisting_age=P.REUSE_S + 60)[0], 2)
    static_checks(check)
    print("RESULT: %s" % ("FAIL " + ", ".join(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
