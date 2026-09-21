import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/get_defs",{"defs":"RoyalTitleDef/Knight;JobDef/Meditate;MeditationFocusDef/Natural;HediffDef/PsychicAmplifier;ThingDef/Plant_TreeAnima;AbilityDef/Skip","fields":"defName,label"})
    print("royalty probes:", [(x.get("requested"),x.get("found")) for x in r.get("defs",[])])
    rb.call("jawa/destroy_batch",{"rects":"118,120,9,9","categories":"All"})
    s=rb.call("jawa/spawn_batch",{"ops":"RUT_PaleTree:122,124,1"})
    print("tree:", json.dumps({k:v for k,v in s.items() if k!="operation"})[:250])
    t=rb.call("jawa/list_things",{"defName":"RUT_PaleTree"})
    print("trees:", [(x["id"],x["x"],x["z"]) for x in t.get("things",[])])
    ins=rb.call("jawa/inspect_string",{"defName":"RUT_PaleTree"})
    print("inspect:", json.dumps(ins.get("things"))[:600])
