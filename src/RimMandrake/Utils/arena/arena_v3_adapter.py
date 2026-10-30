#!/usr/bin/env python3
"""arena_v3_adapter.py - translate v3 rimflow ledger events and testq records into the arena event schema.

ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE; architecture_switch_harness §1.7 ("v3 writes nothing natively").
Adapter code is harness code: it writes through arena_eventlog.HarnessWriter (token-signed), arm "v3".

Mapping (accepted ledger events only; refused ones are skipped, via model.replay(observe=)):
  start   -> pass_start   task=id, detail.agent=seat
  close, implemented
          -> build_end    task=id, sha, detail.builder=seat, detail.via, detail.state_after, detail.done = this
                          event moved the item into `done` (rimflow_metrics.flow["done"] counts that transition,
                          whichever verb caused it: close, verify-of-last-criterion, implemented)
  verify  -> test_end     task=id, sha, verdict=result, detail.tester=seat (the ledger names the seat, not the helper), detail.done as above
testq (result records, jobs for the item): started -> test_start, finished -> test_end, tester "testq:<host>",
  task = job.item, verdict = outcome, detail.job. A testq run is a different agent from any builder by construction.
Not derivable from the ledger: lane (set "v3"), run_id ("v3-ledger" / the testq job id), a test_start for a ledger
verify. The adapter invents nothing for them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402
from rimflow import model  # noqa: E402

ARM = "v3"
LANE = "v3"
LEDGER_RUN = "v3-ledger"


def translate_ledger(events=None) -> list[dict]:
    """-> unsigned records (kwargs for HarnessWriter.emit plus `event`, `ts`), in ledger order."""
    events = model.read() if events is None else events
    out, before = [], {}

    def observe(ev, world, ok):
        iid = ev.get("id")
        it = world.items.get(iid) if iid else None
        prev = before.get(iid)
        if it is not None:
            before[iid] = it.state
        if not ok or ev.get("event") not in ("start", "close", "verify", "implemented") or it is None:
            return
        seat = ev.get("seat") or ev.get("who") or "unknown"
        base = {"ts": ev["ts"], "arm": ARM, "lane": LANE, "run_id": LEDGER_RUN, "task": iid}
        e = ev["event"]
        if e == "start":
            out.append(dict(base, event="pass_start", detail={"agent": seat}))
        elif e in ("close", "implemented"):
            out.append(dict(base, event="build_end", sha=ev.get("sha"),
                            detail={"builder": seat, "via": e, "state_after": it.state,
                                    "done": bool(it.state == "done" and prev != "done")}))
        else:
            out.append(dict(base, event="test_end", sha=ev.get("sha"), verdict=ev.get("result"),
                            detail={"tester": seat, "level": ev.get("level"), "criterion": ev.get("criterion"),
                                    "done": bool(it.state == "done" and prev != "done")}))

    model.replay(events, observe=observe)
    return out


def translate_testq(results: list[dict], jobs: dict | None = None) -> list[dict]:
    jobs = jobs or {}
    out = []
    for r in results:
        jid = r.get("job")
        item = (jobs.get(jid) or {}).get("item") or r.get("item")
        if not (jid and item):
            continue                       # no task to attach it to: not invented
        who = "testq:%s" % (r.get("host") or "unknown")
        base = {"arm": ARM, "lane": (jobs.get(jid) or {}).get("lane") or LANE, "run_id": jid, "task": item}
        if r.get("started"):
            out.append(dict(base, event="test_start", ts=r["started"], detail={"tester": who, "job": jid}))
        if r.get("finished"):
            out.append(dict(base, event="test_end", ts=r["finished"], verdict=r.get("outcome"),
                            detail={"tester": who, "job": jid, "cause": r.get("cause"), "counts": r.get("counts")}))
    return out


def load_testq(directory) -> tuple[list[dict], dict]:
    """Scan a directory tree for testq.job/1 and testq.result/1 json files."""
    results, jobs = [], {}
    for f in sorted(Path(directory).rglob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and d.get("schema") == "testq.result/1":
            results.append(d)
        elif isinstance(d, dict) and d.get("schema") == "testq.job/1":
            jobs[d["id"]] = d
    return results, jobs


def sorted_by_ts(recs):
    return sorted(recs, key=lambda r: A._epoch(r["ts"]))


def write(writer: "L.HarnessWriter", recs: list[dict]) -> int:
    n = 0
    for r in sorted_by_ts(recs):
        r = dict(r)
        ev = r.pop("event")
        arm, lane, run_id = r.pop("arm"), r.pop("lane"), r.pop("run_id")
        writer.emit(arm, ev, lane=lane, run_id=run_id, **r)
        n += 1
    return n


def done_count(recs: list[dict], lo: float, hi: float, via: str | None = None) -> int:
    """Records that moved an item into done, ts in [lo, hi] epoch seconds. via="close" counts only the close verb."""
    return sum(1 for r in recs if r["detail"].get("done") and lo <= A._epoch(r["ts"]) <= hi
               and (via is None or r["detail"].get("via") == via))


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--testq-dir")
    ap.add_argument("--apply", action="store_true", help="write through the harness token (default: count only)")
    a = ap.parse_args(argv)
    recs = translate_ledger()
    if a.testq_dir:
        recs += translate_testq(*load_testq(a.testq_dir))
    print("%d records" % len(recs))
    if a.apply:
        print("wrote %d" % write(L.HarnessWriter(), recs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
