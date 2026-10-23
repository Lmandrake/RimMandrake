"""trace_walk.py ARGS... -- run water_scenes_walk.main(ARGS) logging every bridge call that can remove a pawn."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
import validation_core as V
orig = V.Bridge.call
HOT = ("destroy", "vanish", "kill", "quiet", "despawn", "static_call", "reset", "spawn", "debug_action", "advance", "step")
def call(self, tool, *a, **kw):
    r = orig(self, tool, *a, **kw)
    if any(h in tool for h in HOT):
        print("TRACE", tool, json.dumps(kw, default=str)[:200], "->", json.dumps(r, default=str)[:200], flush=True)
    return r
V.Bridge.call = call
import water_scenes_walk as W
sys.exit(W.main(sys.argv[1:]))
