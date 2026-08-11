#!/usr/bin/env python3
"""
refresh.py — what went stale when the mod list changed, and how to fix it.

VERSION 1.0  (2026-08-11)   Project: G:/My Drive/Personal/Rimworld/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

THE PROBLEM THIS SOLVES
-----------------------
Every generated artefact in this project is a snapshot of ONE mod set. Add a
xenotype pack or a ship-weapons mod and they are all quietly wrong — not
missing, not erroring, just describing a game that no longer exists. Silently
stale data is worse than none, because it still answers questions.

The artefacts, and what each costs to rebuild:

  mods/inventory/*.csv        offline scan          seconds
  contact_sheets/             offline + Pillow      seconds
  DefDump/ (the live dump)    A FULL GAME LOAD      ~23 minutes
  Jawa_Armoury/Patches/*.xml  reads the live dump   seconds, but needs a
                                                    CURRENT dump to be right
  def_diff outputs            needs both            seconds

Only one of those is expensive, and three of the others depend on it. So the
useful thing a tool can do is tell you **whether you need to pay for a game
load**, and do everything that does not.

THE DEPENDENCY ORDER (do not shuffle it)
  1. ModsConfig.xml changes                    <- the root of all staleness
  2. offline scan          (no game needed)
  3. live dump             (GAME LOAD; arm DefDump/dump_request.txt first)
  4. generated patches     (read the live dump)
  5. validation            (--live wants the dump too)
  6. def_diff              (wants both)

Step 4 matters more than it looks: the armoury generator reads CURRENT damage
values out of the dump. Run it against a stale dump and it will retune weapons
using numbers from a mod set you no longer have.

USAGE
  python Utils/refresh.py                 # status only; changes nothing
  python Utils/refresh.py --offline       # rebuild everything not needing a load
  python Utils/refresh.py --patches       # regenerate + validate the patch mod
  python Utils/refresh.py --all           # both, in the right order
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

D_CONFIG = (r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
            r"\RimWorld by Ludeon Studios\Config\ModsConfig.xml")
D_DUMP = (r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios"
          r"\RimWorld by Ludeon Studios\DefDump")
INVENTORY = os.path.join(ROOT, "mods", "inventory")
STAMP = os.path.join(INVENTORY, "GENERATED_FROM.json")
SHEETS = os.path.join(INVENTORY, "contact_sheets")
ARMOURY = os.path.join(ROOT, "custom_patches", "Jawa_Armoury")


# ---------------------------------------------------------------- fingerprint
def loadset_fingerprint(config=D_CONFIG):
    """
    A stable identity for 'which mods are active, in what order'.

    Order is included deliberately: RimWorld resolves def overrides by load
    order, so the same mods in a different order really is a different game.
    """
    root = ET.parse(config).getroot()
    mods = [(li.text or "").strip().lower()
            for li in root.find("activeMods").findall("li")]
    version = (root.findtext("version") or "").strip()
    blob = version + "\n" + "\n".join(mods)
    return {
        "hash": hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16],
        "modCount": len(mods),
        "version": version,
        "mods": mods,
    }


def read_stamp():
    if not os.path.isfile(STAMP):
        return None
    try:
        with io.open(STAMP, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def write_stamp(fp):
    os.makedirs(INVENTORY, exist_ok=True)
    with io.open(STAMP, "w", encoding="utf-8") as fh:
        json.dump({"hash": fp["hash"], "modCount": fp["modCount"],
                   "version": fp["version"]}, fh, indent=2)
        fh.write("\n")


def dump_fingerprint(dump=D_DUMP):
    """The mod set the live dump was taken from, read from its manifest."""
    man = os.path.join(dump, "manifest.json")
    if not os.path.isfile(man):
        return None
    try:
        with io.open(man, encoding="utf-8") as fh:
            m = json.load(fh)
    except (OSError, ValueError):
        return None
    mods = [(x.get("packageId") or "").strip().lower()
            for x in (m.get("mods") or [])]
    blob = (m.get("gameVersion") or "") + "\n" + "\n".join(mods)
    return {"hash": hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16],
            "modCount": m.get("modCount"), "capturedUtc": m.get("capturedUtc"),
            "mods": mods}


def compare(current, other):
    """Human-readable delta between two mod lists."""
    if other is None:
        return None, None
    a, b = set(current["mods"]), set(other["mods"])
    return sorted(a - b), sorted(b - a)


# ---------------------------------------------------------------- status
def status(fp):
    print("\n=== CURRENT LOAD SET ===")
    print("  RimWorld %s | %d active mods | fingerprint %s"
          % (fp["version"], fp["modCount"], fp["hash"]))

    rows = []

    st = read_stamp()
    if st is None:
        rows.append(("mods/inventory/*.csv", "never stamped", "REBUILD", "--offline"))
    elif st.get("hash") != fp["hash"]:
        rows.append(("mods/inventory/*.csv",
                     "%s (%s mods)" % (st.get("hash"), st.get("modCount")),
                     "STALE", "--offline"))
    else:
        rows.append(("mods/inventory/*.csv", st.get("hash"), "current", "-"))

    sheets_ok = os.path.isdir(SHEETS) and any(
        f.endswith(".png") for f in os.listdir(SHEETS)) if os.path.isdir(SHEETS) else False
    rows.append(("contact_sheets/", "-" if sheets_ok else "missing",
                 "current" if (sheets_ok and st and st.get("hash") == fp["hash"])
                 else "STALE", "--offline"))

    dfp = dump_fingerprint()
    if dfp is None:
        rows.append(("DefDump/ (live)", "absent", "MISSING", "GAME LOAD"))
    elif dfp["hash"] != fp["hash"]:
        rows.append(("DefDump/ (live)",
                     "%s (%s mods, %s)" % (dfp["hash"], dfp["modCount"],
                                           dfp.get("capturedUtc", "?")),
                     "STALE", "GAME LOAD"))
    else:
        rows.append(("DefDump/ (live)", dfp["hash"], "current", "-"))

    patch_dir = os.path.join(ARMOURY, "Patches")
    have_patches = os.path.isdir(patch_dir) and any(
        f.endswith(".xml") for f in os.listdir(patch_dir))
    patch_state = ("current" if (have_patches and dfp and dfp["hash"] == fp["hash"])
                   else "STALE" if have_patches else "missing")
    rows.append(("Jawa_Armoury/Patches", "-" if have_patches else "missing",
                 patch_state, "--patches (needs a current dump)"))

    print("\n=== ARTEFACTS ===")
    print("  %-26s %-34s %-9s %s" % ("artefact", "generated from", "state", "refresh with"))
    for name, src, state, how in rows:
        print("  %-26s %-34s %-9s %s" % (name, str(src)[:34], state, how))

    added, removed = compare(fp, dfp)
    if added or removed:
        print("\n=== MOD CHANGES SINCE THE LIVE DUMP ===")
        for p in (added or [])[:12]:
            print("   + %s" % p)
        for p in (removed or [])[:12]:
            print("   - %s" % p)
        extra = len(added or []) + len(removed or []) - 24
        if extra > 0:
            print("   ... and %d more" % extra)

    needs_load = any(r[2] in ("STALE", "MISSING") and r[3] == "GAME LOAD" for r in rows)
    print("\n=== VERDICT ===")
    if needs_load:
        print("  A GAME LOAD IS REQUIRED to refresh the live dump (~23 min).")
        print("  Arm it first:")
        print("     echo all > \"%s\"" % os.path.join(D_DUMP, "dump_request.txt"))
        print("  Then load to the main menu; it writes at startup, no world needed.")
        print("  Everything else can be rebuilt now with --offline.")
    elif any(r[2] == "STALE" for r in rows):
        print("  Offline artefacts are stale. Run --all; no game load needed.")
    else:
        print("  Everything is current.")
    return rows


# ---------------------------------------------------------------- actions
def run(cmd, label):
    print("\n--- %s" % label)
    rc = subprocess.call(cmd, cwd=ROOT)
    print("    %s (exit %d)" % ("ok" if rc == 0 else "FAILED", rc))
    return rc == 0


def do_offline(fp):
    ok = run([sys.executable, os.path.join("Utils", "animal_inventory.py"),
              "--out", os.path.join("mods", "inventory")], "animal inventory")
    if ok:
        run([sys.executable, os.path.join("Utils", "animal_contact_sheet.py"),
             "--out", SHEETS], "contact sheets")
        write_stamp(fp)
        print("    stamped %s" % STAMP)
    return ok


def do_patches():
    src = os.path.join(ARMOURY, "Source")
    ok = run([sys.executable, os.path.join(src, "gen_armoury_patch.py")],
             "armoury patch")
    ok = run([sys.executable, os.path.join(src, "gen_torpedo_speed.py")],
             "torpedo speed") and ok
    run([sys.executable,
         os.path.join("skills", "rimworld-modding", "scripts", "validate_patch.py"),
         os.path.join(ARMOURY, "Patches"),
         "--defs", r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
         "--defs", r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods",
         "--defs", r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data",
         "--live", D_DUMP, "--quiet"], "validate (with --live)")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("USAGE")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=D_CONFIG)
    ap.add_argument("--offline", action="store_true",
                    help="rebuild everything that does not need a game load")
    ap.add_argument("--patches", action="store_true",
                    help="regenerate and validate the armoury patches")
    ap.add_argument("--all", action="store_true", help="--offline then --patches")
    a = ap.parse_args()

    try:
        fp = loadset_fingerprint(a.config)
    except (OSError, ET.ParseError) as exc:
        sys.exit("cannot read ModsConfig: %s" % exc)

    status(fp)

    if a.all or a.offline:
        do_offline(fp)
    if a.all or a.patches:
        dfp = dump_fingerprint()
        if dfp is None or dfp["hash"] != fp["hash"]:
            print("\n!! REFUSING to regenerate patches: the live dump is stale or")
            print("   absent, and the generator reads CURRENT damage values from")
            print("   it. Retuning against a dump of a different mod set would")
            print("   bake in numbers from a game you no longer have.")
            print("   Take a fresh dump first, or pass --patches again once done.")
        else:
            do_patches()

    if a.all or a.offline or a.patches:
        print()
        status(fp)


if __name__ == "__main__":
    main()
