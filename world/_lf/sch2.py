import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
want={"jawa/spawn_pawn","jawa/pawn_get","jawa/list_pawns","jawa/pawnkind_audit"}
for x in b.list_tools():
    if x.get("name") in want:
        print("###", x["name"]); print(json.dumps(x.get("inputSchema") or {})[:900]); print()
