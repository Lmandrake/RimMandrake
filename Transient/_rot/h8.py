import sys, json, os, io, time, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
P=r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def count():
    try:
        d=open(P,"r",encoding="utf-8",errors="replace").read()
    except Exception as e:
        return -1
    return d.count("Could not instantiate or initialize a ThingComp")
SUS=["RUT_GrownFurnace","RUT_BrewingVessel","RUT_AgelessCap","RUT_RegenerantVeil","RUT_FalseFruit","RUT_Glimmerslime","RUT_PaleTree","RUT_Tea_AgeReversal","RUT_Symbiont_Quickflesh"]
base=count(); print("base",base)
with RimBridge(host, port, token) as rb:
    x=200
    for d in SUS:
        rb.call("jawa/spawn_batch",{"ops":"%s:%d,%d,1"%(d,x,200)})
        time.sleep(1.2)
        c=count()
        print(d, "count", c, "NEW" if c>base else "")
        base=c; x+=2
