#!/usr/bin/env python3
"""
refresh.py — what went stale when the mod list changed, and how to fix it.

VERSION 1.0  (2026-08-11)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

THE PROBLEM THIS SOLVES
-----------------------
Every generated artefact in this project is a snapshot of ONE mod set. Add a
xenotype pack or a ship-weapons mod and they are all quietly wrong — not
missing, not erroring, just describing a game that no longer exists. Silently
stale data is worse than none, because it still answers questions.

The artefacts, and what each costs to rebuild:

  observed/2026-08-13_pre-restructure/inventory/*.csv        offline scan          seconds
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
  python src/RimMandrake/Utils/refresh.py                 # status only; changes nothing
  python src/RimMandrake/Utils/refresh.py --offline       # rebuild everything not needing a load
  python src/RimMandrake/Utils/refresh.py --patches       # regenerate + validate the patch mod
  python src/RimMandrake/Utils/refresh.py --all           # both, in the right order
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
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)

# Windows form first, WSL /mnt/c form second; whichever exists wins. This is
# the same candidate-list pattern deploy_custom_mods.py uses (its first_existing)
# and it is why THAT script has always run under both interpreters.
#
# ⚠️ WHY THIS MATTERS MORE THAN IT LOOKS. Until 2026-08-13 these were two
# hardcoded C:\ literals, so `python3 src/RimMandrake/Utils/refresh.py` under WSL died with:
#
#     cannot read ModsConfig: [Errno 2] No such file or directory: 'C:\Users\...'
#
# which names a missing FILE. Every reader hunts a deleted config; nobody
# suspects the interpreter. That single misleading message is the reason
# CLAUDE.md, TODO.md §10 and this project's habits all carried a
# "refresh.py only works under python.exe" rule that was never a real
# constraint — just an unresolved path. The general form, worth keeping:
# a wrong interpreter almost always fails by naming something ELSE as the
# cause, so "it only works under X" deserves one look at WHY before it
# becomes doctrine.
import game_paths as _GP  # per-platform game path resolution


def _first_existing(paths):
    """First path that exists, else the first candidate so the caller's own
    error message still names something concrete."""
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


_LOCALLOW_WIN = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios"
_LOCALLOW_WSL = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios"

D_CONFIG = _first_existing([
    os.path.join(_LOCALLOW_WIN, r"Config\ModsConfig.xml"),
    os.path.join(_LOCALLOW_WSL, "Config/ModsConfig.xml"),
])
D_DUMP = _first_existing([
    os.path.join(_LOCALLOW_WIN, "DefDump"),
    os.path.join(_LOCALLOW_WSL, "DefDump"),
])
INVENTORY = os.path.join(ROOT, "observed", "2026-08-13_pre-restructure",
                         "inventory")
STAMP = os.path.join(INVENTORY, "GENERATED_FROM.json")
SHEETS = os.path.join(INVENTORY, "contact_sheets")
ARMOURY = os.path.join(ROOT, "src", "Jawa", "Jawa_Armoury")


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
    # The MOD LIST alone, deliberately. ModsConfig's <version> records the build
    # that last WROTE the file; the live dump reports the build that is RUNNING.
    # After any game update those differ forever (rev590 vs rev591 here), and
    # hashing the version made a byte-identical mod set read as STALE -- which
    # would send someone on a 23-minute load for nothing. A staleness check that
    # cries wolf gets ignored, and then it protects nothing.
    blob = "\n".join(mods)
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


def write_stamp(fp, note=""):
    """
    Record WHICH mod set an artefact came from, and optionally WHY.

    The note matters more than it looks. Mods get pulled temporarily to isolate
    a bug, and an artefact regenerated during that window is accurate but
    unrepresentative — it describes a configuration nobody intends to play. Six
    months later the hash tells you the set differed; only the note tells you it
    was deliberate and temporary.
    """
    os.makedirs(INVENTORY, exist_ok=True)
    payload = {"hash": fp["hash"], "modCount": fp["modCount"],
               "version": fp["version"]}
    if note:
        payload["note"] = note
    with io.open(STAMP, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
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
    blob = "\n".join(mods)          # mod list only; see loadset_fingerprint
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
    if st and st.get("note"):
        print("  stamp note: %s" % st["note"])
    if st is None:
        rows.append(("observed/2026-08-13_pre-restructure/inventory/*.csv", "never stamped", "REBUILD", "--offline"))
    elif st.get("hash") != fp["hash"]:
        rows.append(("observed/2026-08-13_pre-restructure/inventory/*.csv",
                     "%s (%s mods)" % (st.get("hash"), st.get("modCount")),
                     "STALE", "--offline"))
    else:
        rows.append(("observed/2026-08-13_pre-restructure/inventory/*.csv", st.get("hash"), "current", "-"))

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


def do_offline(fp, note=""):
    ok = run([sys.executable, os.path.join("src", "RimMandrake", "Utils", "animal_inventory.py"),
              "--out", os.path.join("observed", "2026-08-13_pre-restructure",
                                    "inventory")], "animal inventory")
    if ok:
        run([sys.executable, os.path.join("src", "RimMandrake", "Utils", "animal_contact_sheet.py"),
             "--out", SHEETS], "contact sheets")
        write_stamp(fp, note)
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
         # ⚠️ These MUST be the per-platform forms. As C:\ literals they were
         # absent under WSL, validate_patch loaded 0 defs, skipped every live
         # xpath check, warned, and exited 0 — which this function rendered as
         # "validate (with --live) ok". 29c89f0 dual-formed D_CONFIG and D_DUMP
         # and missed exactly these three. Found by CREATE.
         "--defs", _GP.WORKSHOP,
         "--defs", _GP.LOCAL_MODS,
         "--defs", _GP.GAME_DATA,
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
    ap.add_argument("--note", default="",
                    help="record WHY this rebuild happened, e.g. 'VSIE pulled "
                         "for debugging'. Stored in GENERATED_FROM.json and "
                         "shown in status. Use it whenever the mod list is "
                         "deliberately not in its intended shape.")
    a = ap.parse_args()

    try:
        fp = loadset_fingerprint(a.config)
    except (OSError, ET.ParseError) as exc:
        sys.exit("cannot read ModsConfig: %s" % exc)

    status(fp)

    if a.all or a.offline:
        do_offline(fp, a.note)
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
