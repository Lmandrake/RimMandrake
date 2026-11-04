#!/usr/bin/env python3
"""selftest_relentless_canary.py -- the live harness's canaries (relentless_canary.py) and their place in the round.

No game, no bridge: a fake world answers the proof shell, the game's start and rimflow. What must hold, each red under
its mutant:
  healthy canaries let the round run and are cached; the cache is reused only for the same fingerprint and within its
  ttl (a sick verdict for a shorter one); a new game, PATH or WSL_INTEROP runs them again; each canary that fails names
  itself and stops the ones after it; the bridge, once taken, is released whatever happened; a bridge that cannot be
  taken caches nothing; an instrument that says yes to a wrong expectation is sick, and so is one that cannot answer;
  run_round stops before any proof when the canaries are sick (in its own process: the service context); and the PATH
  bug itself (a proof shell without Windows on its PATH) fails the interop canary through the real shell.
"""
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_canary as K        # noqa: E402

FAILS = []
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def check(cond, what):
    print("%s %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


class World(object):
    """Answers like a healthy box; `bad` names one canary to break (and how)."""

    def __init__(self, bad=None, started=1000.0, take_rc=0):
        self.bad, self.started, self.take_rc = bad or {}, started, take_rc
        self.calls = []

    def game_started(self):
        return None if self.bad.get("game") else self.started

    def rimflow(self, *a, **kw):
        self.calls.append(("rimflow",) + a)
        if a[:2] == ("bridge", "take"):
            return types.SimpleNamespace(returncode=self.take_rc, stdout="", stderr="busy: OWNER holds it" if self.take_rc else "")
        if a[:2] == ("bridge", "who"):
            return types.SimpleNamespace(returncode=0, stdout=self.bad.get("holder", "driver lock: HELD  RELENTLESS 1 gen 2\nbridge held by RELENTLESS since 2026-11-04T07:33:08Z  for: x"), stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    def shell(self, cmd, timeout):
        self.calls.append(("shell", cmd))
        if cmd.startswith("python.exe -c"):
            return self.bad.get("interop", (0, cmd.split("'")[1] + "\n"))
        if "rimbridge/ping" in cmd:
            return self.bad.get("bridge", (0, '{"ok": true}'))
        if "jawa/running_mods" in cmd:
            return self.bad.get("load", (0, '{"mods": ["ludeon.rimworld", "mandrake.rm.therot"]}'))
        if K.KNOWN in cmd:
            return self.bad.get("known", (0, "PASS ThingDef/Wall from ludeon.rimworld resolves"))
        if K.WRONG in cmd:
            return self.bad.get("wrong", (1, "FAIL %s: does not resolve in the live game" % K.WRONG))
        return 127, "command not found"

    def taken(self):
        return any(c[:3] == ("rimflow", "bridge", "take") for c in self.calls)

    def released(self):
        return any(c[:3] == ("rimflow", "bridge", "release") for c in self.calls)


ENV = {"PATH": "/usr/bin:/mnt/c/WINDOWS/system32", "USER": "mandrake", "WSL_INTEROP": "/run/WSL/1_interop"}


def t_healthy_runs_once_then_cached():
    with tempfile.TemporaryDirectory() as root:
        w = World()
        check(K.gate(w, root, {}, now=5000, env=ENV) is None, "healthy canaries: the round may run")
        rec = K.read(root)
        check(rec and rec["ok"] and [c["name"] for c in rec["checks"]] == list(K.CHECKS),
              "every canary ran, in order, and the verdict is cached with its fingerprint")
        check(w.released(), "the bridge taken for the canaries is released")
        w2 = World()
        check(K.gate(w2, root, {}, now=5000 + 1800, env=ENV) is None and not any(c[0] == "shell" for c in w2.calls),
              "within ttl and the same fingerprint: cached, no shell, no bridge")
        w3 = World()
        K.gate(w3, root, {}, now=5000 + 3700, env=ENV)
        check(any(c[0] == "shell" for c in w3.calls), "past ttl_s: they run again")


def t_fingerprint_changes_rerun():
    for what, env, started in (("a new game", ENV, 2000.0), ("a new PATH", dict(ENV, PATH="/usr/bin"), 1000.0),
                               ("a new WSL_INTEROP", dict(ENV, WSL_INTEROP="/run/WSL/9_interop"), 1000.0)):
        with tempfile.TemporaryDirectory() as root:
            K.gate(World(), root, {}, now=5000, env=ENV)
            w = World(started=started)
            K.gate(w, root, {}, now=5010, env=env)
            check(any(c[0] == "shell" for c in w.calls), "%s: a different fingerprint runs the canaries again" % what)


def t_each_canary_fails_by_name():
    cases = [
        ("interop", {"interop": (127, "bash: python.exe: command not found")}),
        ("game", {"game": True}),
        ("holder", {"holder": "driver lock: HELD  RELENTLESS 1 gen 2\nbridge held by BENCH since 2026-11-04T07:33:08Z"}),
        ("bridge", {"bridge": (1, "ConnectionRefusedError")}),
        ("load", {"load": (0, '{"mods": []}')}),
        ("known", {"known": (2, "UNMEASURED: the reply is not a get_defs answer")}),
        ("wrong", {"wrong": (0, "PASS")}),               # an instrument that says yes to anything
        ("wrong", {"wrong": (2, "UNMEASURED")}),         # one that cannot answer
    ]
    for name, bad in cases:
        with tempfile.TemporaryDirectory() as root:
            w = World(bad)
            why = K.gate(w, root, {}, now=5000, env=ENV)
            rec = K.read(root)
            names = [c["name"] for c in rec["checks"]] if rec else []
            check(why and why.startswith("canary %s:" % name) and names[-1:] == [name] and rec and not rec["ok"],
                  "%s %s: sick, named, the later canaries not run (%s)" % (name, sorted(bad.values())[0], why))
            check(w.released() == w.taken(), "%s: a bridge taken is released" % name)
            w2 = World(bad)     # the same world: a sick game reads no start, which is its own fingerprint
            check(K.gate(w2, root, {}, now=5000 + 300, env=ENV) == why and not w2.calls,
                  "%s: a sick verdict is cached for fail_ttl_s" % name)
            w3 = World(bad)
            K.gate(w3, root, {}, now=5000 + 700, env=ENV)
            check(bool(w3.calls), "%s: and only that long (fail_ttl_s < ttl_s)" % name)


def t_bridge_not_taken_caches_nothing():
    with tempfile.TemporaryDirectory() as root:
        w = World(take_rc=1)
        why = K.gate(w, root, {}, now=5000, env=ENV)
        check(why and why.startswith(K.NOT_TAKEN) and K.read(root) is None and not w.released(),
              "a busy bridge: the round's STOP word, nothing cached, nothing released that was not taken")


def t_disabled():
    with tempfile.TemporaryDirectory() as root:
        w = World({"interop": (1, "x")})
        check(K.gate(w, root, {"live": {"canary": {"enabled": False}}}, now=5000, env=ENV) is None and not w.calls,
              "live.canary.enabled false: no canary runs")


def t_round_stops_on_a_sick_canary():
    import relentless_live_round as RR
    import selftest_relentless_live_round as SR

    class Fx(SR.FakeFx):
        def __init__(self, why):
            SR.FakeFx.__init__(self)
            self.why = why

        def canary(self, root, r, now):
            return self.why
    with tempfile.TemporaryDirectory() as root:
        run, calls = SR.fake_run({})
        s = RR.run_round(Fx("canary interop: python.exe from the proof shell: exit 127"), root, {}, now=1_800_000_000,
                         run=run)
        check(calls == [] and s["why"].startswith("stopped: canary interop") and s["canary"],
              "run_round: sick canaries stop the round before any proof spends a slot")
        run, calls = SR.fake_run({})
        RR.run_round(Fx(None), root, {"live": {"round_max": 2}}, now=1_800_000_000, run=run)
        check(len(calls) == 2, "run_round: healthy canaries let it run")
    check(hasattr(RR.RoundFx, "canary"), "the round's real effects carry the canary (the service context runs it)")


def t_path_bug_fails_interop_for_real():
    """TITANIC's PATH bug, replayed through the real proof shell: a service PATH without Windows cannot reach python.exe,
    and the interop canary says so before any slot is spent."""
    fx = K.ShellFx(types.SimpleNamespace(books=REPO, game_started=lambda: 1000.0))
    old = os.environ.get("PATH")
    os.environ["PATH"] = "/usr/bin:/bin"
    try:
        code, said = fx.shell('python.exe -c "print(\'n\')"', 30)
    finally:
        os.environ["PATH"] = old
    check(code not in (0, None) and "n" != said.strip(), "no Windows on the proof shell's PATH: python.exe does not "
          "answer (exit %s)" % code)
    w = World({"interop": (code, said)})
    with tempfile.TemporaryDirectory() as root:
        why = K.gate(w, root, {}, now=5000, env={"PATH": "/usr/bin:/bin"})
    check(why and why.startswith("canary interop:") and not w.taken(), "and the interop canary fails before the bridge")


def main():
    for t in (t_healthy_runs_once_then_cached, t_fingerprint_changes_rerun, t_each_canary_fails_by_name,
              t_bridge_not_taken_caches_nothing, t_disabled, t_round_stops_on_a_sick_canary,
              t_path_bug_fails_interop_for_real):
        t()
    print("RESULT %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
