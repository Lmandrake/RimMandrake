#!/usr/bin/env python3
"""An answered question releases the hold waiting on it (RELENTLESS_HOLD_BUILD_RELEASE_ON_ANSWER, recovery plan step 4).

ICON_OUTLINE_REPAINT_1 stood ~33 h held after his card answered it: an owner_call hold kept only a prose `why`, so nothing
could tell that the answer had come. Now:

  * an owner_call hold carries a `question_id` (`HQ_<hex>`), minted when the worker snags and written into the why that
    goes to the ledger, so the card or ruling that answers it can cite it;
  * an answer is a ledger event in his authority (seat OWNER, with `ownerSaid`, `byCard` or `perRuling`; a Conductor
    ruling `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` counts) whose text cites that question_id. A builder's
    own note (seat BENCH, `--why` only) never answers. Matching is by the token only: never by title, time or item;
  * every tick reconciles: a held owner_call hold whose question is answered is released under Store.lock, fenced on its
    question_id (a hold replaced meanwhile is left alone), recorded as an attempt and as a learned line carrying the
    answer, and re-queued with his needs put back. An answer that lands while the item is still `stopping` waits on the
    ledger until the item reaches held: the read is stateless, so nothing is lost;
  * a legacy owner_call hold (no question_id) is never guess-matched: it raises one `hold_unmatchable` alarm per hold,
    naming the item, "needs the Conductor" (who answers it with `relentless.py unhold`).
"""
import hashlib

QID_PREFIX = "HQ_"
AUTHORITY = ("ownerSaid", "byCard", "perRuling")
ALARM = "hold_unmatchable"


def question_id(item, gen, now):
    """A token no answer can cite by accident: the item, the generation it stopped at and the moment."""
    return QID_PREFIX + hashlib.sha1(("%s|%s|%r" % (item, gen, now)).encode()).hexdigest()[:10].upper()


def ask_line(qid):
    """What the delivered why says, so the card that answers it knows what to cite."""
    return "[question %s: answer with --by-card/--owner-said/--per-ruling, the text citing %s]" % (qid, qid)


def cites(ev, qid):
    """An event in his authority whose words carry the question_id. -> bool"""
    if not qid or not isinstance(ev, dict) or ev.get("seat") != "OWNER":
        return False
    if not any(ev.get(k) for k in AUTHORITY):
        return False
    return any(isinstance(v, str) and qid in v for v in ev.values())


def find(evs, qid):
    """The first event that answers `qid`, or None."""
    for ev in evs or ():
        if cites(ev, qid):
            return ev
    return None


def words(ev):
    """The answer in one line, for the record and the next worker's brief."""
    parts = []
    for k in ("byCard", "ownerSaid", "perRuling", "text", "reason", "why"):
        if ev.get(k):
            parts.append("%s=%s" % (k, ev[k]))
    return "; ".join(parts)[:900]


def reconcile(store, fx, item, st, now, acts, iso, journal_alarm=True):
    """The held step for an owner_call hold. -> True when this call released the hold."""
    h = st.get("hold") or {}
    if h.get("kind") != "owner_call":
        return False
    qid = h.get("question_id")
    if not qid:
        if journal_alarm and not h.get("unmatchable_told"):
            store.journal({"at": iso(now), "do": "alarm", "kind": ALARM, "item": item,
                           "why": "%s: owner_call hold with no question_id (prose only), unmatchable: needs the "
                                  "Conductor (answer, then `relentless.py unhold %s`): %s"
                                  % (item, item, (h.get("why") or "")[:300])})
            with store.lock():
                cur = store.load(item)
                if cur and cur.get("status") == "held" and (cur.get("hold") or {}).get("kind") == "owner_call" \
                        and not (cur.get("hold") or {}).get("question_id"):
                    cur["hold"]["unmatchable_told"] = now
                    store.save(cur)
            acts.append({"do": "hold_unmatchable", "item": item})
        return False
    reader = getattr(fx, "ledger_answer", None)
    if reader is None:
        return False
    ev = reader(qid)
    if not ev:
        return False
    said = words(ev)
    with store.lock():
        cur = store.load(item)
        ch = (cur or {}).get("hold") or {}
        if not cur or cur.get("status") != "held" or ch.get("kind") != "owner_call" or ch.get("question_id") != qid:
            return False        # fenced: the hold was lifted or replaced since the read
        cur["answered"] = {"question_id": qid, "at": now, "tsn": ev.get("tsn"), "ts": ev.get("ts"), "said": said}
        cur["hold"] = None
        cur["returned_at"] = now
        cur["status"] = "queued"
        cur["spent_grace"] = cur.get("spent", 0)    # his answer buys another full limit, as unhold does
        cur["needs_back"] = True                    # the ledger says owner; the next step puts its needs back
        store.attempt(item, {"at": iso(now), "end": "answered", "question_id": qid, "tsn": ev.get("tsn"),
                             "said": said})
        store.learn(item, "- %s question %s answered on the ledger (%s): %s" % (iso(now), qid, ev.get("ts"), said))
        store.save(cur)
    acts.append({"do": "hold_answered", "item": item, "question_id": qid})
    return True
