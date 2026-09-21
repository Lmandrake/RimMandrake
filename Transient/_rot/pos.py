import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ALL="Human36838 Human36841 Human36844 Human36847 Human36850 Human36853 Human36856 Human36859 Human36862 Human36865 Human36868 Human36871".split()
with RimBridge(host, port, token) as rb:
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    for pid in ALL:
        p=ps.get(pid,{}); ci=rb.call("rimworld/get_cell_info",{"x":p.get("x",0),"z":p.get("z",0)})["cell"]
        print(pid,p.get("name"),(p.get("x"),p.get("z")),"roof",ci.get("roofDefName"),"drafted?", p.get("drafted"))
