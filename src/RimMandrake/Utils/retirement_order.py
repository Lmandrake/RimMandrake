"""
Retirement ORDER — the one place that knows which donor mods must retire
no later than another mod, because an inheritance chain (ParentName/Name)
crosses between them.

DROID_RETIREMENT_ORDER_ASSERT_1: `guy762_KotORDroidBase` (kotorcore's
`_DroidsBase` folder, loaded only while guy762.KotORDroids is active) carries
`ParentName="ABF_Thing_Synstruct_HumanlikeBase"`, an ABF-owned abstract. No
patch can gate an inheritance dependency — `PatchOperationFindMod` can add or
remove nodes, it cannot make a `ParentName` resolve. If ABF/SynCore retire
before guy762.kotordroids, the parent def is discarded and takes all 12
downstream droid ThingDefs with it, with no Config error and no log line
(the same silent-loss shape already proven in WEAPONS_DONOR_RETIREMENT_1).

So the constraint lives in ONE place —
`infrastructure/state/facts/retirement_order.json` — as data, not as a
hardcoded pair of strings in a script:

    from retirement_order import check_order

    violations = check_order()               # reads the live ModsConfig.xml
    violations = check_order(active_pids={...lowercase packageIds...})

Each returned violation is a dict naming the constraint id, the dependent
mods that are active, and which required mod(s) are missing — enough to act
on without re-reading the fact file.
"""

import io
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
FACT = os.path.join(_ROOT, "infrastructure", "state", "facts",
                     "retirement_order.json")

sys.path.insert(0, _HERE)

_cache = None


def _load():
    global _cache
    if _cache is None:
        with io.open(FACT, encoding="utf-8") as fh:
            data = json.load(fh)
        _cache = list(data["order_constraints"])
    return _cache


def constraints():
    """The raw constraint rows, for reporting."""
    return list(_load())


def _active_pids_from_modsconfig(path):
    from rimworld_loadset import parse_mods_config
    active, _version = parse_mods_config(path)
    return set(active)


def check_order(active_pids=None, modsconfig_path=None):
    """
    Return a list of violation dicts, empty if every constraint holds.

    `active_pids` — an iterable of packageIds (any case) to check against,
    for a test fixture. When omitted, reads the live ModsConfig.xml (or
    `modsconfig_path` if given) via rimworld_loadset.parse_mods_config, the
    same reader every other tool in this repo uses for the live mod list.

    A violation fires when every packageId in a constraint's
    `dependent_active_all` is active AND at least one packageId in
    `requires_active_all` is absent.
    """
    if active_pids is None:
        from game_paths import MODS_CONFIG as DEFAULT_MODS_CONFIG
        path = modsconfig_path or DEFAULT_MODS_CONFIG
        active = _active_pids_from_modsconfig(path)
    else:
        active = set(str(p).strip().lower() for p in active_pids)

    violations = []
    for c in _load():
        dependent = [p.lower() for p in c["dependent_active_all"]]
        required = [p.lower() for p in c["requires_active_all"]]
        if not dependent or not all(p in active for p in dependent):
            continue
        missing = [p for p in required if p not in active]
        if missing:
            violations.append({
                "id": c["id"],
                "dependent_active": dependent,
                "missing_required": missing,
                "reason": c.get("reason", ""),
                "filed": c.get("filed", ""),
            })
    return violations


if __name__ == "__main__":
    vs = check_order()
    if not vs:
        print("retirement_order: no violations against the live ModsConfig.xml")
        sys.exit(0)
    for v in vs:
        print("VIOLATION %s: %s active with %s absent -- %s"
              % (v["id"], v["dependent_active"], v["missing_required"], v["reason"]))
    sys.exit(1)
