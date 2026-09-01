import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
def pawns(rb): return rb.call("jawa/list_pawns",{"faction":"hostile","limit":500}).get("count",0)
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    print("--- dry run: what would the storyteller resolve? ---")
    print(json.dumps(rb.call("jawa/incident_parms_preview", {"category":"ThreatBig"}), ensure_ascii=False)[:700])
    print("\n--- storyteller_fire RaidEnemy, faction=Pirate (the failing one) ---")
    for i in range(3):
        lb=lords(rb); t0=time.time()
        r=rb.call("jawa/storyteller_fire", {"incidentDef":"RaidEnemy","points":3000,"faction":"Pirate","dryRun":False})
        dt=time.time()-t0
        print("  try%d lordDelta=%+d pawns=%d %.2fs :: %s" % (i, lords(rb)-lb, pawns(rb), dt,
              json.dumps({k:v for k,v in r.items() if k!="operation"}, ensure_ascii=False)[:320]))
        rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    print("\n--- storyteller_fire RaidEnemy, faction=Empire (the working one) ---")
    lb=lords(rb); t0=time.time()
    r=rb.call("jawa/storyteller_fire", {"incidentDef":"RaidEnemy","points":3000,"faction":"Empire","dryRun":False})
    print("  lordDelta=%+d pawns=%d %.2fs :: %s" % (lords(rb)-lb, pawns(rb), time.time()-t0,
          json.dumps({k:v for k,v in r.items() if k!="operation"}, ensure_ascii=False)[:320]))
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    print("\n--- storyteller_fire RaidEnemy, NO faction (storyteller picks) x6 ---")
    for i in range(6):
        lb=lords(rb)
        r=rb.call("jawa/storyteller_fire", {"incidentDef":"RaidEnemy","points":3000,"dryRun":False})
        print("  try%d lordDelta=%+d pawns=%d :: %s" % (i, lords(rb)-lb, pawns(rb),
              json.dumps({k:v for k,v in r.items() if k not in ("operation",)}, ensure_ascii=False)[:260]))
        rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
