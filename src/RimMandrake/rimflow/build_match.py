#!/usr/bin/env python3
"""The BUILD MATCH: an in-game verdict counts only on the build he will walk. A program, no AI; run at the Stage 6 exit.

Owner, 2026-11-17, approving the Stage 6 -> Stage 7 change (item RIMMANDRAKE_FOLD_STAGE_SEVEN_INTO_WALK_BRIEF_NO_VETO;
spec design/specs/2026-11-13-maturation-pipeline.md, Stage 6 exit and Stage 7):
  every in-game verdict records the game, the mod's source sha, a hash of its deployed folder, the active mod list
  (ModsConfig.xml activeMods, parsed, in order) and the game build. A verdict whose mod hash or game build differs from
  the build he walks does not count; its check is re-run. A full-list test's list equals his walk's list exactly; a
  minimal-list test's list equals the list modset_builder.py builds for its tier from the same commit.

  python3 src/RimMandrake/rimflow/build_match.py identity --mod M (--tier T | --full) [--mod-sha SHA]
      one JSON line, the identity fields a live driver merges into each rows.jsonl row it writes (run it on the game
      machine, after the deploy and the list swap, before the check)
  python3 src/RimMandrake/rimflow/build_match.py check --mod M [--visit N]
      reads visit N's rows against the walk build (the labelled savegame its Exit block names, read on Archmagi):
      one line per check, then cases read, how many count, the limit and the worst; exit 0 only when every one counts

Where each piece comes from:
  mod hash     sha256 over the deployed folder's files (posix relative path, size, bytes; sorted), so a redeploy of the
               same bytes keeps it and one changed byte changes it. A mod composed into Baroque Biomes
               (src/RimMandrake/Biomes.compose.json, wave <= compose_wave) has no folder of its own: its hash is the
               Biomes folder's, so a change to any composed biome re-runs its checks (the safe side).
  game build   the first line of the game's Version.txt ("1.6.4871 rev590" measured 2026-11-17).
  walk list    the labelled savegame's <modIds>, in order: his walk loads that save (spec: the walk's list is read when
               the walk savegame is made). He walks on Archmagi (WALK_HOST), so the walk build is read there only.
  tier list    modset_builder.resolve_tier(tier, scan()) on this machine and this commit; a tier it refuses or that
               misses a mod gives no list, so the row does not count.
Packages compare lower-case with a trailing `_steam` dropped (RimWorld's own suffix for a Steam copy of a local mod).
MATURATION_WALK_BUILD names a JSON file that stands in for the live machine ({mod_hash, game_build, active_mods,
tiers: {name: [packageIds]}}); selftests use it, and every reading made with it names it.
"""
import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")

WALK_HOST = "archmagi"                       # he walks on Archmagi (spec Stage 8; GAMES in maturation.py)
STANDIN_ENV = "MATURATION_WALK_BUILD"
CACHE_DIR = "/mnt/d/ClaudeWork/rimmandrake/build_match"
CHECKED = ("mod_hash", "game_build")         # must equal the walk's
REQUIRED = ("mod_hash", "game_build", "active_mods")
WORDS = {"mod_hash": "mod hash", "game_build": "game build"}
LIMIT = "every check counts: its mod hash and game build equal the walk's, its list equals its reference list"


# ---- reading the machine ---------------------------------------------------------------------------------------------

def norm_pid(p):
    p = str(p or "").strip().lower()
    return p[:-len("_steam")] if p.endswith("_steam") else p


def norm_list(xs):
    return [norm_pid(x) for x in xs or []]


def same_list(a, b):
    return norm_list(a) == norm_list(b)


def _digest_file(path, h):
    with open(path, "rb") as f:
        size = os.fstat(f.fileno()).st_size
        h.update(b"%d\0" % size)
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)


def _files(folder):
    out = []
    for d, dirs, names in os.walk(folder):
        dirs.sort()
        for n in sorted(names):
            p = os.path.join(d, n)
            out.append((os.path.relpath(p, folder).replace(os.sep, "/"), p))
    return sorted(out)


def deployed_hash(folder, cache_dir=None):
    """sha256:<hex> over the folder's files, or None when there is no folder. With cache_dir, a hash is kept under a key
    of every file's path, size and mtime, so an unchanged folder is not read twice."""
    if not folder or not os.path.isdir(folder):
        return None
    files = _files(folder)
    key = None
    if cache_dir:
        sig = hashlib.sha256()
        for r, p in files:
            st = os.stat(p)
            sig.update(("%s\0%d\0%d\n" % (r, st.st_size, st.st_mtime_ns)).encode())
        key = os.path.join(cache_dir, "hash_%s.txt" % sig.hexdigest()[:32])
        try:
            with open(key) as f:
                got = f.read().strip()
            if got.startswith("sha256:"):
                return got
        except OSError:
            pass
    h = hashlib.sha256()
    for r, p in files:
        h.update(r.encode("utf-8") + b"\0")
        _digest_file(p, h)
    out = "sha256:" + h.hexdigest()
    if key:
        os.makedirs(cache_dir, exist_ok=True)
        with open(key, "w") as f:
            f.write(out + "\n")
    return out


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


def composed_into(root, mod):
    """(packageId, folder name) of Baroque Biomes when Biomes.compose.json composes `mod` into it; else None."""
    try:
        with open(os.path.join(root, "src", "RimMandrake", "Biomes.compose.json"), encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    cw = d.get("compose_wave", 0)
    if any(e.get("key") == mod and e.get("wave", 99) <= cw for e in d.get("entries") or ()):
        return norm_pid((d.get("about") or {}).get("packageId")), d.get("target")
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
    pid = mod_package_id(root, mod)
    comp = composed_into(root, mod)
    folder = deployed_folder(mods_dir, pid, mod)
    if folder is None and comp:
        folder = deployed_folder(mods_dir, comp[0], comp[1] or "")
    return pid, folder


def source_sha(root, mod):
    try:
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%h", "--", "src/RimMandrake/%s" % mod],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def identity(root, mod, tier=None, full=False, mods_dir=None, config=None, version_txt=None, host=None, mod_sha=None,
             cache_dir=None):
    """The fields a row records: game, mod_sha, mod_hash, game_build, active_mods, unit, and tier or full_list. `why`
    names what could not be read (a row with a missing field does not count)."""
    if None in (mods_dir, config, version_txt):
        m, c, v = _paths()
        mods_dir, config, version_txt = mods_dir or m, config or c, version_txt or v
    why = []
    pid, folder = _mod_folder(root, mod, mods_dir)
    h = deployed_hash(folder, cache_dir=cache_dir)
    if h is None:
        why.append("%s is not deployed in %s (no folder whose About.xml names %s): deploy it first" % (
            mod, mods_dir, pid or "its packageId"))
    am = active_mods(config)
    if not am:
        why.append("no activeMods read from %s" % config)
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
    else:
        out["tier"] = tier
    if why:
        out["why"] = why
    return out


def walk_build(root, mod, savegame, host=None, mods_dir=None, version_txt=None, cache_dir=None):
    """The build he will walk: {game, mod_hash, game_build, active_mods, why[]} (why non-empty: unreadable here)."""
    sp = os.environ.get(STANDIN_ENV)
    if sp:
        with open(sp, encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("game", WALK_HOST)
        d["standin"] = sp
        d["why"] = [w for w in (None if d.get(k) else "the stand-in names no %s" % k for k in REQUIRED) if w]
        return d
    out = {"game": (host or socket.gethostname()).strip().lower(), "why": []}
    if WALK_HOST and out["game"] != WALK_HOST:
        out["why"].append("the walk build is read on %s, where he walks; this is %s" % (WALK_HOST, out["game"]))
        return out
    if mods_dir is None or version_txt is None:
        m, _, v = _paths()
        mods_dir, version_txt = mods_dir or m, version_txt or v
    _, folder = _mod_folder(root, mod, mods_dir)
    out["mod_hash"] = deployed_hash(folder, cache_dir=cache_dir)
    out["game_build"] = game_build(version_txt)
    if not out["mod_hash"]:
        out["why"].append("%s is not deployed in %s" % (mod, mods_dir))
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
    machine (scan() of the installed mods, ~13 s; kept under cache_dir keyed on modset_builder.py and the Mods listing)."""
    if walk.get("standin"):
        tiers = walk.get("tiers") or {}
        return lambda t: (list(tiers[t]), None) if t in tiers else (None, "the stand-in has no tier %s" % t)
    memo = {}

    def f(t):
        if t not in memo:
            memo[t] = _resolve_tier(t, cache_dir)
        return memo[t]
    return f


def _resolve_tier(t, cache_dir):
    sys.path.insert(0, UTILS) if UTILS not in sys.path else None
    import modset_builder as MB
    key = None
    if cache_dir:
        sig = hashlib.sha256(open(MB.__file__, "rb").read())
        try:
            sig.update("\n".join(sorted(os.listdir(MB.LOCAL_MODS))).encode())
        except OSError:
            pass
        sig.update(t.encode())
        key = os.path.join(cache_dir, "tier_%s.json" % sig.hexdigest()[:32])
        try:
            with open(key) as f:
                d = json.load(f)
            return d["list"], d["why"]
        except (OSError, ValueError, KeyError):
            pass
    try:
        if MB.tier_def(t) is None:
            res = (None, "modset_builder has no tier %s" % t)
        else:
            ordered, missing, refusals = MB.resolve_tier(t, MB.scan())
            res = (None, "modset_builder refuses tier %s: %s" % (t, "; ".join(map(str, (missing and [
                "missing %s" % ", ".join(missing)] or []) + list(refusals or []))))) if missing or refusals \
                else (list(ordered), None)
    except Exception as e:                  # a tier that cannot be built gives no list; the row does not count
        res = (None, "modset_builder could not build tier %s (%s: %s)" % (t, type(e).__name__, e))
    if key:
        os.makedirs(cache_dir, exist_ok=True)
        with open(key, "w") as f:
            json.dump({"list": res[0], "why": res[1]}, f)
    return res


# ---- the comparison --------------------------------------------------------------------------------------------------

def is_full(test):
    return bool((test or {}).get("why_full_list"))


def _first_diff(a, b):
    a, b = norm_list(a), norm_list(b)
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "(end)"
        y = b[i] if i < len(b) else "(end)"
        if x != y:
            return "at position %d the row has %s, the reference %s (row %d mods, reference %d)" % (
                i + 1, x, y, len(a), len(b))
    return "none"


def judge_row(test, spec, r, walk, tiers):
    """-> (counts, why) for one check's last row."""
    if walk.get("why"):
        return False, "the walk build is unreadable, so nothing counts yet: %s" % "; ".join(walk["why"])
    if not r:
        return False, "no row for this check"
    for f in REQUIRED:
        if not r.get(f):
            return False, "the row records no %s (run `build_match.py identity` and merge it into the row)" % f
    for f in CHECKED:
        if r.get(f) != walk.get(f):
            return False, "the %s differs: the row ran on %s, he walks %s" % (WORDS[f], r.get(f), walk.get(f))
    if is_full(spec):
        if not same_list(r.get("active_mods"), walk.get("active_mods")):
            return False, "a full-list test whose list is not his walk's: %s" % _first_diff(
                r.get("active_mods"), walk.get("active_mods"))
        return True, "mod hash, game build and his walk's full list (%d mods)" % len(walk["active_mods"])
    tier = spec.get("tier") or r.get("tier")
    if not tier:
        return False, "a minimal-list test whose row names no tier"
    if spec.get("tier") and r.get("tier") and spec["tier"] != r["tier"]:
        return False, "the row ran on tier %s; the test table names tier %s" % (r["tier"], spec["tier"])
    ref, why = tiers(tier)
    if ref is None:
        return False, "tier %s gives no list: %s" % (tier, why)
    if not same_list(r.get("active_mods"), ref):
        return False, "a minimal-list test whose list is not tier %s's: %s" % (tier, _first_diff(
            r.get("active_mods"), ref))
    return True, "mod hash, game build and tier %s's list (%d mods)" % (tier, len(ref))


def compare(tests, last_rows, walk, tiers):
    """tests: [(id, spec)]; last_rows: {id: the last row or None}. -> {rows: {id: {counts, why, full}}, read, count,
    rerun, worst}."""
    out = {"rows": {}, "rerun": [], "worst": None, "standin": walk.get("standin"), "walk_why": list(walk.get("why") or [])}
    for t, spec in tests:
        ok, why = judge_row(t, spec, last_rows.get(t), walk, tiers)
        out["rows"][t] = {"counts": ok, "why": why, "full": is_full(spec)}
        if not ok:
            out["rerun"].append(t)
            out["worst"] = out["worst"] or "%s: %s" % (t, why)
    out["read"] = len(tests)
    out["count"] = out["read"] - len(out["rerun"])
    return out


def summary(res):
    return "build match: read %d case(s), %d count, %d to re-run; limit: %s; worst: %s%s" % (
        res["read"], res["count"], len(res["rerun"]), LIMIT, res["worst"] or "none (every one counts)",
        "; walk from stand-in %s" % res["standin"] if res.get("standin") else "")


def last_rows(rows):
    out = {}
    for r in rows or []:
        t = r.get("test") or r.get("id")
        if t:
            out[t] = r
    return out


def check_visit(root, mod, n, tt, savegame, cache_dir=CACHE_DIR):
    """The reading maturation.py's Stage 6 exit makes: the visit's last rows against the walk build."""
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import maturation as M
    rows = M._jsonl(os.path.join(M.mod_dir(root, mod), M.INGAME_DIR, "visit_%d" % n, "rows.jsonl")) or []
    walk = walk_build(root, mod, savegame, cache_dir=cache_dir)
    return compare(M.ingame_tests(tt), last_rows(rows), walk, tier_lister(walk, cache_dir))


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
    c = sub.add_parser("check", help="read a visit's rows against the walk build")
    c.add_argument("--mod", required=True)
    c.add_argument("--visit", type=int)
    c.add_argument("--root", default=REPO)
    args = ap.parse_args(argv)
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
        print("%s  %s%s: %s" % ("ok  " if x["counts"] else "RERUN", t, " (full list)" if x["full"] else "", x["why"]))
    print(summary(res))
    return 0 if not res["rerun"] and res["read"] else 1


if __name__ == "__main__":
    sys.exit(main())
