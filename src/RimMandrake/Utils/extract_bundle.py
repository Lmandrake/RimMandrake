#!/usr/bin/env python3
"""
extract_bundle.py - read and extract RimWorld mod Unity AssetBundles.

WHY THIS EXISTS
===============
RimWorld 1.6 gave AssetBundles "first-class support", and mod authors have begun
shipping art as compiled bundles instead of loose PNGs to halve download size.
Star Wars Animal Collection, Outer Rim (Core / Droid Depot / Galactic Diversity)
and several Mlie ports all do this.

A bundle is invisible to `find -name '*.png'`. On 2026-08-11 a texture-quality
audit of every Star Wars race mod had to record four mods as "UNVERIFIED - art
locked in AssetBundles", which nearly sent us commissioning replacement art for a
race whose good art was already installed. This script closes that blind spot.

WHAT IT DOES
============
  --list      inventory every texture: name, dimensions, and the internal path
  --extract   write textures out as PNGs
  --find      filter by substring (case-insensitive) on name or path

THE PATH MAPPING THAT MATTERS
=============================
Assets inside a bundle are stored at the path the loose file would have used,
prefixed with the mod's identity:

    assets/data/<packageid>/textures/things/pawn/humanlike/heads/wookiee/wookiee_south.png
                                    ^--------------- this part is the RimWorld texture path

Strip `assets/data/<packageid>/textures/` and drop the extension, and you have the
path a def's `graphicPath` / `texPath` uses. --list prints both forms.

WHY YOU CAN STILL OVERRIDE A BUNDLE
===================================
RimWorld resolves a texture request in this order:

    1. a LOOSE file at that path, in ANY active mod
    2. the base game's built-in resources
    3. bundles

Bundles are checked LAST. So a loose PNG at the same path beats a bundled asset
regardless of load order - overriding a bundle mod is actually EASIER than
overriding a loose-file mod, where you would have to win the load-order fight.
(The reverse is the bundle author's problem: a bundle can never override a base
game texture, because step 2 always finds it first.)
Source: https://rimworldwiki.com/wiki/Modding_Tutorials/Asset_Bundles

REQUIREMENTS
============
    pip install UnityPy Pillow

⚠️ In a Cowork cloud session, `device_bash` on the user's machine has NO network,
so pip cannot run there. The working pipeline is:
    device_stage_files (bundle -> container) -> run this in the container ->
    device_commit_files (PNGs -> disk)

USAGE
=====
  python extract_bundle.py <bundle> --list
  python extract_bundle.py <bundle> --list --find wookiee
  python extract_bundle.py <bundle> --extract out/ --find wookiee
  python extract_bundle.py <bundle> --extract out/ --keep-paths

`--keep-paths` writes each texture to its full internal directory structure,
which is what you want when preparing an override mod: the tree it produces
mirrors the `Textures/` layout the overriding mod needs.

MAINTENANCE
===========
UnityPy's API moves between versions. If `obj.read()` stops returning objects
with `.m_Name` / `.m_Width`, check UnityPy's changelog before assuming the bundle
is corrupt. Verified working against UnityPy 1.25.3 on 2026-08-11.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

try:
    import UnityPy
except ImportError:
    sys.exit("UnityPy is required:  pip install UnityPy Pillow")


PATH_PREFIX = re.compile(r"^assets/data/[^/]+/textures/", re.I)


def rimworld_path(container_path: str) -> str:
    """
    'assets/data/mod.id/textures/things/pawn/x/y.png' -> 'Things/Pawn/X/Y'
    Returns the path with original casing lost (bundles lowercase everything),
    which is fine for reading but means you must check the def for true casing
    before writing an override file.
    """
    if not container_path:
        return ""
    p = PATH_PREFIX.sub("", container_path)
    return os.path.splitext(p)[0]


def load_bundle(path: str):
    if not os.path.isfile(path):
        sys.exit(f"not a file: {path}")
    env = UnityPy.load(path)
    # Build path_id -> container path from the AssetBundle manifest object.
    paths = {}
    for obj in env.objects:
        if obj.type.name == "AssetBundle":
            try:
                tree = obj.read_typetree()
            except Exception:
                continue
            for key, val in tree.get("m_Container", []):
                pid = val.get("asset", {}).get("m_PathID")
                if pid is not None:
                    paths[pid] = key
    return env, paths


def iter_textures(env, paths, needle: str | None):
    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        try:
            data = obj.read()
        except Exception as e:
            print(f"  !! unreadable Texture2D (path_id {obj.path_id}): {e}", file=sys.stderr)
            continue
        name = str(getattr(data, "m_Name", "") or "")
        cpath = paths.get(obj.path_id, "")
        if needle:
            hay = (name + " " + cpath).lower()
            if needle.lower() not in hay:
                continue
        yield name, cpath, data


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect/extract a RimWorld mod AssetBundle.")
    ap.add_argument("bundle", help="path to the bundle file (no extension, e.g. .../AssetBundles/mymod_assets)")
    ap.add_argument("--list", action="store_true", help="print an inventory")
    ap.add_argument("--extract", metavar="OUTDIR", help="write PNGs to this directory")
    ap.add_argument("--find", metavar="SUBSTR", help="only textures whose name or path contains this")
    ap.add_argument("--keep-paths", action="store_true",
                    help="with --extract, recreate the internal directory tree "
                         "(use this when building an override mod)")
    args = ap.parse_args()

    if not args.list and not args.extract:
        args.list = True

    env, paths = load_bundle(args.bundle)
    n_total = sum(1 for o in env.objects if o.type.name == "Texture2D")
    print(f"\n{os.path.basename(args.bundle)} - {n_total} Texture2D object(s)\n")

    shown = written = 0
    for name, cpath, data in iter_textures(env, paths, args.find):
        shown += 1
        if args.list:
            rw = rimworld_path(cpath)
            print(f"  {data.m_Width:>5}x{data.m_Height:<5}  {name}")
            if rw:
                print(f"        rimworld path: {rw}")
            elif cpath:
                print(f"        container    : {cpath}")

        if args.extract:
            if args.keep_paths and cpath:
                rel = rimworld_path(cpath) + ".png"
                dest = os.path.join(args.extract, rel)
            else:
                dest = os.path.join(args.extract, f"{name or 'unnamed'}.png")
            os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
            try:
                data.image.save(dest)
                written += 1
            except Exception as e:
                print(f"  !! could not save {name}: {e}", file=sys.stderr)

    if args.find:
        print(f"\n  {shown} texture(s) matched {args.find!r}")
    if args.extract:
        print(f"  wrote {written} PNG(s) to {args.extract}")
    if shown == 0:
        print("  (nothing matched - the bundle may store art under different names; "
              "re-run without --find to see the full inventory)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
