#!/usr/bin/env python3
"""selftest_owner_queue.py — Fleet Watch's "Needs you" and the mods' "waits on you" are one test (offline, fake items).

FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT: the header said "Nothing." while ten mods said "waits on you".
Covers: which routings count as his (Relentless tooling holds do not; owner_call and a flyer game hold do), the
question line (questions file wins, title fallback), fleet_mods.waits_on agreeing with is_his on every case, and
fleet_refresh.plan carrying board/needs and waking a write when only the needs changed.
"""
import json
import os
import sys
import tempfile
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import owner_queue as Q  # noqa: E402
import fleet_mods as M  # noqa: E402
import fleet_refresh as F  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def it(needs="offline", open_=True, blocked=False, kind=None, title="T"):
    return NS(open=open_, needs=needs, blocked=blocked, blocked_kind=kind, held=False, title=title, state="doing")


def held(kind, why=""):
    return {"status": "held", "hold": {"kind": kind, "why": why, "delivered": True}}


items = {
    "A_PLAIN_OWNER": it("owner", title="Plain owner ask"),
    "B_PROOF_WEAK": it("owner"),
    "C_SPEND": it("owner"),
    "D_OWNER_CALL": it("owner", title="Owner call"),
    "E_FLYER": it("owner"),
    "F_GAMESTAGE": it("owner"),
    "G_BLOCKED_OWNER": it("offline", blocked=True, kind="owner", title="Blocked on him"),
    "H_CLOSED": it("owner", open_=False),
    "I_OFFLINE": it("offline"),
    "J_BLOCKED_ITEM": it("offline", blocked=True, kind="item"),
    "K_HOLD_STR": it("owner", title="old store shape"),
    "L_RELEASED": it("owner", title="hold lifted"),
}
rel = {
    "B_PROOF_WEAK": held("proof_weak", "2 returns and the proof still reads weak"),
    "C_SPEND": held("spend", "item spend limit"),
    "D_OWNER_CALL": held("owner_call", "delegation_policy section 2"),
    "E_FLYER": held("game", "game phase: flyer: a flyer's flight is never live-tested without the owner present"),
    "F_GAMESTAGE": held("game", "game phase: stage failed twice"),
    "K_HOLD_STR": {"status": "held", "hold": "owner"},
    "L_RELEASED": {"status": "queued", "hold": {"kind": "proof_weak"}},
}
his = {"A_PLAIN_OWNER", "D_OWNER_CALL", "E_FLYER", "G_BLOCKED_OWNER", "K_HOLD_STR", "L_RELEASED"}
for iid in sorted(items):
    got = Q.is_his(items[iid], rel.get(iid))
    check("is_his %s -> %s" % (iid, iid in his), got == (iid in his))
    # the mods section can never disagree with the header: same predicate, every case
    check("waits_on agrees %s" % iid, (M.waits_on(items[iid], rel.get(iid)) == "you") == got)

n = Q.needs_you(items, rel, {"D_OWNER_CALL": "Does X bind Y?"})
check("count is the set", n["count"] == len(his) and [x["item"] for x in n["lines"]] == sorted(his))
check("question file wins", {x["item"]: x["q"] for x in n["lines"]}["D_OWNER_CALL"] == "Does X bind Y?")
check("title is the fallback", {x["item"]: x["q"] for x in n["lines"]}["A_PLAIN_OWNER"] == "Plain owner ask")
check("text leads with the count", n["text"].startswith("%d things: " % len(his)))
none = Q.needs_you({"I": it("offline")}, {}, {})
check("nothing his -> empty text, count 0", none == {"count": 0, "lines": [], "text": ""})
check("misrouted lists tooling holds", [k for k, _ in Q.misrouted(items, rel)] == ["B_PROOF_WEAK", "C_SPEND", "F_GAMESTAGE"])

with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "q.json")
    with open(p, "w") as f:
        f.write("[1, 2]")
    check("a malformed questions file reads as empty", Q.load_questions(p) == {})
    check("a missing questions file reads as empty", Q.load_questions(os.path.join(d, "none.json")) == {})
q = Q.load_questions()
check("repo questions file: one non-empty line each", q and all(isinstance(v, str) and v.strip() and "\n" not in v
                                                                 for v in q.values()))

# fleet_refresh: board/needs rides with the board docs, and a needs change alone wakes the write
with tempfile.TemporaryDirectory() as d:
    docs = [("board", "factory", {"ok": 1}), ("board", "needs", n)]
    w, _, _, st = F.plan([], {}, 100, d, docs, False)
    check("plan writes board/needs", any(x["collection"] == "board" and x["doc_id"] == "needs" for x in w))
    prev = dict(st, versions={"board/factory": 1, "board/needs": 1, "board/summary": 1})
    w2, _, _, _ = F.plan([], prev, 200, d, docs, False)
    check("unchanged needs -> no write", w2 == [])
    w3, _, _, _ = F.plan([], prev, 300, d, [("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("changed needs alone -> board/needs written", any(x["doc_id"] == "needs" for x in w3))

    mod = ("mods", "m1", {"id": "m1", "waits_you": 1})
    prev2 = dict(prev, versions=dict(prev["versions"], **{"mods/m1": 1}), mods_at=300)
    w4, _, _, _ = F.plan([], prev2, 301, d, [mod, ("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("a needs change pulls the mods along off-schedule", any(x["collection"] == "mods" for x in w4))
    w5, _, _, _ = F.plan([], prev2, 301, d, [mod, ("board", "factory", {"ok": 1}), ("board", "needs", n)], False)
    check("no needs change -> mods wait for their schedule", w5 == [])
    rows = [{"item": "R%02d" % i, "status": "Building", "title": "row %d" % i} for i in range(45)]
    w6, _, _, _ = F.plan(rows, prev, 400, d, docs, False)
    check("40+ changed rows still leave board/needs its slot",
          any(x["doc_id"] == "needs" for x in w6) and len(w6) <= F.MAX_WRITES)

    many = [("mods", "M%02d" % i, {"id": i, "waits": ["waits on you: q%d" % i], "waits_you": 1}) for i in range(45)]
    prev3 = dict(prev, mods_at=390)
    w7, _, _, st7 = F.plan([], prev3, 401, d, many + [("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("a capped needs-forced mods run is due again next run", st7["mods_at"] == 0 and len(w7) == F.MAX_WRITES - 1)
    check("board/needs waits while mods it changed are left over",
          not any(x["doc_id"] == "needs" for x in w7) and st7["doc_hashes"].get("board/needs") == prev3["doc_hashes"]["board/needs"])
    w7b, _, _, _ = F.plan(rows, prev, 405, d, [mod, ("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("a needs change reserves its mods' slots ahead of 45 rows",
          {("mods", "m1"), ("board", "needs")} <= {(x["collection"], x["doc_id"]) for x in w7b} and len(w7b) <= F.MAX_WRITES)
    quiet = [("mods", "Q%02d" % i, {"id": i, "x": 1}) for i in range(45)]
    loud = ("mods", "LOUD", {"id": "LOUD", "waits": ["waits on you: q"], "waits_you": 1})
    wq, _, _, stq = F.plan([], prev3, 406, d, quiet + [loud, ("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("a mod whose waits moved goes first, so the header still goes up beside it",
          {("mods", "LOUD"), ("board", "needs")} <= {(x["collection"], x["doc_id"]) for x in wq}
          and stq["mods_at"] == 0 and stq["mod_waits"]["LOUD"] == F.waits_hash(loud[2]))
    q2 = [("mods", "Q%02d" % i, {"id": i, "x": 2}) for i in range(45)]
    prev4 = dict(prev3, versions=dict(prev3["versions"], **{"mods/OLD": 3}))
    old_ = ("mods", "OLD", {"id": "OLD", "x": 2})  # published before waits were tracked, now says nothing
    wo, _, _, _ = F.plan([], prev4, 407, d, q2 + [old_, ("board", "factory", {"ok": 1}), ("board", "needs", none)], False)
    check("a published mod with unrecorded waits rides with the header",
          {("mods", "OLD"), ("board", "needs")} <= {(x["collection"], x["doc_id"]) for x in wo})
    w8, _, _, st8 = F.plan([dict(r, status="Ended") for r in rows], dict(prev, status={r["item"]: "Building" for r in rows}),
                           402, d, docs, False)
    capped = [r["item"] for r in rows if r["item"] not in {x["doc_id"] for x in w8 if x["collection"] == "parts"}]
    check("a capped row keeps its old status until written",
          capped and all(st8["status"][i] == "Building" for i in capped))

    check("the capped rows are remembered as deferred", st8["deferred"] == sorted(capped))
    st8b = dict(st8, versions=dict(st8["versions"], **{"parts/" + r["item"]: 1 for r in rows}))
    busy = [dict(r, status="Ended", title="changed again") if r["item"] not in capped else dict(r, status="Ended")
            for r in rows]
    w9, _, _, _ = F.plan(busy, st8b, 403, d, docs, False)
    check("deferred rows go first next run", set(capped) <= {x["doc_id"] for x in w9 if x["collection"] == "parts"})
    ten = [{"item": "S%d" % i, "status": "Done", "title": "s%d" % i} for i in range(10)]
    w10, _, _, st10 = F.plan(ten, dict(prev, status={r["item"]: "Building" for r in ten}), 404, d, docs, False)
    feed10 = [x for x in w10 if x["collection"] == "feed"]
    check("changes past the feed's room wait for the next run; every written row's status is saved",
          len(feed10) == F.FEED_MAX and len(st10["feed_pending"]) == 10 - F.FEED_MAX
          and all(v == "Done" for v in st10["status"].values()))
    w10b, _, _, st10b = F.plan(ten, st10, 405, d, docs, False)
    check("and go out first next run", [x["data"]["text"] for x in w10b if x["collection"] == "feed"] == st10["feed_pending"]
          and st10b["feed_pending"] == [])

with tempfile.TemporaryDirectory() as d:
    with open(os.path.join(d, "X.json"), "w") as f:
        json.dump({"item": "X", "status": "Done", "title": "x"}, f)
    with open(os.path.join(d, "Y.json"), "w") as f:
        json.dump({"item": "Y", "status": "Building", "title": "y"}, f)
    e = {r["item"]: r["status"] for r in F.ended({"status": {"X": "Building", "Y": "Building"}}, set(), d)}
    check("ended: a capped finish goes up as its real end; a vanished live row as Ended", e == {"X": "Done", "Y": "Ended"})

w11, _, _, _ = F.plan([{"item": "N", "status": "Building", "title": "n"}], {"status": {}}, 500, "/r")
check("a start after an empty fleet reaches the feed", any(x["collection"] == "feed" for x in w11))
w12, _, _, _ = F.plan([{"item": "N", "status": "Building", "title": "n"}], {}, 500, "/r")
check("the very first run stays silent", not any(x["collection"] == "feed" for x in w12))
W = NS(items={"Z": NS(open=False, needs="offline", blocked=False, blocked_kind=None, title="z", state="done",
                     verdict=None)})
RZ = {"Z": {"status": "done", "done_at": 1999999000, "enrolled_at": 1999998000, "verdict": "PASS"}}
rc = M.receipts(2000000000, {}, RZ, W, [], [{"item": "Z", "status": "Done", "started": 1999998500, "finished_at": 1999999500}])
check("a newer detached run beats an older Relentless one", len(rc) == 1 and rc[0]["finished_at"] == 1999999500)
rc = M.receipts(2000000000, {}, RZ, W, [], [{"item": "Z", "status": "Done", "started": 1999997000, "finished_at": 1999999500}])
check("an older run finishing later does not", len(rc) == 1 and rc[0].get("relentless"))

print("RESULT %s (%d fail)" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
