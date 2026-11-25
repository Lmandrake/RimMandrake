#!/usr/bin/env python3
"""The BUILD MATCH: an in-game verdict counts only on the build he will walk. A program, no AI; run at the Stage 6 exit.

Owner, 2026-11-17, approving the Stage 6 -> Stage 7 change (item RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO;
spec design/specs/2026-11-13-maturation-pipeline.md, Stage 6 exit and Stage 7):
  every in-game verdict records the game, the mod's source sha, a hash of its deployed folder, the active mod list
  (ModsConfig.xml activeMods, parsed, in order) and the game build. A verdict whose mod hash or game build differs from
  the build he walks does not count; its check is re-run. The list for comparison is his walk's for a full-list test,
  or the list modset_builder.py builds for its tier for a minimal-list test. A mod joining or leaving that list reruns
  only checks that read it or whose mod-list relation cannot be read.

  python3 src/RimMandrake/rimflow/build_match.py identity --mod M (--tier T | --full) [--mod-sha SHA]
      one JSON line, the identity fields a live driver merges into each rows.jsonl row it writes (run it on the game
      machine, after the deploy and the list swap, before the check)
  python3 src/RimMandrake/rimflow/build_match.py loaded --mod M [--receipt FILE|-] [--game NAME]
      one JSON line: is what the RUNNING game loaded the deployed folder's and the commit's DLLs, on ModsConfig's list
      (loaded_build.py; the receipt is read over the bridge of the game this shell means, or from FILE). Exit 0 MATCH,
      1 a fault, 2 could not look, 4 the mod ships no DLL
  python3 src/RimMandrake/rimflow/build_match.py check --mod M [--visit N]
      reads each check's last row (visit N's, else the latest earlier visit's) against the walk build (the labelled
      savegame its Exit block names, read on Archmagi): one line per check, then cases read, how many count, the checks
      to run by name, and the worst; exit 0 only when every one counts and the walk folder is the current source

Owner, 2026-11-21 (item RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203), narrowing the 2026-11-17 ruling
to the checks a change touches: "No all 203 checks should NOT have to be rerun it should only be the ones pertaining to
the switch." A row made on an earlier build still counts when the change since its commit (`mod_sha`) touches nothing
its check reads or exercises (rerun_relation.py, one relation for every stage); a touched check, or one whose relation
cannot be read, runs again, and only those. A game build that differs still re-runs the row: the game itself changed.
When the deployed walk folder is not the current source (its .srchash differs), that is one act, a deploy, never a
rerun of checks.

Where each piece comes from:
  mod hash     sha256 over the deployed folder's files (posix relative path, size, bytes; sorted), so a redeploy of the
               same bytes keeps it and one changed byte changes it. A mod composed into Baroque Biomes
               (src/RimMandrake/Biomes.compose.json, wave <= compose_wave) has no folder of its own: its hash is the
               Biomes folder's, so a change to any composed biome re-runs its checks (the safe side).
  game build   the first line of the game's Version.txt ("1.6.4871 rev590" measured 2026-11-17).
  walk list    the labelled savegame's <modIds>, in order: his walk loads that save (spec: the walk's list is read when
               the walk savegame is made). He walks on Archmagi (WALK_HOST), so the walk build is read there only.
  tier list    modset_builder.resolve_tier(tier, scan()) on this machine and this commit; a tier it refuses or that
               misses a mod gives no list, so the row does not count. A row does not name the install it ran on, so a
               list that differs from this process's install is read against the machine's other installs too
               (ArchBig, ArchSmall: each reads its own Mods folder, so one deployed About.xml can differ).
Packages compare lower-case with a trailing `_steam` dropped (RimWorld's own suffix for a Steam copy of a local mod).
MATURATION_WALK_BUILD names a JSON file that stands in for the live machine ({mod_hash, game_build, active_mods,
tiers: {name: [packageIds]}}); selftests use it, and every reading made with it names it.
"""
import errno
import argparse
import hashlib
import json
import os
import re
import socket
import stat
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from functools import cache

import live_kinds as LK
import own_cgroup
import rerun_relation as RR

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE) if HERE not in sys.path else None
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")

WALK_HOST = "archmagi"                       # he walks on Archmagi (spec Stage 8; GAMES in maturation.py)
STANDIN_ENV = "MATURATION_WALK_BUILD"
CACHE_DIR = "/mnt/d/ClaudeWork/rimmandrake/build_match"
REQUIRED = ("mod_hash", "game_build", "active_mods")
LIMIT = ("every check counts: its game build equals the walk's, any change of list membership leaves the mods it reads "
         "or exercises untouched, and its mod hash equals the walk's or the source change leaves it untouched")


# ---- reading the machine ---------------------------------------------------------------------------------------------

def norm_pid(p):
    p = str(p or "").strip().lower()
    return p[:-len("_steam")] if p.endswith("_steam") else p


def norm_list(xs):
    return [norm_pid(x) for x in xs or []]


def same_list(a, b):
    return norm_list(a) == norm_list(b)


# drvfs (/mnt/d) can refuse one read with ENOMEM under memory pressure and read the same file whole the next time
# (measured 2026-11-24 on a 618 kB Biomes texture, ArchSmall's Mods folder). The bound guards a file that always fails
# from holding the reading for ever; the need measured is one read again, so ten tries is ten times that.
TRANSIENT_READ = (errno.ENOMEM, errno.EAGAIN, errno.EINTR)
READ_TRIES = 10
RETRY_PAUSE_S = 0.5


def _digest_file(path, h):
    """A plain file's size and bytes. Anything else raises OSError, so the folder hashes to None: a pipe or device is
    never opened (a pipe would wait for a writer), and a file whose read length is not its size (a /proc file reads
    bytes at size 0) is refused, so every hash the cache keeps was read from bytes its size key describes (third GPT
    review, 2026-11-17). A read that fails with a transient errno is read again from its start; the bytes go into h
    only after one whole read, so a retry never changes the hash."""
    if not stat.S_ISREG(os.stat(path).st_mode):
        raise OSError("not a plain file: %s" % path)
    for attempt in range(READ_TRIES):
        try:
            with open(path, "rb") as f:
                size = os.fstat(f.fileno()).st_size
                chunks = list(iter(lambda: f.read(1 << 20), b""))
            break
        except OSError as e:
            if e.errno not in TRANSIENT_READ or attempt == READ_TRIES - 1:
                raise
            time.sleep(RETRY_PAUSE_S)
    got = sum(len(c) for c in chunks)
    if got != size:
        raise OSError("read %d bytes of a %d-byte file: %s" % (got, size, path))
    h.update(b"%d\0" % size)
    for c in chunks:
        h.update(c)


def _files(folder):
    """(posix relative path, path) of every file, sorted. Linked directories are followed, as the game follows them
    (a link to a directory already on the path down is a cycle and is cut; two links to one directory are two paths the
    game loads, both hashed); an unreadable directory raises OSError, never drops out of the hash.
    Empty directories are not hashed: the game loads files, and a folder holding no file changes nothing it loads.
    A directory is known by its device and inode, not by its path: drvfs folds case and realpath does not, so a link to
    an ancestor spelt in another case was hashed once more (third GPT review; inode equal across case on /mnt/d,
    measured 2026-11-17)."""
    out = []
    st = os.stat(folder)
    stack = [(folder, "", frozenset(((st.st_dev, st.st_ino),)))]
    while stack:
        d, rel, chain = stack.pop()
        with os.scandir(d) as it:
            entries = list(it)
        for e in entries:
            r = rel + e.name
            if e.is_dir():                              # follows a link, as the game does
                s = e.stat()
                ident = (s.st_dev, s.st_ino)
                if ident not in chain:                  # every directory down this path is in chain: no loop
                    stack.append((e.path, r + "/", chain | {ident}))
            else:
                out.append((r, e.path))
    return sorted(out)


def deployed_hash(folder, cache_dir=None):
    """sha256:<hex> over the folder's files, or None when there is no folder or a part of it cannot be read. With
    cache_dir, a hash is kept under a key of the folder's real path and every file's path, size, mtime and change time
    (ctime: a write moves it and no utime can put it back; measured on drvfs 2026-11-17), so an unchanged folder is not
    read twice (RimMandrake.Biomes, 704 MB, 4761 files: 72 s uncached, measured 2026-11-17). The key is metadata, so it
    cannot see a change no write call makes (stores through a live shared mapping) or a file only another user cannot
    open; a deployed mod folder is written by deploy_custom_mods with plain writes as the one user, and the game opens
    it read-only. A deploy during a reading is the same race an uncached read has: the next reading sees it."""
    return deployed_hash_why(folder, cache_dir)[0]


def deployed_hash_why(folder, cache_dir=None):
    """(hash, None), or (None, why): why is "no folder" when there is none, else the read error, so a deployed folder
    that cannot be read is never reported as not deployed."""
    if not folder or not os.path.isdir(folder):
        return None, "no folder"
    try:
        return _hash_files(folder, _files(folder), cache_dir), None
    except OSError as e:
        return None, "a part of %s could not be read: %s" % (folder, e)


def _deploy_stamp(folder):
    return os.path.join(os.path.dirname(folder), ".%s.walk-build.json" % os.path.basename(folder))


def _folder_id(folder):
    st = os.stat(folder)
    return [st.st_dev, st.st_ino]


def _stamped_hash(folder):
    try:
        with open(_deploy_stamp(folder), encoding="utf-8") as f:
            stamp = json.load(f)
        h = stamp.get("mod_hash") if isinstance(stamp, dict) else None
        if isinstance(h, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", h) and stamp.get("folder") == _folder_id(folder):
            return h
    except (OSError, ValueError):
        pass                                     # no usable stamp: read the deployed files
    return None


@contextmanager
def stamp_composed_deploy(folder):
    """Invalidate the forecast's stamp before composing into Mods, then publish the actual deployed hash. The
    writer lock keeps two applies from publishing through one another. An interrupted apply leaves no stamp."""
    import fcntl

    stamp = _deploy_stamp(folder)
    with open(stamp + ".lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            os.unlink(stamp)
        except FileNotFoundError:
            pass
        yield
        try:
            folder_id = _folder_id(folder)
        except OSError:
            return
        h = deployed_hash(folder)
        if h is None:
            return
        tmp = None
        try:
            if folder_id != _folder_id(folder):
                return
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(stamp),
                                             prefix=os.path.basename(stamp) + ".", delete=False) as f:
                tmp = f.name
                json.dump({"folder": folder_id, "mod_hash": h}, f)
            os.replace(tmp, stamp)
            tmp = None
        except OSError as e:
            print("Could not write the composed walk build stamp for %s: %s" % (folder, e), file=sys.stderr)
        finally:
            if tmp is not None:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass


def _cache_key(folder, files, cache_dir):
    """Each part is one JSON line: a name may hold a newline, and JSON escapes it, so no two
    folders serialize alike (third GPT review, 2026-11-17). A part that is not a plain file has no key."""
    sig = hashlib.sha256(json.dumps(os.path.realpath(folder)).encode("ascii") + b"\n")
    for r, p in files:
        st = os.stat(p)
        if not stat.S_ISREG(st.st_mode):
            raise OSError("not a plain file: %s" % p)
        sig.update(json.dumps([r, st.st_size, st.st_mtime_ns, st.st_ctime_ns]).encode("ascii") + b"\n")
    return os.path.join(cache_dir, "hash_%s.txt" % sig.hexdigest()[:32])


def _hash_files(folder, files, cache_dir):
    key = None
    if cache_dir:
        key = _cache_key(folder, files, cache_dir)
        try:
            with open(key) as f:
                got = f.read().strip()
            if got.startswith("sha256:"):
                return got
        except OSError:
            pass
    h = hashlib.sha256()
    for r, p in files:
        h.update(os.fsencode(r) + b"\0")                 # a name that is not UTF-8 hashes too
        _digest_file(p, h)
    out = "sha256:" + h.hexdigest()
    if key:
        _keep(key, out)
    return out


def _keep(key, out):
    """Keeping a hash is best-effort: a cache that cannot be written (read-only, full) costs the next reading time,
    never this reading's hash (fifth GPT review, 2026-11-17)."""
    try:
        os.makedirs(os.path.dirname(key), exist_ok=True)
        with open(key, "w") as f:
            f.write(out + "\n")
    except OSError:
        pass


def active_mods(config):
    """ModsConfig.xml's activeMods, parsed (never grepped: a commented-out line is not a mod), in order; None unread."""
    try:
        node = ET.parse(config).getroot().find("activeMods")
    except (OSError, ET.ParseError):
        return None
    return [(li.text or "").strip() for li in node.findall("li")] if node is not None else None


def game_build(version_txt):
    try:
        with open(version_txt, encoding="utf-8", errors="replace") as f:
            return f.readline().strip() or None
    except OSError:
        return None


def _first_package_id(about):
    try:
        r = ET.parse(about).getroot()
    except (OSError, ET.ParseError):
        return None
    n = r.find("packageId")
    return norm_pid(n.text) if n is not None and n.text else None


def mod_package_id(root, mod):
    """The mod's own packageId: About.xml's top-level <packageId> (one under modDependencies is a dependency)."""
    return _first_package_id(os.path.join(root, "src", "RimMandrake", mod, "About", "About.xml"))


COMPOSE_UNREADABLE = (None, None)   # the composition file is there but cannot be read: which folder loads is unknown


def compose_file(root):
    return os.path.join(root, "src", "RimMandrake", "Biomes.compose.json")


def composed_into(root, mod):
    """(packageId, folder name) of Baroque Biomes when Biomes.compose.json composes `mod` into it; None when it does
    not or there is no such file; COMPOSE_UNREADABLE when the file is there but cannot be read or has the wrong shape,
    so a composed mod is never sent to a stale standalone copy (fourth GPT review, 2026-11-17)."""
    try:
        with open(compose_file(root), encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        return None
    except (OSError, ValueError):
        return COMPOSE_UNREADABLE
    try:
        cw = d.get("compose_wave", 0)
        if any(e.get("key") == mod and e.get("wave", 99) <= cw for e in d.get("entries") or ()):
            return norm_pid((d.get("about") or {}).get("packageId")), d.get("target")
    except (AttributeError, TypeError):
        return COMPOSE_UNREADABLE
    return None


def deployed_folder(mods_dir, pid, mod):
    """The game's folder for packageId `pid`: Mods/<mod> when its About.xml names pid, else the folder that does."""
    first = os.path.join(mods_dir, mod)
    if pid and _first_package_id(os.path.join(first, "About", "About.xml")) == pid:
        return first
    try:
        names = sorted(os.listdir(mods_dir))
    except OSError:
        return None
    for n in names:
        p = os.path.join(mods_dir, n)
        if pid and os.path.isdir(p) and _first_package_id(os.path.join(p, "About", "About.xml")) == pid:
            return p
    return None


def _paths():
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import game_paths
    return game_paths.LOCAL_MODS, game_paths.MODS_CONFIG, os.path.join(game_paths.GAME_DIR, "Version.txt")


def _mod_folder(root, mod, mods_dir):
    """A mod composed into Biomes is read from the Biomes folder only: a standalone copy left from before it was
    composed is not what the walk loads (second GPT review, 2026-11-17), and with Biomes not deployed the mod is not
    deployed (third)."""
    pid = mod_package_id(root, mod)
    comp = composed_into(root, mod)
    if comp == COMPOSE_UNREADABLE:                      # composed or not is unknown: no folder (fourth GPT review)
        return pid, None
    if comp:                                            # composed: Biomes or nothing (third GPT review)
        return pid, deployed_folder(mods_dir, comp[0], comp[1] or "")
    return pid, deployed_folder(mods_dir, pid, mod)


def source_sha(root, mod):
    try:
        r = own_cgroup.run(["git", "-C", root, "log", "-1", "--format=%h", "--", "src/RimMandrake/%s" % mod],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _installed_only(am, mods_dir, scan=None):
    """-> (the packages of am this machine has installed, the ones it has not, why[]). The game skips an active package
    with no mod on disk, so a save never names it (koth.isid, ExplosiveKnockback visit 4). A scan that fails or finds no
    base game is 'could not look': the list comes back whole, with the reason."""
    try:
        if scan is None:
            sys.path.insert(0, UTILS) if UTILS not in sys.path else None
            import modset_builder
            scan = modset_builder.scan
        here = {norm_pid(p) for p in scan(mods_dir)}
    except Exception as e:
        return am, None, ["the installed mods could not be scanned (%s: %s)" % (type(e).__name__, e)]
    if "ludeon.rimworld" not in here:
        return am, None, ["the scan of the installed mods found no base game, so which packages the game loads is unknown"]
    return [p for p in am if norm_pid(p) in here], [p for p in am if norm_pid(p) not in here], []


def identity(root, mod, tier=None, full=False, mods_dir=None, config=None, version_txt=None, host=None, mod_sha=None,
             cache_dir=None, scan=None):
    """The fields a row records: game, mod_sha, mod_hash, game_build, active_mods, unit, and tier or full_list. `why`
    names what could not be read (a row with a missing field does not count). A full row's active_mods are the packages
    of ModsConfig that this machine has installed, the ones the game loads and a save names; the rest are `not_installed`.
    scan: a stand-in for modset_builder.scan (selftests)."""
    if None in (mods_dir, config, version_txt):
        m, c, v = _paths()
        mods_dir, config, version_txt = mods_dir or m, config or c, version_txt or v
    why = []
    pid, folder = _mod_folder(root, mod, mods_dir)
    h, err = deployed_hash_why(folder, cache_dir=cache_dir)
    if composed_into(root, mod) == COMPOSE_UNREADABLE:
        why.append("%s cannot be read, so which folder the game loads %s from is unknown: repair it"
                   % (compose_file(root), mod))
    if h is None and err == "no folder":
        why.append("%s is not deployed in %s (no folder whose About.xml names %s): deploy it first"
                   % (mod, mods_dir, pid or "its packageId"))
    elif h is None:
        why.append("%s is deployed, but %s; read it again" % (mod, err))
    am = active_mods(config)
    if not am:
        why.append("no activeMods read from %s" % config)
    absent = None
    if full and am:
        am, absent, bad = _installed_only(am, mods_dir, scan)
        why += bad
    gb = game_build(version_txt)
    if not gb:
        why.append("no game build read from %s" % version_txt)
    sha = mod_sha or source_sha(root, mod)
    if not sha:
        why.append("no source sha for src/RimMandrake/%s" % mod)
    out = {"game": (host or socket.gethostname()).strip().lower(), "mod_sha": sha, "mod_hash": h, "game_build": gb,
           "active_mods": am, "deployed_folder": folder}
    if os.environ.get("RM_ROLE_UNIT"):
        out["unit"] = os.environ["RM_ROLE_UNIT"]
    if full:
        out["full_list"] = True
        if absent:
            out["not_installed"] = absent
    else:
        out["tier"] = tier
    if why:
        out["why"] = why
    return out


def _standin_refused(root):
    """A stand-in walk build is for a test tree only: refused in this repo and in any git checkout (a pool clone, or
    this repo reached by another spelling on a case-insensitive drive; fourth GPT review, 2026-11-17)."""
    return os.path.realpath(root) == os.path.realpath(REPO) or os.path.exists(os.path.join(root, ".git"))


def _foreign_checkout(root):
    """A git checkout that is not the one this file sits in: tier lists come from UTILS, this checkout's modset_builder,
    so another checkout's rows are not read here (fifth GPT review, 2026-11-17). The same folder by another spelling is
    not foreign (samefile: drvfs is case-insensitive)."""
    if not os.path.exists(os.path.join(root, ".git")):
        return False
    try:
        return not os.path.samefile(root, REPO)
    except OSError:
        return True


def walk_letter(savegame):
    """-> the letter of the game he walks this savegame on: the game whose instance folder holds it (ArchSmall reads its own
    Saves folder), else "a" (ArchBig's Saves folder, and a path that names no game). Owner, 2026-11-24: full-list testing is
    retired, so a walk save stands on a small list, on any game of Archmagi."""
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import game_instance
    p = str(savegame or "").replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", p)
    p = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2)) if m else p
    try:
        top = game_instance.root().replace("\\", "/")
    except Exception:       # no instance root on this machine: no named game's save can be here
        return "a"
    m = re.match(r"^([A-Za-z]):/(.*)$", top)
    top = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2)) if m else top
    m = re.match(re.escape(top.rstrip("/")) + r"/([a-z])/Saves/", p, re.I)
    return m.group(1).lower() if m else "a"


def _game_name(letter):
    import game_names
    return game_names.show(letter)


def walk_paths(savegame):
    """-> (Mods folder, Version.txt) of the game that holds the walk savegame."""
    letter = walk_letter(savegame)
    if letter == "a":
        m, _, v = _paths()
        return m, v
    import game_instance
    d = game_instance.game_dir(letter)
    return os.path.join(d, "Mods"), os.path.join(d, "Version.txt")


def walk_build(root, mod, savegame, host=None, mods_dir=None, version_txt=None, cache_dir=None, *, deploy_stamp=False):
    """The build he will walk: {game, mod_hash, game_build, active_mods, why[]} (why non-empty: unreadable here).
    The Dispatch forecast can use the composed deploy's stamp. The game version and save are read live."""
    sp = os.environ.get(STANDIN_ENV)
    if sp:
        with open(sp, encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("game", WALK_HOST)
        d["standin"] = sp
        d["why"] = [w for w in (None if d.get(k) else "the stand-in names no %s" % k for k in REQUIRED) if w]
        if _standin_refused(root):
            # selftests read temp trees; a stand-in left in a shell's environment must not pass a live exit
            d["why"].append("%s=%s is set while reading the repo checkout %s; a stand-in counts only for a test tree: "
                            "unset it" % (STANDIN_ENV, sp, root))
        return d
    out = {"game": (host or socket.gethostname()).strip().lower(), "why": []}
    if _foreign_checkout(root):
        out["why"].append("%s is another checkout: its walk build and tier lists are read by its own build_match.py "
                          "(this one's modset_builder and readers are %s's)" % (root, REPO))
        return out
    if WALK_HOST and out["game"] != WALK_HOST:
        out["why"].append("the walk build is read on %s, where he walks; this is %s" % (WALK_HOST, out["game"]))
        return out
    if mods_dir is None or version_txt is None:
        m, v = walk_paths(savegame)
        mods_dir, version_txt = mods_dir or m, version_txt or v
    out["walk_game"] = walk_letter(savegame)
    _, folder = _mod_folder(root, mod, mods_dir)
    out["deployed_folder"] = folder
    stamped = _stamped_hash(folder) if deploy_stamp and folder else None
    if stamped:
        out["deploy_stamp"] = _deploy_stamp(folder)
    out["mod_hash"], err = (stamped, None) if stamped else deployed_hash_why(folder, cache_dir=cache_dir)
    out["game_build"] = game_build(version_txt)
    if not out["mod_hash"]:
        out["why"].append("%s is not deployed in %s" % (mod, mods_dir) if err == "no folder"
                          else "%s is deployed, but %s; read it again" % (mod, err))
    if not out["game_build"]:
        out["why"].append("no game build read from %s" % version_txt)
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import modsconfig_from_save
    sv = str(savegame or "")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", sv)
    sv = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")) if m else sv
    if not sv or not os.path.isfile(sv):
        out["why"].append("the walk savegame %s is not on disk" % (savegame or "(none named)"))
    else:
        ids = modsconfig_from_save.mod_list(sv).get("modIds") or []
        out["active_mods"] = ids
        if not ids:
            out["why"].append("the walk savegame %s records no modIds" % savegame)
    return out


def tier_lister(walk, cache_dir=None):
    """-> f(tier) -> (ordered packageIds, None) or (None, why): the stand-in's tiers, else modset_builder's on this
    machine. Built fresh for each reading, never from a file: modset_builder reads more than its own source (each
    installed mod's About.xml, Biomes.compose.json), so no key short of a scan proves a kept list current. One scan()
    of the installed mods (~13 s) serves every tier in the reading. cache_dir is accepted and unused."""
    if walk.get("standin"):
        tiers = walk.get("tiers") or {}
        return lambda t: (list(tiers[t]), None) if t in tiers else (None, "the stand-in has no tier %s" % t)
    memo, installed = {}, []

    def f(t):
        if t not in memo:
            memo[t] = _resolve_tier(t, installed)
        return memo[t]
    scanned, seen = {}, {}

    def others(t):
        """The tier's list on each other install of this machine -> [(game, list or None, why)]: built only when a row's
        list is not this install's, one scan per install per reading."""
        if t not in seen:
            seen[t] = [(g, *_resolve_tier(t, scanned.setdefault(g, []), d)) for g, d in other_installs()]
        return seen[t]
    f.others = others
    return f


def other_installs():
    """-> [(game name, its Mods folder)] for this machine's game installs other than the one this process reads."""
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import game_instance
    import game_names
    here, out = os.path.realpath(_paths()[0]), []
    for game, _key, machine, letter in game_names.GAMES:
        d = os.path.join(game_instance.game_dir(letter), "Mods") if machine == WALK_HOST else ""
        if d and os.path.isdir(d) and os.path.realpath(d) != here:
            out.append((game, d))
    return out


def other_tier_match(tier, mods, tiers):
    """-> (game name whose install gives exactly this list for the tier, or None; what else was read, as text)."""
    said = []
    try:
        lists = (getattr(tiers, "others", None) or (lambda t: []))(tier)
    except Exception as e:                  # could not look is said, and counts nothing
        if could_not_look(e):
            raise
        return None, "; the other installs could not be read (%s: %s)" % (type(e).__name__, e)
    for g, ref, why in lists:
        if ref is not None and same_list(mods, ref):
            return g, ""
        said.append("on %s: %s" % (g, why if ref is None else _first_diff(mods, ref)))
    return None, "".join("; " + x for x in said)


def could_not_look(e):
    """True when e is a read that failed for want of kernel memory (modset_builder.AboutUnreadable is one): it ends by
    itself, and says nothing of what it read."""
    return isinstance(e, OSError) and e.errno == errno.ENOMEM


def _resolve_tier(t, installed, mods_dir=None):
    """installed: [] until the first tier of a reading scans; then [scan()] for the rest of it. mods_dir: another
    install's Mods folder."""
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import modset_builder as MB
    try:
        if MB.tier_def(t) is None:
            return None, "modset_builder has no tier %s" % t
        if not installed:
            installed.append(MB.scan(mods_dir) if mods_dir else MB.scan())
        ordered, missing, refusals = MB.resolve_tier(t, installed[0])
        if missing or refusals:
            return None, "modset_builder refuses tier %s: %s" % (t, "; ".join(map(str, (missing and [
                "missing %s" % ", ".join(missing)] or []) + list(refusals or []))))
        return list(ordered), None
    except MB.AboutUnreadable:              # could not look: no reading, never "this row does not count"
        raise
    except Exception as e:                  # a tier that cannot be built gives no list; the row does not count
        return None, "modset_builder could not build tier %s (%s: %s)" % (t, type(e).__name__, e)


# ---- the comparison --------------------------------------------------------------------------------------------------

def is_full(test):
    """A full-list check: its why_full_list says why, or the test table gives it kind live_full (sc_walk carries only the kind)."""
    return bool((test or {}).get("why_full_list")) or (test or {}).get("kind") == "live_full"


def _first_diff(a, b):
    a, b = norm_list(a), norm_list(b)
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "(end)"
        y = b[i] if i < len(b) else "(end)"
        if x != y:
            return "at position %d the row has %s, the reference %s (row %d mods, reference %d)" % (
                i + 1, x, y, len(a), len(b))
    return "none"


def _list_why(mods, label):
    if isinstance(mods, (list, tuple)) and not mods:
        return "the %s mod list (active_mods) is empty" % label
    if not isinstance(mods, (list, tuple)) or any(not isinstance(p, str) or not norm_pid(p) for p in mods):
        return "the %s mod list (active_mods) cannot be read" % label
    return None


def mod_list_relation(root, mod):
    """Read the mod-list relation on demand. A check or scene names extra package IDs in `mods`; none named,
    it reads what the mod itself reads (its small list holds every mod that it patches or requires)."""
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import small_list as SL

    @cache
    def scenes():
        path = os.path.join(root, "design", "concepts", mod, "scenes.json")
        if not os.path.exists(path):        # a mod with no scenes file names no scene reads
            return {}
        with open(path, encoding="utf-8") as f:
            return {s["id"]: s for s in json.load(f)["scenes"]}

    @cache
    def common():
        folder = SL.mod_dir(root, mod)
        pid = _first_package_id(os.path.join(folder, "About", "About.xml"))
        if not pid:
            raise SL.CouldNotLook("About.xml names no readable packageId")
        need = SL.needs(folder)
        small = SL.load_spec(root, mod)
        ids = {pid, *norm_list(small.get("also", {}) if small is not None else ())}
        names = {n.lower() for kind, k in need if kind == "name" for n in k.split("\n")}
        if names:
            by_name = {"core": {"ludeon.rimworld"}, **{p.rsplit(".", 1)[1]: {p} for p in SL.DLC}}
            for p, rec in SL.with_our_names(SL.scan(), root).items():
                by_name.setdefault(rec["name"].strip().lower(), set()).add(norm_pid(p))
            if names - by_name.keys():
                raise SL.CouldNotLook("no packageId for patch target(s) %s" % ", ".join(sorted(names - by_name.keys())))
            ids.update(p for n in names for p in by_name[n])
        ids.update(p for kind, k in need if kind != "name" for p in k.split(","))
        comp = composed_into(root, mod)
        if comp == COMPOSE_UNREADABLE:
            raise SL.CouldNotLook("Biomes.compose.json")
        if comp:
            ids.add(comp[0])
        return ids

    def compare_lists(test, spec, old, new):
        why = _list_why(old, "old") or _list_why(new, "new")
        if why:
            return False, why
        if same_list(old, new):
            return True, ""
        before, after = set(norm_list(old)), set(norm_list(new))
        left, joined = before - after, after - before
        if not (left or joined):
            return False, "the mod list order differs: %s" % _first_diff(old, new)
        try:
            scene = scenes().get(test, {})
            lists = [s["mods"] for s in (spec, scene) if "mods" in s]
            if any(not isinstance(xs, list) or any(not isinstance(p, str) or not norm_pid(p) for p in xs)
                   for xs in lists):
                return False, "the check or scene's mod read list cannot be read"
            reads = common() | {norm_pid(p) for xs in lists for p in xs}
        except (OSError, ValueError, KeyError, TypeError, SL.CouldNotLook) as e:
            if could_not_look(e):
                raise
            return False, "the mod read list cannot be read: %s" % e
        hit = ["%s %s" % (", ".join(sorted(reads & diff)), verb) for diff, verb in ((left, "left"), (joined, "joined"))
               if reads & diff]
        return ((False, "; ".join(hit) + " the mod list") if hit else
                (True, "; the mod list changed outside what this check reads"))
    return compare_lists


def planned_list_owed(root, mod, tests, last, new):
    """List changes from the published tier definitions can be read before there is a new walk save."""
    if not new:
        return {}
    git = RR.Git(root)
    small = "design/concepts/%s/version/small_list.json" % mod
    out, tiers = {}, None
    for t, spec in tests:
        r = last.get(t) or {}
        old = git.rev(r.get("mod_sha"))
        if not old or old == new:
            continue
        changed = git.changed(old, new, [small])     # not modset_builder.py: a tier's list costs 13 s a tick, Stage 6 reads it
        if changed is None:
            out[t] = "git cannot read the change to the mod list definitions"
            continue
        tier = spec.get("tier") or r.get("tier")
        if not changed and (is_full(spec) or not r.get("tier") or tier == r["tier"]):
            continue
        if is_full(spec):
            raw = git.show(new, small)
            if raw is None and small not in changed:
                continue                    # full-list check without a configured walk tier
            try:
                tier = json.loads(raw)["tier"]
            except (TypeError, ValueError, KeyError):
                out[t] = "the new mod list cannot be read from small_list.json"
                continue
        if tiers is None:
            tiers, lists = tier_lister({}), mod_list_relation(root, mod)
        ref, why = tiers(tier) if tier else (None, "the check and its row name no tier")
        if ref is None:
            out[t] = "the new mod list cannot be read: %s" % why
            continue
        mods = r.get("active_mods")
        if not is_full(spec) and not _list_why(mods, "old") and not same_list(mods, ref):
            game, _ = other_tier_match(tier, mods, tiers)
            if game:
                continue
        counts, why = lists(t, spec, mods, ref)
        if not counts:
            out[t] = why
    return out


def judge_row(test, spec, r, walk, tiers, relation=None, deploy=None):
    """-> (counts, why) for one check's last row. relation: rerun_relation.relate's reading; a row whose mod hash
    differs from the walk's counts only when it reads this check untouched. deploy (the walk folder is not the current
    source): a row on the folder's own hash is judged by the relation to the source too, never counted on a stale
    folder (GimmeSomeSlack visit 1, 2026-11-23: 206 count, 0 to run, with 206 touched)."""
    if walk.get("why"):
        return False, "the walk build is unreadable, so nothing counts yet: %s" % "; ".join(walk["why"])
    if not r:
        return False, "no row for this check"
    lists = (relation or {}).get("mod_lists")
    if lists:
        why = _list_why(r.get("active_mods"), "old")
        if why:
            return False, why
    for f in REQUIRED:
        if not r.get(f):
            return False, "the row records no %s (run `build_match.py identity` and merge it into the row)" % f
    carried = ""
    if r.get("game_build") != walk.get("game_build"):
        return False, "the game build differs: the row ran on %s, he walks %s" % (r.get("game_build"),
                                                                                  walk.get("game_build"))
    if deploy and r.get("mod_hash") == walk.get("mod_hash"):
        rel = ((relation or {}).get("rows") or {}).get(test) or {}
        if rel.get("state") == "touched":
            return False, "the walk folder is stale, and the change since %s to the source touches it: %s" % (
                rel.get("old"), rel["why"])
        if rel.get("state") == "unreadable":
            return False, "the walk folder is stale, and no readable change relation (%s): declare what it exercises" % (
                rel["why"])
    if r.get("mod_hash") != walk.get("mod_hash"):
        rel = ((relation or {}).get("rows") or {}).get(test)
        if not rel:
            return False, "the mod hash differs (the row ran on %s, he walks %s) and no change relation was read" % (
                r.get("mod_hash"), walk.get("mod_hash"))
        if rel["state"] == "touched":
            return False, "the change since %s touches it: %s" % (rel.get("old"), rel["why"])
        if rel["state"] == "unreadable":
            return False, "no readable change relation (%s): declare what it exercises" % rel["why"]
        carried = "; made on %s, and the change since touches nothing it reads or exercises" % rel.get("old")
    if is_full(spec):
        ref = walk.get("active_mods")
        if lists:
            counts, why = lists(test, spec, r["active_mods"], ref)
            if not counts:
                return False, why
            carried += why
        elif not same_list(r.get("active_mods"), ref):
            return False, "a full-list test whose list is not his walk's: %s" % _first_diff(
                r.get("active_mods"), ref)
        return True, "game build and his walk's full list (%d mods)%s" % (len(ref), carried)
    tier = spec.get("tier") or r.get("tier")
    if not tier:
        return False, "a minimal-list test whose row names no tier"
    if not lists and spec.get("tier") and r.get("tier") and spec["tier"] != r["tier"]:
        return False, "the row ran on tier %s; the test table names tier %s" % (r["tier"], spec["tier"])
    ref, why = tiers(tier)
    if ref is None:
        return False, "tier %s gives no list: %s" % (tier, why)
    if lists:
        bad = _list_why(ref, "new")
        if bad:
            return False, bad
    if not same_list(r.get("active_mods"), ref):
        game, said = other_tier_match(tier, r.get("active_mods"), tiers)
        if game:
            ref, carried = r["active_mods"], "%s; the list as %s's install gives it" % (carried, game)
        elif lists:
            counts, why = lists(test, spec, r["active_mods"], ref)
            if not counts:
                return False, why + said
            carried += why
        else:
            return False, "a minimal-list test whose list is not tier %s's: %s%s" % (tier, _first_diff(
                r.get("active_mods"), ref), said)
    return True, "game build and tier %s's list (%d mods)%s%s" % (
        tier, len(ref), "" if spec.get("tier") else "; tier named by the row, the test table names none", carried)


def compare(tests, last_rows, walk, tiers, relation=None, deploy=None):
    """tests: [(id, spec)]; last_rows: {id: the last row or None}; relation: rerun_relation.relate's reading; deploy:
    the one act owed when the walk folder is not the current source (None when it is). -> {rows: {id: {counts, why,
    full}}, read, count, rerun, worst, deploy, undeclared, unreadable}."""
    out = {"rows": {}, "rerun": [], "worst": None, "standin": walk.get("standin"), "walk_why": list(walk.get("why") or []),
           "walk": {k: walk.get(k) for k in ("game", "mod_hash", "game_build", "active_mods", "standin")},
           "deploy": deploy, "undeclared": list((relation or {}).get("undeclared") or []),
           "unreadable": list((relation or {}).get("unreadable") or []), "new": (relation or {}).get("new")}
    if walk.get("deploy_stamp"):
        out["walk"]["deploy_stamp"] = walk["deploy_stamp"]
    for t, spec in tests:
        ok, why = judge_row(t, spec, last_rows.get(t), walk, tiers, relation, deploy)
        # relation: what the source change relation says of the row (None: not read); walk_owed reads it
        out["rows"][t] = {"counts": ok, "why": why, "full": is_full(spec),
                          "relation": (((relation or {}).get("rows") or {}).get(t) or {}).get("state")}
        if not ok:
            out["rerun"].append(t)
            out["worst"] = out["worst"] or "%s: %s" % (t, why)
    out["read"] = len(tests)
    out["count"] = out["read"] - len(out["rerun"])
    known = {t for t, _ in tests}
    out["unmatched"] = sum(len(v) if k == "" else 1 for k, v in last_rows.items() if k not in known)
    return out


def summary(res):
    names = res["rerun"][:24]
    return "build match: read %d case(s), %d count, %d to run (%s)%s%s; limit: %s; worst: %s%s%s" % (
        res["read"], res["count"], len(res["rerun"]), ", ".join(names) + (
            " and %d more" % (len(res["rerun"]) - len(names)) if len(res["rerun"]) > len(names) else "") or "none",
        "; owed first: %s" % res["deploy"] if res.get("deploy") else "",
        "; %d changed file(s) no check declares (%s)" % (len(res["undeclared"]), ", ".join(res["undeclared"][:6]))
        if res.get("undeclared") else "",
        LIMIT, res["worst"] or "none (every one counts)",
        "; %d row(s) name no check in the test table (read, not counted)" % res["unmatched"]
        if res.get("unmatched") else "",
        "; walk from stand-in %s" % res["standin"] if res.get("standin") else "")


def last_rows(rows):
    """{check id: its last row}; rows naming no check are kept as a list under "" so a reading can count them."""
    out = {}
    for r in rows or []:
        t = r.get("test") or r.get("id")
        if t:
            out[t] = r
        else:
            out.setdefault("", []).append(r)
    return out


def carried_rows(root, mod, n=None):
    """{check id: its deciding row}: visit n's last row for each check it ran, else the last row of the latest earlier
    visit that ran it (a row is carried with `_visit` naming its visit). A spoiled run speaks for nobody, so its row never
    replaces one that is not spoiled (live_kinds.later; owner, 2026-11-23). n None: the latest visit on disk. Rows naming
    no check are kept as a list under "" (visit n's only)."""
    import maturation as M
    have = M.visit_numbers(root, mod) or []
    n = n or (have[-1] if have else 1)
    out = {}
    for k in sorted(v for v in have if v <= n):
        rows = M._jsonl(os.path.join(M.mod_dir(root, mod), M.INGAME_DIR, "visit_%d" % k, "rows.jsonl")) or []
        for r in rows:
            t = r.get("test") or r.get("id")
            if t:
                out[t] = LK.later(out.get(t), dict(r, _visit=k))
            elif k == n:
                out.setdefault("", []).append(r)
    return out


def check_runs(root, mod, n=None):
    """{check id: [(visit, row)]}: every row of every visit up to n, in order (live_kinds.reading). A visit with no
    rows.jsonl yet has no rows; one that is there and cannot be read raises, since an UNRESOLVED run in it would be missed."""
    import maturation as M
    have = M.visit_numbers(root, mod)
    n = n or (have[-1] if have else 1)
    out = {}
    for k in sorted(v for v in have if v <= n):
        p = os.path.join(M.mod_dir(root, mod), M.INGAME_DIR, "visit_%d" % k, "rows.jsonl")
        if not os.path.exists(p):
            continue
        rows = M._jsonl(p)
        if rows is None:
            raise ValueError("visit_%d/rows.jsonl is there and cannot be read" % k)
        for r in rows:
            t = r.get("test") or r.get("id")
            if t:
                out.setdefault(t, []).append((k, r))
    return out


def srchash_files(folder):
    """{name: text} of every Assemblies/*.srchash under a mod folder; {} when there is none; None unreadable."""
    a = os.path.join(folder or "", "Assemblies")
    if not folder or not os.path.isdir(a):
        return {}
    try:
        out = {}
        for nm in sorted(os.listdir(a)):
            if nm.endswith(".srchash"):
                with open(os.path.join(a, nm), encoding="utf-8", errors="replace") as f:
                    out[nm] = f.read()
        return out
    except OSError:
        return None


def _file_sha256(path):
    """-> the sha256 of a file's bytes; None when there is no such file. A file that cannot be read raises: the Stage 6
    exit then reads refused by its cause, never met."""
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def walk_source(root, mod, walk):
    """-> (deploy, source): deploy None when the deployed walk folder's .srchash files equal the source's at HEAD (or
    the mod has none), else the one act owed: a deploy, named; source: the source commit the relation reads to."""
    sha = source_sha(root, mod)
    if walk.get("standin"):
        return walk.get("deploy"), walk.get("source_sha") or sha
    folder = walk.get("deployed_folder")
    if not folder:
        return None, sha
    comp = composed_into(root, mod)
    if comp and comp != COMPOSE_UNREADABLE:
        # a composed member's DLL stamp is deployed at Biomes/<key>/Assemblies; the shell's own Assemblies holds only
        # the shell's stamp (Pyrelands visit 2, 2026-11-21: read there, a deploy was owed forever)
        folder = os.path.join(folder, "Biomes", mod)
    inst = "" if walk.get("walk_game", "a") == "a" else " --instance %s" % _game_name(walk["walk_game"])
    dep = srchash_files(folder)
    src = srchash_files(os.path.join(root, "src", "RimMandrake", mod))
    if dep is None or src is None:
        return ("the walk folder's .srchash cannot be read (%s): deploy %s from the source at %s and read again" % (
            folder, mod, sha)), sha
    if src and dep != src:
        return ("the deployed walk folder %s is not the source at %s (its .srchash differs): deploy it "
                "(`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod %s%s --apply`); the deploy itself reruns no check"
                % (folder, sha, mod, inst)), sha
    # the stamps agree; the DLL beside each must be the one it names too: a deploy onto a running game wrote the new stamp
    # beside the old, locked DLL, and this read met (RIMMANDRAKE_KEEP_STAMP_OFF_A_DLL_THE_DEPLOY_COULD_NOT_WRITE)
    for nm in src:
        dll = nm[:-len(".srchash")]
        want = _file_sha256(os.path.join(root, "src", "RimMandrake", mod, "Assemblies", dll))
        if want and _file_sha256(os.path.join(folder, "Assemblies", dll)) != want:
            return ("the deployed walk folder %s holds the source's stamp at %s beside another %s, or none: deploy it "
                    "with the game down (`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod %s%s --apply`)"
                    % (folder, sha, dll, mod, inst)), sha
    return None, sha


def check_visit(root, mod, n, tt, savegame, cache_dir=CACHE_DIR, runner=None, *, deploy_stamp=False):
    """The reading maturation.py's Stage 6 exit makes: each check's last row (visit n's, else an earlier visit's)
    against the walk build, through the change relation. Dispatch can forecast against the last composed deploy."""
    import maturation as M
    last = carried_rows(root, mod, n)
    walk = walk_build(root, mod, savegame, cache_dir=cache_dir, deploy_stamp=deploy_stamp)
    tests = M.ingame_tests(tt)
    deploy, _ = walk_source(root, mod, walk) if not walk.get("why") else (None, None)
    kw = {"runner": runner} if runner else {}
    try:
        rel = RR.relate(root, mod, dict(tests), {t: r for t, r in last.items() if t}, compare_mod_lists=True, **kw)
    except Exception as e:      # a relation that cannot be read relates nothing: each changed row runs again
        rel = {"rows": {}, "undeclared": [], "unreadable": [], "error": "%s: %s" % (type(e).__name__, e)}
    rel["mod_lists"] = mod_list_relation(root, mod)
    return compare(tests, last, walk, tier_lister(walk, cache_dir), relation=rel, deploy=deploy)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("identity", help="the identity fields for one row, as one JSON line")
    a.add_argument("--mod", required=True)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--tier", help="the modset_builder tier the check ran on (a minimal-list test)")
    g.add_argument("--full", action="store_true", help="the check ran on his full list (its why_full_list says why)")
    a.add_argument("--mod-sha")
    a.add_argument("--root", default=REPO)
    d = sub.add_parser("loaded", help="what the RUNNING game loaded, against the deployed folder, the commit and the list")
    d.add_argument("--mod", required=True)
    d.add_argument("--receipt", help="a file holding jawa/running_mods' reply (loadedOf=ours), or - for stdin; else read it over the bridge")
    d.add_argument("--game", help="the game it must be (ArchSmall, ...): another game is WRONG_GAME")
    d.add_argument("--root", default=REPO)
    c = sub.add_parser("check", help="read a visit's rows against the walk build")
    c.add_argument("--mod", required=True)
    c.add_argument("--visit", type=int)
    c.add_argument("--root", default=REPO)
    args = ap.parse_args(argv)
    if args.cmd == "loaded":
        sys.path.insert(0, HERE) if HERE not in sys.path else None
        import game_names
        import loaded_build as LB
        try:
            if args.receipt:
                with (sys.stdin if args.receipt == "-" else open(args.receipt, encoding="utf-8")) as f:
                    reply = LB.unwrap(json.load(f))
            else:
                reply = LB.fetch(UTILS)
        except (OSError, ValueError) as e:
            reply = {"success": False, "message": "the receipt could not be read: %s" % e}
        out = LB.loaded(args.root, args.mod, reply, expected_game=game_names.key(args.game))
        print(json.dumps(out))
        return LB.EXIT.get(out["verdict"], 1)
    if args.cmd == "identity":
        out = identity(args.root, args.mod, tier=args.tier, full=args.full, mod_sha=args.mod_sha, cache_dir=CACHE_DIR)
        print(json.dumps(out))
        return 1 if out.get("why") else 0
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import maturation as M
    tt, _ = M.read_json(args.root, args.mod, "version/test_table.json")
    n = args.visit or (M.visit_numbers(args.root, args.mod) or [0])[-1]
    blk = M.ingame_exit_block(M.read_text(args.root, args.mod, "%s/visit_%d/SUMMARY.md" % (M.INGAME_DIR, n))) or {}
    res = check_visit(args.root, args.mod, n, tt, blk.get("savegame"))
    for t, x in res["rows"].items():
        if not x["counts"]:
            print("RERUN  %s%s: %s" % (t, " (full list)" if x["full"] else "", x["why"]))
    for f in res.get("undeclared") or []:
        print("UNDECLARED  %s: changed, and no check declares it" % f)
    if res.get("deploy"):
        print("DEPLOY  %s" % res["deploy"])
    print(summary(res))
    return 0 if not res["rerun"] and res["read"] and not res.get("deploy") else 1


if __name__ == "__main__":
    sys.exit(main())
