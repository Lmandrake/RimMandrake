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

  observed/2026-08-13/inventory/*.csv        offline scan          seconds
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
import rimworld_loadset as _RL  # packageId -> folder, so "listed" can be checked


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
INVENTORY = os.path.join(ROOT, "observed", "2026-08-13",
                         "inventory")
STAMP = os.path.join(INVENTORY, "GENERATED_FROM.json")
SHEETS = os.path.join(INVENTORY, "contact_sheets")
ARMOURY = os.path.join(ROOT, "src", "Jawa", "Jawa_Armoury")

# The three roots a mod folder can actually live under. A packageId that
# resolves to none of them is LISTED BUT NOT INSTALLED.
MOD_ROOTS = [_GP.WORKSHOP, _GP.LOCAL_MODS, _GP.GAME_DATA]


def _has_files(dirpath, suffix):
    """
    True when dirpath exists AND holds at least one file with that suffix.

    ⚠️ Existence of the ARTEFACT, never of a proxy for it. A stamp file, a
    manifest and an mtime all survive the thing they describe being deleted,
    so comparing only the proxy reports 'current' for an artefact that is not
    on disk — the worst answer this script can give, because it stops the
    reader looking.
    """
    try:
        return any(f.lower().endswith(suffix) for f in os.listdir(dirpath))
    except OSError:
        return False


# ---------------------------------------------------------------- fingerprint
class LoadsetUnmeasurable(RuntimeError):
    """The listed-vs-installed comparison could not be PERFORMED.

    Deliberately distinct from "performed, and nothing was missing". Both used
    to arrive as the same cheerful `missing: []`, and that is the failure this
    class exists to make impossible: an ABSENT input reported as an EMPTY one.

    Subclasses RuntimeError so callers that already catch RuntimeError (main()
    below, and anything scripting this) keep working unchanged.
    """


def _survey_roots(roots):
    """
    (readable, unreadable) for the mod roots, deciding it by ENUMERATION.

    ⚠️ `os.path.isdir()` is not the test. A root can pass isdir and still fail
    to list — a permission error, a dead symlink, an unmounted /mnt/c after a
    WSL restart — and `discover_mods` swallows exactly that with `except
    OSError: pass`. So the probe here is the same call the indexer makes.

    Anything that cannot be enumerated is returned as unreadable with a reason,
    and the caller must treat that as terminal. Skipping it instead produces the
    signature bug: every mod that lived under the vanished root reads as
    'listed but not installed', or — if it was the last root — the whole answer
    collapses to a confident, wrong zero.
    """
    readable, unreadable = [], []
    for r in roots:
        if not r:
            unreadable.append(("<empty path>", "no path configured"))
            continue
        try:
            os.listdir(r)
        except OSError as exc:
            why = "does not exist" if not os.path.exists(r) else str(exc)
            if "\\" in r and os.sep == "/":
                why += ("; this is a Windows-form path under Linux, so "
                        "game_paths found NEITHER candidate for this root")
            unreadable.append((r, why))
            continue
        readable.append(r)
    return readable, unreadable


def loadset_fingerprint(config=D_CONFIG, roots=None):
    """
    A stable identity for 'which mods are active, in what order'.

    Order is included deliberately: RimWorld resolves def overrides by load
    order, so the same mods in a different order really is a different game.

    ⚠️ LISTED IS NOT INSTALLED, and this used to compare listed against
    listed. `ModsConfig.xml` is a wish list: a packageId stays in it after the
    folder is unsubscribed, renamed or deleted, and the game simply drops it.
    Hashing the listed set therefore produced an identity for a load set that
    cannot exist — and a missing mod, which is a BROKEN INSTALL wanting a
    re-subscribe, was folded in silently and then surfaced later as "STALE
    dump, take a 23-minute game load", which is the wrong remedy entirely.

    So the hash is over the mods that RESOLVE TO A FOLDER, which is what the
    game will build and what the live dump's manifest records. With nothing
    missing this is byte-identical to the old hash, so no existing stamp is
    invalidated; it only diverges when there is a real defect to report, and
    the caller gets the offenders in ["missing"] to print loudly.

    🔴 UNMEASURABLE IS NOT ZERO. If any root cannot be enumerated this raises
    LoadsetUnmeasurable rather than carrying on with the roots that worked.
    "Workshop tree gone, so 1,246 mods are missing" and "workshop tree fine,
    nothing missing" are answers a caller cannot tell apart once one has been
    quietly downgraded into the other, and only one of them is safe to act on.
    """
    root = ET.parse(config).getroot()
    listed = [(li.text or "").strip().lower()
              for li in root.find("activeMods").findall("li")]
    version = (root.findtext("version") or "").strip()

    want = list(MOD_ROOTS if roots is None else roots)
    ok_roots, bad_roots = _survey_roots(want)
    if bad_roots:
        raise LoadsetUnmeasurable(
            "%d of %d mod roots could not be read, so 'is this mod installed' "
            "was NOT answered for any of them. This is not 'nothing is "
            "missing' — it is 'unmeasurable'. Fix the root, then re-run.\n"
            % (len(bad_roots), len(want))
            + "\n".join("    UNREADABLE  %s  (%s)" % (r, why)
                        for r, why in bad_roots)
            + ("\n" if ok_roots else "")
            + "\n".join("    ok          %s" % r for r in ok_roots))

    index = _RL.discover_mods(ok_roots)
    if not index:
        # Every root enumerated cleanly and still not one About.xml turned up.
        # That is measurable and absurd, so it is still terminal — but it is a
        # DIFFERENT fault from an unreadable root and says so.
        raise LoadsetUnmeasurable(
            "every mod root read cleanly yet contained no mod with an "
            "About/About.xml, so 'is this mod present' could not be answered "
            "for any listed mod. Roots read:\n    " + "\n    ".join(ok_roots))
    counts = {r: 0 for r in ok_roots}
    for info in index.values():
        counts[info["root"]] = counts.get(info["root"], 0) + 1
    missing = [p for p in listed if p not in index]
    mods = [p for p in listed if p in index]
    # The MOD LIST alone, deliberately. ModsConfig's <version> records the build
    # that last WROTE the file; the live dump reports the build that is RUNNING.
    # After any game update those differ forever (rev590 vs rev591 here), and
    # hashing the version made a byte-identical mod set read as STALE -- which
    # would send someone on a 23-minute load for nothing. A staleness check that
    # cries wolf gets ignored, and then it protects nothing.
    blob = "\n".join(mods)
    return {
        "hash": hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16],
        "modCount": len(mods),          # present on disk, not merely listed
        "listedCount": len(listed),
        "missing": missing,
        "version": version,
        "mods": mods,
        # Provenance for the comparison itself, so "0 missing" can be audited
        # rather than trusted: which roots were read, and how many installed
        # mods each contributed. A root sitting at 0 is the tell that it exists
        # but is not the tree you thought it was.
        "roots": list(ok_roots),
        "rootCounts": counts,
        "installedCount": len(index),
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
    """
    The mod set the live dump was taken from, read from its manifest.

    ⚠️ The manifest is a 1-file PROXY for a multi-gigabyte artefact, and it
    outlives it: clear or move `defs/` and manifest.json still sits there
    reporting a matching mod set, which read as "DefDump/ (live) current" and
    told the reader they had a dump to validate against when they had none.
    So the BODY is a precondition — no defs/*.json, no fingerprint.
    """
    man = os.path.join(dump, "manifest.json")
    if not os.path.isfile(man):
        return None
    if not _has_files(os.path.join(dump, "defs"), ".json"):
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


# ---------------------------------------------------------------- frozen dumps
#
# 🔴 A MOD-COUNT MISMATCH IS NOT STALENESS FOR A FROZEN DUMP — owner's ruling.
#
# This file's entire job is flagging artefacts stale when the mod list changes, and
# that is right for everything DERIVED from the live game. It is wrong for one thing:
# the OFFICIAL dump, which is the DESIGN TARGET. DECIDE and BUILD author against it.
#
# ⚠️ Our own small custom mods change the count constantly — every new Jawa_* mod moves
# it by one. If that read as STALE, the official dump would be permanently red and
# someone would eventually re-freeze it to clear the warning, silently moving the
# target everyone is building toward. **A mismatch, greater OR lesser, is expected.**
#
# ⛔ Only the OWNER re-freezes, deliberately. Nothing here does it automatically, and
# `--freeze` refuses without an explicit `--by owner`.
#
# The registry is `infrastructure/state/dumps/REGISTRY.jsonl`, append-only, one JSON
# object per line:
#   {"id":"OFFICIAL-2026-08-21","kind":"official","frozen":true,"modlist_count":578,
#    "modlist_sha":"…","path":"observed/inventory/DefDump_OFFICIAL/","by":"owner",
#    "note":"the design target — build to this"}
#
# 🔑 `kind` answers two DIFFERENT questions and they must not be conflated:
#   official     — "what should I design against?"    frozen, immune to drift
#   verification — "does the live game match?"        never frozen, staleness applies
# ---------------------------------------------------------------------------
def _registry_path():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
        os.path.dirname(os.path.dirname(here)))
    return os.path.join(root, "infrastructure", "state", "dumps", "REGISTRY.jsonl")


def registry():
    """-> [entry] newest last. [] when absent, which is not an error."""
    out = []
    try:
        with open(_registry_path(), encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    # ⚠️ Reported, never skipped. A registry that quietly drops a line
                    # would let a frozen dump lose its immunity without anyone knowing,
                    # and the symptom — "the official dump went STALE" — points nowhere
                    # near the cause.
                    print("!! REGISTRY.jsonl line %d is not valid JSON; it is being "
                          "ignored and that may make a frozen dump read STALE." % i)
    except OSError:
        pass
    return out


def frozen_entry(path):
    """-> the newest frozen registry entry describing `path`, or None."""
    want = os.path.normpath(str(path)).replace("\\", "/").rstrip("/")
    hit = None
    for e in registry():
        if not e.get("frozen"):
            continue
        p = os.path.normpath(str(e.get("path", ""))).replace("\\", "/").rstrip("/")
        if p and (want.endswith(p) or p.endswith(want)):
            hit = e
    return hit


# ---------------------------------------------------------------- status
def status_only_fingerprint(fp):
    """Just the listed-vs-installed answer. No artefacts, no dump, no load."""
    print("=== LISTED (ModsConfig.xml) vs INSTALLED (on disk) ===")
    print("  RimWorld %s | fingerprint %s" % (fp["version"], fp["hash"]))
    for r, n in fp["rootCounts"].items():
        print("  root  %5d mods  %s" % (n, r))
    print("  listed active : %d" % fp["listedCount"])
    print("  resolved      : %d" % fp["modCount"])
    print("  MISSING       : %d" % len(fp["missing"]))
    for p in fp["missing"]:
        print("     ? %s" % p)


def status(fp, steps_failed=False):
    print("\n=== CURRENT LOAD SET ===")
    print("  RimWorld %s | %d active mods | fingerprint %s"
          % (fp["version"], fp["modCount"], fp["hash"]))
    if fp.get("rootCounts"):
        def _label(r):
            b = os.path.basename(r.rstrip("/\\"))
            return "Workshop" if b.isdigit() else (b or r)
        print("  listed %d, resolved %d against %d installed mods in %s"
              % (fp["listedCount"], fp["modCount"], fp.get("installedCount", 0),
                 " + ".join("%d %s" % (n, _label(r))
                            for r, n in fp["rootCounts"].items())))
        # A root that read cleanly and held nothing is not an error, but it is
        # the shape an absent root would have if the guard above ever slipped.
        for r, n in fp["rootCounts"].items():
            if n == 0:
                print("  ?? mod root read OK but contains no mods: %s" % r)

    # Loud, and above the artefact table: a mod in ModsConfig.xml with no
    # folder is a broken install, and no amount of regenerating fixes it.
    if fp.get("missing"):
        print("\n!! %d of %d LISTED MODS ARE NOT INSTALLED — ModsConfig.xml names"
              % (len(fp["missing"]), fp["listedCount"]))
        print("   them, no folder exists under Workshop, Mods/ or Data/, and the")
        print("   game will silently drop them. The fingerprint above is over the")
        print("   %d that DO exist; re-subscribe or remove the entries." % fp["modCount"])
        for p in fp["missing"][:12]:
            print("     ? %s" % p)
        if len(fp["missing"]) > 12:
            print("     ... and %d more" % (len(fp["missing"]) - 12))

    rows = []

    st = read_stamp()
    if st and st.get("note"):
        print("  stamp note: %s" % st["note"])
    have_csv = _has_files(INVENTORY, ".csv")
    if not have_csv:
        # The stamp can match perfectly while the CSVs it describes are gone.
        rows.append(("observed/2026-08-13/inventory/*.csv",
                     "no .csv on disk" if st is None
                     else "stamped %s, but no .csv" % st.get("hash"),
                     "MISSING", "--offline"))
    elif st is None:
        rows.append(("observed/2026-08-13/inventory/*.csv", "never stamped", "REBUILD", "--offline"))
    elif st.get("hash") != fp["hash"]:
        rows.append(("observed/2026-08-13/inventory/*.csv",
                     "%s (%s mods)" % (st.get("hash"), st.get("modCount")),
                     "STALE", "--offline"))
    else:
        rows.append(("observed/2026-08-13/inventory/*.csv", st.get("hash"), "current", "-"))

    sheets_ok = _has_files(SHEETS, ".png")
    rows.append(("contact_sheets/", "-" if sheets_ok else "no .png on disk",
                 "current" if (sheets_ok and st and st.get("hash") == fp["hash"])
                 else "STALE" if sheets_ok else "MISSING", "--offline"))

    dfp = dump_fingerprint()
    if dfp is None:
        # Name WHICH half is gone: a manifest with no defs/ is a half-deleted
        # dump, not a machine that never took one.
        rows.append(("DefDump/ (live)",
                     "manifest, but no defs/*.json"
                     if os.path.isfile(os.path.join(D_DUMP, "manifest.json"))
                     else "absent", "MISSING", "GAME LOAD"))
    elif frozen_entry(D_DUMP):
        # ✅ FROZEN, not stale — and this branch sits ABOVE the hash comparison on
        # purpose, so a count mismatch can never reach it. See the note at the top.
        fe = frozen_entry(D_DUMP)
        rows.append(("DefDump/ (live)",
                     "%s (%s mods, %s)" % (dfp["hash"], dfp["modCount"],
                                           dfp.get("capturedUtc", "?")),
                     "FROZEN", "owner only (%s, %s)"
                     % (fe.get("by", "?"), fe.get("id", "?"))))
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

    # ⚠️ FROZEN is deliberately absent from this test. A frozen dump must never send
    # anyone on a ~23-minute load: that load would produce a dump matching the CURRENT
    # mod list, which is the opposite of what a frozen design target is for.
    needs_load = any(r[2] in ("STALE", "MISSING") and r[3] == "GAME LOAD" for r in rows)
    print("\n=== VERDICT ===")
    if needs_load:
        print("  A GAME LOAD IS REQUIRED to refresh the live dump (~23 min).")
        print("  Arm it first:")
        print("     echo all > \"%s\"" % os.path.join(D_DUMP, "dump_request.txt"))
        print("  Then load to the main menu; it writes at startup, no world needed.")
        print("  Everything else can be rebuilt now with --offline.")
    elif any(r[2] in ("STALE", "MISSING", "REBUILD") for r in rows):
        print("  Offline artefacts are stale or missing. Run --all; no game load needed.")
    elif steps_failed:
        # The artefact table is built from STAMPS, so it can only ever describe
        # past runs. It cannot see that a step in THIS run exited non-zero, and
        # on 2026-08-13 it printed "Everything is current" directly after four
        # such failures. The run's own outcome outranks the table.
        print("  🔴 NOT current. The table above reads clean because it is built")
        print("     from stamps, but a step in THIS run FAILED (see the exit")
        print("     codes above). Fix the failure and re-run — do not treat any")
        print("     artefact as matching this load set.")
    else:
        print("  Everything is current.")
    if fp.get("missing"):
        print("  ⚠️ ...but %d listed mod(s) are NOT INSTALLED (above). No rebuild"
              % len(fp["missing"]))
        print("     fixes that — the load set is not the one ModsConfig.xml claims.")
    return rows


# ---------------------------------------------------------------- actions
def run(cmd, label):
    print("\n--- %s" % label)
    rc = subprocess.call(cmd, cwd=ROOT)
    print("    %s (exit %d)" % ("ok" if rc == 0 else "FAILED", rc))
    return rc == 0


def do_offline(fp, note=""):
    ok = run([sys.executable, os.path.join("src", "RimMandrake", "Utils", "animal_inventory.py"),
              "--out", os.path.join("observed", "2026-08-13",
                                    "inventory")], "animal inventory")
    if ok:
        # 🔴 Both halves of this used to lie, and they compounded.
        # The contact-sheet exit code was DISCARDED, and write_stamp() ran
        # unconditionally — so a failed run still stamped the fingerprint, the
        # artefact table then read that stamp and reported "current", and the
        # final verdict said "Everything is current" after four steps exited 1.
        # Measured 2026-08-13 in observed/2026-08-13_refresh_all.log:2085-2116,
        # where "contact sheets FAILED (exit 1)" is followed on the next line by
        # "stamped .../GENERATED_FROM.json".
        # A stamp asserts "this artefact was generated from that load set". Only
        # a step that SUCCEEDED may assert it.
        sheets_ok = run([sys.executable,
                         os.path.join("src", "RimMandrake", "Utils", "animal_contact_sheet.py"),
                         "--out", SHEETS], "contact sheets")
        ok = ok and sheets_ok
        if ok:
            write_stamp(fp, note)
            print("    stamped %s" % STAMP)
        else:
            print("    NOT stamped - a generating step failed, so the artefacts "
                  "do NOT match this load set. Re-run after fixing the failure.")
    return ok


def do_patches():
    src = os.path.join(ARMOURY, "Source")
    ok = run([sys.executable, os.path.join(src, "gen_armoury_patch.py")],
             "armoury patch")
    ok = run([sys.executable, os.path.join(src, "gen_torpedo_speed.py")],
             "torpedo speed") and ok

    # ⚠️ REFUSE TO "VALIDATE" AGAINST NOTHING. Both inputs the live half needs
    # are checked HERE, before the subprocess, because a missing input makes
    # validate_patch skip checks rather than fail them, and a skipped check
    # reads exactly like a passed one in this function's output.
    absent = [(n, p) for n, p in (("workshop", _GP.WORKSHOP),
                                  ("local Mods/", _GP.LOCAL_MODS),
                                  ("game Data/", _GP.GAME_DATA))
              if not os.path.isdir(p)]
    if not _has_files(os.path.join(D_DUMP, "defs"), ".json"):
        absent.append(("live dump defs/", os.path.join(D_DUMP, "defs")))
    if absent:
        print("\n!! REFUSING to validate: the inputs the check needs are absent,")
        print("   so it would skip every live xpath check and still exit 0.")
        for n, p in absent:
            print("     MISSING  %-16s %s" % (n, p))
        print("   (src/RimMandrake/Utils/game_paths.py resolves these per platform;")
        print("    a C:\\ literal read from WSL is the classic way to get here.)")
        return False

    ok = run([sys.executable,
         os.path.join("skills", "rimworld-modding", "scripts", "validate_patch.py"),
         os.path.join(ARMOURY, "Patches"),
         # ⚠️ These MUST be the per-platform forms. As C:\ literals they were
         # absent under WSL, validate_patch loaded 0 defs, skipped every live
         # xpath check, warned, and exited 0 — which this function rendered as
         # "validate (with --live) ok". 29c89f0 dual-formed D_CONFIG and D_DUMP
         # and missed exactly these three. Found by a retired seat.
         "--defs", _GP.WORKSHOP,
         "--defs", _GP.LOCAL_MODS,
         "--defs", _GP.GAME_DATA,
         "--live", D_DUMP, "--quiet"], "validate (with --live)") and ok
    # ⚠️ This `and ok` is the whole point of the fix: the validator's exit code
    # was DISCARDED — its result printed to screen and then thrown away, so
    # do_patches returned the two GENERATORS' success and a failing validation
    # left no trace in the exit status. Anything scripting this saw 0.
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
    ap.add_argument("--fingerprint", action="store_true",
                    help="only compare ModsConfig.xml against the mods actually "
                         "on disk, print the result and exit. Touches no "
                         "artefact and needs no game load. Exit 0 = measured, "
                         "nothing missing; 1 = measured, mods are missing; "
                         "2 = UNMEASURABLE (a mod root could not be read).")
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
    except LoadsetUnmeasurable as exc:
        # Exit 2, not 1, and its own wording. "The check failed" and "the check
        # could not run" are different facts and a script must be able to tell
        # them apart from the exit status alone.
        sys.stderr.write("\n!! LOAD SET UNMEASURABLE — no answer was produced.\n"
                         "%s\n" % exc)
        sys.exit(2)
    except RuntimeError as exc:
        sys.exit("cannot resolve the load set: %s" % exc)

    if a.fingerprint:
        status_only_fingerprint(fp)
        sys.exit(1 if fp["missing"] else 0)

    status(fp)

    # An action that could not be carried out must reach the exit status, not
    # just the screen. A caller scripting `refresh.py --patches` had no way to
    # tell "regenerated and validated" from "refused, validated nothing".
    failed = False
    if a.all or a.offline:
        failed = not do_offline(fp, a.note) or failed
    if a.all or a.patches:
        dfp = dump_fingerprint()
        if dfp is None or dfp["hash"] != fp["hash"]:
            print("\n!! REFUSING to regenerate patches: the live dump is stale or")
            print("   absent, and the generator reads CURRENT damage values from")
            print("   it. Retuning against a dump of a different mod set would")
            print("   bake in numbers from a game you no longer have.")
            print("   Take a fresh dump first, or pass --patches again once done.")
            failed = True
        else:
            failed = not do_patches() or failed

    if a.all or a.offline or a.patches:
        print()
        status(fp, steps_failed=failed)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
