#!/usr/bin/env python3
"""selftest_evidence_metrics.py - evidence_metrics.py on fixtures (item METRICS_RECORD_BUILD_EVIDENCE_NOT_TARGETS).

Exit 0 when every case holds, 1 otherwise. No live store, ledger or journal is read.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import delivery_metrics, evidence_metrics as em, jam_classes   # noqa: E402

FAILS = []
DAY = 86400.0
T0 = 1793000000.0                     # an arbitrary epoch: every fixture time is relative to it
NOW = T0 + 30 * DAY


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ev(t, event, **kw):
    return dict(kw, event=event, ts=iso(t), tsn=int(t * 1e9))


EVENTS = [
    # STAY: offline, started day 0, closed day 1, nothing after
    ev(T0, "file", id="STAY", needs="offline"), ev(T0 + 0.5 * DAY, "start", id="STAY"), ev(T0 + DAY, "close", id="STAY"),
    # REOPEN: online (needs set later by a `needs` event), reopened by a start 2 days after close
    ev(T0, "file", id="REOPEN", needs="offline"), ev(T0, "needs", id="REOPEN", to="bridge"),
    ev(T0 + DAY, "close", id="REOPEN"), ev(T0 + 3 * DAY, "start", id="REOPEN"),
    # LATE: broke live 9 days after close: it stayed done for 7 days, yet it is an escape
    ev(T0, "file", id="LATE", needs="offline"), ev(T0 + DAY, "close", id="LATE"),
    ev(T0 + 10 * DAY, "live", id="LATE", result="broken"),
    # FOLLOW: work filed against it (caused_by) within 7 days
    ev(T0, "file", id="FOLLOW", needs="offline"), ev(T0 + DAY, "close", id="FOLLOW"),
    ev(T0 + 2 * DAY, "file", id="FOLLOW_FIX", caused_by="FOLLOW", needs="offline"),
    # SPAWNED: a spawn from it within 7 days
    ev(T0, "file", id="SPAWNED", needs="game-up"), ev(T0 + DAY, "close", id="SPAWNED"),
    ev(T0 + 4 * DAY, "spawn", name="SPAWNED_REPAIR", **{"from": "SPAWNED"}),
    # AFTERFAIL: verify fail afterClose; a plain later verify fail (no afterClose) on OKVERIFY is not a signal
    ev(T0, "file", id="AFTERFAIL", needs="offline"), ev(T0 + DAY, "close", id="AFTERFAIL"),
    ev(T0 + 2 * DAY, "verify", id="AFTERFAIL", result="fail", afterClose=True),
    ev(T0, "file", id="OKVERIFY", needs="offline"), ev(T0 + DAY, "close", id="OKVERIFY"),
    ev(T0 + 2 * DAY, "verify", id="OKVERIFY", result="fail"), ev(T0 + 2 * DAY, "note", id="OKVERIFY", text="x"),
    # YOUNG: closed 3 days before NOW: pending, never counted
    ev(T0, "file", id="YOUNG", needs="offline"), ev(NOW - 3 * DAY, "close", id="YOUNG"),
    # NONEEDS: never set needs -> lane unknown
    ev(T0, "file", id="NONEEDS"), ev(T0 + DAY, "close", id="NONEEDS"),
    # RECLOSE: closed, reopened, closed again: two closes, the first did not stay, the second did
    ev(T0, "file", id="RECLOSE", needs="offline"), ev(T0 + DAY, "close", id="RECLOSE"),
    ev(T0 + 2 * DAY, "implemented", id="RECLOSE"), ev(T0 + 2.5 * DAY, "start", id="RECLOSE"),
    ev(T0 + 3 * DAY, "close", id="RECLOSE"),
]


def main():
    cl = em.closes(sorted(EVENTS, key=lambda e: (e["ts"], e["tsn"])))
    by = {}
    for c in cl:
        by.setdefault(c["item"], []).append(c)
    sd, stayed = em.stays_done(cl, NOW)
    names = sorted(c["item"] for c in stayed)
    check(names == ["LATE", "NONEEDS", "OKVERIFY", "RECLOSE", "STAY"],
          "stayed done after 7 days: STAY, LATE (broke on day 9), OKVERIFY (a plain verify fail is no signal), "
          "NONEEDS and RECLOSE's second close; got %s" % names)
    lanes = sd["by_lane"]
    check(lanes["offline"] == {"stayed": 4, "did_not": 3, "pending": 1, "share_stayed": round(4 / 7, 3)},
          "offline lane: STAY LATE OKVERIFY RECLOSE#2 stayed; FOLLOW AFTERFAIL RECLOSE#1 did not; YOUNG pending: %s"
          % lanes["offline"])
    check(lanes["online"]["stayed"] == 0 and lanes["online"]["did_not"] == 2,
          "online lane (bridge set by a needs event, game-up): REOPEN and SPAWNED did not stay: %s" % lanes["online"])
    check(lanes["unknown"]["stayed"] == 1, "an item that never set needs is lane unknown: %s" % lanes["unknown"])
    check(sd["did_not_because"] == {"failed_after_close": 1, "reopened": 2, "work_filed_against_it": 2},
          "the reasons: reopened (REOPEN, RECLOSE#1), work filed (FOLLOW, SPAWNED), failed after close: %s"
          % sd["did_not_because"])
    check(sum(v["pending"] for v in lanes.values()) == 1 and "YOUNG" not in names,
          "a close younger than 7 days is pending, never counted as stayed or not")
    check(len(by["RECLOSE"]) == 2 and by["RECLOSE"][1]["first_start"] == T0 + 2.5 * DAY,
          "a reclose is a second close whose elapsed time runs from the reopening start")

    # cost: the store fixture prices STAY (two generations) and leaves LATE unpriced
    store = tempfile.mkdtemp(prefix="evm_store_")
    for item, rows in (("STAY", [{"at": iso(T0), "gen": 1, "start": "u"}, {"at": iso(T0 + 3600), "gen": 1, "end": "x"},
                                 {"at": iso(T0 + 7200), "gen": 2, "start": "u"}, {"at": iso(T0 + 3 * 3600), "gen": 2, "end": "finish"}]),):
        d = os.path.join(store, "items", item)
        os.makedirs(d)
        with open(os.path.join(d, "state.json"), "w") as f:
            json.dump({"status": "done"}, f)
        with open(os.path.join(d, "attempts.jsonl"), "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
    h = delivery_metrics.short("STAY")
    with open(os.path.join(store, "spend-20261101.json"), "w") as f:
        json.dump({"runs": {"rm-relentless-work-%s-g1" % h: 1000, "rm-relentless-check-%s-g1-c1" % h: 500,
                            "rm-relentless-work-%s-g2" % h: 2500, "rm-relentless-work-0000000000-g1": 99}}, f)
    snap = delivery_metrics.load(store, os.path.join(store, "noledger"))
    co = em.cost(stayed, snap)
    a = co["all"]
    check(a["closes"] == 5 and a["belt_ran"] == 1, "cost covers the 5 stayed closes, 1 run by the belt: %s" % a)
    check(a["tokens"] == {"priced": 1, "unpriced": 4, "total": 4000, "median": 4000},
          "tokens: STAY's own units summed (work+check, both gens), another item's unit ignored, the rest unpriced "
          "not zero: %s" % a["tokens"])
    check(a["worker_hours"] == {"measured": 1, "total": 2.0, "median": 2.0},
          "worker hours sum STAY's two generations start->end (1 h + 1 h): %s" % a["worker_hours"])
    check(a["elapsed_hours"]["measured"] == 2 and co["offline"]["elapsed_hours"]["median"] is not None,
          "elapsed hours from the first start to the close where the ledger has a start (STAY 12 h, RECLOSE 12 h): %s"
          % a["elapsed_hours"])
    nostore = em.cost(stayed, delivery_metrics.load(os.path.join(store, "absent"), store))
    check(nostore["all"]["tokens"].get("value") == em.UNMEASURED and nostore["all"]["worker_hours"].get("value") == em.UNMEASURED,
          "no store: tokens and worker hours say UNMEASURED with why, never 0")

    # jams by class, through the real registry's matchers
    reg = jam_classes.load()
    ex = {c["id"]: c["examples"][0] for c in reg["classes"] if c.get("examples")}
    kind = reg["kinds"][0]
    two = sorted(ex)[:2]
    jp = os.path.join(store, "journal.jsonl")
    rows = [{"do": "alarm", "kind": kind, "at": iso(NOW - 2 * DAY), "why": ex[two[0]]},
            {"do": "alarm", "kind": kind, "at": iso(NOW - 2 * DAY + 60), "why": ex[two[0]]},
            {"do": "alarm", "kind": kind, "at": iso(NOW - 20 * DAY), "why": ex[two[1]]},
            {"do": "alarm", "kind": kind, "at": iso(NOW - DAY), "why": "a jam nobody has named zzqx"},
            {"do": "enrol", "item": "X", "at": iso(NOW)}]
    with open(jp, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))
    j = em.jams(reg, jp, NOW)
    check(j["last_7d"]["by_class"] == {two[0]: 2, "unnamed": 1} and j["last_7d"]["jams"] == 3,
          "jams last 7 d by class (a class's own example classifies to it; an unmatched reason is unnamed): %s" % j["last_7d"])
    check(j["all_time"]["by_class"].get(two[1]) == 1 and j["all_time"]["jams"] == 4,
          "all-time jams include the 20-day-old one: %s" % j["all_time"])
    check(set(j["plain"]) == set(two), "each counted class carries its plain sentence: %s" % sorted(j["plain"]))
    check(em.jams(reg, os.path.join(store, "nojournal.jsonl"), NOW).get("value") == em.UNMEASURED
          and em.jams(reg, None, NOW).get("value") == em.UNMEASURED, "no journal: jams UNMEASURED, never 0")

    # escapes by tag
    e0 = em.escapes(cl, None)
    check(e0["escapes"] == 6 and e0["tags"]["value"] == em.UNMEASURED and e0["by_tag"] == {},
          "escapes (REOPEN FOLLOW SPAWNED AFTERFAIL RECLOSE#1, and LATE that broke on day 9) with no tag record: "
          "all untagged, tags UNMEASURED: %s" % e0)
    check(e0["untagged_by_signal"] == {"broke_live": 1, "failed_after_close": 1, "reopened": 2, "work_filed_against_it": 2},
          "untagged escapes by the signal that made them: %s" % e0["untagged_by_signal"])
    tp = os.path.join(store, "escape_tags.jsonl")
    with open(tp, "w") as f:
        f.write(json.dumps({"item": "LATE", "tag": "Only proven on the minimal mod list."}) + "\n"
                + json.dumps({"item": "FOLLOW", "tag": "old"}) + "\n"
                + json.dumps({"item": "FOLLOW", "tag": "The test checked the file, not the running game."}) + "\n")
    e1 = em.escapes(cl, em.escape_tags(tp))
    check(e1["by_tag"] == {"Only proven on the minimal mod list.": 1, "The test checked the file, not the running game.": 1}
          and sum(e1["untagged_by_signal"].values()) == 4 and "tags" not in e1,
          "with a tag record: tagged escapes count by their plain tag (newest row wins), the rest stay untagged: %s" % e1)

    # the whole record: four sections, labelled evidence, no target anywhere
    m = em.compute(EVENTS, snap, reg, jp, None, NOW)
    check(all(k in m for k in ("stays_done", "cost_per_stayed_done", "jams_by_class", "escapes_by_tag"))
          and "not a target" in m["note"], "compute -> the four sections and the evidence-not-target note")
    blob = json.dumps(m).lower()
    check(not any(w in blob for w in ('"target"', "threshold\"", '"goal"', '"bar"', '"pass"', '"fail"')),
          "the record carries no target, goal, bar or pass/fail field")
    mn = em.compute(None, snap, reg, jp, None, NOW)
    check(mn["stays_done"].get("value") == em.UNMEASURED and mn["escapes_by_tag"].get("value") == em.UNMEASURED,
          "no ledger: the ledger metrics say UNMEASURED")
    rec = os.path.join(store, "rec.jsonl")
    led = os.path.join(store, "ledger")
    os.makedirs(led)
    with open(os.path.join(led, "BENCH.jsonl"), "w") as f:
        f.write("".join(json.dumps(e) + "\n" for e in EVENTS))
    rc = em.main(["record", "--store", store, "--ledger", led, "--journal", jp, "--record", rec])
    with open(rec) as f:
        got = [json.loads(x) for x in f]
    check(rc == 0 and len(got) == 1 and "jams_by_class" in got[0] and got[0]["stays_done"]["by_lane"]["offline"]["did_not"] == 3,
          "record appends one JSON row, read from the ledger it is pointed at, to the record file")

    print("selftest_evidence_metrics: %s" % ("PASS" if not FAILS else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
