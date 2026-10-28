#!/usr/bin/env python3
"""Reader for testing_policy.json, the RimFlow v3 testing-policy tunables.

Design: design/RimMandrake/testing_policy_2026-10-28.md (item TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME).
Same shape as dispatcher.load_schedule: one JSON file beside this module, read whole. Every param carries
value, unit, why, provenance (O owner words / C owner card / D code default / A agent or autotuner) and signal.
`load_policy` refuses a malformed file rather than guessing, so a gate that reads it fails closed.

    python3 src/RimMandrake/rimflow/testing_policy.py            # list params: name = value [provenance]
    python3 src/RimMandrake/rimflow/testing_policy.py <name>     # one value, as JSON
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_POLICY = os.path.join(HERE, "testing_policy.json")
REQUIRED = ("value", "unit", "why", "provenance", "signal")
PROVENANCE = ("O", "C", "D", "A")
# The autotuner may write only these; O and C move on the owner's word.
TUNABLE = ("D", "A")


class PolicyError(ValueError):
    pass


def validate(pol):
    """Raise PolicyError naming every defect; return pol unchanged when it is well formed."""
    errs = []
    params = pol.get("params") if isinstance(pol, dict) else None
    if not isinstance(params, dict) or not params:
        raise PolicyError("testing policy has no params object")
    for name, p in params.items():
        if not isinstance(p, dict):
            errs.append("%s: not an object" % name)
            continue
        miss = [k for k in REQUIRED if k not in p]
        if miss:
            errs.append("%s: missing %s" % (name, ",".join(miss)))
        if p.get("provenance") not in PROVENANCE:
            errs.append("%s: provenance %r not one of %s" % (name, p.get("provenance"), "/".join(PROVENANCE)))
        for k in ("why", "signal", "unit"):
            if k in p and not (isinstance(p[k], str) and p[k].strip()):
                errs.append("%s: %s is empty" % (name, k))
    if errs:
        raise PolicyError("; ".join(errs))
    return pol


def load_policy(path=None):
    with open(path or DEFAULT_POLICY, encoding="utf-8") as f:
        return validate(json.load(f))


def param(name, policy=None, path=None):
    """The value of one param. KeyError for an unknown name: a caller never gets a silent default."""
    pol = policy if policy is not None else load_policy(path)
    if name not in pol["params"]:
        raise KeyError("testing_policy.json has no param %r" % name)
    return pol["params"][name]["value"]


def tunable(name, policy=None, path=None):
    """True when the autotuner may change this param (provenance D or A)."""
    pol = policy if policy is not None else load_policy(path)
    return pol["params"][name]["provenance"] in TUNABLE


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pol = load_policy()
    if argv:
        print(json.dumps(param(argv[0], pol)))
        return 0
    for n, p in sorted(pol["params"].items()):
        print("%s = %s [%s]" % (n, json.dumps(p["value"]), p["provenance"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
