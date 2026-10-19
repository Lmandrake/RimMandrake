#!/usr/bin/env python3
"""selftest_harvest_donor_free.py -- synthetic Player.logs, each one broken in exactly one way, must each be caught."""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harvest_donor_free as H  # noqa: E402

FAILS = []
N = [0]


def check(cond, what, extra=None):
    N[0] += 1
    print(("ok   " if cond else "FAIL ") + what + ("" if cond or extra is None else "  %s" % (extra,)))
    if not cond:
        FAILS.append(what)


MODS = ["brrainz.harmony", "ludeon.rimworld", "mandrake.rsw.swbestiary"]


def log(d, name, body, mods=MODS, ident=True):
    p = os.path.join(d, name)
    head = "RimWorld 1.6.4871 rev591\n" + ("[JawaBench] ready: 413 tools, build x\n" if ident else "")
    if mods is not None:
        head += "Initializing new game with mods:\n" + "".join("  - %s\n" % m for m in mods)
    open(p, "w").write(head + body)
    return p


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = H.main(argv + ["--no-index", "--no-history", "--expect-list", ""])
    return code, buf.getvalue()


def main():
    d = tempfile.mkdtemp()
    clean = log(d, "clean.log", "Some chatter\nNo textures found at Things/Item/NotOurs\n")
    code, out = run(["--log", clean])
    check(code == 0, "a clean donor-free log exits 0", out)
    check("mods loaded: 3" in out, "the loaded mod count comes from the log's own mod block", out)

    donor = log(d, "donor.log", "", mods=MODS + ["Sarg.AlphaBiomes (incompatible version)"])
    code, out = run(["--log", donor])
    check(code == 2 and "sarg.alphabiomes" in out, "BROKEN: a retired donor in the mod block exits 2", out)

    menu = log(d, "menu.log", "chatter\n", mods=None)
    code, out = run(["--log", menu])
    check(code == 3 and "UNMEASURED" in out, "BROKEN: no mod block (main menu) is UNMEASURED, exit 3", out)
    rm = os.path.join(d, "rm.json")
    json.dump({"success": True, "packageIds": MODS}, open(rm, "w"))
    code, out = run(["--log", menu, "--running-mods", rm])
    check(code == 0 and "reply file" in out, "a running_mods reply file stands in for the mod block", out)

    cap = log(d, "cap.log", "Reached max messages limit. Stopping logging to avoid spam.\n")
    code, out = run(["--log", cap])
    check(code == 3 and "BLIND" in out, "BROKEN: the Verse.Log cap makes the log blind, exit 3", out)

    xr = log(d, "xref.log", "Could not resolve cross-reference: No Verse.ThingDef named RSW_Ghost found to give to "
                            "Verse.ThingDefCountClass x\n")
    code, out = run(["--log", xr])
    check(code == 1 and "xrefOurs 1" in out, "BROKEN: a cross-reference naming RSW_ exits 1", out)

    exc = log(d, "exc.log", "System.NullReferenceException: Object reference not set\n"
                            "  at RimMandrake.FlowWorks.Pump.Tick () [0x0001] in <x>:0\n"
                            "  at Verse.TickManager.DoSingleTick () [0x0002] in <x>:0\n"
                            "UnityEngine.StackTraceUtility:ExtractStackTrace ()\n"
                            "(Filename: C:\\x.cpp Line: 1)\n\nlater line\n")
    s = H.classify(exc)
    check(s["exc"]["events"] == 1, "one exception with its frames is ONE event, not one per line", s["exc"])
    check(s["exc"]["ours"] == 1, "an exception whose stack names RimMandrake is attributed ours", s["exc"])
    code, out = run(["--log", exc])
    check(code == 1, "BROKEN: an exception event exits 1", out)

    tex = log(d, "tex.log", "Could not load Texture2D at 'Things/Plant/Echeveria/EcheveriaA' for def 'X' in any "
                            "active mod or in base resources.\n"
                            "Failed to find any textures at Things/Other/Mod while constructing Multi\n")
    s = H.classify(tex, our_tex={"Things/Plant/Echeveria/EcheveriaA"})
    check(s["tex"]["ours"] == 1 and s["tex"]["other"] == 1, "a texture miss on a path our XML names is ours; "
                                                           "another mod's is not", s["tex"])

    donors = {"AA_AngelMoth", "Bantha"}
    rn = H.renames_of(donors)
    check("RSW_Bantha" in rn and "RM_AngelMoth" in rn, "renames follow the P6 rewrite's rules", sorted(rn)[:6])
    mix = log(d, "mix.log",
              "Could not resolve cross-reference: No Verse.PawnKindDef named AA_AngelMoth found to give to Foo bar\n"
              "Could not resolve cross-reference: No Verse.ThingDef named RSW_Bantha found to give to Foo bar\n"
              "Could not resolve cross-reference: No Verse.ThingDef named RM_Real found to give to Foo bar\n"
              "Could not resolve cross-reference: No Verse.SoundDef named Pawn_X found to give to Foo bar\n"
              "Could not load reference to Verse.ThingDef named Bantha\n"
              "[RimMandrake: Baroque Biomes] Patch operation Verse.PatchOperationRemove(/Defs/PawnKindDef"
              "[defName=\"AA_AngelMoth\"]/x) failed\n"
              "Config error in RM_Foo: bad\n")
    s = H.classify(mix, donors=donors, renames=rn, our_mods={"RimMandrake: Baroque Biomes"})
    x = s["xref"]
    check((x["retired"], x["ours"], x["other"], x["bar"]) == (2, 1, 1, 2),
          "xref split: retired-donor-or-rename 2 / ours 1 / other 1; the bar counts RM_/RSW_ lines (2)", x)
    check(s["scribe"]["retired"] == 1, "a Scribe miss on a donor name is retired-donor", s["scribe"])
    check(s["patch"]["ours"] == 1 and s["patch"]["retiredTarget"] == 1, "a patch failure of ours aimed at a retired "
                                                                         "def is counted both ways", s["patch"])
    check(s["config"]["ours"] == 1, "a config error on an RM_ def is ours", s["config"])

    code, out = run(["--log", exc, "--against", clean])
    check("prev 0, +1" in out, "the delta against a previous log is printed", out)

    big = os.path.join(d, "big.log")
    with open(big, "w") as fh:
        fh.write("[JawaBench] ready\nInitializing new game with mods:\n  - ludeon.rimworld\n")
        for i in range(200000):
            fh.write("filler line %d with some text in it\n" % i)
    import time
    t = time.time()
    s = H.classify(big)
    check(s["lines"] == 200003 and time.time() - t < 20, "a 200k-line log streams in one pass", time.time() - t)

    print("\n%d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
