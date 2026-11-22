"""diag_skill.py <out.json> <diag.jsonl> [proof args...]: RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE.

Theory under test: the island-restore "stall" is a slow worker, not a stuck job. The reach row spawns a random Colonist,
and the fill job's speed is the pawn's MiningSpeed (Mining skill: 0.1 at level 0, about 1.0 at level 8, vanilla
Stats_Pawns_WorkGeneral.xml). RM_DIAG_MINING=<0..20> sets the worker's Mining level right after the spawn (no env: the
random pawn as the proof has it). Every 500-tick wait logs the worker's position, job, Mining level and MiningSpeed.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import validation_core as V  # noqa: E402

out, diag = sys.argv[1], sys.argv[2]
MINING = os.environ.get("RM_DIAG_MINING")
state = {"pid": None}
log = open(diag, "w", encoding="utf-8")
orig = V.Guarded.call


def skill_and_speed(self, pid):
    g = orig(self, "jawa/pawn_get", False, pawn=str(pid)) or {}
    lvl = [s for s in (g.get("skills") or []) if s.get("skill") == "Mining"]
    st = orig(self, "jawa/pawn_stats", False, pawn=str(pid), stats="MiningSpeed") or {}
    sp = [s.get("value") for s in (st.get("stats") or []) if s.get("defName") == "MiningSpeed"]
    return (lvl[0] if lvl else None), (sp[0] if sp else None)


def call(self, tool, _answer=False, **kw):
    r = orig(self, tool, _answer, **kw)
    if tool == "jawa/spawn_pawn" and kw.get("faction") == "player" and kw.get("kindDef") == "Colonist":
        pid = ((r.get("pawns") or [{}])[0]).get("id") if isinstance(r, dict) else None
        state["pid"] = pid
        before = skill_and_speed(self, pid)
        setr = None
        if MINING is not None and pid:
            setr = orig(self, "jawa/set_pawn_skill", False, pawn=str(pid), skill="Mining", level=int(MINING))
            setr = {k: setr.get(k) for k in ("success", "error", "after")} if isinstance(setr, dict) else setr
        log.write(json.dumps({"ev": "spawn", "pid": pid, "before": before, "set": setr,
                              "after": skill_and_speed(self, pid)}, default=str)[:2000] + "\n")
    elif tool == "jawa/ordered_job":
        log.write(json.dumps({"ev": "order", "target": [kw.get("targetAX"), kw.get("targetAZ")],
                              "accepted": r.get("accepted") if isinstance(r, dict) else None}) + "\n")
    elif tool == "rimworld/step_game_ticks" and state["pid"] and kw.get("ticks") == 500:
        me = (orig(self, "jawa/pawn_census", False, ids=state["pid"]) or {}).get("pawns") or []
        if me:
            p = me[0]
            j = p.get("job") or {}
            log.write(json.dumps({"ev": "tick500", "x": p.get("x"), "z": p.get("z"), "job": j.get("def"),
                                  "a": j.get("targetA"), "speed": skill_and_speed(self, state["pid"])[1]}, default=str) + "\n")
        log.flush()
    return r


V.Guarded.call = call
import suspension_bridge_proof as SBP  # noqa: E402
sys.exit(SBP.main([out, "--only", "reach"] + sys.argv[3:]))
