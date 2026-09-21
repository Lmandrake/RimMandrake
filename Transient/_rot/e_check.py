import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for n,rect in {"PEN_BARE":(136,128),"PEN_HELM":(144,128),"PEN_SYM":(152,128)}.items():
        x0,z0=rect
        rows=[]
        for z in range(z0+1,z0+4):
            rows.append("".join("R" if rb.call("rimworld/get_cell_info",{"x":x,"z":z})["cell"].get("roofDefName") else "." for x in range(x0+1,x0+4)))
        print(n, rows)
