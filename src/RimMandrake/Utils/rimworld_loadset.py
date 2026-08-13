#!/usr/bin/env python3
"""
rimworld_loadset.py - resolve which mod folders RimWorld will ACTUALLY load.

WHY THIS EXISTS
===============
Every offline tool in this project has to answer one question before it can
answer any other: which files on disk does the running game actually read?

The naive answer - walk the Workshop tree - is wrong by a large factor, and it
is wrong in a way that produces confident bad numbers rather than errors:

  * Most mods ship several version folders (1.0 ... 1.6). RimWorld loads ONE.
    Beasts of the Rim ships seven copies of its Armadillo def; six are inert.
    Counting all of them made validate_patch.py report "7 matches" for a
    PatchOperationRemove and advise a positional predicate that would have
    broken a correct patch.
  * ~1,211 mods are installed here; 562 are active. The rest contribute nothing.
  * LoadFolders.xml makes a mod's contribution CONDITIONAL on the rest of the
    mod list. Vanilla Animals Expanded carries
        <li IfModNotActive="Ludeon.RimWorld.Odyssey">1.6NotOdyssey</li>
    so with Odyssey active its badger, moose, muskox and porcupine do not exist.
    A scan that ignores this invents four animals that the game cannot spawn -
    and missing that fact is what left Choose Wild Animal Spawns dead for three
    consecutive loads.

Scoped correctly on this machine: 33,174 candidate def files drop to 8,293.

WHAT IT DOES NOT DO
===================
Reads BASE XML only. PatchOperations have not run, so anything another mod's
patch creates, edits or deletes is invisible here. That blind spot is real and
has bitten this project: the five dangling wildAnimals entries that killed CWAS
exist only after Primordial Geysers' patch applies. Scan Patches/ separately if
you need them.

USAGE
=====
    from rimworld_loadset import build_load_set, def_dirs

    mods, missing, version = build_load_set(CONFIG, [WORKSHOP, LOCAL, DATA])
    for m in mods:                      # in load order
        for d in def_dirs(m, "Defs"):
            ...

NOTE ON DUPLICATION
===================
skills/rimworld-modding/scripts/validate_patch.py carries its own copy of this
logic on purpose - that script is packaged into a portable .skill and must not
import from this project. Fix bugs in BOTH. They are verified against the same
numbers (562 active / 8,293 def files / Armadillo == 1 match).

Dependency-free: Python 3.8+ stdlib only. Keep it that way.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

__all__ = ["build_load_set", "def_dirs", "parse_mods_config", "read_about",
           "resolve_load_folders", "parse_xml", "DEFAULT_MODS_CONFIG"]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import MODS_CONFIG as DEFAULT_MODS_CONFIG  # noqa: E402,F401

# ⚠️ This was `os.path.expanduser("~") + AppData/LocalLow/...` until
# 2026-08-13. That is wrong under WSL and wrong SILENTLY: expanduser gives the
# LINUX home, so it builds /home/<user>/AppData/LocalLow/... — a path that has
# never existed on any machine — and the failure names a missing ModsConfig.
# The identical trap hit the bridge client's DEFAULT_PLAYER_LOG, which scraped
# a token from a log path that resolved into the Linux home and reported
# "no bridge token found". expanduser is not a portability fix; it is a
# portability BUG whenever the target file belongs to the Windows side.


def parse_xml(path):
    """Tolerant parse: retry once without the XML declaration (BOM/encoding)."""
    try:
        return ET.parse(path).getroot()
    except Exception:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                raw = fh.read()
            raw = re.sub(r"^\s*<\?xml[^>]*\?>", "", raw).strip()
            return ET.fromstring(raw)
        except Exception:
            return None


def parse_mods_config(path):
    """
    Return (active packageIds lowercased, in load order; 'major.minor' version).

    Deliberately ignores <knownExpansions>. Those entries are ALSO in
    <activeMods>, so counting both double-counts the DLC - a mistake that has
    already produced two wrong mod counts in this project's notes.
    """
    root = parse_xml(path)
    if root is None:
        raise OSError("cannot parse ModsConfig at %s" % path)

    active = []
    node = root.find("activeMods")
    if node is not None:
        for li in node.findall("li"):
            if li.text and li.text.strip():
                active.append(li.text.strip().lower())

    version = ""
    vnode = root.find("version")
    if vnode is not None and vnode.text:
        m = re.match(r"\s*(\d+\.\d+)", vnode.text)
        if m:
            version = m.group(1)
    return active, version


def read_about(mod_dir):
    """
    (packageId lowercased, display name) from <mod_dir>/About/About.xml.

    packageId MUST be read as a DIRECT CHILD of the root <ModMetaData>. A regex
    for the first packageId in the file, or a recursive find(), returns one out
    of a <modDependencies> block instead - which maps Harmony to Camera+ and
    poisons the entire index. Display name falls back to the folder name so
    Core/DLC never render as "?".
    """
    about = os.path.join(mod_dir, "About", "About.xml")
    if not os.path.isfile(about):
        return None
    root = parse_xml(about)
    if root is None:
        return None
    pid_node = root.find("packageId")           # direct child only
    if pid_node is None or not (pid_node.text or "").strip():
        return None
    name_node = root.find("name")
    name = (name_node.text or "").strip() if name_node is not None else ""
    return (pid_node.text.strip().lower(),
            name or os.path.basename(mod_dir.rstrip("/\\")))


def discover_mods(roots):
    """
    Index installed mods by packageId across the given roots.

    A candidate is a root itself or any IMMEDIATE subdirectory holding
    About/About.xml, which covers all three real layouts:
        steamapps/workshop/content/294100/<id>/
        RimWorld/Data/<Core|Royalty|Odyssey|...>/
        RimWorld/Mods/<name>/
    First root wins a packageId collision.
    """
    index = {}
    for root_dir in roots:
        if not os.path.isdir(root_dir):
            continue
        candidates = [root_dir]
        try:
            candidates += [os.path.join(root_dir, e)
                           for e in sorted(os.listdir(root_dir))]
        except OSError:
            pass
        for cand in candidates:
            if not os.path.isdir(cand):
                continue
            got = read_about(cand)
            if not got:
                continue
            pid, name = got
            if pid not in index:
                index[pid] = {"packageId": pid, "name": name, "folder": cand,
                              "root": root_dir}
    return index


def _norm_rel(rel):
    """'/' and '\\' both mean the mod root. Otherwise normalise separators."""
    rel = (rel or "").strip()
    if rel in ("", "/", "\\", ".", "./"):
        return ""
    return rel.replace("\\", "/").strip("/")


def _condition_ok(li, active):
    """Honour IfModActive / IfModNotActive: case-insensitive, comma tolerant."""
    want = li.get("IfModActive")
    if want:
        ids = [x.strip().lower() for x in want.split(",") if x.strip()]
        if not all(i in active for i in ids):
            return False
    nope = li.get("IfModNotActive")
    if nope:
        ids = [x.strip().lower() for x in nope.split(",") if x.strip()]
        if any(i in active for i in ids):
            return False
    return True


def resolve_load_folders(mod_dir, version, active):
    """
    The content folders this mod contributes at the target game version.

    With a LoadFolders.xml: the <v{major.minor}> block, every <li> whose
    condition holds. Without one: <mod>/<version> if present, else the mod root.
    ElementTree drops comments, so commented-out entries are free to ignore.
    """
    lf = os.path.join(mod_dir, "LoadFolders.xml")
    folders = []

    if version and os.path.isfile(lf):
        root = parse_xml(lf)
        if root is not None:
            block = root.find("v%s" % version)
            if block is not None:
                for li in block.findall("li"):
                    if not _condition_ok(li, active):
                        continue
                    rel = _norm_rel(li.text)
                    p = os.path.join(mod_dir, *rel.split("/")) if rel else mod_dir
                    if os.path.isdir(p) and p not in folders:
                        folders.append(p)
                return folders

    # No LoadFolders.xml: the game loads the mod ROOT *and* the versioned
    # folder, not one or the other. Getting this wrong silently hides content.
    #
    # Measured on the 562-mod stack (2026-08-10): 35 active mods ship a root
    # Defs/ alongside a version folder — RIMMSqol (178 defs), Way Better
    # Romance (64), Numbers (40), LWM's Deep Storage (18), Adaptive Storage
    # Framework (11) and others — for 667 def nodes total. Treating the version
    # folder as exclusive made all of them invisible, which showed up as 28
    # defs across 4 mods failing to resolve ParentName="AdaptiveStorageBase":
    # the framework declares that base in its ROOT Defs/ThingDefBase.xml. Those
    # mods demonstrably work in game and the log carries no inheritance errors,
    # so the root is definitely loaded.
    #
    # Order: root first, then versioned, so a version-specific override wins
    # over the root's copy of the same def under last-in-wins.
    versioned = os.path.join(mod_dir, version) if version else ""
    folders.append(mod_dir)
    if versioned and os.path.isdir(versioned) and versioned != mod_dir:
        folders.append(versioned)
    return folders


def build_load_set(config_path, roots, version_override=None):
    """
    Resolve the real load set.

    Returns (mods, missing, version):
      mods    - list of dicts in LOAD ORDER, each with packageId, name, folder,
                workshopId, order (1-based), contentDirs (resolved folders)
      missing - active packageIds with no folder on disk (a broken install, or
                a mod whose files were removed without deactivating it)
      version - the 'major.minor' the load set was resolved against
    """
    active, version = parse_mods_config(config_path)
    if version_override:
        version = version_override
    active_set = set(active)
    index = discover_mods(roots)

    mods, missing = [], []
    for i, pid in enumerate(active, 1):
        info = index.get(pid)
        if not info:
            missing.append(pid)
            continue
        folder = info["folder"]
        rec = dict(info, order=i)
        rec["workshopId"] = ("core/dlc"
                             if os.path.basename(info["root"]).lower() == "data"
                             else os.path.basename(folder))
        rec["contentDirs"] = resolve_load_folders(folder, version, active_set)
        mods.append(rec)
    return mods, missing, version


def def_dirs(mod, subdir):
    """Existing <contentDir>/<subdir> paths for a mod ('Defs', 'Patches', ...)."""
    out = []
    for base in mod.get("contentDirs") or [mod["folder"]]:
        p = os.path.join(base, subdir)
        if os.path.isdir(p) and p not in out:
            out.append(p)
    return out


if __name__ == "__main__":
    from game_paths import WORKSHOP, LOCAL_MODS, GAME_DATA
    cfg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODS_CONFIG
    roots = sys.argv[2:] or [WORKSHOP, LOCAL_MODS, GAME_DATA]
    mods, missing, ver = build_load_set(cfg, roots)
    ndirs = sum(len(m["contentDirs"]) for m in mods)
    print("version %s | active %d | resolved %d | missing %d | content dirs %d"
          % (ver, len(mods) + len(missing), len(mods), len(missing), ndirs))
    if missing:
        print("missing:", ", ".join(missing[:10]))
