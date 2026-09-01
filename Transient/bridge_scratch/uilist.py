import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    names = sorted(d.get("name") for d in rb.list_tools())
    for kw in ("ui_","gizmo","button","window","world_","planet","tab","click"):
        hits=[n for n in names if kw in n.lower()]
        print(kw, "->", hits)
