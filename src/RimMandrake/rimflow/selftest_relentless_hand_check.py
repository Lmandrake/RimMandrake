#!/usr/bin/env python3
"""PIPELINE_BLESS_ENFORCE_HAND_CHECKS_SMALL (owner 2026-11-05: "The pipeline is NOT to be used to bless any change in
the game. That's a huge expenditure for a small validation that could be manually performed."). An item whose only
remaining work is a hand check is never enrolled (eligible, pool_why) and never rechecked: one already in the store is
bounced to its maker with a ledger note, its lease handed back, and retired before any check. Ordinary items are
untouched. Planted items on a temp store, the real rules file read for its shape. No units, no network."""
import os
import sys
import tempfile
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_pool_why as P  # noqa: E402

FAILS = []
REAL = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
NOW = 1_800_000_000


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def item(i, title="", **kw):
    base = dict(id=i, owner=REAL["pool_seats"][0], state="proposed", needs=REAL["pool_needs"][0], kind="task",
                target=None, lease=None, blocked=False, blocked_reason=None, blocked_on=None, blocked_kind=None,
                blocked_until=None, blocked_lift_at=None, blocked_also=(), title=title, makers=[], built_by=None)
    base.update(kw)
    return NS(**base)


r = dict(REAL)
r["pool_ids_exclude"], r["pool_parked_lists"] = [], {}
r["hand_check"] = {"ids": {"ART_PICK_CONFIRM_INSTALLED": "installed art is his pick"},
                   "title_rx": [r"(?i)^(first )?live look\b", r"(?i)\b(it is built|it exists)\b.{0,40}\bverify\b"]}

# --- the rule itself
ok(bool(REAL.get("hand_check", {}).get("title_rx")), "the real rules carry hand_check.title_rx")
ok(R.hand_check(item("ART_PICK_CONFIRM_INSTALLED"), r) == "installed art is his pick", "an id in hand_check.ids is one")
ok(bool(R.hand_check(item("SIGNS_X", "Live look on the walk save: signs are signboards"), r)), "a title pattern is one")
ok(bool(R.hand_check(item("ROSTER_X", "GPT says no tree - it is built, verify the listing"), r)), "built-verify title")
plain = item("HOSE_FIX_TERRAIN_WONT_READ_BACK", "set_terrain_batch leaves cells that do not read back")
ok(R.hand_check(plain, r) is None, "real work is not a hand check (a read-back BUG)", R.hand_check(plain, r))
ok(R.hand_check(item("PIPELINE_BLESS_ENFORCE_HAND_CHECKS_SMALL",
                     "Enforce the 2026-11-05 ruling: Relentless refuses ... a deploy landed ..."), REAL) is None,
   "the real rules never match the item that built them (its candidate would be bounced, not checked)")
ok(R.hand_check(item("X"), {}) is None, "no hand_check rule: nothing is one")

# --- enrolment: eligible and pool_why
W = NS(items={})
ok(not R.eligible(item("ART_PICK_CONFIRM_INSTALLED"), r), "eligible refuses a hand check")
ok(R.eligible(item("BUILD_THING_FIX_IT", "Fix the thing"), r), "eligible admits ordinary work")
rs = P.reasons(item("ART_PICK_CONFIRM_INSTALLED"), W, r, NOW)
ok(rs == ["hand_check"], "pool_why names hand_check", rs)


# --- the store: bounce, never recheck
class Fx:
    def __init__(self, items):
        self.w = NS(items={i.id: i for i in items})
        self.notes, self.reclaims, self.note_fail = [], [], None

    def ledger_items(self):
        return None, self.w

    def ledger_note(self, item, text):
        if self.note_fail:
            return self.note_fail
        self.notes.append((item, text))

    def ledger_reclaim(self, item):
        self.reclaims.append(item)


tmp = tempfile.mkdtemp(prefix="hand_check_")
store = R.Store(tmp)
rows = {"ART_PICK_CONFIRM_INSTALLED": ("candidate", "doing", ["BENCH", "ARTIST"]),
        "SIGNS_X": ("queued", "proposed", []),
        "BUILD_THING_FIX_IT": ("candidate", "doing", []),
        "ROSTER_X": ("running", "doing", [])}
for i, (status, _, _) in rows.items():
    st = R.new_state(i, NOW, "test")
    st["status"] = status
    st["ledger_started"] = status != "queued"
    if status == "candidate":
        st["candidate"] = {"sha": "a" * 40}
    store.save(st)
fx = Fx([item(i, {"SIGNS_X": "Live look on the walk save", "ROSTER_X": "it is built, verify the listing"}.get(i, ""),
              state=led, makers=mk) for i, (_, led, mk) in rows.items()])
fx.note_fail = "ledger busy"
acts = []
R.hand_back(store, fx, r, NOW, acts)
ok(store.load("ART_PICK_CONFIRM_INSTALLED")["status"] == "candidate", "a refused note changes nothing: next tick")
ok(any(a["do"] == "hand_back_waits" for a in acts), "and says it waits", acts)
fx.note_fail, acts = None, []
R.hand_back(store, fx, r, NOW, acts)
ok(store.load("ART_PICK_CONFIRM_INSTALLED")["status"] == "retired", "a hand-check candidate is retired, never checked")
ok(store.load("SIGNS_X")["status"] == "retired", "a queued hand check is retired")
ok(store.load("BUILD_THING_FIX_IT")["status"] == "candidate", "an ordinary candidate keeps its check")
ok(store.load("ROSTER_X")["status"] == "running", "a running hand check is left to end (bounced as a candidate)")
ok(fx.reclaims == ["ART_PICK_CONFIRM_INSTALLED"], "the lease we hold on the ledger is handed back", fx.reclaims)
notes = dict(fx.notes)
ok(set(notes) == {"ART_PICK_CONFIRM_INSTALLED", "SIGNS_X"}, "one note per bounced item", sorted(notes))
n = notes.get("ART_PICK_CONFIRM_INSTALLED", "")
ok(n.startswith(R.HAND_CHECK_SAID), "the note says what to do first", n)
ok("BENCH, ARTIST" in n and "installed art is his pick" in n and len(n) <= R.NOTE_MAX, "names maker and why", n)
ok(any(a.get("end") == "hand_check" for a in store.attempts("SIGNS_X")), "the attempt log records the bounce")
fx.notes, acts = [], []
R.hand_back(store, fx, r, NOW, acts)
ok(fx.notes == [] and acts == [], "a retired item is never told twice", (fx.notes, acts))
st = store.load("ROSTER_X")
st["status"], st["candidate"] = "candidate", {"sha": "b" * 40}
store.save(st)
R.hand_back(store, fx, r, NOW, acts)
ok(store.load("ROSTER_X")["status"] == "retired", "its candidate is bounced on the next tick, before the check")
ok(R.hand_back(store, NS(), r, NOW, []) is None, "an Fx with no ledger reader bounces nothing")


# --- eligible by title pattern (the clause the id test alone left open)
ok(not R.eligible(item("SIGNS_X", "Live look on the walk save: signs are signboards"), r),
   "eligible refuses a hand check matched by title pattern alone")
ok(R.eligible(item("SIGNS_Y", "Signs render as signboards on the walk save"), r), "the same subject as real work enrols")

# --- the real tick: hand_back runs inside R.tick() before any check or launch (a direct call proves the helper only)
import selftest_relentless as T  # noqa: E402


def t_tick_never_checks_or_launches_a_hand_check():
    x = T.Rig(n=4)                              # share 0.5 of 4: I0 and I1 enrol
    x.r["hand_check"] = {}                      # both enrolled and built before the rule
    for i in ("I0", "I1"):
        x.run_one(i)
        st = x.st(i)
        R.contract(x.s, i, st["gen"], "proof", live="once: test")
        R.finish(x.s, i, st["gen"], "sha1", "evidence")
        x.w.up[st["run"]["unit"]] = False
    q = R.new_state("I2", x.now, "test")        # a queued hand check, never yet launched
    x.s.save(q)
    x.w.items["I2"] = "proposed"
    world = NS(items={"I0": item("I0", "Fix the thing", state="doing", owner=x.r.get("seat"), makers=["ARTIST"]),
                      "I1": item("I1", "Fix the other thing", state="doing", owner=x.r.get("seat")),
                      "I2": item("I2", "Live look on the walk save", state="proposed")})
    x.w.ledger_items = lambda: (None, world)
    x.r["hand_check"] = {"ids": {"I0": "a value reads back"}, "title_rx": [r"(?i)^live look\b"]}
    before = len(x.w.launches)
    x.tick()
    x.tick()
    later = [l[:2] for l in x.w.launches[before:]]   # (item, unit): the prompt is pages long
    ok(x.st("I0")["status"] == "retired", "tick(): a hand-check candidate ends retired", x.st("I0")["status"])
    ok(not x.st("I0").get("check"), "tick(): no check was started on it", x.st("I0").get("check"))
    ok(not [l for l in later if l[0] == "I0"], "tick(): nothing launched for the hand-check candidate", later)
    ok(x.st("I2")["status"] == "retired", "tick(): a queued hand check (title pattern) ends retired", x.st("I2")["status"])
    ok(not [l for l in later if l[0] == "I2"], "tick(): the queued hand check is never launched", later)
    ok(any(R.HAND_CHECK_SAID in n for n in x.w.notes), "tick(): its maker gets the note", x.w.notes)
    # sanity probe: the same tick does check ordinary work, so the rig can see a check start
    ok(x.st("I1")["status"] == "checking", "tick(): the ordinary candidate beside it is checked", x.st("I1")["status"])
    x.done()


t_tick_never_checks_or_launches_a_hand_check()

# --- lint
probs = R.hand_check_lint({"hand_check": {"ids": {"NOT_FILED_X": "w", "ART_PICK_CONFIRM_INSTALLED": ""},
                                          "title_rx": ["("]}}, {"ART_PICK_CONFIRM_INSTALLED": 1})
ok(len(probs) == 3, "lint finds an unfiled id, an empty why and a bad pattern", probs)

print("FAIL %d" % len(FAILS) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)
