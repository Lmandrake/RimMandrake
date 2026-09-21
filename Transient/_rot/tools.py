import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ts = rb.list_tools()
    names = sorted(t["name"] for t in ts)
    print(len(names), "tools;", sum(1 for n in names if n.startswith("jawa/")), "jawa")
    open("Transient/_rot/tools.txt","w").write("\n".join(names))
    for n in names:
        if any(k in n for k in ("condition","weather","hediff","temper","room","roof","terrain","pawn","time","tick","quicktest","debug_game","camera","screenshot","spawn","harvest","stat","rot","thing_")):
            print(n)
