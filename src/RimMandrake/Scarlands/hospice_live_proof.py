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

A2 is the STANDALONE wake (criterion A2: a colony mech needing no mechanitor). On a load where the RUT campaign swap is
live (spec 7: UtinniPatches with a mod named Droidworks adds RM_HospiceWakeExtension.wakeKinds to RM_HospiceCradle),
the cradle wakes a Droidworks droid by design, so the clause cannot be judged there: before the hook writes anything,
jawa/get_def reads the cradle's modExtensions, and a live swap ends on a `reload needed:` line (exit 2; the game phase
restages, as live_site.py --without does). An unreadable def is exit 2, never "no swap". A PASS must also name
RM_AncientServitor as the woken kind, and an unchecked haul offer (no colonist) is exit 2: the clause was not measured.
"""
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

TYPE = "RimMandrake.Scarlands.RM_HospiceProof"
METHOD = {"A1": "Rings", "A2": "Revival", "A3": "Failure"}
ADVANCE_STEP, ADVANCE_MAX = 2500, 12
CRADLE, SWAP_EXT, SERVITOR = "RM_HospiceCradle", "RM_HospiceWakeExtension", "RM_AncientServitor"
SWAP_PKG = "mandrake.rsw.droidworks"
RELOAD = ("reload needed: restart on a list (all five DLC) that lacks %s: the RUT campaign swap (%s on %s) is live on "
          "this load, so the cradle wakes a Droidworks droid by design and A2's standalone %s wake cannot be judged here"
          % (SWAP_PKG, SWAP_EXT, CRADLE, SERVITOR))
WOKE = re.compile(r" woke as (\S+), colony mech")


class Blind(Exception):
    """The instrument could not see: exit 2, never a verdict."""


def swap_live(c):
    """-> True when RM_HospiceCradle carries RM_HospiceWakeExtension on the RUNNING load. Raises Blind when the def
    cannot be read (a missing key is never read as 'no swap')."""
    r = c.call("jawa/get_def", {"defName": CRADLE, "defType": "ThingDef"})
    if not isinstance(r, dict) or not r.get("success"):
        raise Blind("get_def %s refused: %r" % (CRADLE, r))
    extra = r.get("extra")
    if not isinstance(extra, dict) or not extra.get("thingClass"):
        raise Blind("get_def %s carries no ThingDef extra block: %r" % (CRADLE, str(r)[:200]))
    exts = extra.get("modExtensions") or []
    if not isinstance(exts, list):
        raise Blind("get_def %s modExtensions is not a list: %r" % (CRADLE, exts))
    return SWAP_EXT in exts


def judge_revival(line):
    """The Revival hook's line -> (exit, line) with the driver's own A2 checks on top of the hook's."""
    if not line.startswith("PASS"):
        return 1, line
    m = WOKE.search(line)
    if not m:
        return 1, "FAIL the PASS line names no woken kind: " + line
    if m.group(1) != SERVITOR:
        return 1, "FAIL woke as %s, not %s, on a load with no campaign swap: %s" % (m.group(1), SERVITOR, line)
    if not line.startswith("PASS haul offered;"):
        return 2, "UNMEASURED the RM_HospiceHaul offer was not checked (no free colonist on the map): " + line
    return 0, line


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
        if clause == "A2":
            if swap_live(c):
                print(RELOAD)
                return 2
            code, line = judge_revival(hook(c, METHOD[clause]))
            if code == 2:
                print("A2 " + line)
                return 2
        elif clause in METHOD:
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
    except Blind as e:
        print("%s UNMEASURED: %s" % (clause, e))
        return 2
    except Exception as e:  # noqa: BLE001 -- any bridge failure is an instrument error, never a verdict
        print("%s UNMEASURED: %s: %s" % (clause, type(e).__name__, e))
        return 2
    print("%s %s" % (clause, line))
    if clause == "A2":
        return code
    return 0 if line.startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
