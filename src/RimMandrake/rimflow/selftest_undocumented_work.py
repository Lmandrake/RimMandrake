#!/usr/bin/env python3
"""Selftest for cli.py's `_undocumented_work_warning` (QUEUE_ITEM_FILES_DECAY_1).

    python3 src/RimMandrake/rimflow/selftest_undocumented_work.py

This is the check `rimflow show` now runs before dumping an item's prose: a
substring search over commit messages for "<ID>:" (this repo's near-universal
subject-line convention), flagging when every commit that cites an ID left
items/<ID>.md untouched — exactly the gap that let BUILDING_THEFT_HAULER_1
and SETTLEMENT_VERBS_WAVE_1 both nearly get re-built from scratch on
2026-09-02 after being fully built and committed the night before.

🔴 A SCRATCH GIT REPO, NOT THE REAL ONE. The function shells out to `git log`
against `model.ROOT`, so testing it for real means giving it real commits —
this builds a tiny throwaway repo under the real repo (same 9p-filesystem
reasoning selftest_cli.py's own header documents: `/tmp` here is a different,
lossier filesystem) with `model.ROOT`/`model.ITEMS` monkeypatched to point at
it, then restores both. Nothing here ever touches this project's own git
history.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP = os.path.join(REPO, ".rimflow_selftest_undoc")     # under the repo, ON 9p, on purpose

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


def _run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("%s failed: %s%s" % (cmd, r.stdout, r.stderr))
    return r.stdout


def _commit(cwd, path, content, message):
    full = os.path.join(cwd, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    _run(["git", "add", path], cwd)
    _run(["git", "commit", "-m", message], cwd)


def main():
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    try:
        _run(["git", "init", "-q"], TMP)
        _run(["git", "config", "user.email", "selftest@example.com"], TMP)
        _run(["git", "config", "user.name", "selftest"], TMP)

        import importlib
        cli = importlib.import_module("rimflow.cli")
        model = importlib.import_module("rimflow.model")
        real_root, real_items = model.ROOT, model.ITEMS
        model.ROOT = TMP
        model.ITEMS = os.path.join(TMP, "infrastructure", "state", "items")

        try:
            # ---- an ID nobody has ever mentioned -----------------------------
            def _no_citation_case():
                _commit(TMP, "src/thing.py", "x = 1\n", "unrelated setup commit")
                got = cli._undocumented_work_warning("NEVER_MENTIONED_1")
                assert got is None, "an ID with zero citing commits must be silent: got %r" % got
            case("no_citing_commits_is_silent", _no_citation_case)

            # ---- the exact BUILDING_THEFT_HAULER_1 shape: real work committed,
            # item file never touched -------------------------------------------
            def _undoc_case():
                _commit(TMP, "src/FooMod/Thing.cs", "class Thing {}\n",
                        "FAKE_ITEM_1: build the fake thing, done and deployed")
                got = cli._undocumented_work_warning("FAKE_ITEM_1")
                assert got is not None, "a commit citing FAKE_ITEM_1: that never touches its item file must warn"
                assert "FAKE_ITEM_1" in got, "the warning must name the item"
            case("citing_commit_that_never_touches_the_item_file_warns", _undoc_case)

            # ---- the fix: a later commit citing the same ID DOES touch the item
            # file -> the warning must clear, matching this session's own
            # BUILDING_THEFT_HAULER_1 correction ----------------------------------
            def _fixed_case():
                _commit(TMP, "infrastructure/state/items/FAKE_ITEM_1.md",
                        "# FAKE_ITEM_1\n\nbuilt, see the commit.\n",
                        "FAKE_ITEM_1: correct the record, it was already built")
                got = cli._undocumented_work_warning("FAKE_ITEM_1")
                assert got is None, "once ANY citing commit touches the item file, the warning must clear: got %r" % got
            case("a_later_commit_touching_the_item_file_clears_the_warning", _fixed_case)

            # ---- prefix safety: FAKE_ITEM_1's own commits must not bleed into
            # FAKE_ITEM_10's check (both share the "FAKE_ITEM_1" prefix) ---------
            def _prefix_case():
                got = cli._undocumented_work_warning("FAKE_ITEM_10")
                assert got is None, ("FAKE_ITEM_1's commits must not satisfy or trigger a check for the "
                                      "DIFFERENT id FAKE_ITEM_10 (colon-anchored match): got %r" % got)
            case("prefix_collision_FAKE_ITEM_1_does_not_match_FAKE_ITEM_10", _prefix_case)

            # ---- a body-only mention (not the subject-line convention) is a
            # known, accepted false-positive shape - documented, not silently
            # assumed away ----------------------------------------------------
            def _body_mention_case():
                _commit(TMP, "docs/notes.md", "notes\n",
                        "unrelated subject\n\nsaw FAKE_ITEM_2: mentioned in passing here too")
                got = cli._undocumented_work_warning("FAKE_ITEM_2")
                assert got is not None, ("a body-line citation is expected to still trigger the heuristic "
                                          "(documented limitation, not a silent gap): got %r" % got)
            case("body_only_citation_still_triggers_the_documented_heuristic", _body_mention_case)
        finally:
            model.ROOT, model.ITEMS = real_root, real_items
    finally:
        shutil.rmtree(TMP, ignore_errors=True)

    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(HERE))  # so `import rimflow.cli` resolves
    sys.exit(main())
