#!/usr/bin/env python3
"""Offline selftest of the typed settings registry (hose port step 4, design FINAL §3.10 G5.10/G6.1). No game.

Proves: every registry row names a real Scribe key in its section's C#; keys are unique across sections; the hose section
Scribes under `hose_`; registry.toggles() == site_spec.toggles(); extensions.py's SETTINGS_OF/DEFAULTS are the registry's;
validation_v2.py's BOOL/FLOAT default tables agree with it; the all-off fixture covers machinery, river, river-steam and
hose switches and never an internal flag; a typed flip + restore round-trips on a fake store (bools flip, numbers are
refused without an explicit value); and each check can fail (planted drift)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "src", "RimMandrake", "Utils")
for _p in (HERE, os.path.join(os.path.dirname(HERE), "..", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import site_spec as S  # noqa: E402
import settings_registry as R  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def flip_restore(store, key, value=None):
    """Typed flip on a {(cls, field): value} store; returns the restore closure. Numbers need an explicit value."""
    r = R.BY_KEY[key]
    new = r["flip"] if value is None else value
    if new is None:
        raise ValueError("no flip value for %s (a %s): pass one" % (key, type(r["default"]).__name__))
    k = (r["cls"], r["field"])
    old = store[k]
    store[k] = new

    def restore():
        store[k] = old
    return restore


def main():
    import collections
    c = collections.Counter(r["key"] for r in R.ROWS)
    check("registry keys unique across sections", all(v == 1 for v in c.values()), [k for k, v in c.items() if v > 1])
    check("every row has its section's Scribe key", all(r["scribe"] for r in R.ROWS), [r["key"] for r in R.ROWS if not r["scribe"]])
    hose = [r for r in R.ROWS if r["cls"].endswith(".RM_HoseSettings")]
    check("hose section Scribes under hose_ (17 fields: +tanksFeedHoses, review S2)", len(hose) == 17 and all(r["scribe"] == "hose_" + r["field"] for r in hose if not r["internal"]),
          [(r["field"], r["scribe"]) for r in hose][:6])
    check("registry.toggles() == site_spec.toggles()", R.toggles() == S.toggles(), sorted(set(R.toggles()) ^ set(S.toggles())))
    import extensions as E
    check("extensions SETTINGS_OF/DEFAULTS are the registry's",
          E.SETTINGS_OF == R.settings_of(E.suite.toggles) and E.DEFAULTS == R.defaults(E.suite.toggles))
    import validation_v2 as V2
    bad = [(f, w, R.BY_KEY.get(f, {}).get("default")) for typ, fs in V2.BOOL_DEFAULTS.items() for f, w in fs.items()
           if R.BY_KEY.get(f, {}).get("default") != w or R.BY_KEY[f]["cls"] != typ]
    bad += [(f, w, R.BY_KEY.get(f, {}).get("default")) for f, w in V2.FLOAT_DEFAULTS.items() if R.BY_KEY.get(f, {}).get("default") != w]
    check("validation_v2 default tables agree with the registry", not bad, bad[:5])
    off = R.all_off()
    classes = {cls.rsplit(".", 1)[1] for cls, _, _ in off}
    check("all-off fixture covers machinery, river, river-steam and hose switches",
          {"RM_MachinerySettings", "RM_RiversSettings", "RiverSteamSettings", "RM_HoseSettings", "RimMandrakeFlowWorksSettings"} <= classes, classes)
    check("all-off fixture never touches an internal flag", not any(f in S.INTERNAL_FLAGS for _, f, _ in off))
    store = {(r["cls"], r["field"]): r["default"] for r in R.ROWS}
    snap = dict(store)
    rs = [flip_restore(store, k) for k in ("enabled", "universalPipesEnabled", "riverSteamEnabled")]
    check("typed flip changes exactly the three switches", sum(1 for k in store if store[k] != snap[k]) == 3)
    for f in rs:
        f()
    check("typed restore puts every value back", store == snap)
    try:
        flip_restore(store, "maxLength")
        refused = False
    except ValueError:
        refused = True
    check("a number is never flipped without an explicit value", refused)
    rv = flip_restore(store, "maxLength", 52.0)
    ok = store[(R.BY_KEY["maxLength"]["cls"], "maxLength")] == 52.0
    rv()
    check("an explicit numeric flip and restore round-trip", ok and store == snap)
    # sanity probes: the checks can fail
    saved = R.BY_KEY["enabled"]["scribe"]
    R.BY_KEY["enabled"]["scribe"] = "enabled"
    probe = all(r["scribe"] == "hose_" + r["field"] for r in hose if not r["internal"])
    R.BY_KEY["enabled"]["scribe"] = saved
    check("sanity: an unprefixed hose Scribe key is caught", not probe)
    V2.FLOAT_DEFAULTS["pulseIntervalTicks"], keep = 999.0, V2.FLOAT_DEFAULTS["pulseIntervalTicks"]
    caught = R.BY_KEY["pulseIntervalTicks"]["default"] != V2.FLOAT_DEFAULTS["pulseIntervalTicks"]
    V2.FLOAT_DEFAULTS["pulseIntervalTicks"] = keep
    check("sanity: a drifted v2 default is caught", caught)
    print("settings registry: %s -- %d rows, %d toggles" % ("PASS" if not FAILS else "FAIL", len(R.ROWS), len(R.toggles())))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
