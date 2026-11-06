#!/usr/bin/env python3
"""Release fixture for PITPRISON_CHAIN_FIX_LEFTOVERS_PICK_FIGHTS (PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES's HARNESS wait).

Live 2026-11-05: pit_prison_room vanished its fixtures only on a clean chain end. A surprise abort in capture_down_off
left colonist Boy 86561 and an unarmed hostile (Crab 86565) brawling on plot G, so runs 2 and 3 stopped UNMEASURED on
Boy's hurt/downed. This runs the REAL chain (extensions.pit_prison_room at --rev) against a fake bridge that records
every call, offline, 0 ticks:

  --case abort-mid-chain  a wait inside capture_down_off raises a surprise stop: every pawn the chain spawned must still
                          get a vanish call after its spawn, and the stop must propagate (not be swallowed).
  --case clean            no abort: every spawned pawn is vanished at the end.
  --case stray-hostiles   the map already holds an earlier run's leftovers: a living hostile far off the plot and a
                          living colonist on plot G must be vanished BEFORE the chain's first spawn; a dead hostile and
                          an off-plot friendly colonist must be left alone.
  --rev REV               a git revision whose extensions.py to judge (default WORKTREE: the file on disk)
Prints FIXTURE_VERDICT: PASS (exit 0) | FAIL (exit 1); a source it cannot load prints UNMEASURED (exit 2), no verdict."""
import argparse
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = "src/RimMandrake/FlowWorks/northstar/extensions.py"
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class SurpriseStop(Exception):
    """Stands in for a safe_advance stop that ends the chain (not an ExpectationFailed a component absorbs)."""


def load_ext(rev):
    if rev == "WORKTREE":
        import extensions as EXT  # noqa: E402
        return EXT
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, REL)], capture_output=True, text=True)
    if r.returncode != 0:
        raise OSError(r.stderr.strip() or "git show failed")
    mod = types.ModuleType("extensions_at_%s" % rev.replace("~", "_").replace("^", "_"))
    mod.__file__ = os.path.join(HERE, "extensions.py")
    exec(compile(r.stdout, mod.__file__, "exec"), mod.__dict__)
    return mod


class _Session(object):
    def __init__(self, t):
        self.t = t

    def call(self, tool, **kw):
        return self.t.bridge_call(tool, **kw)


class _Comp(object):
    def __init__(self, t, name):
        self.t, self.name = t, name

    def __enter__(self):
        self.t.calls.append(("component", {"name": self.name}))
        return self

    def __exit__(self, et, ev, tb):
        return et is not None and issubclass(et, self.t.EF)    # a component absorbs its own ExpectationFailed only


class FakeT(object):
    anchor = (125, 125)

    def __init__(self, EXT, abort_in=None, strays=(), drop_vanish=False):
        self.EF = EXT.ExpectationFailed
        self.calls, self.records = [], []
        self.abort_in, self.strays, self.drop_vanish = abort_in, list(strays), drop_vanish
        self.n_spawn, self.cur, self.fixtures = 0, None, []
        self.session = _Session(self)
        self.alive = {p["id"] for p in self.strays if not p.get("dead")}

    def _guard(self):
        return True

    def _record(self, what, data=None):
        self.records.append(what)

    def component(self, name, toggle=None, **kw):
        self.cur = name
        return _Comp(self, name)

    def set_setting(self, typ, values):
        self.calls.append(("set_setting", dict(values)))

    def wait_ticks(self, n):
        self.calls.append(("wait_ticks", {"n": n, "component": self.cur}))
        if self.abort_in and self.cur == self.abort_in:
            raise SurpriseStop("safe_advance stopped: hurt colonist (fixture)")

    def bridge_call(self, tool, **kw):
        if tool == "jawa/pawn_force_incapacitate" and self.drop_vanish:
            return {"success": True}
        self.calls.append((tool, kw))
        if tool == "jawa/spawn_pawn":
            self.n_spawn += 1
            pid = "Thing_Fixture%d" % self.n_spawn
            self.alive.add(pid)
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/pawn_force_incapacitate":
            self.alive.discard(kw.get("pawn"))
            return {"success": True, "destroyedAfter": True}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(p) for p in self.strays]}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "Thing_Bed1"}]}
        if tool == "jawa/static_call":
            m = kw.get("method")
            if m == "ProofResetRect":
                return {"success": True, "result": "RESET cells=0 left=0"}
            return {"success": True, "result": "VERDICT Allowed prisoner=True split=True pitRoom=True edge=False "
                                               "prison=True serve=True kind=Interact lipInPit=False dist=2"}
        return {"success": True}


def spawned_ids(t):
    """The chain's own fixtures (what _spawn_pawn_at returned); a colony keeper _keep_colony spawns is meant to stay."""
    return list(t.fixtures)


def run_chain(EXT, t):
    del EXT._SPAWNED[:]
    real = EXT._spawn_pawn_at

    def spy(t_, *a, **kw):
        pid = real(t_, *a, **kw)
        t_.fixtures.append(pid)
        return pid
    EXT._spawn_pawn_at = spy
    try:
        EXT.pit_prison_room(t)
    except SurpriseStop:
        return "stopped"
    finally:
        EXT._spawn_pawn_at = real
    return "ended"


def case_abort(EXT, drop_vanish=False):
    t = FakeT(EXT, abort_in="capture_down_off", drop_vanish=drop_vanish)
    how = run_chain(EXT, t)
    probs = []
    if how != "stopped":
        probs.append("the surprise stop in capture_down_off did not propagate out of the chain (%s)" % how)
    ids = spawned_ids(t)
    if len(ids) < 3:
        probs.append("instrument blind: only %d pawn(s) spawned before the abort (expected hostile, warden, h2)" % len(ids))
    left = sorted(set(ids) & t.alive)
    if left:
        probs.append("pawns left alive after the abort: %s" % left)
    return probs


def case_clean(EXT, drop_vanish=False):
    t = FakeT(EXT, drop_vanish=drop_vanish)
    how = run_chain(EXT, t)
    probs = [] if how == "ended" else ["clean run did not end (%s)" % how]
    ids = spawned_ids(t)
    if len(ids) < 3:
        probs.append("instrument blind: only %d pawn(s) spawned" % len(ids))
    left = sorted(set(ids) & t.alive)
    if left:
        probs.append("pawns left alive after a clean end: %s" % left)
    return probs


def stray_rows(EXT):
    x0, z0 = EXT._plot(FakeT(EXT), "G")
    far = (x0 + EXT.PW + EXT.PLOT_BUFFER + 30, z0 + 2)
    return [
        {"id": "Thing_StrayCrab", "hostile": True, "isPlayer": False, "dead": False, "spawned": True,
         "x": far[0], "z": far[1], "intelligence": "Humanlike"},
        {"id": "Thing_StrayBoy", "hostile": False, "isPlayer": True, "dead": False, "spawned": True,
         "x": x0 + 3, "z": z0 + 3, "intelligence": "Humanlike"},
        {"id": "Thing_DeadRaider", "hostile": True, "isPlayer": False, "dead": True, "spawned": False,
         "x": x0 + 4, "z": z0 + 4, "intelligence": "Humanlike"},
        {"id": "Thing_KeeperOffPlot", "hostile": False, "isPlayer": True, "dead": False, "spawned": True,
         "x": far[0], "z": far[1] + 3, "intelligence": "Humanlike"},
    ]


def case_strays(EXT, drop_vanish=False):
    t = FakeT(EXT, strays=stray_rows(EXT), drop_vanish=drop_vanish)
    run_chain(EXT, t)
    probs = []
    first_spawn = next((i for i, (tool, _) in enumerate(t.calls) if tool == "jawa/spawn_pawn"), None)
    if first_spawn is None:
        probs.append("instrument blind: the chain spawned nothing")
    vi = {}
    for i, (tool, kw) in enumerate(t.calls):
        if tool == "jawa/pawn_force_incapacitate" and kw.get("action") == "vanish":
            vi.setdefault(kw.get("pawn"), i)
    for sid in ("Thing_StrayCrab", "Thing_StrayBoy"):
        if sid not in vi:
            probs.append("stray %s was never vanished" % sid)
        elif first_spawn is not None and vi[sid] > first_spawn:
            probs.append("stray %s vanished only after the chain's first spawn" % sid)
    for kid in ("Thing_DeadRaider", "Thing_KeeperOffPlot"):
        if kid in vi:
            probs.append("%s should have been left alone but was vanished" % kid)
    return probs


CASES = {"abort-mid-chain": case_abort, "clean": case_clean, "stray-hostiles": case_strays}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--case", choices=sorted(CASES), required=True)
    ap.add_argument("--rev", default="WORKTREE")
    a = ap.parse_args(argv)
    try:
        EXT = load_ext(a.rev)
    except Exception as e:                                   # noqa: BLE001
        print("UNMEASURED: cannot load extensions.py at %s: %s: %s" % (a.rev, type(e).__name__, e))
        return 2
    probs = CASES[a.case](EXT)
    print("fixture_pit_prison_cleanup --case %s --rev %s" % (a.case, a.rev))
    for p in probs:
        print("  - " + p)
    print("FIXTURE_VERDICT: %s" % ("PASS" if not probs else "FAIL"))
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
