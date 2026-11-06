#!/usr/bin/env python3
"""Mod lists must spell every packageId lowercase (MINIMALLIST_FIX_OUTERRIMCORE_CTOR_NRE).

RimWorld 1.6 fills ModsConfig.activeModsHashSet with ModsConfig.xml's raw strings, while IsActive() lowercases its
query. A capitalised entry therefore loads its mod and still reads inactive: Outer Rim Core's constructor
(GetActiveModWithIdentifier, DevMode only) got null and threw a NullReferenceException in get_VersionDir, and every
MayRequire on such an id reads false. The writing doors lowercase (zoom_guard.lower_text); this checks the results.

    modlist_case.py stored   every stored list in infrastructure/state/modlists is lowercase      exit 0 / 1
    modlist_case.py live     the live ModsConfig.xml is lowercase                                exit 0 / 1
    modlist_case.py log      the last Player.log loaded Outer Rim Core with no get_VersionDir NRE  exit 0 / 1,
                             2 when that log never loaded the mod (it measured nothing)
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zoom_guard  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
STORE = os.path.join(REPO, "infrastructure", "state", "modlists")
BANNER = ":: Outer Rim - Core ::"
NRE = "OuterRimCoreMod.get_VersionDir"


def bad_ids(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return zoom_guard.mixed_case(zoom_guard.active_ids(f.read()))


def stored(store=STORE):
    paths = sorted(glob.glob(os.path.join(store, "*.xml")))
    bad = {p: b for p in paths for b in [bad_ids(p)] if b}
    for p, b in bad.items():
        print("MIXED CASE %s: %s" % (os.path.basename(p), ", ".join(b)))
    print("%d stored lists read, %d with capitals" % (len(paths), len(bad)))
    return 1 if bad or not paths else 0


def live():
    from game_paths import MODS_CONFIG
    b = bad_ids(MODS_CONFIG)
    print("live ModsConfig.xml: " + ("capitals in %s" % ", ".join(b) if b else "lowercase"))
    return 1 if b else 0


def log(path=None):
    if path is None:
        from game_paths import PLAYER_LOG as path
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    if BANNER not in text:
        print("UNMEASURED: %s never loaded Outer Rim Core" % path)
        return 2
    if NRE in text:
        print("FAIL: %s still throws in %s" % (path, NRE))
        return 1
    print("PASS: Outer Rim Core constructed with no %s exception" % NRE)
    return 0


if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    if verb == "stored":
        sys.exit(stored())
    if verb == "live":
        sys.exit(live())
    if verb == "log":
        sys.exit(log(sys.argv[2] if len(sys.argv) > 2 else None))
    sys.exit(__doc__)
