#!/usr/bin/env python3
"""Live proof of PUMP_ON_TANK_FIX_NO_COUPLER (clause A1): a liquid pump touching a 2x2 RM_LiquidTank on its west or east
prints a coupler ON the tank's drawn nozzle and a drop pipe from its own port to it. Drives the bridge, so run it with
Windows python on a throwaway quicktest colony on a list holding FlowWorks:

    python.exe src/RimMandrake/FlowWorks/prove_pump_tank_coupler.py [x,z]

It calls RM_LiquidJoins.ProofMachineCouplers through jawa/static_call, which spawns a tank with a pump on each side at
x,z (or the first clear 4x2 block near the map centre), regenerates each pump's SectionLayer_RM_LiquidJoins, reads what
it printed (couplers, on-port couplers, drops, the coupler's point against TankPortGeometry.PortPoint, no placeholder
art) and destroys all three. Exit 0 when the reply says ok=True, 1 when it says ok=False, 2 when no verdict came back.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

TYPE = "RimMandrake.FlowWorks.Machinery.RM_LiquidJoins"


def main(argv):
    arg = argv[1] if len(argv) > 1 else "go"
    if arg != "go" and not re.fullmatch(r"\d+,\d+", arg):
        print("usage: prove_pump_tank_coupler.py [x,z]", file=sys.stderr)
        return 2
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    # jawa/static_call binds a one-string method; "go" is not x,z, so the method searches for a clear block itself
    r = c.call("jawa/static_call", {"type": TYPE, "method": "ProofMachineCouplers", "args": arg}, check=False)
    text = str(r.get("result") if isinstance(r, dict) else r)
    print(text)
    if not text.startswith("COUPLERS "):
        return 2
    return 0 if text.startswith("COUPLERS ok=True ") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
