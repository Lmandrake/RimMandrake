import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

TARGETS = ["Pirate","Jawa_AscendantHelix","Jawa_DeepwaterCompact","Jawa_FreeDroidEnclaves",
           "Jawa_GeonosianFoundryHive","Jawa_HuttCartel","Jawa_Junkers","Jawa_IndigenousTribes",
           "Jawa_WildsteamClan","TribeCivil","OutlanderCivil","Empire"]
mode = sys.argv[1] if len(sys.argv)>1 else "--check"
todo = ["Pirate"] if mode=="--test" else [t for t in TARGETS if t!="Pirate"] if mode=="--rest" else []

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    fs = rb.call("jawa/list_factions", {}).get("factions", [])
    from collections import Counter
    c = Counter(f["defName"] for f in fs)
    dups = {d:n for d,n in c.items() if d in TARGETS and n>1}
    missing = [t for t in TARGETS if c.get(t,0)==0]
    print("faction instances per target:", {t:c.get(t,0) for t in TARGETS})
    if dups: print("!! MULTI-INSTANCE DEFS (tool converts only the FIRST):", dups)
    if missing: print("!! NOT IN WORLD:", missing)
    for t in todo:
        b = rb.call("jawa/faction_ideo_get", {"factionDefName": t})
        r = rb.call("jawa/faction_ideo_set", {"factionDefName": t, "confirmReplace": True})
        a = rb.call("jawa/faction_ideo_get", {"factionDefName": t})
        ok = r.get("success") is True and a.get("success") is True
        print(f"{t}: {b.get('ideoName')!r} -> {a.get('ideoName')!r} | title M/F: "
              f"{a.get('leaderTitleMale')!r}/{a.get('leaderTitleFemale')!r} | "
              f"memes {a.get('memeCount')} precepts {a.get('preceptCount')} | "
              f"ideoClassic {r.get('newIdeoClassicMode')} | {'OK' if ok else 'FAIL: '+json.dumps(r)[:200]}")
