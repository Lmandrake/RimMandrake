#!/usr/bin/env python3
"""selftest_priority_list: DI3 by planted fault on the real paths.

    python3 src/RimMandrake/rimflow/selftest_priority_list.py

The ring: `cli.py next --peek` as a process. The writer: what it refuses, and that a finished entry drops by itself.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
TMP = Path(tempfile.mkdtemp(prefix="selftest_priority_list_"))
os.environ.pop("RM_PRIORITY_LIST", None)

from rimflow import priority_list as PL  # noqa: E402

FAILS = []
RAN = 0
T0 = 1793500000.0
CLI = str(HERE / "cli.py")


def check(name, good, detail=None):
    global RAN
    RAN += 1
    print("%s %s" % ("ok  " if good else "FAIL", name))
    if not good:
        FAILS.append(name)
        print("     ", str(detail)[:700])


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def filed(iid, ts="2026-10-01T00:00:00Z", owner="BENCH", **kw):
    d = dict(seat="BENCH", event="file", id=iid, title="t", kind="task", ts=ts, needs="offline", target="v1", **kw)
    d["for"] = owner
    return d


def doc(entries, t=T0, by="Conductor"):
    return {"set_at": iso(t), "set_by": by, "entries": entries}


def entry(iid, mod="ModA"):
    return {"id": iid, "reading": {"mod": mod}}


def put(root, d):
    p = Path(PL.path(root))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(d if isinstance(d, str) else json.dumps(d), encoding="utf-8")


# ---------------------------------------------------------------- the ring: `next --peek` as the Dispatcher runs it
def ring():
    d = TMP / "ring"
    (d / "events").mkdir(parents=True)
    led = d / "events.jsonl"
    ids = ("ITEM_RANKED_OLD", "ITEM_ROWLESS", "ITEM_LISTED")
    evs = [filed("ITEM_RANKED_OLD", "2026-01-01T00:00:00Z", row="1"), filed("ITEM_ROWLESS", "2026-02-01T00:00:00Z"),
           filed("ITEM_LISTED", "2026-10-30T00:00:00Z", row="9"), filed("ITEM_PROPOSED", "2026-10-31T00:00:00Z")]
    evs += [dict(seat="BENCH", event="claim", id=i, ts="2026-10-31T01:00:00Z") for i in ids]
    (d / "events" / "BENCH.jsonl").write_text("".join(json.dumps(e) + "\n" for e in evs), encoding="utf-8")
    env = dict(os.environ, RIMFLOW_LEDGER=str(led), RM_PRIORITY_LIST=str(d / "priority_list.json"))

    def peek():
        r = subprocess.run([sys.executable, CLI, "next", "--seat", "BENCH", "--peek"], env=env, capture_output=True, text=True)
        lines = [ln.split()[0] for ln in r.stdout.splitlines() if ln.startswith("ITEM_")]
        return lines[0] if lines else (r.stdout + r.stderr)[-400:]

    check("no list: the ring peeks today's first", peek() == "ITEM_RANKED_OLD", peek())
    Path(env["RM_PRIORITY_LIST"]).write_text(json.dumps(doc([entry("ITEM_LISTED")])), encoding="utf-8")
    check("the ring peeks the listed item", peek() == "ITEM_LISTED", peek())
    Path(env["RM_PRIORITY_LIST"]).write_text(json.dumps(doc([{"row": "9", "reading": {"mod": "ModA"}}])), encoding="utf-8")
    check("a row name on the list orders that row's items", peek() == "ITEM_LISTED", peek())
    Path(env["RM_PRIORITY_LIST"]).write_text(json.dumps(doc([entry("ITEM_PROPOSED")])), encoding="utf-8")
    check("a listed proposed item beats a ranked ready one", peek() == "ITEM_PROPOSED", peek())


# ---------------------------------------------------------------- the writer
def writer():
    d = TMP / "writer"
    d.mkdir()
    ok_list = [entry("ITEM_%d" % n) for n in range(29)]
    PL.write(d, ok_list, "Conductor")
    check("the writer takes 29 entries and stamps set_at", PL.load(d)["state"] == "ok" and PL.load(d)["doc"]["set_at"])
    before = Path(PL.path(d)).read_text(encoding="utf-8")
    for name, es, by in (("31 entries", [entry("ITEM_%d" % n) for n in range(31)], "Conductor"),
                         ("30 entries, the list is under 30", [entry("ITEM_%d" % n) for n in range(30)], "Conductor"),
                         ("an entry with no reading", [{"id": "X"}], "Conductor"),
                         ("a reading outside the repo", [{"id": "X", "reading": {"file": "../x.json", "key": "a"}}], "Conductor"),
                         ("a duplicate", [entry("X"), entry("X")], "Conductor"),
                         ("an id that is no text", [{"id": [], "reading": {"mod": "ModA"}}], "Conductor"),
                         ("an entry naming id and row", [{"id": "A", "row": None, "reading": {"mod": "ModA"}}], "Conductor"),
                         ("another writer", [entry("X")], "FOUNDRY")):
        try:
            PL.write(d, es, by)
            refused = False
        except ValueError:
            refused = True
        check("the writer refuses %s" % name, refused and Path(PL.path(d)).read_text(encoding="utf-8") == before)
    r = subprocess.run([sys.executable, str(HERE / "priority_list.py"), "add", "NO_SUCH_ITEM_X", "--mod", "ModA", "--by", "Conductor"],
                       env=dict(os.environ, RM_PRIORITY_LIST=str(TMP / "writer" / "cli.json")), capture_output=True, text=True)
    check("the tool refuses an item the ledger does not hold", r.returncode == 1 and "NO_SUCH_ITEM_X" in r.stderr
          and not (TMP / "writer" / "cli.json").exists(), r.stdout + r.stderr)
    # `add` beside a finished entry drops that entry by itself (it once refused the whole add until a full `set`)
    led = d / "events.jsonl"
    (d / "events").mkdir()
    (d / "events" / "BENCH.jsonl").write_text("".join(json.dumps(e) + "\n" for e in (
        filed("ITEM_DONE_A"), filed("ITEM_OPEN_B"), filed("ITEM_NEW_C"),
        dict(seat="BENCH", event="close", id="ITEM_DONE_A", sha="abc", ts="2026-10-02T00:00:00Z"))), encoding="utf-8")
    lst = d / "add.json"
    lst.write_text(json.dumps(doc([entry("ITEM_DONE_A"), entry("ITEM_OPEN_B")], by="Conductor")), encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "priority_list.py"), "add", "ITEM_NEW_C", "--mod", "ModA", "--by", "Conductor"],
                       env=dict(os.environ, RM_PRIORITY_LIST=str(lst), RIMFLOW_LEDGER=str(led)), capture_output=True, text=True)
    got = [e.get("id") for e in json.loads(lst.read_text(encoding="utf-8")).get("entries") or []]
    check("add drops a closed entry by itself and names it", r.returncode == 0 and got == ["ITEM_OPEN_B", "ITEM_NEW_C"]
          and "ITEM_DONE_A" in r.stdout, (got, r.stdout + r.stderr))


def main():
    ring()
    writer()
    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_priority_list: %s (%d checks, %d fails)" % ("FAIL" if FAILS else "OK", RAN, len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
