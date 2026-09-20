#!/usr/bin/env python3
"""build_desert_review_sheet.py — the desert family flora+fauna review sheet, 2026-09-20.

Scope (coordinator-revised mid-build, 2026-09-20): three BiomeDefs treated as one
family, one sheet —
  RUT_ExtremeDesert (3,969 tiles), RUT_Desert (2,390 tiles),
  RUT_AridShrubland (628 tiles).
RUT_BlueDesert was dropped from scope — NOT because it is "deliberately
sterile" or "by design" (an earlier, WRONG claim in this build, retracted by
the coordinator): its empty <wildAnimals/> and absent <wildPlants> exist
because the biome's intended life (Swallowers, Burners, Pickers fauna; the
transparent fractal flora) was COMMISSIONED in
design/Jawa/worldbuilding/biomes/the_blue_desert.md and NEVER AUTHORED — the
def's own comment says density was zeroed only because "nothing to scale
until [those defs] exist". A verdict sheet reviews roster entries that
already exist; this biome has none yet, so it needs AUTHORING, not a verdict
pass (tracked as its own item, filed separately).

Unlike RotSporeKit's build_review_sheet.py and LanternDeeps's
build_species_sheet.py (both hand-literal Python tables), THIS generator is
fully DATA-DRIVEN: every row is parsed straight from the three BiomeDef XML
files with xml.etree.ElementTree (never string/regex matching — see the <li>
and descriptionHyperlinks traps in CLAUDE.md), and every def's label,
description, texPath and size are resolved live from the owning mod's own XML,
never hand-transcribed. This was a deliberate choice, not an oversight: the Rot
and Deeps sheets cover ~20-50 owned/near-owned species each, hand-curated in one
sitting; the desert family's wildAnimals/wildPlants tables carry ~140 raw
entries across 6+ donor mods (Star Wars Animal Collection alone contributes
~140 planet-wide), which is squarely in "a table goes stale and gets
transcribed wrong twice" territory this project has already paid for once
(RotSporeKit visualSizeRange, see that script's own header note). Parsing is
strictly cheaper and cannot drift from the def.

Origin resolution rule (coordinator correction, 2026-09-20): the ORIGIN column
names the real packageId from each entry's own MayRequire attribute — NEVER
inferred from the defName's prefix, because Star Wars Animal Collection ships
BARE defNames (Bantha, Kreetle, Scavrat, Rat-lookalikes, Plant_ names) that a
prefix rule misreads as vanilla. Entries with NO MayRequire attribute that are
not one of our own defs are UNGUARDED — flagged with their own visible marker
(a distinct badge + filter), never silently defaulted to vanilla. Every
unguarded defName's real owning mod was independently resolved by a scoped grep
against the specific candidate mod root (never a blind full-workshop scan —
see UNGUARDED_ORIGIN below and the build report for how each was found).

Usage:
    python3 build_desert_review_sheet.py             # dry run: prints the plan, writes nothing
    python3 build_desert_review_sheet.py --apply      # writes the sheet + thumbnails + decisions seed

Then review it:
  python3 <review-sheets skill>/assets/check_sheet.py <out.html> --decisions <out.decisions.json>
  python3 <review-sheets skill>/assets/serve_sheet.py --sheet <out.html> --decisions <out.decisions.json>
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = Path("/home/mandrake/.claude/skills/review-sheets/assets/sheet_template.html")

STAMP = "2026-09-20"
OUT_HTML = REPO_ROOT / "Transient" / f"desert_family_review_{STAMP}.html"
OUT_THUMBS_DIR = REPO_ROOT / "Transient" / f"desert_family_review_thumbs_{STAMP}"
OUT_DECISIONS = REPO_ROOT / "Transient" / f"desert_family_review_{STAMP}.decisions.json"
SHEET_ID = f"desert_family_review_{STAMP}"

THUMB_MAX = 160
PX_PER_CELL = 64
HUMAN_CELLS = 1.5
PANEL_MAX_PX = 240
HUMAN_ANCHOR = REPO_ROOT / "design" / "Jawa" / "worldbuilding" / "review" / "assets" / "human_anchor_south.png"

BIOME_DEFS_DIR = REPO_ROOT / "src" / "RimUtinni" / "UtinniPatches" / "Defs" / "BiomeDefs"
BIOMES = {
    "RUT_ExtremeDesert": {"file": BIOME_DEFS_DIR / "RUT_ExtremeDesert.xml", "tiles": 3969},
    "RUT_Desert": {"file": BIOME_DEFS_DIR / "RUT_Desert.xml", "tiles": 2390},
    "RUT_AridShrubland": {"file": BIOME_DEFS_DIR / "RUT_AridShrubland.xml", "tiles": 628},
}
BIOME_ORDER = ["RUT_ExtremeDesert", "RUT_Desert", "RUT_AridShrubland"]
BIOME_SHORT = {"RUT_ExtremeDesert": "ExtremeDesert", "RUT_Desert": "Desert", "RUT_AridShrubland": "AridShrubland"}

WORKSHOP = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")
GAME_DATA = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
BUNDLE_CACHE = REPO_ROOT / "observed" / "inventory" / "bundle_textures"

# MayRequire packageId (as it appears in the biome XML, lowercased for lookup)
# -> (display name, live def root for THIS mod's own XML, live texture root).
# Roots confirmed present on disk 2026-09-20 (see build report for how each
# workshop id was found: About.xml packageId scan, never a blind file scan).
MOD_INFO = {
    "mlie.starwarsanimalcollection": ("Star Wars Animal Collection (mlie)",
                                       WORKSHOP / "3497316713"),
    "sarg.alphaanimals": ("Alpha Animals (sarg)", WORKSHOP / "1541721856"),
    "sarg.alphabiomes": ("Alpha Biomes (sarg)", WORKSHOP / "1841354677"),
    "oskarpotocki.vfe.insectoid2": ("VFE — Insectoids 2 (Oskar Potocki)", WORKSHOP / "3309003431"),
    "neronix17.outerrim.droiddepot": ("Outer Rim — Droid Depot (neronix17)", WORKSHOP / "3096501398"),
    "mlie.horrors": ("Horrors (mlie)", WORKSHOP / "3535224844"),
    "regrowth.botr.core": ("ReGrowth 2 (BOTR core)", WORKSHOP / "2260097569"),
    "mandrake.rsw.swbestiary": ("OURS — SWBestiary", REPO_ROOT / "src" / "RimStarWars" / "SWBestiary"),
    "mandrake.rut.patches": ("OURS — UtinniPatches", REPO_ROOT / "src" / "RimUtinni" / "UtinniPatches"),
    "ludeon.rimworld": ("Vanilla Core", GAME_DATA / "Core"),
    "ludeon.rimworld.biotech": ("Vanilla Biotech DLC", GAME_DATA / "Biotech"),
    "ludeon.rimworld.odyssey": ("Vanilla Odyssey DLC", GAME_DATA / "Odyssey"),
    "ludeon.rimworld.royalty": ("Vanilla Royalty DLC", GAME_DATA / "Royalty"),
    "ludeon.rimworld.anomaly": ("Vanilla Anomaly DLC", GAME_DATA / "Anomaly"),
    "ludeon.rimworld.ideology": ("Vanilla Ideology DLC", GAME_DATA / "Ideology"),
}

# Entries with NO MayRequire attribute in the biome XML that are not one of our
# own defs ("JOE_Landopus" / "mandrake.rut.patches" excepted, see below) — each
# independently resolved 2026-09-20 by a SCOPED grep against a specific
# candidate mod root (never a blind full-workshop scan, which timed out at
# 120s when tried). defName -> MayRequire-equivalent packageId key into
# MOD_INFO above. This is the UNGUARDED set the coordinator asked to be
# flagged, not "fixed".
UNGUARDED_ORIGIN = {
    # RUT_Desert wildPlants
    "AB_HardyGrass": "sarg.alphabiomes",
    "Plant_Chakroot_Wild": "mlie.starwarsanimalcollection",
    "Plant_HubbaGourd_Wild": "mlie.starwarsanimalcollection",
    "AB_Aaklac": "sarg.alphabiomes",
    "AB_DessertTree": "sarg.alphabiomes",  # lives under AlphaBiomes' 1.6/Mods/Odyssey subfolder
    # RUT_Desert / RUT_ExtremeDesert / RUT_AridShrubland wildAnimals
    "JOE_Landopus": "mandrake.rut.patches",   # OURS per the biome file's own comment
    "Rat": "ludeon.rimworld",                 # vanilla Core; correctly needs no guard
    # RUT_ExtremeDesert wildPlants
    "Plant_Bloddle": "mlie.starwarsanimalcollection",
    "AB_GiantStikehr": "sarg.alphabiomes",
    # RUT_AridShrubland wildPlants
    "Plant_ShrubLow": "ludeon.rimworld",
    "RG_Plant_AridGrass": "regrowth.botr.core",
    "Plant_Brambles": "ludeon.rimworld",
    "Plant_Bush": "ludeon.rimworld",
    "Plant_Ripthorn": "ludeon.rimworld.biotech",
    "Plant_HealrootWild": "ludeon.rimworld",
    "Plant_Nysyllin_Wild": "mlie.starwarsanimalcollection",
    "RG_Plant_CreepStern": "regrowth.botr.core",
    "RG_Plant_CrimsonCushion": "regrowth.botr.core",
    "RG_Plant_Dervish": "regrowth.botr.core",
}

OUR_PACKAGE_KEYS = {"mandrake.rsw.swbestiary", "mandrake.rut.patches"}


# ============================================================================
# 1. PARSE THE BIOME DEFS — ElementTree only, direct-child shape (MEASURED:
#    all three files use <TagIsDefName comm="text">, never the <li> shape —
#    but the parser still checks for <li> and reports rather than silently
#    mis-reading if a future biome file uses it).
# ============================================================================

def parse_roster_block(el):
    """Yield (defName, commonality_or_None, mayRequire_or_None) for a
    <wildAnimals>/<wildPlants> element, handling both the direct-child shape
    (all three desert files) and the <li> shape (other biomes in this repo),
    so this parser is not silently wrong if reused elsewhere."""
    if el is None:
        return
    for child in el:
        if child.tag == "li":
            name_el = child.find("animal")
            if name_el is None:
                name_el = child.find("plant")
            if name_el is None:
                name_el = child.find("defName")
            comm_el = child.find("commonality")
            name = (name_el.text or "").strip() if name_el is not None else None
            comm = None
            if comm_el is not None and comm_el.text and comm_el.text.strip():
                comm = float(comm_el.text.strip())
            if name:
                yield name, comm, child.get("MayRequire")
        else:
            name = child.tag
            comm = float(child.text.strip()) if child.text and child.text.strip() else None
            yield name, comm, child.get("MayRequire")


def parse_biome(biome_name, path):
    tree = ET.parse(path)
    bd = tree.getroot().find("BiomeDef")
    if bd is None:
        raise ValueError(f"{path}: no <BiomeDef> found")
    animals = list(parse_roster_block(bd.find("wildAnimals")))
    plants = list(parse_roster_block(bd.find("wildPlants")))
    return animals, plants


def build_roster():
    """defName -> {'kind': 'animal'|'plant', 'biomes': {biome: (comm, mayRequire)}}"""
    roster = {}
    per_biome_counts = {}
    for biome_name in BIOME_ORDER:
        animals, plants = parse_biome(biome_name, BIOMES[biome_name]["file"])
        per_biome_counts[biome_name] = {"animals": len(animals), "plants": len(plants)}
        for defname, comm, mreq in animals:
            e = roster.setdefault(defname, {"kind": "animal", "biomes": {}})
            e["biomes"][biome_name] = (comm, mreq)
        for defname, comm, mreq in plants:
            e = roster.setdefault(defname, {"kind": "plant", "biomes": {}})
            e["biomes"][biome_name] = (comm, mreq)
    return roster, per_biome_counts


def origin_key_for(defname, mreq):
    """The MOD_INFO key this entry belongs to, and whether it was unguarded."""
    if mreq:
        return mreq.lower(), False
    if defname in UNGUARDED_ORIGIN:
        return UNGUARDED_ORIGIN[defname], True
    # Should not happen for the desert family (every entry was resolved above)
    # but never silently mislabel — surface it instead.
    return None, True


# ============================================================================
# 2. RESOLVE EACH DEF'S OWN XML — label, description, texPath, size.
#    One index per mod root, built once and cached; ThingDef AND PawnKindDef
#    both indexed by defName (both conventions in this donor set put the
#    PawnKindDef in the same file as its race ThingDef, same defName).
# ============================================================================

_ROOT_INDEX_CACHE = {}


def _index_root(root):
    """key -> {'ThingDef': el, 'PawnKindDef': el} across every *.xml under
    root, keyed by BOTH defName and the ParentName-referenceable Name=
    attribute (often the same string on a concrete leaf def, but abstract
    parents carry ONLY Name=, no defName — skipping those would break the
    ParentName chain walk below at the very first hop). Scoped to one mod
    root at a time (never the whole Workshop tree)."""
    if root in _ROOT_INDEX_CACHE:
        return _ROOT_INDEX_CACHE[root]
    idx = {}
    if root and root.exists():
        for f in root.rglob("*.xml"):
            try:
                tree = ET.parse(f)
            except ET.ParseError:
                continue
            for tag in ("ThingDef", "PawnKindDef"):
                for el in tree.getroot().iter(tag):
                    dn = el.findtext("defName")
                    nm = el.get("Name")
                    for key in (dn, nm):
                        if key:
                            idx.setdefault(key.strip(), {})[tag] = el
    _ROOT_INDEX_CACHE[root] = idx
    return idx


def _walk_chain_first(el, idx, tag, getter, max_hops=8):
    """Walk el's ParentName chain (via idx, same-root only) returning the
    first non-None result of getter(node). Used so a leaf def that overrides
    nothing but plant/wildCluster* (the 'X_Wild' donor pattern — description,
    graphicData and visualSizeRange all live on the CULTIVATED parent def)
    still resolves real values instead of reading as UNMEASURED."""
    seen = set()
    node = el
    hops = 0
    while node is not None and hops < max_hops:
        key = node.findtext("defName") or node.get("Name")
        if key in seen:
            break
        seen.add(key)
        val = getter(node)
        if val is not None:
            return val
        parent_name = node.get("ParentName")
        node = idx.get(parent_name, {}).get(node.tag) if parent_name else None
        hops += 1
    return None


def resolve_def(defname, origin_key):
    """-> dict with label, description, thingdef_el, pawnkind_el, mod_root, or
    None fields where nothing was found (never silently substituted). label/
    description walk the ParentName chain (the 'X_Wild' donor pattern ships
    only wildCluster*/sowTags on the leaf def, inheriting everything else)."""
    info = MOD_INFO.get(origin_key)
    root = info[1] if info else None
    idx = _index_root(root) if root else {}
    hit = idx.get(defname, {})
    td = hit.get("ThingDef")
    pkd = hit.get("PawnKindDef")
    label = None
    desc = None
    if td is not None:
        label = _walk_chain_first(td, idx, "ThingDef", lambda n: n.findtext("label"))
        desc = _walk_chain_first(td, idx, "ThingDef", lambda n: n.findtext("description"))
    if desc is None and pkd is not None:
        desc = pkd.findtext("description")
    if label is None and pkd is not None:
        label = pkd.findtext("label")
    return {"thingdef": td, "pawnkind": pkd, "label": label, "description": desc, "root": root, "idx": idx}


# ============================================================================
# 3. FAUNA SIZE — adult (LAST) lifeStage's bodyGraphicData.drawSize.
#    🔴 Never li[0] — that is the baby. Always the last <li> under <lifeStages>.
# ============================================================================

def fauna_adult_drawsize_and_tex(pkd):
    if pkd is None:
        return None, None
    stages = pkd.find("lifeStages")
    if stages is None:
        return None, None
    lis = stages.findall("li")
    if not lis:
        return None, None
    last = lis[-1]
    bgd = last.find("bodyGraphicData")
    if bgd is None:
        return None, None
    ds_txt = bgd.findtext("drawSize")
    tex = bgd.findtext("texPath")
    try:
        ds = float(ds_txt.strip()) if ds_txt else None
    except ValueError:
        ds = None
    return ds, tex


# ============================================================================
# 4. FLORA SIZE — drawSize.x * visualSizeRange.max, resolved by walking the
#    def's ParentName chain (the donor 'X_Wild' pattern ships only
#    wildCluster*/sowTags on the leaf def; graphicData AND visualSizeRange
#    live on the cultivated parent def it inherits from — RotSporeKit's own
#    build_review_sheet.py paid for this exact lesson on visualSizeRange, see
#    its header note). A row where nothing in the reachable chain sets a
#    field is reported UNMEASURED, never guessed at a default.
# ============================================================================

def flora_size(td, idx=None):
    if td is None:
        return None, None, None, None
    idx = idx or {}
    gd = _walk_chain_first(td, idx, "ThingDef", lambda n: n.find("graphicData"))
    draw = None
    tex = None
    gclass = None
    if gd is not None:
        dtxt = gd.findtext("drawSize")
        draw = float(dtxt.strip()) if dtxt else 1.0
        tex = gd.findtext("texPath")
        gclass = gd.findtext("graphicClass")
    vsr_text = _walk_chain_first(
        td, idx, "ThingDef",
        lambda n: (n.find("plant").findtext("visualSizeRange") if n.find("plant") is not None else None))
    vmin = vmax = None
    if vsr_text and "~" in vsr_text:
        lo, hi = vsr_text.split("~")
        vmin, vmax = float(lo), float(hi)
    return draw, (vmin, vmax) if vmax is not None else None, tex, gclass


# ============================================================================
# 5. THUMBNAIL RESOLUTION — loose PNG suffix ladder (reading-rimworld-graphics
#    skill): bare / _south / directory-listing (Graphic_Random 'A' suffix,
#    both bare-letter and underscore-letter forms) — falls back to the
#    project's own bundle_textures cache (observed/inventory/bundle_textures)
#    for sources with no live loose-PNG root (mlie.horrors) or for vanilla
#    Core/DLC (resources.assets, already extracted there).
# ============================================================================

def _candidates_for_tex(tex_path):
    """All the filenames this texPath could resolve to, richest-first."""
    stem = tex_path.rsplit("/", 1)[-1]
    parent = tex_path.rsplit("/", 1)[0] if "/" in tex_path else ""
    out = []
    # direct file forms
    for suf in ("_south", "", "_a", "_A"):
        out.append(f"{tex_path}{suf}.png")
    # Graphic_Random directory forms: <dir>/<stem><LETTER>[.png] and
    # <dir>/<stem>/<stem><LETTER>.png (dir-per-plant convention)
    for letter in "ABCDEFGH":
        out.append(f"{tex_path}{letter}.png")
        out.append(f"{parent}/{stem}/{stem}{letter}.png" if parent else f"{stem}/{stem}{letter}.png")
    # Third form: the letter lands as an INFIX before the last '_' segment,
    # e.g. Grass_Leafless -> GrassA_Leafless (reading-rimworld-graphics skill).
    if "_" in stem:
        head, tail = stem.rsplit("_", 1)
        for letter in "ABCDEFGH":
            infix = f"{head}{letter}_{tail}"
            out.append(f"{parent}/{infix}.png" if parent else f"{infix}.png")
    return out


def find_loose(root, tex_path):
    if not root or not tex_path:
        return None
    tex_root_candidates = [root / "Textures", root]
    for tr in tex_root_candidates:
        if not tr.exists():
            continue
        for cand in _candidates_for_tex(tex_path):
            p = tr / cand
            if p.exists():
                return p
        # last resort: list the directory the texPath implies and grab the
        # first PNG (Graphic_Random / Graphic_Multi container the ladder
        # above didn't spell correctly)
        d = tr / tex_path
        if d.is_dir():
            pngs = sorted(d.glob("*.png"))
            if pngs:
                return pngs[0]
    return None


_BUNDLE_CACHE_INDEX = {}


def _index_bundle_source(source_key):
    """List every PNG under observed/inventory/bundle_textures/<source_key>,
    once. These are already-extracted local caches (hundreds to low
    thousands of files each) — walking them is not the blind full-Workshop
    scan the skill warns against, it's exactly the 'build once, query the
    cache' pattern it recommends. Cached extraction preserves the container
    path (mlie.starwarsanimalcollection/textures/swanimals/bantha/
    banthaw_south.png), which is what makes matching by trailing segments
    against the def's texPath possible at all — a flat m_Name-keyed lookup
    would collide (see reading-rimworld-graphics skill)."""
    if source_key in _BUNDLE_CACHE_INDEX:
        return _BUNDLE_CACHE_INDEX[source_key]
    src_dir = BUNDLE_CACHE / source_key
    files = list(src_dir.rglob("*.png")) if src_dir.exists() else []
    _BUNDLE_CACHE_INDEX[source_key] = files
    return files


def _stem_matches(fname_lower, stem_lower):
    """fname_lower is the candidate file's stem, stem_lower is the texPath's
    own stem — both already lowercased. Covers all three Graphic_Random
    forms from the reading-rimworld-graphics skill: bare suffix (Bryolux ->
    BryoluxA), underscore suffix (Shell_Firefoam -> Shell_Firefoam_a), and
    infix before the last '_' (Grass_Leafless -> GrassA_Leafless)."""
    if fname_lower == stem_lower or fname_lower.startswith(stem_lower):
        return True
    if "_" in stem_lower:
        head, tail = stem_lower.rsplit("_", 1)
        if fname_lower.startswith(head) and fname_lower.endswith(f"_{tail}"):
            mid = fname_lower[len(head):-len(tail) - 1]
            if len(mid) <= 2:  # a single inserted variant letter, at most
                return True
    return False


def find_bundle_cache(source_key, tex_path):
    """Match a def's texPath (e.g. 'swanimals/Bantha/BanthaW') against the
    cached extraction's container-derived file paths (e.g. .../swanimals/
    bantha/banthaw_south.png) by trailing path segments, case-insensitive —
    the container path runs deeper than the texPath, so segments are
    compared from the right-hand end, same method as reading-rimworld-
    graphics' resolve_texture(). Prefers a _south suffix, then bare."""
    files = _index_bundle_source(source_key)
    if not files:
        return None
    want_segs = [s.lower() for s in tex_path.split("/") if s]
    stem = want_segs[-1] if want_segs else ""
    best, best_score, best_pref = None, -1, -1
    for f in files:
        fname = f.stem.lower()
        if not _stem_matches(fname, stem):
            continue
        have_dirs = [p.lower() for p in f.relative_to(BUNDLE_CACHE / source_key).parts[:-1]]
        score = 0
        for a, b in zip(reversed(want_segs[:-1]), reversed(have_dirs)):
            if a == b:
                score += 1
            else:
                break
        pref = 2 if fname == f"{stem}_south" else (1 if fname == stem else 0)
        if (score, pref) > (best_score, best_pref):
            best, best_score, best_pref = f, score, pref
    return best


# origin_key (MOD_INFO's key) -> the folder name this project's own
# bundle_textures cache actually used when it extracted that source (these
# differ from MOD_INFO's packageId keys in a couple of cases — MEASURED
# against the live cache directory listing, 2026-09-20).
CACHE_KEY_ALIASES = {
    "ludeon.rimworld": ["ludeon.rimworld.core"],
    "ludeon.rimworld.biotech": ["ludeon.rimworld.biotech"],
    "ludeon.rimworld.odyssey": ["ludeon.rimworld.odyssey"],
    "mlie.starwarsanimalcollection": ["mlie.starwarsanimalcollection"],
    "neronix17.outerrim.droiddepot": ["neronix17.outerrim.droiddepot"],
    "mlie.horrors": ["mlie.horrors"],
    "regrowth.botr.core": ["regrowth.botr.core"],
}


def resolve_thumbnail(origin_key, tex_path, kind):
    """-> (Path or None, note). Tries loose PNG in the def's own mod root
    first (cheap, exact), then this repo's own bundle_textures cache for
    sources that ship AssetBundle-only art (confirmed for Star Wars Animal
    Collection, 2026-09-20 — its Textures/ folder holds no loose PNGs at
    all, only an AssetBundle; UnityPy is not available on this machine's
    python3, so the already-extracted cache is the only route)."""
    if not tex_path:
        return None, "def declares no texPath"
    info = MOD_INFO.get(origin_key)
    root = info[1] if info else None
    p = find_loose(root, tex_path)
    if p:
        return p, "loose PNG, own mod"
    for k in CACHE_KEY_ALIASES.get(origin_key, [origin_key]):
        p = find_bundle_cache(k, tex_path)
        if p:
            return p, f"bundle_textures cache ({k})"
    # Last resort, ranked below every path match (reading-rimworld-graphics
    # skill): donor biome packs routinely reuse vanilla Core plant/animal art
    # wholesale rather than shipping their own (AB_Bryolux/AB_Agarilux in the
    # Rot sheet were exactly this) — try Core's own cache regardless of this
    # entry's actual origin mod.
    if origin_key != "ludeon.rimworld":
        p = find_bundle_cache("ludeon.rimworld.core", tex_path)
        if p:
            return p, "bundle_textures cache (ludeon.rimworld.core, vanilla reuse — donor ships no art of its own)"
    return None, "no loose PNG and no bundle_textures cache entry"


# ============================================================================
# 6. TO-SCALE THUMBNAIL PANELS — same method as
#    src/RimMandrake/Utils/gen_plant_register.py / gen_creature_register.py and
#    RotSporeKit's build_review_sheet.py (copied rather than imported — those
#    modules pull in cherrypicker/game_paths/rimworld_loadset machinery this
#    generator's parser-driven rows don't need). PX_PER_CELL/HUMAN_CELLS match
#    exactly; PANEL_MAX_PX (240) is this sheet's own row-thumbnail cap.
# ============================================================================

def _human_figure(hh, Image):
    from PIL import ImageDraw
    try:
        im = Image.open(HUMAN_ANCHOR).convert("RGBA")
        k = hh / float(im.height)
        return im.resize((max(1, int(im.width * k)), hh), Image.LANCZOS)
    except Exception:                                        # noqa: BLE001
        fig = Image.new("RGBA", (max(6, int(hh * 0.45)), hh), (0, 0, 0, 0))
        ImageDraw.Draw(fig).rectangle([0, 0, fig.width - 1, hh - 1],
                                       outline=(255, 80, 80, 255))
        return fig


def _cap_panel(panel, Image):
    if max(panel.size) > PANEL_MAX_PX:
        k = PANEL_MAX_PX / float(max(panel.size))
        panel = panel.resize((max(1, int(panel.width * k)), max(1, int(panel.height * k))),
                              Image.LANCZOS)
    return panel


def make_thumb(src, dst):
    from PIL import Image
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        im.save(dst)


def make_plant_scale_panel(src, dst, cells):
    from PIL import Image, ImageDraw
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as raw:
        im = raw.convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        hh = int(round(HUMAN_CELLS * PX_PER_CELL))
        fig = _human_figure(hh, Image)
        fig_w = fig.width
        quad = max(8, int(round(cells * PX_PER_CELL)))
        gap, pad = 12, 8
        tw = pad + fig_w + gap + quad + pad
        th = pad + max(hh, quad) + pad
        panel = Image.new("RGBA", (tw, th), (16, 22, 18, 255))
        d = ImageDraw.Draw(panel)
        for x in range(pad, tw, PX_PER_CELL):
            d.line([(x, 0), (x, th)], fill=(32, 42, 34, 255))
        for y in range(th - pad, -1, -PX_PER_CELL):
            d.line([(0, y), (tw, y)], fill=(32, 42, 34, 255))
        base_y = th - pad
        panel.alpha_composite(fig, (pad, base_y - hh))
        k = min(quad / float(im.width), quad / float(im.height))
        cw, ch = max(1, int(round(im.width * k))), max(1, int(round(im.height * k)))
        spr = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)
        left = pad + fig_w + gap
        panel.alpha_composite(spr, (left, base_y - ch))
        panel = _cap_panel(panel, Image)
        panel.convert("RGB").save(dst, optimize=True)


def make_creature_scale_panel(src, dst, cells):
    from PIL import Image, ImageDraw
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as raw:
        im = raw.convert("RGBA")
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        box = max(8, int(round(cells * PX_PER_CELL)))
        hh = int(round(HUMAN_CELLS * PX_PER_CELL))
        k = min(box / float(im.width), box / float(im.height))
        cw, ch = max(1, int(round(im.width * k))), max(1, int(round(im.height * k)))
        fig = _human_figure(hh, Image)
        fig_w = fig.width
        gap, pad = 12, 8
        tw = pad + fig_w + gap + cw + pad
        th = pad + max(hh, ch) + pad
        panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
        d = ImageDraw.Draw(panel)
        for x in range(pad, tw, PX_PER_CELL):
            d.line([(x, 0), (x, th)], fill=(34, 39, 47, 255))
        for y in range(th - pad, -1, -PX_PER_CELL):
            d.line([(0, y), (tw, y)], fill=(34, 39, 47, 255))
        base_y = th - pad
        panel.alpha_composite(fig, (pad, base_y - fig.height))
        cre = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)
        panel.alpha_composite(cre, (pad + fig_w + gap, base_y - ch))
        panel = _cap_panel(panel, Image)
        panel.convert("RGB").save(dst, optimize=True)


# ============================================================================
# 7. BUILD ROWS — fully data-driven: no literal row table anywhere above this
#    point except MOD_INFO (mod roots, a fact about disk layout) and
#    UNGUARDED_ORIGIN (a fact about which mod owns which unguarded defName,
#    independently resolved per-entry, see the module docstring).
# ============================================================================

def biome_membership_text(biomes):
    parts = []
    for b in BIOME_ORDER:
        if b in biomes:
            comm, mreq = biomes[b]
            ctxt = f"{comm}" if comm is not None else "?"
            parts.append(f"{BIOME_SHORT[b]}={ctxt}")
    return ", ".join(parts)


def truncate(text, n=220):
    if not text:
        return None
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def build_items():
    roster, per_biome_counts = build_roster()
    items = []
    thumb_jobs = []
    unresolved_thumbs = []
    unresolved_defs = []
    origin_counts = {}

    for defname in sorted(roster.keys()):
        entry = roster[defname]
        kind = entry["kind"]
        biomes = entry["biomes"]
        # origin: take it from whichever biome carries a MayRequire/guard fact;
        # all biomes sharing a defName carry the same donor, but a defName
        # could in principle be guarded in one file and not another — use the
        # first biome (BIOME_ORDER) that has a MayRequire, else fall back to
        # the UNGUARDED_ORIGIN resolution.
        mreq = None
        for b in BIOME_ORDER:
            if b in biomes and biomes[b][1]:
                mreq = biomes[b][1]
                break
        origin_key, unguarded = origin_key_for(defname, mreq)
        mod_display = MOD_INFO.get(origin_key, (f"UNRESOLVED ({origin_key})", None))[0] if origin_key else "UNRESOLVED"
        is_ours = origin_key in OUR_PACKAGE_KEYS
        origin_bucket = "OURS" if is_ours else ("VANILLA/DLC" if origin_key and origin_key.startswith("ludeon") else "DONOR")
        origin_counts.setdefault(origin_bucket, 0)
        origin_counts[origin_bucket] += 1

        resolved = resolve_def(defname, origin_key)
        label = resolved["label"] or defname
        desc = truncate(resolved["description"])
        if desc is None:
            unresolved_defs.append(defname)

        if kind == "animal":
            ds, tex = fauna_adult_drawsize_and_tex(resolved["pawnkind"])
            sizetxt = f"adult bodyGraphicData.drawSize {ds:.2f}×{ds:.2f} cells (last lifeStage)" if ds is not None else "adult drawSize UNMEASURED (no PawnKindDef/lifeStages resolved)"
            mature_val = ds
        else:
            draw, vsr, tex, gclass = flora_size(resolved["thingdef"], resolved["idx"])
            if vsr:
                vmin, vmax = vsr
                d = draw if draw is not None else 1.0
                mature_val = d * vmax
                sizetxt = f"mature size {mature_val:.2f} cells (drawSize {d:.2f} × visualSizeRange max {vmax:.2f}, grows from {d*vmin:.2f})"
            else:
                mature_val = draw
                sizetxt = f"drawSize {draw:.2f}×{draw:.2f} cells; visualSizeRange UNMEASURED" if draw is not None else "size UNMEASURED (no graphicData/plant node resolved)"

        thumb_path, thumb_note = resolve_thumbnail(origin_key, tex, kind)
        thumb_rel = None
        if thumb_path:
            dst_name = re.sub(r"[^A-Za-z0-9_.-]", "_", defname) + ".png"
            dst_abs = OUT_THUMBS_DIR / dst_name
            dst_rel = f"{OUT_THUMBS_DIR.name}/{dst_name}"
            thumb_jobs.append({"kind": kind, "src": thumb_path, "dst": dst_abs,
                                "rel": dst_rel, "cells": mature_val or 1.0})
            thumb_rel = dst_rel
        else:
            unresolved_thumbs.append((defname, thumb_note))

        maxcomm = max((c for c, _ in biomes.values() if c is not None), default=None)
        bmembership = biome_membership_text(biomes)
        flags = []
        if unguarded:
            flags.append("⚠ UNGUARDED (no MayRequire guard on this entry)")
        if desc is None:
            flags.append("description UNRESOLVED")
        if thumb_path is None:
            flags.append(f"art UNRESOLVED ({thumb_note})")
        flagtxt = (" — " + "; ".join(flags)) if flags else ""

        effect = (f"[{mod_display}] in {bmembership}. {sizetxt}.{flagtxt} "
                  f"{desc or '(no description resolved)'}")

        items.append({
            "id": f"{'A' if kind == 'animal' else 'P'}_{defname}",
            "label": f"{label} [{defname}]",
            "group": "Fauna" if kind == "animal" else "Flora",
            "effect": effect,
            "thumb": thumb_rel,
            "prefill": "keep",
            "inferred": desc is None or thumb_path is None,
            "sortkey": -(maxcomm or 0),
            "meta": {
                "origin": mod_display,
                "unguarded": "YES" if unguarded else "no",
                "biomes": bmembership,
                "kind": kind,
            },
        })

    items.sort(key=lambda it: (it["group"], it["sortkey"]))
    for it in items:
        del it["sortkey"]
    return items, per_biome_counts, thumb_jobs, unresolved_thumbs, unresolved_defs, origin_counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sheet, thumbnails and decisions seed (default: dry run)")
    ap.add_argument("--i-know-this-overwrites-the-owners-decisions", action="store_true", dest="force_overwrite",
                    help="required to regenerate the decisions file if it already carries savedBy/writeCount")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"ERROR: sheet template not found at {TEMPLATE}", file=sys.stderr)
        return 1

    items, per_biome_counts, thumb_jobs, unresolved_thumbs, unresolved_defs, origin_counts = build_items()
    print(f"# build_desert_review_sheet.py plan — {len(items)} unique species rows")
    for b in BIOME_ORDER:
        c = per_biome_counts[b]
        print(f"  {b}: {c['animals']} wildAnimals entries, {c['plants']} wildPlants entries (raw, pre-dedup)")
    print(f"  origin: {origin_counts}")
    print(f"  {len(unresolved_thumbs)} rows with no art resolved, {len(unresolved_defs)} rows with no description resolved")
    for it in items:
        print(f"  [{'thumb' if it['thumb'] else 'NO-THUMB':8s}] {it['group']:6s} {it['id']}")

    if not args.apply:
        print(f"\nDry run only. Re-run with --apply to write:\n  {OUT_HTML}\n  {OUT_THUMBS_DIR}/*.png\n  {OUT_DECISIONS}")
        return 0

    if OUT_DECISIONS.exists():
        try:
            existing = json.loads(OUT_DECISIONS.read_text())
        except Exception:
            existing = {}
        if (existing.get("savedBy") or existing.get("writeCount")) and not args.force_overwrite:
            print(f"REFUSED: {OUT_DECISIONS} already carries savedBy/writeCount — the owner has reviewed this. "
                  f"Pass --i-know-this-overwrites-the-owners-decisions to overwrite anyway.", file=sys.stderr)
            return 1

    OUT_THUMBS_DIR.mkdir(parents=True, exist_ok=True)
    made, missing = 0, []
    for job in thumb_jobs:
        src, dst, kind = job["src"], job["dst"], job["kind"]
        if not src.exists():
            missing.append(str(src))
            continue
        try:
            if kind == "plant":
                make_plant_scale_panel(src, dst, job["cells"])
            elif kind == "animal":
                make_creature_scale_panel(src, dst, job["cells"])
            else:
                make_thumb(src, dst)
            made += 1
        except Exception as exc:
            missing.append(f"{src} ({exc})")
    print(f"\nThumbnails written: {made}; missing/failed: {len(missing)}")
    for m in missing:
        print(f"  NO THUMB: {m}")

    fauna_n = sum(1 for it in items if it["group"] == "Fauna")
    flora_n = sum(1 for it in items if it["group"] == "Flora")
    cfg = {
        "sheetId": SHEET_ID,
        "title": "Desert family — flora & fauna review",
        "subtitle": f"{len(items)} unique species — {flora_n} flora, {fauna_n} fauna — across RUT_ExtremeDesert (3,969 tiles), RUT_Desert (2,390 tiles), RUT_AridShrubland (628 tiles)",
        "briefHtml": (
            "<p><b>Posture: BLACKLIST.</b> Every row defaults to <b>keep</b>. Nothing is removed from a "
            "biome's roster unless you mark it otherwise — disagreeing is the whole point of this page.</p>"
            "<p>Three BiomeDefs, one sheet, because they share one donor-heavy roster problem. "
            "<b>RUT_BlueDesert was dropped from this pass</b>: it is UNAUTHORED, not sterile-by-design — its "
            "intended fauna (Swallowers, Burners, Pickers) and flora (transparent fractal life) were "
            "commissioned in the_blue_desert.md and never built, so animalDensity/plantDensity were zeroed "
            "because there is nothing yet to scale. A verdict sheet reviews roster entries that already exist; "
            "this biome has none yet — it needs authoring, tracked as its own item, not a verdict pass here.</p>"
            "<p>Every row's <b>[origin]</b> tag is the real packageId from that entry's own MayRequire "
            "attribute in the biome XML — never inferred from the defName's prefix. Star Wars Animal Collection "
            "(mlie) ships many BARE defNames (Bantha, Kreetle, Scavrat, Rat-lookalike plant names) that a "
            "prefix rule would misread as vanilla; it is in fact the single largest donor here.</p>"
            "<p><b>⚠ UNGUARDED rows</b> carry NO MayRequire attribute in the biome file at all, despite most of "
            "them belonging to a donor mod — each one's real owner was independently resolved by a scoped "
            "search (never a blind full-workshop scan) and is named in its origin tag. These are flagged, not "
            "fixed: no MayRequire attribute was added anywhere by this pass.</p>"
            "<p>This sheet is fully DATA-DRIVEN — every row is parsed live from the three BiomeDef XML files "
            "and every def's own label/description/texPath/size, never a hand-transcribed table (unlike the "
            "Rot and Deeps sheets) — see build_desert_review_sheet.py's module docstring for why.</p>"
            "<p><b>Size:</b> fauna rows print the ADULT (last) lifeStage's bodyGraphicData.drawSize — never "
            "life stage 0, which is the baby. Flora rows print drawSize × visualSizeRange.max (mature size), "
            "resolved from the def's own &lt;plant&gt; node only (no ParentName chain walk in this pass — "
            "rows that don't set their own visualSizeRange are marked UNMEASURED rather than guessed).</p>"
            "<p><b>Thumbnails:</b> resolved live from each donor mod's own loose Textures/ folder (suffix "
            "ladder: _south, bare, Graphic_Random A–H, both bare-letter and underscore forms, per the "
            "reading-rimworld-graphics skill), falling back to this repo's own extracted "
            "observed/inventory/bundle_textures cache for sources with no loose art (mlie.horrors) or for "
            "vanilla Core/DLC (resources.assets, already extracted there). A row with no thumbnail is marked "
            "'art UNRESOLVED' with the reason, never left silently blank.</p>"
        ),
        "criterion": "Sorted by MAX commonality across the biomes each species appears in, within Flora/Fauna — "
                     "ranks how often a player meets it in its worst-affected biome, not its worth or its art "
                     "quality.",
        "invented": [
            "Grouping is Flora/Fauna (not per-biome) because most species appear in 2-3 of the three biomes at "
            "once and a per-biome grouping would either duplicate rows or force a pick; each row's 'biomes' "
            "meta chip and the effect line's '[origin] in <BiomeShort=commonality, ...>' text name every "
            "biome + commonality it actually carries, so no membership fact is lost.",
            "The origin bucket for a defName with a MayRequire attribute present on one biome's entry but "
            "(hypothetically) absent on another was taken from whichever biome in ExtremeDesert/Desert/"
            "AridShrubland order carries a MayRequire first — not observed to matter for this roster (every "
            "shared defName in this set carries the same guard state on every biome that lists it), but "
            "stated here as the tie-break rule in case a future biome file disagrees.",
            "UNGUARDED_ORIGIN's 19 entries were each resolved by a scoped grep against ONE specific candidate "
            "mod root (Alpha Biomes, Star Wars Animal Collection, ReGrowth, vanilla Core/Biotech), never a "
            "blind full-Workshop scan — one such scan was tried and did not return within 120s. See the build "
            "report for which root matched which defName.",
            "AB_DessertTree resolves to a real ThingDef, but that def lives under Alpha Biomes' own "
            "1.6/Mods/Odyssey/ subfolder, which its LoadFolders.xml only loads when Ludeon.RimWorld.Odyssey is "
            "active — true on every campaign mod list per the 2026-09-19 all-five-expansions ruling, so this "
            "is not currently a stranded-folder gap, just worth naming.",
        ],
        "posture": {"mode": "blacklist", "explain": "Default is KEEP. A row only leaves a biome's wildAnimals/"
                    "wildPlants if you mark it cut."},
        "options": [
            {"key": "keep", "label": "Keep", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "retire", "label": "Retire (cut donor)", "hotkey": "2", "color": "#e06c6c", "counts": "out"},
            {"key": "replace", "label": "Replace with owned", "hotkey": "3", "color": "#6aa6e8", "counts": "in"},
            {"key": "undecided", "label": "Undecided", "hotkey": "4", "color": "#98a2b3", "counts": "in"},
        ],
        "groupLabel": "group",
        "media": True,
        "decisionsFile": OUT_DECISIONS.name,
        "decisionsPath": str(OUT_DECISIONS),
        "sheetPath": str(OUT_HTML),
    }

    html = TEMPLATE.read_text()
    html = re.sub(
        r'(<script id="CONFIG" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(cfg, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    html = re.sub(
        r'(<script id="ITEMS" type="application/json">\n).*?(\n</script>)',
        lambda m: m.group(1) + json.dumps(items, indent=2) + m.group(2),
        html, count=1, flags=re.S,
    )
    OUT_HTML.write_text(html)

    if not OUT_DECISIONS.exists() or args.force_overwrite:
        seed = {"sheetId": SHEET_ID, "posture": "blacklist", "frozen": False, "writeCount": 0, "decisions": {}}
        OUT_DECISIONS.write_text(json.dumps(seed, indent=2) + "\n")

    print(f"\nWrote {OUT_HTML}")
    print(f"Decisions file: {OUT_DECISIONS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
