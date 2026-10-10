#!/usr/bin/env python3
"""texture_gap_lint.py — every texPath a shipped def/patch names must resolve to a picture the game can load.

ART_TEXTURE_GAPS_FOLLOWUP_1. The game draws magenta (or nothing) for a texPath no active mod ships, and logs one
line. This is the offline census of that class. Tiers, first match wins, for each texPath-like element under
src/<tier>/<mod>/{Defs,Patches} (UI/ is never judged):

  OK_SRC      resolves to a PNG under src/**/Textures (placeholder_lint.resolve: Graphic_Random folder, file, facings, no masks)
  OK_ACTIVE   the gametex index (cached; never rebuilt here) holds it in an ACTIVE donor mod, or in the base game bundles
  INACTIVE    only an INACTIVE installed mod ships it (e.g. the absorbed KotOR crystal donor)  -> a GAP
  MISSING     nowhere                                                                              -> a GAP
  UNRESOLVED  the index has no ACTIVE copy but a mod on disk does and the path uses the base-game layout (Things/…), or
              an active mod's own directory holds it: Core's art is not fully indexed, so absence is not shown
              -> NOT a gap, never claimed missing
  UNMEASURED  no gametex cache on this machine: only OK_SRC can be judged; the rest are reported, not failed

GAPS must be listed in texture_gap_allowlist.json (shrink-only): an unlisted gap fails, a stale entry fails, an entry
added after `frozen` fails. Each entry says what is owed. SANITY PROBE: a known-present texPath must classify OK.

    python3 src/RimMandrake/Utils/art/texture_gap_lint.py [-v]      exit 1 on any failure
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_lint as PL  # noqa: E402

REPO = PL.REPO
ALLOWLIST = HERE / "texture_gap_allowlist.json"
CACHE = Path(os.environ.get("RM_GAMETEX_CACHE") or "/tmp/rm_gametex")
DONOR_ROOTS = (Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
               Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"))


def load_index():
    p = CACHE / "texindex.json"
    return json.loads(p.read_text()) if p.is_file() else None


_DISK = None
VANILLA_LAYOUT = ("Things/", "Terrain/", "Mote/")


def on_disk(tp: str):
    """-> the mod dir of an installed mod whose Textures ship tp (file, facing or folder), else None. One directory
    listing of the installed roots is cached; used only for paths the index has no copy of."""
    global _DISK
    if _DISK is None:
        cp = CACHE / "texdirs.json"          # ~minutes to list on /mnt/c, so listed once per boot
        if cp.is_file():
            _DISK = [Path(x) for x in json.loads(cp.read_text())]
        else:
            _DISK = []
            for root in DONOR_ROOTS:
                if root.is_dir():
                    for pat in ("*/Textures", "*/*/Textures", "*/*/*/Textures"):
                        _DISK += list(root.glob(pat))
            if _DISK:
                CACHE.mkdir(parents=True, exist_ok=True)
                cp.write_text(json.dumps([str(x) for x in _DISK]))
    for tex in _DISK:
        b = tex / tp
        if not b.parent.is_dir():
            continue
        if b.is_dir() or any(Path(str(b) + s + ".png").is_file() for s in ("", "_south", "_east", "_north", "_west")):
            return tex
    return None


class Index:
    """Read-only view of the cached gametex index. active = mods the live list loads (load_index >= 0)."""

    def __init__(self, ix):
        self.ix = ix
        self.active = {i for i, m in enumerate(ix["mods"]) if m["load_index"] >= 0}
        self.active_dirs = {m["dir"] for m in ix["mods"] if m["load_index"] >= 0}
        self.dirs = {k.rsplit("/", 1)[0] for k in ix["files"] if "/" in k}
        self.bnames = [k for k in ix["bundle_files"] if k.startswith("name:")]
        self.bdirs = {k.rsplit("/", 1)[0] for k in ix["bundle_files"] if "/" in k}

    def active_has(self, tp: str) -> bool:
        key = tp.lower().rstrip("/")
        hits = self.ix["files"].get(key)
        if hits and any(h[0] in self.active for h in hits):
            return True
        if key in self.dirs:                       # a Graphic_Random folder: some active mod ships a file inside
            pre = key + "/"
            return any(h[0] in self.active for k, v in self.ix["files"].items() if k.startswith(pre) for h in v)
        bf = self.ix["bundle_files"]
        base = key.split("/")[-1]
        # base game: no container, a Random folder's variants are named <Base>A / <Base>_a (gametex.resolve_res rung)
        return key in bf or key in self.bdirs or ("name:" + base) in bf or \
            any(re.fullmatch(re.escape("name:" + base) + r"_?[a-z]", k) for k in self.bnames)


def classify(tp: str, roots, ix) -> str:
    if tp.startswith("UI/") or PL.resolve(tp, roots):
        return "OK_SRC"
    if ix is None:
        return "UNMEASURED"
    if ix.active_has(tp):
        return "OK_ACTIVE"
    hit = on_disk(tp)
    if hit is None:
        return "MISSING"
    mod = str(hit.parent)
    if tp.startswith(VANILLA_LAYOUT):        # base-game folder layout: Core's own art is not fully indexed, so another
        return "UNRESOLVED"                  # mod shipping it proves nothing either way
    return "UNRESOLVED" if any(mod == d or mod.startswith(d + "/") or d.startswith(mod + "/") for d in ix.active_dirs) else "INACTIVE"


def census(paths: dict | None = None, roots=None, ix="load") -> dict:
    paths = PL.texpaths() if paths is None else paths
    roots = PL.texture_roots() if roots is None else roots
    ix = (lambda r: Index(r) if r else None)(load_index()) if ix == "load" else ix
    out: dict = {}
    for tp, files in paths.items():
        out[tp] = {"class": classify(tp, roots, ix), "defs": files}
    return out


def lint(found: dict, allow: dict) -> list[str]:
    frozen = allow.get("frozen") or ""
    entries = {e["texPath"]: e for e in allow.get("entries", [])}
    gaps = {tp: f for tp, f in found.items() if f["class"] in ("INACTIVE", "MISSING")}
    fails = []
    for e in entries.values():
        if not frozen or (e.get("added") or "9999") > frozen:
            fails.append(f"ALLOWLIST GREW: {e['texPath']} added {e.get('added')!r} after the list froze on {frozen!r}")
        if not e.get("owed"):
            fails.append(f"ALLOWLIST entry {e['texPath']} says nothing about what is owed")
    for tp, f in sorted(gaps.items()):
        if tp not in entries:
            fails.append(f"TEXTURE GAP: {tp} ({f['class']}; {', '.join(f['defs'][:2])})")
    measured = any(f["class"] != "UNMEASURED" for f in found.values() if not f["class"] == "OK_SRC") or \
        not any(f["class"] == "UNMEASURED" for f in found.values())
    if measured:
        for tp in sorted(set(entries) - set(gaps)):
            fails.append(f"STALE ALLOWLIST ENTRY: {tp} is no longer a gap — delete it from {ALLOWLIST.name}")
    return fails


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    found = census()
    allow = json.loads(ALLOWLIST.read_text()) if ALLOWLIST.is_file() else {"frozen": "", "entries": []}
    from collections import Counter
    print("classes:", dict(Counter(f["class"] for f in found.values())))
    if "-v" in argv:
        for tp, f in sorted(found.items()):
            if f["class"] not in ("OK_SRC", "OK_ACTIVE"):
                print(f"  {f['class']:10} {tp}  [{f['defs'][0]}]")
    if all(f["class"] in ("OK_SRC", "UNMEASURED") for f in found.values()) and not load_index():
        print("UNMEASURED: no gametex cache here; only src-resolved paths were judged")
        return 0
    fails = lint(found, allow)
    for x in fails:
        print("FAIL", x)
    print("texture_gap_lint:", "FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
