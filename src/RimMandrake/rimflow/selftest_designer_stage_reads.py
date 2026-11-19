#!/usr/bin/env python3
"""Offline selftest of designer_stage.py's reads: one test per promise on design/specs/2026-11-19-designer-stage-reads/
boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_designer_stage_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_designer_stage_reads.py --only t_x ...  those alone
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_designer_stage_reads_")
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def write(rel, text):
    p = os.path.join(TMP, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def t_absent_is_default_unparseable_refuses():
    """read_json: an absent file is the caller's default; a file that does not parse raises Refused, never a default."""
    check(DS.read_json(os.path.join(TMP, "absent.json")) is None, "absent reads the default None")
    check(DS.read_json(os.path.join(TMP, "absent.json"), {}) == {}, "absent reads the default given")
    bad = write("bad.json", "{not json")
    try:
        got = DS.read_json(bad, {})
        check(False, "an unparseable file refuses", got)
    except DS.Refused:
        check(True, "an unparseable file refuses")


def t_unread_owner_shard_is_none():
    """owner_uncited: None when no copy of OWNER.jsonl can be read, [] when one was read and nothing is uncited."""
    real = DS.CT.owner_lines
    try:
        DS.CT.owner_lines = lambda *a: None
        got = DS.owner_uncited(TMP, "RIMMANDRAKE_PLANT_A_READ_FOR_THE_TEST", TMP)
        check(got is None, "an unreadable shard reads None", got)
        DS.CT.owner_lines = lambda *a: []
        got = DS.owner_uncited(TMP, "RIMMANDRAKE_PLANT_A_READ_FOR_THE_TEST", TMP)
        check(got == [], "a read shard with nothing for the item reads []", got)
    finally:
        DS.CT.owner_lines = real


def t_unread_ledger_is_said_in_the_packet():
    """built_evidence: a ledger done_items cannot read is a note "ledger UNMEASURED", not a mod with no done items."""
    real = DS.done_items
    try:
        DS.done_items = lambda repo: None
        refs, notes = DS.built_evidence(TMP, "PlantedMod")
        check(any("ledger UNMEASURED" in n for n in notes), "the unread ledger is named in the notes", notes)
        DS.done_items = lambda repo: {}
        refs, notes = DS.built_evidence(TMP, "PlantedMod")
        check(not any("ledger" in n for n in notes), "a read ledger with no done items says nothing of it", notes)
    finally:
        DS.done_items = real


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_absent_is_default_unparseable_refuses, t_unread_owner_shard_is_none, t_unread_ledger_is_said_in_the_packet):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_designer_stage_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
