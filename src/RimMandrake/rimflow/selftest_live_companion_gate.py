#!/usr/bin/env python3
"""selftest_live_companion_gate.py -- LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED: a live proof that drives JawaBench runs
only on a game folder whose companion DLL was built from the build's sources, and the staging deploys it.

BRIDGE_STALL_DIAGNOSTIC_1's companion-only fix e26a661423 read A1 FAIL twice on the hand-deployed d62e3e51 DLL
(companion_identity STALE): the round deployed mod folders only. What must hold, each red under its mutant:
  * `live-companion: JawaBench` is read (wrapped, commented); any other name is refused;
  * a build touching a companion compile input owes the companion without the line; a README there, or a mod, does not;
  * owed and STALE / UNSTAMPED / MISSING -> UNMEASURED "not deployed" (the game phase restages), game-stamped, no bridge;
  * owed and FRESH -> the proof runs; FRESH but written after the game started -> "not deployed";
  * an unreadable identity -> UNMEASURED that is not "not deployed" (no restage) and no bridge;
  * not owed -> the companion is never read;
  * the real Fx reads BridgeTools/JawaBench beside the Mods folder and judges it against the build's sources;
  * the round passes companion=True for a file with the line;
  * the stage plan carries the hash, the prompt says so, the stager builds in the shutdown window, and refuses before
    anything is written when its clone's companion sources are not the build's.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bridgetools"))
import relentless_live as L     # noqa: E402
import relentless_live_round as R     # noqa: E402
import relentless_game as G     # noqa: E402
import relentless_stage as S    # noqa: E402
import companion_identity as CI     # noqa: E402
import selftest_relentless_live as TL   # noqa: E402
import selftest_relentless_stage as TS  # noqa: E402

FAILS = []
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CS = L.COMPANION_SRC + "JawaBenchStallTools.cs"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append((name, detail))


class CompFx(TL.FakeFx):
    def __init__(self, comp=None, **kw):
        TL.FakeFx.__init__(self, **kw)
        self.comp = comp

    def companion(self, sha):
        self.calls.append(("companion", sha))
        return dict(self.comp)


def v(state, mtime=1500.0):
    return {"state": state, "embedded": "a" * 64 if state in ("FRESH", "STALE") else None,
            "want": None if state == "UNMEASURED" else "a" * 64 if state == "FRESH" else "b" * 64,
            "dll": "/g/BridgeTools/JawaBench/JawaBench.BridgeTools.dll", "build_commit": None, "mtime": mtime}


def go(fx, companion=False):
    root = tempfile.mkdtemp(prefix="rl_comp_")
    return L.run(fx, root, "ROT_X", "A2", "python3 x.py", "--mod TheRot", {}, now=1_800_000_000, companion=companion)


def t_line():
    check("line: bare", R.companion_line("live-companion: JawaBench\n") is True)
    check("line: wrapped and commented", R.companion_line("- `live-companion: JawaBench` # stall tools") is True)
    check("line: absent", R.companion_line("live-mods: Graffiti\nlive-proof A1: echo x") is False)
    try:
        R.companion_line("live-companion: Oracle")
        check("line: another name is refused", False)
    except ValueError:
        check("line: another name is refused", True)


def t_touched():
    check("touched: a companion .cs owes it", L.companion_touched(TL.FakeFx(touched=[CS]), TL.SHA) is True)
    check("touched: a README in the folder does not",
          L.companion_touched(TL.FakeFx(touched=[L.COMPANION_SRC + "README.md"]), TL.SHA) is False)
    check("touched: a mod build does not", L.companion_touched(TL.FakeFx(), TL.SHA) is False)
    check("touched: bin/ is no compile input",
          L.companion_touched(TL.FakeFx(touched=[L.COMPANION_SRC + "bin/x.cs"]), TL.SHA) is False)


def t_gate():
    for st in ("STALE", "UNSTAMPED", "MISSING"):
        fx = CompFx(v(st))
        row = go(fx, companion=True)
        check("gate: %s is not deployed, no bridge" % st, row["outcome"] == "UNMEASURED"
              and row["why"].startswith(L.UNDEPLOYED[0]) and "take" not in fx.verbs() and "proof" not in fx.verbs()
              and row.get("game") is not None and row["companion"]["state"] == st, row)
    fx = CompFx(v("FRESH"))
    row = go(fx, companion=True)
    check("gate: FRESH runs the proof", row["outcome"] == "PASS" and "proof" in fx.verbs()
          and row["companion"]["state"] == "FRESH", (row, fx.calls))
    fx = CompFx(v("FRESH", mtime=2500.0))
    row = go(fx, companion=True)
    check("gate: FRESH but deployed after the game started is not deployed",
          row["outcome"] == "UNMEASURED" and row["why"].startswith(L.UNDEPLOYED[0]) and "take" not in fx.verbs(), row)
    fx = CompFx(v("UNMEASURED"))
    row = go(fx, companion=True)
    check("gate: an unreadable identity is no restage and no bridge",
          row["outcome"] == "UNMEASURED" and not row["why"].startswith(L.UNDEPLOYED) and "take" not in fx.verbs()
          and "identity could not be read" in row["why"], row)
    fx = CompFx(v("STALE"))
    row = go(fx, companion=False)
    check("gate: not owed, never read", row["outcome"] == "PASS" and "companion" not in fx.verbs(), fx.calls)
    fx = CompFx(v("STALE"), touched=TL.TOUCHED + [CS])
    row = go(fx, companion=False)
    check("gate: a build touching the companion owes it without the line",
          row["outcome"] == "UNMEASURED" and row["why"].startswith(L.UNDEPLOYED[0]), row)
    fx = TL.FakeFx()
    row = go(fx, companion=True)
    check("gate: an Fx with no companion reader measures nothing", row["outcome"] == "UNMEASURED"
          and "take" not in fx.verbs(), row)


def t_real_fx():
    want = CI.srchash_at(REPO, "HEAD")
    if want is None:
        check("real fx: HEAD's companion sources hash (sanity probe)", False, "srchash_at gave None")
        return
    with tempfile.TemporaryDirectory() as d:
        mods = os.path.join(d, "RimWorld", "Mods")
        os.makedirs(mods)
        fx = L.Fx(books=REPO, mods_dir=mods)
        check("real fx: no DLL reads MISSING", fx.companion("HEAD")["state"] == "MISSING")
        dll = os.path.join(d, "RimWorld", "BridgeTools", "JawaBench", CI.DLL_NAME)
        CI.write_fixture(dll, want)
        got = fx.companion("HEAD")
        check("real fx: the build's hash reads FRESH, with its mtime",
              got["state"] == "FRESH" and abs(got["mtime"] - os.path.getmtime(dll)) < 1, got)
        CI.write_fixture(dll, "0" * 64)
        check("real fx: another hash reads STALE", fx.companion("HEAD")["state"] == "STALE")


def t_round():
    import selftest_relentless_live_round as TR
    seen = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=(), site=None, trees=(), **kw):
        seen.append((item_id, kw.get("companion")))
        return {"item": item_id, "criterion": cid, "outcome": "PASS", "why": "x", "sha": "abc123"}

    class Fx(TR.FakeFx):
        def proofs(self, i):
            return TR.PROSE + ("\nlive-companion: JawaBench\n" if i == "EG_A" else "")
    with tempfile.TemporaryDirectory() as root:
        R.run_round(Fx(), root, {"live": {"round_max": 2}}, now=1_800_000_000, run=run)
    check("round: the line passes companion=True, its absence nothing",
          dict(seen).get("EG_A") is True and dict(seen).get("EG_B") is None, seen)


def t_stage():
    st = {"item": "I0", "gen": 3, "game": {"full": None}}
    p = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], ["Armoury"], [], None, None, companion="c" * 64)
    check("stage plan: carries the companion hash", p.get("companion") == "c" * 64, p)
    p = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], ["Armoury"], [], None, None)
    check("stage plan: none owed, no key", "companion" not in p, p)
    txt = G.stage_prompt(st, {"seat": "BENCH"}, "abc", companion="c" * 64)
    check("stage prompt: names build.py --gm --apply", "build.py --gm --apply" in txt)

    class Ops(TS.FakeOps):
        def __init__(self, have, **kw):
            TS.FakeOps.__init__(self, **kw)
            self.have = have

        def companion_hash(self):
            self.calls.append(("hash",))
            return self.have

        def companion_build(self):
            self.calls.append(("companion_build",))
            return 0, "deployed."
    plan = dict(TS.PLAN, companion="c" * 64, remedy_cmds=[])
    ops = Ops("c" * 64)
    verdict, text = S.run(plan, ops)
    seq = TS.tags(ops)
    check("stager: builds the companion in the shutdown window", verdict == "ready" and "companion_build" in seq
          and seq.index("kill") < seq.index("companion_build") < seq.index("launch") and "companion JawaBench" in text,
          (seq, text))
    ops = Ops("d" * 64)
    verdict, text = S.run(plan, ops)
    seq = TS.tags(ops)
    check("stager: another clone's companion stops it before anything is written",
          verdict == "snag" and "kill" not in seq and "apply" not in seq and "companion_build" not in seq, (seq, text))
    ops = Ops("c" * 64)
    ops.companion_build = lambda: (1, "REFUSING TO DEPLOY")
    verdict, text = S.run(plan, ops)
    check("stager: a failed companion build snags", verdict == "snag" and "build.py" in text, text)
    ops = TS.FakeOps()
    verdict, _ = S.run(dict(TS.PLAN, remedy_cmds=[]), ops)
    check("stager: no companion owed, no build", verdict == "ready" and "companion_build" not in TS.tags(ops))


def main():
    for t in (t_line, t_touched, t_gate, t_real_fx, t_round, t_stage):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a crash is a red, named
            import traceback
            traceback.print_exc()
            FAILS.append((t.__name__, "crashed: %r" % e))
    if FAILS:
        print(json.dumps(FAILS, default=str)[:2000])
    print("selftest_live_companion_gate:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
