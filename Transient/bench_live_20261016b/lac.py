from afk_lib import *
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
kids=B.call("rimworld/list_debug_action_children",path="Actions").get("children") or []
acts={}
for c in kids:
    if c.get("label")=="Deepfire" or (c.get("path") or "").endswith("\\Deepfire"):
        acts={l.get("label"):l.get("path") for l in B.call("rimworld/list_debug_action_children",path=c.get("path")).get("children") or []}
if not acts: acts={c.get("label"):c.get("path") for c in kids if "Lacquer" in (c.get("label") or "")}
print([k for k in acts if "acquer" in (k or "")])
p=next(v for k,v in acts.items() if "lacquer bill: round trip" in (k or "").lower())
r=B.call("rimworld/execute_debug_action",path=p,x=104,z=204)
for m in ((r.get("effects") or {}).get("logs") or []):
    s=str(m.get("message") if isinstance(m,dict) else m)
    if "[DeepfireLacquerBill]" in s: print(s[:900])
print(r.get("success"),str(r.get("message"))[:200])
