#!/usr/bin/env python3
"""conductor_log_receipt.py -- proof that a test's fake alarms left the real Conductor log and stay out
(SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG).

    python3 src/RimMandrake/Utils/conductor_log_receipt.py record     # after a removal, from the backup and the log
    python3 src/RimMandrake/Utils/conductor_log_receipt.py check      # exit 0 clean, 1 fixture or bad receipt, 2 log lost

A bare `! grep -q` over the log is vacuous: grep exits 2 on an absent file and the negation turns that green. So `check`
reads the log itself and tells three states apart:
  VISIBLE       the log holds text: any fixture line is a failure.
  LOST          the log is absent or empty, yet its folder's other file is there: a failure, never a clean result.
  NOT VISIBLE   the folder itself is masked (a walled checker's empty mount): says so, and proves only the committed
                receipt, which is a record of the removal and not a reading of the log.
The receipt holds the removed lines verbatim and the hashes of the log before and after. `record` writes it only when
the backup minus the fixture entries is exactly what the log starts with, so nothing else was removed.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOG = Path("/mnt/d/ClaudeWork/rimmandrake/conductor/log.md")
BACKUP = Path("/mnt/d/ClaudeWork/rimmandrake/backups/conductor_log/log_before_SELFTEST_ALARM_FIX.md")
RECEIPT = ROOT / "infrastructure/state/facts/conductor_log_fixture_removal.json"
SIBLING = "running_state.json"      # always beside the real log; a masked folder has neither
FIXTURE = re.compile(rb"^- 2026-11-07T\d\d:\d\d:\d\dZ ops_watch ALARM OPS_RED_OVERDUE_CHASE_[A-Z0-9]+: .*src/x/selftest_")
MARK = b"src/x/selftest_"           # wider than FIXTURE on purpose: any trace in the log is a failure
OK, DIRTY, LOST = 0, 1, 2


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strip_fixtures(data):
    """-> (data without each fixture line and the one blank line after it, the removed fixture lines)."""
    kept, removed, lines, i = [], [], data.splitlines(keepends=True), 0
    while i < len(lines):
        if FIXTURE.match(lines[i]):
            removed.append(lines[i])
            i += 1
            if i < len(lines) and not lines[i].strip():
                i += 1
            continue
        kept.append(lines[i])
        i += 1
    return b"".join(kept), removed


def receipt_problems(rec):
    """-> what is wrong with a receipt on its own terms; empty when it holds together."""
    lines = rec.get("removed") or []
    out = []
    if not lines:
        out.append("it lists no removed lines")
    if rec.get("removed_count") != len(lines):
        out.append("removed_count %r but %d lines listed" % (rec.get("removed_count"), len(lines)))
    out += ["not fixture-shaped: %s" % s[:100] for s in lines if not FIXTURE.match(s.encode("utf-8"))]
    if rec.get("removed_sha256") != sha("".join(lines).encode("utf-8")):
        out.append("removed_sha256 does not hash the listed lines")
    if rec.get("before_sha256") == rec.get("after_sha256"):
        out.append("before and after hashes are the same: nothing was removed")
    if rec.get("before_bytes", 0) - rec.get("after_bytes", 0) < sum(len(s.encode("utf-8")) for s in lines):
        out.append("the log shrank by less than the listed lines")
    return out


def check(log=LOG, receipt=RECEIPT, out=print):
    """-> an exit code, after saying which state it found."""
    try:
        rec = json.loads(Path(receipt).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        out("FAIL receipt unreadable: %s" % e)
        return DIRTY
    problems = receipt_problems(rec)
    for p in problems:
        out("FAIL receipt: %s" % p)
    log = Path(log)
    try:
        data = log.read_bytes()
    except OSError:
        data = b""
    if not data.strip():
        if (log.parent / SIBLING).exists():
            out("FAIL LOST: %s is absent or empty and its folder is visible" % log)
            return LOST
        out("NOT VISIBLE: %s's folder is masked here, so the log itself was NOT read" % log)
        out("receipt only: %d fixture lines recorded removed, before %s, after %s"
            % (len(rec.get("removed") or []), rec.get("before_sha256", "?")[:12], rec.get("after_sha256", "?")[:12]))
        return DIRTY if problems else OK
    hits = [ln for ln in data.splitlines() if MARK in ln]
    for ln in hits[:3]:
        out("FAIL fixture line in the log: %s" % ln[:120].decode("utf-8", "replace"))
    if hits:
        return DIRTY
    out("VISIBLE: %s read, %d bytes, %d lines, 0 fixture lines" % (log, len(data), len(data.splitlines())))
    return DIRTY if problems else OK


def record(log=LOG, backup=BACKUP, receipt=RECEIPT, out=print):
    """Write the receipt, or refuse when the backup minus its fixtures is not what the log starts with."""
    before, now = Path(backup).read_bytes(), Path(log).read_bytes()
    after, removed = strip_fixtures(before)
    if not removed:
        out("REFUSED: the backup holds no fixture lines")
        return DIRTY
    if not now.startswith(after):
        out("REFUSED: the log does not start with the backup minus its fixtures, so something else changed")
        return DIRTY
    Path(receipt).write_text(json.dumps({
        "item": "SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG",
        "removed_count": len(removed),
        "removed_sha256": sha(b"".join(removed)),
        "before_sha256": sha(before), "before_bytes": len(before),
        "after_sha256": sha(after), "after_bytes": len(after),
        "removed": [s.decode("utf-8") for s in removed],
    }, indent=1) + "\n", encoding="utf-8")
    out("recorded %d removed lines: %s" % (len(removed), receipt))
    return OK


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verb", choices=("check", "record"))
    return check() if ap.parse_args().verb == "check" else record()


if __name__ == "__main__":
    sys.exit(main())
