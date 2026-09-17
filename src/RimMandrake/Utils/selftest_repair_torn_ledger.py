#!/usr/bin/env python3
"""Selftest for repair_torn_ledger.py. Never touches the real ledger — every
case builds its own throwaway file under a tmp directory and points `repair()`
and `find_bad_lines()` at that, never at the module's hardcoded LEDGER path."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repair_torn_ledger as rtl  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append((name, detail))


def valid_lines(n=5):
    return [json.dumps({"seat": "FOUNDRY", "event": "note", "id": f"X_{i}", "ts": f"t{i}"}) + "\n"
            for i in range(n)]


def write(path, lines):
    path.write_text("".join(lines), encoding="utf-8")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_repair_torn_ledger_"))
    try:
        # 1. A clean file has nothing to repair, in dry-run or --apply.
        p = tmp / "clean.jsonl"
        write(p, valid_lines(5))
        rc = rtl.repair(p, apply=False, owner_said=None, backup_dir=tmp / "backups1")
        check("clean file: dry-run rc=0", rc == 0)
        check("clean file: unchanged", p.read_text() == "".join(valid_lines(5)))

        # 2. The exact incident shape: git-stash conflict markers, dry-run
        #    reports but does not write.
        p = tmp / "conflict.jsonl"
        lines = valid_lines(2) + ["<<<<<<< Updated upstream\n"] + valid_lines(2) \
            + ["=======\n"] + valid_lines(1) + [">>>>>>> Stashed changes\n"]
        write(p, lines)
        before = p.read_text()
        rc = rtl.repair(p, apply=False, owner_said=None, backup_dir=tmp / "backups2")
        check("conflict markers: dry-run rc=0", rc == 0)
        check("conflict markers: dry-run writes nothing", p.read_text() == before)

        # 3. --apply without --owner-said refuses and writes nothing.
        rc = rtl.repair(p, apply=True, owner_said=None, backup_dir=tmp / "backups3")
        check("apply w/o owner-said: refuses (rc!=0)", rc != 0)
        check("apply w/o owner-said: writes nothing", p.read_text() == before)
        rc = rtl.repair(p, apply=True, owner_said="   ", backup_dir=tmp / "backups3b")
        check("apply w/ blank owner-said: refuses (rc!=0)", rc != 0)

        # 4. --apply with --owner-said actually repairs: markers gone, every
        #    real line kept, backup written, result fully valid JSON.
        backup_dir = tmp / "backups4"
        rc = rtl.repair(p, apply=True, owner_said="test authorization", backup_dir=backup_dir)
        check("apply: rc=0", rc == 0)
        result_lines = p.read_text().splitlines()
        check("apply: marker lines gone", not any(
            l in ("<<<<<<< Updated upstream", "=======", ">>>>>>> Stashed changes")
            for l in result_lines))
        check("apply: exactly 5 real lines kept (2+2+1)", len(result_lines) == 5)
        check("apply: every kept line still parses",
              all(_parses(l) for l in result_lines))
        backups = list(backup_dir.glob("*.bak"))
        check("apply: exactly one backup written", len(backups) == 1)
        check("apply: backup holds the ORIGINAL (still-conflicted) content",
              backups and "<<<<<<< Updated upstream" in backups[0].read_text())

        # 5. A file with only valid lines removed around markers must not
        #    lose or reorder any real event — content-level check, not just
        #    count, in case a future refactor swaps two lines by accident.
        p2 = tmp / "order.jsonl"
        real = [json.dumps({"seat": "FOUNDRY", "event": "note", "id": f"K{i}"}) + "\n"
                for i in range(4)]
        write(p2, [real[0], real[1], "<<<<<<< Updated upstream\n", real[2],
                   "=======\n", real[3], ">>>>>>> Stashed changes\n"])
        rtl.repair(p2, apply=True, owner_said="order test", backup_dir=tmp / "backups5")
        check("apply: real events kept in original order",
              p2.read_text().splitlines() == [r.rstrip("\n") for r in real])

        # 6. More bad lines than MAX_BAD_LINES refuses outright, writes nothing.
        p3 = tmp / "toomany.jsonl"
        junk = [f"not json at all {i}\n" for i in range(rtl.MAX_BAD_LINES + 5)]
        write(p3, valid_lines(2) + junk)
        before3 = p3.read_text()
        rc = rtl.repair(p3, apply=True, owner_said="try anyway", backup_dir=tmp / "backups6")
        check("too many bad lines: refuses (rc!=0)", rc != 0)
        check("too many bad lines: writes nothing", p3.read_text() == before3)

        # 7. A nonexistent file is a clean refusal, not a crash.
        rc = rtl.repair(tmp / "does_not_exist.jsonl", apply=False, owner_said=None,
                         backup_dir=tmp / "backups7")
        check("missing file: refuses (rc!=0), no traceback", rc != 0)

        # 8. This tool's own path is the REAL LEDGER path constant -- guard
        #    against a future edit accidentally repointing it at something
        #    outside infrastructure/state/ledger/.
        check("LEDGER constant still points at the real ledger path",
              str(rtl.LEDGER).replace("\\", "/").endswith(
                  "infrastructure/state/ledger/events.jsonl"))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = len(PASS) + len(FAIL)
    print(f"{len(PASS)}/{total} passed")
    for name, detail in FAIL:
        print(f"  FAIL: {name}  {detail}")
    return 0 if not FAIL else 1


def _parses(line):
    try:
        json.loads(line)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
