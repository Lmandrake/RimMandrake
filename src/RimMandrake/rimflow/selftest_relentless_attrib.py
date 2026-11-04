#!/usr/bin/env python3
"""selftest_relentless_attrib.py -- blame before rebuild, and one incident per shared instrument fault
(REWORK_GATE_BUILD_BLAME_BEFORE_REBUILD, INSTRUMENT_INCIDENT_BUILD_NO_STRIKES; spec
design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md).

A replay of three real endings through the REAL supervisor transitions (R.tick, R.verdict, relentless_game's round,
relentless_block.sweep, relentless_attrib.answer); only the world (ledger, units, game) is faked:

  STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT   the checker FAILed it in prose because its box could not see the disk the
                                            item measures (a SITE/CHECKER fault): the candidate is kept, no strike, no
                                            builder; it waits on the repair and is re-checked on the same sha.
  LEANINGSCRUB_STALL_SHARED_MOVE_1          FAILed on a live game that measured nothing (the shared live harness):
                                            HARNESS, one incident with TITANIC's harness half; released only when the
                                            repair closes AND its fixtures pass, then back in the game on the same sha
                                            with the old rows voided.
  TITANIC_BODYSIZE_TEST_RACE_1              mixed: one clause genuinely violated (PRODUCT) and one unmeasured (HARNESS):
                                            a builder with the strike it earned, and recorded on the incident.
Plus: a known unmet predecessor (REPAINT / COMB_HOLDS shape) is never staffed; a diagnosis that does not answer holds
the item for a person, never a builder; nothing closes on incomplete evidence.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_attrib as A           # noqa: E402
import relentless_incident as I         # noqa: E402
import selftest_relentless as S         # noqa: E402
import selftest_relentless_game as SG   # noqa: E402

ok = S.ok
SHA = SG.SHA
STEVE = "STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT"
LEAN = "LEANINGSCRUB_STALL_SHARED_MOVE_1"
TITANIC = "TITANIC_BODYSIZE_TEST_RACE_1"
HARNESS_FIX = "RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED"
BOX_FIX = "CHECKER_BOX_FIX_DISK_NOT_MOUNTED"
COMB = "COMB_HOLDS_BUILD_PREDECESSOR"
REPAINT = "REPAINT_HOLDS_AFTER_COMB"
GOOD, BAD = "python3 probe.py --mounted D:", "python3 probe.py --mounted Q:"


class World(SG.GW):
    """The game world plus a ledger that holds blocks (BlockWorld's rule) and the supervisor's fixture runner."""

    def __init__(self, items, repairs=()):
        SG.GW.__init__(self, 0)
        self.items = dict({i: "proposed" for i in items}, **{r: "doing" for r in repairs})
        self.blocks, self.closed, self.fixture_exits, self.fixture_runs = {}, {}, {}, []

    def item_state(self, item):
        st = SG.GW.item_state(self, item)
        if st is not None:
            b = self.blocks.get(item)
            holds = bool(b) and not (b[0] == "item" and b[1] and
                                     all(self.items.get(x) in ("done", "dropped") for x in b[1]))
            st.update(block_holds=holds, block=repr(b) if b else None, closed_sha=self.closed.get(item))
        return st

    def ledger_block(self, item, kind, ons, reason):
        if any(o not in self.items for o in ons):
            return "rimflow: no such item %s" % ons
        self.blocks[item] = (kind, list(ons), reason)

    def run_fixture(self, cmd, timeout=180):
        self.fixture_runs.append(cmd)
        return self.fixture_exits.get(cmd, (None, "not run"))

    def close_repair(self, item, sha):
        self.items[item], self.closed[item] = "done", sha


def rig(items, repairs=(), **rules):
    x = S.Rig(1, **dict({"share": 1.0, "max_workers": 3}, **rules))
    x.w = World(items, repairs)
    x.r = dict(x.r, live=dict(x.r.get("live") or {}, auto=False))
    return x


def launches(x, item, role):
    return [z for z in x.w.launches if z[0] == item and ("-%s-" % role) in z[1]]


def strikes(st):
    return sum((st.get("failures") or {}).values())


def checked(x, item, word, why, defects=None):
    """The item finishes on SHA and its blind checker answers `word`."""
    x.run_one(item)
    st = x.st(item)
    if not st.get("contract"):
        R.contract(x.s, item, st["gen"], "python3 selftest_x.py")
    R.finish(x.s, item, st["gen"], SHA, "evidence")
    x.w.up[st["run"]["unit"]] = False
    for _ in range(4):
        if x.st(item)["status"] == "checking":
            break
        x.tick()
    st = x.st(item)
    ok(st["status"] == "checking", "%s reaches its checker" % item)
    R.verdict(x.s, item, st["check"]["nonce"], word, why, defects=defects)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()


def kept(x, item, gen=1):
    st = x.st(item)
    return (st["gen"] == gen and (st.get("candidate") or {}).get("sha") == SHA and strikes(st) == 0
            and not st.get("approach_changes") and x.w.closes == [])


def operator(x, item, targets, **a):
    a.setdefault("evidence", "the deciding log line")
    return A.answer(x.s, item, None, targets, a, x.r, x.now, R, known=lambda i: i in x.w.items)


def t_steve_site_checker():
    """STEVE: the checker's prose FAIL is no PRODUCT; the candidate waits on the box's repair, untouched by time."""
    x = rig([STEVE], [BOX_FIX])
    checked(x, STEVE, "FAIL", "df shows 40G left on C: but the item measures D:, which this box does not mount")
    st = x.st(STEVE)
    ok(kept(x, STEVE) and (st.get("wait") or {}).get("kind") == "attribution" and st["wait"]["sha"] == SHA,
       "a prose FAIL is withheld: the candidate is kept, no strike, no new builder: %s" % st.get("wait"))
    ok(st["status"] == "held" and st["hold"]["kind"] == "attribution",
       "with no consult machinery it is held for a person to attribute, not rebuilt: %s" % st["status"])
    works = len(launches(x, STEVE, "work"))
    for _ in range(4):
        x.tick(3600)
    ok(len(launches(x, STEVE, "work")) == works and kept(x, STEVE), "four hours later: still no builder")
    try:
        operator(x, STEVE, ["SITE", "CHECKER"], repair="NO_SUCH_REPAIR_FILED", fixture_good=GOOD, fixture_bad=BAD)
        ok(False, "a repair id the ledger lacks is refused")
    except ValueError as e:
        ok("never been filed" in str(e), "a repair id the ledger lacks is refused: %s" % e)
    try:
        operator(x, STEVE, ["SITE"], repair=BOX_FIX)
        ok(False, "an instrument wait without release fixtures is refused")
    except ValueError as e:
        ok("fixture" in str(e), "an instrument wait without release fixtures is refused")
    route = operator(x, STEVE, ["SITE", "CHECKER"], repair=BOX_FIX, component="checker box, D: not mounted",
                     fixture_good=GOOD, fixture_bad=BAD)
    ok(route == "wait:" + BOX_FIX, "SITE+CHECKER waits on the repair: %s" % route)
    for _ in range(3):
        x.tick(3600)
    st = x.st(STEVE)
    ok(st["status"] == "blocked" and x.w.blocks.get(STEVE, (None, None))[:2] == ("item", [BOX_FIX]) and kept(x, STEVE),
       "the ledger holds the block on the repair; the candidate is kept: %s %s" % (st["status"], x.w.blocks.get(STEVE)))
    ok(len(launches(x, STEVE, "work")) == works and not launches(x, STEVE, "check")[1:] and not x.w.fixture_runs,
       "a repair dependency is never staffed, re-checked or released by a clock")
    inc = I.get(x.s, BOX_FIX)
    ok(inc and STEVE in inc["items"] and inc["fixtures"] == {"good": GOOD, "bad": BAD}
       and inc["component"].startswith("checker box"), "one incident records component, repro, item and fixtures")
    # the repair closes, but its fixtures refuse: still waiting, an alarm once, no rerun on the next ticks
    x.w.fixture_exits = {GOOD: (1, "Q: still unmounted"), BAD: (1, "not mounted")}
    x.w.close_repair(BOX_FIX, "fix1")
    x.tick()
    x.tick()
    x.tick(3600)
    st = x.st(STEVE)
    ok(st["status"] == "blocked" and kept(x, STEVE) and len(x.w.fixture_runs) == 2,
       "fixtures refuse the repair: it keeps waiting, and the refusal is not rerun on a tick: %d runs" % len(x.w.fixture_runs))
    ok(sum("fixtures refuse" in n for n in x.w.notes) == 1, "the refusal is said once on the ledger")
    # a new close of the repair is a new evidence event: fixtures hold, the same candidate goes back to its checker
    x.w.fixture_exits = {GOOD: (0, "D: 412G free"), BAD: (2, "Q: no such drive")}
    x.w.closed[BOX_FIX] = "fix2"
    x.tick()
    st = x.st(STEVE)
    ok(st["status"] in ("candidate", "checking") and kept(x, STEVE) and not st.get("wait"),
       "the fixtures hold: the same sha resumes at its check, no builder: %s" % st["status"])
    ok(I.get(x.s, BOX_FIX)["status"] == I.RELEASED, "its last parent out releases the incident")
    for _ in range(3):
        if x.st(STEVE)["status"] == "checking":
            break
        x.tick()
    st = x.st(STEVE)
    ok(st["status"] == "checking" and len(launches(x, STEVE, "work")) == works and x.w.closes == [],
       "it is re-checked on %s; nothing closed yet" % SHA)
    R.verdict(x.s, STEVE, st["check"]["nonce"], "PASS", "D: measured: 412G")
    x.w.up[st["check"]["run"]["unit"]] = False
    for _ in range(3):
        x.tick()
    ok(x.w.closes == [(STEVE, SHA)], "only the re-check's PASS closes it, on the kept sha: %s" % x.w.closes)
    x.done()


def game_failed(x, item, crit):
    """`item` passed blind on SHA, entered the game, and the round FAILed `crit`."""
    SG.to_game(x, item)
    x.tick()
    x.tick()
    x.w.rows = [r for r in x.w.rows if r["item"] != item] + [
        {"at": "2099-01-01T00:00:00Z", "item": item, "criterion": crit, "sha": SHA, "outcome": "FAIL",
         "log": "/l/%s.log" % item}]
    x.tick()


def t_shared_harness_incident():
    """LEANINGSCRUB and TITANIC: one broken live harness is one incident; a mixed row still reaches a builder."""
    x = rig([LEAN, TITANIC], [HARNESS_FIX], max_workers=1)
    game_failed(x, LEAN, "A2")
    st = x.st(LEAN)
    ok(kept(x, LEAN) and (st.get("wait") or {}).get("kind") == "attribution" and st["wait"]["resume"] == "game"
       and not st["failures"], "LEANINGSCRUB's game FAIL is withheld: no strike, candidate kept: %s" % st.get("wait"))
    route = operator(x, LEAN, ["HARNESS"], repair=HARNESS_FIX, component="live round: game UP, nothing measured",
                     fixture_good=GOOD, fixture_bad=BAD)
    ok(route == "wait:" + HARNESS_FIX, "HARNESS waits on the harness repair")
    game_failed(x, TITANIC, "A2")
    # mixed: A1 observed violated (the race's body size), A2 unmeasured by the same harness
    route = operator(x, TITANIC, ["PRODUCT", "HARNESS"], repair=HARNESS_FIX, obligation="A1 bodySize 2.4",
                     observed="bodySize 1.0 in the def dump", why_product="the dump is read from the game the harness "
                     "reached; only A2's tick probe was blind")
    st = x.st(TITANIC)
    ok(route == "builder" and st["failures"].get("game_fail") == 1 and not st.get("wait"),
       "the observed violation earns its strike and goes to a builder: %s" % route)
    inc = I.get(x.s, HARNESS_FIX)
    ok(sorted(inc["items"]) == [LEAN, TITANIC] and inc["items"][LEAN]["waits"] and not inc["items"][TITANIC]["waits"],
       "one incident for the shared fault, both items on it; only LEANINGSCRUB waits: %s" % inc["items"])
    for _ in range(4):
        x.tick(3600)
    ok(x.st(LEAN)["status"] == "blocked" and kept(x, LEAN) and not launches(x, LEAN, "work")[1:],
       "LEANINGSCRUB is not staffed while the repair is open")
    ok(len(launches(x, TITANIC, "work")) >= 2, "TITANIC's builder ran")
    voided = len([1 for ln in open(os.path.join(x.s.root, "live", "runs.jsonl"))
                  if '"void"' in ln]) if os.path.exists(os.path.join(x.s.root, "live", "runs.jsonl")) else 0
    x.w.fixture_exits = {GOOD: (0, "ok"), BAD: (1, "nothing measured")}
    x.w.close_repair(HARNESS_FIX, "fix9")
    x.tick()
    st = x.st(LEAN)
    ok(st["status"] == "game" and (st.get("game") or {}).get("sha") == SHA and kept(x, LEAN),
       "the repair closed and its fixtures hold: back in the game on the same sha: %s" % st["status"])
    rows = [json.loads(ln) for ln in open(os.path.join(x.s.root, "live", "runs.jsonl"))]
    ok(len([r for r in rows if r.get("void")]) == voided + 1 and rows[-1]["item"] == LEAN,
       "its old rows on that sha are voided, so the round cannot read the old FAIL again")
    ok(x.w.closes == [], "nothing closed on the release itself")
    x.done()


def t_predecessor_not_staffed():
    """REPAINT waits on COMB (a known unmet predecessor): DEPENDENCY, never staffed until COMB is done."""
    x = rig([REPAINT], [COMB])
    checked(x, REPAINT, "FAIL", "the holds it repaints do not exist yet: COMB_HOLDS_BUILD_PREDECESSOR is open")
    route = operator(x, REPAINT, ["DEPENDENCY"], on=COMB)
    ok(route == "wait:" + COMB, "DEPENDENCY waits on the predecessor")
    works = len(launches(x, REPAINT, "work"))
    for _ in range(5):
        x.tick(3600)
    ok(x.st(REPAINT)["status"] == "blocked" and len(launches(x, REPAINT, "work")) == works and kept(x, REPAINT),
       "a known unmet predecessor: no staffing, no strike, the candidate kept")
    x.w.close_repair(COMB, "c1")
    x.tick()
    ok(x.st(REPAINT)["status"] in ("candidate", "checking") and not x.w.fixture_runs and kept(x, REPAINT),
       "the predecessor done: the same candidate is checked again (a dependency has no fixtures)")
    x.done()


def t_product_and_failed_diagnosis():
    """A structured defect is PRODUCT by itself; a diagnose consult that ends without attributing holds the item."""
    x = rig([TITANIC])
    checked(x, TITANIC, "FAIL", "bodySize 1.0", defects=["A1: bodySize 1.0, owed 2.4"])
    st = x.st(TITANIC)
    ok(st["failures"].get("blind_fail") == 1 and not st.get("wait") and st["attribution"]["targets"] == ["PRODUCT"],
       "a Marker's structured defect is an observed violation: builder, with the strike")
    x.run_one(TITANIC)
    ok("bodySize" in launches(x, TITANIC, "work")[-1][2], "the builder is told the defect")
    x.done()
    x = rig([STEVE], circling=S.HELP)
    checked(x, STEVE, "FAIL", "could not read D:")
    for _ in range(3):
        x.tick()
    con = launches(x, STEVE, "help")
    ok(len(con) == 1 and "DIAGNOSTICIAN" in con[0][2] and con[0][3] == x.r["help_agent"],
       "the withheld FAIL gets one read-only diagnostic consult: %d" % len(con))
    ok(not launches(x, STEVE, "work")[1:] and kept(x, STEVE), "no builder while it diagnoses")
    for _ in range(8):      # each consult ends without `attribute`; the help machinery's own retry is bounded
        for c in launches(x, STEVE, "help"):
            x.w.up[c[1]] = False
        x.tick()
        if x.st(STEVE)["status"] == "held":
            break
    st = x.st(STEVE)
    ok(len(launches(x, STEVE, "help")) <= 3, "the unanswered diagnosis is retried a bounded number of times: %d"
       % len(launches(x, STEVE, "help")))
    ok(st["status"] == "held" and st["hold"]["kind"] == "attribution" and kept(x, STEVE)
       and not launches(x, STEVE, "work")[1:], "a diagnosis that does not answer holds it for a person, never a builder")
    x.done()
    # a diagnosis that answers PROOF goes to the proof road on the same sha, not to the code
    x = rig([STEVE], circling=S.HELP)
    checked(x, STEVE, "FAIL", "the proof greps the wrong log")
    for _ in range(3):
        x.tick()
    nonce = x.st(STEVE)["help"]["nonce"]
    route = A.answer(x.s, STEVE, nonce, ["PROOF"], {"evidence": "proof reads Player-prev.log"}, x.r, x.now, R)
    st = x.st(STEVE)
    ok(route == "proof" and st["last_fail"]["class"] == A.PROOF_OWED and (st.get("proof_only") or {}).get("sha") == SHA
       and not st["failures"].get("blind_fail"), "PROOF: the proof road, code frozen at the sha, no strike: %s" % route)
    try:
        A.answer(x.s, STEVE, nonce, ["PRODUCT"], {"evidence": "x", "obligation": "o", "observed": "o",
                                                  "why_product": "w"}, x.r, x.now, R)
        ok(False, "a nonce answers once")
    except R.Fenced:
        ok(True, "a nonce answers once")
    x.done()


def main():
    for t in (t_steve_site_checker, t_shared_harness_incident, t_predecessor_not_staffed, t_product_and_failed_diagnosis):
        t()
    if S.FAILS:
        print("FAIL: %d" % len(S.FAILS))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
