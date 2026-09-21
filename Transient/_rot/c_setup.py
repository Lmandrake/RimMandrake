import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # outdoor meat (3 stacks, several samples) + control meat in R1
    r = rb.call("jawa/spawn_batch", {"ops":"Meat_Cow:145,120,75;Meat_Cow:147,120,75;Meat_Cow:149,120,75"})
    print("outdoor meat:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
    r = rb.call("jawa/spawn_batch", {"ops":"Meat_Cow:142,102,75;Meat_Cow:143,102,75;Meat_Cow:144,102,75"})
    print("control meat:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
    # living produce: 200 units in R2
    r = rb.call("jawa/spawn_batch", {"ops":"RUT_Glimmerslime:152,102,75;RUT_Glimmerslime:153,102,75;RUT_Glimmerslime:154,102,50"})
    print("produce:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:300])
    # grown furnace in R5
    r = rb.call("jawa/spawn_batch", {"ops":"RUT_GrownFurnace:183,103,1"})
    print("furnace:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:400])
    for tag,rect in (("outdoor","145,120,6,1"),("control","142,102,3,1"),("produce","152,102,3,1"),("furnaceRoom","181,101,5,5")):
        t = rb.call("jawa/list_things", {"rect":rect})
        print(tag, [(x.get("defName"), x.get("stackCount"), x.get("x"), x.get("z")) for x in t.get("things",[])][:10])
