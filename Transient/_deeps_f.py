import sys, json, collections; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="4f3c0a7aa74e4446ac19465c14fd54a9"
b=RimBridge(token=T,timeout=90); b.connect()
def call(t,p={}): return b.call(t,p,check=False)
r=call("jawa/list_things",{"limit":5000})
things=r.get("things") or []
print("message:", r.get("message"))
c=collections.Counter(t.get("def") for t in things)
print("TOTAL things:", len(things)); print("by def:", dict(c.most_common(25)))
r=call("jawa/export_things",{}) ; print("export_things:", json.dumps(r)[:300])
