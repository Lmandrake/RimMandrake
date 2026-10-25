#!/usr/bin/env python3
"""Selftest for src/RimMandrake/Minerals/validation.py's LIVE suite, run offline against a fake game.

The fake answers jawa/static_call (RM_MineralPolicyProof.ProofState / ProofApply) and jawa/mod_settings_field the way
RM_MineralPolicy.cs does: ProofApply re-applies and sets the last reason to "proof: <why>". Every chain runs in
registration order, each with a fresh TestContext (as modcheck's runner does).

What it guards: reassert_on_game_init reads the last apply reason, which any ProofApply overwrites. When it sat after the
toggles rows it could only ever read "proof: ..." and record UNMEASURED - a live row that could never PASS or FAIL.
On a fresh game (reason "Game.FinalizeInit") it must PASS; with a reason that says the re-assert never ran it must FAIL.
A planted probe checks that the fake really switches the reason, so a vacuous pass cannot hide.

    python3 selftest_minerals_validation.py [path/to/validation.py]
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from modcheck import TestContext  # noqa: E402

VALIDATION = os.path.join(HERE, "..", "Minerals", "validation.py")
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def load(path):
    spec = importlib.util.spec_from_file_location("minerals_validation_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeGame(object):
    """The parts of a running game the suite reads. Weights change only on an apply, as in RM_MineralPolicy."""

    def __init__(self, v, reason, quarry="ok"):
        self.v = v
        self.quarry = quarry          # "ok" | "absent" | "leak" (a Grey Sea draw yields a component)
        self.settings = dict(v.DEFAULTS)
        self.rev = 2
        self.reason = reason
        self.weights = {}
        self._apply()

    def _apply(self):
        on, sup = self.settings["enabled"], self.settings["suppressUnregistered"]
        self.weights = {
            "MineableComponentsIndustrial": (0.0 if on else 1.0, 0.0, "componentsindustrial"),
            "MineablePlasteel": (0.0 if on else 0.4, 0.0, "plasteel"),
            "MineableSteel": (0.0 if (on and sup) else 1.0, 0.0, "unregistered"),
            "Steel": (0.0, 0.0 if (on and sup) else 4.0, "unregistered"),
        }

    def state(self, defs):
        out = "rev=%d;rows=31;decided=40;unreg=2;placer=0;reason=%s" % (self.rev, self.reason)
        for n in (defs or "").split(";"):
            if not n:
                continue
            w = self.weights.get(n)
            out += ";%s=%s" % (n, "missing" if w is None else "%g/%g/%s" % w)
        return out

    def proof_quarry(self, args):
        """RM_MineralQuarryProof.ProofQuarry's format: draws count every roll, rock the empty-pool rolls."""
        biome, _, n = args.partition(";")
        n = int(n or 1)
        if self.quarry == "absent":
            return "quarry=0;wired=0;yield=0;on=1;biome=%s;share=0;local=;unreg=;draws=;rock=0" % biome
        on = self.settings["quarryFollowsLocal"]
        if biome == "RM_GreySea":
            local = "salt_halite:RM_Halite:300,salt_sylvite:RM_Sylvite:300"
            unreg, share = "", "0"
            a = n // 2
            draws = ("ComponentIndustrial:%d,RM_Halite:%d" if self.quarry == "leak" else "RM_Halite:%d,RM_Sylvite:%d") % (a, n - a)
            rock = 0
        else:
            local, unreg, share = "", "Gold:20,Silver:50,Steel:60", "0.8667"
            a = n * 13 // 15
            draws, rock = "Steel:%d" % a, n - a
        return "quarry=1;wired=%d;yield=1;on=%d;biome=%s;share=%s;local=%s;unreg=%s;draws=%s;rock=%d" % (
            1 if on else 0, 1 if on else 0, biome, share, local, unreg, draws, rock)

    def call(self, tool, **kw):
        if tool == "jawa/static_call" and kw.get("method") == "ProofQuarry":
            if kw.get("type") != self.v.QUARRY_PROOF_TYPE:
                return {"success": False, "error": "no such type %s" % kw.get("type")}
            return {"success": True, "result": self.proof_quarry(kw.get("args", ""))}
        if tool == "jawa/static_call":
            if kw["method"] == "ProofState":
                return {"success": True, "result": self.state(kw.get("args", ""))}
            if kw["method"] == "ProofApply":
                self.rev += 1
                self.reason = "proof: " + kw.get("args", "")
                self._apply()
                return {"success": True, "result": self.state("")}
        if tool == "jawa/mod_settings_field":
            f = kw["field"]
            if kw["action"] == "get":
                return {"value": str(self.settings[f])}
            cur = self.v.DEFAULTS[f]
            raw = kw["value"]
            self.settings[f] = (raw.strip().lower() == "true") if isinstance(cur, bool) else float(raw)
            return {"success": True}
        return {"success": False, "error": "fake does not know %s" % tool}


def run(v, reason, quarry="ok"):
    game = FakeGame(v, reason, quarry)
    rows = {}
    for name, fn in v.suite.chains:
        t = TestContext(game)
        fn(t)
        for c in t.components:
            rows["%s.%s" % (name, c.name)] = (c.verdict, c.detail)
    return rows, game


def find(rows, comp):
    hits = [(k, r) for k, r in rows.items() if k.endswith("." + comp)]
    return hits[0] if hits else (None, (None, None))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else VALIDATION
    v = load(path)
    ok(v.suite is not None, "validation.py builds its suite on the modcheck path")
    if v.suite is None:
        print("FAIL %d" % len(FAILS))
        return 1

    # probe: the fake must overwrite the reason on an apply, else the ordering check below is vacuous
    g = FakeGame(v, "Game.FinalizeInit")
    g.call("jawa/static_call", type=v.PROOF_TYPE, method="ProofApply", args="x")
    ok(g.reason == "proof: x", "fake: ProofApply overwrites the last reason (probe)")

    rows, game = run(v, "Game.FinalizeInit")
    key, (verdict, detail) = find(rows, "reassert_on_game_init")
    ok(verdict == "PASS", "fresh game: %s is PASS (got %s: %s)" % (key, verdict, detail))
    ok(game.reason.startswith("proof:"), "the suite did re-apply after reading it (so order mattered): %r" % game.reason)
    for comp in ("registry_loaded", "probe_can_say_absent", "components_and_plasteel_zeroed", "unregistered_steel_kept",
                 "master_off_restores", "suppress_unregistered_zeroes_steel"):
        k, (vd, dt) = find(rows, comp)
        ok(vd == "PASS", "fresh game: %s is PASS against the faithful fake (got %s: %s)" % (k, vd, dt))

    for comp in ("quarry_wired", "grey_sea_draws_local_salts", "vanilla_biome_keeps_unregistered"):
        k, (vd, dt) = find(rows, comp)
        ok(vd == "PASS", "fresh game: %s is PASS against the faithful fake (got %s: %s)" % (k, vd, dt))
    k, (vd, _) = find(rows, "quarry_yields_salt_in_game")
    ok(vd == "UNMEASURED", "the in-game quarry look is owed to eyes: %s is UNMEASURED (got %s)" % (k, vd))

    rows, _ = run(v, "Game.FinalizeInit", quarry="leak")
    k, (vd, _) = find(rows, "grey_sea_draws_local_salts")
    ok(vd == "FAIL", "a Grey Sea quarry that yields a component: %s is FAIL (got %s)" % (k, vd))
    rows, _ = run(v, "Game.FinalizeInit", quarry="absent")
    for comp in ("quarry_wired", "grey_sea_draws_local_salts", "vanilla_biome_keeps_unregistered"):
        k, (vd, _) = find(rows, comp)
        ok(vd == "UNMEASURED", "Quarry not loaded: %s is UNMEASURED, never PASS (got %s)" % (k, vd))
    k, (vd, _) = find(rows, "registry_loaded")
    ok(vd == "PASS", "Quarry absent does not blank registry_loaded: got %s" % vd)

    rows, _ = run(v, "startup")
    key, (verdict, _) = find(rows, "reassert_on_game_init")
    ok(verdict == "FAIL", "the re-assert never ran (reason 'startup'): %s is FAIL (got %s)" % (key, verdict))
    k, (vd, _) = find(rows, "registry_loaded")
    ok(vd == "PASS", "a reassert FAIL does not blank registry_loaded (own chain): got %s" % vd)

    rows, _ = run(v, "proof: earlier run")
    key, (verdict, _) = find(rows, "reassert_on_game_init")
    ok(verdict == "UNMEASURED", "a session someone already proved in: %s is UNMEASURED (got %s)" % (key, verdict))

    print(("FAIL %d" % len(FAILS)) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
