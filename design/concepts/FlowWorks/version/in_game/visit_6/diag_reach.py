"""diag_reach.py <out.json> <diag.jsonl> [proof args...]: run suspension_bridge_proof.py --only reach with every bridge call
wrapped (visit 6 diagnosis of SB_islands_restore_reach "reached_not_grounded"; RM_DIAG_REACH_LABOUR=<x> plants a fill too slow to
ground, which the row must read FAIL). job, needs and carried thing are logged at every 500-tick wait step, so a stalled fill shows what the colonist did instead."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import validation_core as V  # noqa: E402

out, diag = sys.argv[1], sys.argv[2]
state = {"pid": None, "job": 0}
log = open(diag, "w", encoding="utf-8")
orig = V.Guarded.call


def call(self, tool, _answer=False, **kw):
    r = orig(self, tool, _answer, **kw)
    if tool == "jawa/ordered_job":
        state["pid"], state["job"] = kw.get("pawnId"), state["job"] + 1
        gv = (orig(self, "jawa/list_things", False, defName="RM_Gravel", limit=50) or {}).get("things") or []
        log.write(json.dumps({"ev": "gravel", "n": state["job"] + 1, "first": kw.get("targetBId"),
                              "stacks": [{k: g.get(k) for k in ("id", "x", "z", "stackCount", "position")} for g in gv]}, default=str)[:1500] + "\n")
        log.write(json.dumps({"ev": "order", "n": state["job"], "target": [kw.get("targetAX"), kw.get("targetAZ")],
                              "reply": {k: r.get(k) for k in ("accepted", "message", "error", "job") if isinstance(r, dict)}}) + "\n")
    elif tool == "rimworld/step_game_ticks" and state["pid"] and kw.get("ticks") in (500, 300):
        ps = orig(self, "jawa/pawn_census", False, ids=state["pid"]) or {}
        me = ps.get("pawns") or []
        if me:
            p = me[0]
            keep = {k: p.get(k) for k in ("x", "z", "job", "needs", "downed", "inMentalState")}
            log.write(json.dumps({"ev": "tick%d" % kw.get("ticks"), "n": state["job"], "pawn": keep}, default=str)[:1500] + "\n")
        log.flush()
    return r


V.Guarded.call = call
import suspension_bridge_proof as SBP  # noqa: E402
if os.environ.get("RM_DIAG_REACH_LABOUR"):
    # the planted state: labour so slow that no fill can ground in its wait (the row must read reached_not_grounded)
    SBP.LABOUR_REACH = float(os.environ["RM_DIAG_REACH_LABOUR"])
sys.exit(SBP.main([out, "--only", "reach"] + sys.argv[3:]))
