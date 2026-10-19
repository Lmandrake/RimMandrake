#!/usr/bin/env python3
"""donor_standins.py — copy donor/vanilla art our defs still borrow into OUR mods as marked stand-ins, and repoint
our XML at the copies, so the donor mods can be retired (owner, 2026-10-18: "Just put in placeholder art for now or
donor copies and retire these mods!!! Just get it done.").

    python3 src/RimMandrake/Utils/art/donor_standins.py plan  --census CENSUS.json --cats DONOR,DONOR_BUNDLE ...
                                                               [--only TEXPATH ...] --out PLAN.json
    python3 src/RimMandrake/Utils/art/donor_standins.py apply PLAN.json [--apply]      dry run without --apply

CENSUS is `donor_retire_census.py tex --json` output. For every texPath of a chosen category, `plan` finds:
  * the SOURCE pictures: every file of that texPath in the serving mod (facings, masks, Graphic_Random variants), or
    for AssetBundle/base-game art the extract under observed/inventory/bundle_textures (index.csv, names keep their
    in-game casing);
  * the OWNING mods: every src/ mod (FlowWorks excluded) whose XML names the texPath in a *Path element;
  * the copy's path: Textures/StandIn/<texPath>... inside each owning mod — OUR path, never the donor's.
`apply` installs each picture through the art ledger (artwrite.TextureWriter, reason script:<this file>,
provenance kind=donor + standin=true, so a later regenerated render replaces it through `art install` and review
sheets show it as past art), never over a file already in our tree, then rewrites `<x...Path>T</x...Path>` to
`StandIn/T` in that mod's XML. A geometric placeholder is refused by the ledger (owner rule 2026-10-07), so a row
with no source picture is reported, never drawn.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "src"
sys.path.insert(0, str(HERE))
BUNDLES = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures")
SKIP = ("src/RimMandrake/FlowWorks/",)
PREFIX = "StandIn/"
SUFFIX = re.compile(r"^(_(north|south|east|west))?(_?m|_?Mask)?(_(north|south|east|west))?$", re.I)
EXTRA_SUFFIX = re.compile(r"^(_[a-z0-9]+)?$", re.I)          # Graphic_Random-in-file variants: Name_a, NameA ...


def mod_dirs() -> list[Path]:
    return sorted({p.parent.parent for p in SRC.glob("*/*/About/About.xml")})


def path_elems(text: str, tex: str):
    """Spans of `>tex<` inside an element whose tag ends in Path/path (texPath, texturePath, iconPath, ...)."""
    pat = re.compile(r"<(\w*[Pp]ath)(\s[^>]*)?>\s*" + re.escape(tex) + r"\s*</\1>")
    return list(pat.finditer(text))


def owners(tex: str, files_by_mod) -> dict:
    out = {}
    for mod, files in files_by_mod.items():
        hits = [f for f, t in files if path_elems(t, tex)]
        if hits:
            out[mod] = hits
    return out


def loose_sources(row_file: str, tex: str) -> list[tuple[Path, str]]:
    """(source file, relative name under the texPath's folder) — every sibling picture of this texPath."""
    f = Path(row_file)
    base = tex.rsplit("/", 1)[-1]
    if f.parent.name.lower() == base.lower() and not f.stem.lower().startswith(base.lower()):
        # Graphic_Random folder: copy the folder
        return [(p, f"{base}/{p.name}") for p in sorted(f.parent.glob("*.png"))]
    folder = f.parent
    out = []
    for p in sorted(folder.glob("*.png")):
        st = p.stem
        if st.lower().startswith(base.lower()) and (SUFFIX.match(st[len(base):]) or
                                                     st[len(base):].lower() in ("_dessicated", "dessicated")):
            out.append((p, p.name))
    return out


def bundle_sources(pkg: str, tex: str) -> list[tuple[Path, str]]:
    idx = BUNDLES / "index.csv"
    low = tex.lower()
    base = tex.rsplit("/", 1)[-1]
    out = []
    with idx.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["sourceKey"].lower() != pkg:
                continue
            cont = (r["container"] or "").lower()
            name = r["m_Name"]
            if cont:
                pre = f"assets/data/{pkg}/textures/"
                if not cont.startswith(pre):
                    continue
                rel = cont[len(pre):-4] if cont.endswith(".png") else cont[len(pre):]
                if rel == low or (rel.startswith(low) and SUFFIX.match(rel[len(low):])):
                    out.append((BUNDLES / r["file"], name + ".png"))
                elif rel.startswith(low + "/") and "/" not in rel[len(low) + 1:]:
                    out.append((BUNDLES / r["file"], f"{base}/{name}.png"))
            else:                                       # base game: names only
                if name.lower() == base.lower() or (name.lower().startswith(base.lower())
                                                    and SUFFIX.match(name[len(base):])):
                    out.append((BUNDLES / r["file"], name + ".png"))
    return out


def plan(census: dict, cats: set, only: set | None) -> dict:
    rows = [r for r in census["rows"] if r["cat"] in cats and (not only or r["tex"] in only)]
    files_by_mod = defaultdict(list)
    for md in mod_dirs():
        rel = md.relative_to(REPO).as_posix() + "/"
        if rel.startswith(SKIP):
            continue
        for f in md.rglob("*.xml"):
            if "/Textures/" in f.as_posix():
                continue
            files_by_mod[md.relative_to(REPO).as_posix()].append((f.relative_to(REPO).as_posix(),
                                                                   f.read_text(errors="replace")))
    out, seen = [], set()
    for r in rows:
        t = r["tex"]
        if t in seen:
            continue
        seen.add(t)
        if r["cat"] in ("DONOR_BUNDLE", "VANILLA") and r["file"] and str(r["file"]).startswith(str(BUNDLES)):
            srcs = bundle_sources(r["by"], t)
        elif r["file"]:
            srcs = loose_sources(r["file"], t)
        else:
            srcs = []
        own = owners(t, files_by_mod)
        defs = sorted({x["def"] for x in census["rows"] if x["tex"] == t})
        out.append({"tex": t, "cat": r["cat"], "donor_pkg": r["by"], "defs": defs,
                    "sources": [[str(a), b] for a, b in srcs],
                    "owners": {m: fs for m, fs in own.items()},
                    "dest_tex": PREFIX + t})
    return {"census": census.get("capture"), "items": out}


def apply(pl: dict, do: bool) -> int:
    from artwrite import TextureWriter
    bad = 0
    changed_xml = set()
    for it in pl["items"]:
        if not it["sources"] or not it["owners"]:
            print(f"SKIP {it['tex']}: sources={len(it['sources'])} owners={len(it['owners'])}")
            bad += 1
            continue
        folder = it["dest_tex"].rsplit("/", 1)[0]
        tw = TextureWriter(__file__, dry_run=not do, provenance={
            "kind": "donor", "donor_pkg": it["donor_pkg"], "standin": True, "orig_texpath": it["tex"],
            "why": "donor-retirement stand-in until regenerated (owner 2026-10-18)"})
        for mod, files in it["owners"].items():
            for src, name in it["sources"]:
                dest = REPO / mod / "Textures" / folder / name
                if dest.exists():
                    continue                                    # never over a file already in our tree
                tw.copy(src, dest)
            for f in files:
                p = REPO / f
                txt = p.read_text()
                new = txt
                for m in reversed(path_elems(txt, it["tex"])):
                    seg = m.group(0).replace(it["tex"], it["dest_tex"], 1)
                    new = new[:m.start()] + seg + new[m.end():]
                if new != txt:
                    if do:
                        p.write_text(new)
                    changed_xml.add(f)
        print(f"{'APPLIED' if do else 'DRY'} {it['tex']} -> {it['dest_tex']}  {tw.counts}  owners={list(it['owners'])}")
        for r in tw.refusals:
            print("   REFUSED", r)
            bad += 1
    print(f"xml files {'changed' if do else 'to change'}: {len(changed_xml)}")
    for f in sorted(changed_xml):
        print("  ", f)
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--census", required=True)
    p.add_argument("--cats", required=True)
    p.add_argument("--only", nargs="*")
    p.add_argument("--out", required=True)
    a2 = sub.add_parser("apply")
    a2.add_argument("plan")
    a2.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        pl = plan(json.load(open(a.census)), set(a.cats.split(",")), set(a.only) if a.only else None)
        Path(a.out).write_text(json.dumps(pl, indent=1))
        for it in pl["items"]:
            print(f"{len(it['sources']):3} src {len(it['owners']):2} own  {it['cat']:14} {it['tex']}")
        return 0
    return apply(json.load(open(a.plan)), a.apply)


if __name__ == "__main__":
    sys.exit(main())
