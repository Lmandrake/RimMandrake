#!/usr/bin/env python3
"""selftest_priority_list: DI3 and MI1 by planted fault on the real paths.

    python3 src/RimMandrake/rimflow/selftest_priority_list.py

The pool: relentless's real Effects.pool_order inside a real tick decides the launch. The ring: `cli.py next --peek` as
a process, which is what the Dispatcher runs. The alarms: the real ops_watch.run under the shipped rules, over a throwaway
data clone whose ledger is the real format, down to the alarm handed to the filer and the row in the alarm log.
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
UTILS = HERE.parent / "Utils"
sys.path[:0] = [str(HERE), str(HERE.parent), str(UTILS)]
TMP = Path(tempfile.mkdtemp(prefix="selftest_priority_list_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_STREAMS_BENCH"] = str(TMP / "data")
os.environ.pop("RM_PRIORITY_LIST", None)

import ops_watch as OW  # noqa: E402
import selftest_relentless as SR  # noqa: E402
from rimflow import model, priority_list as PL  # noqa: E402

R = SR.R
FAILS = []
RAN = 0
T0 = 1793500000.0
DAY = 86400.0
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


def doc(entries, t=T0, by="Producer"):
    return {"set_at": iso(t), "set_by": by, "entries": entries}


def entry(iid, mod="ModA"):
    return {"id": iid, "reading": {"mod": mod}}


def put(root, d):
    p = Path(PL.path(root))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(d if isinstance(d, str) else json.dumps(d), encoding="utf-8")


# ---------------------------------------------------------------- the pool: a listed item launches before a ranked one
def pool():
    books = TMP / "books"
    evs = [filed("ITEM_RANKED_OLD", "2026-01-01T00:00:00Z"), filed("ITEM_RAISED", "2026-02-01T00:00:00Z"),
           filed("ITEM_Z_LISTED", "2026-10-30T00:00:00Z"),
           dict(seat="BENCH", event="raise", id="ITEM_RAISED", reason="plan", ts="2026-10-30T01:00:00Z", tsn=7)]
    world = model.replay(evs, strict=True)

    class Belt(SR.FakeWorld):
        pool_order = R.Effects.pool_order

        def ledger_items(self):
            return evs, world

    def launched(setup):
        x = SR.Rig(n=0, share=1.0, max_workers=1, staffing=None, pool_seats=["BENCH"], pool_needs=["offline"],
                   pool_targets=["v1"], pool_kinds_exclude=[], pool_ids_exclude=[])
        x.w = Belt(0)
        x.w.books = str(books)
        x.w.items = {i: "proposed" for i in world.items}
        setup()
        for _ in range(6):
            x.tick()
        got = [ln[0] for ln in x.w.launches]
        x.done()
        return got

    shutil.rmtree(books, ignore_errors=True)
    today = launched(lambda: None)
    check("no list: the belt launches today's order, the raised item first", today[:1] == ["ITEM_RAISED"], today)
    got = launched(lambda: put(books, doc([entry("ITEM_Z_LISTED")])))
    check("a listed item launches before a ranked and a raised one, through a real tick", got[:1] == ["ITEM_Z_LISTED"], got)
    def full_queue():
        x = SR.Rig(n=0, share=1.0, max_workers=0, max_queued=1, staffing=None, pool_seats=["BENCH"], pool_needs=["offline"],
                   pool_targets=["v1"], pool_kinds_exclude=[], pool_ids_exclude=[])
        x.w = Belt(0)
        x.w.books = str(books)
        x.w.items = {i: "proposed" for i in world.items}
        shutil.rmtree(books, ignore_errors=True)
        x.tick()
        early = [s["item"] for s in x.s.states()]
        put(books, doc([entry("ITEM_Z_LISTED")]))
        x.r["max_workers"] = 1
        for _ in range(6):
            x.tick()
        x.done()
        return early, [ln[0] for ln in x.w.launches]

    early, got = full_queue()
    check("a full line of ranked work: an item listed later still launches first",
          "ITEM_Z_LISTED" not in early and got[:1] == ["ITEM_Z_LISTED"], (early, got))
    put(books, doc([entry("ITEM_%d" % n) for n in range(31)]))
    got = launched(lambda: None)
    check("a list over the limit is not obeyed: today's order", got == today, got)
    put(books, "{torn")
    got = launched(lambda: None)
    check("a torn list is not obeyed: today's order", got == today, got)


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
    for name, es, by in (("31 entries", [entry("ITEM_%d" % n) for n in range(31)], "Producer"),
                         ("30 entries, the list is under 30", [entry("ITEM_%d" % n) for n in range(30)], "Producer"),
                         ("an entry with no reading", [{"id": "X"}], "Producer"),
                         ("a reading outside the repo", [{"id": "X", "reading": {"file": "../x.json", "key": "a"}}], "Producer"),
                         ("a duplicate", [entry("X"), entry("X")], "Producer"),
                         ("an id that is no text", [{"id": [], "reading": {"mod": "ModA"}}], "Producer"),
                         ("an entry naming id and row", [{"id": "A", "row": None, "reading": {"mod": "ModA"}}], "Producer"),
                         ("another writer", [entry("X")], "FOUNDRY")):
        try:
            PL.write(d, es, by)
            refused = False
        except ValueError:
            refused = True
        check("the writer refuses %s" % name, refused and Path(PL.path(d)).read_text(encoding="utf-8") == before)
    r = subprocess.run([sys.executable, str(HERE / "priority_list.py"), "add", "NO_SUCH_ITEM_X", "--mod", "ModA", "--by", "Producer"],
                       env=dict(os.environ, RM_PRIORITY_LIST=str(TMP / "writer" / "cli.json")), capture_output=True, text=True)
    check("the tool refuses an item the ledger does not hold", r.returncode == 1 and "NO_SUCH_ITEM_X" in r.stderr
          and not (TMP / "writer" / "cli.json").exists(), r.stdout + r.stderr)


# ---------------------------------------------------------------- the alarms: the real pass under the shipped rules
RULES = json.loads((UTILS / "ops_watch_rules.json").read_text(encoding="utf-8"))
for tg in RULES["targets"]:
    if tg.get("conductor_log"):
        tg["conductor_log"] = str(TMP / "conductor.md")
for fam in OW.ORDER:
    if fam != "plan":
        OW.COLLECTORS[fam] = lambda now, rules, ctx: {}
OW.COLLECTORS["relentless"] = lambda now, rules, ctx: {"relentless.blind": OW.M(0)}     # quiet, or their alarms take the pass
OW.COLLECTORS["seats"] = lambda now, rules, ctx: {"seats.blind": OW.M(0)}
OW.COLLECTORS["disk"] = lambda now, rules, ctx: {"disk.scratch_outside_blind": OW.M(0)}
DATA = TMP / "data"
STATE = DATA / "infrastructure" / "state"
AGE_LIMIT = RULES["ranges"]["plan.list_age_h"]["classes"]["distressed"]["at_least"]
ADVANCE_LIMIT = RULES["ranges"]["plan.days_since_advance"]["classes"]["distressed"]["at_least"]


def lay(closes=0, status="RED", done=()):
    shutil.rmtree(TMP / "ops", ignore_errors=True)
    (TMP / "ops").mkdir()
    shutil.rmtree(DATA, ignore_errors=True)
    (STATE / "ledger" / "events").mkdir(parents=True)
    evs = [filed("ITEM_LISTED"), filed("ITEM_OTHER")]
    evs += [filed("BUSY_%d" % n) for n in range(closes)]
    evs += [dict(seat="BENCH", event="close", id="BUSY_%d" % n, sha="abc", ts=iso(T0 - 3600)) for n in range(closes)]
    evs += [dict(seat="BENCH", event="close", id=i, sha="abc", ts=iso(T0 - 3600)) for i in done]
    (STATE / "ledger" / "events.jsonl").write_text("", encoding="utf-8")
    (STATE / "ledger" / "events" / "BENCH.jsonl").write_text("".join(json.dumps(e) + "\n" for e in evs), encoding="utf-8")
    status_file(status)


def status_file(status):
    (STATE / "modcheck_status.json").write_text(json.dumps({"ModA": {"status": status}}), encoding="utf-8")


def plant_flat(days, best=1):
    atomic = {"ITEM_LISTED": {"spec": {"mod": "ModA"}, "best": best, "rose_t": T0 - days * DAY}}
    (TMP / "ops" / "plan_advance.json").write_text(json.dumps(atomic), encoding="utf-8")


def go(now=T0):
    filed_now = []

    def filer(todo, conf):
        filed_now.extend(todo)

    OW.run(now=now, rules=RULES, filer=filer)
    return json.loads((TMP / "ops" / "status.json").read_text(encoding="utf-8"))["points"], filed_now, None


def tagged(fired, tag):
    return [a for a in fired if tag in json.dumps(a, default=str)]


def alarms():
    # sane: the instrument sees a good list, and the alarm stays quiet
    lay()
    put(DATA, doc([entry("ITEM_LISTED")]))
    k, fired, _ = go()
    check("a fresh list with an open entry reads sane and files nothing",
          k["plan.distressed"]["v"] == 0 and k["plan.blind"]["v"] == 0 and k["plan.list_state"]["class"] == "sane"
          and not tagged(fired, "PLAN_"), (k.get("plan.distressed"), k.get("plan.blind"), fired))

    lay()
    put(DATA, doc([entry("ITEM_LISTED")], t=T0 - (AGE_LIMIT + 1) * 3600))
    k, fired, _ = go()
    check("a stale list reads distressed", k["plan.list_age_h"]["class"] == "distressed" and k["plan.distressed"]["v"] == 1, k.get("plan.list_age_h"))
    check("a stale list files the alarm", len(tagged(fired, "PLAN_DISTRESS")) == 1, fired)

    lay(done=["ITEM_LISTED"])
    put(DATA, doc([entry("ITEM_LISTED"), entry("ITEM_OTHER")]))
    k, fired, _ = go()
    check("a closed entry reads distressed", k["plan.list_state"]["v"] == "closed_entry" and k["plan.list_state"]["class"] == "distressed", k.get("plan.list_state"))
    check("a closed entry files the alarm and is named", len(tagged(fired, "PLAN_DISTRESS")) == 1, fired)

    lay()
    k, fired, _ = go()
    check("a missing list reads distressed, seen and not blind", k["plan.list_state"]["v"] == "missing"
          and k["plan.list_state"]["class"] == "distressed" and k["plan.blind"]["v"] == 0, k.get("plan.list_state"))
    check("a missing list files the alarm", len(tagged(fired, "PLAN_DISTRESS")) == 1, fired)

    lay()
    put(DATA, doc([entry("ITEM_%d" % n) for n in range(31)]))
    k, fired, _ = go()
    check("31 entries hand-written are refused at read and alarm", k["plan.list_state"]["v"] == "over_limit" and k["plan.entries"]["v"] == 0
          and len(tagged(fired, "PLAN_DISTRESS")) == 1, k.get("plan.list_state"))

    lay(closes=20)
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT + 1)
    k, fired, _ = go()
    p = k["plan.days_since_advance"]
    check("a flat reading past advance_max_days is distressed despite 20 closes", p["class"] == "distressed" and p["v"] >= ADVANCE_LIMIT
          and (p.get("x") or p).get("closes") == 20, p)
    check("the flat reading files the alarm, naming entry and closes", len(tagged(fired, "PLAN_DISTRESS")) == 1
          and "20 closes" in k["plan.cause"]["v"] and "ITEM_LISTED" in k["plan.cause"]["v"], (k["plan.cause"], fired))

    lay(closes=20)
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT - 1)
    k, fired, _ = go()
    check("inside advance_max_days it reads sane", k["plan.days_since_advance"]["class"] == "sane" and not tagged(fired, "PLAN_DISTRESS"), k["plan.days_since_advance"])

    lay(closes=20, status="GREEN")
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT + 1)
    k, fired, _ = go()
    check("a rise clears it", k["plan.days_since_advance"]["v"] == 0 and k["plan.distressed"]["v"] == 0, k["plan.days_since_advance"])

    lay(status="RED")
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT + 1, best=2)
    k, _, _ = go()
    check("a fall then a return under the best is no rise", k["plan.days_since_advance"]["class"] == "distressed", k["plan.days_since_advance"])

    lay(closes=20)
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT + 1)
    put(DATA, "{torn")
    k, fired, _ = go()
    put(DATA, doc([entry("ITEM_LISTED")]))
    k, fired, _ = go()
    check("a torn list for one pass does not start the flat clock again", k["plan.days_since_advance"]["class"] == "distressed", k["plan.days_since_advance"])

    lay(closes=20)
    put(DATA, doc([entry("ITEM_LISTED")]))
    plant_flat(ADVANCE_LIMIT + 1)
    torn = json.loads((TMP / "ops" / "plan_advance.json").read_text(encoding="utf-8"))
    torn["ITEM_LISTED"]["rose_t"] = "yesterday"
    (TMP / "ops" / "plan_advance.json").write_text(json.dumps(torn), encoding="utf-8")
    k, fired, _ = go()
    check("a torn advance record is blind, never a fresh clock", k["plan.blind"]["v"] == 1 and len(tagged(fired, "PLAN_BLIND")) == 1, k.get("plan.blind"))

    lay()
    (STATE / "nums.json").write_text('{"a": {"b": NaN}}', encoding="utf-8")
    put(DATA, doc([{"id": "ITEM_LISTED", "reading": {"file": "infrastructure/state/nums.json", "key": "a.b"}}]))
    k, fired, _ = go()
    check("a NaN reading is blind", k["plan.blind"]["v"] == 1 and len(tagged(fired, "PLAN_BLIND")) == 1, k.get("plan.blind"))
    (STATE / "nums.json").write_text('{"a": {"b": 3}}', encoding="utf-8")
    k, fired, _ = go()
    check("a number in a repo file is a reading", k["plan.blind"]["v"] == 0 and k["plan.days_since_advance"]["v"] == 0, k.get("plan.blind"))

    lay(status="NO_SUCH_STATUS")
    put(DATA, doc([entry("ITEM_LISTED")]))
    k, fired, _ = go()
    check("a reading that cannot be read is blind and alarms, never sane", k["plan.blind"]["v"] == 1 and len(tagged(fired, "PLAN_BLIND")) == 1, k.get("plan.blind"))

    lay()
    put(DATA, doc([entry("ITEM_LISTED")]))
    keep = OW.COLLECTORS["plan"]
    OW.COLLECTORS["plan"] = lambda now, rules, ctx: 1 / 0
    k, fired, _ = go()
    OW.COLLECTORS["plan"] = keep
    check("a collector that dies is blind and alarms", k["plan.blind"]["v"] == 1 and len(tagged(fired, "PLAN_BLIND")) == 1, (k.get("plan.blind"), fired))

    lay()
    (STATE / "ledger" / "events" / "BENCH.jsonl").unlink()
    put(DATA, doc([entry("ITEM_LISTED")]))
    k, fired, _ = go()
    check("a ledger the pass cannot see is blind, never a closed entry", k["plan.blind"]["v"] >= 1 and k["plan.list_state"]["v"] == "ok"
          and len(tagged(fired, "PLAN_BLIND")) == 1, (k.get("plan.blind"), k.get("plan.list_state")))

    r = subprocess.run([sys.executable, str(UTILS / "ops_watch.py"), "lint"], capture_output=True, text=True)
    check("the shipped ranges lint clean with the plan block", r.returncode == 0, r.stdout + r.stderr)
    routes = json.loads((HERE / "alarm_routes.json").read_text(encoding="utf-8"))["routes"]
    check("plan alarms reach a reader, not the program route", [x for x in routes if x["match"] == "plan.*" and x["route"] == "role"])


def main():
    pool()
    ring()
    writer()
    alarms()
    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_priority_list: %s (%d checks, %d fails)" % ("FAIL" if FAILS else "OK", RAN, len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
