"""rimdrive.selftest -- offline proof of the mutate/reconnect/litter contracts.

No socket, no game. Everything here is decidable on this side of the socket,
and a live bridge session costs a game load or at least a live driver's
attention -- see bridgetools/load_session.py's own docstring for why an
item's plumbing gets proven here first, the same discipline this package
inherits.

    python3 src/RimMandrake/Utils/rimdrive/selftest.py

Picked up automatically by run_selftests.py (glob `selftest*.py` under src/).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
# Only the PARENT goes on sys.path -- never `_HERE` itself. `session.py`
# imports `verify` via `from .verify import ...` (bound to the package name
# `rimdrive.verify`); if this file also put `_HERE` on sys.path, an
# unqualified `import verify` would load a SECOND copy of that module under
# the bare name `verify`, and its `UNVERIFIED = object()` sentinel would be a
# different object from the one `rimdrive.verify` created -- every `is
# UNVERIFIED` identity check below would then silently fail for the wrong
# reason. Import everything through the package name, always.
if _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)

from rimdrive import verify as v  # noqa: E402
from rimdrive.session import Session, SessionError  # noqa: E402
import rimdrive.session as session_mod  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s  %s" % (name, detail))
        FAILURES.append(name)


class Scripted(object):
    """The bare surface `verify.mutate()` needs: `strict`, counters, `log()`.
    Not a `Session` -- `mutate()` is a free function taking any duck-typed
    session-like object, which this test leans on directly."""

    def __init__(self):
        self.strict = True
        self.mutations = 0
        self.no_ops = []
        self.unverified = []
        self.logged = []

    def log(self, msg):
        self.logged.append(msg)


# --------------------------------------------------------- verify.mutate()

def t_mutate_happy_path():
    s = Scripted()
    got = v.mutate(s, "spawn X", lambda: None, lambda: True)
    check("mutate: happy path returns truthy", got is True)
    check("mutate: happy path counts one mutation", s.mutations == 1)
    check("mutate: happy path has no no-ops", s.no_ops == [])


def t_mutate_noop_strict_raises():
    s = Scripted()
    try:
        v.mutate(s, "paint nothing", lambda: None, lambda: False)
        check("mutate: strict no-op raises Unchanged", False)
    except v.Unchanged:
        check("mutate: strict no-op raises Unchanged", True)
    check("mutate: strict no-op is still recorded", s.no_ops == ["paint nothing"])


def t_mutate_noop_nonstrict_logs():
    s = Scripted()
    s.strict = False
    got = v.mutate(s, "paint nothing", lambda: None, lambda: False)
    check("mutate: non-strict no-op returns None", got is None)
    check("mutate: non-strict no-op logs it",
          any("NO-OP" in m for m in s.logged), s.logged)


def t_mutate_unverified_is_not_a_noop():
    s = Scripted()
    got = v.mutate(s, "set stuff, no cell", lambda: None, lambda: v.UNVERIFIED)
    check("mutate: UNVERIFIED sentinel returned as-is", got is v.UNVERIFIED)
    check("mutate: UNVERIFIED tracked separately from no_ops",
          s.unverified == ["set stuff, no cell"] and s.no_ops == [])


def t_mutate_reconnect_then_verified_is_success():
    s = Scripted()
    calls = {"n": 0}

    def do():
        calls["n"] += 1
        if calls["n"] == 1:
            raise v.Reconnected("died mid-call")

    got = v.mutate(s, "spawn X", do, lambda: True)
    check("mutate: reconnect + post-condition true -> success", got is True)
    check("mutate: post-condition already satisfied -> no blind retry",
          calls["n"] == 1)


def t_mutate_reconnect_then_unresolved_is_indeterminate():
    s = Scripted()

    def do():
        raise v.Reconnected("died mid-call")

    try:
        v.mutate(s, "spawn X", do, lambda: False, idempotent=False)
        check("mutate: reconnect + still-false + non-idempotent -> Indeterminate",
              False)
    except v.Indeterminate:
        check("mutate: reconnect + still-false + non-idempotent -> Indeterminate",
              True)


def t_mutate_reconnect_idempotent_retries_once():
    s = Scripted()
    calls = {"n": 0}
    verifies = {"n": 0}

    def do():
        calls["n"] += 1
        if calls["n"] == 1:
            raise v.Reconnected("died mid-call")

    def verify():
        verifies["n"] += 1
        return verifies["n"] >= 2   # false right after reconnect, true on retry

    got = v.mutate(s, "spawn X", do, verify, idempotent=True)
    check("mutate: declared-idempotent retry succeeds", got is True)
    check("mutate: declared-idempotent retry calls do() exactly twice",
          calls["n"] == 2)


# --------------------------------------------------------- Session.sweep()

def _bare_session():
    """A real `Session` with `__init__` never run -- no socket opened, no
    entry in the one-per-process registry. `sweep()`'s actual logic is what's
    under test, not a reimplementation of it."""
    s = Session.__new__(Session)
    s.strict = True
    s.quiet = True
    s.calls = 0
    s.mutations = 0
    s.no_ops = []
    s.unverified = []
    s.litter = []
    return s


def t_sweep_things_destroys_and_verifies_empty():
    s = _bare_session()
    seen = []

    def fake_call(tool, **p):
        seen.append((tool, p))
        if tool == "rimworld/get_cell_info":
            return {"success": True, "cell": {"things": []}}   # empty after the destroy
        return {"success": True}

    s.call = fake_call
    s.track("thing", "Thing_1", x=5, z=5)
    result = s.sweep()
    check("sweep: a tracked thing -> destroy_batch(categories=All)",
          any(t == "jawa/destroy_batch" and p.get("categories") == "All"
              for t, p in seen), seen)
    check("sweep: fully swept thing reports nothing left",
          result == {"swept": 1, "left": []}, result)


def t_sweep_pawn_still_alive_is_reported_left():
    s = _bare_session()

    def fake_call(tool, **p):
        if tool == "jawa/list_pawns":
            return {"pawns": [{"id": "Pawn_1"}]}   # still there after teardown
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    result = s.sweep()
    check("sweep: a pawn that survived teardown is reported, never hidden",
          result["swept"] == 0 and len(result["left"]) == 1, result)


def t_sweep_pawn_gone_counts_swept():
    s = _bare_session()

    def fake_call(tool, **p):
        if tool == "jawa/list_pawns":
            return {"pawns": []}
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    result = s.sweep()
    check("sweep: a pawn confirmed gone counts as swept",
          result == {"swept": 1, "left": []}, result)


def t_sweep_pawn_kill_overrides_the_colonist_safety_rail():
    """MEASURED live 2026-09-12: a modcheck component's own player-faction
    test walker is genuine PlayerColony litter, and jawa/damage's safety
    rail silently refused to kill it without allowColonists=True -- the
    pawn walked back onto the map alive when its container was destroyed.
    This asserts the fix stays fixed."""
    s = _bare_session()
    seen = []

    def fake_call(tool, **p):
        seen.append((tool, p))
        if tool == "jawa/list_pawns":
            return {"pawns": []}
        return {"success": True}

    s.call = fake_call
    s.track("pawn", "Pawn_1", x=9, z=9)
    s.sweep()
    damage_calls = [p for t, p in seen if t == "jawa/damage"]
    check("sweep: killing litter passes allowColonists=True",
          len(damage_calls) == 1 and damage_calls[0].get("allowColonists") is True,
          damage_calls)


def t_sweep_empty_litter_makes_no_calls():
    s = _bare_session()
    called = []
    s.call = lambda tool, **p: called.append(tool) or {"success": True}
    result = s.sweep()
    check("sweep: nothing tracked -> no calls at all, not even a read",
          result == {"swept": 0, "left": []} and called == [], (result, called))


def t_one_session_per_process():
    sentinel = object()
    session_mod._ACTIVE.append(sentinel)
    try:
        try:
            Session()
            ok = False
        except SessionError:
            ok = True
    finally:
        session_mod._ACTIVE.remove(sentinel)
    check("one Session per process is enforced", ok)


TESTS = [
    t_mutate_happy_path,
    t_mutate_noop_strict_raises,
    t_mutate_noop_nonstrict_logs,
    t_mutate_unverified_is_not_a_noop,
    t_mutate_reconnect_then_verified_is_success,
    t_mutate_reconnect_then_unresolved_is_indeterminate,
    t_mutate_reconnect_idempotent_retries_once,
    t_sweep_things_destroys_and_verifies_empty,
    t_sweep_pawn_still_alive_is_reported_left,
    t_sweep_pawn_gone_counts_swept,
    t_sweep_pawn_kill_overrides_the_colonist_safety_rail,
    t_sweep_empty_litter_makes_no_calls,
    t_one_session_per_process,
]


def main():
    for t in TESTS:
        t()
    passed = len(TESTS) - len(FAILURES)
    print("\nSELFTEST %s -- %d/%d passed"
          % ("FAILED" if FAILURES else "OK", passed, len(TESTS)))
    if FAILURES:
        print("  failed: %s" % ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
