#!/usr/bin/env python3
"""Selftest for repair_torn_art_events.py on temp files."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import repair_torn_art_events as R

FAILS = []


def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        FAILS.append(m)


G = b'{"a":1}\n{"b":2}\n'
d = Path(tempfile.mkdtemp(prefix="rtae_"))
(d / "archive").mkdir()
(d / "CLEAN.jsonl").write_bytes(G)
(d / "TORN.jsonl").write_bytes(G + b'{"c":3,"x":"hal')
(d / "archive" / "ARCH.0001.20260101_20260102.jsonl").write_bytes(G + b'{"c"')
(d / "MID.jsonl").write_bytes(b'{"a":1}\nGARBAGE\n{"b":2}\n')

check(R.repair(d, False) == 1, "dry run exits 1 (mid-file present)")
check((d / "TORN.jsonl").read_bytes().endswith(b'"hal') and not (d / "_torn").exists(), "dry run writes nothing")
rc = R.repair(d, True, "T1")
check(rc == 1, "apply still exits 1 because of mid-file")
check((d / "TORN.jsonl").read_bytes() == G, "torn tail truncated to last good line")
q = d / "_torn" / "TORN.jsonl.T1.txt"
check(q.exists() and q.read_bytes() == b'{"c":3,"x":"hal', "fragment quarantined byte-exact")
check((d / "archive" / "ARCH.0001.20260101_20260102.jsonl").read_bytes() == G, "archive shard repaired")
check((d / "_torn" / "archive.ARCH.0001.20260101_20260102.jsonl.T1.txt").read_bytes() == b'{"c"', "archive fragment quarantined")
check((d / "MID.jsonl").read_bytes() == b'{"a":1}\nGARBAGE\n{"b":2}\n', "mid-file corruption untouched")
check((d / "CLEAN.jsonl").read_bytes() == G, "clean file untouched")
(d / "MID.jsonl").unlink()
check(R.repair(d, True, "T2") == 0, "all clean after repair exits 0")
# torn tail that ends with a newline is still the final line
(d / "NL.jsonl").write_bytes(G + b'{"z":\n')
R.repair(d, True, "T3")
check((d / "NL.jsonl").read_bytes() == G, "bad final line with newline truncated")
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
