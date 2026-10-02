import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=240.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
def show(tag, r): print(tag, json.dumps(r)[:500])
show("map", call("jawa/map_info"))
r = call("jawa/spawn_pawn", kindDef="Colonist", x=140, z=140, faction="player", count=1); show("spawn", r)
pid = r["pawns"][0]["id"]
call("jawa/set_draft", pawnId=pid, drafted=False)
for x in range(135,146): call("jawa/spawn_thing", defName="Wall", x=x, z=141, stuffDef="BlocksGranite") if False else None
show("job", call("jawa/ordered_job", pawnId=pid, jobDef="RM_PaintGraffitiJob", targetAX=140, targetAZ=140, waitTicks=600, timeoutSeconds=60))
show("pawn", call("jawa/pawn_get", pawn=pid))
