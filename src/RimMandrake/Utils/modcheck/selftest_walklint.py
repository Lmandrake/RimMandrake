#!/usr/bin/env python3
"""Selftest for walklint (infrastructure/DETERMINISM_ASSESSMENT.md SS3, C1).

Deterministic and offline: builds fixture walks and a fixture `src/` tree in
a tempdir, never touches the real repo's identifiers, never shells out.

Run: python3 src/RimMandrake/Utils/modcheck/selftest_walklint.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import walklint  # noqa: E402

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
    """A tiny but real-shaped repo: one good mod, one walk with every
    finding class, one walk that is entirely clean."""
    # -- source tree: one mod, one packageId, one defName, one class -----
    _write(os.path.join(tmp, "src", "RimUtinni", "Demo", "About",
                         "About.xml"),
           "<ModMetaData><packageId>mandrake.rut.demo</packageId>"
           "</ModMetaData>")
    _write(os.path.join(tmp, "src", "RimUtinni", "Demo", "Defs",
                         "ThingDefs_Demo.xml"),
           "<Defs><ThingDef><defName>RUT_DemoThing</defName></ThingDef>"
           "</Defs>")
    _write(os.path.join(tmp, "src", "RimUtinni", "Demo", "Source",
                         "DemoComp.cs"),
           "namespace RimMandrake.Utinni.Demo {\n"
           "  public class RUT_DemoComp { }\n"
           "}\n")

    # -- a walk naming only real identifiers: zero findings ---------------
    _write(os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                         "Clean.md"),
           "# Clean -- validation walk\n"
           "subject: src/RimUtinni/Demo  (packageId mandrake.rut.demo)\n\n"
           "## the walk\n"
           "1. [L] Player.log after load contains no "
           "\"Config error in mandrake.rut.demo\" and no XML error naming "
           "`ThingDefs_Demo.xml`\n"
           "2. [D] def read-back: ThingDef `RUT_DemoThing` exists\n")

    # -- a walk hitting every finding class --------------------------------
    _write(os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                         "Dirty.md"),
           "# Dirty -- validation walk\n"
           "subject: src/RimUtinni/GoneMod  (packageId "
           "mandrake.rut.gonemod)\n\n"
           "## the walk\n"
           "1. [L] Player.log after load contains no "
           "\"Config error in mandrake.rut.gonemod\"\n"
           "2. Game load produces no Config error for "
           "mandrake.rut.alsonotreal, unrelated prose\n"
           "3. [D] def read-back: ThingDef `RUT_GhostThing` exists\n"
           "4. [L] no XML error naming `GhostFile.xml`\n"
           "5. [D] and mandrake.rut.mentioned.in.prose is unaffected\n"
           "6. [L] Player.log after load contains no "
           "\"Config error in mandrake.rut.escaped\" "
           "<!-- walklint-ok: recording a dead id on purpose -->\n")

    return tmp


def test_positive_counts_on_the_fixture():
    print("--- index and walk counts are all positive on the fixture ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        ok(len(index["packageids"]) > 0, "packageIds indexed > 0")
        ok(len(index["xml_names"]) > 0, "XML defNames/Name= indexed > 0")
        ok(len(index["cs_symbols"]) > 0, "C# symbols indexed > 0")
        ok(len(index["basenames"]) > 0, "basenames indexed > 0")

        walks = walklint.find_walks(tmp)
        ok(len(walks) == 2, "both fixture walks were found (got %d)"
           % len(walks))


def test_clean_walk_has_no_findings():
    print("--- a walk naming only real identifiers reports nothing ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        clean = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "Clean.md")
        findings = walklint.lint_walk(clean, index, tmp)
        ok(findings == [], "zero findings on the clean walk (got %r)"
           % (findings,))


def test_bad_subject_is_caught():
    print("--- subject: naming a directory with no About.xml is BAD_SUBJECT"
          " ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        dirty = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "Dirty.md")
        findings = walklint.lint_walk(dirty, index, tmp)
        subj = [f for f in findings if f[1] == walklint.BAD_SUBJECT]
        ok(len(subj) == 1, "exactly one BAD_SUBJECT finding (got %d)"
           % len(subj))
        if subj:
            ok(subj[0][0] == walklint.FAIL, "BAD_SUBJECT is FAIL severity")


def test_vacuous_absence_assertion_is_caught():
    print("--- an absence assertion naming a dead packageId is VACUOUS ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        dirty = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "Dirty.md")
        findings = walklint.lint_walk(dirty, index, tmp)
        vac = [f for f in findings if f[1] == walklint.VACUOUS]
        tokens = {f[4] for f in vac}
        ok("mandrake.rut.gonemod" in tokens,
           "the Config-error absence line is VACUOUS")
        ok("mandrake.rut.escaped" not in tokens,
           "the walklint-ok escaped line is suppressed")


def test_bad_packageid_outside_absence_context():
    print("--- a bad mandrake.* token outside an absence assertion is "
          "BAD_PACKAGEID, not VACUOUS ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        dirty = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "Dirty.md")
        findings = walklint.lint_walk(dirty, index, tmp)
        bad = [f for f in findings if f[1] == walklint.BAD_PACKAGEID]
        tokens = {f[4] for f in bad}
        ok("mandrake.rut.mentioned.in.prose" in tokens,
           "the prose-only bad id is BAD_PACKAGEID")


def test_unknown_id_and_bad_file_are_warn():
    print("--- an unknown RUT_ symbol and an unknown filename are WARN "
          "(never FAIL) ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        index = walklint.build_index(tmp)
        dirty = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "Dirty.md")
        findings = walklint.lint_walk(dirty, index, tmp)
        ids = [f for f in findings if f[1] == walklint.UNKNOWN_ID]
        files = [f for f in findings if f[1] == walklint.BAD_FILE]
        ok(len(ids) == 1 and ids[0][4] == "RUT_GhostThing",
           "RUT_GhostThing is UNKNOWN_ID (got %r)" % ids)
        ok(len(files) == 1 and files[0][4] == "GhostFile.xml",
           "GhostFile.xml is BAD_FILE (got %r)" % files)
        ok(all(f[0] == walklint.WARN for f in ids + files),
           "both are WARN severity, never FAIL")


def test_glob_returning_nothing_is_not_silently_clean():
    print("--- an empty walk directory is reported as zero walks, not "
          "hidden inside a zero-findings result ---")
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "design", "validation_walks"))
        os.makedirs(os.path.join(tmp, "src"))
        findings, counts = walklint.lint(tmp)
        ok(counts["walks"] == 0, "an empty walk tree reports walks == 0")
        ok(findings == [], "and correctly zero findings to go with it")


def test_real_repo_indexes_are_positive():
    print("--- the live repo's own indexes are all positive (the failure "
          "mode this checker exists to avoid) ---")
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    walks = walklint.find_walks(repo_root)
    ok(len(walks) > 0, "live repo: walks found > 0 (got %d)" % len(walks))
    index = walklint.build_index(repo_root)
    ok(len(index["packageids"]) > 0,
       "live repo: packageIds indexed > 0 (got %d)"
       % len(index["packageids"]))
    ok(len(walklint._symbol_index(index)) > 0,
       "live repo: symbols indexed > 0 (got %d)"
       % len(walklint._symbol_index(index)))


def main():
    for t in (test_positive_counts_on_the_fixture,
              test_clean_walk_has_no_findings,
              test_bad_subject_is_caught,
              test_vacuous_absence_assertion_is_caught,
              test_bad_packageid_outside_absence_context,
              test_unknown_id_and_bad_file_are_warn,
              test_glob_returning_nothing_is_not_silently_clean,
              test_real_repo_indexes_are_positive):
        t()
    print()
    if FAILED:
        print("%d FAILED:" % len(FAILED))
        for f in FAILED:
            print("  -", f)
        return 1
    print("all walklint checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
