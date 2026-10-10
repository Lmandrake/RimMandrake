import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x, n=400): return json.dumps(x, default=str)[:n]
# ART_OVERRIDE_FOLD_ALL_1 F3: donor-def + RSW_-port specimens of folded creatures, texPath read + screenshot.
X, Z = int(sys.argv[1]), int(sys.argv[2])
kinds = sys.argv[3].split(",")
# def read-back: which texPath does each kind's lifeStages carry now
for k in kinds:
    r = S.call("jawa/get_defs", defs="PawnKindDef/" + k)
    print("DEF", k, j(r, 900))
S.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (X - 2, Z - 2, len(kinds) * 4 + 4, 8))
for i, k in enumerate(kinds):
    r = S.call("jawa/spawn_pawn", kindDef=k, x=X + i * 4, z=Z, faction="player", count=1)
    print("SPAWN", k, j(r, 200))
print("SHOT", j(S.call("rimworld/screenshot_cell_rect", x=X - 2, z=Z - 3, width=len(kinds) * 4 + 3, height=7, paddingCells=1), 400))
