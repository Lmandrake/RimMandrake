#!/usr/bin/env python3
"""STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS: a live_proofs file's main-menu step and with/without pair reach the staging.

  `live-menu: <cmd>` runs once the load reaches the main menu (the bridge token) and before game-ready, so before any
  game starts; `{toggle}` in it is the staging's side. `live-toggle: <mod>` alternates an item's stagings with and
  without the mod: the with side enables it, the without side keeps it off the list and the stager refuses a list that
  still holds it; a toggling item stages alone and never rides. Neither line goes to SteveDesktop's inferred tier.

  selftest_relentless_staging_menu.py                     every case below; exit 0 when all hold (t_step_two_stagings
                                                          drives relentless_game.step() itself: two stagings)
  selftest_relentless_staging_menu.py --fixture good      the instrument on the real planner and stager over
                                                          PLANET_ATMOSPHERE_CLOUD_COST_1.txt: FIXTURE_VERDICT: PASS, exit 0
  selftest_relentless_staging_menu.py --fixture bad       the same, on a plan built the old way (no menu step: the
                                                          staging that parked without sampling): FIXTURE_VERDICT: FAIL, exit 1
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import relentless_game as G  # noqa: E402
import relentless_live_round as LR  # noqa: E402
import relentless_stage as S  # noqa: E402
import selftest_relentless_stage as T  # noqa: E402

PLANET = "PLANET_ATMOSPHERE_CLOUD_COST_1"
PLANET_TXT = os.path.join(REPO, "infrastructure", "state", "live_proofs", PLANET + ".txt")
MOD = "rwnodetree.rwplanetatmosphere"
FAILS = []


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class Fx(object):
    """proofs_at only: what staging_menu and toggles read."""
    def __init__(self, texts):
        self.texts = texts

    def proofs_at(self, item, sha, ext=".txt"):
        return self.texts.get(item)


class Ops(T.FakeOps):
    """FakeOps whose live list is `have`, recording when the bridge token was waited on."""
    def __init__(self, have=(), **kw):
        T.FakeOps.__init__(self, **kw)
        self.have = [m.lower() for m in have]

    def live_mods(self):
        return list(self.have)


def planet_text():
    with open(PLANET_TXT, encoding="utf-8") as f:
        return f.read()


def menu_ran(ops, plan):
    """-> (held, why): every menu command of `plan`'s proofs ran through bash AFTER the bridge-token wait and before the
    staging reported, and the staging said ready. The instrument both fixtures run."""
    order = [c[0] for c in ops.calls]
    if "wait" not in order:
        return False, "the staging never waited for the main menu"
    after = [c[1][2] for c in ops.calls[order.index("wait"):] if c[0] == "bash"]
    missing = [c for c in plan["_want_menu"] if c not in after]
    if missing:
        return False, "the menu step never ran at the main menu: %s" % "; ".join(missing)
    return True, "ran at the main menu: %s" % "; ".join(after)


def stage(menu_on, stages=0):
    """The real planner and stager on the PLANET file: staging_menu -> stage_plan -> relentless_stage.run (faked
    world). menu_on=False builds the plan the old way, without the menu keys."""
    fx = Fx({PLANET: planet_text()})
    st = {"item": PLANET, "gen": 1, "game": {"full": None}}
    menu = G.staging_menu(fx, PLANET, "abc", stages)
    want = [MOD] if menu["side"] == "with" else []
    plan = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [], want, [], None, None, menu=menu if menu_on else None)
    ops = Ops(have=["ludeon.rimworld"] + want, up=False)
    verdict, text = S.run(plan, ops)
    plan["_want_menu"] = LR.menu_cmds(planet_text(), menu["side"])
    return verdict, text, ops, plan


def fixture(which):
    verdict, text, ops, plan = stage(menu_on=(which == "good"))
    held, why = menu_ran(ops, plan)
    held = held and verdict == "ready"
    print("staging %s: %s" % (verdict, text[:300]))
    print("menu step: %s" % why)
    print("FIXTURE_VERDICT: %s" % ("PASS" if held else "FAIL"))
    return 0 if held else 1


# ---------------------------------------------------------------- cases

def t_parse():
    t = ("live-proof A1: x\n`live-menu: python3 a.py --side {toggle}`\nlive-menu: echo b\nlive-menu: echo b\n"
         "- live-toggle: some.mod  # the pair\n")
    ok(LR.live_menu(t) == ["python3 a.py --side {toggle}", "echo b"], "live-menu: bare or wrapped, in order, no repeats")
    ok(LR.live_toggle(t) == "some.mod", "live-toggle: one mod, a # comment dropped")
    ok(LR.menu_cmds(t, "without")[0] == "python3 a.py --side without", "{toggle} filled with the side")
    for bad in ("live-toggle: a b\n", "live-toggle: a\nlive-toggle: b\n"):
        try:
            LR.live_toggle(bad)
            ok(False, "refused: %r" % bad)
        except ValueError:
            ok(True, "refused: %r" % bad)
    try:
        LR.menu_cmds("live-menu: x {toggle}\n", None)
        ok(False, "{toggle} with no side is refused")
    except ValueError:
        ok(True, "{toggle} with no side is refused")
    ok([LR.toggle_side(n) for n in range(4)] == ["with", "without", "with", "without"], "stagings alternate sides")
    ok(LR.live_menu("live-proof A1: x\n") == [] and LR.live_toggle("") is None, "a file with neither asks nothing")


def t_not_inferred():
    plain = "live-proof A1: python3 x.py\n"
    ok(LR.inferable(plain, "A1", None), "sanity: a plain file goes to the inferred tier")
    ok(not LR.inferable(plain + "live-menu: echo m\n", "A1", None), "a live-menu file stays on Archmagi's staging")
    ok(not LR.inferable(plain + "live-toggle: a.b\n", "A1", None), "a live-toggle file stays on Archmagi's staging")
    ok(not LR.inferable(planet_text(), "A1", None), "the PLANET file is never inferred")


def t_plan_and_prompt():
    fx = Fx({"I": "live-menu: echo m {toggle}\nlive-toggle: a.b\n", "R": "live-menu: echo r\n", "P": "live-proof A1: x\n"})
    m0 = G.staging_menu(fx, "I", "s", 0)
    m1 = G.staging_menu(fx, "I", "s", 1)
    ok(m0["side"] == "with" and m1["side"] == "without" and m0["cmds"] == ["echo m with"], "the item's side: %s %s" % (m0, m1))
    p0, p1 = G.menu_plan(m0), G.menu_plan(m1)
    ok(p0 == {"menu_cmds": ["echo m with"], "toggle": {"mod": "a.b", "side": "with"}}, "with plan: %s" % p0)
    ok(p1.get("without") == ["a.b"] and p1["toggle"]["side"] == "without", "without plan lacks the mod: %s" % p1)
    mr = G.staging_menu(fx, "P", "s", 0, [{"item": "R", "game": {"sha": "t"}}])
    ok(mr == {"cmds": ["echo r"], "toggle": None, "side": None}, "a rider's menu step rides with it: %s" % mr)
    ok(G.menu_plan(G.staging_menu(fx, "P", "s", 0)) == {}, "no menu, no toggle: the plan is unchanged")
    ok(G.toggles(fx, {"item": "I", "game": {"sha": "s"}}) and not G.toggles(fx, {"item": "R", "game": {}}),
       "a toggling item never rides another's load")
    fx.texts["B"] = "live-menu: echo {toggle}\n"
    ok(G.menu_ok(fx, {"item": "R", "game": {}}) and not G.menu_ok(fx, {"item": "B", "game": {}}),
       "a rider whose {toggle} has no side is dropped, never holding the item it rides with")
    c = {"stage_tries": 2}
    ok(G.stage_tries(c, {"toggle": "a.b"}) == 4 and G.stage_tries(c, {}) == 2, "a pair gets stage_tries per side")
    st = {"item": "I", "gen": 1, "game": {"full": None}}
    r = {"seat": "RELENTLESS"}
    pr = G.stage_prompt(st, r, "s", menu=m1)
    ok("BEFORE you start or load any game" in pr and "`echo m without`" in pr, "the fallback brief carries the menu step")
    ok("without side" in pr and "must lack it" in pr, "and the side")
    ok("MAIN MENU STEP: none." in G.stage_prompt(st, r, "s"), "an item with none says none")
    plan = G.stage_plan(st, {"stage_max_s": 3600}, "s", [], [], [], None, None, menu=m1)
    ok(plan["menu_cmds"] == ["echo m without"] and plan["without"] == ["a.b"], "stage_plan carries both: %s" % plan)


def t_stager():
    base = dict(T.PLAN, remedy_cmds=["echo remedy"], menu_cmds=["echo menu"])
    ops = Ops()
    verdict, text = S.run(base, ops)
    order = [c[0] for c in ops.calls]
    bash = [c[1][2] for c in ops.calls if c[0] == "bash"]
    ok(verdict == "ready" and bash == ["echo menu", "echo remedy"], "menu step before the remedies: %s" % bash)
    ok(order.index("wait") < order.index("bash"), "and after the bridge token (the main menu)")
    ok("menu `echo menu` exit 0" in text, "game-ready says what the menu step did: %s" % text[-200:])
    ops = Ops(have=["ludeon.rimworld", "a.b"])
    verdict, text = S.run(dict(base, without=["a.b"], toggle={"mod": "a.b", "side": "without"}), ops)
    ok(verdict == "snag" and "must load without" in text and ("launch",) not in ops.calls,
       "a without load holding the mod stops before the launch: %s" % text[:160])
    ops = Ops(have=["ludeon.rimworld"])
    verdict, text = S.run(dict(base, toggle={"mod": "a.b", "side": "with"}), ops)
    ok(verdict == "snag" and "lacks a.b" in text, "a with load lacking the mod stops: %s" % text[:160])
    ops = Ops(have=["ludeon.rimworld"])
    verdict, text = S.run(dict(base, without=["a.b"], toggle={"mod": "a.b", "side": "without"}), ops)
    ok(verdict == "ready" and "toggle: without a.b" in text, "a without load that lacks it goes on: %s" % text[:200])
    ops = Ops(token="slow")
    verdict, text = S.run(base, ops)
    ok(verdict == "snag" and "main-menu step never ran" in text, "a load still going is a snag: the step never ran")
    ops = Ops(token="slow")
    verdict, text = S.run(dict(base, menu_cmds=[]), ops)
    ok(verdict == "ready" and "STILL LOADING" in text, "sanity: with no menu step a slow load is still handed over")


def t_fixtures():
    ok(fixture("good") == 0, "fixture good: PASS on the PLANET file through the real planner and stager")
    ok(fixture("bad") == 1, "fixture bad: FAIL on a plan without the menu step")
    v, text, _, _ = stage(True, stages=1)
    ok(v == "ready" and "--require without" in text, "the PLANET file's second staging samples the without side")


def t_step_two_stagings():
    """The supervisor's own wiring: relentless_game.step() stages an item whose proofs file is the PLANET one twice
    (the first staging ends with the game down, so the prove phase stages again). Staging 1 enables the mod and its
    plan and brief carry the menu step with --require with; staging 2 keeps the mod off the list, plans without=[mod]
    and carries --require without. Red when step() builds its plan without staging_menu() (the item's own defect: the
    staging parks on a map with no menu sample and no with/without pair)."""
    import relentless as R
    import selftest_relentless_game as SG
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.w.proofs[("I0", ".txt")] = planet_text()
    staged, launch = [], x.w.launch

    def spy(st, run, prompt, agent, clone, max_s, env):
        if agent == G.STAGE_AGENT:
            staged.append((dict(st.get("_stage_plan") or {}), prompt, len(x.w.enabled)))
        return launch(st, run, prompt, agent, clone, max_s, env)
    x.w.launch = spy
    x.tick()
    x.w.running = False
    x.tick()
    ok(len(staged) == 1, "step() launched the first staging: %d" % len(staged))
    st = x.st("I0")
    R.beat(x.s, "I0", st["gen"])
    G.ready(x.s, "I0", st["gen"], "up at the menu")
    x.w.up[st["run"]["unit"]] = False
    for _ in range(3):
        x.tick()
        if len(staged) >= 2:
            break
    ok(len(staged) == 2, "step() staged a second time on the game still down: %d" % len(staged))
    if len(staged) < 2:
        return
    want = {s: LR.menu_cmds(planet_text(), s) for s in ("with", "without")}
    (p1, b1, n1), (p2, b2, n2) = staged
    en1, en2 = [[m.lower() for m in e] for e in (x.w.enabled[n1 - 1], x.w.enabled[n2 - 1])]
    ok(MOD in en1, "staging 1 enables %s: %s" % (MOD, en1))
    ok(p1.get("menu_cmds") == want["with"] and "--require with" in want["with"][0],
       "staging 1's plan runs the menu step --require with: %s" % p1.get("menu_cmds"))
    ok((p1.get("toggle") or {}).get("side") == "with" and not p1.get("without"), "staging 1 is the with side: %s"
       % p1.get("toggle"))
    ok("MAIN MENU STEP: the moment" in b1 and "`%s`" % want["with"][0] in b1, "staging 1's brief carries the menu step")
    ok(MOD not in en2, "staging 2 keeps %s off the list: %s" % (MOD, en2))
    ok(p2.get("without") == [MOD] and (p2.get("toggle") or {}).get("side") == "without",
       "staging 2 plans without=[%s]: %s %s" % (MOD, p2.get("without"), p2.get("toggle")))
    ok(p2.get("menu_cmds") == want["without"] and "--require without" in want["without"][0],
       "staging 2's plan runs the menu step --require without: %s" % p2.get("menu_cmds"))
    ok("`%s`" % want["without"][0] in b2, "staging 2's brief carries the without menu step")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fixture", choices=["good", "bad"])
    a = ap.parse_args(argv)
    if a.fixture:
        return fixture(a.fixture)
    for t in (t_parse, t_not_inferred, t_plan_and_prompt, t_stager, t_fixtures, t_step_two_stagings):
        print("-- " + t.__name__)
        t()
    print("selftest_relentless_staging_menu: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
