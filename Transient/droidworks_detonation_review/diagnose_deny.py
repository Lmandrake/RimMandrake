import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs": "ThingDef/RSW_DW_Race_JDSCIS_B1_Battle_Droid",
                                    "fields": "modExtensions,comps", "deep": True})
    print(json.dumps(r, indent=2)[:4000])
