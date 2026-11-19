#!/usr/bin/env python3
"""selftest_scratch_reap_session_stamp.py — a closed item's own `session` stamp does not pin its session dir
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH, spec point 3). Measured 2026-11-16: session_stale 203,
raised by sessions every detached helper's claim/start event names in its `"session": <uuid>` field; the ledger mention
held each for MENTION_DAYS (7) after the dir went stale at 24 h, so each was refused for six days by design.

Proves: a recent event whose only mention is its `session` field does not pin once its item is closed; it still pins
while the item is open, when the event's text also names the session, and when no needle is given (the old call).
Pure: a temp tree shaped like the repo; no ledger is read."""
import datetime as dt
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402

F = []


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


now = time.time()
recent = dt.datetime.fromtimestamp(now - 3600, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
U = "44d031a5-88e0-4c82-ac45-9d1da5906ad8"
with tempfile.TemporaryDirectory(prefix="selftest_session_stamp_") as td:
    root = Path(td)
    shard = root / "infrastructure" / "state" / "ledger" / "events" / "BENCH.jsonl"
    items = root / "infrastructure" / "state" / "items"
    (items / "closed").mkdir(parents=True)
    shard.parent.mkdir(parents=True)
    (items / "closed" / "DONE_ITEM_ONE_TWO.md").write_text("x")
    (items / "OPEN_ITEM_ONE_TWO.md").write_text("x")

    def ev(item, text="detached run", event="claim"):
        return json.dumps({"seat": "BENCH", "event": event, "id": item, "session": U, "text": text, "ts": recent})

    def blocks(line, needle):
        try:
            return R.mention_blocks(str(shard), line, now, needle)
        except TypeError as e:
            return "crash: %s" % e

    got = blocks(ev("DONE_ITEM_ONE_TWO"), U)
    ck(got is False, "a closed item's claim stamp does not pin its session (%r)" % got)
    got = blocks(ev("DONE_ITEM_ONE_TWO", event="start"), U)
    ck(got is False, "nor its start stamp (%r)" % got)
    got = blocks(ev("OPEN_ITEM_ONE_TWO"), U)
    ck(got is True, "an open item's stamp still pins (%r)" % got)
    got = blocks(ev("DONE_ITEM_ONE_TWO", text="resume from session %s" % U), U)
    ck(got is True, "a closed item's event that names the session in its text still pins (%r)" % got)
    got = blocks(ev("UNKNOWN_ITEM_ONE_TWO"), U)
    ck(got is True, "an item with no prose and no ledger end still pins (%r)" % got)

    # an item that lives only in the ledger: its last lifecycle event decides
    def led(item, event, ts):
        return json.dumps({"seat": "BENCH", "event": event, "id": item, "ts": ts})
    t0, t1, t2 = (dt.datetime.fromtimestamp(now - k, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") for k in (9000, 1800, 100))   # the stamp is 3600 s old: close after it
    lines = [ev("LEDGER_ONLY_DONE_ITEM"), ev("LEDGER_ONLY_REOPENED_ITEM"),
             led("LEDGER_ONLY_DONE_ITEM", "claim", t0), led("LEDGER_ONLY_DONE_ITEM", "close", t1),
             led("LEDGER_ONLY_DONE_ITEM", "note", t2),
             led("LEDGER_ONLY_REOPENED_ITEM", "close", t1), led("LEDGER_ONLY_REOPENED_ITEM", "live", t2)]
    shard.write_text("\n".join(lines) + "\n")
    saved = (R._CORPUS, R._VOCAB, R._ENDED if hasattr(R, "_ENDED") else None)
    R._CORPUS, R._VOCAB = [(str(shard), shard.read_text())], None
    try:
        got = blocks(ev("LEDGER_ONLY_DONE_ITEM"), U)
        ck(got is False, "a ledger-only item whose last lifecycle event is close does not pin (%r)" % got)
        got = blocks(ev("LEDGER_ONLY_REOPENED_ITEM"), U)
        ck(got is True, "one with a live event after its close still pins (%r)" % got)
    finally:
        R._CORPUS, R._VOCAB = saved[0], saved[1]
        if hasattr(R, "_ENDED"):
            R._ENDED = saved[2]
    ck(R.mention_blocks(str(shard), ev("DONE_ITEM_ONE_TWO"), now) is True, "without a needle the old answer stands")

print("%s: %d failure(s)" % ("FAIL" if F else "PASS", len(F)))
sys.exit(1 if F else 0)
