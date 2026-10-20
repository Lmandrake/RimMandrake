#!/usr/bin/env python3
"""save_guard.py - protect the Saves keepers around anything that can write a save.

KEEPER_SAVES_HARDEN_WRONG_SLOT_WRITES (2026-10-10). `rimworld/save_game` has written the CURRENT slot instead of
`saveName` and reported the requested path with exists:true (CLAUDE.md "Options he must LOOK at"). Checking
afterwards is necessary but too late, so this guard works in three steps:

  snapshot   hash every keeper (*.rws except Autosave-*) and copy each into a content-addressed store
             (D:\\ClaudeWork\\rimmandrake\\scratch\\save_keepers\\<sha256>.rws) - recoverable copies BEFORE the act
  admit      refuse: an existing target (no overwrite), a path escape, and any run where the game's CURRENT slot is
             a keeper or unknown - save_game may write the current slot, so only a known non-keeper is admitted
             ("none" = a game never loaded from a file, e.g. a quicktest)
  verify     after: list EVERY changed file; the target must be new, >= 1000 bytes and start like a savegame;
             every keeper must be unchanged by hash (same-size rewrites included). `restore` puts one back.

    python3 save_guard.py run --current-slot none -- python.exe some_bridge_script.py   # snapshot, run, verify
    python3 save_guard.py check                       # snapshot only; prints keeper count and store
    library:  snap = snapshot(); problems = admit(snap, name, slot); ...save...; verify(snap, SAVES, name)

Exit 0 verified; 1 refused or a keeper changed (the keeper is named and its store copy given); 2 cannot measure.
Autosaves rotate by design and are listed as changed, never as violations.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
STORE = rm_win("scratch", "save_keepers") if os.name == "nt" else rm_str("scratch", "save_keepers")
AUTOSAVE = re.compile(r"^Autosave-\d+\.rws$", re.I)
NAME_OK = re.compile(r"^[A-Za-z0-9_\-. ]+$")
MIN_BYTES = 1000


def _saves():
    from game_paths import SAVES
    return SAVES


def store_path(store, sha):
    return os.path.join(store, sha + ".rws")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _index(store):
    p = os.path.join(store, "index.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _stat(path):
    st = os.stat(path)
    return st.st_size, st.st_mtime_ns


def _listing(saves_dir):
    return {n: _stat(os.path.join(saves_dir, n)) for n in os.listdir(saves_dir) if n.lower().endswith(".rws")}


def snapshot(saves_dir=None, store=None):
    """{saves_dir, store, files: {name: [size, mtime_ns]}, keepers: {name: {size, mtime_ns, sha256}}}.
    Raises OSError if a keeper cannot be backed up - a guard that cannot back up must not admit."""
    saves_dir = saves_dir or _saves()
    store = store or STORE
    os.makedirs(store, exist_ok=True)
    idx = _index(store)                       # "name|size|mtime_ns" -> sha, so unchanged keepers are not rehashed
    files = _listing(saves_dir)
    keepers = {}
    for n, (size, mt) in sorted(files.items()):
        if AUTOSAVE.match(n):
            continue
        key = "%s|%d|%d" % (n, size, mt)
        sha = idx.get(key)
        if not sha or not os.path.exists(store_path(store, sha)):
            sha = _sha(os.path.join(saves_dir, n))
            dst = store_path(store, sha)
            if not os.path.exists(dst):
                tmp = dst + ".part"
                shutil.copy2(os.path.join(saves_dir, n), tmp)
                os.replace(tmp, dst)
            idx[key] = sha
        keepers[n] = {"size": size, "mtime_ns": mt, "sha256": sha}
    tmp = os.path.join(store, "index.json.part")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(idx, fh)
    os.replace(tmp, os.path.join(store, "index.json"))
    return {"saves_dir": saves_dir, "store": store, "files": {k: list(v) for k, v in files.items()},
            "keepers": keepers}


def admit(snap, target, current_slot):
    """[] to admit, else the reasons to refuse. current_slot: the save the running game was loaded from, 'none' for
    a game never loaded from a file, None if unknown (refused)."""
    why = []
    if target is not None:
        if not NAME_OK.match(target or "") or ".." in target or target.startswith("."):
            why.append("target %r is not a plain save name (path escape refused)" % target)
        elif target + ".rws" in snap["files"]:
            why.append("%s.rws already exists - choose a new name (overwrite is never admitted here)" % target)
    if current_slot is None:
        why.append("current slot UNKNOWN: save_game has written the current slot instead of saveName, so the slot "
                   "must be known; pass --current-slot <loaded save name> or none")
    elif current_slot.lower() != "none":
        slot = current_slot if current_slot.lower().endswith(".rws") else current_slot + ".rws"
        if slot in snap["keepers"]:
            why.append("current slot %s is a keeper: a wrong-slot write would overwrite it - load a disposable "
                       "copy first" % slot)
    return why


def _looks_like_save(path):
    try:
        with open(path, "rb") as fh:
            head = fh.read(4096)
    except OSError:
        return False
    return head.lstrip().startswith(b"<?xml") and b"<savegame" in head


def verify(snap, saves_dir=None, target=None):
    saves_dir = saves_dir or snap["saves_dir"]
    now = _listing(saves_dir)
    before = {k: tuple(v) for k, v in snap["files"].items()}
    changed = sorted(n for n in now if before.get(n) != now[n])
    vanished = sorted(n for n in before if n not in now)
    problems = []
    for n, k in sorted(snap["keepers"].items()):
        if n not in now:
            problems.append("keeper %s VANISHED (store copy %s)" % (n, store_path(snap["store"], k["sha256"])))
        elif now[n] != (k["size"], k["mtime_ns"]) and _sha(os.path.join(saves_dir, n)) != k["sha256"]:
            problems.append("keeper %s CHANGED (%d -> %d bytes; store copy %s)" % (
                n, k["size"], now[n][0], store_path(snap["store"], k["sha256"])))
    if target is not None:
        t = target + ".rws"
        if t not in now:
            problems.append("no %s appeared (a wrong-slot write looks exactly like this)" % t)
        elif t in before:
            problems.append("%s existed before the save" % t)
        elif now[t][0] < MIN_BYTES or not _looks_like_save(os.path.join(saves_dir, t)):
            problems.append("%s is not a well-formed savegame (%d bytes)" % (t, now[t][0]))
    return {"verified": not problems, "problems": problems, "changed": changed, "vanished": vanished}


def restore(snap, saves_dir, store, name):
    k = snap["keepers"].get(name)
    if not k:
        return False
    src = store_path(store, k["sha256"])
    if not os.path.exists(src) or _sha(src) != k["sha256"]:
        return False
    shutil.copy2(src, os.path.join(saves_dir, name))
    return True


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    r = sub.add_parser("run")
    r.add_argument("--current-slot", help="save the game was loaded from, or none")
    r.add_argument("--target", help="the save name the command will write, if any")
    r.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    try:
        snap = snapshot()
    except OSError as e:
        print("save_guard: UNMEASURED - cannot snapshot/back up keepers: %s" % e)
        return 2
    print("save_guard: %d keepers hashed and backed up in %s" % (len(snap["keepers"]), snap["store"]))
    if a.cmd == "check":
        return 0
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd:
        print("save_guard: run needs a command after --")
        return 2
    why = admit(snap, a.target, a.current_slot)
    if why:
        print("save_guard: REFUSED\n  - " + "\n  - ".join(why))
        return 1
    rc = subprocess.call(cmd)
    v = verify(snap, target=a.target)
    print("save_guard: command exit %d; changed files: %s" % (rc, ", ".join(v["changed"]) or "none"))
    if not v["verified"]:
        print("save_guard: KEEPER VIOLATION\n  - " + "\n  - ".join(v["problems"]))
        return 1
    print("save_guard: VERIFIED - no keeper changed%s" % (", %s.rws is new and well-formed" % a.target
                                                          if a.target else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main())
