#!/usr/bin/env python3
"""selftest_expectations_manifest.py - fast, offline, no-game selftest for
expectations_manifest.py + run_expectations.py (MASS_VALIDATION_LADDER_1).

Same shape as selftest_research_validator.py: every checked behavior gets at
least one case engineered to trip it and at least one engineered to pass it,
so an always-PASS bug in the diff logic cannot hide behind an all-pass
fixture. Uses the real `testdata/expectations_selftest_manifest.json` +
`expectations_selftest_fixture.json` pair through the real `load_manifest()`/
`evaluate()` path - no mocked internals.

Run:  python3 src/RimMandrake/Utils/selftest_expectations_manifest.py
Exit 0 = every assertion behaved as engineered. Exit 1 = a real regression.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import expectations_manifest as em  # noqa: E402
import run_expectations as re_  # noqa: E402

MANIFEST = HERE / "testdata" / "expectations_selftest_manifest.json"
FIXTURE = HERE / "testdata" / "expectations_selftest_fixture.json"

FAILED = []
CHECKED = [0]


def expect(label, condition, detail=""):
    CHECKED[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s%s" % (label, ("  -- " + detail) if detail else ""))
        FAILED.append(label)


# --------------------------------------------------------------- path walking

def test_walk_path():
    obj = {"a": {"b": [{"c": 3}, {"c": 4}]}}
    expect("walk_path scalar", em.walk_path({"x": 1}, "x") == 1)
    expect("walk_path nested dict+list+dict",
           em.walk_path(obj, "a.b[1].c") == 4)
    try:
        em.walk_path(obj, "a.b[9].c")
        expect("walk_path out-of-range index raises", False)
    except KeyError:
        expect("walk_path out-of-range index raises", True)
    try:
        em.walk_path(obj, "a.nope")
        expect("walk_path missing key raises", False)
    except KeyError:
        expect("walk_path missing key raises", True)


def test_classify_path():
    expect("classify scalar", em.classify_path("wildness") == "scalar")
    expect("classify deep (dot)", em.classify_path("race.wildness") == "deep")
    expect("classify deep (bracket)", em.classify_path("stages[0]") == "deep")


# --------------------------------------------------------------- manifest parsing

def test_manifest_parse_rejects_malformed():
    try:
        em.parse_manifest({"checks": []})
        expect("parse rejects missing 'item'", False)
    except em.ManifestError:
        expect("parse rejects missing 'item'", True)

    try:
        em.parse_manifest({"item": "X", "checks": []})
        expect("parse rejects empty checks list", False)
    except em.ManifestError:
        expect("parse rejects empty checks list", True)

    try:
        em.parse_manifest({"item": "X", "checks": [{"defType": "T", "defName": "N"}]})
        expect("parse rejects check missing 'path'/'expected'", False)
    except em.ManifestError:
        expect("parse rejects check missing 'path'/'expected'", True)

    m = em.parse_manifest({"item": "X", "checks": [
        {"defType": "T", "defName": "N", "path": "a", "expected": 1}]})
    expect("parse accepts a minimal valid manifest", m.item == "X" and len(m.checks) == 1)


# --------------------------------------------------------------- evaluate()

def test_evaluate_against_real_fixtures():
    manifest = em.load_manifest(MANIFEST)
    live = re_._load_fixture(str(FIXTURE))
    results = em.evaluate(manifest, live, allow_deep=True)
    # Index by (defName, path): two checks share the bare path "wildness"
    # (RSW_Cindermare and RSW_DoesNotExist) and another two share
    # "stages[N].label"'s prefix - a path-only dict would silently collide
    # and hide exactly the kind of bug this ladder exists to catch.
    by_defpath = {(r.check.defName, r.check.path): r for r in results}

    expect("scalar PASS (wildness matches)",
           by_defpath[("RSW_Cindermare", "wildness")].status == "PASS")
    expect("scalar FAIL (raceGroup mismatch reports both values)",
           by_defpath[("RSW_Cindermare", "raceGroup")].status == "FAIL"
           and "wrong-on-purpose" in by_defpath[("RSW_Cindermare", "raceGroup")].detail
           and "Predator" in by_defpath[("RSW_Cindermare", "raceGroup")].detail)
    expect("MISSING-DEF (defName absent from live_defs)",
           by_defpath[("RSW_DoesNotExist", "wildness")].status == "MISSING-DEF")
    expect("deep PASS (stages[0].label matches)",
           by_defpath[("RSW_ColdDrain", "stages[0].label")].status == "PASS")
    expect("deep PATH-ERROR (stages[9] out of range)",
           by_defpath[("RSW_ColdDrain", "stages[9].label")].status == "PATH-ERROR")

    counts = em.summarize(results)
    expect("summarize counts add up to len(results)",
           sum(counts.values()) == len(results),
           "counts=%r results=%d" % (counts, len(results)))


def test_deep_checks_skip_without_allow_deep():
    """The honest-by-default guard: live (--live, allow_deep=False) mode must
    never silently attempt a deep check against scalar-only live data."""
    manifest = em.load_manifest(MANIFEST)
    live = re_._load_fixture(str(FIXTURE))
    results = em.evaluate(manifest, live, allow_deep=False)
    deep_results = [r for r in results if r.check.is_deep]
    scalar_results = [r for r in results if not r.check.is_deep]
    expect("deep checks all SKIPPED-PENDING-UPGRADE when allow_deep=False",
           deep_results and all(r.status == "SKIPPED-PENDING-UPGRADE" for r in deep_results))
    expect("scalar checks still evaluate when allow_deep=False",
           scalar_results and any(r.status in ("PASS", "FAIL", "MISSING-DEF") for r in scalar_results))


# --------------------------------------------------------------- fixture loader

def test_fixture_loader_rejects_bad_keys():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"NoDoubleColonHere": {}}, f)
        path = f.name
    try:
        re_._load_fixture(path)
        expect("fixture loader rejects a key with no '::' ", False)
    except em.ManifestError:
        expect("fixture loader rejects a key with no '::' ", True)
    finally:
        Path(path).unlink(missing_ok=True)


# --------------------------------------------------------------- run

def main():
    test_walk_path()
    test_classify_path()
    test_manifest_parse_rejects_malformed()
    test_evaluate_against_real_fixtures()
    test_deep_checks_skip_without_allow_deep()
    test_fixture_loader_rejects_bad_keys()

    print("\n%d checked, %d failed" % (CHECKED[0], len(FAILED)))
    if FAILED:
        print("FAILED: %s" % ", ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
