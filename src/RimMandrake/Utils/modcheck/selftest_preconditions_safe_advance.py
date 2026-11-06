"""selftest_preconditions_safe_advance -- a safe_advance STOP is clockgate's to judge, not a precondition fault.

GAMEENV_FIX_PROOFSITE_73C8F2D0_ITEMS_WAIT: Contagion's coalescence_emits_manhunters_and_grows_on_its_own declares its own
manhunter emission (clockgate.expected_disturbance). advance_chunk resumed past the hostile_arrival stop, but the
_ReportingSession had already handed the stopped reply (success False) to Preconditions.reply, which recorded it as a
HARNESS 'refused' fault, so the row read "UNMEASURED (a precondition did not hold; PASS withheld)".
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["RIMBRIDGE_GOVERNOR_LOG"] = ""     # the fake stops below must not land in the real governor_stops.jsonl

import clockgate as cg  # noqa: E402
import preconditions as PC  # noqa: E402
from suite import _ReportingSession  # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


EMIT = {"seq": 21, "kind": "hostile_arrival", "severity": "threat", "tick": 26561,
        "detail": "RM_Unfinished arrived hostile", "subjectId": 90001}
RAID = {"seq": 22, "kind": "hostile_arrival", "severity": "threat", "tick": 26561,
        "detail": "Pirate arrived hostile", "subjectId": 90002}


def stopped(trig, req, ex):
    return {"success": False, "state": "stopped", "requested": req, "executed": ex, "stopBy": trig, "triggers": [trig]}


class FakeSession(object):
    """Answers jawa/safe_advance from a script of replies (the real companion's shapes)."""
    tools = {cg.SAFE_ADVANCE}

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        return self.replies.pop(0)


def run(replies, expect_pred):
    pre = PC.Preconditions()
    s = _ReportingSession(FakeSession(replies), pre)
    raised = None
    with pre.scope("coalescence_emits_manhunters_and_grows_on_its_own"):
        try:
            if expect_pred is None:
                cg.advance_chunk(s, 400)
            else:
                with cg.expected_disturbance("Coalescence emits manhunter Unfinished", expect_pred):
                    cg.advance_chunk(s, 400)
        except cg.GovernorStop as e:
            raised = e
        verdict = pre.judge("PASS", "MOD", "grew and emitted")[0]
    return verdict, raised, s._s.calls


def emission(t):
    return t.get("kind") == "hostile_arrival" and "RM_Unfinished" in str(t.get("detail"))


# 1. the live instance: a declared emission stops the chunk, it resumes and finishes -> PASS stands
v, raised, calls = run([stopped(EMIT, 400, 300), {"success": True, "state": "done", "requested": 100, "executed": 100}],
                       emission)
ok(raised is None, "a declared emission stop is resumed, no GovernorStop")
ok(len(calls) == 2, "resumed with a second safe_advance call (%d calls)" % len(calls))
ok(v == "PASS", "the resumed declared stop leaves the row's PASS standing (got %s)" % v)

# 2. an undeclared stop (a real raid) still ends the row: GovernorStop, never a silent PASS
v, raised, _ = run([stopped(RAID, 400, 300)], emission)
ok(raised is not None, "an undeclared hostile arrival still raises GovernorStop")

# 3. no expectation at all: the emission stop is a GovernorStop too
v, raised, _ = run([stopped(EMIT, 400, 300)], None)
ok(raised is not None, "with nothing declared, the same stop raises GovernorStop")

# 4. a real refusal is still a precondition fault
ok(PC.refusal(cg.SAFE_ADVANCE, {}, {"success": False, "state": "refused", "refused": "over budget"}) is not None,
   "a safe_advance refusal (state refused) is still a HARNESS fault")
ok(PC.refusal(cg.SAFE_ADVANCE, {}, {"success": False, "state": "stopped", "refused": True}) is not None,
   "a stopped reply that also carries refused is still a fault")
ok(PC.refusal("jawa/spawn_pawn", {}, {"success": False, "state": "stopped"}) is not None,
   "the exemption is safe_advance's alone")
ok(PC.refusal(cg.SAFE_ADVANCE, {}, stopped(EMIT, 400, 300)) is None,
   "a latch stop of safe_advance is not a refusal")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
