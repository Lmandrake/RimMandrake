import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
P=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def count():
    return open(P,"r",encoding="utf-8",errors="replace").read().count("Could not instantiate or initialize a ThingComp")
base=count(); print("base",base)
with RimBridge(host, port, token) as rb:
    for d,x in [("Plant_TreeAnima",220),("RUT_PaleTree",224),("Plant_TreeAnima",228),("RUT_PaleMoss",232),("Plant_GrassAnima",236)]:
        r=rb.call("jawa/spawn_batch",{"ops":"%s:%d,%d,1"%(d,x,200)})
        time.sleep(1.2); c=count(); print(d,"->",c,"NEW" if c>base else "", r.get("message")[:60]); base=c
