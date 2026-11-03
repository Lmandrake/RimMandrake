#!/usr/bin/env python3
"""selftest_donor_off_w4_verdict.py -- donor_off_w4_verdict.py judges each clause off synthetic round rows, offline,
no bridge: a clause holds only on PASS rows it names, and every miss (FAIL, UNMEASURED, missing row, aborted round,
exception in our defs, a capped log, a donor dependency) reads as a failure."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import donor_off_w4_verdict as V  # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def row(rid, status, detail=None):
    return {"id": rid, "status": status, "cls": "MOD", "detail": detail}


MAN = {"species": [{"kind": "K%02d" % i, "race": "R%02d" % i} for i in range(10)],
       "flyers": ["K01", "R02"],
       "tier": {"closure": ["ludeon.rimworld", "mandrake.rsw.swbestiary"]},
       "offlineRows": [row(r, "PASS") for r in ("O01_TIER_RESOLVES", "O02_SUBJECTS_IN_TIER", "O03_ART_PRESENT",
                                                "O04_MANIFEST_SANE")]}


def log_rows(**l01):
    d = {"ours": 0, "retiredDonor": 0, "capAt": None, "firstException": "x"}
    d.update(l01)
    return {"rows": [row("P01_TIER_TRUTH", "PASS", {"donorsPresent": [], "dlcMissing": []}),
                     row("L01_FIRST_EXCEPTION", "FAIL", d), row("L02_XREF_OURS", "PASS"),
                     row("L03_TEX_PORTED", "PASS")]}


def pin_rows():
    """derive reads the committed Phase 0 pin, not git or Transient: the shipped pin is clean, and a missing pin or a
    count that drifts from it is an O04 problem (gen 1 blind-failed on a git-less export: 156 species, not 200)."""
    import json
    import l1_donor_off_round as L
    closure = {"ordered": [], "missing": [], "refusals": []}   # no installed-mod scan: the pin is the subject
    pin, err = L.load_pin()
    ok(err is None and pin["commitFiles"] and pin["expect"]["species"] > 0, "the committed pin loads: %s" % err)
    man = L.derive(closure=closure)
    ok(not [p for p in man["problems"] if "pin" in p or "expect" in p], "shipped pin derives clean: %s" % man["problems"])
    ok(len(man["species"]) == pin["expect"]["species"], "species count is the pin's %s" % pin["expect"])
    tmp = tempfile.mkdtemp(prefix="dow4pin_")
    saved = L.PIN
    try:
        L.PIN = os.path.join(tmp, "absent.json")
        ok(any("pin" in p for p in L.derive(closure=closure)["problems"]), "a missing pin is an O04 problem")
        bad = dict(pin, expect={"species": pin["expect"]["species"] + 1, "flyers": pin["expect"]["flyers"]})
        L.PIN = os.path.join(tmp, "drift.json")
        json.dump(bad, open(L.PIN, "w"))
        ok(any(p.startswith("species: derived") for p in L.derive(closure=closure)["problems"]),
           "a species count off the pin by one is an O04 problem")
    finally:
        L.PIN = saved


def main():
    # A1: L01's own FAIL on other mods' exceptions is not the bar; ours/donor/cap are
    ok(V.judge_live("A1", log_rows(), MAN)[0], "A1 holds with 0 ours / 0 donor though L01 itself reads FAIL")
    ok(not V.judge_live("A1", log_rows(ours=1), MAN)[0], "A1 fails on an exception naming ours")
    ok(not V.judge_live("A1", log_rows(retiredDonor=2), MAN)[0], "A1 fails on an exception naming the donor")
    ok(not V.judge_live("A1", log_rows(capAt=12345), MAN)[0], "A1 fails on a capped (blind) log")
    r = log_rows()
    r["rows"] = [x for x in r["rows"] if x["id"] != "L01_FIRST_EXCEPTION"]
    ok(not V.judge_live("A1", r, MAN)[0], "A1 fails when the L01 row is missing")
    r = log_rows()
    r["rows"][3] = row("L03_TEX_PORTED", "UNMEASURED")
    ok(not V.judge_live("A1", r, MAN)[0], "A1 fails on UNMEASURED L03")
    ok(not V.judge_live("A1", dict(log_rows(), aborted=True), MAN)[0], "A1 fails on an aborted round")

    # spawn: every kind of the manifest PASS, nothing else counts
    p0 = [s["kind"] for s in MAN["species"]]
    good = {"rows": [row("SPAWN_" + k, "PASS") for k in p0] + [row("SPAWN_BADTEX_CONTROL", "UNMEASURED")]}
    ok(V.judge_live("A2", good, MAN)[0], "A2 holds when every kind is PASS")
    other = {"rows": [row("SPAWN_X" + k, "PASS") for k in p0]}
    ok(not V.judge_live("A2", other, MAN)[0], "A2 does not count PASS rows of kinds outside the manifest")
    bad = {"rows": good["rows"][1:]}
    ok(not V.judge_live("A2", bad, MAN)[0], "A2 fails on one missing kind")
    bad = {"rows": [row("SPAWN_" + k, "UNMEASURED" if k == p0[0] else "PASS") for k in p0]}
    ok(not V.judge_live("A2", bad, MAN)[0], "A2 fails on one UNMEASURED kind")
    ok(not V.judge_live("A2", {"rows": []}, {"species": []})[0], "A2 fails on an empty manifest (vacuous)")

    # mapgen
    good = {"rows": [row("MAPGEN_" + b, "PASS") for b in V.BIOMES]}
    ok(V.judge_live("A3", good, MAN)[0], "A3 holds on three PASS mapgen rows")
    good["rows"][1] = row("MAPGEN_" + V.BIOMES[1], "FAIL", {"exceptions": ["NRE"]})
    ok(not V.judge_live("A3", good, MAN)[0], "A3 fails on a mapgen exception")

    # reload line
    ok(V.wrong_load({"rows": [row("P01_TIER_TRUTH", "FAIL", {"donorsPresent": [V.DONOR], "dlcMissing": []})]})
       is not None, "a running donor asks for a reload")
    ok(V.wrong_load(log_rows()) is None, "the right load asks for nothing")

    # offline
    ok(V.judge_offline(MAN, [])[0], "offline holds: rows PASS, no dependents, flyers are subjects")
    ok(not V.judge_offline(MAN, ["src/X/About/About.xml"])[0], "offline fails on a donor dependent")
    m = dict(MAN, flyers=["NOPE"])
    ok(not V.judge_offline(m, [])[0], "offline fails on a flyer that is no spawn subject")
    m = dict(MAN, tier={"closure": MAN["tier"]["closure"] + [V.DONOR]})
    ok(not V.judge_offline(m, [])[0], "offline fails on a donor in the closure")

    # donor_dependents sees a real <modDependencies> entry (sanity probe: the instrument can see)
    tmp = tempfile.mkdtemp(prefix="dow4_")
    os.makedirs(os.path.join(tmp, "src", "T", "M", "About"))
    with open(os.path.join(tmp, "src", "T", "M", "About", "About.xml"), "w") as fh:
        fh.write("<ModMetaData><modDependenciesByVersion><v1.6><li><packageId>Mlie.StarWarsAnimalCollection"
                 "</packageId></li></v1.6></modDependenciesByVersion></ModMetaData>")
    saved, V.REPO = V.REPO, tmp
    try:
        ok(V.donor_dependents() == [os.path.join("src", "T", "M", "About", "About.xml")],
           "donor_dependents finds a by-version dependency, case-folded")
    finally:
        V.REPO = saved
    pin_rows()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
