#!/usr/bin/env python3
"""Harvest every XenotypeDef and GeneDef from the ACTIVE mod list into JSON.

Why this exists: the genome comparison matrix needs three things the game keeps
in three different places -- the xenotype's gene list (XenotypeDef), each gene's
label/category/biostats (GeneDef, sometimes generated from a GeneTemplateDef and
so absent from XML), and the gene's icon PNG (Textures/, resolved per-mod with
later mods overriding earlier ones).

Reads ModsConfig.xml so it only ever sees mods that actually load. Writes
genes.json / xenotypes.json / icons index; genome_matrix_build.py renders them.

Usage:  python3 src/RimMandrake/Utils/genome_scan.py [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_packageid_index import read_about as _read_about  # noqa: E402
from game_paths import GAME_DATA, LOCAL_MODS, MODS_CONFIG, WORKSHOP as _WORKSHOP  # noqa: E402

WORKSHOP = Path(_WORKSHOP)
MODSCONFIG = Path(MODS_CONFIG)
GAME_VERSION = "1.6"

# Official DLC live under Data/<Name> and carry their own About.xml.
DEF_MARKERS = (b"GeneDef", b"XenotypeDef", b"GeneTemplateDef")


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- mod discovery


def active_package_ids() -> list[str]:
    root = ET.parse(MODSCONFIG).getroot()
    ids = [li.text.strip().lower() for li in root.findall("./activeMods/li") if li.text]
    return ids


def read_package_id(mod_dir: Path) -> str | None:
    """The mod's OWN packageId, lowercased, or None.

    Delegates to build_packageid_index.read_about, which strips <modDependencies>
    before searching. Reading "the first <packageId> in About.xml" returns the
    dependency's id whenever dependencies are declared first -- it reported
    brrainz.harmony for Alpha Animals -- and that is why 62 active mods came back
    unresolvable on the first run of this script.
    """
    for name in ("About/About.xml", "about/About.xml", "About/about.xml"):
        p = mod_dir / name
        if p.is_file():
            _label, pid = _read_about(str(p))
            return pid.lower() if pid else None
    return None


def discover_mod_dirs() -> dict[str, Path]:
    """packageId -> mod folder, over every place RimWorld looks."""
    roots: list[Path] = []
    for base in (Path(GAME_DATA), Path(LOCAL_MODS), WORKSHOP):
        if base.is_dir():
            roots += [d for d in base.iterdir() if d.is_dir()]

    found: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=24) as ex:
        for d, pid in zip(roots, ex.map(read_package_id, roots)):
            if pid and pid not in found:
                found[pid] = d
    return found


def content_dirs(mod_dir: Path, kind: str) -> list[Path]:
    """Version-folder resolution: root/<kind> plus <version>/<kind>.

    RimWorld loads the root folder AND the folder matching the running version.
    Scanning 1.4 and 1.5 too would double-count defs that were later revised.
    """
    out: list[Path] = []
    root = mod_dir / kind
    if root.is_dir():
        out.append(root)
    versioned = mod_dir / GAME_VERSION / kind
    if versioned.is_dir():
        out.append(versioned)
    else:
        # Mod has not been updated to 1.6 -- fall back to its highest version dir.
        vers = []
        for d in mod_dir.iterdir() if mod_dir.is_dir() else []:
            if d.is_dir() and re.fullmatch(r"1\.\d+", d.name) and (d / kind).is_dir():
                vers.append((tuple(int(x) for x in d.name.split(".")), d / kind))
        if vers:
            out.append(max(vers)[1])
    return out


# ------------------------------------------------------------------ def parsing


def candidate_xml(def_dirs: list[Path]) -> list[Path]:
    hits: list[Path] = []
    for d in def_dirs:
        for dirpath, _dirnames, filenames in os.walk(d):
            for fn in filenames:
                if fn.lower().endswith(".xml"):
                    hits.append(Path(dirpath) / fn)
    return hits


def file_mentions_genes(p: Path) -> bytes | None:
    try:
        raw = p.read_bytes()
    except OSError:
        return None
    return raw if any(m in raw for m in DEF_MARKERS) else None


def parse_defs(raw: bytes, source: str) -> list[tuple[str, ET.Element]]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # Mod XML is frequently malformed in ways the game tolerates; a broken
        # file costs us that file, not the run.
        log(f"  ! unparseable XML: {source}")
        return []
    out = []
    for child in root:
        if child.tag in ("GeneDef", "XenotypeDef", "GeneTemplateDef"):
            out.append((child.tag, child))
    return out


def text(el: ET.Element, tag: str) -> str | None:
    node = el.find(tag)
    if node is None:
        return None
    return (node.text or "").strip() or None


def li_list(el: ET.Element, tag: str) -> list[str]:
    node = el.find(tag)
    if node is None:
        return []
    return [(li.text or "").strip() for li in node.findall("li") if (li.text or "").strip()]


def resolve_inheritance(raw_defs: dict[str, dict]) -> None:
    """Fold ParentName chains down so children carry the parent's fields.

    Abstract parents supply displayCategory / exclusionTags to dozens of real
    genes; without this most genes come out uncategorised.
    """
    named = {d["_name"]: d for d in raw_defs.values() if d.get("_name")}

    def fold(d: dict, depth: int = 0) -> dict:
        parent_name = d.get("_parent")
        if not parent_name or depth > 8:
            return d
        parent = named.get(parent_name)
        if parent is None:
            return d
        parent = fold(parent, depth + 1)
        for k, v in parent.items():
            if k.startswith("_"):
                continue
            if d.get(k) in (None, [], ""):
                d[k] = v
        return d

    for d in list(raw_defs.values()):
        fold(d)


# --------------------------------------------------------- template expansion


def skill_and_chemical_defnames(mod_dirs: dict[str, Path], active: list[str]) -> dict:
    """SkillDefs and ChemicalDefs, which is what {0} in a template resolves to."""
    out = {"Skill": [], "Chemical": []}
    wanted = {"SkillDef": "Skill", "ChemicalDef": "Chemical"}
    for pid in active:
        d = mod_dirs.get(pid)
        if not d:
            continue
        for defdir in content_dirs(d, "Defs"):
            for dirpath, _dn, filenames in os.walk(defdir):
                for fn in filenames:
                    if not fn.lower().endswith(".xml"):
                        continue
                    p = Path(dirpath) / fn
                    try:
                        raw = p.read_bytes()
                    except OSError:
                        continue
                    if b"SkillDef" not in raw and b"ChemicalDef" not in raw:
                        continue
                    try:
                        root = ET.fromstring(raw)
                    except ET.ParseError:
                        continue
                    for child in root:
                        kind = wanted.get(child.tag)
                        if not kind:
                            continue
                        dn = text(child, "defName")
                        if dn and dn not in out[kind]:
                            out[kind].append(dn)
    return out


def expand_templates(templates: dict[str, dict], fillers: dict) -> dict[str, dict]:
    """GeneTemplateDef + SkillDef -> the concrete genes the game generates.

    `AptitudeRemarkable` x `Mining` becomes `AptitudeRemarkable_Mining`,
    label "great mining", icon UI/Icons/Genes/Skills/Mining/Remarkable. These
    genes appear in xenotype gene lists but exist nowhere in XML, so a scanner
    that skips this step reports them as missing.
    """
    generated: dict[str, dict] = {}
    for tpl in templates.values():
        ttype = tpl.get("geneTemplateType")
        if ttype not in fillers:
            continue
        base = tpl.get("defName")
        if not base:
            continue
        for filler in fillers[ttype]:
            def_name = f"{base}_{filler}"
            pretty = re.sub(r"(?<!^)(?=[A-Z])", " ", filler).lower()
            label = (tpl.get("label") or base).replace("{0}", pretty)
            icon = (tpl.get("iconPath") or "").replace("{0}", filler) or None
            generated[def_name] = {
                "defName": def_name,
                "label": label,
                "description": (tpl.get("description") or "").replace("{0}", pretty),
                "iconPath": icon,
                "displayCategory": tpl.get("displayCategory"),
                "biostatMet": tpl.get("biostatMet"),
                "biostatCpx": tpl.get("biostatCpx"),
                "biostatArc": tpl.get("biostatArc"),
                "exclusionTags": ([tpl["exclusionTagPrefix"] + "_" + filler]
                                  if tpl.get("exclusionTagPrefix") else []),
                "mod": tpl.get("mod"),
                "generated": True,
            }
    return generated


# ------------------------------------------------------------- icon resolution


def build_texture_index(mod_dirs: dict[str, Path], active: list[str]) -> dict[str, str]:
    """lowercased 'UI/Icons/Genes/Foo' -> absolute PNG path.

    Later mods in the load order override earlier ones for the same path, which
    is exactly how the game resolves textures, so we overwrite as we go.
    """
    index: dict[str, str] = {}

    def scan(pid: str) -> list[tuple[str, str]]:
        d = mod_dirs.get(pid)
        if not d:
            return []
        pairs = []
        for texdir in content_dirs(d, "Textures"):
            for dirpath, _dn, filenames in os.walk(texdir):
                for fn in filenames:
                    if not fn.lower().endswith(".png"):
                        continue
                    full = Path(dirpath) / fn
                    rel = full.relative_to(texdir).with_suffix("")
                    pairs.append((str(rel).replace("\\", "/").lower(), str(full)))
        return pairs

    with ThreadPoolExecutor(max_workers=16) as ex:
        for pairs in ex.map(scan, active):
            for key, val in pairs:
                index[key] = val
    return index


# ------------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="observed/genome", help="output directory")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    active = active_package_ids()
    log(f"active mods in ModsConfig: {len(active)}")

    mod_dirs = discover_mod_dirs()
    log(f"mod folders with a readable packageId: {len(mod_dirs)}")
    missing = [p for p in active if p not in mod_dirs]
    if missing:
        log(f"  ! {len(missing)} active packageIds have no folder (first 5): {missing[:5]}")

    genes: dict[str, dict] = {}
    xenotypes: dict[str, dict] = {}
    templates: dict[str, dict] = {}

    for pid in active:
        d = mod_dirs.get(pid)
        if not d:
            continue
        files = candidate_xml(content_dirs(d, "Defs"))
        if not files:
            continue
        with ThreadPoolExecutor(max_workers=16) as ex:
            blobs = list(ex.map(file_mentions_genes, files))
        for p, raw in zip(files, blobs):
            if raw is None:
                continue
            for tag, el in parse_defs(raw, str(p)):
                name_attr = el.attrib.get("Name")
                parent_attr = el.attrib.get("ParentName")
                abstract = el.attrib.get("Abstract", "").lower() == "true"
                def_name = text(el, "defName")
                key = def_name or name_attr
                if not key:
                    continue
                rec = {
                    "_name": name_attr,
                    "_parent": parent_attr,
                    "_abstract": abstract,
                    "defName": def_name,
                    "label": text(el, "label"),
                    "description": text(el, "description"),
                    "iconPath": text(el, "iconPath"),
                    "displayCategory": text(el, "displayCategory"),
                    "displayOrderInCategory": text(el, "displayOrderInCategory"),
                    "biostatMet": text(el, "biostatMet"),
                    "biostatCpx": text(el, "biostatCpx"),
                    "biostatArc": text(el, "biostatArc"),
                    "exclusionTags": li_list(el, "exclusionTags"),
                    "mod": pid,
                }
                if tag == "GeneDef":
                    genes[key] = rec
                elif tag == "GeneTemplateDef":
                    rec["geneTemplateType"] = text(el, "geneTemplateType")
                    rec["exclusionTagPrefix"] = text(el, "exclusionTagPrefix")
                    templates[key] = rec
                else:
                    rec["genes"] = li_list(el, "genes")
                    rec["inheritable"] = text(el, "inheritable")
                    rec["displayPriority"] = text(el, "displayPriority")
                    rec["factionlessGenerationWeight"] = text(
                        el, "factionlessGenerationWeight")
                    xenotypes[key] = rec

    resolve_inheritance(genes)
    resolve_inheritance(templates)
    resolve_inheritance(xenotypes)

    fillers = skill_and_chemical_defnames(mod_dirs, active)
    log(f"template fillers: {len(fillers['Skill'])} skills, "
        f"{len(fillers['Chemical'])} chemicals")
    generated = expand_templates(
        {k: v for k, v in templates.items() if not v["_abstract"]}, fillers)
    for k, v in generated.items():
        genes.setdefault(k, v)

    genes = {k: v for k, v in genes.items() if not v.get("_abstract")}
    xenotypes = {k: v for k, v in xenotypes.items() if not v.get("_abstract")}
    log(f"genes: {len(genes)} ({len(generated)} generated from templates)")
    log(f"xenotypes: {len(xenotypes)}")

    tex = build_texture_index(mod_dirs, active)
    log(f"texture index: {len(tex)} loose PNGs")

    # Anything Biotech-side ships compiled into a Unity AssetBundle and has no
    # loose file at all, so fall back to whatever genome_art_cache.py extracted.
    cache_dir = out_dir / "art_cache"
    cache: dict[str, str] = {}
    if cache_dir.is_dir():
        for f in cache_dir.iterdir():
            if f.suffix.lower() == ".png":
                cache[f.stem.replace("%", "/").lower()] = str(f)
    log(f"bundle art cache: {len(cache)} PNGs")

    from_loose = from_bundle = 0
    for rec in list(genes.values()) + list(xenotypes.values()):
        ip = rec.get("iconPath")
        if not ip:
            rec["iconFile"] = None
            continue
        key = ip.lower().replace("\\", "/")
        if key in tex:
            rec["iconFile"] = tex[key]
            from_loose += 1
        elif key in cache:
            rec["iconFile"] = cache[key]
            from_bundle += 1
        else:
            rec["iconFile"] = None
    log(f"icons resolved: {from_loose} loose, {from_bundle} from bundles")

    unresolved = sum(1 for g in genes.values() if g.get("iconPath") and not g["iconFile"])
    log(f"genes with an iconPath but no PNG found: {unresolved}")

    (out_dir / "genes.json").write_text(
        json.dumps(genes, indent=1, sort_keys=True), encoding="utf-8")
    (out_dir / "xenotypes.json").write_text(
        json.dumps(xenotypes, indent=1, sort_keys=True), encoding="utf-8")
    (out_dir / "scan_manifest.json").write_text(json.dumps({
        "activeMods": len(active),
        "modFolders": len(mod_dirs),
        "genes": len(genes),
        "genesGenerated": len(generated),
        "xenotypes": len(xenotypes),
        "texturesIndexed": len(tex),
        "genesMissingIcon": unresolved,
        "gameVersion": GAME_VERSION,
    }, indent=1), encoding="utf-8")
    log(f"wrote {out_dir}/genes.json, xenotypes.json, scan_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
