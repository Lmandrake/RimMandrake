#!/usr/bin/env python3
"""build_review_deck.py — the per-biome fauna+flora examination deck.

Assembles ONE review page from the round-2 artifacts so the owner can examine
every creature and plant currently assigned to each biome, at correct relative
size, with the description/intention on hover, the biome's own text, and BENCH's
per-biome comments — plus sheets for the decided non-biome groupings.

Reads (never writes) the owner's decision files. Correct per-biome cast =
in-rows keyed to the biome  +  move-rows resolving to it (via move_mapping_v2).
Sizing is true drawSize (beast_census), not the 4-tier bin. Cut families
(boom-15, the two retiring Cryptoforge creatures) are dropped with a footnote.

Output: fauna_review_deck.html (self-contained, sprites embedded as data URIs).
"""
from __future__ import annotations
import base64, csv, glob, io, json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path("/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils")))
import game_paths as GP  # noqa: E402

ROOT = Path("/mnt/d/Luke/dev/Rimworld")
REVIEW = ROOT / "design/Jawa/worldbuilding/review"
R2 = REVIEW / "round2"
BIOMES = ROOT / "design/Jawa/worldbuilding/biomes"
FAUNA_SPRITES = ROOT / "design/Jawa/fauna/sprites"
FLORA_SPRITES = ROOT / "design/Jawa/mods/plant_sprites"

from PIL import Image

CUT_BOOM = {"Boomalope","Boomrat","VFEI2_Boomtick","GR_Bearalope","GR_Boomabear",
 "GR_Boomalisk","GR_Boombeetle","GR_Boomcat","GR_Boomffalo","GR_Boomsnake",
 "GR_Boomsquirrel","GR_Chickenlope","GR_Manalope","GR_ParagonBoomalope","GR_Squirralope"}
CRYPTO_OUT = {"VQE_IceCrawler","VQE_Megamidge"}
DROPPED = CUT_BOOM | CRYPTO_OUT

THUMB = 128  # px longest side for embedded sprites

# ---- sprite cache: defName -> data URI (deduped) -------------------------
_sprite_cache: dict[str, str | None] = {}
def sprite(defName: str, folder: Path) -> str | None:
    if defName in _sprite_cache:
        return _sprite_cache[defName]
    uri = None
    p = folder / f"{defName}.png"
    if p.exists():
        try:
            im = Image.open(p).convert("RGBA")
            im.thumbnail((THUMB, THUMB), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
            uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        except Exception:
            uri = None
    _sprite_cache[defName] = uri
    return uri

# ---- census: label, drawSize, bodySize -----------------------------------
def load_census():
    info: dict[str, dict] = {}
    for r in csv.DictReader(open(ROOT/"design/Jawa/fauna/animal_census.csv")):
        info[r["defName"]] = {"label": r.get("label") or r["defName"],
                              "bodySize": _f(r.get("bodySize")), "drawSize": None,
                              "mod": r.get("mod","")}
    for r in csv.DictReader(open(ROOT/"design/Jawa/worldbuilding/data/beast_census.csv")):
        d = info.setdefault(r["defName"], {"label": r["defName"], "bodySize": None,
                                           "drawSize": None, "mod": r.get("mod","")})
        d["drawSize"] = _f(r.get("drawSize")) or d.get("drawSize")
        if not d.get("bodySize"): d["bodySize"] = _f(r.get("bodySize"))
    return info
def _f(x):
    try: return float(x)
    except (TypeError, ValueError): return None

# ---- drawSize instrument fix (owner hit it, 2026-09-11) -------------------
# 🔴 The census merge above silently fell through drawSize -> bodySize -> 1.0.
# RSW_Reefback (our own def, absent from BOTH harvest CSVs) rendered at 1.0
# while its PawnKindDef's adult lifeStage says 10.7. Never default silently:
# resolve the true drawSize from the def XML itself.
#
# 🔴 CALIBRATION PASS 2026-09-11 — RESOLUTION ORDER FLIPPED. The harvested
# census can carry a WRONG or unparseable value (`beast_census.csv`'s own
# `drawSize` column is frequently the literal string "UNMEASURED (field not
# captured by dump...)", not a number) and must never outrank the def files
# themselves. New order, def truth first:
#   1. our own repo mods (src/Rim*/**/Defs) — freshest, authoritative intent
#   2. the LIVE active mod set (workshop + local Mods, ParentName-resolved via
#      def_inventory.build) — what the game actually runs today; catches a
#      third-party def we do not ship AND a stale-deployed copy of our own
#   3. the offline captured dump — a cached snapshot, may be older than #2
#   4. the harvested census — LAST, only when no def source resolves at all
#   5. bodySize, or a bare 1.0 — both ALWAYS badged ⚠ UNMEASURED, never silent
# All four resolve a PawnKindDef's ADULT lifeStage (index -1, matching the
# race's own lifeStageAges 1:1 — RimWorld indexes lifeStages by that bracket,
# not by counting backwards from some assumed "final" entry).
_REPO_DRAWSIZE: dict[str, float] | None = None
def _repo_drawsize_index() -> dict[str, float]:
    global _REPO_DRAWSIZE
    if _REPO_DRAWSIZE is not None:
        return _REPO_DRAWSIZE
    idx: dict[str, float] = {}
    for path in glob.glob(str(ROOT / "src/Rim*/**/Defs/**/*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        els = root.findall(".//PawnKindDef")
        if root.tag == "PawnKindDef":
            els = [root] + els
        for el in els:
            race_el = el.find("race")
            race = (race_el.text or "").strip() if race_el is not None else ""
            if not race:
                continue
            stages = el.findall("lifeStages/li")
            if not stages:
                continue
            ds_el = stages[-1].find("bodyGraphicData/drawSize")
            if ds_el is None or not (ds_el.text or "").strip():
                continue
            ds = _f(ds_el.text.strip())
            if ds:
                idx[race] = ds
    _REPO_DRAWSIZE = idx
    return idx

_LIVE_DRAWSIZE: dict[str, float] | None = None
def _live_drawsize_index() -> dict[str, float]:
    """The ACTIVE mod set (workshop + local Mods), ParentName-resolved.
    Unlike the repo-only scan this handles third-party PawnKindDefs that
    inherit their lifeStages from an abstract base — raw-XML grepping would
    miss those entirely."""
    global _LIVE_DRAWSIZE
    if _LIVE_DRAWSIZE is not None:
        return _LIVE_DRAWSIZE
    idx: dict[str, float] = {}
    try:
        import def_inventory as DI
        ds = DI.build(DI.D_CONFIG, DI.D_WORKSHOP, DI.D_LOCAL, DI.D_DATA,
                      types=("PawnKindDef",), quiet=True)
        for rec in ds.of_type("PawnKindDef"):
            el = rec.element
            race = (el.findtext("race") or "").strip()
            if not race or race in idx:
                continue
            stages = el.findall("lifeStages/li")
            if not stages:
                continue
            ds_el = stages[-1].find("bodyGraphicData/drawSize")
            if ds_el is None or not (ds_el.text or "").strip():
                continue
            v = _f(ds_el.text.strip())
            if v:
                idx[race] = v
            rec.release()
    except Exception:                                    # noqa: BLE001
        pass
    _LIVE_DRAWSIZE = idx
    return idx

_DUMP_DRAWSIZE: dict[str, float] | None = None
def _dump_drawsize_index() -> dict[str, float]:
    global _DUMP_DRAWSIZE
    if _DUMP_DRAWSIZE is not None:
        return _DUMP_DRAWSIZE
    idx: dict[str, float] = {}
    try:
        p = Path(GP.DEF_DUMP) / "defs" / "PawnKindDef.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        for rec in doc.get("defs", []):
            f = rec.get("fields") or {}
            race = f.get("race")
            if not race or race in idx:
                continue
            stages = f.get("lifeStages") or []
            if not stages:
                continue
            bg = (stages[-1] or {}).get("bodyGraphicData") or {}
            ds = bg.get("drawSize")
            x = ds.get("x") if isinstance(ds, dict) else None
            if x is not None:
                idx[race] = float(x)
    except (OSError, ValueError, KeyError):
        pass
    _DUMP_DRAWSIZE = idx
    return idx

def resolve_game_drawsize(defName: str) -> float | None:
    """The PawnKindDef adult lifeStage drawSize: repo mods, then the live
    active mod set, then the offline dump. None means truly unresolvable,
    never a guessed number."""
    for idx in (_repo_drawsize_index(), _live_drawsize_index(), _dump_drawsize_index()):
        v = idx.get(defName)
        if v:
            return v
    return None

def resolve_size(defName: str, c: dict) -> tuple[float, bool, str]:
    """(renderSize, unmeasured, gameDrawSize_display). Def-XML truth first,
    the harvested census LAST — a harvest row can carry a stale or literally
    unparseable value (`beast_census.csv`'s "UNMEASURED (field not
    captured...)" string) and must never outrank the game's own def files.
    `unmeasured` is True the moment we render at anything other than a
    resolved drawSize — the card MUST show the ⚠ UNMEASURED badge then,
    never silently."""
    game_ds = resolve_game_drawsize(defName)
    if game_ds:
        return game_ds, False, game_ds
    ds = c.get("drawSize")
    if ds:
        return ds, False, ds
    bs = c.get("bodySize")
    if bs:
        return bs, True, None
    return 1.0, True, None

# ---- move map: row_key -> resolved target --------------------------------
def load_moves():
    m = {}
    for line in (R2/"move_mapping_v2.md").read_text().splitlines():
        if not line.startswith("| `"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4: continue
        key = cells[0].strip("` "); target = cells[-1]
        m[key] = target
    return m

# ---- biome sheet excerpt (identity prose, bounded) -----------------------
def biome_text(sheet_key: str) -> str:
    fn = sheet_key.split(" + ")[0].strip()
    p = BIOMES / f"{fn}.md"
    if not p.exists(): return "(no sheet found)"
    lines = p.read_text().splitlines()
    out, started = [], False
    for ln in lines:
        s = ln.strip()
        if s.startswith("# "): started = True; continue
        if not started: continue
        if s.startswith(">") or s.startswith("🧊") or s.startswith("_Owner"): continue
        if s.startswith("#"):  # next header ends the intro
            if out: break
            continue
        if s: out.append(s)
        if sum(len(x) for x in out) > 1400: break
    return " ".join(out) or "(no prose found)"

# ---- BENCH per-biome findings --------------------------------------------
def load_findings():
    txt = (R2/"biome_findings.md").read_text()
    blocks = {}
    cur = None; buf = []
    for ln in txt.splitlines():
        m = re.match(r"^##\s+(.+?)\s+—\s+churn", ln)
        if m:
            if cur: blocks[cur] = "\n".join(buf).strip()
            cur = m.group(1).strip(); buf = []
        elif cur is not None:
            buf.append(ln)
    if cur: blocks[cur] = "\n".join(buf).strip()
    return {canon(k): v for k, v in blocks.items()}

def canon(b: str) -> str:
    """One biome, one key: bare sea keys and their 'terminator_sea + …' twins merge."""
    if b.startswith("terminator_sea + "):
        return b.split(" + ", 1)[1]
    return b

FACTION_KW = ("hutt","helix","wildsteam","moisture","farmer","spicemine")
def build_faction_group(census):
    """The ninth roster — creatures the owner assigned to a FACTION's ground, not a
    biome. These live in move_mapping_v2 as OPEN/GROUP rows with faction language."""
    rows = []
    for line in (R2/"move_mapping_v2.md").read_text().splitlines():
        if not line.startswith("| `"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4: continue
        defName = re.sub(r"[`]", "", cells[1]).strip()
        words = cells[2].lower()
        tgt = cells[3]
        fac = next((k for k in FACTION_KW if k in words), None)
        if not fac: continue
        faction = {"hutt":"Hutt","helix":"Helix","wildsteam":"Wildsteam",
                   "moisture":"Moisture Farmers","farmer":"Moisture Farmers",
                   "spicemine":"Hutt"}[fac]
        c = census.get(defName, {})
        size, unmeasured, gameDs = resolve_size(defName, c)
        rows.append({"defName": defName, "label": c.get("label", defName),
            "drawSize": size, "unmeasured": unmeasured, "gameDrawSize": gameDs,
            "note": cells[2], "conf": faction, "img": sprite(defName, FAUNA_SPRITES)})
    return rows

# ---- assemble per-biome casts --------------------------------------------
NON_BIOME_TARGETS = ("OUT", "OPEN", "RESERVE")
def is_biome_target(tgt: str) -> bool:
    """move_mapping_v2.md targets that are NOT a biome — a creature going to
    RESERVE (2026-09-10 arid sitting: Cannok/Vulptex/Kwi/AA_Gigantelope/
    BMT_Diggerpede) or a GROUP:* sheet is exactly as much a non-arrival as
    OUT or OPEN and must not spawn its own fake biome slide."""
    return bool(tgt) and tgt not in NON_BIOME_TARGETS and not tgt.startswith("GROUP")

RESERVED_TAGS = ("FACTION-RESERVED", "INJECTABLE-RESERVED", "DUNGEON-RESERVED", "MERGE-RESERVED")
def is_reserved(note: str) -> bool:
    """A row can carry decision 'in'/'move' AND a *-RESERVED tag at the same
    time (sitting rulings sometimes leave the decision field stale while the
    note overrides it — e.g. `fauna:the_miasma:AA_Slurrypede` is decision
    'in' but its note reads 'Not here | DUNGEON-RESERVED...'). The tag always
    wins: none of these ever belong on a biome slide (they live on the
    reserved-groups sheet instead)."""
    note = note or ""
    return any(t in note for t in RESERVED_TAGS)

def is_fishing_result(note: str) -> bool:
    """Owner ruling 2026-09-10 (Grey Deep cap release / schooling retarget):
    BMT_Megakrill is 'still a FISHING RESULT, never a spawn' — it must not
    appear on a biome's wildAnimals cast at all, unlike an ordinary resident
    or arrival."""
    return "fishing result" in (note or "").lower()

def is_visitor(note: str) -> bool:
    """Owner ruling 2026-09-10, 'nightside visitor law': Wampa, Tauntaun and
    Jakobeast are margin visitors that stray in at low commonality, never
    natives — the note says so ('VISITOR-DYING...' / 'visitor-dying...',
    casing varies) and the card must mark them distinctly from residents."""
    return "visitor-dying" in (note or "").lower()

# ---- family collapse (owner, 2026-09-11: "why do 5 identical pustules show
# in the Rot") -------------------------------------------------------------
# Explicit map, no regex magic: several organisms ship as multiple lifecycle
# ThingDefs (larva/adult/queen/colony-variant, ...) that all land in the same
# biome and, post-dedup, still render once EACH because dedup keys on
# defName. Collapse every listed member into ONE card keyed by the family,
# using the rep def's art/size; the tooltip lists every member def that
# actually showed up in that biome.
FAMILIES = {
    "BMT_PustuleHornet": {
        "members": ("BMT_PustuleHornet", "BMT_PustuleHornetQueen", "BMT_PustuleHornetSpawned",
                    "BMT_ColonyPustuleHornet", "BMT_ColonyPustuleHornetQueen"),
        "rep": "BMT_PustuleHornetQueen",
        "label": "pustule hornet (x5 lifecycle defs, one organism)",
    },
    "BMT_MutatingTumorfish": {
        "members": ("BMT_MutatingTumorfishAdult", "BMT_MutatingTumorfishFry",
                    "BMT_MutatingTumorfishSpawn"),
        "rep": "BMT_MutatingTumorfishAdult",
        "label": "mutating tumorfish (x3 lifecycle defs, one organism)",
    },
}
FAMILY_OF = {m: key for key, fam in FAMILIES.items() for m in fam["members"]}

def build_biomes(fauna, flora, moves, census):
    # defName -> row, PER BIOME, so a def that is both resident ('in') and
    # arriving (a move resolving to the same biome) merges into ONE card
    # instead of rendering twice — owner ruling 2026-09-11, proven cases:
    # Beldon x2 in the_forge, AA_BloodShrimp x3 in the_contagion. The resident
    # row's fields (decision/note/art) win; every origin it arrived from is
    # kept as a union so the tooltip still says where it came from.
    buckets: dict[str, dict[str, dict]] = {}
    def add(biome, defName, note, decision, art, origin=None, sizeBin=None):
        if defName in DROPPED: return
        if is_reserved(note): return
        if is_fishing_result(note): return
        biome = canon(biome)
        bucket = buckets.setdefault(biome, {})
        visitor = is_visitor(note)

        fam_key = FAMILY_OF.get(defName)
        key = fam_key if fam_key else defName
        entry = bucket.get(key)
        if entry is None:
            if fam_key:
                fam = FAMILIES[fam_key]
                c = census.get(fam["rep"], {})
                size, unmeasured, gameDs = resolve_size(fam["rep"], c)
                bucket[key] = {
                    "defName": fam["rep"], "label": fam["label"], "family": fam_key,
                    "members": [defName],
                    "drawSize": size, "unmeasured": unmeasured, "gameDrawSize": gameDs,
                    "sizeBin": sizeBin, "visitor": visitor,
                    "note": note or "", "decision": decision, "art": art,
                    "origins": [origin] if origin else [], "mod": c.get("mod",""),
                    "img": sprite(fam["rep"], FAUNA_SPRITES)}
            else:
                c = census.get(defName, {})
                size, unmeasured, gameDs = resolve_size(defName, c)
                bucket[key] = {
                    "defName": defName, "label": c.get("label", defName),
                    "drawSize": size, "unmeasured": unmeasured, "gameDrawSize": gameDs,
                    "sizeBin": sizeBin, "visitor": visitor,
                    "note": note or "", "decision": decision, "art": art,
                    "origins": [origin] if origin else [], "mod": c.get("mod",""),
                    "img": sprite(defName, FAUNA_SPRITES)}
            return
        if fam_key and defName not in entry["members"]:
            entry["members"].append(defName)
        if origin and origin not in entry["origins"]:
            entry["origins"].append(origin)
        if visitor:
            entry["visitor"] = True
        if sizeBin and not entry.get("sizeBin"):
            entry["sizeBin"] = sizeBin
        if decision == "in" and entry["decision"] != "in":
            # the resident row always wins the displayed fields once it shows up,
            # regardless of whether an arrival got added to the bucket first
            entry["decision"], entry["note"], entry["art"] = decision, note or "", art
    for k, v in fauna.items():
        p = k.split(":")
        dec = v.get("decision")
        if p[0] == "fauna":
            biome, defName = p[1], p[2]
            if dec == "in":
                add(biome, defName, v.get("note"), "in", v.get("art"), sizeBin=v.get("sizeBin"))
            elif dec == "move":
                tgt = moves.get(k, "")
                if is_biome_target(tgt):
                    add(tgt, defName, v.get("note"), "arrived", v.get("art"), origin=biome,
                        sizeBin=v.get("sizeBin"))
        elif p[0] == "homeless":
            # 🔴 Fixed 2026-09-10: homeless:<name> rows with decision "move" were
            # previously dropped entirely — 117 such rows (81 resolving to a real
            # biome, e.g. homeless:JRWBeelzebufo -> the_miasma) never appeared on
            # any slide. Joined the same way as a fauna: move row, origin "homeless"
            # since there is no origin biome sheet for a homeless creature.
            defName = p[1]
            if dec == "move":
                tgt = moves.get(k, "")
                if is_biome_target(tgt):
                    add(tgt, defName, v.get("note"), "arrived", v.get("art"), origin="homeless",
                        sizeBin=v.get("sizeBin"))
    animals: dict[str, list] = {}
    for biome, bucket in buckets.items():
        rows = []
        for e in bucket.values():
            e["origin"] = ", ".join(e.pop("origins")) or None
            rows.append(e)
        animals[biome] = rows
    plants: dict[str, list] = {}
    for k, v in flora.items():
        p = k.split(":")
        if len(p) < 3 or p[0] != "flora": continue
        if v.get("decision") != "in": continue
        biome, defName = canon(p[1]), p[2]
        plants.setdefault(biome, []).append({
            "defName": defName, "label": defName, "note": v.get("note") or "",
            "img": sprite(defName, FLORA_SPRITES)})
    return animals, plants

# ---- grouping sheets ------------------------------------------------------
def load_groups(census):
    """Parse reserved_groups_draft.md tables into {group: [rows]}."""
    txt = (R2/"reserved_groups_draft.md").read_text()
    groups: dict[str, list] = {}
    cur = None
    for ln in txt.splitlines():
        m = re.match(r"^##\s+(.+)", ln)
        if m: cur = m.group(1).strip(); groups.setdefault(cur, [])
        elif ln.startswith("|") and cur and "creature" not in ln.lower() and "---" not in ln:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] != "creature":
                defName = re.sub(r"[`*]", "", cells[0]).split()[0]
                note = cells[2] if len(cells) > 2 else (cells[1] if len(cells)>1 else "")
                conf = cells[-1] if len(cells) >= 4 else ""
                c = census.get(defName, {})
                size, unmeasured, gameDs = resolve_size(defName, c)
                groups[cur].append({"defName": defName, "label": c.get("label", defName),
                    "drawSize": size, "unmeasured": unmeasured, "gameDrawSize": gameDs,
                    "note": note, "conf": conf, "img": sprite(defName, FAUNA_SPRITES)})
    return {g: rows for g, rows in groups.items() if rows}

# ---- render ---------------------------------------------------------------
def render(animals, plants, findings, groups):
    biome_order = sorted(animals, key=lambda b: -(len(animals.get(b,[]))+len(plants.get(b,[]))))
    data = {"biomes": [], "groups": []}
    for b in biome_order:
        data["biomes"].append({
            "key": b, "text": biome_text(b),
            "findings": findings.get(b, ""),
            "animals": sorted(animals.get(b,[]), key=lambda a: -a["drawSize"]),
            "plants": plants.get(b, [])})
    for g, rows in groups.items():
        data["groups"].append({"key": g, "rows": sorted(rows, key=lambda r: -r.get("drawSize",1))})
    return HTML.replace("/*DATA*/", json.dumps(data))

HTML = r"""<title>Ash'karr Fauna & Flora Deck</title>
<style>
:root{--bg:#221a12;--panel:#2e2318;--panel2:#37291a;--ink:#f0e3d0;--dim:#b9a488;
--line:#4a382550;--accent:#c98a3e;--in:#7fae6a;--arr:#5b9bd5;--cut:#c9635b;--stage:#1a140d;}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,system-ui,sans-serif;margin:0}
header{position:sticky;top:0;z-index:20;background:#1b140dee;backdrop-filter:blur(6px);
 border-bottom:1px solid var(--line);padding:10px 16px}
header h1{margin:0;font-size:16px;color:var(--accent);letter-spacing:.3px}
nav{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
nav a{font-size:11px;color:var(--dim);text-decoration:none;background:var(--panel);
 padding:2px 8px;border-radius:10px;border:1px solid var(--line)}
nav a:hover{color:var(--ink);border-color:var(--accent)}
nav a.grp{color:var(--accent)}
.wrap{max-width:1180px;margin:0 auto;padding:16px}
section{background:var(--panel);border:1px solid var(--line);border-radius:12px;
 margin-bottom:26px;overflow:hidden;scroll-margin-top:88px}
.head{padding:12px 18px;border-bottom:1px solid var(--line);display:flex;
 align-items:baseline;gap:12px;flex-wrap:wrap}
.head h2{margin:0;font-size:19px;color:var(--accent);text-transform:capitalize}
.head .count{font-size:12px;color:var(--dim)}
.stage{background:var(--stage);padding:16px 18px 6px}
.lbl{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--dim);margin:0 0 8px}
.row{display:flex;flex-wrap:wrap;align-items:flex-end;gap:14px;min-height:40px}
.crit{position:relative}
.crit img{display:block;image-rendering:auto;filter:drop-shadow(0 2px 3px #0007)}
.crit .cap{font-size:9.5px;color:var(--dim);text-align:center;margin-top:3px;max-width:90px;
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.crit .dot{position:absolute;top:-3px;right:8px;width:7px;height:7px;border-radius:50%}
.d-in{background:var(--in)}.d-arr{background:var(--arr)}.d-visit{background:#c98a3e}
.crit .badge{position:absolute;top:-8px;left:-4px;font-size:12px;filter:drop-shadow(0 1px 1px #000a)}
.ruler{display:flex;flex-direction:column;align-items:center;opacity:.5;align-self:flex-end}
.ruler .human{width:2px;background:var(--accent);border-radius:2px}
.ruler .cap{font-size:9px;color:var(--accent)}
.plants{background:#241a10}
.boxes{display:grid;grid-template-columns:1fr 1fr;gap:0}
.box{padding:14px 18px}
.box+.box{border-left:1px solid var(--line)}
.box h3{margin:0 0 6px;font-size:11px;text-transform:uppercase;letter-spacing:1px}
.box.biome h3{color:var(--dim)}
.box.me h3{color:var(--accent)}
.box .body{font-size:12.5px;color:var(--ink);white-space:pre-wrap;max-height:280px;overflow:auto}
.box.biome .body{color:var(--dim)}
.foot{font-size:10.5px;color:#8a7355;padding:6px 18px 12px}
#tip{position:fixed;z-index:50;pointer-events:none;max-width:320px;background:#120d07f5;
 border:1px solid var(--accent);border-radius:8px;padding:9px 11px;font-size:12px;
 color:var(--ink);box-shadow:0 6px 24px #000a;display:none}
#tip .t{color:var(--accent);font-weight:600;font-size:13px}
#tip .m{color:var(--dim);font-size:10.5px;margin-bottom:4px}
#tip .k{color:var(--dim)}
#tip .note{margin-top:5px;font-style:italic}
@media(max-width:720px){.boxes{grid-template-columns:1fr}.box+.box{border-left:none;border-top:1px solid var(--line)}}
</style>
<header>
 <h1>Ash'karr — Fauna &amp; Flora Assignment Deck · round 2 examination</h1>
 <nav id="nav"></nav>
</header>
<div class="wrap" id="deck"></div>
<div id="tip"></div>
<script id="DATA" type="application/json">/*DATA*/</script>
<script>
const D=JSON.parse(document.getElementById('DATA').textContent);
const PX=40, MINH=20, MAXH=190, HUMAN=1.35;
const tip=document.getElementById('tip');
function hpx(ds){return Math.max(MINH, Math.min(MAXH, PX*(ds||1)));}
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function crit(a, isGroup){
  // 🔴 RENDER-MATH BUG (owner screenshot proof, 2026-09-11): the img got ONLY
  // an inline height, no width — the browser auto-scaled width to the cached
  // SPRITE'S OWN pixel aspect ratio, which varies wildly by capture pose
  // (AA_Helixien's cache is 128x31, a near-4:1 sliver; AA_DrainerLarva's is
  // 128x34). At height alone that stretched their width to ~4x every other
  // card at the SAME drawSize, painting a "row-spanning caterpillar" that has
  // nothing to do with drawSize. RimWorld draws every pawn in a SQUARE
  // drawSize×drawSize footprint (the XML's <drawSize> is one scalar, not a
  // width/height pair) — so the card must be square too, with the sprite
  // fit INSIDE it (object-fit:contain), never stretched to fill it.
  const h=hpx(a.drawSize), clamped = PX*(a.drawSize||1) > MAXH;
  const d=document.createElement('div'); d.className='crit';
  const dotcls = a.visitor?'d-visit':(a.decision==='arrived'?'d-arr':(a.decision==='in'?'d-in':''));
  d.innerHTML = (a.img?`<img src="${a.img}" style="height:${h}px;width:${h}px;object-fit:contain">`
                     :`<div style="height:${h}px;width:${h}px;display:flex;align-items:center;justify-content:center;border:1px dashed #6a533560;border-radius:6px;font-size:9px;color:#7a6242">no art</div>`)
    + (dotcls?`<span class="dot ${dotcls}"></span>`:'')
    + (a.unmeasured?`<span class="badge" title="drawSize unmeasured — sized by a fallback">⚠</span>`:'')
    + `<div class="cap">${esc(a.label)}</div>`;
  d.dataset.j = JSON.stringify({...a, clamped, img:undefined, isGroup});
  d.addEventListener('mouseenter',showTip); d.addEventListener('mousemove',moveTip);
  d.addEventListener('mouseleave',()=>tip.style.display='none');
  return d;
}
function showTip(e){
  const a=JSON.parse(e.currentTarget.dataset.j);
  let s=`<div class="t">${esc(a.label)}</div><div class="m">${esc(a.defName)}${a.mod?' · '+esc(a.mod):''}</div>`;
  // two-value size display, labeled so the render size and the owner's size
  // RULING are never confused for the same number again (owner, 2026-09-11)
  if(a.gameDrawSize) s+=`<div><span class="k">current drawSize (game)</span> ${a.gameDrawSize}${a.clamped?' (shown clamped)':''}</div>`;
  else if(a.unmeasured) s+=`<div><span class="k">current drawSize (game)</span> ⚠ UNMEASURED — shown at ${a.drawSize} (fallback)</div>`;
  if(a.sizeBin) s+=`<div><span class="k">ruled bin (register)</span> ${esc(a.sizeBin)}</div>`;
  if(a.visitor) s+=`<div><span class="k">status</span> visitor (nightside visitor law) — never native</div>`;
  if(a.members) s+=`<div><span class="k">member defs</span> ${a.members.map(esc).join(', ')}</div>`;
  if(a.decision==='arrived') s+=`<div><span class="k">moved in from</span> ${esc(a.origin||'')}</div>`;
  else if(a.decision==='in') s+=`<div><span class="k">assigned here</span></div>`;
  if(a.art) s+=`<div><span class="k">art</span> ${esc(a.art)}</div>`;
  if(a.conf) s+=`<div><span class="k">grouping</span> ${esc(a.conf)}</div>`;
  if(a.note) s+=`<div class="note">“${esc(a.note)}”</div>`;
  tip.innerHTML=s; tip.style.display='block'; moveTip(e);
}
function moveTip(e){
  const pad=14; let x=e.clientX+pad, y=e.clientY+pad;
  const r=tip.getBoundingClientRect();
  if(x+r.width>innerWidth) x=e.clientX-r.width-pad;
  if(y+r.height>innerHeight) y=e.clientY-r.height-pad;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}
function ruler(){
  const r=document.createElement('div'); r.className='ruler';
  r.innerHTML=`<div class="human" style="height:${hpx(HUMAN)}px"></div><div class="cap">human</div>`;
  return r;
}
const deck=document.getElementById('deck'), nav=document.getElementById('nav');
D.biomes.forEach(b=>{
  const id='b_'+b.key.replace(/[^a-z0-9]+/gi,'_');
  const a=document.createElement('a'); a.href='#'+id; a.textContent=b.key; nav.appendChild(a);
  const sec=document.createElement('section'); sec.id=id;
  sec.innerHTML=`<div class="head"><h2>${esc(b.key)}</h2>
    <span class="count">${b.animals.length} animals · ${b.plants.length} plants</span></div>`;
  const stage=document.createElement('div'); stage.className='stage';
  stage.innerHTML='<p class="lbl">Animals — sized by drawSize (hover for intent)</p>';
  const arow=document.createElement('div'); arow.className='row';
  arow.appendChild(ruler());
  b.animals.forEach(x=>arow.appendChild(crit(x)));
  stage.appendChild(arow); sec.appendChild(stage);
  const pstage=document.createElement('div'); pstage.className='stage plants';
  pstage.innerHTML='<p class="lbl">Plants</p>';
  const prow=document.createElement('div'); prow.className='row';
  if(b.plants.length) b.plants.forEach(x=>prow.appendChild(crit({...x,drawSize:0.9})));
  else prow.innerHTML='<span style="color:#7a6242;font-size:12px">— none assigned —</span>';
  pstage.appendChild(prow); sec.appendChild(pstage);
  const boxes=document.createElement('div'); boxes.className='boxes';
  boxes.innerHTML=`<div class="box biome"><h3>Biome text (for review)</h3><div class="body">${esc(b.text)}</div></div>
    <div class="box me"><h3>BENCH per-biome comments</h3><div class="body">${esc(b.findings)||'—'}</div></div>`;
  sec.appendChild(boxes);
  deck.appendChild(sec);
});
const gsep=document.createElement('a'); gsep.textContent='— groupings —'; gsep.style.color='#7a6242'; nav.appendChild(gsep);
D.groups.forEach(g=>{
  const id='g_'+g.key.replace(/[^a-z0-9]+/gi,'_');
  const a=document.createElement('a'); a.href='#'+id; a.className='grp'; a.textContent=g.key.split('(')[0].trim().slice(0,26); nav.appendChild(a);
  const sec=document.createElement('section'); sec.id=id;
  sec.innerHTML=`<div class="head"><h2 style="text-transform:none">${esc(g.key)}</h2><span class="count">${g.rows.length} creatures</span></div>`;
  const stage=document.createElement('div'); stage.className='stage';
  const row=document.createElement('div'); row.className='row';
  row.appendChild(ruler());
  g.rows.forEach(x=>row.appendChild(crit(x,true)));
  stage.appendChild(row); sec.appendChild(stage);
  deck.appendChild(sec);
});
</script>
<div class="wrap"><p style="color:#7a6242;font-size:11px">Cut families excluded: the 15-creature boom family and the two retiring Cryptoforge creatures (VQE_IceCrawler, VQE_Megamidge). Green dot = assigned here; blue dot = moved in from another sheet; orange dot = visitor (nightside visitor law — never native). ⚠ = drawSize could not be resolved from the game files; sized by a fallback instead. Sizes are true drawSize, clamped for titans (noted in tooltip).</p></div>
"""

def main():
    fauna = json.load(open(REVIEW/"round2/decisions_propagated.json"))["decisions"]
    flora = json.load(open(REVIEW/"flora_assignment_register.decisions.json"))["decisions"]
    census = load_census()
    moves = load_moves()
    animals, plants = build_biomes(fauna, flora, moves, census)
    findings = load_findings()
    groups = load_groups(census)
    fac = build_faction_group(census)
    if fac:
        groups["9. faction-territory fauna (ninth roster — Hutt / Helix / Wildsteam / Moisture Farmers)"] = fac
    html = render(animals, plants, findings, groups)
    out = R2 / "fauna_review_deck.html"
    out.write_text(html)
    na = sum(len(v) for v in animals.values()); npl = sum(len(v) for v in plants.values())
    withart = sum(1 for v in animals.values() for a in v if a["img"])
    print(f"biomes={len(animals)} animals={na} (art {withart}) plants={npl} "
          f"groups={len(groups)} size={out.stat().st_size/1e6:.2f}MB -> {out}")

if __name__ == "__main__":
    main()
