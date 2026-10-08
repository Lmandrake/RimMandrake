# scratch wrapper: run validation_v2 live with settings overrides and a phase subset, restoring afterwards. Not source.
import os, sys, json, time
NS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "RimMandrake", "FlowWorks", "northstar")
sys.path.insert(0, NS)
import validation_v2 as v
S_FW = v.S_FW
over = {}
for kv in [a for a in sys.argv[1:] if "=" in a and not a.startswith("--")]:
    k, val = kv.split("=", 1); over[k] = (val.lower() == "true") if val.lower() in ("true", "false") else float(val)
phases = [a.split("=",1)[1] for a in sys.argv if a.startswith("--phases=")]
if phases: v.PHASES = tuple(phases[0].split(","))
out = [a.split("=",1)[1] for a in sys.argv if a.startswith("--out=")][0]
orig = {k: v._SETTINGS[S_FW][k] for k in over}
for k, val in over.items():
    v._SETTINGS[S_FW][k] = val
class A: pass
a = A(); a.live=True; a.mock=False; a.fault=None; a.fresh_map=("--nofresh" not in sys.argv); a.reset_settings=True
a.max_job_ticks=4000; a.progress=None; a.out=out
res = v.run_live(a)
json.dump(res, open(out, "w"), indent=1)
B = v.RealBridge()
for k, val in orig.items():
    B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=k, value=str(val))
    print("RESTORED", k, B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=k).get("value"))
print("OVERRIDES", over)
print("SUMMARY", res["summary"], "green", res["green"])
print("NONPASS", [(r.get("id"), r.get("status")) for r in res["rows"] if r.get("status") != "PASS"] if res["rows"] and isinstance(res["rows"][0], dict) else res["rows"][:1])
