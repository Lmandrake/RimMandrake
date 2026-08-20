"""P2 proof: equipment primary-slot trap, apparel, inventory, hediffs, bionics, needs."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
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

call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
lst = call("jawa/pawn_get", limit=8)
tgt = next((p for p in lst["pawns"] if p.get("faction") == "PlayerColony"), lst["pawns"][0])
PID = str(tgt["thingIdNumber"])
print("pawn:", tgt["name"], PID)

def gear():
    g = call("jawa/pawn_get", pawn=PID)["pawns"][0]
    return ([e["def"] for e in g["equipment"]], [a["def"] for a in g["apparel"]])

print("\n== 0. clear, then baseline ==")
call("jawa/pawn_gear", pawn=PID, action="clear", clearWhat="all")
print("   after clear:", gear())

print("\n== 1. EQUIP a weapon ==")
e1 = call("jawa/pawn_gear", pawn=PID, action="equip", quality="Excellent", **{"def": "Gun_BoltActionRifle"})
print("   success:", e1.get("success"), (e1.get("message") or "")[:70])
print("   displaced:", e1.get("displaced"), " notes:", e1.get("notes"))
print("   equipment now:", gear()[0])

print("\n== 2. EQUIP A SECOND WEAPON - THE PRIMARY-SLOT TRAP ==")
e2 = call("jawa/pawn_gear", pawn=PID, action="equip", **{"def": "MeleeWeapon_LongSword"})
print("   displaced:", e2.get("displaced"))
print("   notes:", e2.get("notes"))
print("   equipment now:", gear()[0], " <- vanilla AddEquipment alone would have kept the rifle and logged an error")

print("\n== 3. WEAR apparel (Wear enforces CanWearTogether itself) ==")
for d in ("Apparel_Parka", "Apparel_Pants", "Apparel_BasicShirt"):
    w = call("jawa/pawn_gear", pawn=PID, action="wear", **{"def": d})
    print("   %-22s ok=%s notes=%s" % (d, w.get("success"), w.get("notes")))
print("   apparel now:", gear()[1])

print("\n== 4. INVENTORY ==")
i1 = call("jawa/pawn_gear", pawn=PID, action="inventory", count=42, **{"def": "MealSurvivalPack"})
print("   notes:", i1.get("notes"))

print("\n== 5. HEDIFF add/remove ==")
h1 = call("jawa/pawn_health", pawn=PID, action="add", hediff="Flu")
print("   add Flu ->", h1.get("didWhat"), " hediffCount:", h1.get("hediffCount"))
h2 = call("jawa/pawn_health", pawn=PID, action="remove", hediff="Flu")
print("   remove  ->", h2.get("didWhat"), " hediffCount:", h2.get("hediffCount"))

print("\n== 6. BIONIC with no RecipeDef ==")
b1 = call("jawa/pawn_health", pawn=PID, action="bionic", hediff="BionicEye", bodyPart="Eye")
print("   success:", b1.get("success"), (b1.get("message") or "")[:120])
if b1.get("success"):
    print("   ->", b1.get("didWhat"))
    print("   hediffs:", [(h["def"], h["part"]) for h in (b1.get("hediffs") or []) if h["def"] == "BionicEye"])

print("\n== 7. RESTORE is gated ==")
r1 = call("jawa/pawn_health", pawn=PID, action="restore", bodyPart="Eye")
print("   without confirm -> success:", r1.get("success"), (r1.get("message") or "")[:110])

print("\n== 8. NEEDS + a social thought without an otherPawn ==")
n1 = call("jawa/pawn_need", pawn=PID, action="need", need="Food", level=0.15)
print("   set Food:", n1.get("notes"))
n2 = call("jawa/pawn_need", pawn=PID, action="thought", thought="AteLavishMeal")
print("   non-social thought ok:", n2.get("success"), n2.get("notes"))
n3 = call("jawa/pawn_need", pawn=PID, action="thought", thought="RebuffedMyKindWords")
print("   social w/o other  -> success:", n3.get("success"), (n3.get("message") or "")[:110])
