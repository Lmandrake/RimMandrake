#!/usr/bin/env python3
r"""extract_bundle_textures.py — make bundled art visible to the offline tools.

WHY THIS EXISTS
===============
The contact sheets and the review page resolve a def's `texPath` by looking for
a loose PNG on disk. About 30% of every category came back `no_loose_png`, and
that was read as "missing art". It is not: RimWorld 1.6 gave AssetBundles
first-class support, and the base game's expansions (Royalty, Ideology, Biotech,
Anomaly, Odyssey) plus a growing number of mods ship their textures compiled
into a Unity bundle that `find -name '*.png'` cannot see. The art exists, the
game draws it, only our scanner is blind.

This script walks every AssetBundle in the active load set AND in the game's own
`Data/<Expansion>/AssetBundles/`, extracts every Texture2D to a PNG cache, and
writes an index CSV the sheet tooling consults when the loose ladder misses.

🔴 RUN IT UNDER WINDOWS `python.exe`, NOT WSL `python3`.
UnityPy is installed on the Windows interpreter; PEP 668 blocks pip on the WSL
one. Relative paths work from the repo root:

    python.exe src/RimMandrake/Utils/extract_bundle_textures.py

THE MATCH IS BY CONTAINER PATH, NOT BY NAME
===========================================
`m_Name` is NOT unique inside a bundle, and not nearly. Measured across the live
load set: 60 textures are called `Apparel`, 27 `Head`; the Outer Rim Galactic
Empire bundle alone ships 42 called `Apparel`, because RimWorld apparel art is
`<Mod>/Textures/OuterRim/Apparel/<Set>/<Piece>/Apparel.png` — the piece is the
DIRECTORY and the file is always literally `Apparel`. Matching a def's texPath
on its last segment therefore made every Imperial garment resolve to the same
sprite, and (index.csv being sorted by name) usually one from a different mod.

UnityPy 1.25 does expose the missing half: `obj.container` on a Texture2D reads
back the bundle's own asset path,

    assets/data/neronix17.outerrim.galacticempire/textures/
        outerrim/apparel/imperialarmy/cuirass/apparel_fat_east.png

which is `texPath` plus a suffix, lowercased, under a boilerplate
`assets/data/<something>/` prefix. That is enough to match by PATH. It is
present for every AssetBundle; it is NOT present in the game player's own
`resources.assets` (all 3,469 Core textures come back with `container=None`),
so the m_Name fallback stays, and for Core it is safe because the resolver
prefers a texture from the def's own mod.

OUTPUT
======
    observed/inventory/bundle_textures/<sourceKey>/<container path>.png
    observed/inventory/bundle_textures/index.csv
        sourceKey,m_Name,container,file,width,height
    observed/inventory/bundle_textures/manifest.json   per-bundle mtime/size + rows

The on-disk layout mirrors the container path (minus the `assets/data/<x>/`
prefix, purely to stay under Windows' 260-char path limit) so that two textures
called `Apparel` land in different directories instead of racing for one name.
`container` is the column the resolver matches on; `m_Name` is kept because it
is all a `resources.assets` object has.

INCREMENTAL
===========
A bundle whose (mtime, size) matches the manifest is skipped whole — its rows
are replayed from the manifest into index.csv. A re-run with nothing changed
costs a stat() per bundle and a manifest rewrite. `--force` re-extracts.

The PNG cache lives under `observed/inventory/`, which is gitignored. It is a
derived artifact: regenerate it, never commit it.
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import MODS_CONFIG, WORKSHOP, LOCAL_MODS, GAME_DATA  # noqa: E402
from rimworld_loadset import build_load_set  # noqa: E402

VERSION = "2.0"

# Manifest row format. v1 rows are (m_Name, file, w, h) and carry no container,
# so a v1 record is treated as stale and its bundle re-extracted.
ROW_FMT = 2

REPO_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DEFAULT_OUT = os.path.join(REPO_ROOT, "observed", "inventory", "bundle_textures")

INDEX_NAME = "index.csv"
MANIFEST_NAME = "manifest.json"
INDEX_COLS = ["sourceKey", "m_Name", "container", "file", "width", "height"]

# Longest absolute path we will write. Windows refuses at 260 unless long paths
# are enabled machine-wide, and a container path can be deep; anything over this
# is flattened to <m_Name>__<hash>.png instead of being silently lost.
MAX_ABS_PATH = 230

# Files that sit next to a bundle and are not one.
SKIP_EXT = (".manifest", ".meta", ".json", ".txt", ".md", ".xml", ".dll")
# Every Unity bundle container starts with one of these.
MAGIC = (b"UnityFS", b"UnityWeb", b"UnityRaw", b"UnityArchive")


# ------------------------------------------------------------------ discovery
def is_bundle(path):
    """Cheap magic-byte test. A `.manifest` sitting beside a bundle is text."""
    if path.lower().endswith(SKIP_EXT):
        return False
    try:
        with open(path, "rb") as fh:
            head = fh.read(16)
    except OSError:
        return False
    return any(head.startswith(m) for m in MAGIC)


def bundles_under(base):
    """Every bundle file inside `<base>/AssetBundles/` (recursively)."""
    root = os.path.join(base, "AssetBundles")
    if not os.path.isdir(root):
        return []
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            if is_bundle(p):
                out.append(p)
    return out


def player_resources(data_dir):
    """
    The game player's own serialized asset files — NOT AssetBundles.

    🔴 Core ships no `Textures/` and no `AssetBundles/`. Look in
    `RimWorld/Data/Core/` and you find About, Defs, Languages and nothing else:
    every base-game texture (assault rifle, bows, mortars, ~3,470 of them) is
    compiled into the Unity player at
    `RimWorld/RimWorldWin64_Data/resources.assets`. Scanning only mod bundles
    and `Data/<Expansion>/AssetBundles/` leaves the whole of Core blank, which
    was 41 of the 61 weapons still missing on the first pass.

    UnityPy reads these exactly like a bundle; only the discovery differs, since
    a serialized file has no `UnityFS` magic and `is_bundle` rejects it.
    Attributed to sourceKey `ludeon.rimworld.core`, because that is the mod the
    defs asking for these names belong to.
    """
    install = os.path.dirname(os.path.normpath(data_dir))   # .../common/RimWorld
    out = []
    try:
        entries = sorted(os.listdir(install))
    except OSError:
        return out
    for e in entries:
        d = os.path.join(install, e)
        if not (e.lower().endswith("_data") and os.path.isdir(d)):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.lower().endswith(".assets"):
                out.append(os.path.join(d, fn))
    return out


def sanitize(key):
    return "".join(c if (c.isalnum() or c in "._-") else "_" for c in key).strip("_")


def discover_sources(config, workshop, local, data, quiet=False, inactive=False):
    """
    [(sourceKey, label, [bundle paths])] over the active load set plus the
    game's own Data/ tree.

    The mod side reads contentDirs (the LoadFolders-resolved folders) plus the
    mod root plus its immediate subdirectories: a bundle mod usually puts the
    bundle at `<mod>/<version>/AssetBundles/`, which contentDirs already covers,
    but a mod with a LoadFolders.xml that does not list the version folder still
    ships one, and one listdir is cheaper than being wrong.

    The Data/ tree is scanned unconditionally, not only for expansions that are
    active: a sheet built against a load set that omits Royalty still benefits
    from having Royalty's names in the cache, and the cost is five stat calls.
    """
    seen_bundle = set()
    sources = []

    mods, missing, version = build_load_set(config, [workshop, local, data])
    if not quiet:
        print("load set: version %s, %d active mods (%d unresolved)"
              % (version, len(mods), len(missing)))

    for m in mods:
        bases = list(m.get("contentDirs") or [])
        if m["folder"] not in bases:
            bases.append(m["folder"])
        try:
            bases += [os.path.join(m["folder"], e)
                      for e in os.listdir(m["folder"])
                      if os.path.isdir(os.path.join(m["folder"], e))]
        except OSError:
            pass
        found = []
        for b in dict.fromkeys(bases):
            for p in bundles_under(b):
                if p not in seen_bundle:
                    seen_bundle.add(p)
                    found.append(p)
        if found:
            sources.append((sanitize(m["packageId"] or m["name"]), m["name"], found))

    # Mods on disk but NOT active. Off by default — but the load set churns
    # under us (a mod deactivated between two sheet runs takes its art with it),
    # and a name-keyed cache entry for an inactive mod is inert: nothing looks
    # it up unless a def in the sheet asks for that exact name.
    if inactive:
        for root_dir in (workshop, local):
            if not os.path.isdir(root_dir):
                continue
            for e in sorted(os.listdir(root_dir)):
                d = os.path.join(root_dir, e)
                if not os.path.isdir(d):
                    continue
                found = []
                bases = [d] + [os.path.join(d, x) for x in os.listdir(d)
                               if os.path.isdir(os.path.join(d, x))]
                for b in bases:
                    for p in bundles_under(b):
                        if p not in seen_bundle:
                            seen_bundle.add(p)
                            found.append(p)
                if found:
                    got = None
                    try:
                        from rimworld_loadset import read_about
                        got = read_about(d)
                    except Exception:
                        pass
                    pid = got[0] if got else ("inactive." + e)
                    nm = got[1] if got else e
                    sources.append((sanitize(pid), nm + " [inactive]", found))

    if os.path.isdir(data):
        for e in sorted(os.listdir(data)):
            d = os.path.join(data, e)
            if not os.path.isdir(d):
                continue
            found = [p for p in bundles_under(d) if p not in seen_bundle]
            for p in found:
                seen_bundle.add(p)
            if found:
                sources.append((sanitize("ludeon.rimworld." + e.lower()), e, found))

    core = [p for p in player_resources(data) if p not in seen_bundle]
    if core:
        seen_bundle.update(core)
        sources.append(("ludeon.rimworld.core", "Core (player resources)", core))

    return sources


# ------------------------------------------------------------------ extraction
def container_of(obj):
    """
    The bundle-internal asset path of one object, or "".

    UnityPy 1.25 hangs this off the ObjectReader (`obj.container`), sourced from
    the serialized file's container map — NOT off the parsed Texture2D, where
    `container` and `assetPath` are both absent. Verified on this build: 697/697
    on an Outer Rim bundle, 522/522 on Royalty, 0/3469 on `resources.assets`.
    """
    try:
        return (getattr(obj, "container", None) or "").replace("\\", "/").strip("/")
    except Exception:
        return ""


def rel_for(container, name):
    """
    Repo-relative-ish file path (no extension) for one texture, from its
    container path, falling back to `m_Name` when there is none.

    Two deliberate edits to the container path:

      * the trailing `.png` / `.psd` Unity kept is dropped, because the def's
        texPath is extension-less and the resolver compares the two.
      * a leading `assets/data/<x>/` is dropped. It is boilerplate — every
        RimWorld bundle has it, and `<x>` is the packageId for a mod but the
        expansion name for Royalty/Biotech, so it carries nothing the sourceKey
        does not. Dropping it buys ~40 characters against Windows' path limit.
    """
    p = (container or "").strip("/")
    if p:
        stem, dot, ext = p.rpartition(".")
        if dot and stem and "/" not in ext and len(ext) <= 5:
            p = stem
        segs = [sanitize(s) for s in p.split("/") if s not in ("", ".", "..")]
        if segs and segs[0].lower() == "assets":
            segs = segs[1:]
            if len(segs) >= 2 and segs[0].lower() == "data":
                segs = segs[2:]
        segs = [s for s in segs if s]
        if segs:
            return "/".join(segs)
    return sanitize(name) or "texture"


def extract_bundle(path, out_dir, taken):
    """
    [(m_Name, container, relfile, w, h)] for every Texture2D in one bundle.

    `taken` is the set of relative paths already written for this sourceKey. Two
    objects can still land on one path — a bundle carrying both a texture and
    its atlas entry, or two containerless objects sharing an m_Name — and they
    are disambiguated (`name~2.png`), never overwritten. Nothing is dropped.

    NEVER raises on one bad object: a bundle is thousands of objects and one
    undecodable sprite must cost one row, not the run.
    """
    import UnityPy

    env = UnityPy.load(path)
    rows = []
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        try:
            container = container_of(obj)
            data = obj.read()
            name = getattr(data, "m_Name", "") or getattr(data, "name", "")
            if not name and not container:
                continue
            img = data.image
            if img is None:
                continue
            w, h = img.size
            if w <= 0 or h <= 0:
                continue
            rel = rel_for(container, name)
            # Long-path guard: flatten rather than lose the texture.
            if len(os.path.join(out_dir, rel)) + 4 > MAX_ABS_PATH:
                rel = "%s__%s" % (sanitize(name) or "texture",
                                  hashlib.md5(container.encode("utf-8",
                                                               "replace")).hexdigest()[:8])
            fn = rel + ".png"
            n = 1
            while fn.lower() in taken:
                n += 1
                fn = "%s~%d.png" % (rel, n)
            taken.add(fn.lower())
            dest = os.path.join(out_dir, *fn.split("/"))
            d = os.path.dirname(dest)
            if d:
                os.makedirs(d, exist_ok=True)
            img.save(dest)
            rows.append((name, container, fn, w, h))
        except Exception:
            continue
    return rows


def load_manifest(out_dir):
    p = os.path.join(out_dir, MANIFEST_NAME)
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def write_manifest(out_dir, man):
    with open(os.path.join(out_dir, MANIFEST_NAME), "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=0, sort_keys=True)


def write_index(out_dir, man):
    """
    index.csv regenerated wholly from the manifest, every run.

    Deliberately not appended to: an append leaves stale rows for a bundle that
    shrank, and the manifest already holds every row we ever wrote. One pass,
    always consistent with what is on disk.
    """
    rows = []
    for rec in man.values():
        key = rec["sourceKey"]
        for name, container, fn, w, h in rec.get("rows", []):
            rows.append([key, name, container, "%s/%s" % (key, fn), w, h])
    rows.sort(key=lambda r: (r[0].lower(), r[3].lower()))
    with open(os.path.join(out_dir, INDEX_NAME), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(INDEX_COLS)
        w.writerows(rows)
    return len(rows)


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Extract every Texture2D from every AssetBundle in the load "
                    "set and the game install into a name-keyed PNG cache.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--config", default=MODS_CONFIG)
    ap.add_argument("--workshop", default=WORKSHOP)
    ap.add_argument("--local", default=LOCAL_MODS)
    ap.add_argument("--data", default=GAME_DATA)
    ap.add_argument("--force", action="store_true",
                    help="re-extract even bundles whose mtime/size are unchanged")
    ap.add_argument("--include-inactive", action="store_true",
                    help="also scan mods on disk that ModsConfig does not list")
    ap.add_argument("--only", default="", metavar="SUBSTR",
                    help="only sources whose key or name contains this")
    a = ap.parse_args(argv)

    try:
        import UnityPy  # noqa: F401
    except ImportError:
        print("UnityPy is not importable under this interpreter (%s).\n"
              "Run this under Windows python.exe, not WSL python3." % sys.executable)
        return 2

    t0 = time.perf_counter()
    os.makedirs(a.out, exist_ok=True)
    man = load_manifest(a.out)

    t = time.perf_counter()
    sources = discover_sources(a.config, a.workshop, a.local, a.data,
                               inactive=a.include_inactive)
    if a.only:
        s = a.only.lower()
        sources = [x for x in sources if s in x[0].lower() or s in x[1].lower()]
    nb = sum(len(x[2]) for x in sources)
    print("bundles: %d in %d sources  (discovery %.1fs)"
          % (nb, len(sources), time.perf_counter() - t))

    live = set()
    stats = []
    for key, label, paths in sources:
        src_dir = os.path.join(a.out, key)
        taken = set()
        n_tex = 0
        n_new = 0
        for p in paths:
            live.add(p)
            try:
                st = os.stat(p)
            except OSError:
                continue
            rec = man.get(p)
            fresh = (rec and not a.force
                     and rec.get("fmt") == ROW_FMT
                     and rec.get("size") == st.st_size
                     and int(rec.get("mtime", -1)) == int(st.st_mtime))
            if fresh:
                for _, _, fn, _, _ in rec.get("rows", []):
                    taken.add(fn.lower())
                n_tex += len(rec.get("rows", []))
                continue
            os.makedirs(src_dir, exist_ok=True)
            rows = extract_bundle(p, src_dir, taken)
            man[p] = {"sourceKey": key, "size": st.st_size, "fmt": ROW_FMT,
                      "mtime": int(st.st_mtime), "rows": rows}
            n_tex += len(rows)
            n_new += len(rows)
        stats.append((key, label, len(paths), n_tex, n_new))
        print("  %-44s %2d bundle(s)  %6d tex  (%d new)"
              % (key[:44], len(paths), n_tex, n_new))

    # A bundle that vanished (mod removed or updated to loose art) must not keep
    # feeding the index. Its PNGs are left on disk — harmless, and deleting is
    # the one operation here that can destroy something we did not create.
    for gone in [p for p in man if p not in live]:
        del man[gone]

    write_manifest(a.out, man)
    n_rows = write_index(a.out, man)

    size = 0
    for dirpath, _, files in os.walk(a.out):
        for fn in files:
            try:
                size += os.path.getsize(os.path.join(dirpath, fn))
            except OSError:
                pass

    print("\n%-44s %8s %8s" % ("source", "bundles", "textures"))
    for key, label, nbun, ntex, _ in sorted(stats, key=lambda s: -s[3]):
        print("%-44s %8d %8d" % (key[:44], nbun, ntex))
    print("\n%d textures over %d sources -> %s"
          % (n_rows, len(stats), os.path.abspath(a.out)))
    print("cache %.1f MB   total %.1fs" % (size / 1048576.0,
                                           time.perf_counter() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
