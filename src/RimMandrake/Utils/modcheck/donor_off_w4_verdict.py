#!/usr/bin/env python3
"""donor_off_w4_verdict.py -- DONOR_OFF_LOAD_PROVE_AFTER_BENCH: the W4 gate for retiring the Star Wars Animal
Collection (mlie.starwarsanimalcollection), one exit code per clause, judged off l1_donor_off_round.py's own rows.

    python3 src/RimMandrake/Utils/modcheck/donor_off_w4_verdict.py --offline
    python3 src/RimMandrake/Utils/modcheck/donor_off_w4_verdict.py --clause A1     # live, bridge up on the tier

Clauses (infrastructure/state/live_proofs/DONOR_OFF_LOAD_PROVE_AFTER_BENCH.criteria):
  offline  derive: tier donor_off_phase0 resolves with all five DLC and no donor (O01-O04 PASS); no About.xml under
           src/ hard-depends on the donor; every manifest flyer is a spawn subject and carries MaxFlightTime > 0 in its
           defs or patches (flight is proven by def STATE only: the live Pawn_FlightTracker read stays owner-present,
           l1_donor_off_round.py FLIGHT_* rows, and is never run here).
  A1       log: P01_TIER_TRUTH PASS (running list: no donor, all DLC); the load's exceptions name none of our defs and
           not the retired donor (L01 ours == 0, retiredDonor == 0, log not capped); L02 (cross-refs on ours) and L03
           (texture misses on ported texPaths) PASS. L01's own status is not the bar: it fails on ANY exception, and a
           19-mod list carries hundreds that are not ours (2026-10-18 run: 485 other, 0 ours).
  A2       spawn: every species of the derived manifest reads SPAWN_<kind> PASS (two spawned, two alive, no
           substitution, no log line naming it). One round, in the 600 s a live proof gets; past TIMEOUT it is
           UNMEASURED (exit 2), never a FAIL.
  A3       mapgen: MAPGEN_RUT_AridShrubland, MAPGEN_RM_TheRot, MAPGEN_RM_Webwork PASS (map biome right, life on it, no
           exception during generation).

The live clauses need a debug quicktest colony map loaded (P04_MAP): without one preflight aborts and the clause
exits 1. The round never deploys, swaps the list or restarts the game; it spawns and generates on the loaded map only.

Exit: 0 the clause holds, 1 it does not (FAIL, UNMEASURED, row missing, aborted preflight), 2 nothing was measured
(derive or the round wrote no file, or the round timed out: the live lane reads 2 as UNMEASURED) or usage.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(UTILS, "..", "..", ".."))
ROUND = os.path.join(HERE, "l1_donor_off_round.py")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

DONOR = "mlie.starwarsanimalcollection"
BIOMES = ("RM_LeaningScrub", "RM_TheRot", "RM_Webwork")
DLC = ("ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
       "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey")   # core + all five expansions (every DLC is assumed)
TIMEOUT = 570         # relentless_live proof_max_s is 600; derive takes the rest


def donor_dependents():
    """[About.xml path] under src/ whose <modDependencies> (any version block) names the donor, parsed as XML."""
    bad = []
    for p in sorted(glob.glob(os.path.join(REPO, "src", "*", "*", "About", "About.xml"))):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            bad.append(p + " (unparseable)")
            continue
        blocks = [root.find("modDependencies")] + list(root.iter("modDependenciesByVersion"))
        for b in blocks:
            if b is None:
                continue
            ids = [(x.text or "").strip().lower() for x in b.iter("packageId")]
            if DONOR in ids:
                bad.append(os.path.relpath(p, REPO))
                break
    return bad


def judge_offline(man, dependents):
    """-> (ok, [lines]) for the offline clause."""
    lines, ok = [], True
    rows = {r["id"]: r for r in man.get("offlineRows") or []}
    for rid in ("O01_TIER_RESOLVES", "O02_SUBJECTS_IN_TIER", "O03_ART_PRESENT", "O04_MANIFEST_SANE"):
        st = (rows.get(rid) or {}).get("status", "MISSING")
        ok &= st == "PASS"
        lines.append("%-22s %s" % (rid, st))
    closure = [str(x).lower() for x in (man.get("tier") or {}).get("closure") or []]
    if not closure or DONOR in closure:
        ok = False
        lines.append("tier closure: %s" % ("EMPTY" if not closure else "carries the donor"))
    dlc_missing = [d for d in DLC if d not in closure]   # O01's PASS text says "all DLC" but never checks it
    if dlc_missing:
        ok = False
        lines.append("tier closure lacks DLC: %s" % dlc_missing)
    ok &= not dependents
    lines.append("About.xml hard-depending on the donor: %s" % (dependents or "none"))
    kinds = {s["kind"] for s in man.get("species") or []} | {s["race"] for s in man.get("species") or []}
    flyers = man.get("flyers") or []
    stray = [f for f in flyers if f not in kinds]
    if not flyers or stray:
        ok = False
    lines.append("flyers with MaxFlightTime > 0 by def: %d; not a spawn subject: %s" % (len(flyers), stray or "none"))
    return ok, lines


def judge_live(clause, res, man):
    """-> (ok, [lines]) for live clause `clause` off a round result dict."""
    rows = {r["id"]: r for r in res.get("rows") or []}
    lines = []
    if res.get("aborted"):
        lines.append("round aborted at preflight: %s" % {k: rows[k]["status"] for k in rows if k.startswith("P0")})
        return False, lines

    def st(rid):
        return (rows.get(rid) or {}).get("status", "MISSING")

    if clause == "A1":
        d = (rows.get("L01_FIRST_EXCEPTION") or {}).get("detail") or {}
        if not isinstance(d, dict):
            d = {}
        checks = [("P01_TIER_TRUTH", st("P01_TIER_TRUTH") == "PASS"),
                  ("L01 ours==0", rows.get("L01_FIRST_EXCEPTION") is not None and d.get("ours") == 0),
                  ("L01 retiredDonor==0", d.get("retiredDonor") == 0),
                  ("L01 log not capped", "L01_FIRST_EXCEPTION" in rows and not d.get("capAt")),
                  ("L02_XREF_OURS", st("L02_XREF_OURS") == "PASS"),
                  ("L03_TEX_PORTED", st("L03_TEX_PORTED") == "PASS")]
        lines.append("first exception: %s" % str(d.get("firstException"))[:200])
        lines += ["%-22s %s" % (n, "ok" if v else "NO") for n, v in checks]
        return all(v for _, v in checks), lines
    if clause == "A2":
        want = [s["kind"] for s in man.get("species") or []]
        bad = {k: st("SPAWN_" + k) for k in want if st("SPAWN_" + k) != "PASS"}
        lines.append("spawn: %d kinds, %d not PASS" % (len(want), len(bad)))
        lines += ["  %s %s %s" % (k, s, str((rows.get("SPAWN_" + k) or {}).get("detail"))[:160]) for k, s in bad.items()]
        return bool(want) and not bad, lines
    if clause == "A3":
        bad = {b: st("MAPGEN_" + b) for b in BIOMES if st("MAPGEN_" + b) != "PASS"}
        lines += ["MAPGEN_%s %s" % (b, st("MAPGEN_" + b)) for b in BIOMES]
        for b in bad:
            lines.append("  %s %s" % (b, str((rows.get("MAPGEN_" + b) or {}).get("detail"))[:200]))
        return not bad, lines
    raise ValueError(clause)


def wrong_load(res):
    """-> why the running game is the wrong load for every clause (the donor or a DLC on the wrong side), or None."""
    d = next((r.get("detail") for r in res.get("rows") or [] if r.get("id") == "P01_TIER_TRUTH"), None)
    if not isinstance(d, dict):
        return None
    if d.get("donorsPresent") or d.get("dlcMissing"):
        return "tier donor_off_phase0 (all DLC, no donor); running: donors %s, DLC missing %s" % (
            d.get("donorsPresent"), d.get("dlcMissing"))
    return None


def derive(out):
    r = subprocess.run([sys.executable, ROUND, "derive", "--out", out], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=300)
    if not os.path.exists(out):
        print("UNMEASURED: derive wrote no manifest (exit %d): %s" % (r.returncode, (r.stdout + r.stderr)[-400:]))
        return None
    return json.load(open(out, encoding="utf-8"))


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def live(clause, man, man_path, scratch):
    out = os.path.join(scratch, "result_%s_%d_%d.json" % (clause, os.getpid(), time.time_ns()))
    argv = ["python.exe", win(ROUND), "run", "--manifest", win(man_path), "--out", win(out)]
    if clause == "A2":
        argv += ["--phase", "spawn"]
    elif clause == "A3":
        argv += ["--phase", "mapgen", "--only-biomes", ",".join(BIOMES)]
    else:
        argv += ["--phase", "log"]
    print("$ python.exe l1_donor_off_round.py run %s" % " ".join(argv[6:])[:300], flush=True)
    try:
        rc = subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode
    except subprocess.TimeoutExpired:
        print("UNMEASURED: the round ran past %d s" % TIMEOUT)
        return None
    if not os.path.exists(out):
        print("UNMEASURED: the round wrote no %s (exit %d)" % (out, rc))
        return None
    try:
        return json.load(open(out, encoding="utf-8"))
    finally:
        os.remove(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--offline", action="store_true")
    g.add_argument("--clause", choices=["A1", "A2", "A3"])
    a = ap.parse_args(argv)
    if a.offline:
        tmp = tempfile.mkdtemp(prefix="donor_off_w4_")
        try:
            man = derive(os.path.join(tmp, "manifest.json"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if man is None:
            return 2
        ok, lines = judge_offline(man, donor_dependents())
    else:
        import rmpaths
        scratch = rmpaths.rm_str("scratch", "donor_off_w4")
        os.makedirs(scratch, exist_ok=True)
        man_path = os.path.join(scratch, "manifest_%d.json" % os.getpid())
        try:
            man = derive(man_path)
            res = live(a.clause, man, man_path, scratch) if man is not None else None
        finally:
            if os.path.exists(man_path):
                os.remove(man_path)
        if res is None:
            return 2
        ok, lines = judge_live(a.clause, res, man)
    print("\n".join(lines))
    print("%s %s" % ("PASS" if ok else "FAIL", "offline" if a.offline else a.clause))
    why = None if a.offline else wrong_load(res)
    if why:   # last line: relentless_live.asked_reload restages instead of sending the item back
        print("reload needed: %s" % why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
