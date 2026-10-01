"""TERMINALBIOMES_REVIEW_FIXES_1 live state reads (run under python.exe from the repo root, map loaded).

1. effective tickerType of RM_VauliskLure and RM_CargoFloat (jawa/get_defs, reflective field read).
2. lure springs: spawn RM_VauliskLure at (X,Z) with NO pawn in 1.9 cells, step 2100 ticks
   (> one TickLong bucket) -> lure still there (no false spring). Then spawn a pawn on the
   adjacent cell, step 2100 more -> lure gone AND an RM_Vaulisk pawn spawned near it.
"""
import json
import sys

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb

X, Z = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (60, 30)
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def things(dn):
    r = call("jawa/list_things", defName=dn, limit=50)
    return r.get("things") or r.get("rows") or [], r


def vaulisks():
    r = call("jawa/list_pawns", rect="%d,%d,%d,%d" % (X - 6, Z - 6, 13, 13))
    ps = r.get("pawns") or r.get("rows") or []
    return [p for p in ps if "Vaulisk" in json.dumps(p)], r


print("== 1 effective tickerType ==")
d = call("jawa/get_defs", defs="ThingDef/RM_VauliskLure;ThingDef/RM_CargoFloat;PawnKindDef/RM_Vaulisk",
         fields="tickerType,comps")
print(json.dumps(d)[:2500])

print("== 2a spawn lure, no pawn near ==")
print(json.dumps(call("rimworld/spawn_thing", defName="RM_VauliskLure", x=X, z=Z))[:400])
t, raw = things("RM_VauliskLure")
print("lure count after spawn:", len(t), json.dumps(raw)[:400])
v0, _ = vaulisks()
print("vaulisks near before:", len(v0))
print(json.dumps(call("rimworld/step_game_ticks", ticks=2100))[:200])
t, raw = things("RM_VauliskLure")
print("CONTROL lure count after 2100 ticks alone:", len(t))

print("== 2b pawn adjacent ==")
for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    sp = call("jawa/spawn_pawn", kindDef="Muffalo", x=X + dx, z=Z + dz, faction="none")
    print("spawn pawn:", json.dumps(sp)[:300])
for i in range(3):
    call("rimworld/step_game_ticks", ticks=700)
    t, _ = things("RM_VauliskLure")
    v, _ = vaulisks()
    print("after +%d ticks: lure=%d vaulisk_near=%d" % (700 * (i + 1), len(t), len(v)))
v, raw = vaulisks()
print("vaulisk rows:", json.dumps(v)[:1500])
