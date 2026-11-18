#!/usr/bin/env python3
"""scene_empty_game.py: run an in-game scene against an empty game and list the rows that PASS on nothing.

A check that reads PASS when every bridge call answers a bare success and nothing is on the map tests nothing: FlowWorks
visit 1 (2026-11-15) drove three such rows live (RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED; guard SCENES_CAN_ASK,
part 2, design/specs/2026-11-15-cheap-guards-at-every-door.md section 3.4). No game, no bridge, no model.

    EmptyGame            a bridge stand-in: call(tool, **kw) and probe_of(...) -> {"success": True}; ticks(n) -> None.
    rows_on_empty(scene) -> [row]     one FlowWorks-style scene `scene(B, snapshot, reload_snapshot, receipt, ...)` on an
                         EmptyGame; an exception escaping it is one row {"id": <scene>, "status": "ERROR", "detail": ...}.
    vacuous(scenes)      -> [(scene name, row id)] for every row whose status is PASS on the empty game.
    flowworks_vacuous(root) -> (pairs, None) on FlowWorks' concept_scenes.py, or (None, why) when it could not run.

    python3 src/RimMandrake/Utils/scene_empty_game.py [--root DIR] [--json]   FlowWorks' vacuous rows; exit 0 none,
                         1 some, 2 did not run (--json: {"vacuous": [[scene, row], ...], "scenes": [every scene run]}
                         or {"did_not_run": why})

Only the FlowWorks scene harness (`_Stage` scenes in a STAGE3_SCENES table) has an adapter. The modcheck `Suite` scenes
(Graffiti, Pyrelands: `validation.py` functions taking a suite) read "did not run": that adapter would hand the scene a
Suite whose bridge is an EmptyGame and collect the Suite's rows instead of a returned list.
"""
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOWWORKS_SCENES = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
_LOADED = {}      # the scene names flowworks_vacuous last ran: a scene absent from them was never examined


class EmptyGame:
    """Every tool answers "done" with no data: nothing is on the map and nothing can be read."""
    stop_on = None

    def call(self, tool, **kw):
        return {"success": True}

    def probe_of(self, *a, **kw):
        return {"success": True}

    def ticks(self, n):
        return None


def rows_on_empty(scene):
    """-> the rows `scene` returns on an EmptyGame (its receipt's rows when it returns the receipt)."""
    name = getattr(scene, "__name__", "scene")
    receipt = {"calls": []}
    kw = {}
    try:
        params = inspect.signature(scene).parameters
    except (TypeError, ValueError):
        params = {}
    for k in ("save_mid", "load_mid"):
        if k in params:
            kw[k] = lambda: None
    try:
        out = scene(EmptyGame(), lambda: None, lambda: None, receipt, **kw)
    except Exception as e:  # noqa: BLE001  any escape is the scene failing to read an empty answer, never a pass
        return [{"id": name, "status": "ERROR", "detail": ("%s: %s" % (type(e).__name__, e))[:400]}]
    rows = out.get("rows") if isinstance(out, dict) else out
    if not isinstance(rows, list):
        return [{"id": name, "status": "ERROR", "detail": "the scene returned no rows: %r" % (out,)[:400]}]
    return [r for r in rows if isinstance(r, dict)]


def vacuous(scenes):
    """-> [(scene name, row id)] for every row that reads PASS on the empty game, in the table's order."""
    out = []
    for name, scene in (scenes or {}).items():
        for r in rows_on_empty(scene):
            if r.get("status") == "PASS":
                out.append((name, r.get("id")))
    return out


def flowworks_vacuous(root):
    """-> (vacuous pairs, None) for FlowWorks' STAGE3_SCENES under root, or (None, why) when the scenes cannot be loaded."""
    path = os.path.join(root, FLOWWORKS_SCENES)
    if not os.path.isfile(path):
        return None, "%s is not there" % FLOWWORKS_SCENES
    north = os.path.dirname(path)
    utils = os.path.join(root, "src/RimMandrake/Utils")
    added = [p for p in (north, utils, os.path.join(utils, "modcheck")) if p not in sys.path]
    sys.path[:0] = added
    import types
    m = types.ModuleType("concept_scenes_empty_game")
    m.__file__ = path
    try:
        with open(path, encoding="utf-8") as fh:
            exec(compile(fh.read(), path, "exec"), m.__dict__)  # noqa: S102  our own scene file, loaded as its runner does
    except Exception as e:  # noqa: BLE001
        return None, "%s did not load: %s: %s" % (FLOWWORKS_SCENES, type(e).__name__, str(e)[:200])
    finally:
        for p in added:
            if p in sys.path:
                sys.path.remove(p)
    scenes = getattr(m, "STAGE3_SCENES", None)
    if not isinstance(scenes, dict) or not scenes:
        return None, "%s has no STAGE3_SCENES table" % FLOWWORKS_SCENES
    _LOADED["scenes"] = list(scenes)
    return vacuous(scenes), None


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    pairs, why = flowworks_vacuous(a.root)
    if a.json:
        import json
        names = sorted(_LOADED.get("scenes") or []) if pairs is not None else []
        print(json.dumps({"did_not_run": why} if pairs is None else {"vacuous": pairs, "scenes": names}))
        return 2 if pairs is None else 1 if pairs else 0
    if pairs is None:
        print("DID NOT RUN: %s" % why)
        return 2
    for s, r in pairs:
        print("VACUOUS %s %s" % (s, r))
    print("%d row(s) pass on an empty game%s" % (len(pairs), "" if pairs else " (looked, none)"))
    return 1 if pairs else 0


if __name__ == "__main__":
    sys.exit(main())
