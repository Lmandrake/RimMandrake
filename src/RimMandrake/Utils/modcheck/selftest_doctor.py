#!/usr/bin/env python3
"""Selftest for modcheck.doctor (infrastructure/DETERMINISM_ASSESSMENT.md
SS4, C2).

Deterministic and offline: builds fixture walks and a fixture `src/` tree
in a tempdir for every per-assertion function, never touches the real
repo's `modcheck_status.json` or rimflow ledger, never shells out. Only
`test_real_repo_run_has_positive_counts` reads the live repo, and only to
assert its counts are positive (the failure mode `doctor` exists to avoid).

Run: python3 src/RimMandrake/Utils/modcheck/selftest_doctor.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import doctor  # noqa: E402

FAILED = []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    if not cond:
        FAILED.append(label)


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _fixture_repo(tmp):
    """A tiny but real-shaped repo covering every finding class:
    - `Good` resolves cleanly, subject and packageId both agree.
    - `Ghost` has no src folder at all (ORPHAN_WALK).
    - `NoAbout` resolves to a folder holding no About.xml (WALK_NO_ABOUT).
    - `WrongSubject` resolves to a real folder but its `subject:` line
      names a different path (SUBJECT_MISMATCH).
    - `BadPkg` resolves fine but declares the wrong packageId
      (PACKAGEID_MISMATCH).
    - `Shared1`/`Shared2` both declare the same `subject:`
      (SUBJECT_COLLISION).
    """
    _write(os.path.join(tmp, "src", "RimUtinni", "Good", "About",
                         "About.xml"),
           "<ModMetaData><packageId>mandrake.rut.good</packageId>"
           "</ModMetaData>")
    _write(os.path.join(tmp, "src", "RimUtinni", "NoAbout", "leftover.txt"),
           "just cache noise, no About.xml here")
    _write(os.path.join(tmp, "src", "RimUtinni", "WrongSubject", "About",
                         "About.xml"),
           "<ModMetaData><packageId>mandrake.rut.wrongsubject</packageId>"
           "</ModMetaData>")
    _write(os.path.join(tmp, "src", "RimUtinni", "BadPkg", "About",
                         "About.xml"),
           "<ModMetaData><packageId>mandrake.rut.realid</packageId>"
           "</ModMetaData>")
    _write(os.path.join(tmp, "src", "RimUtinni", "Shared", "About",
                         "About.xml"),
           "<ModMetaData><packageId>mandrake.rut.shared</packageId>"
           "</ModMetaData>")

    walks = os.path.join(tmp, "design", "validation_walks", "RimUtinni")
    _write(os.path.join(walks, "Good.md"),
           "subject: src/RimUtinni/Good  (packageId mandrake.rut.good)\n")
    _write(os.path.join(walks, "Ghost.md"),
           "subject: src/RimUtinni/Ghost  (packageId mandrake.rut.ghost)\n")
    _write(os.path.join(walks, "NoAbout.md"),
           "subject: src/RimUtinni/NoAbout  (packageId "
           "mandrake.rut.noabout)\n")
    _write(os.path.join(walks, "WrongSubject.md"),
           "subject: src/RimUtinni/SomewhereElse  (packageId "
           "mandrake.rut.wrongsubject)\n")
    _write(os.path.join(walks, "BadPkg.md"),
           "subject: src/RimUtinni/BadPkg  (packageId "
           "mandrake.rut.totallywrong)\n")
    _write(os.path.join(walks, "Shared1.md"),
           "subject: src/RimUtinni/Shared  (packageId mandrake.rut.shared)\n")
    _write(os.path.join(walks, "Shared2.md"),
           "subject: src/RimUtinni/Shared  (packageId mandrake.rut.shared)\n")
    return tmp


def test_positive_counts_on_the_fixture():
    print("--- walk discovery on the fixture is positive, never a silent "
          "zero ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = walklint.find_walks(tmp)
        ok(len(walks) == 7, "all 7 fixture walks were found (got %d)"
           % len(walks))


def test_good_walk_has_no_findings():
    print("--- a walk whose folder, subject and packageId all agree "
          "reports nothing ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = [w for w in walklint.find_walks(tmp)
                 if doctor.mod_name_from_walk(w) == "Good"]
        findings, _ = doctor.check_walks(tmp, walks)
        ok(findings == [], "zero findings on Good.md (got %r)" % (findings,))


def test_orphan_walk_is_caught():
    print("--- a walk naming a folder that does not exist is ORPHAN_WALK "
          "---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = [w for w in walklint.find_walks(tmp)
                 if doctor.mod_name_from_walk(w) == "Ghost"]
        findings, _ = doctor.check_walks(tmp, walks)
        cls = [f[1] for f in findings]
        ok(doctor.ORPHAN_WALK in cls,
           "Ghost.md is flagged ORPHAN_WALK (got %r)" % cls)
        for f in findings:
            if f[1] == doctor.ORPHAN_WALK:
                ok(f[0] == doctor.FAIL, "ORPHAN_WALK is FAIL severity")


def test_walk_no_about_is_caught():
    print("--- a resolved folder holding no About.xml is WALK_NO_ABOUT "
          "(the Pits class) ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = [w for w in walklint.find_walks(tmp)
                 if doctor.mod_name_from_walk(w) == "NoAbout"]
        findings, _ = doctor.check_walks(tmp, walks)
        cls = [f[1] for f in findings]
        ok(doctor.WALK_NO_ABOUT in cls,
           "NoAbout.md is flagged WALK_NO_ABOUT (got %r)" % cls)
        ok(doctor.ORPHAN_WALK not in cls,
           "NoAbout.md is NOT ORPHAN_WALK -- an existence test is not an "
           "identity test, the folder DOES exist")


def test_subject_mismatch_is_caught():
    print("--- a subject: line naming a different path than the "
          "resolved folder is SUBJECT_MISMATCH ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = [w for w in walklint.find_walks(tmp)
                 if doctor.mod_name_from_walk(w) == "WrongSubject"]
        findings, _ = doctor.check_walks(tmp, walks)
        cls = [f[1] for f in findings]
        ok(doctor.SUBJECT_MISMATCH in cls,
           "WrongSubject.md is flagged SUBJECT_MISMATCH (got %r)" % cls)


def test_packageid_mismatch_is_caught():
    print("--- a subject: packageId disagreeing with the real About.xml "
          "is PACKAGEID_MISMATCH ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        import walklint
        walks = [w for w in walklint.find_walks(tmp)
                 if doctor.mod_name_from_walk(w) == "BadPkg"]
        findings, _ = doctor.check_walks(tmp, walks)
        cls = [f[1] for f in findings]
        ok(doctor.PACKAGEID_MISMATCH in cls,
           "BadPkg.md is flagged PACKAGEID_MISMATCH (got %r)" % cls)
        for f in findings:
            if f[1] == doctor.PACKAGEID_MISMATCH:
                ok(f[0] == doctor.WARN, "PACKAGEID_MISMATCH is WARN, not "
                   "FAIL -- an unverifiable case must never block")


def test_subject_collision_is_caught():
    print("--- two walks declaring the same subject: is SUBJECT_COLLISION "
          "---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        findings, counts = doctor.check_walks(tmp)
        collisions = [f for f in findings if f[1] == doctor.SUBJECT_COLLISION]
        ok(len(collisions) == 1,
           "exactly one collision reported (got %d)" % len(collisions))
        ok(counts["subject_collisions"] == 1,
           "counts agree there is exactly one collision (got %r)" % counts)
        if collisions:
            ok("Shared1" in collisions[0][3] and "Shared2" in collisions[0][3],
               "the collision names both walks (got %r)" % (collisions[0],))
            ok(collisions[0][0] == doctor.FAIL,
               "SUBJECT_COLLISION is FAIL severity")


class _fake_status_registry(object):
    """`status.check()` always reads `status.LOG_PATH` off disk -- it has
    no parameter to inject a fixture. This context manager redirects
    `status.LOG_PATH` at a tempfile holding exactly `data`, so
    `check_status()`'s calls into the real `status.check()` see the fixture
    instead of the live repo's `modcheck_status.json`, and restores the
    real path on exit no matter what."""

    def __init__(self, tmp, data):
        self.tmp = tmp
        self.data = data
        self._orig = None

    def __enter__(self):
        import json
        import status
        self._orig = status.LOG_PATH
        status.LOG_PATH = os.path.join(self.tmp, "fake_modcheck_status.json")
        with open(status.LOG_PATH, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh)
        return self

    def __exit__(self, *exc):
        import status
        status.LOG_PATH = self._orig
        return False


def test_status_disagreement_ignores_reason_decoration():
    print("--- status.check()'s human-readable parenthetical on a "
          "non-GREEN verdict is NOT a disagreement ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        # `Good` mod, recorded RED in the fake status registry.
        # status.check() will return "RED (last run failed)" for this --
        # same verdict, just decorated. Must NOT fire STATUS_DISAGREEMENT.
        import status
        good_dir = os.path.join(tmp, "src", "RimUtinni", "Good")
        real_hash = status.mod_hash(good_dir)
        fake_status = {
            "Good": {"status": "RED", "hash": real_hash},
        }
        with _fake_status_registry(tmp, fake_status):
            findings, counts = doctor.check_status(tmp, fake_status)
        ok(counts["status_entries"] == 1, "one status entry read")
        ok(findings == [], "RED vs 'RED (last run failed)' is not flagged "
           "(got %r)" % (findings,))


def test_status_disagreement_on_stale_hash_is_caught():
    print("--- a stored GREEN whose hash no longer matches disk is "
          "STATUS_DISAGREEMENT (the Pits class: GREEN vs STALE) ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        fake_status = {
            "Good": {"status": "GREEN", "hash": "0" * 64},  # stale on purpose
        }
        with _fake_status_registry(tmp, fake_status):
            findings, _ = doctor.check_status(tmp, fake_status)
        ok(len(findings) == 1 and findings[0][1] == doctor.STATUS_DISAGREEMENT,
           "the stale GREEN is flagged STATUS_DISAGREEMENT (got %r)"
           % (findings,))
        ok(findings and findings[0][0] == doctor.FAIL,
           "STATUS_DISAGREEMENT is FAIL severity")


def test_orphan_status_is_caught_not_raised():
    print("--- a status.json key naming a folder that no longer exists "
          "reports ORPHANED, never raises (the FluidCanals class) ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        fake_status = {"RenamedAway": {"status": "GREEN", "hash": "abc"}}
        findings, _ = doctor.check_status(tmp, fake_status)
        ok(len(findings) == 1 and findings[0][1] == doctor.ORPHAN_STATUS,
           "the orphaned entry is flagged ORPHAN_STATUS (got %r)"
           % (findings,))

        # And the fix belongs in status.py itself: check_or_orphaned must
        # never raise for a mod with no folder.
        import status
        result = status.check_or_orphaned("RenamedAway")
        ok(result == "ORPHANED (no such mod folder)",
           "status.check_or_orphaned() returns ORPHANED, not a traceback "
           "(got %r)" % result)


def test_orphan_capability_is_caught():
    print("--- a capability name resolving to no folder is "
          "ORPHAN_CAPABILITY ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        findings, counts = doctor.check_capabilities(
            tmp, ["Good", "RetiredMod"])
        ok(counts["capabilities"] == 2, "two capability names counted")
        cls = [(f[1], f[2]) for f in findings]
        ok((doctor.ORPHAN_CAPABILITY, "RetiredMod") in cls,
           "RetiredMod is flagged ORPHAN_CAPABILITY (got %r)" % cls)
        ok(not any(f[2] == "Good" for f in findings),
           "Good (which resolves fine) is not flagged")


def test_cross_registry_both_directions():
    print("--- walk-without-capability and capability-without-walk are "
          "both caught, as WARN ---")
    findings = doctor.check_cross_registry(
        walk_mod_names={"HasWalkOnly", "Both"},
        capability_names={"HasCapOnly", "Both"})
    cls = {(f[1], f[2]) for f in findings}
    ok((doctor.WALK_WITHOUT_CAPABILITY, "HasWalkOnly") in cls,
       "HasWalkOnly is WALK_WITHOUT_CAPABILITY")
    ok((doctor.CAPABILITY_WITHOUT_WALK, "HasCapOnly") in cls,
       "HasCapOnly is CAPABILITY_WITHOUT_WALK")
    ok(not any(f[2] == "Both" for f in findings),
       "a mod with both a walk and a capability row is not flagged")
    ok(all(f[0] == doctor.WARN for f in findings),
       "cross-registry findings are WARN, never FAIL")


def test_empty_walk_dir_raises_rather_than_reporting_clean():
    print("--- an empty validation_walks tree makes run() raise "
          "UNMEASURED, never a silent 0-findings pass ---")
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "design", "validation_walks"))
        os.makedirs(os.path.join(tmp, "src"))
        raised = False
        try:
            doctor.run(tmp)
        except RuntimeError as e:
            raised = True
            ok("UNMEASURED" in str(e), "the refusal says UNMEASURED "
               "(got %r)" % str(e))
        ok(raised, "run() raised RuntimeError on an empty walk tree "
           "instead of returning quietly")


def test_real_repo_run_has_positive_counts():
    print("--- the live repo's own doctor run has positive counts on "
          "every registry (the failure mode this checker exists to "
          "avoid) ---")
    findings, counts = doctor.run()
    ok(counts.get("walks", 0) > 0,
       "live repo: walks read > 0 (got %r)" % counts.get("walks"))
    ok(counts.get("status_entries", 0) > 0,
       "live repo: status entries loaded > 0 (got %r)"
       % counts.get("status_entries"))
    ok(counts.get("capabilities", 0) > 0,
       "live repo: capability rows replayed > 0 (got %r)"
       % counts.get("capabilities"))
    ok(isinstance(findings, list),
       "run() returns a findings list (got %r)" % type(findings))
    # This is the specific defect the ledger already knew about --
    # SS1/SS4. If it ever disappears, the repo has actually been fixed,
    # not this test broken: leave it here as a live tripwire either way.
    ok(any(f[1] == doctor.SUBJECT_COLLISION and "SWBestiary" in f[2]
           for f in findings),
       "live repo: SWBestiary's 7-way subject collision is still "
       "detected (update this test, not the checker, once it's resolved)")


def main():
    for t in (test_positive_counts_on_the_fixture,
              test_good_walk_has_no_findings,
              test_orphan_walk_is_caught,
              test_walk_no_about_is_caught,
              test_subject_mismatch_is_caught,
              test_packageid_mismatch_is_caught,
              test_subject_collision_is_caught,
              test_status_disagreement_ignores_reason_decoration,
              test_status_disagreement_on_stale_hash_is_caught,
              test_orphan_status_is_caught_not_raised,
              test_orphan_capability_is_caught,
              test_cross_registry_both_directions,
              test_empty_walk_dir_raises_rather_than_reporting_clean,
              test_real_repo_run_has_positive_counts):
        t()
    print()
    if FAILED:
        print("%d FAILED:" % len(FAILED))
        for f in FAILED:
            print("  -", f)
        return 1
    print("all doctor checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
