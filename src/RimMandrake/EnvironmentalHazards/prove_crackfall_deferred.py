"""Live proof of MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES clause A2: a due RM_Mirrelbole survives the real Plant.TickLong
without the NRE and falls on a later map tick.

    python.exe src/RimMandrake/EnvironmentalHazards/prove_crackfall_deferred.py < /dev/null

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED. Any Playing quicktest map with Greentide loaded; the probe
RM_CrackFallProof (Source/RM_CompCrackFall.cs) answers through jawa/static_call. judge() is unit-tested offline by
selftest_crackfall_deferred.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = "RimMandrake.EnvironmentalHazards.RM_CrackFallProof"
SETTLE_TICKS = 5


def judge(stage, read):
    """(exit code, why) from the two probe answers."""
    for text in (stage, read):
        if text.startswith("FAIL"):
            return 1, text
        if text.startswith("UNMEASURED"):
            return 2, text
    if not stage.startswith("STAGED"):
        return 2, "UNMEASURED: the probe did not answer: " + stage[:200]
    if read == "READ felled=True":
        return 0, "PASS A2: Plant.TickLong ran with the fall due, no throw; the tree fell after the map ticked"
    if read == "READ felled=False":
        return 1, "FAIL A2: the tree was still standing %d ticks after its fall was queued" % SETTLE_TICKS
    return 2, "UNMEASURED: the probe did not answer: " + read[:200]


def main():
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    try:
        import validation_core as VC
        B = VC.Bridge()

        def probe(method):
            r = B.call("jawa/static_call", type=PROBE, method=method, args="")
            return str((r or {}).get("result", r)) if isinstance(r, dict) else str(r)

        stage = probe("Stage")
        read = ""
        if stage.startswith("STAGED"):
            B.ticks(SETTLE_TICKS)
            read = probe("Read")
    except Exception as ex:
        print("UNMEASURED: no bridge or game: %s" % type(ex).__name__)
        return 2
    code, why = judge(stage, read)
    print(why)
    return code


if __name__ == "__main__":
    sys.exit(main())
