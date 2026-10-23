"""watch.py LOGNAME MODULE ARGS... -- run a northstar proof's main(ARGS) with the excavation destroyed-liquid counter read after every mutating call."""
import sys, os, json, time
sys.path.insert(0, r"src\RimMandrake\Utils"); sys.path.insert(0, r"src\RimMandrake\FlowWorks"); sys.path.insert(0, r"src\RimMandrake\FlowWorks\northstar")
import importlib
import proof_hose as PH
logname, modname, args = sys.argv[1], sys.argv[2], sys.argv[3:]
M = importlib.import_module(modname)
orig_call, orig_hp = PH.PB.call, PH.PB.hp
state = {"last": None, "n": 0}
LOG = open(os.path.join(r"Transient\live_batch_20261023\r2", logname), "w")
def total(self):
    r = orig_call(self, "jawa/map_comp_read", comp="RM_MapComponent_Excavation", members="overflowDestroyedTotal,releaseLostDl", _answer=True) or {}
    return json.dumps(r.get("values") or r, default=str)[:300]
def note(self, what):
    state["n"] += 1
    t = total(self)
    if t != state["last"]:
        LOG.write("%s #%d after %s -> %s\n" % (time.strftime("%H:%M:%S"), state["n"], what[:220], t)); LOG.flush()
        state["last"] = t
SKIP = ("jawa/map_comp_read", "rimworld/get_game_info", "jawa/mod_settings_field")
def call(self, tool, **kw):
    r = orig_call(self, tool, **kw)
    if tool not in SKIP:
        note(self, tool + " " + json.dumps({k: v for k, v in kw.items() if not k.startswith("_")}, default=str)[:160])
    return r
def hp(self, cmd, *a, **kw):
    r = orig_hp(self, cmd, *a, **kw)
    note(self, "hp " + cmd + " -> " + json.dumps(r, default=str)[:100])
    return r
PH.PB.call = call; PH.PB.hp = hp
LOG.write("start -> %s\n" % total(PH.PB())); LOG.flush()
sys.exit(M.main(args))
