#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, guard SCENES_CAN_ASK, part 2). Written by the filing seat; the
builder does not edit it.

    python3 src/RimMandrake/rimflow/acceptance/guard_empty_game_accept.py       # exit 0 and "PASS 8/8" when built

THE CONTRACT IT FIXES: `src/RimMandrake/Utils/scene_empty_game.py`. No game, no bridge, no model.
  EmptyGame            a bridge stand-in: call(tool, **kw) -> {"success": True} and nothing else; ticks(n) -> None.
                       Every tool answers "done" with no data: nothing is on the map and nothing can be read.
  rows_on_empty(scene) -> [row]     runs a FlowWorks-style scene `scene(B, snapshot, reload_snapshot, receipt, ...)` on
                       an EmptyGame (save_mid/load_mid given as no-ops when the scene takes them) and returns its rows;
                       an exception escaping the scene is one row {"id": "<scene>", "status": "ERROR", "detail": ...}.
  vacuous(scenes) -> [(scene name, row id)]   every row whose status is PASS on the empty game: a check that passes
                       with nothing to test.
  `maturation.py certificate FlowWorks --to in_game` refuses a bar decided by a scene with a vacuous row (clause
  `asks_on_empty_game`), the refusal naming the row; a harness the module has no adapter for is did_not_run.

THE BACKTEST IS THE TEST. Measured by the filing seat 2026-11-15 with a 25-line prototype of exactly this:
  FlowWorks' scenes as they were when visit 1 was driven (commit 99ff70d91a): 3 rows PASS on an empty game
    (scene_fetch_fallen, scene_pit_trap_raid PTR_control_open_pit_no_one_falls, scene_source_pays SRC_flow_stops_when_empty).
  FlowWorks' scenes on the base of this ticket: 1 row still does, SRC_flow_stops_when_empty. The builder fixes that row
  (it must read UNMEASURED or FAIL when the flow was never seen running) in the same change.
"""
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RIMFLOW, "..", "..", ".."))
NORTH = os.path.join(REPO, "src/RimMandrake/FlowWorks/northstar")
UTILS = os.path.join(REPO, "src/RimMandrake/Utils")
for _p in (NORTH, UTILS, os.path.join(UTILS, "modcheck")):
    sys.path.insert(0, _p)
REAL = os.path.join(NORTH, "concept_scenes.py")
OLD = "99ff70d91a"
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


def load(source, name):
    m = types.ModuleType(name)
    m.__file__ = REAL          # the module finds its neighbours from its own path
    sys.modules[name] = m
    exec(compile(source, REAL, "exec"), m.__dict__)
    return m


def main():
    try:
        import scene_empty_game as SE
    except Exception as e:  # noqa: BLE001
        SE = None
        print("FAIL  import scene_empty_game: %r" % (e,))
    g = SE.EmptyGame() if SE else None
    check(g is not None and g.call("jawa/anything", x=1) == {"success": True} and g.ticks(60) is None,
          "the empty game answers every tool with a bare success")

    def scene_vac(B, snapshot, reload_snapshot, receipt):
        B.call("jawa/spawn_pawn")
        return [{"id": "V_ok", "status": "PASS"}, {"id": "V_un", "status": "UNMEASURED"}]

    def scene_honest(B, snapshot, reload_snapshot, receipt, *, save_mid, load_mid):
        r = B.call("jawa/read")
        return [{"id": "H", "status": "PASS" if r.get("value") else "UNMEASURED"}]

    def scene_crash(B, snapshot, reload_snapshot, receipt):
        return B.call("jawa/read")["pawns"][0]

    try:
        v = SE.vacuous({"scene_vac": scene_vac, "scene_honest": scene_honest, "scene_crash": scene_crash})
        rows = SE.rows_on_empty(scene_crash)
    except Exception as e:  # noqa: BLE001
        v, rows = "raised %r" % (e,), []
    check(v == [("scene_vac", "V_ok")], "only the row that passes on nothing is vacuous (%s)" % (v,))
    check(len(rows) == 1 and rows[0].get("status") == "ERROR", "a scene that cannot parse an empty answer is one ERROR row, not a pass")
    old_src = subprocess.run(["git", "-C", REPO, "show", "%s:src/RimMandrake/FlowWorks/northstar/concept_scenes.py" % OLD],
                             capture_output=True, text=True).stdout
    check(len(old_src) > 1000, "the visit-1 scene file is readable from git (%s)" % OLD)
    try:
        old = sorted(SE.vacuous(load(old_src, "cs_visit1").STAGE3_SCENES))
    except Exception as e:  # noqa: BLE001
        old = "raised %r" % (e,)
    want = {("scene_fetch_fallen", None), ("scene_pit_trap_raid", "PTR_control_open_pit_no_one_falls"),
            ("scene_source_pays", "SRC_flow_stops_when_empty")}
    got = {(s, r if s != "scene_fetch_fallen" else None) for s, r in old} if isinstance(old, list) else set()
    check(got == want, "backtest: on the visit-1 scenes it finds the 3 rows that passed on nothing (%s)" % (old,))
    try:
        now = SE.vacuous(load(open(REAL, encoding="utf-8").read(), "cs_now").STAGE3_SCENES)
    except Exception as e:  # noqa: BLE001
        now = "raised %r" % (e,)
    check(now == [], "today's FlowWorks scenes have no row that passes on an empty game (%s)" % (now,))
    try:
        src = open(os.path.join(RIMFLOW, "judge_certificate.py"), encoding="utf-8").read()
    except OSError:
        src = ""
    check("asks_on_empty_game" in src, "the certificate carries the asks_on_empty_game clause for an in-game visit")
    r = subprocess.run([sys.executable, os.path.join(UTILS, "run_selftests.py"), "--only",
                        "src/RimMandrake/FlowWorks/northstar/selftest_fill_scenes_dig_first.py"], capture_output=True, text=True,
                       cwd=REPO, timeout=900)
    check(r.returncode == 0 and SE is not None, "the scenes' own fake-game selftest is still green")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
