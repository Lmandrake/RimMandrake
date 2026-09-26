#!/usr/bin/env python3
"""check_biome_present.py — is a BiomeDef actually in the LIVE loaded def set?

BIOME_LOAD_PROOF_WAVE_1's positive half. Absence of errors in Player.log is NOT
a pass: a patch that matches nothing logs nothing, and a def silently discarded
by a missing modExtension type logs nothing useful either. So each load is
settled by asking the running game whether the biome exists.

🔴 MUST run under Windows python (`python.exe`), never WSL python. RimBridge
binds Windows loopback and WSL2 is NAT-mode, so there is no route from WSL and
retrying cannot fix it — rimbridge_client.py says so itself.

Prints exactly one word on the last line, for the shell to read:
    PRESENT | ABSENT | UNMEASURED
UNMEASURED is used for every failure to ASK (no bridge, no route, tool missing,
timeout). It is never conflated with ABSENT — "we could not look" and "we looked
and it is not there" are different findings and only one of them is a defect.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv):
    if len(argv) < 2:
        print("usage: check_biome_present.py <BiomeDefName>", file=sys.stderr)
        print("UNMEASURED")
        return 2
    defname = argv[1].strip()
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
    except Exception as ex:                                   # noqa: BLE001
        print("could not import rimbridge_client: %s" % ex, file=sys.stderr)
        print("UNMEASURED")
        return 0

    try:
        host, port, token = resolve_endpoint()
    except Exception as ex:                                   # noqa: BLE001
        print("no endpoint: %s" % ex, file=sys.stderr)
        print("UNMEASURED")
        return 0

    # jawa/get_defs declares: deep, defs, fields, limit — NOT defName/defType.
    # `defs` is a STRING "DefType/DefName" (a LIST raises
    # System.InvalidCastException "Object must implement IConvertible" and comes
    # back success:False).
    try:
        with RimBridge(host=host, port=port, token=token, timeout=45.0) as br:
            res = br.call("jawa/get_defs", {"defs": "BiomeDef/%s" % defname})
    except Exception as ex:                                   # noqa: BLE001
        _err("bridge call failed: %s" % ex)
        print("UNMEASURED")
        return 0

    # 🔴 Read the tool's OWN result fields. An earlier version of this check
    # substring-matched the payload, which read a FAILED call (success:False,
    # an exception blob with no defName in it) as ABSENT — a false negative that
    # would have failed all 22 biomes while looking like a real finding.
    if not isinstance(res, dict) or not res.get("success"):
        _err("call unsuccessful: %s" % (res or {}).get("message"))
        print("UNMEASURED")
        return 0
    if defname in (res.get("notFound") or []):
        print("ABSENT")
        return 0
    for d in (res.get("defs") or []):
        if d.get("defName") == defname:
            print("PRESENT" if d.get("found") else "ABSENT")
            return 0
    if res.get("foundCount") == 0:
        print("ABSENT")
        return 0
    _err("unrecognised payload shape; refusing to guess")
    print("UNMEASURED")
    return 0


def _err(msg):
    """stderr that survives the Windows cp1252 console."""
    try:
        sys.stderr.write(str(msg).encode("ascii", "replace").decode("ascii") + "\n")
    except Exception:                                         # noqa: BLE001
        pass


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
