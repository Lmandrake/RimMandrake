#!/usr/bin/env python3
"""The escalation route, as the owner's card has it (relentless_expedite.py, 2026-11-03). Planted: no cap on count; two
levels; interrupt stops one running worker when the house is full, expedited stops nobody; neither touches the live game;
content and system workers go in that order, an expedited one never; only Operations or the Conductor may set it, never a
Relentless run; 4 h expiry, renew and clear; every use reaches the digest's reader. No units, no network."""
import json
import os
import shutil
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import delegated_digest as DD  # noqa: E402
import relentless as R  # noqa: E402
import relentless_expedite as X  # noqa: E402
import relentless_game as G  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, share=0.5, max_workers=2,
             enrol_per_tick=50, max_queued=50, staffing=None, one_builder_per_mod=False, pool_ids_exclude=["BANNED"])
H = 3600


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def refused(fn, word, what):
    try:
        fn()
    except ValueError as e:
        ok(word in str(e), what, str(e))
    else:
        ok(False, what + " (was allowed)")


class Fx:
    def __init__(self, first=None):
        self.first, self.notes, self.fail_notes = first or {}, [], 0

    def expedite_note(self, item, text):
        if self.fail_notes:
            self.fail_notes -= 1
            return "ledger down"
        self.notes.append((item, text))
        return None

    def item_state(self, item, fresh=False):
        return None


def st(item, status="queued", **kw):
    return dict(R.new_state(item, 1.0, ""), status=status, **kw)


def fresh():
    d = tempfile.mkdtemp(prefix="rlexp-")
    return d, R.Store(d)


def setit(s, item, level="expedited", now=100.0, by="Conductor", why="w"):
    return X.request(s, "set", item, now, {}, level, by, why)


# --- who may set it
d, s = fresh()
refused(lambda: setit(s, "A", by="Relentless"), "--by", "set: only Operations or the Conductor")
for k in X.WORKER_ENV:
    refused(lambda: X.request(s, "set", "A", 1.0, {k: "1"}, "interrupt", "Operations", "w"), "may not expedite",
            "set: refused inside a Relentless run (%s)" % k)
refused(lambda: X.request(s, "set", "A", 1.0, {}, "soon", "Operations", "w"), "--level", "set: the switch has two positions")
refused(lambda: X.request(s, "set", "A", 1.0, {}, "interrupt", "Operations", " "), "--why", "set: a use names its reason")
ok(not X.read_log(s), "set: a refusal writes nothing")

# --- no cap on count; the 4 h clock; renew; clear
for n in range(40):
    setit(s, "M%02d" % n)
ok(len(X.fold(X.read_log(s), 100.0)) == 40, "count: forty stand at once, the owner set no cap")
ok(not X.fold(X.read_log(s), 100.0 + 4 * H), "expiry: gone at exactly 4 h with no renewal")
ok(len(X.fold(X.read_log(s), 100.0 + 4 * H - 1)) == 40, "expiry: alive a second before")
shutil.rmtree(d, ignore_errors=True)

d, s = fresh()
setit(s, "A", "expedited", 100.0)
e = X.request(s, "renew", "A", 100.0 + 3 * H, {}, None, "Operations", "still")
ok(e["until"] == 100.0 + 7 * H and e["level"] == "expedited", "renew: a fresh 4 h from the renewal, level kept", e)
e = X.request(s, "renew", "A", 100.0 + 3 * H, {}, "interrupt", "Operations", "worse")
ok(e["level"] == "interrupt", "renew: may throw the switch", e)
ok(X.request(s, "clear", "A", 100.0 + 3 * H, {}, None, "Conductor", "done") is None, "clear: the request is gone")
refused(lambda: X.request(s, "renew", "A", 100.0 + 3 * H, {}, None, "Conductor", "x"), "no standing", "renew: nothing to renew")
refused(lambda: X.request(s, "clear", "A", 100.0 + 3 * H, {}, None, "Conductor", "x"), "no standing", "clear: nothing to clear")
with open(s.p(X.LOG), "a") as f:
    f.write("{torn\n")
ok(len(X.read_log(s)) == 4, "log: a torn line loses that line only", X.read_log(s))
shutil.rmtree(d, ignore_errors=True)

# --- the order
states = [st("CONTENT"), st("LISTED"), st("SYSTEM"), st("EXP_OLD", expedite={"level": "expedited", "at": 1.0}),
          st("EXP_NEW", expedite={"level": "expedited", "at": 2.0}), st("INT", expedite={"level": "interrupt", "at": 3.0})]
got = [x["item"] for x in R.queue_order(states, {"LISTED": 0}, {"SYSTEM": 0})]
ok(got == ["INT", "EXP_OLD", "EXP_NEW", "SYSTEM", "LISTED", "CONTENT"],
   "order: interrupt, expedited oldest first, then system, the list, content", got)

# --- sync: log onto the state, the use into the ledger, expiry by itself
d, s = fresh()
s.save(st("A"))
setit(s, "A", "expedited", 100.0)
fx, acts = Fx(), []
fx.fail_notes = 1
X.sync(s, fx, 100.0, acts)
ok(s.load("A")["expedite"]["level"] == "expedited", "sync: the state carries the level")
ok(not fx.notes and any(a["do"] == "expedite_note_failed" for a in acts), "sync: a failed ledger note is said", acts)
X.sync(s, fx, 110.0, [])
ok(len(fx.notes) == 1 and "by Conductor" in fx.notes[0][1], "sync: tried again, lands once", fx.notes)
X.sync(s, fx, 120.0, [])
ok(len(fx.notes) == 1, "sync: never told twice", fx.notes)
acts = []
X.sync(s, fx, 100.0 + 4 * H, acts)
ok("expedite" not in s.load("A") and any(a["do"] == "expedite_expired" for a in acts), "sync: 4 h on, it lapses by itself, said", acts)
ok("lapsed" in fx.notes[-1][1], "sync: the lapse reaches the ledger too", fx.notes)
shutil.rmtree(d, ignore_errors=True)

# every use is on the digest's reader: the real why, the real reader
fxr = R.Effects.__new__(R.Effects)
calls = []
fxr.rimflow = lambda *a: (calls.append(a), types.SimpleNamespace(returncode=0))[1]
fxr.expedite_note("A", "expedite set")
why = calls[0][calls[0].index("--why") + 1]
rows = DD.ledger_read([{"event": "note", "id": "A", "why": why, "ts": "2026-11-03T21:00:00Z", "seat": "RUNNER"}])
ok(len(rows["items"]) == 1, "digest: the note's why is one the daily digest lists", why)

# --- interrupt makes room; expedited never does
def house(*extra):
    d, s = fresh()
    s.save(st("CONTENT_RUN", status="running", enrolled_at=5.0))
    s.save(st("SYSTEM_RUN", status="running", enrolled_at=9.0))
    for x in extra:
        s.save(x)
    return d, s


INT = {"level": "interrupt", "at": 50.0, "by": "Operations", "why": "disk"}
EXP = {"level": "expedited", "at": 50.0, "by": "Conductor", "why": "soon"}
d, s = house(st("I", expedite=INT))
fx, acts = Fx({"SYSTEM_RUN": 0}), []
stopped = X.make_room(s, fx, RULES, 100.0, acts, 2, "max_workers", R.fail)
ok(stopped == ["CONTENT_RUN"] and s.load("CONTENT_RUN")["status"] == "stopping", "interrupt: a full house stops the content worker", acts)
ok(s.load("SYSTEM_RUN")["status"] == "running", "interrupt: one stop per interrupt, system work kept")
ok(s.load("CONTENT_RUN")["failures"].get("interrupted") == 1 and s.load("CONTENT_RUN")["hold"] is None,
   "interrupt: the stopped item returns; it is not held against itself")
acts = []
ok(X.make_room(s, fx, RULES, 101.0, acts, 2, "max_workers", R.fail) == [], "interrupt: the next tick waits for the place on its way back")
ok(s.load("SYSTEM_RUN")["status"] == "running", "interrupt: a second tick stops nobody more")
shutil.rmtree(d, ignore_errors=True)

d, s = house(st("I", expedite=INT))
ok(X.make_room(s, Fx(), RULES, 100.0, [], 1, None, R.fail) == [], "interrupt: a free place stops nobody")
for why in ("paused", "memory", "breaker open until x: y"):
    acts = []
    ok(X.make_room(s, Fx(), RULES, 100.0, acts, 2, why, R.fail) == [] and "waits" in acts[0]["why"],
       "interrupt: stopping cannot cure %r, nobody stopped, said" % why, acts)
shutil.rmtree(d, ignore_errors=True)

d, s = house(st("E", expedite=EXP))
ok(X.make_room(s, Fx(), RULES, 100.0, [], 2, "max_workers", R.fail) == [] and s.load("CONTENT_RUN")["status"] == "running",
   "expedited: waits for the next place, stops nobody")
shutil.rmtree(d, ignore_errors=True)

d, s = fresh()
s.save(st("LIVE_WORKER", status="running", live_iter={"x": 1}))
s.save(st("OTHER_EXP", status="running", expedite=EXP))
s.save(st("I", expedite=INT))
acts = []
ok(X.make_room(s, Fx(), RULES, 100.0, acts, 2, "max_workers", R.fail) == [] and "nothing it may stop" in acts[-1]["why"],
   "interrupt: never a worker on the live game, never another expedited item; said", acts)
shutil.rmtree(d, ignore_errors=True)

d, s = house(st("I1", expedite=INT), st("I2", expedite=dict(INT, at=60.0)))
stopped = X.make_room(s, Fx({"SYSTEM_RUN": 0}), RULES, 100.0, [], 2, "max_workers", R.fail)
ok(stopped == ["CONTENT_RUN", "SYSTEM_RUN"], "interrupt: two interrupts, content first and system only after it", stopped)
shutil.rmtree(d, ignore_errors=True)

# --- the line while degraded: content stays paused, the lane does not
d, s = fresh()
s.save(st("SYS_Q"))
s.save(st("E", expedite=EXP))
acts = []
R.lease(s, types.SimpleNamespace(first={"SYS_Q": 0}, degraded=True, plan={}, item_state=lambda i: None), dict(RULES, share=1.0), 100.0, acts)
ok(not any("content paused" in (a.get("why") or "") for a in acts), "lease: degraded never pauses an expedited item", acts)
shutil.rmtree(d, ignore_errors=True)

# --- the game: left alone, then the next turn
def game(item, phase, **kw):
    e = kw.pop("expedite", None)
    x = dict(st(item, status=G.GAME), game=dict({"phase": phase}, **kw))
    return dict(x, expedite=e) if e else x


active = game("HOLDER", "proving")
ok(G.other_active([active, game("E", "prove", expedite=EXP)], "E") == "HOLDER", "game: a running user keeps the game, an interrupt's too")
ok(G.other_active([active, game("I", "prove", expedite=INT)], "I") == "HOLDER", "game: interrupt does not stop the live game")
waiting = game("E", "prove", expedite=EXP)
ok(G.other_active([waiting, game("PLAIN", "prove")], "PLAIN") == "E", "game: nothing behind an expedited item starts")
ok(G.other_active([waiting, game("PLAIN", "prove")], "E") is None, "game: the expedited item itself goes")
ok(G.other_active([waiting, game("I", "prove", expedite=INT)], "E") == "I", "game: an interrupt goes before an expedited")
ok(G.other_active([waiting, game("I", "prove", expedite=INT)], "I") is None, "game: and is not held by it")
ok(G.other_active([game("E", "stage", retry_at=999.0, expedite=EXP), game("PLAIN", "prove")], "PLAIN") is None,
   "game: one put down on a retry holds nothing")
ok(G.other_active([game("E", "prove", expedite=EXP)], None) is None, "game: the tick's own 'is anyone live' reading is unchanged")
worker_q = st("E", expedite=EXP)
ok(G.other_active([worker_q, game("PLAIN", "prove")], "PLAIN") is None, "game: an expedited item still at the worker stage takes no game turn")
f = [game("OLD", "final", final_since=1.0), game("E", "final", final_since=9.0, expedite=EXP)]
ok([i for _t, i in G.finals_waiting(f)] == ["E", "OLD"], "game: an expedited final stages the load", G.finals_waiting(f))

# --- the CLI
d, s = fresh()
a = types.SimpleNamespace(verb="set", item="NEVER_FILED_XYZ", level="interrupt", by="Conductor", why="w")
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 2 and not X.read_log(s), "cli: a name never filed is refused")
sys.stdout.flush()
real_pkg = R.pkg
# the real ledger_has on a real spawn-event row: the child's id is in `name`, and it has no later event
R.pkg = lambda n: types.SimpleNamespace(read=lambda: [
    {"seat": "BENCH", "event": "spawn", "name": "BORN_BY_SPAWN_ONLY", "from": "PARENT_X", "for": "BENCH"},
    {"seat": "BENCH", "event": "note", "id": "PARENT_X"}], REPO="")
ok(R.ledger_has("BORN_BY_SPAWN_ONLY"), "ledger_has: an item whose only event is its spawn is filed")
ok(R.ledger_has("PARENT_X"), "ledger_has: an item with an id event is filed")
ok(not R.ledger_has("NEVER_FILED_XYZ"), "ledger_has: a name no event carries is not filed")
# end to end, ledger_has NOT stubbed: `expedite set` on a spawn-only item enrols it
real_cr, R.concept_refused = R.concept_refused, (lambda *x: None)
a.item = "BORN_BY_SPAWN_ONLY"
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 0 and (s.load("BORN_BY_SPAWN_ONLY") or {}).get("status") == "queued",
   "cli: expedite set on an item whose only event is its spawn succeeds")
R.concept_refused = real_cr
R.pkg = real_pkg
real = R.ledger_has, R.concept_refused
R.ledger_has, R.concept_refused = (lambda i: True), (lambda *x: None)
real_pkg = R.pkg
R.pkg = lambda n: types.SimpleNamespace(read=lambda: [], REPO="")
a.item = "BANNED"
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 2, "cli: an item the line retires on sight is refused now, not left 4 h")
a.item = "FRESH"
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 0 and s.load("FRESH")["status"] == "queued", "cli: a set enrols at once, past every cap")
s.save(st("OLD", status="retired"))
a.item = "OLD"
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 0 and s.load("OLD")["status"] == "queued", "cli: a retired item comes back")
s.save(st("DONE", status="done"))
a.item = "DONE"
ok(R.expedite_cli(a, s, 100.0, RULES, {}) == 2, "cli: a done item is refused")
a.item = "WORKER"
ok(R.expedite_cli(a, s, 100.0, RULES, {"RELENTLESS_GEN": "3"}) == 2 and s.load("WORKER") is None,
   "cli: a worker may not, and enrols nothing")
ok(R.expedite_cli(types.SimpleNamespace(verb="list", item=None), s, 100.0, RULES, {}) == 0, "cli: list reads")
ok(any("interrupt" in x for x in X.listing(s, 100.0)), "cli: list names the level")
R.ledger_has, R.concept_refused = real
R.pkg = real_pkg
shutil.rmtree(d, ignore_errors=True)

json.dumps(FAILS)
print("selftest_relentless_expedite: " + ("RED %d: %s" % (len(FAILS), FAILS[:5]) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
