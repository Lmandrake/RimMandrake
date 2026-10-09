import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def show(tag, r):
    print(tag, "|", json.dumps(r, default=str)[:900]); sys.stdout.flush()
for kind in ["AA_GreenGoo", "AA_Thunderbeast"]:
    with S.Scene("burst_"+kind, 30, 30, 30, 30) as sc:
        pid = sc.pawn(kind, 15, 15)
        before = S.call("rimworld/get_game_info").get("ticksGame")
        show("DMG "+kind, S.call("jawa/damage", damageDef="Bomb", amount=2000, thingId=pid))
        S.run(30)
        t = sc.things()
        names = sorted(set((x.get("def") or x.get("defName") or "?") for x in (t.get("things") or [])))
        print("THINGS", kind, names[:40]); sys.stdout.flush()
        show("CONDS "+kind, S.call("jawa/list_game_conditions") if True else None)
