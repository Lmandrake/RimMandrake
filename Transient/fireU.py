import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PEN_CX, PEN_CZ = 300, 36   # 14 cells north of sniper at (300,22): outside min 12, close
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/build_batch", {"bogus":1})
    except Exception as e:
        print("build_batch declared:", str(e).split("Declared:")[-1].strip()[:140])
    # teleport thrumbo into pen spot first (T: Teleport acts on selection? it worked on SOMETHING last time)
    # select via debug: 'T: Select' ? use jawa select? try rimworld select_thing?
    names = [t["name"] for t in rb.list_tools()]
    print("select tools:", [n for n in names if "select" in n][:6])
    print("move tools:", [n for n in names if "teleport" in n or "move" in n][:6])
