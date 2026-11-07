#!/usr/bin/env python3
"""selftest_owner_queue.py — RELENTLESS_NOW's "Needs you" and the mods' "waits on you" are one test (offline, fake items).

FLEETWATCH_NEEDS_FIX_NOTHING_WHILE_MODS_WAIT: the header said "Nothing." while ten mods said "waits on you".
Covers: which routings count as his (Relentless tooling holds do not; owner_call and a flyer game hold do), the
question line (questions file wins, title fallback), fleet_mods.waits_on agreeing with is_his on every case, and
fleet_mods.receipts choosing between a detached and a Relentless run of the same item.
"""
import contextlib
import io
import os
import sys
import tempfile
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import owner_queue as Q  # noqa: E402
import fleet_mods as M  # noqa: E402

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
    "N_FLYER_WORD": it("owner"),
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
    "N_FLYER_WORD": held("game", "game phase: refused again unchanged: proof selftest_flyer_body.py changed since the build"),
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
check("nothing his -> empty text, count 0", (none["count"], none["lines"], none["text"], none["topics"], none["answered"]) == (0, [], "", [], []))
check("the seat queue is every tooling hold", [k for k, _, _ in Q.seat_queue(rel)] == ["B_PROOF_WEAK", "C_SPEND", "F_GAMESTAGE", "N_FLYER_WORD"])
check("misrouted lists tooling holds", [k for k, _ in Q.misrouted(items, rel)] == ["B_PROOF_WEAK", "C_SPEND", "F_GAMESTAGE", "N_FLYER_WORD"])



def run_main(*flags):
    """owner_queue's own main(), the flag parsing and printing included, on the fixture store: -> (exit code, lines)."""
    saved = sys.argv, M.ledger, M.relentless_states, Q.designer_turns
    cli_items = dict(items, M_STRIKES=it("owner"))
    cli_rel = dict(rel, M_STRIKES=held("strikes", "3 strikes"))
    sys.argv, M.ledger, M.relentless_states = ["owner_queue.py"] + list(flags), (lambda: ([], NS(items=cli_items))), (lambda **_: cli_rel)
    Q.designer_turns = lambda root=None: {}  # the live Designer queue is not the fixture's (it leaked real turns in, 2026-11-05)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc = Q.main()
    finally:
        sys.argv, M.ledger, M.relentless_states, Q.designer_turns = saved
    return rc, out.getvalue().splitlines()


# RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS: --seat is the road the tooling holds go down, so the flag itself is pinned (blind
# check, gap 1: `if a.seat:` -> `if False:` stayed green while seat_queue() alone was called).
rc, rows = run_main("--seat")
check("--seat prints the tooling holds, proof_weak, strikes and a non-flyer game hold, and nothing else",
      rc == 0 and rows == ["B_PROOF_WEAK\tproof_weak\t2 returns and the proof still reads weak", "C_SPEND\tspend\titem spend limit",
                           "F_GAMESTAGE\tgame\tgame phase: stage failed twice", "M_STRIKES\tstrikes\t3 strikes",
                           "N_FLYER_WORD\tgame\tgame phase: refused again unchanged: proof selftest_flyer_body.py changed since the build"])
check("--seat omits owner_call and a flyer's flight", not [r for r in rows if r.startswith(("D_OWNER_CALL", "E_FLYER"))])
rc, rows = run_main()
check("no flag is his list, with no tooling hold on it",
      rc == 0 and rows[0] == "%d truly his" % len(his) and {r.split("\t")[0] for r in rows[1:len(his) + 1]} == his)
rc, rows = run_main("--misrouted")
check("--misrouted stays its own answer", rc == 0 and rows == ["B_PROOF_WEAK\tproof_weak", "C_SPEND\tspend", "F_GAMESTAGE\tgame", "M_STRIKES\tstrikes", "N_FLYER_WORD\tgame"])

with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "q.json")
    with open(p, "w") as f:
        f.write("[1, 2]")
    check("a malformed questions file reads as empty", Q.load_questions(p) == {})
    check("a missing questions file reads as empty", Q.load_questions(os.path.join(d, "none.json")) == {})
q = Q.load_questions()
check("repo questions file: one non-empty line each", q and all(isinstance(v, str) and v.strip() and "\n" not in v
                                                                 for v in q.values()))

W = NS(items={"Z": NS(open=False, needs="offline", blocked=False, blocked_kind=None, title="z", state="done",
                     verdict=None)})
RZ = {"Z": {"status": "done", "done_at": 1999999000, "enrolled_at": 1999998000, "verdict": "PASS"}}
rc = M.receipts(2000000000, {}, RZ, W, [], [{"item": "Z", "status": "Done", "started": 1999998500, "finished_at": 1999999500}])
check("a newer detached run beats an older Relentless one", len(rc) == 1 and rc[0]["finished_at"] == 1999999500)
rc = M.receipts(2000000000, {}, RZ, W, [], [{"item": "Z", "status": "Done", "started": 1999997000, "finished_at": 1999999500}])
check("an older run finishing later does not", len(rc) == 1 and rc[0].get("relentless"))

# RUNNING_PAGE_FIX_REVIEW_LEFTOVERS: an answered item leaves the list; a later routing gives it back
evs = [{"event": "file", "needs": "owner", "seat": "OWNER"}, {"event": "note", "seat": "BENCH", "text": "t"}, {"event": "note", "seat": "OWNER", "text": "RULED"},
       {"event": "needs", "to": "owner", "seat": "BENCH"}]
def hist(*idx):
    x = it("owner")
    x.history = list(idx)
    return x
check("no note from him: not answered", not Q.answered(hist(0, 1), evs))
check("his note after the routing: answered", Q.answered(hist(0, 2), evs))
check("routed again after his note: his again", not Q.answered(hist(0, 2, 3), evs))
check("no events given: stays on the list", not Q.answered(hist(0, 2), None))
check("no routing event on record: stays on the list", not Q.answered(hist(2), evs))
check("is_his honours answered only with events", Q.is_his(hist(0, 2), None) and not Q.is_his(hist(0, 2), None, evs))
items2 = {"DRAW_A": hist(0), "DRAW_B": hist(0), "DRAW_C": hist(0, 2), "K_X": hist(0)}
n = Q.needs_you(items2, {}, {"DRAW_A": "Look?", "DRAW_B": "Press?"}, evs)
check("answered items are named, not counted", n["count"] == 3 and [a["item"] for a in n["answered"]] == ["DRAW_C"])
check("a shared leading word folds to one row", [t["topic"] for t in n["topics"]] == ["DRAW", "K"] and n["topics"][0]["items"] == ["DRAW_A", "DRAW_B"] and n["topics"][0]["others"] == ["Press?"])

# OWNER_QUEUE_FIX_FIRST_TOUCH_NEEDS_PASS: a first-touch row is his once its Designer pass exists, and stays open before that
def ftit(iid, needs="owner"):
    x = it(needs, title="pass on " + iid)
    x.id = iid
    return x


with tempfile.TemporaryDirectory() as root:
    def concept(name, files, stage=None):
        d = os.path.join(root, name)
        os.makedirs(d)
        for f in files:
            open(os.path.join(d, f), "w").close()
        if stage is not None:
            with open(os.path.join(d, "stage.json"), "w") as f:
                f.write(stage)
    concept("Done", ["result.run-1.json"])
    concept("Rejected", ["result.run-1.rejected.json"])
    concept("Unclosed", ["result.json"])
    concept("Empty", [])
    concept("Odd_Name", ["result.run-2.json"], '{"item": "HANDFILED_DESIGN_FIRST_TOUCH"}')
    concept("Garbled", ["result.run-3.json"], "{not json")
    concept("_dry_walk", ["result.run-4.json"])
    passes = Q.read_designer_passes(root)
    check("an accepted result is a pass; rejected, unclosed, empty and _dry_walk are not",
          passes == {"DONE_DESIGN_FIRST_TOUCH", "ODDNAME_DESIGN_FIRST_TOUCH", "HANDFILED_DESIGN_FIRST_TOUCH", "GARBLED_DESIGN_FIRST_TOUCH"})
    check("an unreadable concepts root answers None, never an empty set", Q.read_designer_passes(os.path.join(root, "no_such")) is None)
    check("designer_passes reads the root it is given", Q.designer_passes(root) == passes)
    concept("Late", ["result.run-5.json"])
    check("the memo holds inside its window", "LATE_DESIGN_FIRST_TOUCH" not in Q.designer_passes(root))
    at, got = Q._passes_memo[root]
    Q._passes_memo[root] = (at - Q.PASSES_TTL - 1, got)
    check("a long-lived board sees a new result after the window", "LATE_DESIGN_FIRST_TOUCH" in Q.designer_passes(root))

ft = {i: ftit(i) for i in ("BARE_DESIGN_FIRST_TOUCH", "DONE_DESIGN_FIRST_TOUCH", "TURN_DESIGN_FIRST_TOUCH", "HELD_DESIGN_FIRST_TOUCH", "SAID_DESIGN_FIRST_TOUCH")}
ft["OFFLINE_DESIGN_FIRST_TOUCH"] = ftit("OFFLINE_DESIGN_FIRST_TOUCH", "offline")
ft["PLAIN_OWNER_ASK"] = ftit("PLAIN_OWNER_ASK")
ft["BARE_DESIGN_FIRST_TOUCH"].history = [0]
ft["SAID_DESIGN_FIRST_TOUCH"].history = [0, 2]
ftrel = {"HELD_DESIGN_FIRST_TOUCH": held("proof_weak", "weak")}
ftpass = {"DONE_DESIGN_FIRST_TOUCH"}
ftturn = {"TURN_DESIGN_FIRST_TOUCH": "Turn waits on you"}
n = Q.needs_you(ft, ftrel, {}, evs, ftturn, passes=ftpass)
check("listed: a row with a result, a row with a waiting turn, and any non-first-touch ask, and no bare row",
      [x["item"] for x in n["lines"]] == ["DONE_DESIGN_FIRST_TOUCH", "PLAIN_OWNER_ASK", "TURN_DESIGN_FIRST_TOUCH"])
check("the waiting turn's line is its question", {x["item"]: x["q"] for x in n["lines"]}["TURN_DESIGN_FIRST_TOUCH"] == "Turn waits on you")
check("a passless row is named, not lost; his answered row and a tooling hold are not on that list",
      [x["item"] for x in n["awaiting_designer"]] == ["BARE_DESIGN_FIRST_TOUCH"] and [x["item"] for x in n["answered"]] == ["SAID_DESIGN_FIRST_TOUCH"])
check("the row stays open: needs_you changes no item", ft["BARE_DESIGN_FIRST_TOUCH"].open and ft["BARE_DESIGN_FIRST_TOUCH"].needs == "owner")
saved = Q.designer_passes
Q.designer_passes = lambda root=None: None
try:
    check("a concepts root that cannot be read leaves the row on his list, never hides it", Q.is_his(ftit("X_DESIGN_FIRST_TOUCH"), None) and not Q.awaiting_designer(ftit("X_DESIGN_FIRST_TOUCH")))
    Q.designer_passes = lambda root=None: {"DONE_DESIGN_FIRST_TOUCH"}
    # the page's tags read the same test with no passes passed: they must agree with the header on the same answer
    check("waits_on and is_his agree with no passes passed", M.waits_on(ft["BARE_DESIGN_FIRST_TOUCH"], None, []) == "" and M.waits_on(ft["DONE_DESIGN_FIRST_TOUCH"], None, []) == "you")
    check("the mods' stuck line says who it waits on", (M.stuck_of(ft["BARE_DESIGN_FIRST_TOUCH"], None, [])["waits"] == "the Designer"
                                                        and M.stuck_of(ft["DONE_DESIGN_FIRST_TOUCH"], None, [])["waits"] == "you"))
    check("a non-first-touch row never asks the Designer's folder", not Q.awaiting_designer(ft["PLAIN_OWNER_ASK"]))
finally:
    Q.designer_passes = saved

# the real books: every first-touch row routed to him is on exactly one list, and a listed one has its pass or its turn
real_evs, real_w = M.ledger()
real_turns, real_passes = Q.designer_turns(), Q.read_designer_passes(os.path.join(Q.REPO, "design", "concepts"))  # this tree, whichever clone runs it
n = Q.needs_you(real_w.items, {}, {}, real_evs, real_turns, passes=real_passes)
first_touch_suffix = Q.first_touch.SUFFIX
listed = {x["item"] for x in n["lines"] if x["item"].endswith(first_touch_suffix)}
real_routed = {i for i, x in real_w.items.items() if i.endswith(first_touch_suffix) and Q.routed(x)}
check("real books: the concepts root reads", real_passes is not None)
check("real books: no listed first-touch row lacks a pass or a turn", all(i in real_passes or i in real_turns for i in listed))
check("real books: every routed first-touch row is on a list", real_routed <= listed | {x["item"] for x in n["awaiting_designer"]} | {x["item"] for x in n["answered"]})
print("real books: %d first touches listed, %d awaiting their Designer pass" % (len(listed), len(n["awaiting_designer"])))

print("RESULT %s (%d fail)" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
