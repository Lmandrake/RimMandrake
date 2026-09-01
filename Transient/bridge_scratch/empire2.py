import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("=== live Empire field ===")
    r = rb.call("jawa/get_defs", {"defs":"FactionDef/Empire","fields":"permanentEnemyToEveryoneExcept,permanentEnemy"})
    print(json.dumps(r, indent=1)[:2500])
    for t in ("FactionDef","Faction","FactionGenerator","DefGenerator","FactionManager","GameInitData","DirectXmlLoader","LoadedModManager","XmlInheritance"):
        print("=== harmony_patches", t, "===")
        try:
            r = rb.call("jawa/harmony_patches", {"typeName": t})
            s = json.dumps(r)
            print(s[:3000])
        except Exception as e:
            print("ERR", e)
