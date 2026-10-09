import sys, json, re, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h,port=p,token=t,timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation",None); r.pop("state",None)
    return r
b = open(r"src\RimMandrake\TerminalBiomes\Defs\BiomeDefs\RM_GreySea.xml", encoding="utf-8").read()
def roster(k):
    m = re.search(r"<%s>(.*?)</%s>" % (k,k), b, re.S); return re.findall(r"<(\w+)[^>]*>[\d.]+</\1>", m.group(1))
plants, cast = roster("wildPlants"), roster("wildAnimals")
SC = ["RM_SaltPillar","RM_SaltDome","RM_SaltChimney","RM_GreatSaltCrystal_White","RM_GreatSaltCrystal_Pink","RM_GreatSaltCrystal_Amber","RM_GreatSaltCrystal_Violet","RM_GreyFloorWreckHull","RM_GreyFloorWreckSpine"]
call("jawa/set_current_map", mapId=int(sys.argv[1]))
out = {}
for name, defs, pw in (("scatter",SC,False),("plants",plants,False),("cast",cast,True)):
    r = call("jawa/list_things", defName=",".join(defs), includePawns=pw, limit=3000)
    c = collections.Counter(x.get("def") for x in r.get("things") or [])
    out[name] = dict(c); print(name.upper(), "scanned=%s" % r.get("scanned"), len(defs), "asked;", dict(c))
pp = call("jawa/list_pawns", limit=3000).get("pawns") or []
print("ALLPAWNS", len(pp), collections.Counter(x.get("def") for x in pp).most_common(12))
print("SAMPLE", [(x.get("def"), x.get("x"), x.get("z"), x.get("dead"), x.get("downed")) for x in pp[:3]])
mi = call("rimworld/get_map_info") if False else None
