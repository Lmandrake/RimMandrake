#!/usr/bin/env python3
"""STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION: a staging makes a load that LACKS the mods a proof is `live-without`.

Before: stage_prompt and the stager only ran modlist_swap.py --enable, so a proof needing a list without X
(GENERATOR_MODS_PROVE_INERT_AFTER_CREATION A2, live-without oblitus.mylittleplanet: four UNMEASURED runs) ran on
whatever list was up. Now batch_gap reports the batch's live-without mods, the supervisor runs modlist_swap.py
--disable on them after its enable, the stage plan carries them as `without` (the stager takes them off again after
its own swap and enable, before the launch), and the fallback brief says so.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_game as G  # noqa: E402
import relentless_live_round as LR  # noqa: E402
import relentless_stage as S  # noqa: E402
import selftest_relentless_stage as T  # noqa: E402

X = "oblitus.mylittleplanet"
FAILS = []


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def t_batch_gap():
    import selftest_relentless_needs as N
    fx = N.GapFx({"lead": ["KeelHoist"]})
    fx.names_index = lambda: N.index(defs=N.DEFS)
    g = LR.batch_gap(fx, [("lead", "live-without: UtinniPatches\nlive-proof A1: true\n", "L")])
    ok(g.get("without") == ["UtinniPatches"] and "UtinniPatches" not in g["mods"],
       "batch_gap names the mods the load must lack: %s" % g.get("without"))
    g = LR.batch_gap(fx, [("lead", "live-proof A1: true\n", "L")])
    ok(g.get("without") == [], "and none when no proof is live-without")


def t_plan_and_prompt():
    gaps = [{"mods": ["KeelHoist"], "without": [X]}, {"without": ["a.b"]}]
    ok(G.without_set(gaps) == sorted([X, "a.b"]), "without_set: the union over the batch")
    ok(G.without_set([{}], {"toggle": "t.t", "side": "without"}) == ["t.t"], "a toggle's without side is one of them")
    ok(G.without_set([{}], {"toggle": "t.t", "side": "with"}) == [], "its with side is not")
    st = {"item": "I0", "gen": 1, "game": {"full": None}}
    plan = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], ["KeelHoist"], [], None, None, without=[X])
    ok(plan.get("without") == [X] and "toggle" not in plan, "stage_plan carries without with no toggle: %s" % plan)
    plan = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], [], [], None, None)
    ok("without" not in plan, "and no without key when nothing must be off")
    r = {"seat": "RELENTLESS"}
    pr = G.stage_prompt(st, r, "abc", (), ["KeelHoist"], without=[X])
    ok("MOD LIST WITHOUT: the next load must LACK %s" % X in pr and
       "modlist_swap.py --disable %s --apply" % X in pr, "the fallback brief names the mods and the --disable command")
    pr = G.stage_prompt(st, r, "abc", (), ["KeelHoist"])
    ok("MOD LIST WITHOUT: no mod must be kept off" in pr, "and says so when there are none")


class Ops(T.FakeOps):
    """FakeOps whose live list is `have`; --disable takes its names off it (unless `stuck`), --minimal keeps X on (the
    stored minimal list holding it, the case only a removal can fix)."""
    def __init__(self, have, stuck=False, **kw):
        T.FakeOps.__init__(self, **kw)
        self.have, self.stuck = [m.lower() for m in have], stuck

    def sh(self, argv, timeout=480):
        if "--disable" in argv:
            self.calls.append(("disable", argv))
            if self.stuck:
                return 2, "REFUSING: cannot disable"
            names = {a.lower() for a in argv[argv.index("--disable") + 1:] if a != "--apply"}
            self.have = [m for m in self.have if m not in names]
            return 0, "done"
        return T.FakeOps.sh(self, argv, timeout)

    def live_mods(self):
        return list(self.have)


def t_stager():
    plan = dict(T.PLAN, without=[X])
    ops = Ops(["ludeon.rimworld", X])
    verdict, text = S.run(plan, ops)
    tags = [c[0] for c in ops.calls]
    ok("disable" in tags and X in ops.calls[tags.index("disable")][1], "the stager runs modlist_swap --disable %s" % X)
    ok(tags.index("minimal") < tags.index("disable") and tags.index("enable") < tags.index("disable"),
       "after its own swap and enable: %s" % tags)
    ok("launch" in tags and tags.index("disable") < tags.index("launch"), "and before the launch")
    ok(verdict == "ready" and X not in ops.have and "without %s" % X in text,
       "the load it launches lacks %s: %s" % (X, text[:200]))
    ops = Ops(["ludeon.rimworld", X], stuck=True)
    verdict, text = S.run(plan, ops)
    ok(verdict == "snag" and "launch" not in [c[0] for c in ops.calls], "a refused --disable stops before the launch")
    ops = Ops(["ludeon.rimworld"])
    verdict, text = S.run(dict(T.PLAN), ops)
    ok("disable" not in [c[0] for c in ops.calls], "sanity: a plan with no without runs no --disable")


def t_step():
    """relentless_game.step() on an item whose batch gap is live-without X: the supervisor's own --disable runs, and
    the staging it launches is planned and briefed without X."""
    import selftest_relentless_game as SG
    x = SG.rig(1)
    SG.to_game(x, "I0")
    gap = x.w.game_batch_gap
    x.w.game_batch_gap = lambda builds: dict(gap(builds), without=[X])
    disabled = []
    x.w.modlist_disable = lambda mods: disabled.append(list(mods)) or None
    staged, launch = [], x.w.launch

    def spy(st, run, prompt, agent, clone, max_s, env):
        if agent == G.STAGE_AGENT:
            staged.append((dict(st.get("_stage_plan") or {}), prompt))
        return launch(st, run, prompt, agent, clone, max_s, env)
    x.w.launch = spy
    for _ in range(3):
        x.tick()
        if staged:
            break
        x.w.running = False
    ok(disabled and disabled[0] == [X], "step() runs modlist_swap --disable %s before the slot: %s" % (X, disabled))
    ok(len(staged) == 1, "and launches the staging: %d" % len(staged))
    if staged:
        plan, prompt = staged[0]
        ok(plan.get("without") == [X], "its plan holds without=[%s]: %s" % (X, plan.get("without")))
        ok("--disable %s" % X in prompt, "its brief carries the --disable command")
    x2 = SG.rig(1)
    SG.to_game(x2, "I0")
    gap2 = x2.w.game_batch_gap
    x2.w.game_batch_gap = lambda builds: dict(gap2(builds), without=[X])
    x2.w.modlist_disable = lambda mods: "REFUSING: cannot disable %s" % mods[0]
    staged2, launch2 = [], x2.w.launch
    x2.w.launch = lambda st, *a: (staged2.append(1) if a[2] == G.STAGE_AGENT else None) or launch2(st, *a)
    for _ in range(3):
        x2.tick()
        x2.w.running = False
    ok(not staged2, "a refused --disable holds the item: no staging spends a load that cannot lack %s" % X)


def main():
    for t in (t_batch_gap, t_plan_and_prompt, t_stager, t_step):
        print("-- " + t.__name__)
        t()
    print("selftest_relentless_staging_without: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
