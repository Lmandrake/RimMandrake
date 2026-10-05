#!/usr/bin/env python3
"""biome_census.py — every flora/fauna row of every one of our biomes, with its art and canon state
(BIOME_FLORAFAUNA_ART_REVIEW_1). Re-runnable; reads only, writes two files:

    python3 src/RimMandrake/Utils/art/biome_census.py [--no-wookiee] [--out Transient/biome_ffar]

  -> <out>/census.json   machine-readable; the schema below is what the per-biome sheet builder reads
  -> <out>/census.md     one summary table per biome + the NO-ART and canon-entry-missing rows named

BIOMES. Scope = "RimMandrake: Baroque Biomes" (mandrake.rm.biomes): every non-abstract RM_ BiomeDef
declared under the Defs/ of an entry of src/RimMandrake/Biomes.compose.json (derived on each run, never
listed here; includes the RM_SeabedFloor_* defs). One biome = one RM_ BiomeDef. NOT in scope: vanilla
or donor biomes, the RUT_ campaign twins, and patches onto any non-RM biome. Order: RM_LongShade (the
Desert's Baroque twin), RM_Stillsand (deep desert), RM_BlueDesert, then the rest alphabetically.

ROSTERS. Read from src/ only, as XML ELEMENTS: <wildAnimals>/<wildPlants> are `<DefName>c</DefName>`
(never <li>); <fishTypes> are `<group><DefName>c</DefName></group>`. Inline rows come from each
BiomeDef; patch rows come from every PatchOperation whose OWN <xpath> targets
Defs/BiomeDef[defName="RM_..."]/wildAnimals|wildPlants|fishTypes (Add/Insert read <value>, Replace of the
whole list resets it, Remove of /wildAnimals/<Name> removes; Conditional/FindMod/Sequence are walked
into, never read as an add). Files are applied in path order. NOT read (UNMEASURED): the base rosters
of vanilla/donor BiomeDefs (Core's own Desert cast), Cherry Picker cuts, other mods' patches.

ROW IDENTITY. One row per species per biome. A donor's bare defName and our port of it are ONE row;
the port is found by (in order) an explicit `Donor -> RSW_Port` comment in our XML, the desert sitting
assignment file, the Mlie wave maps, or the stem rule (X -> RSW_X / RM_X / RUT_X, AA_X -> RSW_X).
`pairing` records which. The row key is our port's defName when one exists, else the name as written.

CANON. `canon.entry` is set only from design/RimStarWars/canon_references: first the generated
INDEX.md's own defName(s) column (match "index_defname"), else a directory named for the stem/label
(match "dir_name", as art_sheet.canon_entry does). Canon is NEVER inferred from a defName or from
absence. `canon.wookieepedia` (rows with no entry only; --no-wookiee skips) is an exact-title hit on
Wookieepedia's search API for the label or stem whose page carries a lifeform infobox
({{Species}}/{{Plant}}/...) — a CANDIDATE, not proof; `canon_missing_entry` is true only on such a
hit. Same-name person/place/object pages are rejected, but a generic page (e.g. "Grass") can remain.

TWINS. `twins` lists related defs: donor<->port (relation "donor"/"port"), an RM_/RUT_ stand-in and an
RSW_ def sharing a stem ("tier_twin_same_stem"), sharing a texPath ("tier_twin_shared_texpath"), or an
explicit "copied from RSW_X" comment ("tier_twin_comment"). `noncanon_twin` on a row = it has a canon
entry and an RM_/RUT_ twin, or it is an RM_/RUT_ def twinned to a def that has a canon entry.

ART. Per row, every body-role texPath (texPath -> def via artledger.scan_def_slots; PawnKindDefs joined
to their race) is passed to art_sheet.build_row, which assembles every picture set the art ledger knows
(live copies by load order, artpipe render families, git history, donor original; purged pictures
dropped; masks and dessicated textures never counted). A donor-only row with no def of ours is joined
to ledger resources by name (`joined_by: "name"`). `artpipe_state_jobs` = job families found by
`artpipe_state.py find --names-only` on the stem (word-boundary filtered), whether or not the ledger
holds them. `prior_selection` carries the owner's desert-sitting-1 pick per texPath
(Transient/desert_sitting1_2026-10-04.decisions.json resolved through its snapshot).

census.json top-level keys:
  schema            "biome_ffar.census/1"
  generated         ISO time;  git_head  sha of HEAD when run
  inputs            ledger/event counts, load-order fingerprint, artpipe root, wookiee on/off
  sanity_probe      {name: rows hit} for known-present species — a zero there means the census is broken
  biome_order       [biome keys, review order]
  biomes            {RM_ defName: {label, biome_def, biome_file, compose_entry, order, defs:[{defName, ours,
                    file, rows_here}], summary:{...}, rows:[ROW]}}
  unmapped_patch_targets  out-of-scope BiomeDefs (RUT_/vanilla/donor) with roster rows, for traceability only
  unmeasured        list of strings
ROW: key, kind (fauna|flora|fish), label, defNames, port, donors, pairing, placements[{biome_def,
  as_written, commonality, source(inline|patch), layer(inline_RM|patch), patch_mod (packageId of the
  patching mod, null inline), file, may_require}], commonality_max,
  canon{entry, match, images, has_must_show, ruled, wookieepedia, canon_missing_entry},
  twins[{defName, relation, evidence, in_this_biome}], noncanon_twin,
  art{resources[{res, role, joined_by, in_ledger, subjects, live{mod,label,faces}|null, versions[{kind,label,
  detail,date,faces,near_dup_of}], prior_selection|null}], n_versions, has_art, live_res},
  artpipe_state_jobs, ledger_rulings[{verdict, by, trust, ts, via, row}]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import art_sheet as A  # noqa: E402
import subject as S_  # noqa: E402

REPO = L.REPO_ROOT
SRC = REPO / "src"
CANON = REPO / "design" / "RimStarWars" / "canon_references"
ASSIGN = REPO / "Transient" / "desert_sittings_assignment_2026-10-04.json"
SIT1 = REPO / "Transient" / "desert_sitting1_2026-10-04.decisions.json"
WOOKIEE_CACHE = Path.home() / ".cache" / "rm_biome_census" / "wookiee.json"
PROBES = ("korrum", "hawkbat", "bantha", "anooba", "stoneback")
REQUIRED_PROBES = ("korrum", "hawkbat", "bantha")

COMPOSE = SRC / "RimMandrake" / "Biomes.compose.json"
FIRST = ["RM_LongShade", "RM_Stillsand", "RM_BlueDesert"]     # Desert's Baroque twin, deep desert, blue desert


def baroque_biomes():
    """[(defName, label, file, compose entry key)] — every non-abstract RM_ BiomeDef declared under the Defs/
    of an entry of Biomes.compose.json ('RimMandrake: Baroque Biomes', mandrake.rm.biomes). Derived, never listed."""
    comp = json.load(open(COMPOSE))
    out = []
    for e in comp["entries"]:
        base = SRC / "RimMandrake" / e["source"]
        for f in sorted(base.rglob("*.xml")):
            if "/Defs/" not in str(f):
                continue
            root = parse(f)
            if root is None:
                continue
            for bd in root.iter("BiomeDef"):
                dn = (bd.findtext("defName") or "").strip()
                if dn.startswith("RM_") and bd.get("Abstract") != "True":
                    out.append((dn, (bd.findtext("label") or "").strip(), str(f.relative_to(REPO)), e["key"]))
    return out


LISTS = {"wildAnimals": "fauna", "wildPlants": "flora", "fishTypes": "fish"}
OURS_RE = re.compile(r"^(RSW_|RM_|RUT_|rut_)")
BODY_ROLES = {"body", "flying", "swimming", "plant_immature", "plant_leafless"}
t0 = time.time()


def log(*a):
    print(f"[{time.time() - t0:5.0f}s]", *a, flush=True)


def xml_files(sub=None):
    for f in sorted(SRC.rglob("*.xml")):
        s = str(f)
        if "/archive" in s.lower() or "/_archive" in s:
            continue
        if sub and f"/{sub}/" not in s:
            continue
        yield f


def parse(f):
    try:
        return ET.parse(f).getroot()
    except (ET.ParseError, OSError):
        return None


def num(t):
    try:
        return float((t or "").strip())
    except ValueError:
        return None


def list_entries(node, field):
    """[(defName, commonality, mayRequire)] from a roster element, element form only."""
    out = []
    if field == "fishTypes":
        for grp in node:
            if isinstance(grp.tag, str):
                for ch in grp:
                    if isinstance(ch.tag, str) and ch.tag != "li":
                        out.append((ch.tag, num(ch.text), ch.get("MayRequire") or grp.get("MayRequire")))
        return out
    for ch in node:
        if isinstance(ch.tag, str) and ch.tag != "li":
            out.append((ch.tag, num(ch.text), ch.get("MayRequire")))
    return out


# ───────────────────────────────────────────────────────────── rosters ──

_PKG = {}


def mod_of(f: Path) -> str:
    """packageId of the mod folder holding a patch file (src/<Tier>/<Mod>/...), else that folder."""
    parts = f.relative_to(SRC).parts
    folder = SRC / parts[0] / parts[1]
    if folder not in _PKG:
        try:
            _PKG[folder] = (ET.parse(folder / "About" / "About.xml").getroot().findtext("packageId") or "").strip() or str(folder.relative_to(REPO))
        except (ET.ParseError, OSError):
            _PKG[folder] = str(folder.relative_to(REPO))
    return _PKG[folder]


def read_rosters():
    """biome_def -> {"ours": bool, "file": str, "entries": {(field, defName): placement}}."""
    R = {}
    for f in xml_files():
        if "/Defs/" not in str(f):
            continue
        root = parse(f)
        if root is None:
            continue
        for b in root.iter("BiomeDef"):
            dn = (b.findtext("defName") or "").strip()
            if not dn:
                continue
            ent = {}
            for field in LISTS:
                node = b.find(field)
                if node is None:
                    continue
                for name, c, mr in list_entries(node, field):
                    ent[(field, name)] = {"as_written": name, "commonality": c, "source": "inline",
                                          "layer": "inline_RM", "patch_mod": None,
                                          "file": str(f.relative_to(REPO)), "may_require": mr}
            R[dn] = {"ours": True, "file": str(f.relative_to(REPO)), "entries": ent}
    xp_re = re.compile(r'BiomeDef\s*\[\s*defName\s*=\s*"([^"]+)"\s*\]\s*/\s*(wildAnimals|wildPlants|fishTypes)(.*)$')
    for f in xml_files():
        if "/Patches/" not in str(f):
            continue
        root = parse(f)
        if root is None:
            continue
        for op in root.iter():
            cls = (op.get("Class") or "")
            x = op.find("xpath")
            if x is None or not cls or "Conditional" in cls or "FindMod" in cls or "Sequence" in cls:
                continue
            m = xp_re.search((x.text or "").strip())
            if not m:
                continue
            bdef, field, tail = m.group(1), m.group(2), m.group(3).strip()
            if bdef not in R:
                R[bdef] = {"ours": False, "file": None, "entries": {}}
            ent = R[bdef]["entries"]
            rel = str(f.relative_to(REPO))
            if "Remove" in cls:
                nm = re.match(r"/\s*([A-Za-z0-9_]+)\s*$", tail)
                if nm:
                    ent.pop((field, nm.group(1)), None)
                continue      # positional duplicate removals do not change the species set
            v = op.find("value")
            if v is None:
                continue
            kids = [c for c in v if isinstance(c.tag, str)]
            if "Replace" in cls and not tail:
                for k in [k for k in ent if k[0] == field]:
                    ent.pop(k)
            if len(kids) == 1 and kids[0].tag == field:
                v = kids[0]
            if tail:
                continue      # an add into a single entry's node: not a roster row
            for name, c, mr in list_entries(v, field):
                ent[(field, name)] = {"as_written": name, "commonality": c, "source": "patch",
                                      "layer": "patch", "patch_mod": mod_of(f),
                                      "file": rel, "may_require": mr}
    return R


# ───────────────────────────────────────────────────────── our defs, ports ──

def read_our_defs():
    """defName -> {type, label, file, race(kind only)}; plus comment-declared renames and 'copied from'."""
    D, renames, copied = {}, {}, {}
    arrow = re.compile(r"\b([A-Za-z][A-Za-z0-9_]{2,})\s*(?:->|→)\s*((?:RSW_|RM_|RUT_|rut_)[A-Za-z0-9_]+)")
    cpy = re.compile(r"copied from\s+(RSW_[A-Za-z0-9_]+)", re.I)
    for f in xml_files():
        if "/Defs/" not in str(f):
            continue
        root = parse(f)
        if root is None:
            continue
        rel = str(f.relative_to(REPO))
        for d in root:
            if not isinstance(d.tag, str) or d.tag not in ("ThingDef", "PawnKindDef"):
                continue
            dn = (d.findtext("defName") or "").strip()
            if not dn:
                continue
            rec = D.setdefault(dn, {"types": [], "label": None, "file": rel})
            rec["types"].append(d.tag)
            rec["label"] = rec["label"] or (d.findtext("label") or "").strip() or None
            if d.tag == "PawnKindDef":
                rec["race"] = (d.findtext("race") or "").strip() or None
            if d.tag == "ThingDef":
                rec["is_race"] = d.find("race") is not None
                rec["is_plant"] = d.find("plant") is not None
        try:
            txt = f.read_text(errors="replace")
        except OSError:
            continue
        for m in arrow.finditer(txt):
            renames.setdefault(m.group(1), (m.group(2), rel))
        for m in cpy.finditer(txt):
            nxt = re.search(r"<defName>\s*([^<\s]+)\s*</defName>", txt[m.end():])
            if nxt:
                copied[nxt.group(1)] = (m.group(1), rel)
    return D, renames, copied


def mlie_map():
    out = {}
    for f in sorted((REPO / "infrastructure/state/facts").glob("mlie_creature_defname_map_wave_*.json")):
        d = json.load(open(f))
        if isinstance(d.get("creatures"), dict):
            items = d["creatures"].items()
        else:
            items = [(k, v) for k, v in d.items() if isinstance(v, str) and v.startswith("RSW_")]
        for k, v in items:
            if isinstance(v, str) and not k.startswith("_"):
                out[k] = (v, str(f.relative_to(REPO)))
    return out


def assignment_map():
    if not ASSIGN.exists():
        return {}
    out = {}
    for r in json.load(open(ASSIGN)):
        b = re.sub(r"^[AP]_", "", r["id"])
        if r.get("ported") and r["ported"] != b:
            out[b] = (r["ported"], str(ASSIGN.relative_to(REPO)))
    return out


def stem(dn):
    s = re.sub(r"^(RSW_|RM_|RUT_|rut_|AA_|SW_|BMT_|VCE_|JOE_|AEXP_|VFEI2_|AB_|RG_|ZB_)", "", dn)
    return re.sub(r"^Plant_", "", s)


# ───────────────────────────────────────────────────────────────── canon ──

def canon_index():
    """defName -> slug, from the generated INDEX.md table."""
    out = {}
    p = CANON / "INDEX.md"
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        m = re.match(r"\|\s*\[([^\]]+)\]\([^)]*\)\s*\|\s*[^|]*\|\s*([^|]*)\|", line)
        if m:
            for dn in re.findall(r"[A-Za-z0-9_]+", m.group(2)):
                out.setdefault(dn, m.group(1))
    # entries newer than the generated INDEX.md: their own "**defName**: `X`" line
    for d in sorted(CANON.iterdir()):
        f = d / "description.md"
        if d.is_dir() and f.exists():
            for line in f.read_text(errors="replace").splitlines()[:12]:
                if line.lower().startswith("**defname"):
                    for dn in re.findall(r"`([A-Za-z0-9_]+)`", line):
                        out.setdefault(dn, d.name)
    return out


def canon_info(slug_dir: Path, match):
    txt = (slug_dir / "description.md").read_text(errors="replace") if (slug_dir / "description.md").exists() else ""
    secs = {m.group(1).strip().lower(): m.group(2).strip()
            for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", txt, re.S | re.M)}
    must = secs.get("must show", "")
    rul = secs.get("ruling", "")
    imgs = sorted(str(p.relative_to(REPO)) for p in slug_dir.iterdir()
                  if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not p.name.startswith("donor_"))
    return {"entry": str(slug_dir.relative_to(REPO)), "match": match, "images": imgs,
            "has_must_show": bool(re.search(r"^\s*[-*\d]", must, re.M)),
            "ruled": bool(rul) and "owner has not reviewed" not in rul,
            "wookieepedia": None, "canon_missing_entry": False}


def wookiee_lookup(names, cache):
    """First exact-title hit (normalised) for any of names, else None. Cached by name."""
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    for n in names:
        if not n:
            continue
        if n not in cache:
            url = ("https://starwars.fandom.com/api.php?action=query&list=search&format=json&srlimit=8&srsearch="
                   + urllib.parse.quote(n))
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "RimMandrake-biome-census/1"})
                d = json.loads(urllib.request.urlopen(req, timeout=20).read())
                cache[n] = [h["title"] for h in d.get("query", {}).get("search", [])]
            except Exception as e:  # noqa: BLE001 — record, never treat as "absent"
                cache[n] = {"error": str(e)[:120]}
        hits = cache[n]
        if isinstance(hits, dict):
            return {"query": n, "error": hits["error"]}
        for t in hits:
            base = t[:-8] if t.endswith("/Legends") else t
            if norm(base) == norm(n):
                box = wookiee_infobox(t, cache)
                if box is None:
                    continue          # a person/place/object page with the same name: not a lifeform
                return {"query": n, "title": t, "legends": t.endswith("/Legends"), "infobox": box}
    return None


LIFEFORM_BOX = re.compile(r"\{\{\s*(Species|Creature|Plant|Fungus|Lifeform|Fauna|Flora)\s*[\n|}]")


def wookiee_infobox(title, cache):
    """The page's lifeform infobox name (Species/Plant/...), or None. Cached under 'page:<title>'."""
    k = "page:" + title
    if k not in cache:
        url = ("https://starwars.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main"
               "&format=json&redirects=1&titles=" + urllib.parse.quote(title))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RimMandrake-biome-census/1"})
            d = json.loads(urllib.request.urlopen(req, timeout=20).read())
            pg = next(iter(d["query"]["pages"].values()))
            w = pg.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
            m = LIFEFORM_BOX.search(w)
            cache[k] = m.group(1) if m else ""
        except Exception as e:  # noqa: BLE001
            return f"ERROR {str(e)[:60]}"
    return cache[k] or None


def split_camel(s):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s).replace("_", " ").strip()


# ─────────────────────────────────────────────────────────────── artpipe ──

def artpipe_jobs(terms):
    """term -> sorted job families (word-boundary filtered), from artpipe_state.py find --names-only."""
    terms = sorted({t.lower() for t in terms if len(t) >= 3})
    cmd = [sys.executable, str(REPO / "src/RimMandrake/Utils/artpipe/artpipe_state.py"), "find",
           "--names-only", "--limit", "100000", *terms]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if out.returncode != 0:
        return None, out.stderr.strip()[-300:]
    res, cur, head = defaultdict(set), None, ""
    for line in out.stdout.splitlines():
        m = re.match(r"^(\S.*?): (\d+) hit\(s\)$", line)
        if m:
            cur = m.group(1)
            continue
        if line.startswith("searched"):
            head = line
        if cur and line.startswith("  ") and not line.strip().startswith("…"):
            p = line.strip().split(" (content)")[0]
            name = re.sub(r"^LEGACY .*?/(_artsrc|done|pending|failed|running)/", "", p)
            name = re.sub(r"^(_artsrc|done|pending|failed|running|[a-z_]+)/", "", name).rstrip("/")
            name = re.sub(r"(\.manifest)?\.json$|\.png$", "", name)
            fam = re.sub(r"_(north|east|south|west)(_r\d+)?$", "", name)
            if re.search(rf"(^|_){re.escape(cur)}(_|$)", fam.lower()):   # word-bounded both sides (B2: fuzz≠Fuzzrunner)
                if ":" not in fam:
                    res[cur].add(fam)
    return {k: sorted(v) for k, v in res.items()}, head


# ──────────────────────────────────────────────────────────────── main ──

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(REPO / "Transient" / "biome_ffar"))
    ap.add_argument("--no-wookiee", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    md_path, js_path = out / "census.md", out / "census.json"
    unmeasured = ["base rosters of vanilla/donor BiomeDefs (e.g. Core's own Desert cast) — only OUR patches onto them are read",
                  "Cherry Picker cuts and other mods' biome patches — not applied",
                  "art the game draws from a donor mod for a donor-only row, unless the ledger holds that donor texture"]

    log("rosters")
    R = read_rosters()
    D, renames, copied = read_our_defs()
    ML, AS = mlie_map(), assignment_map()
    log(f"{len(R)} BiomeDefs with rosters/patches, {len(D)} our ThingDef/PawnKindDefs, {len(renames)} rename comments")

    def port_of(name):
        if OURS_RE.match(name) and name in D:
            return name, "is_ours"
        for src_map, how in ((renames, "rename_comment"), (AS, "desert_assignment"), (ML, "mlie_map")):
            if name in src_map and src_map[name][0] in D:
                return src_map[name][0], f"{how}:{src_map[name][1]}"
        for c in ("RSW_" + name, "RM_" + name, "RUT_" + name, "RSW_" + stem(name), "RSW_Plant_" + stem(name)):
            if c in D:
                return c, "stem_rule"
        return None, None

    # biomes = the Baroque Biomes compose set, one per RM_ BiomeDef
    BB = baroque_biomes()
    grouped = {dn for dn, _, _, _ in BB}
    order = [d for d in FIRST if d in grouped] + sorted(d for d in grouped if d not in FIRST)
    gmap = {dn: (lbl or dn, [dn], f, ek) for dn, lbl, f, ek in BB}
    unmapped = {dn: len(rec["entries"]) for dn, rec in R.items() if dn not in grouped and rec["entries"]}

    # art plumbing
    log("art ledger")
    idx = L.Index()
    slots = L.scan_def_slots()
    lorder, lfp = A.load_order()
    SW = S_.World(index=idx)
    tex_by_def = defaultdict(set)
    for tp, ss in slots.items():
        for s in ss:
            if s["role"] in BODY_ROLES:
                tex_by_def[s["subject"].split("#")[0]].add(tp)
    for dn, rec in D.items():
        if rec.get("race") and rec["race"] != dn:
            tex_by_def[rec["race"]] |= tex_by_def.get(dn, set())
    all_res = set(idx.by_res) | {L.parse_texfile(rel)["res"] for (_, rel) in idx.live}
    row_cache = {}

    def res_art(res):
        if res not in row_cache:
            row_cache[res] = A.build_row(idx, res, lorder, slots)
        return row_cache[res]

    # prior owner selection (desert sitting 1)
    prior = {}
    if SIT1.exists():
        dj = json.load(open(SIT1))
        snap = json.load(open(REPO / dj["snapshot"])) if (REPO / dj["snapshot"]).exists() else {"rows": {}}
        for res, dec in dj["decisions"].items():
            srow = snap["rows"].get(res, {})
            letter = dec.get("decision", "")
            prior[res] = {"sheet": dj["sheetId"], "decision": letter, "note": dec.get("note", ""),
                          "prefill": dec.get("prefill", ""), "changed_from_prefill": letter != dec.get("prefill", ""),
                          "picked_label": srow.get("labels", {}).get(letter),
                          "picked_faces": srow.get("columns", {}).get(letter), "saved_at": dj.get("savedAt")}

    # canon
    cidx = canon_index()
    cache = json.load(open(WOOKIEE_CACHE)) if WOOKIEE_CACHE.exists() else {}

    def canon_for(defnames, label):
        for dn in defnames:
            if dn in cidx and (CANON / cidx[dn]).is_dir():
                return canon_info(CANON / cidx[dn], "index_defname")
        e = A.canon_entry(*(list(defnames) + ([label] if label else [])))
        if e:
            return canon_info(REPO / e["dir"], "dir_name")
        # A1: a Star Wars row whose name carries a variant word (WraidAlpha, FaaJuv) -> the base species' entry
        for dn in defnames:
            e, base = A.canon_base(dn, label or "", {k: str(CANON / v) for k, v in cidx.items()})
            if e:
                return dict(canon_info(REPO / e["dir"], "variant_stripped"), base=base)
        # A1: a Star Wars row drawn with a canon creature's texture -> that creature's entry
        for dn in defnames:
            if not dn.startswith("RSW_"):
                continue
            for y, ev in sorted(tex_twins.get(dn, ())):
                if y in cidx and (CANON / cidx[y]).is_dir():
                    return dict(canon_info(CANON / cidx[y], "texpath_twin"), base=f"{cidx[y]} (shares its texture)")
        # last: the one resolver (subject.py) — INDEX defNames, own-line defNames, variant-stripped, twins
        sc = S_.resolve_canon(defnames[0], SW, originals=defnames[1:])
        if sc["match"] != "none" and sc["slug"] and (CANON / sc["slug"]).is_dir():
            out = canon_info(CANON / sc["slug"], f"subject:{sc['match']}")
            return dict(out, base=sc["slug"]) if sc["match"] == "base-species" else out
        return None

    # shared-texpath twins
    tex_twins = defaultdict(set)
    for tp, ss in slots.items():
        subs = {s["subject"].split("#")[0] for s in ss}
        rsw = {s for s in subs if s.startswith("RSW_")}
        rm = {s for s in subs if re.match(r"^(RM_|RUT_|rut_)", s)}
        for x in rm:
            for y in rsw:
                if stem(x).lower() != stem(y).lower():
                    tex_twins[x].add((y, f"shares texPath {tp}"))
                    tex_twins[y].add((x, f"shares texPath {tp}"))

    def twins_of(port, donors):
        tw = []
        for dn in donors:
            tw.append({"defName": dn, "relation": "donor", "evidence": "same row (donor bare defName)"})
        if port:
            s = stem(port)
            for pre in ("RSW_", "RM_", "RUT_", "rut_"):
                c = pre + s
                if c != port and c in D:
                    tw.append({"defName": c, "relation": "tier_twin_same_stem", "evidence": f"{port} / {c}"})
            for y, ev in sorted(tex_twins.get(port, ())):
                tw.append({"defName": y, "relation": "tier_twin_shared_texpath", "evidence": ev})
            if port in copied:
                tw.append({"defName": copied[port][0], "relation": "tier_twin_comment",
                           "evidence": f"'copied from' in {copied[port][1]}"})
            for x, (src_, f) in copied.items():
                if src_ == port:
                    tw.append({"defName": x, "relation": "tier_twin_comment", "evidence": f"'copied from' in {f}"})
        seen, outl = set(), []
        for t in tw:
            if t["defName"] not in seen:
                seen.add(t["defName"])
                outl.append(t)
        return outl

    # ── build rows ──
    biomes = {}
    all_rows = []
    for bk in order:
        lbl, defs, bfile, ekey = gmap[bk]
        rows = {}
        for bd in defs:
            rec = R.get(bd)
            if not rec:
                continue
            for (field, name), pl in rec["entries"].items():
                port, how = port_of(name)
                key = port or name
                kind = LISTS[field]
                r = rows.setdefault((kind, key), {"key": key, "kind": kind, "port": port, "donors": [],
                                                  "pairing": {}, "placements": []})
                if name != key and name not in r["donors"]:
                    r["donors"].append(name)
                    r["pairing"][name] = how
                r["placements"].append(dict(pl, biome_def=bd))
        biomes[bk] = {"label": lbl, "biome_def": bk, "biome_file": bfile, "compose_entry": ekey,
                      "order": order.index(bk),
                      "defs": [{"defName": d, "ours": R.get(d, {}).get("ours", False),
                                "file": R.get(d, {}).get("file"), "rows_here": len(R.get(d, {}).get("entries", {}))}
                               for d in defs], "rows": sorted(rows.values(), key=lambda r: (r["kind"], r["key"].lower()))}
        # Star Wars twins (owner, 2026-10-04, by card): an RM_/RUT_ stand-in's RSW_ twin is a full LINKED row of
        # the same biome even though the biome never casts it — judged in the same sitting, never skipped as
        # "related, not in this biome". Flagged twin_row_of; carries no placement.
        have = {r["key"] for r in biomes[bk]["rows"]}
        for r in list(biomes[bk]["rows"]):
            if not (r["port"] and re.match(r"^(RM_|RUT_|rut_)", r["port"])):
                continue
            c = "RSW_" + stem(r["port"])
            if c in D and c not in have:
                have.add(c)
                biomes[bk]["rows"].append({"key": c, "kind": r["kind"], "port": c, "donors": [], "pairing": {},
                                           "placements": [], "twin_row_of": r["key"],
                                           "layer": f"Star Wars twin of {r['key']} (not cast in this biome)"})
        biomes[bk]["rows"].sort(key=lambda r: (r["kind"], r["key"].lower()))
        all_rows += biomes[bk]["rows"]
    log(f"{len(all_rows)} biome rows across {len(order)} biomes")

    # artpipe_state, one call
    stems = {stem(r["key"]).lower() for r in all_rows} | {stem(d).lower() for r in all_rows for d in r["donors"]}
    log(f"artpipe_state find over {len(stems)} stems")
    ajobs, ahead = artpipe_jobs(stems)
    if ajobs is None:
        unmeasured.append(f"artpipe_state find failed: {ahead}")
        ajobs = {}

    # canon + wookiee for every distinct row identity
    ids = {}
    for r in all_rows:
        ids.setdefault(r["key"], r)
    canon_by = {}
    for k, r in ids.items():
        label = (D.get(k) or {}).get("label")
        canon_by[k] = canon_for([k] + r["donors"], label)
    if not a.no_wookiee:
        todo = [k for k, c in canon_by.items() if c is None]
        log(f"wookieepedia exact-title check for {len(todo)} rows with no canon entry")

        def wq(k):
            label = (D.get(k) or {}).get("label")
            names = [label, split_camel(stem(k))] + [split_camel(stem(d)) for d in ids[k]["donors"]]
            return k, wookiee_lookup(list(dict.fromkeys(n for n in names if n)), cache)
        with ThreadPoolExecutor(6) as ex:
            wres = dict(ex.map(wq, todo))
        WOOKIEE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        WOOKIEE_CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True))
    else:
        wres = {}
        unmeasured.append("canon_missing_entry: --no-wookiee given, Wookieepedia not consulted")

    # md skeleton header
    md = [f"# Biome flora/fauna art census — {time.strftime('%Y-%m-%d %H:%M')}",
          "", "Item `BIOME_FLORAFAUNA_ART_REVIEW_1`. Generator: `src/RimMandrake/Utils/art/biome_census.py` "
          "(schema in its docstring). Machine-readable: `census.json` beside this file.", "",
          "Columns: **rows** = species rows (donor + our port merged) · **art** = rows with ≥1 picture set in the "
          "art ledger · **canon** = rows with a `canon_references` entry · **canon, no entry** = no entry but an "
          "exact Wookieepedia title (a candidate, not proof) · **non-canon twin** = canon row with an RM_/RUT_ "
          "stand-in, or the stand-in itself · **any twin** = donor/port or RM_/RSW_ relation of any kind · "
          "**no art** = zero picture sets.", ""]
    md_path.write_text("\n".join(md) + "\n_filling…_\n")

    tot = defaultdict(int)
    for bk in order:
        B = biomes[bk]
        for r in B["rows"]:
            k = r["key"]
            label = (D.get(k) or {}).get("label")
            r["label"] = label
            r["defNames"] = ([k] if r["port"] else []) + r["donors"] + ([] if r["port"] else [k])
            r["defNames"] = list(dict.fromkeys(r["defNames"]))
            cs = [p["commonality"] for p in r["placements"] if p["commonality"] is not None]
            r["commonality_max"] = max(cs) if cs else None
            c = canon_by.get(k)
            if c is None:
                c = {"entry": None, "match": None, "images": [], "has_must_show": False, "ruled": False,
                     "wookieepedia": wres.get(k), "canon_missing_entry": bool(wres.get(k) and wres[k].get("title"))}
            r["canon"] = c
            r["twins"] = twins_of(r["port"], r["donors"])
            present = {x["key"] for x in B["rows"]} | {d for x in B["rows"] for d in x["donors"]}
            for t in r["twins"]:
                t["in_this_biome"] = t["defName"] in present
            # art
            res_list = []
            texs = set()
            for dn in r["defNames"]:
                texs |= tex_by_def.get(dn, set())
            joined = "def"
            if not texs:                  # donor/vanilla def: what the game draws, from the live (post-patch) dump
                texs = set(SW.live_texpaths(r["defNames"]))
                joined = "live-def-dump"
            if not texs:
                pat = re.compile(rf"(^|/){re.escape(stem(k))}(_[a-z]{{1,2}})?$", re.I)
                texs = {rr for rr in all_res if pat.search(rr)}
                joined = "name"
            for res in sorted(texs):
                if res.lower().endswith(("_dessicated", "_desiccated", "_corpse")):
                    continue
                br = res_art(res)
                vers, live = [], None
                for col in br["cols"]:
                    v = {"kind": col["kind"], "label": col["label"], "detail": col.get("detail", ""),
                         "date": col.get("date", ""), "faces": col["faces"],
                         "near_dup_of": col["near_of"]["label"] if col.get("near_of") else None}
                    vers.append(v)
                    if col["kind"] == "live" and (col.get("winner") or live is None):
                        live = {"mod": col.get("mod"), "label": col["label"], "faces": col["faces"],
                                "winner_by_load_order": bool(col.get("winner"))}
                res_list.append({"res": res, "role": next((s["role"] for s in slots.get(res, [])), "body"),
                                 "joined_by": joined, "in_ledger": res in all_res, "subjects": br["subjects"], "live": live,
                                 "versions": vers, "prior_selection": prior.get(res)})
            nv = sum(len(x["versions"]) for x in res_list)
            st = stem(k).lower()
            r["artpipe_state_jobs"] = sorted(set(ajobs.get(st, [])) | {j for d in r["donors"] for j in ajobs.get(stem(d).lower(), [])})
            # A2a/A2b: renders found by name are art (name-matched), never NO ART. Name matching goes through
            # subject.py (whole-token, never prefix-only) so the census and the sheet resolve the row ONE way.
            searched = None
            if not nv:
                sa = S_.resolve_art(k, SW, originals=r["donors"])
                fams = sorted({c["ref"] for c in sa["columns"] if c["kind"] in ("render", "job") and c["role"] == "body"})
                r["artpipe_state_jobs"] = sorted(set(r["artpipe_state_jobs"]) | set(fams))
                searched = S_.describe_none(sa["searched"]) if not sa["columns"] and not r["artpipe_state_jobs"] else None
            basis = "ledger" if nv else ("name-matched" if r["artpipe_state_jobs"] else "none")
            r["art"] = {"resources": res_list, "n_versions": nv, "has_art": basis != "none", "basis": basis,
                        "live_res": sum(1 for x in res_list if x["live"]),
                        "in_game": sum(1 for x in res_list for v in x["versions"] if v["label"].startswith("IN GAME"))}
            if searched:
                r["art"]["searched"] = searched
            keys = {L.subject_key(x) for x in r["defNames"]}
            r["ledger_rulings"] = [{"verdict": x.get("verdict"), "by": x.get("by"), "trust": x.get("trust"),
                                    "ts": x.get("ts"), "via": x.get("via"),
                                    "row": (x.get("target") or {}).get("row")}
                                   for x in sorted(idx.subject_rulings(keys), key=lambda x: x.get("ts", ""))][-6:]
        # non-canon twin flag (needs every row's canon first)
        canon_keys = {x["key"] for x in B["rows"] if x["canon"]["entry"]} | {k for k, c in canon_by.items() if c}
        for r in B["rows"]:
            tw_tier = [t for t in r["twins"] if t["relation"].startswith("tier_twin")]
            if r["canon"]["entry"]:
                r["noncanon_twin"] = [t["defName"] for t in tw_tier if re.match(r"^(RM_|RUT_|rut_)", t["defName"])]
            else:
                r["noncanon_twin"] = [t["defName"] for t in tw_tier if t["defName"] in canon_keys
                                      or canon_for([t["defName"]], None)]
        rs = [x for x in B["rows"] if not x.get("twin_row_of")]
        S = {"twin_rows": len(B["rows"]) - len(rs), "rows": len(rs), "fauna": sum(r["kind"] == "fauna" for r in rs),
             "flora": sum(r["kind"] == "flora" for r in rs), "fish": sum(r["kind"] == "fish" for r in rs),
             "with_art": sum(r["art"]["has_art"] for r in rs), "no_art": sum(not r["art"]["has_art"] for r in rs),
             "canon_entry": sum(bool(r["canon"]["entry"]) for r in rs),
             "canon_missing_entry": sum(r["canon"]["canon_missing_entry"] for r in rs),
             "noncanon_twin": sum(bool(r["noncanon_twin"]) for r in rs),
             "any_twin": sum(bool(r["twins"]) for r in rs),
             "prior_selection_rows": sum(any(x["prior_selection"] for x in r["art"]["resources"]) for r in rs)}
        B["summary"] = S
        for kk, vv in S.items():
            tot[kk] += vv
        # md, filled per biome
        lay = defaultdict(int)
        for r in rs:
            for pl in r["placements"]:
                lay[pl["layer"] if pl["layer"] == "inline_RM" else "patch " + pl["patch_mod"]] += 1
        md += [f"## {order.index(bk) + 1}. {B['label']} (`{bk}`)", "",
               f"file `{bfile}` · layers: " + ", ".join(f"{k} {v}" for k, v in sorted(lay.items())), "",
               "defs: " + ", ".join(f"`{d['defName']}` ({d['rows_here']})" for d in B["defs"]), "",
               "| rows | fauna | flora | fish | art ≥1 | canon | canon, no entry | non-canon twin | any twin | no art |",
               "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
               f"| {S['rows']} | {S['fauna']} | {S['flora']} | {S['fish']} | {S['with_art']} | {S['canon_entry']} | "
               f"{S['canon_missing_entry']} | {S['noncanon_twin']} | {S['any_twin']} | {S['no_art']} |", ""]
        noart = [r for r in rs if not r["art"]["has_art"]]
        if noart:
            def why(r):
                rs_ = [x["res"] for x in r["art"]["resources"]]
                return (f" — texPath `{rs_[0]}` not in the art ledger and no copy in any game root" if rs_
                        else " — no texPath resolved") + (f" ({r['art']['searched']})" if r["art"].get("searched") else "")
            md.append("**NO ART** (no picture set of ours in the ledger):")
            md += [f"- `{r['key']}`" + (f" ({r['label']})" if r["label"] else "") + why(r) for r in noart]
            md.append("")
        cme = [r for r in rs if r["canon"]["canon_missing_entry"]]
        if cme:
            md.append("**Canon, no entry (Wookieepedia title):** " + ", ".join(
                f"`{r['key']}` → {r['canon']['wookieepedia']['title']}" for r in cme))
            md.append("")
        nct = [r for r in rs if r["noncanon_twin"]]
        if nct:
            md.append("**Non-canon twins:** " + ", ".join(f"`{r['key']}` ↔ " + "/".join(f"`{t}`" for t in r["noncanon_twin"])
                                                       for r in nct))
            md.append("")
        md_path.write_text("\n".join(md) + "\n_filling…_\n")
        log(f"{bk}: {S}")

    # sanity probe
    probe = {}
    for p in PROBES:
        probe[p] = sum(1 for r in all_rows if any(p in d.lower() for d in r["defNames"])
                       or p in (r.get("label") or "").lower()
                       or any(p in x["res"].lower() for x in r["art"]["resources"]))
    probe["_canon_index_defnames"] = len(cidx)
    probe["_artpipe_jobs_anooba"] = len(ajobs.get("anooba", []))
    probe["_ledger_variants"] = len(idx.variants)
    bad = [p for p in REQUIRED_PROBES if probe[p] == 0] + [p for p in ("_canon_index_defnames", "_ledger_variants")
                                                          if probe[p] == 0]
    werr = sum(1 for v in wres.values() if v and v.get("error"))
    if werr:
        unmeasured.append(f"Wookieepedia lookup errored for {werr} rows — their canon_missing_entry is UNMEASURED")

    md += ["## Planet totals", "",
           "| rows | fauna | flora | fish | art ≥1 | canon | canon, no entry | non-canon twin | any twin | no art |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
           f"| {tot['rows']} | {tot['fauna']} | {tot['flora']} | {tot['fish']} | {tot['with_art']} | {tot['canon_entry']} | "
           f"{tot['canon_missing_entry']} | {tot['noncanon_twin']} | {tot['any_twin']} | {tot['no_art']} |", "",
           "Rows are per biome: a species cast in two biomes counts in each. "
           f"Distinct species rows: {len(ids)}.", "",
           "**Sanity probe** (rows hit; a zero on korrum/hawkbat/bantha means the census is broken): "
           + ", ".join(f"{k} {v}" for k, v in probe.items()), "",
           "", "**UNMEASURED:**", *[f"- {u}" for u in unmeasured], ""]
    md_path.write_text("\n".join(md) + "\n")

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    J = {"schema": "biome_ffar.census/1", "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "git_head": head,
         "inputs": {"ledger_events": len(idx.events), "ledger_variants": len(idx.variants), "load_order": lfp,
                    "artpipe_state": ahead, "wookieepedia": not a.no_wookiee, "prior_selection_sheet": str(SIT1.relative_to(REPO))},
         "sanity_probe": probe, "biome_order": order, "biomes": biomes,
         "totals": dict(tot, distinct_species=len(ids)),
         "unmapped_patch_targets": unmapped, "unmeasured": unmeasured}
    js_path.write_text(json.dumps(J, indent=1, sort_keys=False))
    log(f"wrote {js_path} and {md_path}; totals {dict(tot)}; probe {probe}")
    if bad:
        print(f"SANITY PROBE FAILED: {bad} — the census cannot see known-present species; do not trust it", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
