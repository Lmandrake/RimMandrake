import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for typ in ("VBE.BackgroundImageDef", "BackgroundImageDef"):
        r = rb.call("jawa/get_defs", {"defs": f"{typ}/RUT_BG_ShellIshkoGate", "fields": "label,path"})
        print(typ, "->", json.dumps(r)[:350])
