import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        names = [t.get("name","") for t in rb._request("tools/list", {}).get("tools", [])]
        print("tools:", len(names), "| jawa:", len([n for n in names if n.startswith("jawa/")]))
        print("ideo-ish:", [n for n in names if "ideo" in n.lower()])
    except Exception as e:
        print("tools/list failed:", e)
    gi = rb.call("rimworld/get_game_info", {})
    print("game_info:", {k: gi.get(k) for k in ("gameLoaded","tickCount","ticksGame","mapCount","worldName","scenario") if k in gi})
    fac = rb.call("jawa/list_factions", {})
    rows = fac.get("factions", fac) if isinstance(fac, dict) else fac
    print("faction rows:", len(rows))
    for f in rows:
        print("-", f.get("name"), "|", f.get("defName") or f.get("def"), "| ideo:", f.get("ideo") or f.get("ideoName") or f.get("primaryIdeo"))
