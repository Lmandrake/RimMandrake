"""Live proof L1 of FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE: run RM_FirefoamAimProof.ProofAim through jawa/static_call.

Exit 0 = the colonist holding RM_FE_FirefoamSprayer can target a fire and an open cell AND the vanilla-default
control refuses both; 1 = the probe answered and something differs; 2 = UNMEASURED (no bridge, no reply, the probe
REFUSED to stage, or the reply had no FIREFOAM line). Runs from WSL as `python.exe <this file>` (repo-relative).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))

WANT = ("FIREFOAM fire True | cell True | validFire True | validCell True | hitFire True | hitCell True"
        " | control fire False cell False")


def verdict(text):
    """-> (exit code, line) for the probe's returned text. Pure, so it can be checked offline."""
    for line in str(text).splitlines() + [str(text)]:
        i = line.find("FIREFOAM fire ")
        if i >= 0:
            got = line[i:].split('"')[0].strip()
            return (0 if got.startswith(WANT) else 1), got
    if "REFUSED" in str(text):
        return 2, "probe refused to stage: %s" % str(text)[:300]
    return 2, "no FIREFOAM line in the reply: %s" % str(text)[:300]


def main():
    try:
        import rimbridge_client as R
        host, port, token = R.resolve_endpoint()
        if not token:
            print("UNMEASURED: no bridge token")
            return 2
        with R.RimBridge(host, port, token, timeout=60) as rb:
            out = rb.call("jawa/static_call", {"type": "RimMandrake.Pyrelands.RM_FirefoamAimProof",
                                               "method": "ProofAim"})
    except Exception as ex:  # any transport failure means the proof could not see
        print("UNMEASURED: bridge call failed: %s" % str(ex)[:300])
        return 2
    code, line = verdict(json.dumps(out))
    print({0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code] + ": " + line)
    return code


if __name__ == "__main__":
    sys.exit(main())
