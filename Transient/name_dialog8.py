import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try: rb.call("rimworld/click_ui_target", {"zzz": 1})
    except Exception as e: print("click_ui_target:", str(e).split("Declared:")[-1].strip())
    r = rb._request("tools/list", {})
    tools = [t["name"] for t in r.get("tools", [])]
    print("text-ish tools:", [t for t in tools if any(s in t for s in ("text","input","key","type"))])
