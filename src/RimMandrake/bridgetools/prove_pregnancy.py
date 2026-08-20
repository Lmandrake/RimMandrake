import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
# the brief listing has no gender - fetch each pawn's full snapshot
brief = call("jawa/pawn_get", limit=20)["pawns"]
full = []
for b in brief:
    if b.get("faction") != "PlayerColony": continue
    f = call("jawa/pawn_get", pawn=str(b["thingIdNumber"]))["pawns"][0]
    full.append(f)
print("colonists:", [(p["nameShort"], p["gender"], p["ageBiologicalYears"]) for p in full])
males = [p for p in full if p["gender"] == "Male"]
females = [p for p in full if p["gender"] == "Female"]
if not (males and females):
    print("no mixed-gender pair; forcing one pawn to Female")
    tgt = full[0]
    call("jawa/set_pawn_appearance", pawn=str(tgt["thingIdNumber"]), bodyType="Female")
    print("   NOTE: set_pawn_appearance does not change pawn.gender - that is a separate field")
    females = []
M = str(males[0]["thingIdNumber"]) if males else None
F = str(females[0]["thingIdNumber"]) if females else None
if not (M and F):
    print("SKIP: need one male and one female colonist. males=%d females=%d" % (len(males), len(females)))
    raise SystemExit
print("mother:", females[0]["nameShort"], " father:", males[0]["nameShort"])

s1 = call("jawa/pawn_pregnancy", pawn=F, action="start", father=M)
print("start -> ok:", s1.get("success"), (s1.get("message") or "")[:140])
for n in (s1.get("notes") or []): print("   ", n)
print("   pregnant:", s1.get("pregnant"), " hediff:", s1.get("hediff"),
      " gestation:", s1.get("gestation"), " father:", s1.get("father"))
s2 = call("jawa/pawn_pregnancy", pawn=F, action="progress", progress=0.75)
print("progress 0.75 -> gestation:", s2.get("gestation"))
for n in (s2.get("notes") or []): print("   ", n)
s3 = call("jawa/pawn_pregnancy", pawn=F, action="get")
print("read back -> pregnant:", s3.get("pregnant"), " gestation:", s3.get("gestation"))
s4 = call("jawa/pawn_pregnancy", pawn=F, action="end", quiet=True)
print("end -> pregnant:", s4.get("pregnant"), " notes:", (s4.get("notes") or []))
