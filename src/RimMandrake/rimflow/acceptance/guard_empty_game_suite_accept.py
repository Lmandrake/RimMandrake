#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY (the modcheck Suite adapter
the certificate's asks_on_empty_game clause names as missing; RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED built
the clause with an adapter for FlowWorks' concept_scenes.py only). Written by the filing seat; the builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_suite_accept.py      # exit 0 and "PASS 7/7" when built

THE CONTRACT IT FIXES: `src/RimMandrake/Utils/scene_empty_game.py`
  suite_vacuous(suite) -> [(chain name, component name)]   runs every live chain of a modcheck `Suite` (offline=True
      chains are left out) on a `modcheck.TestContext` whose session is an empty game (every call a bare success, nothing
      on the map, ticks a no-op) and lists each component whose verdict is PASS: a row that passes with nothing to test.
      A component that FAILs or reads UNMEASURED is not listed; an exception escaping a chain lists nothing from it.
  `judge_certificate.certify(..., to="in_game")` uses it for a live test whose file defines a module-level modcheck
  `suite` and whose entry names one of its chains, so such a test no longer reads "no empty-game adapter".
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(RIMFLOW), "Utils")
for _p in (UTILS, os.path.join(UTILS, "modcheck")):
    sys.path.insert(0, _p)
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def main():
    from modcheck import Suite, ExpectationFailed
    s = Suite("Fixture")

    @s.chain("vac")
    def vac(t):
        with t.component("c_vac"):
            pass

    @s.chain("honest")
    def honest(t):
        with t.component("c_honest"):
            r = t.session.call("jawa/read")
            if not (r or {}).get("value"):
                raise ExpectationFailed("nothing read")

    @s.chain("parse")
    def parse(t):
        with t.component("c_parse"):
            t.session.call("jawa/list_pawns")["pawns"][0]

    @s.chain("escape")
    def escape(t):
        raise RuntimeError("a chain that dies before any component")

    @s.chain("off", offline=True)
    def off(t):
        with t.component("c_off"):
            pass

    try:
        import scene_empty_game as SE
        fn = SE.suite_vacuous
    except Exception as e:  # noqa: BLE001
        fn = None
        print("FAIL  scene_empty_game.suite_vacuous: %r" % (e,))
    try:
        got = fn(s) if fn else None
    except Exception as e:  # noqa: BLE001
        got = "raised %r" % (e,)
    lst = got if isinstance(got, list) else []
    check(isinstance(got, list), "suite_vacuous returns a list (%s)" % (got,))
    check(("vac", "c_vac") in lst, "a component that passes with nothing read is listed")
    check(not [x for x in lst if x[0] == "honest"], "a component that refuses on an empty read is not listed")
    check(not [x for x in lst if x[0] == "parse"], "a component that cannot parse an empty answer is not listed")
    check(not [x for x in lst if x[0] == "escape"], "a chain that raises lists nothing")
    check(not [x for x in lst if x[0] == "off"], "an offline chain is left out")
    try:
        src = open(os.path.join(RIMFLOW, "judge_certificate.py"), encoding="utf-8").read()
    except OSError:
        src = ""
    check("suite_vacuous" in src, "the certificate's asks_on_empty_game clause uses the Suite adapter")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
