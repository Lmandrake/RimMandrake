#!/usr/bin/env python3
"""check_declarations.py — do the packageIds our mods NAME actually exist?

    python3 src/RimMandrake/Utils/check_declarations.py
    python3 src/RimMandrake/Utils/check_declarations.py --quiet   # exit code only

Exit 0 = every declaration resolves. 1 = at least one does not. 2 = could not tell.

WHY THIS EXISTS
===============
**RimWorld's mod surface fails SILENT by default.** A `loadAfter` naming a
packageId that does not exist is not an error, not a warning, and not a log line —
it is simply ignored, and the constraint you thought you had never existed.

Measured on 2026-08-13, in our own mods:

  Jawa_Armoury  loadAfter  guy762.starwarskotorweapons   ← does not exist
                loadAfter  Aoba.OuterRim.Core            ← different author's mod
  real ids:     guy762.kotorweapons, Neronix17.OuterRim.Core

That block had constrained nothing, for as long as it had existed. It was found by
a seat reading the file, not by any check — and it was one of **seven** silent
failures found that day: mods deployed but never enabled, `loadBottom` defeating
`loadAfter`, a weapon whose failure cannot log, an export dropping cells, floors
not surviving a mid-game spawn. **All of them looked exactly like success.**

`check_refs.py` already does this for prose — it verifies that paths named in our
documents exist. **We were mechanically checking our writing and not our code.**

WHAT IT CHECKS
==============
For every `About.xml` under `src/`, every packageId named in `loadAfter`,
`loadBefore`, `forceLoadAfter`, `forceLoadBefore`, `modDependencies` and
`incompatibleWith`:

  MISSING   named, but no mod on disk declares that packageId  → the silent killer
  INACTIVE  exists on disk but is not in ModsConfig.xml        → a no-op constraint

⚠️ **INACTIVE is a warning, not a failure.** A `loadAfter` on a mod you have not
enabled is legitimate — it is how an optional-compat declaration is written. A
MISSING one never is.

⚠️ **This checks DECLARATIONS, not ORDER.** A correct, resolvable `loadAfter` can
still be defeated at runtime by `loadBottom` in the same RimSort rule. That is a
different check and a real one: on 2026-08-13, six of our thirteen User Rules
carried both.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

FIELDS = ("loadAfter", "loadBefore", "forceLoadAfter", "forceLoadBefore",
          "modDependencies", "incompatibleWith")
MOD_ROOTS = (
    "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100",
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods",
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
)
CONFIG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios"
          "/RimWorld by Ludeon Studios/Config/ModsConfig.xml")


def repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/" and not os.path.isdir(os.path.join(d, ".git")):
        d = os.path.dirname(d)
    return d


def installed(mod_roots=None):
    """Every packageId present on disk, lowercased.

    `mod_roots` is injectable so `selftest_checkers.py` can point this at a
    fixture tree. Default is the real install — CLI behaviour is unchanged.
    """
    ids = {}
    for root in (MOD_ROOTS if mod_roots is None else mod_roots):
        for about in glob.glob(os.path.join(root, "*", "About", "About.xml")):
            # ⚠️ Parse, do NOT regex. An About.xml lists its DEPENDENCIES'
            # packageIds inside <modDependencies> before its own, so the first
            # <packageId> in the file is very often `brrainz.harmony`. A regex
            # here registers every Harmony-dependent mod under Harmony's id and
            # then reports its real id as MISSING.
            #
            # This is not hypothetical: OPS made exactly this mistake earlier on
            # 2026-08-13 and reported 3 phantom absent mods, and THIS TOOL —
            # written to catch silent errors — shipped with the same bug and
            # produced 8 false alarms on its first run. The mod's own id is the
            # DIRECT CHILD of the root element; a dependency's never is.
            try:
                node = ET.parse(about).getroot()
            except Exception:
                continue
            pid = (node.findtext("packageId") or "").strip()
            if pid:
                ids.setdefault(pid.lower(), about)
    return ids


def active(config=None):
    """Active packageIds, lowercased, or None if ModsConfig.xml is unreadable."""
    try:
        root = ET.parse(CONFIG if config is None else config).getroot()
        return {(li.text or "").strip().lower()
                for li in root.find("activeMods").findall("li")}
    except Exception:
        return None


def declared(about_path):
    """(field, packageId) pairs named by one About.xml. Never raises."""
    out = []
    try:
        root = ET.parse(about_path).getroot()
    except Exception:
        return out
    for field in FIELDS:
        for node in root.iter(field):
            for li in node.findall("li"):
                # modDependencies entries are objects carrying <packageId>
                pid = (li.findtext("packageId") or li.text or "").strip()
                if pid:
                    out.append((field, pid.lower()))
    return out


def our_abouts(src_root):
    """Every About.xml belonging to one of OUR mods, sorted."""
    return sorted(glob.glob(os.path.join(src_root, "**", "About", "About.xml"),
                            recursive=True))


def analyse(src_root, on_disk, act):
    """The whole verdict, as data. No printing, no exit codes, no globals.

    Returns (missing, inactive, checked, abouts). ⚠️ INACTIVE is deliberately
    NOT a failure — only MISSING is. See the module docstring.
    """
    missing, inactive, checked = [], [], 0
    abouts = our_abouts(src_root)
    for about in abouts:
        mod = os.path.basename(os.path.dirname(os.path.dirname(about)))
        for field, pid in declared(about):
            checked += 1
            if pid not in on_disk:
                # ⚠️ incompatibleWith is the exception: declaring incompatibility
                # with a mod you have not installed is normal and harmless. Only
                # a LOAD-ORDER or DEPENDENCY declaration that names nothing is a
                # real fault, because only those were supposed to constrain
                # something. Found by selftest_checkers.py before it ever fired.
                if field == "incompatibleWith":
                    inactive.append((mod, field, pid + "  (incompatibleWith, not installed — fine)"))
                else:
                    missing.append((mod, field, pid))
            elif act is not None and pid not in act:
                inactive.append((mod, field, pid))
    return missing, inactive, checked, abouts


def main():
    quiet = "--quiet" in sys.argv
    root = os.path.join(repo_root(), "src")
    on_disk = installed()
    if not on_disk:
        print("No mods found on disk — cannot tell.", file=sys.stderr)
        return 2
    act = active()

    missing, inactive, checked, abouts = analyse(root, on_disk, act)

    if not quiet:
        print("checked %d declarations across %d of our mods"
              % (checked, len(abouts)))
        if missing:
            print("\n🔴 MISSING — named, but NO mod on disk declares this id.")
            print("   These constrain NOTHING and never have. Nothing logs it.")
            for mod, field, pid in missing:
                print("   %-28s %-16s %s" % (mod, field, pid))
        if inactive:
            print("\n⚠️  INACTIVE — exists on disk, not enabled. A no-op today,")
            print("   legitimate if it is an optional-compat declaration.")
            for mod, field, pid in inactive:
                print("   %-28s %-16s %s" % (mod, field, pid))
        if not missing and not inactive:
            print("\n✅ every declaration resolves to an installed, active mod")
        elif not missing:
            print("\n✅ no MISSING declarations (inactive ones are warnings)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
