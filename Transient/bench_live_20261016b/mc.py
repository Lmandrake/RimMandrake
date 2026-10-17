from afk_lib import *
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
MC="RimMandrake.FlowWorks.MapControls.RM_MapControls"
def eng(): e=B.call("jawa/flowworks_engine_state"); return (e.get("sinkTransferredTotal"),e.get("overflowDestroyedTotal"))
def canal(): rows=rect(74,208,16,14); return wetn(rows),vol(rows),[ (r["x"],r["f"]) for r in rows if r["f"]>0][:16]
print("before",canal(),eng())
print(sc(MC,"PlaceSource","75,214|RM_Fluid_Water|1"))
for i in range(6):
    step(250); print("src t",i+1,canal(),eng(),flush=True)
print(sc(MC,"PlaceSink","88,214|any|1"))
for i in range(6):
    step(250); print("sink t",i+1,canal(),eng(),flush=True)
print(sc(MC,"Report")[:600])
lg=B.call("rimworld/list_logs",limit=60); 
msgs=[m for m in (lg.get("logs") or lg.get("entries") or []) if "onserv" in json.dumps(m) or "FlowWorks" in json.dumps(m) and "rror" in json.dumps(m)]
print("conservation/error log lines",len(msgs),[str(m)[:160] for m in msgs[:3]])
print(safety())
