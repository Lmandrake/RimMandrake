#!/usr/bin/env python3
"""Selftest for readline_registry (READ_LINE_REGISTRY_SHARED_1).

Deterministic and offline: builds a fixture registry and fixture walks in a
tempdir, never touches the real repo's registry entries, never shells out.
Mirrors selftest_walklint.py's shape.

Run: python3 src/RimMandrake/Utils/modcheck/selftest_readline_registry.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import readline_registry  # noqa: E402

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
    """One registry entry, one walk citing it correctly, one walk with a
    dangling citation, one walk with an untagged (purely local) read line
    that must never be flagged."""
    _write(readline_registry.registry_path(tmp),
           "# Shared read-line registry (fixture)\n\n"
           "## registry\n\n"
           "### cannot read\n\n"
           "- [ ] `never_engineering_marker_in_player_text` (absolute) -- "
           "a bracketed marker or defName in player text.\n")

    _write(os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                         "CitesClean.md"),
           "# CitesClean -- validation walk\n"
           "subject: src/RimUtinni/Demo\n\n"
           "## north star\n"
           "state: DRAFT\n"
           "validated-hash:\n\n"
           "### must read\n"
           "read-state: DRAFT\n"
           "read-validated-hash:\n\n"
           "- [ ] `some_local_line` (fixed) -- a purely local demand, no "
           "shared tag, must never be flagged.\n\n"
           "### cannot read\n\n"
           "- [ ] `never_engineering_marker_in_player_text` (absolute, "
           "shared) -- a bracketed marker or defName in player text.\n")

    _write(os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                         "CitesDangling.md"),
           "# CitesDangling -- validation walk\n"
           "subject: src/RimUtinni/Demo\n\n"
           "## north star\n"
           "state: DRAFT\n"
           "validated-hash:\n\n"
           "### cannot read\n\n"
           "- [ ] `never_promoted_anywhere` (absolute, shared) -- an id "
           "that was never added to the registry.\n")


def test_registry_loads_its_own_ids():
    print("--- the fixture registry parses to exactly one id ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        ids = readline_registry.load_registry(tmp)
        ok(ids == {"never_engineering_marker_in_player_text"},
           "registry ids == {never_engineering_marker_in_player_text} "
           "(got %r)" % ids)


def test_missing_registry_raises_not_a_silent_zero():
    print("--- no registry file raises, rather than reporting zero "
          "findings ---")
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "design", "validation_walks"))
        raised = False
        try:
            readline_registry.load_registry(tmp)
        except FileNotFoundError:
            raised = True
        ok(raised, "load_registry raises FileNotFoundError when absent")


def test_citations_in_finds_only_shared_tagged_lines():
    print("--- citations_in() finds the shared-tagged line, not the local "
          "one ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        clean = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "CitesClean.md")
        cites = readline_registry.citations_in(clean)
        ids = [c[1] for c in cites]
        ok(ids == ["never_engineering_marker_in_player_text"],
           "exactly the shared-tagged id was found (got %r)" % ids)


def test_matching_citation_is_clean():
    print("--- a shared citation whose id IS in the registry: zero "
          "findings ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        registry_ids = readline_registry.load_registry(tmp)
        clean = os.path.join(tmp, "design", "validation_walks", "RimUtinni",
                              "CitesClean.md")
        findings = readline_registry.lint_walk(clean, registry_ids)
        ok(findings == [], "zero findings on the clean citation (got %r)"
           % (findings,))


def test_dangling_citation_fails_loudly():
    print("--- a shared citation whose id is NOT in the registry: "
          "DANGLING_CITATION, FAIL ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        registry_ids = readline_registry.load_registry(tmp)
        dangling = os.path.join(tmp, "design", "validation_walks",
                                "RimUtinni", "CitesDangling.md")
        findings = readline_registry.lint_walk(dangling, registry_ids)
        ok(len(findings) == 1, "exactly one finding (got %d)" % len(findings))
        if findings:
            sev, cls, _path, _line, token = findings[0]
            ok(sev == readline_registry.FAIL, "severity is FAIL")
            ok(cls == readline_registry.DANGLING_CITATION,
               "class is DANGLING_CITATION")
            ok(token == "never_promoted_anywhere",
               "the dangling id is named (got %r)" % token)


def test_full_lint_counts_and_findings():
    print("--- lint() over the fixture repo: right counts, one dangling "
          "finding ---")
    with tempfile.TemporaryDirectory() as tmp:
        _fixture_repo(tmp)
        findings, counts = readline_registry.lint(tmp)
        ok(counts["walks"] == 2, "2 walks found (got %d)" % counts["walks"])
        ok(counts["registry_ids"] == 1,
           "1 registry id (got %d)" % counts["registry_ids"])
        ok(counts["citations"] == 2,
           "2 shared citations found across both walks (got %d)"
           % counts["citations"])
        ok(len(findings) == 1,
           "exactly one FAIL across the fixture repo (got %d)"
           % len(findings))


def test_glob_returning_nothing_is_not_silently_clean():
    print("--- an empty walk directory reports zero walks, not a hidden "
          "zero-findings pass ---")
    with tempfile.TemporaryDirectory() as tmp:
        _write(readline_registry.registry_path(tmp),
               "## registry\n### cannot read\n"
               "- [ ] `x` (absolute) -- placeholder\n")
        findings, counts = readline_registry.lint(tmp)
        ok(counts["walks"] == 0, "an empty walk tree reports walks == 0")
        ok(findings == [], "and correctly zero findings to go with it")


def test_live_registry_exists_and_is_nonempty():
    print("--- the live repo's registry exists and parses to >= 1 id ---")
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    ids = readline_registry.load_registry(repo_root)
    ok(len(ids) >= 1, "live registry has >= 1 id (got %d)" % len(ids))
    ok("never_engineering_marker_in_player_text" in ids,
       "the founding entry (Oracle's, reconciled by "
       "READ_LINE_REGISTRY_SHARED_1) is present")


def test_live_repo_has_no_dangling_citations():
    """The gate this whole module exists for: a `shared`-tagged read-line id
    anywhere in the live walk set must resolve to a real registry entry."""
    print("--- live repo: zero dangling `shared` citations ---")
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    findings, counts = readline_registry.lint(repo_root)
    ok(counts["walks"] > 0, "live repo: walks found > 0 (got %d)"
       % counts["walks"])
    if findings:
        print("%d live dangling citation(s):" % len(findings))
        for f in findings:
            print("  -", readline_registry.format_finding(f))
    ok(len(findings) == 0,
       "live repo: 0 dangling citations (got %d)" % len(findings))


def main():
    for t in (test_registry_loads_its_own_ids,
              test_missing_registry_raises_not_a_silent_zero,
              test_citations_in_finds_only_shared_tagged_lines,
              test_matching_citation_is_clean,
              test_dangling_citation_fails_loudly,
              test_full_lint_counts_and_findings,
              test_glob_returning_nothing_is_not_silently_clean,
              test_live_registry_exists_and_is_nonempty,
              test_live_repo_has_no_dangling_citations):
        t()
    print()
    if FAILED:
        print("%d FAILED:" % len(FAILED))
        for f in FAILED:
            print("  -", f)
        return 1
    print("all readline_registry checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
