"""Run pipe_levelling_perf_proof --rehearsal with the excavation engine's destroyed-liquid counter read after every mutating call."""
import sys, os, json
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
import proof_hose as PH
import pipe_levelling_perf_proof as LP
orig_call = PH.PB.call
orig_hp = PH.PB.hp
state = {"last": None, "n": 0}
LOG = open(r"Transient\live_batch_20261023\r2\level_watch.log", "w")
def total(self):
    r = orig_call(self, "jawa/map_comp_read", comp="RM_MapComponent_Excavation", members="overflowDestroyedTotal,releaseLostDl", _answer=True) or {}
    return json.dumps(r.get("members") or r.get("values") or r, default=str)[:300]
def note(self, what):
    state["n"] += 1
    t = total(self)
    if t != state["last"]:
        LOG.write("#%d after %s -> %s\n" % (state["n"], what[:160], t)); LOG.flush()
        state["last"] = t
def call(self, tool, **kw):
    r = orig_call(self, tool, **kw)
    if tool in ("jawa/static_call", "rimworld/step_game_ticks", "jawa/build_batch"):
        note(self, tool + " " + str(kw.get("method") or kw.get("ticks") or "") + " " + str(kw.get("args") or "")[:60])
    return r
def hp(self, cmd, *a, **kw):
    r = orig_hp(self, cmd, *a, **kw)
    note(self, "hp " + cmd + " -> " + json.dumps(r, default=str)[:80])
    return r
PH.PB.call = call; PH.PB.hp = hp
B = PH.PB(); LOG.write("start -> %s\n" % total(B)); LOG.flush()
sys.exit(LP.main([r"Transient\live_batch_20261023\r2\level_rehearsal_rerun.json", "--rehearsal", "--rigs", "200", "--calls", "20"]))
