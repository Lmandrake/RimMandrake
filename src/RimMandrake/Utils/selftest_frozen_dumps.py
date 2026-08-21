#!/usr/bin/env python3
"""Selftest for refresh.py's frozen-dump immunity.

⭐ WHY THIS RULE NEEDS A TEST RATHER THAN A COMMENT. The failure it prevents is
invisible and self-inflicting: if the official dump reads `STALE`, the board sits
permanently red, and sooner or later somebody clears the warning by re-freezing —
silently moving the design target that DECIDE and BUILD are both authoring against.
Nothing announces that. A stale warning is loud; a moved target is not.

⚠️ And the mismatch is not an edge case. Every new `Jawa_*` mod moves the live count by
one, so the official dump is drifting from the live list ALL THE TIME, on purpose.

    python3 src/RimMandrake/Utils/selftest_frozen_dumps.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import refresh                                                    # noqa: E402

PASS, FAIL = [], []


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))


def with_registry(lines):
    """Point refresh.registry() at a throwaway file under the repo."""
    d = tempfile.mkdtemp(prefix=".frozen_", dir=os.path.dirname(os.path.dirname(HERE)))
    path = os.path.join(d, "REGISTRY.jsonl")
    open(path, "w", encoding="utf-8").write("".join(lines))
    refresh._registry_path = lambda: path
    return d


# ⚠️ A REAL matching path, not a placeholder. An earlier draft used "…/DefDump", which
# matched nothing — so `t_a_verification_dump_is_never_immune` returned None because the
# PATH failed, not because `frozen` was False, and passed without ever exercising the
# rule it names. A test that passes for the wrong reason is worse than one that fails.
DUMP = ("C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")


def entry(**kw):
    d = {"id": "OFFICIAL-1", "kind": "official", "frozen": True,
         "modlist_count": 578, "path": "RimWorld by Ludeon Studios/DefDump",
         "by": "owner"}
    d.update(kw)
    return json.dumps(d) + "\n"


def t_frozen_entry_matches_by_suffix():
    """An absolute path from another machine must still resolve."""
    d = with_registry([entry()])
    try:
        got = refresh.frozen_entry(
            "C:/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
            "RimWorld by Ludeon Studios/DefDump")
        assert got and got["id"] == "OFFICIAL-1", got
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_verification_dump_is_never_immune():
    """`kind: verification` answers 'does the live game match?' — staleness applies."""
    d = with_registry([entry(id="verify-1", kind="verification", frozen=False,
                             modlist_count=13)])
    try:
        assert refresh.frozen_entry(DUMP) is None, (
            "a verification dump was treated as frozen; it would then never be "
            "reported stale, which is the only thing it is FOR")
        # …and prove the PATH is not what made it None, which is how this test
        # silently passed before.
        d2 = with_registry([entry(id="OFFICIAL-1", kind="official", frozen=True)])
        try:
            assert refresh.frozen_entry(DUMP) is not None, (
                "the path does not match at all, so the frozen=False case above "
                "proved nothing")
        finally:
            shutil.rmtree(d2, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_newest_frozen_entry_wins():
    """The registry is append-only, so a re-freeze is a later line, not an edit."""
    d = with_registry([entry(id="OFFICIAL-1", modlist_count=575),
                       entry(id="OFFICIAL-2", modlist_count=578)])
    try:
        got = refresh.frozen_entry(DUMP)
        assert got and got["id"] == "OFFICIAL-2", got
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_torn_line_is_reported_not_skipped():
    """🔴 Silence here loses a frozen dump's immunity with no symptom at the cause."""
    d = with_registry([entry(), '{"id":"OFFICIAL-2","fro\n'])
    try:
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys;sys.path.insert(0,%r);import refresh;"
             "refresh._registry_path=lambda: %r;refresh.registry()" % (HERE,
                                                                       os.path.join(d, "REGISTRY.jsonl"))],
            capture_output=True, text=True, timeout=30)
        assert "not valid JSON" in r.stdout, (
            "a malformed registry line was skipped silently. The symptom would be "
            "'the official dump went STALE', which points nowhere near the cause. "
            "Got: %r" % r.stdout[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_no_registry_is_not_an_error():
    d = with_registry([])
    try:
        os.unlink(os.path.join(d, "REGISTRY.jsonl"))
        assert refresh.registry() == []
        assert refresh.frozen_entry(DUMP) is None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_shipped_registry_freezes_the_live_dump():
    """The real file, unmocked — the rule has to hold in the repo, not just in a test."""
    got = refresh.frozen_entry(refresh.D_DUMP)
    assert got and got.get("frozen") and got.get("kind") == "official", (
        "the shipped REGISTRY.jsonl does not freeze the live DefDump; it would go "
        "STALE on the next custom mod and demand a ~23-minute load for nothing. "
        "Got: %r" % (got,))


def t_a_replaced_capture_is_not_reported_as_frozen():
    """🔴 A freeze that cannot detect replacement is not a freeze.

    Measured 2026-08-21: the registry froze 2026-08-20T15:08:30Z and the disk
    held 2026-08-21T08:20:20Z. Both were 578 mods, so the mod-count comparison
    — the only one the frozen branch made — saw nothing, and the design target
    moved silently. That is the failure this file's README calls worse than a
    stale warning.
    """
    d = with_registry(['{"id":"T","kind":"official","frozen":true,'
                       '"modlist_count":578,"path":"DefDump",'
                       '"capturedUtc":"2026-08-20T15:08:30Z"}\n'])
    try:
        fe = refresh.frozen_entry("/x/DefDump")
        assert fe, "the test registry did not take"
        assert fe["capturedUtc"] == "2026-08-20T15:08:30Z"
        # the branch must compare capturedUtc, not only the mod count
        src = open(os.path.join(HERE, "refresh.py"), encoding="utf-8").read()
        assert "REPLACED" in src, (
            "refresh.py no longer reports a replaced frozen capture")
        assert 'fe.get("capturedUtc")' in src, (
            "the frozen branch no longer compares capturedUtc, so a re-capture "
            "on the same mod count would pass unnoticed again")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_derived_db_is_outside_the_freeze():
    """`defs.sqlite` lives inside the frozen path and must NOT be frozen —
    it is a pure function of the capture, so rebuilding it cannot move the
    target, and freezing it would freeze its schema bugs."""
    readme = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                          "..", "infrastructure", "state", "dumps", "README.md")
    readme = os.path.normpath(readme)
    if not os.path.exists(readme):
        return
    text = open(readme, encoding="utf-8").read()
    assert "defs.sqlite" in text and "never" in text.lower(), (
        "the README no longer records that the derived db is outside the freeze")


if __name__ == "__main__":
    real = refresh._registry_path
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            if k == "t_the_shipped_registry_freezes_the_live_dump":
                refresh._registry_path = real
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
