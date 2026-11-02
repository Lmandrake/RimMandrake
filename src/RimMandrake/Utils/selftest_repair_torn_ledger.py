#!/usr/bin/env python3
"""Selftest for repair_torn_ledger.py. Never touches the real ledger — every
case builds its own throwaway file under a tmp directory and points `repair()`
and `find_bad_lines()` at that, never at the module's hardcoded LEDGER path."""
import fcntl
import json
import os
import shutil
import sys
import tempfile
import threading
import time
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
        # 1. A clean file has nothing to repair (dry-run).
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

        # 9. rimflow writes ensure_ascii=False, so a valid event may hold a raw
        #    U+2028 / U+0085 / form-feed. str.splitlines() splits there and the
        #    repair would delete two halves of a GOOD event. Only "\n" ends a line.
        p4 = tmp / "unicode.jsonl"
        ev = json.dumps({"seat": "FOUNDRY", "id": "U", "text": "a\u2028b\x85c\x0cd"},
                        ensure_ascii=False) + "\n"
        p4.write_bytes((ev + "<<<<<<< x\n" + ev).encode("utf-8"))
        rc = rtl.repair(p4, apply=True, owner_said="unicode test", backup_dir=tmp / "backups9")
        check("raw U+2028 inside a valid event: both events survive",
              p4.read_bytes() == (ev + ev).encode("utf-8"), repr(p4.read_bytes()[:80]))

        # 10. A write torn INSIDE a multibyte char (an em-dash) must be repaired, not crash the
        #     strict UTF-8 decode; the backup keeps the original bytes exactly.
        p5 = tmp / "torn_multibyte.jsonl"
        good = (json.dumps({"seat": "FOUNDRY", "id": "M", "text": "em — dash"}, ensure_ascii=False) + "\n").encode("utf-8")
        cut = good[:good.index("—".encode("utf-8")) + 1]          # first byte of the 3-byte dash only
        orig = good + cut + b"\n" + good
        p5.write_bytes(orig)
        rc = rtl.repair(p5, apply=True, owner_said="torn multibyte test", backup_dir=tmp / "backups10")
        baks = list((tmp / "backups10").glob("*.bak"))
        check("torn multibyte line: removed, both good events survive",
              rc == 0 and p5.read_bytes() == good + good, repr(p5.read_bytes()[:80]))
        check("torn multibyte line: backup holds the original bytes",
              len(baks) == 1 and baks[0].read_bytes() == orig)

        # 11. A seat appending while the repair runs must not lose its event. The repair takes the same LOCK_EX
        #     rimflow.model.append() takes; here the test holds it as the "appender", appends a good event, then lets
        #     go — the repair must have waited and must keep that event.
        p6 = tmp / "concurrent.jsonl"
        write(p6, valid_lines(2) + ["<<<<<<< x\n"])
        late = json.dumps({"seat": "FOUNDRY", "event": "note", "id": "LATE", "ts": "t9"}) + "\n"
        fd = os.open(p6, os.O_WRONLY | os.O_APPEND)
        fcntl.flock(fd, fcntl.LOCK_EX)
        rcs = []
        t = threading.Thread(target=lambda: rcs.append(
            rtl.repair(p6, apply=True, owner_said="lock test", backup_dir=tmp / "backups11")))
        t.start()
        time.sleep(0.3)
        check("concurrent append: repair waits for the appender's lock", t.is_alive() and not rcs)
        os.write(fd, late.encode("utf-8"))
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        t.join(10)
        check("concurrent append: the late event survives the repair",
              rcs == [0] and p6.read_text(encoding="utf-8") == "".join(valid_lines(2)) + late,
              repr((rcs, p6.read_text(encoding="utf-8")[-80:])))

        # 12. rimflow append() does not check the tail ends in "\n": a write torn at the tail gets the NEXT good
        #     event glued onto the same line. Only the fragment may go; the glued event must survive, in place.
        p7 = tmp / "glued.jsonl"
        a, b, c = valid_lines(3)
        torn = a[:len(a) // 2]                                   # unterminated half of an event
        p7.write_text(a + torn + b + c, encoding="utf-8")
        rc = rtl.repair(p7, apply=True, owner_said="glued test", backup_dir=tmp / "backups12")
        check("glued event after a torn fragment: kept, fragment dropped, order kept",
              rc == 0 and p7.read_text(encoding="utf-8") == a + b + c, repr(p7.read_text(encoding="utf-8")[-160:]))
        check("salvage: a conflict marker yields nothing", rtl.salvage(">>>>>>> Stashed changes") is None)
        check("salvage: a bare torn fragment yields nothing", rtl.salvage(torn.rstrip("\n")) is None)
        check("salvage: a nested-object fragment is not mistaken for an event",
              rtl.salvage('{"seat":"X","meta":{"a":1') is None)
        check("salvage: a fragment torn just after a nested object does not invent an event",
              rtl.salvage('{"seat":"X","meta":{"a":1}') is None)

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
