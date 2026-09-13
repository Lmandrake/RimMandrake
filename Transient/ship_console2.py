import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    f = rb.call("jawa/get_terrain_layers", {"rect": "183,148,8,5", "limit": 60})
    found = {(c["x"],c["z"]): (c.get("foundation"), c.get("top")) for c in f.get("cells", [])}
    for z in range(152, 147, -1):
        print(z, [ (x, found.get((x,z),("-","-"))[0] and "F" or ".", ) for x in range(183,191)])
    c = rb.call("jawa/build_check", {"ops": "PilotConsole:184,150,0"})
    print("build_check:", str(c)[:300])
