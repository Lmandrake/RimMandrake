"""prove_draw_order_live.py -- live proof of RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES (owner 2026-10-16, 2026-11-08:
"if you are more south, you go in front"; "for ALL large pawns and objects in the game").

    python3 src/RimMandrake/MandrakePatches/prove_draw_order_live.py
    python3 src/RimMandrake/MandrakePatches/prove_draw_order_live.py --selftest    # offline: the judge goes red on mutants

Needs a started game whose load holds RimMandrake Patches AFTER the DLL was deployed and the game restarted, with at least
two large pawns (body size >= 1.5 or drawn taller than 1.5 cells, e.g. two Dalgo mares) standing within 1.5 cells across
and 2.5 cells north-south of each other on the current map. One read-only jawa/static_call to
RimMandrake.Patches.SouthDrawsFrontPatches.Probe, which returns, per such pair, both pawns' tweened z and the game's own
DrawPos.y (larger y = in front). Holds when, for every pair, the southern pawn's y is larger. Vanilla's SeededYOffset of
both is returned too: a pair where vanilla would have put the northern one in front is counted (the bug this fixes).
Exit 0 holds, 1 a northern pawn draws in front, 2 UNMEASURED (no bridge answer, setting off, patch not routed, no pair).
Callers hold the bridge lock; this never takes it. Written 2026-11-08, NOT yet run: the owner was playing.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

PASS, FAIL, UNMEASURED = 0, 1, 2


def parse(text):
    """'setting=1;pawnRouted=1;printRouted=1;big=2;pair=A|B|zS|zN|yS|yN|sS|sN' -> dict, or None when not that shape."""
    if not isinstance(text, str) or "setting=" not in text:
        return None
    out = {"pairs": []}
    try:
        for part in text.strip().split(";"):
            k, v = part.split("=", 1)
            if k == "pair":
                f = v.split("|")
                out["pairs"].append({"south": f[0], "north": f[1], "zS": float(f[2]), "zN": float(f[3]),
                                     "yS": float(f[4]), "yN": float(f[5]), "seedS": float(f[6]), "seedN": float(f[7])})
            else:
                out[k] = v
    except (ValueError, IndexError):
        return None
    return out


def judge(vals):
    """Pure. vals: parse() result or None -> (code, lines)."""
    if vals is None:
        return UNMEASURED, ["UNMEASURED no readable Probe answer"]
    if vals.get("setting") != "1":
        return UNMEASURED, ["UNMEASURED the setting 'Southern things draw in front' is off"]
    if vals.get("pawnRouted") != "1":
        return UNMEASURED, ["UNMEASURED Pawn_DrawTracker.DrawPos was not patched (see the log line '[RimMandrake Patches] south draws front:')"]
    if vals.get("map") == "none":
        return UNMEASURED, ["UNMEASURED no current map"]
    pairs = vals["pairs"]
    if not pairs:
        return UNMEASURED, ["UNMEASURED no two large pawns close enough to overlap (big=%s): stage two Dalgo mares a cell apart" % vals.get("big")]
    out, fails, flipped = [], [], 0
    for p in pairs:
        if p["zS"] >= p["zN"]:
            return UNMEASURED, out + ["UNMEASURED the probe returned a pair out of order: %r" % p]
        if p["seedN"] > p["seedS"]:
            flipped += 1
        line = "%s (z %.2f, y %.5f) vs %s north (z %.2f, y %.5f)" % (p["south"], p["zS"], p["yS"], p["north"], p["zN"], p["yN"])
        if p["yS"] > p["yN"]:
            out.append("ok " + line)
        else:
            fails.append("FAIL " + line + ": the northern pawn draws in front")
    out.append("%d of %d pairs would have drawn north-in-front under vanilla's seed" % (flipped, len(pairs)))
    code = FAIL if fails else PASS
    return code, out + fails + [{PASS: "VERDICT PASS", FAIL: "VERDICT FAIL"}[code]]


def selftest():
    head = "setting=1;pawnRouted=1;printRouted=1;big=2"
    good = head + ";pair=Mare|Mare|10.500|11.500|8.70000|8.69880|-0.02|0.03"
    steps = [
        ("good answer holds", judge(parse(good))[0] == PASS),
        ("north in front fails", judge(parse(head + ";pair=Mare|Mare|10.5|11.5|8.69|8.70|0|0"))[0] == FAIL),
        ("equal y fails", judge(parse(head + ";pair=Mare|Mare|10.5|11.5|8.7|8.7|0|0"))[0] == FAIL),
        ("setting off is unmeasured", judge(parse(good.replace("setting=1", "setting=0")))[0] == UNMEASURED),
        ("unpatched is unmeasured", judge(parse(good.replace("pawnRouted=1", "pawnRouted=0")))[0] == UNMEASURED),
        ("no pair is unmeasured", judge(parse(head))[0] == UNMEASURED),
        ("a pair out of order is unmeasured", judge(parse(head + ";pair=A|B|12|11|8.7|8.6|0|0"))[0] == UNMEASURED),
        ("garbage is unmeasured", judge(parse("nonsense"))[0] == UNMEASURED and judge(None)[0] == UNMEASURED),
    ]
    for n, ok in steps:
        print(("ok   " if ok else "FAIL ") + n)
    return 0 if all(ok for _, ok in steps) else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    from live_def_check import _bridge
    reply, why = _bridge("jawa/static_call", {"type": "RimMandrake.Patches.SouthDrawsFrontPatches", "method": "Probe", "args": ""}, 60,
                         read_only_static=True)
    if reply is None:
        print("UNMEASURED bridge: " + str(why))
        return UNMEASURED
    if not isinstance(reply, dict) or not reply.get("success"):
        print("UNMEASURED the static call failed: %r" % (reply,))
        return UNMEASURED
    code, lines = judge(parse(str(reply.get("result")).strip().strip('"')))
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
