import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=60.0); S.connect()
names = [t.get("name") for t in (S.list_tools() or [])]
print(len(names), "tools")
for n in sorted(names):
    if any(k in n for k in ("quicktest","spawn","pawn","harmony","game_","map_","list_")):
        print(n)
