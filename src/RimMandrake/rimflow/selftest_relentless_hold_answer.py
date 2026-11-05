#!/usr/bin/env python3
"""Selftest: an answered question releases the owner_call hold waiting on it (RELENTLESS_HOLD_BUILD_RELEASE_ON_ANSWER).

    python3 src/RimMandrake/rimflow/selftest_relentless_hold_answer.py

Pins (recovery plan step 4, consult C's tests minus C5):
  * an owner_call snag mints a question_id and the delivered why cites it (C1);
  * an answer that lands while the item is still `stopping` survives until it is held, then releases it (C3);
  * the release is recorded (attempt `answered`, a learned line carrying the answer, `st.answered`), re-queues the item
    and puts his needs back (C2: one recorded path, not a blind unhold);
  * a Conductor ruling `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` citing the question is an answer;
  * never an answer: a BENCH note citing the question, an OWNER event with no authority field, an answer citing another
    question, an OWNER ruling naming only the item (no guess match);
  * fenced on question_id: an answer to the old question never lifts a newer hold;
  * a legacy prose-only owner_call hold is never released by a ledger event and raises one hold_unmatchable alarm (C4).
Runs on selftest_relentless's FakeWorld and a throwaway store; no ledger of the repo is touched.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_answer as A           # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def owner_snag(x, i="I0", detail="a north-star bar moves"):
    x.run_one(i)
    st = x.st(i)
    g, unit = st["gen"], st["run"]["unit"]
    R.snag(x.s, i, g, "owner_call", detail, x.r, section="2.1 loosening a north-star bar", now=x.now)
    return unit


def settle(x, unit, i="I0"):
    for _ in range(6):
        x.tick()
        if x.st(i)["status"] != "stopping":
            return
        x.w.up[unit] = False


def ev(qid=None, seat="OWNER", **kw):
    e = {"seat": seat, "event": "note", "id": "I0", "ts": "2026-11-05T06:00:00Z", "tsn": 1}
    if qid:
        e["text"] = "answers %s: go ahead" % qid
    e.update(kw)
    return e


def t_answer_during_stopping():
    x = T.Rig(n=1, share=1.0)
    unit = owner_snag(x)
    st = x.st("I0")
    qid = (st["hold"] or {}).get("question_id")
    ok(st["status"] == "stopping" and qid and qid.startswith(A.QID_PREFIX), "an owner_call snag mints a question_id")
    ok(qid in st["hold"]["why"], "the why the ledger gets cites the question_id")
    x.w.answers.append(ev(qid, byCard="Loosen the bar? → Yes"))     # lands before the worker is stopped
    settle(x, unit)
    for _ in range(3):
        if x.st("I0")["status"] != "held":
            break
        x.tick()
    st = x.st("I0")
    ok(st["status"] not in ("held", "stopping") and not st["hold"], "the answer survives stopping and releases the hold: %s"
       % st["status"])
    ok((st.get("answered") or {}).get("question_id") == qid and "Loosen the bar" in st["answered"]["said"],
       "the release records which answer it consumed")
    ends = [a.get("end") for a in x.s.attempts("I0")]
    ok("answered" in ends, "an `answered` attempt is recorded: %s" % ends[-3:])
    ok(qid in x.s.learned("I0") and "Loosen the bar" in x.s.learned("I0"), "the next worker's brief carries the answer")
    x.tick()        # the queued step puts the needs back
    ok(("I0", x.w.needs_back) in x.w.needs, "his needs are put back on the ledger: %s" % x.w.needs)
    x.done()


def t_conductor_ruling_counts():
    x = T.Rig(n=1, share=1.0)
    settle(x, owner_snag(x))
    qid = x.st("I0")["hold"]["question_id"]
    ok(x.st("I0")["status"] == "held", "setup: held")
    x.w.answers.append(ev(qid, perRuling="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", why="Conductor: yes"))
    x.tick()
    ok((x.st("I0").get("answered") or {}).get("question_id") == qid, "a Conductor --per-ruling answer releases the hold")
    x.done()


def t_not_answers():
    x = T.Rig(n=1, share=1.0)
    settle(x, owner_snag(x))
    qid = x.st("I0")["hold"]["question_id"]
    x.w.answers += [
        ev(qid, seat="BENCH", why="builder: I think he meant yes"),       # a builder's word
        ev(qid),                                                         # OWNER seat, no authority field
        ev("HQ_0000000000", byCard="other → yes"),                       # another question
        ev(None, perRuling="CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", text="I0 is fine, release it"),   # item only
    ]
    for _ in range(4):
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["question_id"] == qid and not st.get("answered"),
       "no builder note, authority-less event, other question or item-only ruling releases it")
    x.done()


def t_fenced_on_question():
    x = T.Rig(n=1, share=1.0)
    settle(x, owner_snag(x))
    old = x.st("I0")
    R.unhold(x.s, "I0", "Conductor: lifted by hand", now=x.now)
    x.now += 60
    settle(x, owner_snag(x, detail="a second call"))
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["question_id"] != old["hold"]["question_id"], "setup: a newer hold")
    x.w.answers.append(ev(old["hold"]["question_id"], ownerSaid="yes to the first"))
    for _ in range(3):
        x.tick()
    ok(x.st("I0")["status"] == "held" and not x.st("I0").get("answered"), "an answer to the old question never lifts the new")
    acts = []
    released = A.reconcile(x.s, type("F", (), {"ledger_answer": lambda s, q: ev(q, ownerSaid="y")})(), "I0", old,
                           x.now, acts, R.iso)
    ok(not released and x.st("I0")["status"] == "held", "a stale read is fenced under the lock")
    x.done()


def t_legacy_alarm():
    x = T.Rig(n=1, share=1.0)
    settle(x, owner_snag(x))
    with x.s.lock():
        st = x.s.load("I0")
        qid = st["hold"].pop("question_id")
        st["hold"]["why"] = "delegation_policy section 2: legacy prose only"
        x.s.save(st)
    x.w.answers.append(ev(qid, byCard="q → yes"))
    x.w.answers.append(ev(None, byCard="I0 → yes", text="release I0"))
    for _ in range(4):
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and not st.get("answered"), "a legacy prose hold is never guess-matched")
    with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
        alarms = [r for r in map(json.loads, f) if r.get("do") == "alarm" and r.get("kind") == A.ALARM]
    ok(len(alarms) == 1 and alarms[0]["item"] == "I0" and "needs the Conductor" in alarms[0]["why"],
       "one hold_unmatchable alarm names it for the Conductor: %d" % len(alarms))
    x.done()


if __name__ == "__main__":
    for t in (t_answer_during_stopping, t_conductor_ruling_counts, t_not_answers, t_fenced_on_question, t_legacy_alarm):
        print("--", t.__name__)
        t()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)
