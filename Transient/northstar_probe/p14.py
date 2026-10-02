import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimdrive.session import Session
def fires(s): return s.call("jawa/list_things", defName="Fire")["countMatched"]
with Session(strict=False, quiet=True, focus=False) as s:
    r=s.call("jawa/spawn_pawn", kindDef="Boomalope", x=60, z=60, faction="none"); a=r["pawns"][0]["id"]
    s.call("jawa/pawn_force_incapacitate", pawn=a, action="kill")
    for n in (0, 5, 30, 120):
        if n: s.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
        print("after +%d: fires=%d" % (n, fires(s)))
    s.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    # which wild animals does a fresh map carry? (explosive ones)
    from collections import Counter
    print(Counter(x["kindDef"] for x in s.call("jawa/list_pawns", limit=500)["pawns"] if x["faction"] is None and x["intelligence"]=="Animal").most_common(12))
