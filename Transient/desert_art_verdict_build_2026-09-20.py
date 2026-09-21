#!/usr/bin/env python3
"""Builds the desert-family art verdict sheet (DESERT_FAMILY_PORT_EXECUTION_1).

HOW TO RE-RUN THIS AS MORE ART LANDS (the sheet is deliberately self-extending):
  1. python3 desert_art_verdict_build_2026-09-20.py
     (run from anywhere with src/RimMandrake/Utils on sys.path; add any newly
     `awaiting_verdict` creature's defName -> job-stem to the CREATURES dict
     at the top of this file first — check `artreg.py status` or
     `python3 -c "...artreg.build_status()..."` filtered to
     source=="DESERT_FAMILY_PORT_EXECUTION_1" for what's newly landed)
  2. python3 desert_art_verdict_assemble_2026-09-20.py
     (regenerates the .html from the intermediate JSON the step above writes;
     never touches an existing .decisions.json with real owner decisions in it)
  3. python3 <review-sheets skill>/assets/check_sheet.py <the .html> --decisions <the .decisions.json>
     must show 0 FAIL before handing back over.

Reuses:
  - artreg.build_status() for the live registry state (never hand-parsed)
  - animal_contact_sheet.build_texture_index()/resolve_texture() for donor art
  - the review-sheets skill's sheet_template.html chrome

Writes:
  - Transient/desert_art_verdict_2026-09-20.html
  - Transient/desert_art_verdict_2026-09-20.decisions.json (only if absent —
    never overwrites a decisions file that may hold real owner verdicts)
  - Transient/desert_verdict_assets/<creature>/{render,donor}_<facing>.png (copies)
  - Transient/_desert_verdict_build_data.json (intermediate; consumed by the
    assemble script, not committed — regenerate it, don't hand-edit it)
"""
from __future__ import annotations
import json, os, re, shutil, sys, pickle
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = Path("/mnt/d/Luke/dev/Rimworld")
UTILS = REPO / "src/RimMandrake/Utils"
ARTPIPE = REPO / "infrastructure/artpipe"
CANON = REPO / "design/RimStarWars/canon_references"
OUT_DIR = REPO / "Transient"
ASSETS = OUT_DIR / "desert_verdict_assets"
SHEET_ID = "desert_art_verdict_2026-09-20"
OUT_HTML = OUT_DIR / f"{SHEET_ID}.html"
OUT_DECISIONS = OUT_DIR / f"{SHEET_ID}.decisions.json"
CACHE = Path("/tmp/desert_art_verdict_texidx.pkl")  # rebuilt automatically if absent (~100s)

sys.path.insert(0, str(UTILS))
sys.path.insert(0, str(UTILS / "artpipe"))

# --------------------------------------------------------------------------
# 24 creatures ready for review (all facts=PASS in the live registry as of
# this build) mapped defName -> job stem. Kybuck is partial (north still
# `generated`, not yet in awaiting_verdict).
# --------------------------------------------------------------------------
CREATURES = {
    "RSW_Anooba": "desert_swaca_anooba",
    "RSW_Bantha": "desert_swaca_bantha",
    "RSW_Corinathoth": "desert_swaca_corinathoth",
    "RSW_Eopie": "desert_swaca_eopie",
    "RSW_FrilledGorg": "desert_swaca_frilledgorg",
    "RSW_Gizka": "desert_swaca_gizka",
    "RSW_Gorg": "desert_swaca_gorg",
    "RSW_Gutkurr": "desert_swaca_gutkurr",
    "RSW_Hrumph": "desert_swaca_hrumph",
    "RSW_Igitz": "desert_swaca_igitz",
    "RSW_Iriaz": "desert_swaca_iriaz",
    "RSW_IridonianReek": "desert_swaca_iridonianreek",
    "RSW_Jamel": "desert_swaca_jamel",
    "RSW_Jimvu": "desert_swaca_jimvu",
    "RSW_Kreetle": "desert_swaca_kreetle",
    "RSW_Kwi": "desert_swaca_kwi",
    "RSW_Kybuck": "desert_swaca_kybuck",
    "RSW_LongtailGorg": "desert_swaca_longtailgorg",
    "RSW_Lothcat": "desert_swaca_lothcat",
    "RSW_Massiff": "desert_swaca_massiff",
    "RSW_Mudhorn": "desert_swaca_mudhorn",
    "RSW_Mynock": "desert_swaca_mynock",
    "RSW_Nuna": "desert_swaca_nuna",
    "RSW_Pufferpig": "desert_swaca_pufferpig",
    # Ferroclaw's OWN desert-port job (desertportb_ferroclaw) is still `queued` —
    # nothing to look at yet. But an EARLIER job for the same creature
    # (aa_terramorph, source ART_REGEN_WAVE5_QUEUE_1) already has south+east
    # PASS sitting unreviewed (north FAILED, retried, still not passing) — real,
    # on-disk, PASS-validated art the owner has never seen. Shown under
    # RSW_Ferroclaw's own canon/donor info so he can judge it now rather than
    # wait for the redundant today's-wave job to also land.
    "RSW_Ferroclaw": "aa_terramorph",
}
CANON_SLUG_OVERRIDE = {
    "RSW_IridonianReek": None,  # no "reek"/"iridonianreek" entry exists — checked
}

FLAG_CUT_RULED = {"RSW_MossBeetle"}  # not in this 24 but kept for completeness


def find_xml_for_def(defname: str) -> Path | None:
    stem = defname[len("RSW_"):]
    cands = [
        REPO / f"src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_{stem}.xml",
        REPO / f"src/RimStarWars/SWBestiary/Defs/ShipVermin/ThingDefs_Races/RSW_{stem}.xml",
    ]
    for c in cands:
        if c.is_file():
            return c
    hits = list(REPO.glob(f"src/RimStarWars/SWBestiary/Defs/**/*{stem}*.xml"))
    if hits:
        return hits[0]
    # fallback: the def lives in a differently-named file (e.g. a *_Misc_Races.xml
    # grouping several small ports together) — grep for the exact defName tag.
    needle = f"<defName>{defname}</defName>"
    for p in REPO.glob("src/RimStarWars/SWBestiary/Defs/**/*.xml"):
        try:
            if needle in p.read_text(encoding="utf-8", errors="ignore"):
                return p
        except OSError:
            continue
    return None


def extract_def_info(defname: str) -> dict:
    """{"label": str, "texpaths": [texpath,...] in document order, last=adult}"""
    xml_path = find_xml_for_def(defname)
    if xml_path is None:
        return {"label": defname, "texpaths": [], "xml_path": None}
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return {"label": defname, "texpaths": [], "xml_path": str(xml_path)}
    root = tree.getroot()
    label = defname
    texpaths = []
    for tag in ("ThingDef", "PawnKindDef"):
        for td in root.iter(tag):
            dn = td.findtext("defName")
            if dn != defname:
                continue
            lab = td.findtext("label")
            if lab:
                label = lab
            # PawnKindDef-style: race/body via lifeStages -> bodyGraphicData/texPath
            for ls in td.findall(".//lifeStages/li"):
                tp = ls.findtext("bodyGraphicData/texPath") or ls.findtext("texPath")
                if tp:
                    texpaths.append(tp)
            # plain graphicData (buildings/items/plants use this; some animals too)
            tp = td.findtext("graphicData/texPath")
            if tp:
                texpaths.append(tp)
    return {"label": label, "texpaths": texpaths, "xml_path": str(xml_path)}


def main():
    from animal_contact_sheet import build_texture_index, TextureIndex
    print("== loading mod set + texture index (cached) ==")
    if CACHE.is_file():
        raw = pickle.loads(CACHE.read_bytes())
        index = TextureIndex(raw)
        print(f"loaded cached index: {len(index)} entries")
    else:
        from rimworld_loadset import build_load_set, DEFAULT_MODS_CONFIG
        from game_paths import WORKSHOP, LOCAL_MODS, GAME_DATA
        mods, missing, version = build_load_set(DEFAULT_MODS_CONFIG, [WORKSHOP, LOCAL_MODS, GAME_DATA])
        index, files_seen, dirs_seen = build_texture_index(mods)
        CACHE.write_bytes(pickle.dumps(dict(index)))
        print(f"built index: {len(index)} entries, {files_seen} files")

    def resolve_donor(texpaths: list[str], facing: str) -> str | None:
        """Try each candidate texpath stem with the facing suffix ladder."""
        for tp in reversed(texpaths):  # last = adult life stage, prefer it
            stem = tp.rstrip("/").lower()
            for suf in (f"_{facing}", ""):
                key = f"{stem}{suf}.png"
                if key in index:
                    return index[key]
            # directory form
            entries = index.dir_entries(stem) if hasattr(index, "dir_entries") else []
            for e in entries:
                if facing in e.lower():
                    return index[e]
            if entries:
                return index[entries[0]]
        return None

    print("== extracting def info ==")
    def_info = {d: extract_def_info(d) for d in CREATURES}
    for d, info in def_info.items():
        print(f"  {d}: label={info['label']!r} texpaths={info['texpaths']}")

    ASSETS.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    def copy_thumb(src: Path, dst: Path, max_side=320):
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(src) as im:
                im = im.convert("RGBA")
                w, h = im.size
                scale = min(1.0, max_side / max(w, h))
                if scale < 1.0:
                    im = im.resize((max(1, round(w*scale)), max(1, round(h*scale))), Image.NEAREST)
                im.save(dst, format="PNG", optimize=True)
            return True
        except Exception as exc:
            print(f"    WARN could not copy/thumb {src}: {exc}")
            return False

    sys.path.insert(0, str(UTILS / "artpipe"))
    import artreg, common as apcommon
    rows = [json.loads(l) for l in open(artreg.REGISTRY_PATH)]
    st = artreg.build_status()
    per = st["perTarget"]

    items = []
    canon_hits, canon_misses, donor_missing = [], [], []

    for defname, stem in sorted(CREATURES.items()):
        info = def_info[defname]
        slug = re.sub(r"[^a-z0-9]+", "", info["label"].lower())
        cdir = CANON / slug if (CANON / slug).is_dir() else None
        # try alternates: defName stem lowercased, first word
        if cdir is None:
            alt = defname[len("RSW_"):].lower()
            if (CANON / alt).is_dir():
                cdir = CANON / alt

        renders = {}
        donors = {}
        facings_present = []
        facings_missing = []
        for facing in ("south", "east", "north"):
            target = f"{stem}/{facing}"
            tinfo = per.get(target)
            state = tinfo.get("state") if tinfo else "not-registered"
            if state != "awaiting_verdict":
                facings_missing.append(f"{facing}:{state}")
                continue
            job_id = tinfo["job_ids"][-1]
            regen_src = apcommon.DEFAULT_ARTSRC / job_id / f"{job_id}.png"
            if not regen_src.is_file():
                facings_missing.append(f"{facing}:png-missing")
                continue
            dst = ASSETS / defname / f"render_{facing}.png"
            if copy_thumb(regen_src, dst):
                renders[facing] = f"desert_verdict_assets/{defname}/render_{facing}.png"
                facings_present.append(facing)

        # donor art
        donor_source = None
        for facing in ("south", "east", "north"):
            if cdir and (cdir / "donor_current_sprite.png").is_file() and facing == "south":
                src = cdir / "donor_current_sprite.png"
                dst = ASSETS / defname / f"donor_{facing}.png"
                if copy_thumb(src, dst):
                    donors[facing] = f"desert_verdict_assets/{defname}/donor_{facing}.png"
                    donor_source = "canon_reference"
                continue
            src = resolve_donor(info["texpaths"], facing)
            if src:
                dst = ASSETS / defname / f"donor_{facing}.png"
                if copy_thumb(Path(src), dst):
                    donors[facing] = f"desert_verdict_assets/{defname}/donor_{facing}.png"
                    donor_source = donor_source or "texture_index"

        if not donors:
            donor_missing.append(defname)

        # canon must-show
        must_show = []
        ruling_text = ""
        if cdir and (cdir / "description.md").is_file():
            text = (cdir / "description.md").read_text(encoding="utf-8", errors="replace")
            m = re.search(r"## Must show\n(.*?)\n##", text, re.S)
            if m:
                must_show = [l.strip("- []").strip() for l in m.group(1).splitlines() if l.strip().startswith("- [")]
            m2 = re.search(r"## ruling\n(.*?)(\n##|\Z)", text, re.S)
            if m2:
                ruling_text = m2.group(1).strip()
            canon_hits.append(defname)
        else:
            canon_misses.append(defname)

        primary_thumb = renders.get("south") or renders.get("east") or renders.get("north") or ""

        note_bits = []
        if facings_missing:
            note_bits.append("Missing/not-ready facings: " + ", ".join(facings_missing))
        if defname == "RSW_Kybuck":
            note_bits.append("PARTIAL: north facing still `generated` (not yet validated) — only east/south are ready to judge.")
        if defname == "RSW_Mynock":
            note_bits.append("RSW_Mynock already ships its OWN art (Mynock.png, from SHIP_VERMIN_MOD_1) — this is a NEW regen job under the desert-port wave; you are choosing between two pieces of OUR OWN art, not replacing donor art.")
        if defname == "RSW_Ferroclaw":
            note_bits.append("TWO ART JOBS EXIST for Ferroclaw. This row shows the EARLIER job (`aa_terramorph`, from ART_REGEN_WAVE5_QUEUE_1) — south+east PASS, north FAILED (retried, still not passing, so north is not shown). Today's desert-port job (`desertportb_ferroclaw`) is still QUEUED — nothing rendered yet, not shown. Reconcile before wiring either in: judge THIS art now, or wait for the redundant new job.")

        items.append({
            "id": defname,
            "label": info["label"],
            "group": "Ready for review" if len(facings_present) >= 2 else "Partial / needs attention",
            "thumb": primary_thumb,
            "meta": {
                "renders": renders,
                "donors": donors,
                "donor_source": donor_source,
                "must_show": must_show,
                "ruling": ruling_text,
                "canon_dir": str(cdir.relative_to(REPO)) if cdir else None,
                "job_stem": stem,
                "note_prefill": " ".join(note_bits),
            },
        })

    print(f"\ncanon entries found: {len(canon_hits)} ({canon_hits})")
    print(f"canon entries missing: {len(canon_misses)} ({canon_misses})")
    print(f"donor art NOT recovered for: {donor_missing}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "_desert_verdict_build_data.json").write_text(json.dumps(items, indent=2))
    print(f"\nwrote intermediate data: {OUT_DIR / '_desert_verdict_build_data.json'}")
    print(f"total rows: {len(items)}")


if __name__ == "__main__":
    main()
