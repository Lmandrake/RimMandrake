"""prove_junk_reskin_live.py -- STARWARS_JUNK_RESKIN_1 clause A2, read-only against the running game.

Asks the deployed mod (jawa/static_call RSW_JunkReskinProof.Report) what the engine BUILT for the 24 reskinned junk
defs: Graphic_Random, every variant texture loaded from Textures/Things/Building/Ruins/RSW_Junk/<defName>/, and on
the rotatable ones (car frame, truck, troop carrier, warwalker claw/leg/torso, mega-cannon barrel) every variant a
Single that draws rotated, so the north-drawn picture turns with the building. Also scans Player.log for a texture
load error naming RSW_Junk. Spawns nothing.

Exit 0 = clause holds, 1 = it does not, 2 = UNMEASURED (no bridge, no game, mod not loaded).
Run with Windows python (python.exe) like the other live proofs.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "RimMandrake", "Utils", "rimbench"))

TYPE = "RimMandrake.StarWars.Patches.RSW_JunkReskinProof"
TEX_ERR = re.compile(r"(Could not load|Failed to find any textures|Cannot load).*RSW_Junk", re.I)


def main():
    try:
        import validation_core as vc
        b = vc.Bridge()
        r = b.call("jawa/static_call", type=TYPE, method="Report", args="x")
    except Exception as e:  # noqa: BLE001  no bridge / no game is not a verdict
        print("UNMEASURED: bridge call failed: %s" % str(e)[:300])
        return 2
    text = str((r or {}).get("result") or "")
    if not text:
        print("UNMEASURED: no result (is mandrake.rsw.patches loaded with its DLL?): %r" % (r,))
        return 2
    print(text)
    bad_log = []
    try:
        import game_paths
        with open(game_paths.PLAYER_LOG, encoding="utf-8", errors="replace") as fh:
            bad_log = [ln.strip() for ln in fh if TEX_ERR.search(ln)]
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: Player.log unreadable: %s" % e)
        return 2
    for ln in bad_log[:10]:
        print("LOG  " + ln[:300])
    ok = text.startswith("PASS ") and "junkReskin setting=True" in text and not bad_log
    print("A2 %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
