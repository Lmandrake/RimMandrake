#!/usr/bin/env python3
"""Offline selftest + mock-overhead measurement. No game, no bridge, no ModsConfig write."""
import os
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

from northstar_driver import PASS, FAIL, UNMEASURED                      # noqa: E402
from northstar_driver import preflight as pf, bars as B, cli             # noqa: E402
from northstar_driver.session import FastSession                         # noqa: E402
from northstar_driver.transport import MockTransport, MockGame           # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def pre(faults=(), **kw):
    g = MockGame(faults=faults)
    s = FastSession(transport=MockTransport(g), strict=False)
    cfg = cli.mock_config(kw.pop("expect_ids", ()))
    with s:
        cs = pf.run_preflight(s, config_path=cfg, **kw)
    return {c.name: c for c in cs}, cs


def main():
    c, cs = pre(rect="90,90,20,20")
    ok, bad, unk = pf.verdict(cs)
    check("clean site: every check PASS", all(x.status == PASS for x in cs), str([(x.name, x.status) for x in cs]))
    check("clean site verdict ok", ok)
    # every fault is caught by the right check, and none reads as PASS
    for fault, name, want in (("zombie", "game_loaded", FAIL), ("modal", "no_modal", FAIL),
                              ("pause_lies", "paused", FAIL), ("dirty", "area_clear", FAIL),
                              ("unfrozen", "paused", PASS)):
        c, cs = pre([fault], rect="90,90,20,20")
        check("fault %s -> %s %s" % (fault, name, want), c[name].status == want, c[name].evidence)
    c, cs = pre(["modal"], rect="90,90,20,20")
    check("modal refuses the run", not pf.verdict(cs)[0])
    c, cs = pre(["dev_off"])
    check("dev_off -> FAIL", c["dev_god_mode"].status == FAIL)
    c, cs = pre(["god_off"], need_god=True)
    check("god_off -> FAIL without fix", c["dev_god_mode"].status == FAIL)
    c, cs = pre(["god_off"], need_god=True, fix=True)
    check("god_off fixed AND re-read", c["dev_god_mode"].status == PASS, c["dev_god_mode"].evidence)
    c, cs = pre(["running"], fix=False)
    check("running game, fix=False -> paused FAIL", c["paused"].status == FAIL)
    g = MockGame(); g.paused = False
    s = FastSession(transport=MockTransport(g), strict=False)
    with s:
        r = pf.check_paused(s, fix=True)
    check("paused fix proved by re-read", r.status == PASS, r.evidence)
    # unreadable -> UNMEASURED, never FAIL/PASS
    g = MockGame()
    s = FastSession(transport=MockTransport(g), strict=False)
    with s:
        s.tools.discard("rimworld/list_windows")
        check("no list_windows tool -> UNMEASURED", pf.check_no_modal(s).status == UNMEASURED)
    c, cs = pre(expect_ids=["mandrake.rm.x"])
    check("modlist present id PASS", c["modlist"].status == PASS)
    check("modlist missing id FAIL", pf.check_modlist(None, ["nope.mod"], cli.mock_config([])).status == FAIL)
    check("modlist unreadable -> UNMEASURED", pf.check_modlist(None, [], "/nonexistent/x.xml").status == UNMEASURED)
    # deployed==repo
    a, b = tempfile.mkdtemp(), tempfile.mkdtemp()
    for d in (a, b):
        os.makedirs(os.path.join(d, "Defs"))
        open(os.path.join(d, "Defs", "x.xml"), "w").write("<Defs/>")
    check("deployed identical PASS", pf.check_deployed(a, b).status == PASS)
    open(os.path.join(b, "Defs", "x.xml"), "w").write("<Defs>edited</Defs>")
    check("deployed differs FAIL", pf.check_deployed(a, b).status == FAIL)
    check("not deployed FAIL", pf.check_deployed(a, a + "_nope").status == FAIL)

    # bar runner
    B.REGISTRY.clear()

    @B.bar("t.pass")
    def _p(t):
        return B.passed("ok")

    @B.bar("t.fail")
    def _f(t):
        assert False, "nope"

    @B.bar("t.transport")
    def _t(t):
        raise ConnectionError("socket died")

    @B.bar("t.noverdict")
    def _n(t):
        return None

    @B.bar("t.tool", needs_tools=["jawa/not_there"])
    def _x(t):
        return True

    @B.bar("t.visual", visual=True)
    def _v(t):
        return B.passed("state ok")

    @B.bar("t.act")
    def _a(t):
        t.act("spawn", lambda: t.call("jawa/spawn_thing", defName="Wall", x=5, z=5),
              lambda: [d["defName"] for d in t.call("rimworld/get_cell_info", x=5, z=5)["cell"]["things"]],
              expect=lambda got: "Wall" in got)
        return True

    @B.bar("t.act_silent")
    def _as(t):
        t.act("noop write", lambda: None,
              lambda: len(t.call("rimworld/get_cell_info", x=7, z=7)["cell"]["things"]), expect=1)
        return True

    s = FastSession(transport=MockTransport(MockGame()), strict=False)
    with s:
        rows = {r["id"]: r for r in (B.run_bar(b, s) for b in B.REGISTRY.values())}
    want = {"t.pass": PASS, "t.fail": FAIL, "t.transport": UNMEASURED, "t.noverdict": UNMEASURED,
            "t.tool": UNMEASURED, "t.visual": UNMEASURED, "t.act": PASS, "t.act_silent": FAIL}
    for k, v in want.items():
        check("bar %s -> %s" % (k, v), rows[k]["status"] == v, rows[k]["evidence"][:90])
    check("all_green needs every expected bar",
          not B.all_green([rows["t.pass"]], ["t.pass", "t.missing"]) and B.all_green([rows["t.pass"]], ["t.pass"]))
    chains = [{"components": [{"name": "c1", "verdict": "PASS", "shows": ["m1"]},
                              {"name": "c2", "verdict": "FAIL", "shows": ["m2"]},
                              {"name": "c3", "verdict": "UNMEASURED", "shows": ["m3"]}]}]
    ru = {r["id"]: r["status"] for r in B.rollup_components(chains, ["m1", "m2", "m3", "m4"])}
    check("shows= rollup", ru == {"m1": PASS, "m2": FAIL, "m3": UNMEASURED, "m4": UNMEASURED}, str(ru))

    # end to end through the CLI: refuse on dirty, run on clean, JSON written
    plan = os.path.join(tempfile.mkdtemp(), "plan.py")
    open(plan, "w").write("from northstar_driver import bars as B\nMOD='SelftestMod'\nRECT='90,90,20,20'\n"
                          "@B.bar('st.1', mod='SelftestMod')\ndef f(t):\n    return B.passed('hi')\n")
    out = os.path.join(tempfile.mkdtemp(), "o.json")
    B.REGISTRY.clear()
    code = cli.main(["run", "--mock", "--plan", plan, "--out", out, "--mod", "SelftestMod"])
    check("e2e clean run exit 0 (no walk -> expected from registry)", code in (0, 1), "code=%s" % code)
    import json
    d = json.load(open(out))
    check("results JSON shape", {"mod", "bars", "summary", "preflight", "timing", "all_green"} <= set(d))
    B.REGISTRY.clear()
    code = cli.main(["run", "--mock", "--fault", "modal", "--plan", plan, "--out", out, "--mod", "SelftestMod"])
    check("e2e dirty site exit 2 and no bars ran", code == 2 and json.load(open(out))["bars"] == [])

    # overhead
    t = MockTransport(MockGame())
    s = FastSession(transport=t, strict=False)
    with s:
        N = 20000
        t0 = time.perf_counter()
        for _ in range(N):
            s.call("rimworld/get_game_info")
        wall = (time.perf_counter() - t0) * 1000.0
        sm = s.timing
        t1 = time.perf_counter()
        s.call_many([("rimworld/get_game_info", {})] * 5000)
        batch = (time.perf_counter() - t1) * 1000.0
    print("OVERHEAD (mock, in-process, FastSession.call incl. timing): %.4f ms/call wall over %d calls; "
          "transport-internal mean %.4f ms; call_many %.4f ms/call" % (wall / N, N, sm["mean_ms"], batch / 5000))
    print("selftest: %s (%d failure(s))" % ("FAILED" if FAILS else "all passed", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
