"""prove_metal_nonflammable_live.py -- live proof of METAL_STONE_NONFLAMMABLE (owner order 2026-11-08).

    python3 src/RimMandrake/MandrakePatches/prove_metal_nonflammable_live.py
    python3 src/RimMandrake/MandrakePatches/prove_metal_nonflammable_live.py --selftest    # offline: the judge goes red on mutants

Needs a started game whose load holds RimMandrake Patches AFTER the DLL was deployed and the game restarted. One read-only
jawa/static_call to RimMandrake.Patches.MetalNonFlammable.Probe, which returns the game's own computed Flammability of a vanilla
Wall built from steel, gold, silver, plasteel, granite, marble, jade, diamond, RSW_Durasteel, RSW_Transparisteel, KOTOR_Duracrete,
RM_Vexxith, RM_Lanternstone and (control) WoodLog. Holds when every present metal/stone/gem reads 0 and the WoodLog control reads
above 0 (an instrument that reads 0 for wood too is blind, not proof). Steel, the vanilla case that burns (0.4), must be present.
Exit 0 holds, 1 a metal still burns, 2 UNMEASURED (no bridge answer, setting off, or the control reads 0).
Callers hold the bridge lock; this never takes it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

PASS, FAIL, UNMEASURED = 0, 1, 2
CONTROL = "WoodLog"


def parse(text):
    """'Wall|Steel=0;Wall|WoodLog=1' -> {'Steel': 0.0, 'WoodLog': 1.0, 'X': None (absent)}, or None when it is not that shape."""
    if not isinstance(text, str) or "|" not in text:
        return None
    out = {}
    for part in text.strip().split(";"):
        try:
            k, v = part.split("=", 1)
            name = k.split("|", 1)[1]
            out[name] = None if v.strip() == "absent" else float(v)
        except (ValueError, IndexError):
            return None
    return out or None


def judge(vals):
    """Pure. vals: parse() result or None -> (code, lines)."""
    if vals is None:
        return UNMEASURED, ["UNMEASURED no readable Probe answer"]
    out, fails = [], []
    ctrl = vals.get(CONTROL)
    if ctrl is None or ctrl <= 0:
        return UNMEASURED, ["UNMEASURED control %s reads %r: the instrument cannot see a burning wall (or the stat is off everywhere)" % (CONTROL, ctrl)]
    out.append("ok control %s wall = %g (burns)" % (CONTROL, ctrl))
    if vals.get("Steel") is None:
        return UNMEASURED, out + ["UNMEASURED Steel is not in the load"]
    for name, v in sorted(vals.items()):
        if name == CONTROL:
            continue
        if v is None:
            out.append("skip %s: not in this load" % name)
        elif v == 0:
            out.append("ok %s wall = 0" % name)
        else:
            fails.append("FAIL %s wall = %g (still burns)" % (name, v))
    code = FAIL if fails else PASS
    return code, out + fails + [{PASS: "VERDICT PASS", FAIL: "VERDICT FAIL"}[code]]


def selftest():
    good = parse("Wall|Steel=0;Wall|RSW_Durasteel=0;Wall|RM_Vexxith=absent;Wall|WoodLog=1")
    steps = [
        ("good answer holds", judge(good)[0] == PASS),
        ("steel at 0.4 fails", judge(parse("Wall|Steel=0.4;Wall|WoodLog=1"))[0] == FAIL),
        ("an RSW metal at 0.2 fails", judge(parse("Wall|Steel=0;Wall|RSW_Durasteel=0.2;Wall|WoodLog=1"))[0] == FAIL),
        ("wood reading 0 is unmeasured, not a pass", judge(parse("Wall|Steel=0;Wall|WoodLog=0"))[0] == UNMEASURED),
        ("no steel in the load is unmeasured", judge(parse("Wall|Steel=absent;Wall|WoodLog=1"))[0] == UNMEASURED),
        ("garbage is unmeasured", judge(parse("nonsense"))[0] == UNMEASURED and judge(None)[0] == UNMEASURED),
    ]
    bad = [n for n, ok in steps if not ok]
    for n, ok in steps:
        print(("ok   " if ok else "FAIL ") + n)
    return 1 if bad else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    from live_def_check import _bridge
    reply, why = _bridge("jawa/static_call", {"type": "RimMandrake.Patches.MetalNonFlammable", "method": "Probe", "args": ""}, 60,
                         read_only_static=True)
    if reply is None:
        print("UNMEASURED bridge: " + str(why))
        return UNMEASURED
    if not isinstance(reply, dict) or not reply.get("success"):
        print("UNMEASURED the static call failed: %r" % (reply,))
        return UNMEASURED
    text = str(reply.get("result")).strip().strip('"')
    code, lines = judge(parse(text))
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
