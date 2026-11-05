#!/usr/bin/env python3
"""selftest_scratch_reap_self_mentions.py -- a ledger note on the cleaner's own item that lists the session dirs it
refused must not pin them (the refusal wrote the note, the note renewed the refusal for 7 more days). A recent note on
any other item still pins; an old one does not; an undatable one holds."""
import json
import sys
import time
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402

now = time.time()
recent = dt.datetime.fromtimestamp(now - 3600, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
old = dt.datetime.fromtimestamp(now - 30 * 86400, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
F = []


def line(i, ts):
    return json.dumps({"id": i, "ts": ts, "text": "x"})


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


ck(not R.mention_blocks("BENCH.jsonl", line("REAPER_FIX_OWN_SELFTEST_LITTERS_FAKE_SAVES", recent), now), "recent note on a REAPER_ item does not pin")
ck(not R.mention_blocks("BENCH.jsonl", line("OPS_SCRATCH_DIRT_MEASURE_AT_END_RVNI", recent), now), "recent note on an OPS_SCRATCH_ item does not pin")
ck(not R.mention_blocks("BENCH.jsonl", json.dumps({"seat": "DISPATCHER", "id": "RIMFLOW_V3_BUILD_DISPATCHER_FIRST", "ts": recent, "text": "dispatcher alarm : scratch cleaner, end of run: session_dirs 466"}), now), "the Dispatcher relay of the cleaner alarm does not pin")
ck(R.mention_blocks("BENCH.jsonl", json.dumps({"seat": "DISPATCHER", "id": "X_Y_Z", "ts": recent, "text": "restart_verified"}), now), "another Dispatcher note still pins")
ck(R.mention_blocks("BENCH.jsonl", line("CRACKEDLANDS_FULL_RENAME_1", recent), now), "recent note on another item pins")
ck(not R.mention_blocks("BENCH.jsonl", line("CRACKEDLANDS_FULL_RENAME_1", old), now), "30-day-old note does not pin")
ck(R.mention_blocks("BENCH.jsonl", "not json", now), "an undatable line holds")
ck(R.mention_blocks("BENCH.jsonl", "[1]", now), "a non-object line holds")
print("%s: %d failure(s)" % ("FAIL" if F else "PASS", len(F)))
sys.exit(1 if F else 0)
