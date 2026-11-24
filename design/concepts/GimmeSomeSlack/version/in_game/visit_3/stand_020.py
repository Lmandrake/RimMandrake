"""stand_020.py -- two labelled stands for the 0.2.0 features on the walk map (after human_review.py --build), by the
scenes' own probe verbs. python.exe, bridge held. Stands 32 (one line, every kind of piece) and 33 (wall lamps)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack")
sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, scene_rows as S, human_review as H
from modcheck import reviewmap as RM
X, Z, W, HT = 20, 60, 40, 30
B = VA.A()
S.SITE = (X - 3, Z - 3, W + 6, HT + 6)
def stage():
    S._site(B, V)
    # 32: the line
    x, z = X, Z
    la = S._line(x + 2, z + 4, x + 8, z + 4) + S._line(x + 10, z + 4, x + 12, z + 4)
    lb = S._line(x + 23, z + 4, x + 26, z + 4)
    sw, ma, mb, br = (x + 9, z + 4), (x + 13, z + 4), (x + 22, z + 4), (x + 27, z + 4)
    out = {}
    out["b1"] = B.call("jawa/build_batch", ops=V.ops("Wall", [(br[0], br[1] + 1)]), stuff="Steel", faction="player", wipeExisting=False)
    out["b2"] = B.call("jawa/build_batch", ops=V.ops("PowerConduit", la + lb), faction="player", wipeExisting=False)
    out["b3"] = B.call("jawa/build_batch", ops="Battery:%d,%d,0;PowerSwitch:%d,%d,0;RM_AerialMast:%d,%d;RM_AerialMast:%d,%d;RM_AerialWallBracket:%d,%d,0" % ((x + 1, z + 4) + sw + ma + mb + br), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ap("cplace:StandingLamp:Industrial:%d,%d:god" % (x + 5, z + 5)); B.ticks(3)
    _, mem, _ = S._styles(B, (x, z, 32, 10))
    ids = {c: m.get("id") for c, m in mem.items()}
    out["link"] = B.ap("link:%d,%d" % (ids[ma], ids[mb]))
    B.ap("cprocess"); B.ap("crestyle:%d,%d:Industrial" % la[0]); B.ap("cprocess")
    S._fill(B, (x, z, 32, 10))
    # 33: wall lamps
    z = Z + 14
    B.call("jawa/build_batch", ops=V.ops("Wall", S._line(x + 2, z + 8, x + 24, z + 8) + S._line(x + 26, z + 2, x + 26, z + 7)), stuff="Steel", faction="player", wipeExisting=False)
    cord = S._line(x + 2, z + 6, x + 24, z + 6)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x + 1, z + 6), faction="player", wipeExisting=False)
    out["cl"] = B.ap("cline:PowerConduit:Industrial:%d,%d:%d,%d:god" % (cord[0] + cord[-1]))
    out["wl"] = [B.ap("cplace:WallLamp:%s:%d,%d:god" % (l, x + 3 + 4 * i, z + 7)).get("success") for i, l in enumerate(S.LOOK_NAMES)]
    out["wl"].append(B.ap("cplace:WallLamp:Industrial:%d,%d:god" % (x + 21, z + 7)).get("success"))
    out["wl"].append(B.ap("cplace:StandingLamp:Industrial:%d,%d:god" % (x + 18, z + 5)).get("success"))
    f = [(x + 25, z + 4, 1), (x + 27, z + 4, 3), (x + 6, z + 9, 2)]
    B.call("jawa/build_batch", ops=";".join("WallLamp:%d,%d,%d" % c for c in f), faction="player", wipeExisting=False)
    B.ticks(2)
    out["clamp"] = [B.ap("clamp:%d,%d:%s" % (c[0], c[1], l)).get("success") for c, l in zip(f, ("Futuristic", "Industrial", "Modern"))]
    B.ap("cprocess"); S._fill(B, (x, z, 32, 14)); B.ticks(2)
    out["walllamps"] = [(l["def"], l.get("look"), l.get("drawnPath")) for l in (S._styles(B, (x, z, 30, 12))[2]).values()]
    return out
def label():
    t = [(X, Z + 9, 32, "ONE LINE, EVERY PIECE", "cords, a switch, two poles with their wire, a wall bracket and a standing lamp: one line",
          "select any piece, Restyle, pick a look, All connected: every piece and the lamp must change together; each look shows its own icon in the menu",
          "a piece that keeps the old look"),
         (X, Z + 25, 33, "WALL LAMPS IN THE FOUR LOOKS", "four looks on one wall, one lamp beside a standing lamp, and lamps facing east, west and south",
          "restyle the cord, All connected: the Industrial wall lamps follow it; each wall lamp has its own Restyle", "a lamp that does not read as its look, or floats off its wall")]
    L = [RM.label_line(x + 15, z, "%d  %s" % (n, ti), RM.weak_spot_sign(sub, "", do, weak), H.GOLD, "medium", "GSS020") for x, z, n, ti, sub, do, weak in t]
    r1 = B.call("jawa/review_label", action="add", ops="\n".join(L), tag="GSS020")
    ops = [RM.sign_book(x, z - 1, n, ti, sub, "", do, RM.weak_decide(weak)) for x, z, n, ti, sub, do, weak in t]
    r2 = B.call("jawa/review_sign", action="place", ops="\n".join(ops))
    return r1, r2
if "label" not in sys.argv[1:2]:
    print(json.dumps(stage(), default=str)[:3000])
print(json.dumps(label(), default=str)[:1200])
