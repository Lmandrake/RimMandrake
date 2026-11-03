#!/usr/bin/env python3
"""Live proofs of WARSCAR_HOSPICE_DESERTERS_1, one clause per call: exit 0 when it holds, 1 when it does not, 2 when
the instrument cannot see (no bridge, no map, the hook type absent: never a verdict).

    python3 src/RimMandrake/Scarlands/hospice_live_proof.py A1|A2|A3|A4

Each clause is one jawa/static_call into RimMandrake.Scarlands.RM_HospiceProof (Source/RM_HospiceProof.cs) on the
CURRENT map of a quicktest colony with Warscar loaded (standalone or inside the Baroque Biomes composite):
  A1 Rings      RM_Warscar runs RM_KneelingRings live; the genstep lays rings facing their centre with 0..cap intact
                chassis, each holding a history that is in its save XML.
  A2 Revival    an intact chassis the haul workgiver offers is fed to a cradle with each stage's input and passes the
                five stages (stage time skipped by DebugCompleteStage); it wakes a colony mech with no mechanitor,
                its history's modification hediffs present, the cradle lights dark at diagnosis and lit after lights.
  A3 Failure    a forced failure at the lights stage leaves RM_FailedChassis labelled with the machine's name.
  A4 WalkIn     the walk-in incident fired with forced parms (pursuer held off), then real ticks through
                jawa/safe_advance until the servitor knelt within 6 cells of the cradle as an intact chassis.
It writes to the quicktest map only (every save but the canonical world saves is disposable) and never the world.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

TYPE = "RimMandrake.Scarlands.RM_HospiceProof"
METHOD = {"A1": "Rings", "A2": "Revival", "A3": "Failure"}
ADVANCE_STEP, ADVANCE_MAX = 2500, 12


def hook(c, method, args="current"):
    r = c.call("jawa/static_call", {"type": TYPE, "method": method, "args": args})
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("static_call %s refused: %r" % (method, r))
    return str(r.get("result", ""))


def main(argv):
    if len(argv) != 2 or argv[1] not in ("A1", "A2", "A3", "A4"):
        print(__doc__)
        return 2
    clause = argv[1]
    try:
        h, p, tok = rb.resolve_endpoint()
        c = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
        c.connect()
        if clause in METHOD:
            line = hook(c, METHOD[clause])
        else:
            fired = hook(c, "WalkInFire")
            if not fired.startswith("PASS fired: "):
                print("A4 " + fired)
                return 1
            unit = fired[len("PASS fired: "):].strip()
            line = "FAIL never read"
            for i in range(ADVANCE_MAX):
                adv = c.call("jawa/safe_advance", {"ticks": ADVANCE_STEP, "stopOn": "default"})
                line = hook(c, "WalkInRead", "current|" + unit)
                print("  +%d ticks: %s (advance: %s)" % ((i + 1) * ADVANCE_STEP, line,
                                                         (adv or {}).get("state") if isinstance(adv, dict) else adv), flush=True)
                if line.startswith("PASS") or "is gone" in line:
                    break
    except Exception as e:  # noqa: BLE001 -- any bridge failure is an instrument error, never a verdict
        print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, e))
        return 2
    print("%s %s" % (clause, line))
    return 0 if line.startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
