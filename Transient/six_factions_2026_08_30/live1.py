import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
KEY = ["Empire","Insect","OutlanderCivil","TribeCivil","TradersGuild","Pirate","CASacrilegHunters",
       "Jawa_HuttCartel","Jawa_Junkers","Jawa_AscendantHelix","Jawa_FreeDroidEnclaves",
       "Jawa_IndigenousTribes","Jawa_WildsteamClan","Jawa_GeonosianFoundryHive","Jawa_DeepwaterCompact"]
out={}
with RimBridge(host, port, token) as rb:
    f = rb.call("jawa/list_factions", {"includeHidden": True})
    out["factions"]=f
    print("FACTION_KEYS", [k for k in f.keys() if k!="operation"])
    lst = f.get("factions") or []
    print("N", len(lst), "sample", json.dumps(lst[0])[:400] if lst else None)
    rel = rb.call("jawa/faction_relations_get", {})
    out["relations"]=rel
    print("REL_KEYS", [k for k in rel.keys() if k!="operation"])
    print("REL_SAMPLE", json.dumps(rel)[:900])
    for fd in KEY:
        try:
            out["ideo_"+fd] = rb.call("jawa/faction_ideo_get", {"factionDefName": fd})
        except Exception as e:
            out["ideo_"+fd] = {"error": str(e)}
    out["raid_preview"] = rb.call("jawa/raid_preview", {"points": 3000})
with io.open("live1.json","w",encoding="utf-8") as fh: json.dump(out, fh, indent=1, ensure_ascii=False)
print("WROTE live1.json")
