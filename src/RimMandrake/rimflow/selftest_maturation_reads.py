#!/usr/bin/env python3
"""Offline selftest of maturation.py's reads: one test per promise on design/specs/2026-11-19-maturation-reads/
boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_maturation_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_maturation_reads.py --only t_x ...  those alone
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_maturation_reads_")
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


def t_absent_only_when_measured():
    """_absent: True only for a path measured absent; a stat that fails another way is not absence."""
    f = write("here.txt", "x")
    check(M._absent(os.path.join(TMP, "gone.txt")) is True, "a missing path is absent")
    check(M._absent(f) is False, "a present path is not absent")
    check(M._absent(os.path.join(f, "under")) is False, "a path under a file (the stat fails) is not absent")


def t_mod_json_read_names_its_failure():
    """read_json(root, mod, p): (None, "no file") for an absent file, (None, "unreadable JSON") for one that does not
    parse, (value, None) for one that does."""
    write("design/concepts/PlantedMod/good.json", '{"a": 1}')
    write("design/concepts/PlantedMod/bad.json", "{nope")
    got = [M.read_json(TMP, "PlantedMod", p) for p in ("absent.json", "bad.json", "good.json")]
    check(got == [(None, "no file"), (None, "unreadable JSON"), ({"a": 1}, None)], "three answers, three readings", got)


def t_unread_ledger_endings_is_none():
    """ledger_live_endings: None when the ledger folder or a shard in it cannot be read; a read shard with no notes
    reads 0 endings."""
    root = os.path.join(TMP, "repo")
    check(M.ledger_live_endings(root, ["X_ITEM"]) is None, "no ledger folder reads None")
    ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(os.path.join(ev, "BENCH.jsonl"))         # a shard that cannot be read
    check(M.ledger_live_endings(root, ["X_ITEM"]) is None, "an unreadable shard reads None")
    os.rmdir(os.path.join(ev, "BENCH.jsonl"))
    write(os.path.relpath(os.path.join(ev, "BENCH.jsonl"), TMP), "")
    got = M.ledger_live_endings(root, ["X_ITEM"])
    check(isinstance(got, dict) and (got.get("X_ITEM") or {}).get("ends") == [], "a read empty shard is 0 endings", got)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_absent_only_when_measured, t_mod_json_read_names_its_failure, t_unread_ledger_endings_is_none):
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
    print("PASS selftest_maturation_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
