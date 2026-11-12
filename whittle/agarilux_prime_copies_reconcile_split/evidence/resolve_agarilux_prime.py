#!/usr/bin/env python3
"""Which PNG does the player see for RM_AgariluxPrime? A resolved-def read, offline.

1. The base def's graphicData/texPath (src XML, ParentName chain walked).
2. Every PatchOperation in src/ whose xpath names RM_AgariluxPrime, and whether it touches graphicData/texPath
   (Conditional/Sequence children included).
3. The resolved texPath -> every Textures/<path>.png across our src mods (RimWorld's ContentFinder takes the
   last-loaded mod that has the file; more than one hit is a shadow).
4. The live def dump (a real full-list game load) for RM_AgariluxPrime / AB_AgariluxPrime, and every dumped def whose
   JSON names the old donor slot path.
5. Every PNG at the old slot, in src/ and in the deployed Steam Mods folder.
Usage: python3 resolve_agarilux_prime.py   (prints a report; exit 1 if the player would see anything but one PNG)
"""
from __future__ import annotations

import json
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
DEF = "RM_AgariluxPrime"
OLD = "Things/Plants/AB_AgariluxPrime"
DUMP = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite")
STEAM_MODS = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")


def defs_by_name():
    out = {}
    for f in SRC.rglob("*.xml"):
        if "/Defs/" not in str(f):
            continue
        try:
            root = ET.parse(f).getroot()
        except (ET.ParseError, OSError):
            continue
        for d in root:
            if not isinstance(d.tag, str):
                continue
            key = (d.findtext("defName") or "").strip() or ("@" + (d.get("Name") or ""))
            if key not in ("", "@"):
                out.setdefault(key, []).append((f, d))
    return out


def base_texpath(defs):
    chain, name = [], DEF
    while name:
        hits = defs.get(name) or defs.get("@" + name) or []
        if len(hits) != 1:
            chain.append((name, f"{len(hits)} definitions"))
            return None, chain
        f, d = hits[0]
        tp = d.findtext("graphicData/texPath")
        chain.append((name, str(f.relative_to(REPO))))
        if tp:
            return tp.strip(), chain
        name = d.get("ParentName")
    return None, chain


def patch_ops():
    rows = []
    for f in SRC.rglob("*.xml"):
        if "/Patches/" not in str(f):
            continue
        try:
            root = ET.parse(f).getroot()
        except (ET.ParseError, OSError):
            continue
        for op in root.iter():
            xp = op.find("xpath")
            if xp is None or DEF not in (xp.text or ""):
                continue
            val = op.find("value")
            touched = ("graphicData" in xp.text or "texPath" in xp.text
                       or (val is not None and val.find(".//texPath") is not None))
            rows.append((str(f.relative_to(REPO)), op.get("Class"), xp.text.strip(), touched))
    return rows


def pngs(rel):
    return sorted(str(p.relative_to(REPO)) for p in SRC.glob(f"*/*/Textures/{rel}.png"))


def main() -> int:
    bad = 0
    defs = defs_by_name()
    tp, chain = base_texpath(defs)
    print(f"== 1. base def {DEF}")
    for n, where in chain:
        print(f"   {n:40s} {where}")
    print(f"   base graphicData/texPath = {tp!r}")
    print(f"\n== 2. patch operations naming {DEF} (src/**/Patches)")
    ops = patch_ops()
    tex_ops = [o for o in ops if o[3]]
    for f, cls, xp, t in ops:
        print(f"   {'TEXPATH ' if t else 'other   '}{cls:32s} {f}  {xp}")
    print(f"   {len(ops)} operation(s); {len(tex_ops)} touch graphicData/texPath")
    resolved = tp
    if tex_ops:
        print("   !! a patch changes the texPath: the base value is not the final one")
        bad += 1
    print(f"\n== 3. resolved texPath {resolved!r} -> PNG(s) in our src mods")
    hits = pngs(resolved) if resolved else []
    for h in hits:
        print(f"   {h}  ({(REPO / h).stat().st_size} bytes)")
    if len(hits) != 1:
        print(f"   !! {len(hits)} PNGs answer the resolved path (want exactly 1)")
        bad += 1
    print(f"\n== 4. live def dump {DUMP}")
    if DUMP.is_file():
        db = sqlite3.connect(f"file:{DUMP}?mode=ro", uri=True)
        prov = dict(db.execute("select key, value from provenance"))
        print(f"   captured_utc={prov.get('captured_utc')} mod_count={prov.get('mod_count')} "
              f"game={prov.get('game_version')} modlist_fingerprint={prov.get('modlist_fingerprint')}")
        for dn in (DEF, "AB_AgariluxPrime"):
            r = db.execute("select json from defs where def_name=? and def_type='ThingDef'", (dn,)).fetchone()
            if r:
                j = json.loads(r[0])
                print(f"   {dn}: texPath={j['fields'].get('graphicData', {}).get('texPath')!r} "
                      f"packageId={j.get('packageId')} mod={j.get('modName')!r}")
            else:
                print(f"   {dn}: NOT IN THE LIVE GAME (no row)")
        n = db.execute("select count(*) from defs where json like ?", (f"%{OLD}%",)).fetchone()[0]
        names = [r[0] for r in db.execute("select def_type||':'||def_name from defs where json like ?", (f"%{OLD}%",))]
        print(f"   dumped defs whose JSON names {OLD!r}: {n} {names}")
        sanity = db.execute("select count(*) from defs where json like ?", ("%RotSpecies/AgariluxPrime%",)).fetchone()[0]
        print(f"   sanity probe: dumped defs naming 'RotSpecies/AgariluxPrime': {sanity} (instrument can see)")
    else:
        print("   UNMEASURED: dump not readable")
    print(f"\n== 5. PNGs at the old slot {OLD}.png")
    old_src = pngs(OLD)
    print(f"   src/: {old_src or 'none'}")
    if old_src:
        bad += 1
    if STEAM_MODS.is_dir():
        dep = sorted(str(p) for p in STEAM_MODS.glob(f"**/Textures/{OLD}.png"))
        print(f"   deployed Steam Mods (stale until the next deploy of those mods): {dep or 'none'}")
    print(f"\nVERDICT: {'ONE PNG' if not bad else 'NOT ONE PNG'} -- the player sees "
          f"{hits[0] if len(hits) == 1 else hits}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
