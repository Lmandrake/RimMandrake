import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
TEST=set("Human36838 Human36841 Human36844 Human36847 Human36850 Human36853 Human36856 Human36859 Human36862 Human36865 Human36868 Human36871".split())
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/set_roof_batch",{"ops":"None:136,128,5,5;None:144,128,5,5;None:152,128,5,5"})
    print("unroof:", r.get("message"))
    for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[]):
        if p.get("intelligence")!="Humanlike": continue
        d=rb.call("jawa/set_draft",{"pawnId":p["id"],"drafted":True})
        print("draft",p["id"],p["name"],d.get("success"),str(d.get("message"))[:80], "TEST" if p["id"] in TEST else "")
    # also remove any roof-build designations
    print("designations at pen:", json.dumps(rb.call("rimworld/get_cell_info",{"x":138,"z":130})["cell"].get("designations"))[:200])
