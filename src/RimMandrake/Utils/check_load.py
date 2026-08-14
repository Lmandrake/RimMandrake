#!/usr/bin/env python3
"""check_load.py — did the game load the mods we asked for, in the order we asked?

    python3 src/RimMandrake/Utils/check_load.py          # human
    python3 src/RimMandrake/Utils/check_load.py --quiet  # exit code only

Exit 0 = the load matches the request exactly. Exit 1 = it does not. Exit 2 =
could not tell (a missing file is NOT a pass).

WHY THIS IS MECHANICAL AND NOT A JUDGEMENT
==========================================
"Did the load take?" has been answered all day by reading a log and forming an
opinion. It is a set comparison, so it should be a command.

⚠️ **`Player.log` cannot answer this and never could.** Measured 2026-08-13 on a
580-mod load: the log carries **44 `Mod ` lines naming 6 distinct mods**, and they
appear only when a mod has a *problem* — a missing `downloadUrl`, an unsatisfied
dependency. Roughly 1% coverage, biased entirely toward the broken. A clean log is
compatible with a mod silently not loading, which is this project's most expensive
recurring failure shape.

THE TWO SOURCES, AND WHY THE SECOND ONE IS THE GOOD ONE
=======================================================
  request  Config/ModsConfig.xml  <activeMods>   — what we ASKED for
  reality  DefDump/manifest.json  mods[]         — what the game HAS

`manifest.json` is written by our own RimDefDump mod during the load, enumerating
the mod set from inside the running game. **That makes it runtime evidence, not
disk evidence** — the distinction that cost two wrong rulings on 2026-08-13, when
a def dump captured *before* BTD Xenotype Remix's load-time dedup was read as
though it described the running game.

⚠️ **A stale manifest silently answers about a previous load.** It is compared
against `ModsConfig.xml`'s mtime and flagged, because "580 == 580" from yesterday
is the most convincing wrong answer this script could give.

ORDER MATTERS, NOT JUST MEMBERSHIP
==================================
RimWorld resolves def overrides by load order, so the same mods in a different
order really is a different game. Set equality is not enough and this checks the
sequence.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

LOW = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios"
       "/RimWorld by Ludeon Studios")
CONFIG = os.path.join(LOW, "Config", "ModsConfig.xml")
MANIFEST = os.path.join(LOW, "DefDump", "manifest.json")


def requested(path):
    """Active packageIds in load order, lowercased.

    ⚠️ Only `<activeMods>`. A bare `grep -c '<li>'` also catches
    `<knownExpansions>` and reads 585 against a real 580 — the exact miscount
    this project has made twice.
    """
    root = ET.parse(path).getroot()
    return [(li.text or "").strip().lower()
            for li in root.find("activeMods").findall("li")]


def loaded(path):
    with open(path, encoding="utf-8-sig") as fh:
        man = json.load(fh)
    mods = man.get("mods", [])
    return ([(m.get("packageId") or "").strip().lower() for m in mods],
            man.get("gameVersion"), man.get("capturedUtc"))


def evaluate(config=None, manifest=None):
    """The whole verdict, as data. No printing, no exit codes, no globals.

    Paths are injectable so `selftest_checkers.py` can drive this against
    fixtures; the defaults are the real game files, so the CLI is unchanged.
    Returns a dict; `absent` names a required file that does not exist, in
    which case the caller must report 2 — a missing file is NOT a pass.
    """
    config = CONFIG if config is None else config
    manifest = MANIFEST if manifest is None else manifest
    for p in (config, manifest):
        if not os.path.isfile(p):
            return {"absent": p}

    want = requested(config)
    got, version, captured = loaded(manifest)
    want_set, got_set = set(want), set(got)
    missing = [p for p in want if p not in got_set]
    extra = [p for p in got if p not in want_set]
    ordered = want == got

    # A manifest older than the request describes a DIFFERENT load.
    stale = os.path.getmtime(manifest) < os.path.getmtime(config)

    return {"absent": None, "want": want, "got": got, "missing": missing,
            "extra": extra, "ordered": ordered, "stale": stale,
            "version": version, "captured": captured,
            "ok": not missing and not extra and ordered and not stale}


def main():
    quiet = "--quiet" in sys.argv
    r = evaluate()
    if r["absent"]:
        print("MISSING: %s" % r["absent"], file=sys.stderr)
        print("Cannot tell. A missing file is not a pass.", file=sys.stderr)
        return 2

    want, got = r["want"], r["got"]
    missing, extra = r["missing"], r["extra"]
    ordered, stale, ok = r["ordered"], r["stale"], r["ok"]
    version, captured = r["version"], r["captured"]

    if quiet:
        return 0 if ok else 1

    print("requested (ModsConfig)  %d" % len(want))
    print("loaded    (DefDump)     %d   %s  captured %s"
          % (len(got), version or "?", captured or "?"))
    print("requested but NOT loaded  %d %s"
          % (len(missing), missing[:8] if missing else ""))
    print("loaded but NOT requested  %d %s"
          % (len(extra), extra[:8] if extra else ""))
    print("order identical           %s" % ordered)

    if stale:
        print("\n⚠️  STALE: the manifest predates ModsConfig.xml, so it describes a")
        print("    PREVIOUS load. Everything above may be a confident wrong answer.")
        print("    Re-run after a load that postdates your last mod-list edit.")
    if not ordered and not missing and not extra:
        print("\n⚠️  Same mods, DIFFERENT ORDER. RimWorld resolves def overrides by")
        print("    load order, so this is a different game, not a cosmetic diff.")
    print("\n%s" % ("✅ LOAD MATCHES THE REQUEST" if ok else "❌ LOAD DOES NOT MATCH"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
