#!/usr/bin/env python3
"""art_size_audit.py -- deep scan of the drawn size of every plant and animal WE define.

VERSION 1.0 (2026-11-03). Item: ART_SIZES_AUDIT_AFTER_DONORS_LEAVE.
Owner, 2026-10-16: "After we finish retiring the donor mods we really need to do a deep scan of
the art sizes for flora and fauna." (Hydenock and jogan had been far too small.)

WHAT IT READS (no dump, no game)
================================
The owner's full load set exactly as plant_draw_layers.py builds it (mandrake.* read from THIS
repo, every Patches/ operation applied, ParentName resolved nearest-wins), but keeping ThingDef
AND PawnKindDef. Subjects are every non-abstract plant (`plant` present) and animal (`race`
present, intelligence Animal, flesh not Mechanoid) whose defining package is mandrake.*. Every
ludeon.* plant and animal is read too, as the REFERENCE envelope.

WHAT A SIZE IS
==============
* plant: mature cells = max(graphicData/drawSize) x visualSizeRange max (the engine lerps
  visualSizeRange by growth, so full growth draws at the max).
* animal: adult cells = max(drawSize) of the LAST lifeStage's bodyGraphicData of the race's
  PawnKindDef; body = race/baseBodySize (default 1).
* sprite fill: the alpha (>16) bounding box of the def's own PNG as a fraction of its canvas
  (Graphic_Random: the mean over the folder; Graphic_Multi: _east for animals, _south for
  plants). visible = cells x fill. Vanilla textures are not loose, so only OUR sprites get a fill.

THE RULES (severity HIGH gates --check; MEDIUM and INFO are listed for the review)
================================================================================
HIGH  TREE_TIER        a tree the owner tiered on the tree-tiers sheet (q.tier) whose mature
                       cells sit outside that tier (small 3-5, big 5-8, giant 8-12, titanic 12+),
                       with 5% slack at each edge for the enactment's rounding.
HIGH  OWNER_ORDER      the newest owner size order (a saved sheet note: "N cells|squares", "size N",
                       or a bare number on a `resize` row) for this def -- or its donor ancestor,
                       matched by name stem -- is off by more than 1.25x, and no later tree tier
                       supersedes it.
REVIEW ANIMAL_ENVELOPE adult drawSize vs bodySize is outside everything vanilla does: the log-log
                       residual against the vanilla fit exceeds 1.25x the largest vanilla residual.
                       Not a gate: whether a creature is MEANT to read tiny or huge is a taste call
                       for a true-scale judge sitting, so these are listed, never auto-fixed. A
                       creature with a numeric owner order is exempt: its size is his call.
HIGH  BAD_SIZE         a drawn size of zero or less.
HIGH  NO_SPRITE        no texPath at all; or the texPath resolves to no loose texture in the
                       def's own mod or ours, nor in any loaded non-vanilla mod, and no vanilla
                       def draws that texPath. A Graphic_Single must be exactly <texPath>.png.
MEDIUM VANILLA_TEXTURE the def draws a vanilla texture (a placeholder, or art never made).
MEDIUM PLANT_ENVELOPE  mature cells below 0.8x or above 1.5x the vanilla range for its class
                       (tree / non-tree), and no owner tier or order covers it.
MEDIUM SPRITE_PADDED   the subject fills under 55% of its canvas on both axes: it draws smaller
                       than its numbers say.
MEDIUM DONOR_TEXTURE   the texture resolves only inside a non-mandrake, non-ludeon mod.
MEDIUM FICTION         the description's words or metres disagree with the drawn size
                       ("towering"/"giant"/"N metres tall" drawn small, "tiny" drawn big).
MEDIUM BIN_RESCALE     the owner moved the size bin off the prefill and the size is outside it
                       (10% slack); a numeric order or a tree tier, being more precise, outranks it.
INFO  ORDER_MATCHED    an owner order honoured (within 1.25x), for the record.

A HIGH may be waived only in art_size_audit_waivers.json ({defName: {code: why}}), with a reason
(a blank reason waives nothing). --check also fails a scan that cannot be complete: a mod of the
load set missing, an xpath error, or a size patch the runner cannot apply.
Known blind spots: a def ADDED by a patch carries no defining package and is not audited; a
patch Conditional on a def type other than ThingDef/PawnKindDef/BiomeDef sees no match.

USAGE
    python3 src/RimMandrake/Utils/art_size_audit.py                    # summary + HIGH list
    python3 src/RimMandrake/Utils/art_size_audit.py --md report.md --json rows.json
    python3 src/RimMandrake/Utils/art_size_audit.py --from-json rows.json --md report.md
    python3 src/RimMandrake/Utils/art_size_audit.py --check            # exit 0 = no unwaived HIGH
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys

from lxml import etree as LX

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import plant_draw_layers as PDL  # noqa: E402

WAIVERS = os.path.join(HERE, "art_size_audit_waivers.json")
TREE_TIER_SHEET = os.path.join(REPO, "Transient", "biome_ffar",
                               "tree_tiers_sheet_2026-10-18.decisions.json")
TIERS = {"small": (3.0, 5.0), "big": (5.0, 8.0), "giant": (8.0, 12.0), "titanic": (12.0, 1e9)}
# design/Jawa/worldbuilding/flora_commission_template.md:177 -- the owner's bins, in cells.
BINS = {"small": (0.0, 1.0), "medium": (1.0, 2.2), "large": (2.2, 5.0), "titan": (5.0, 1e9)}
ORDER_SOURCES = [
    os.path.join(REPO, "design", "Jawa", "worldbuilding", "review", "*.decisions.json"),
    os.path.join(REPO, "infrastructure", "state", "art_rulings", "*.decisions.json"),
    os.path.join(REPO, "Transient", "biome_ffar", "*.decisions.json"),
]
SANITY = {"our_plants": 100, "our_animals": 40, "ref_plants": 30, "ref_animals": 40}

# Only these types go through the patch runner (keeping every type is >3x slower): BiomeDef so
# a Conditional on one sees what the engine sees. The vanilla texture index is taken from EVERY
# ludeon def at load (build_doc), so terrain, building and item art count as vanilla.
KEEP_TAG = re.compile(r"(^|\.)(ThingDef|PawnKindDef|BiomeDef)$")
ALPHA_MIN = 16
VANILLA_TEX = set()   # texPaths named by any ludeon def, any type (filled by build_doc)

BIG_WORDS = re.compile(r"\b(towering|gigantic|giant|huge|massive|enormous|colossal|immense|"
                       r"titanic|mountainous|leviathan|behemoth)\b", re.I)
SMALL_WORDS = re.compile(r"\b(tiny|diminutive|miniature|minuscule|palm-sized|thumb-sized|"
                         r"fist-sized|knee-high|ankle-high|low-growing|creeping)\b", re.I)
NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15,
            "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}
METRES = re.compile(r"\b(\d+(?:\.\d+)?|" + "|".join(NUMWORDS) + r")(?:\s*(?:-|to|–)\s*"
                    r"(?:\d+(?:\.\d+)?|" + "|".join(NUMWORDS) + r"))?\s*(?:-\s*)?"
                    r"(m|meters?|metres?)\b\s*(?:-\s*)?(tall|high|long|across|wide|in length|"
                    r"in height|wingspan)?", re.I)
# An enacted order sets the max to his number; past 1.25x either way it was not enacted.
ORDER_TOL = 1.25
# A pawn is ~1.75 m and draws ~1.5 cells: about 1.2 m a cell. Metres disagree only past 3x.
M_PER_CELL = 1.2
_ORDER_NUM = r"\d*\.?\d+|half an?|quarter of an?|an?|" + "|".join(NUMWORDS)
ORDER_RE = re.compile(r"(?<![\d.\w])(" + _ORDER_NUM + r")\s*(?:-|to|~)?\s*(?:\d*\.?\d+)?\s*"
                      r"(cells?|squares?)\b", re.I)
ORDER_WORDS = {"half a": 0.5, "half an": 0.5, "quarter of a": 0.25, "quarter of an": 0.25,
               "a": 1.0, "an": 1.0}


# ── loading ─────────────────────────────────────────────────────────────────────────────

def build_doc(mods, active):
    root = LX.Element("Defs")
    nfiles = 0
    for m in mods:
        for p in PDL._rel_files(m, "Defs"):
            r = PDL._parse(p)
            nfiles += 1
            if r is None or r.tag != "Defs":
                continue
            for e in list(r):
                if not isinstance(e.tag, str):
                    continue
                if m["packageId"].startswith("ludeon."):
                    VANILLA_TEX.update(t.text.strip() for t in e.iter("texPath")
                                       if t.text and t.text.strip())
                if not KEEP_TAG.search(e.tag):
                    continue
                if not PDL._may_require_ok(e, active):
                    continue
                e.tag = e.tag.split(".")[-1]
                e.set("_pkg", m["packageId"])
                e.set("_file", p)
                root.append(e)
    return root, nfiles


class Resolver(PDL.Resolver):
    """plant_draw_layers' resolver, for one def tag."""

    def __init__(self, root, tag):
        self.by_name, self.by_def = {}, {}
        for e in root:
            if e.tag != tag:
                continue
            if e.get("Name"):
                self.by_name[e.get("Name")] = e
            dn = PDL._txt(e, "defName")
            if dn and (e.get("Abstract") or "").lower() != "true":
                self.by_def[dn] = e


def _vec(s):
    return PDL._vec(s)


def _f(s, default=None):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


# ── sprites ─────────────────────────────────────────────────────────────────────────────

def _fill(path):
    from PIL import Image
    try:
        im = Image.open(path)
        im.load()
    except Exception:
        return None
    w, h = im.size
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > ALPHA_MIN else 0).getbbox()
    if not bb or not w or not h:
        return (0.0, 0.0)
    return ((bb[2] - bb[0]) / w, (bb[3] - bb[1]) / h)


def _candidates(root, tex, gclass, prefer):
    """PNG files this texPath names under one Textures root, best facing first."""
    base = os.path.join(root, tex)
    out = []
    gclass = gclass or ""   # unknown class: lenient (directory, then facings)
    single = gclass.split(".")[-1] == "Graphic_Single"
    if single:   # the engine loads exactly <texPath>.png for a Graphic_Single, nothing else
        return [base + ".png"] if os.path.isfile(base + ".png") else []
    if gclass.endswith("Random") or gclass.endswith("Collection") or os.path.isdir(base):
        if os.path.isdir(base):
            fs = sorted(f for f in os.listdir(base) if f.lower().endswith(".png")
                        and not re.search(r"_(north|m|mask)\.png$", f, re.I))
            pick = [f for f in fs if re.search(r"_%s\.png$" % prefer, f, re.I)] or \
                [f for f in fs if not re.search(r"_(south|east|west)\.png$", f, re.I)] or fs
            out = [os.path.join(base, f) for f in pick]
    if not out:
        for suf in ("_%s" % prefer, "", "_south", "_east", "_north"):
            p = base + suf + ".png"
            if os.path.isfile(p):
                out = [p]
                break
    return out


class Textures:
    def __init__(self, mods):
        self.roots = {}          # packageId -> [Textures dirs]
        for m in mods:
            # later LoadFolders roots override earlier ones, so search them first
            ds = [os.path.join(d, "Textures") for d in reversed(m["contentDirs"])]
            self.roots[m["packageId"]] = [d for d in ds if os.path.isdir(d)]
        self.ours = [d for p, ds in self.roots.items() if p.startswith("mandrake.") for d in ds]
        self.others = [(p, d) for p, ds in self.roots.items()
                       if not p.startswith(("mandrake.", "ludeon.")) for d in ds]
        self.cache = {}

    def resolve(self, pkg, tex, gclass, prefer):
        """(where, [png paths]) -- where is 'own', 'ours', 'donor:<pkg>' or None."""
        key = (pkg, tex, gclass, prefer)
        if key in self.cache:
            return self.cache[key]
        res = (None, [])
        for where, roots in (("own", self.roots.get(pkg, [])), ("ours", self.ours)):
            for r in roots:
                c = _candidates(r, tex, gclass, prefer)
                if c:
                    res = (where, c)
                    break
            if res[1]:
                break
        if not res[1]:
            for p, r in self.others:
                c = _candidates(r, tex, gclass, prefer)
                if c:
                    res = ("donor:" + p, c)
                    break
        self.cache[key] = res
        return res


def sprite_fill(paths):
    fs = [f for f in (_fill(p) for p in paths[:24]) if f]
    if not fs:
        return None
    return (round(sum(f[0] for f in fs) / len(fs), 3), round(sum(f[1] for f in fs) / len(fs), 3))


# ── extraction ──────────────────────────────────────────────────────────────────────────

def _is_animal(R, e):
    if R.field(e, "race") is None:
        return False
    intel = R.text(e, "race/intelligence") or "Animal"
    flesh = R.text(e, "race/fleshType") or ""
    tc = R.text(e, "thingClass") or ""
    return intel == "Animal" and flesh != "Mechanoid" and "AlienRace" not in tc


def _adult_graphic(K, kind):
    ls = K.field(kind, "lifeStages")
    if ls is None:
        return None
    lis = [li for li in ls if li.tag == "li"]
    for li in reversed(lis):
        g = li.find("bodyGraphicData")
        if g is not None:
            return g
    return None


def extract(root, mods, active):
    T = Resolver(root, "ThingDef")
    K = Resolver(root, "PawnKindDef")
    tex = Textures(mods)
    kinds = {}
    for dn, k in K.by_def.items():
        race = K.text(k, "race")
        if race:
            kinds.setdefault(race, []).append(k)
    rows = []
    for dn, e in T.by_def.items():
        pkg = e.get("_pkg") or ""
        ours, ref = pkg.startswith("mandrake."), pkg.startswith("ludeon.")
        if not (ours or ref):
            continue
        r = {"defName": dn, "package": pkg, "ours": ours, "label": PDL._txt(e, "label"),
             "description": T.text(e, "description") or "",
             "file": os.path.relpath(e.get("_file") or "", REPO) if ours else None}
        if T.field(e, "plant") is not None:
            ds = _vec(T.text(e, "graphicData/drawSize")) or [1.0]
            vsr = _vec(T.text(e, "plant/visualSizeRange")) or [0.9, 1.1]  # PlantProperties default
            tc = T.text(e, "plant/treeCategory")
            r.update(kind="plant", drawSize=ds, visualSizeRange=vsr,
                     tree=tc not in (None, "None"), cells=round(max(ds) * vsr[-1], 3),
                     texPath=T.text(e, "graphicData/texPath"),
                     graphicClass=T.text(e, "graphicData/graphicClass") or "Graphic_Single")
            prefer = "south"
        elif _is_animal(T, e):
            body = _f(T.text(e, "race/baseBodySize"), 1.0)
            ks = sorted(kinds.get(dn, []), key=lambda k: (PDL._txt(k, "defName") != dn,
                                                          PDL._txt(k, "defName") or ""))
            g = _adult_graphic(K, ks[0]) if ks else None
            # a bodyGraphicData with no drawSize draws at GraphicData's default (1,1)
            ds = (_vec(PDL._txt(g, "drawSize")) or [1.0]) if g is not None else None
            r.update(kind="animal", body=body, kindDef=PDL._txt(ks[0], "defName") if ks else None,
                     drawSize=ds, cells=round(max(ds), 3) if ds else None,
                     texPath=PDL._txt(g, "texPath") if g is not None else None,
                     graphicClass=(PDL._txt(g, "graphicClass") if g is not None else None)
                     or "Graphic_Multi")
            prefer = "east"
        else:
            continue
        if ours and r.get("texPath"):
            where, paths = tex.resolve(pkg, r["texPath"], r["graphicClass"], prefer)
            r["texWhere"] = where
            r["texFile"] = os.path.relpath(paths[0], REPO) if paths and paths[0].startswith(REPO) \
                else (paths[0] if paths else None)
            r["fill"] = sprite_fill(paths) if paths else None
        rows.append(r)
    return rows


# ── reference envelopes ─────────────────────────────────────────────────────────────────

def animal_fit(rows):
    pts = [(math.log(r["body"]), math.log(r["cells"])) for r in rows
           if r["kind"] == "animal" and not r["ours"] and r.get("cells") and r.get("body", 0) > 0]
    n = len(pts)
    if n < 3:
        return None
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx if sxx else 0.0
    a = my - b * mx
    res = [p[1] - (a + b * p[0]) for p in pts]
    sd = math.sqrt(sum(x * x for x in res) / max(1, n - 2))
    return {"a": a, "b": b, "n": n, "sd": sd, "maxres": max(abs(x) for x in res)}


def plant_env(rows):
    env = {}
    for cls in (True, False):
        v = sorted(r["cells"] for r in rows if r["kind"] == "plant" and not r["ours"]
                   and r["tree"] == cls)
        if v:
            env["tree" if cls else "plant"] = {"min": v[0], "max": v[-1], "n": len(v),
                                               "median": v[len(v) // 2]}
    return env


# ── owner orders ────────────────────────────────────────────────────────────────────────

def stem(name):
    s = name.split(":")[-1]
    s = re.sub(r"^[A-E]_(?=(RSW|RM|RUT)_)", "", s)      # a sheet's variant-row prefix: A_RUT_CrimsonCap
    s = re.sub(r"^(RSW_Plant_|RM_Plant_|RUT_Plant_|RSW_|RM_|RUT_|AB_|AA_|BMT_|VRE_|VFEI2_|VFEI_|AG_|GR_|"
               r"Ling_|SW_|Plant_|SWAC_)", "", s)
    s = re.sub(r"_(Wild|Race|Animal)$", "", s)
    s = re.sub(r"^(Plant|Tree)_?", "", s) if len(s) > 8 else s
    return re.sub(r"[^a-z0-9]", "", s.lower())


AGENT_NOTE = re.compile(r"IS your own ruling|you judged this against", re.I)
SIZE_WORD = re.compile(r"\bsize\s*(\d*\.?\d+)\b", re.I)
BARE_NUM = re.compile(r"^\s*(\d*\.?\d+)\b")


def order_cells(txt, decision=None):
    """The cells an owner note orders, or None: "N cells|squares", "size N", or -- on a row
    whose decision is `resize` (the rot size re-judge sheet) -- a bare leading number."""
    txt = txt or ""
    m = ORDER_RE.search(txt) or SIZE_WORD.search(txt)
    if not m and decision == "resize":
        m = BARE_NUM.search(txt)
    if not m:
        return None
    tok = re.sub(r"\s+", " ", m.group(1).lower())
    if tok in ORDER_WORDS:
        return ORDER_WORDS[tok]
    if tok in NUMWORDS:
        return float(NUMWORDS[tok])
    try:
        return float(tok)
    except ValueError:
        return None


CONFIRMED = re.compile(r"current number \((\d*\.?\d+) cells?\) IS your own ruling", re.I)
# Markdown rulings tables: (path, the column holding the ruled cells, the ruling's timestamp).
# rot_flora_fauna_names.md's table is the owner's 2026-09-19 ruling; the re-judge sheet that
# afternoon (16:3xZ) is later and wins where it speaks.
TABLE_SOURCES = [
    (os.path.join(REPO, "design", "Jawa", "worldbuilding", "biomes", "rot_flora_fauna_names.md"),
     "ruled width (cells)", "2026-09-19T12:00:00"),
]


def table_orders(sources=None):
    out = {}
    for path, col, at in TABLE_SOURCES if sources is None else sources:
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        idx = None
        for ln in lines:
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if col in cells:
                idx = cells.index(col)
                name_i = next((i for i, c in enumerate(cells) if c.lower() == "defname"), None)
                cur_i = next((i for i, c in enumerate(cells) if c.lower().startswith("current width")), None)
                continue
            if idx is None or not ln.startswith("|") or len(cells) <= idx or name_i is None:
                if idx is not None and not ln.startswith("|"):
                    idx = None
                continue
            ruled = cells[idx]
            if ruled in ("—", "-", "–") and cur_i is not None:
                # "—" = size unchanged at that sitting: the ruling is the width it then had
                ruled, how = re.sub(r"\s*\(.*$", "", cells[cur_i]), "unchanged at %s"
            else:
                how = "ruled width %s"
            try:
                n = float(ruled)
            except ValueError:
                continue
            name = cells[name_i].strip("`* ")
            out.setdefault(name, []).append({"cells": n, "note": (how % "%g" % n) + " (table)",
                                             "at": at, "file": os.path.relpath(path, REPO)})
    return out


def _at(v):
    return v.get("at") or v.get("decidedAt") or ""


def owner_orders(sources=None):
    """{key: [order]} from every decisions file. key = defName as written on the sheet."""
    out = {}
    seen = set()
    for pat in sources or ORDER_SOURCES:
        for f in sorted(glob.glob(pat)):
            try:
                d = json.load(open(f))
            except (OSError, ValueError):
                continue
            dd = d.get("decisions") if isinstance(d, dict) else None
            if not isinstance(dd, dict):
                continue
            for k, v in dd.items():
                if not isinstance(v, dict):
                    continue
                name = k.split(":")[-1]
                notes = []
                # A note is the owner's only on a row he saved (`at`/`decidedAt`); an unsaved row's
                # note is the sheet's own prefill text ("the current number (7 cells) IS your own
                # ruling ..."), agent words that must not count as an order.
                if _at(v) and not AGENT_NOTE.search(v.get("note") or ""):
                    notes.append((v.get("note") or "", _at(v), v.get("decision")))
                elif v.get("decision") == "ok" and CONFIRMED.search(v.get("note") or ""):
                    # the rot re-judge sheet: a row left at `ok` is a CONFIRMED size (its
                    # frozen_meaning counts them), the number being the one its note restates.
                    notes.append(("confirmed %s cells" % CONFIRMED.search(v["note"]).group(1),
                                  _at(v) or "%sT16:00:00" % (d.get("frozen_at") or ""), "ok"))
                for nf in v.get("notes_followed") or []:
                    if isinstance(nf, dict):
                        notes.append((nf.get("note") or "", nf.get("when") or nf.get("at") or "", None))
                for txt, at, dec in notes:
                    cells = order_cells(txt, dec)
                    if cells is None:
                        continue
                    sig = (name, txt.strip(), at)
                    if sig in seen:
                        continue
                    seen.add(sig)
                    out.setdefault(name, []).append({"cells": cells, "note": txt.strip(),
                                                     "at": at, "file": os.path.relpath(f, REPO)})
                sb, sp = v.get("sizeBin"), v.get("sizeBinPrefill")
                if sb in BINS and sp and sb != sp:
                    sig = (name, "bin:" + sb)
                    if sig not in seen:
                        seen.add(sig)
                        out.setdefault(name, []).append({"bin": sb, "from": sp, "at": _at(v),
                                                         "file": os.path.relpath(f, REPO)})
    return out


def tree_tiers(path=TREE_TIER_SHEET):
    try:
        dd = json.load(open(path))["decisions"]
    except (OSError, ValueError, KeyError):
        return {}
    return {k: (v.get("q") or {}).get("tier") for k, v in dd.items()
            if isinstance(v, dict) and (v.get("q") or {}).get("tier") in TIERS}


def match_orders(rows, orders):
    """Attach to each of our rows the orders whose key is its defName, else its name stem."""
    ours = [r for r in rows if r["ours"]]
    by_def = {r["defName"]: r for r in ours}
    by_stem = {}
    for r in ours:
        by_stem.setdefault(stem(r["defName"]), []).append(r)
        if r.get("label"):
            by_stem.setdefault(re.sub(r"[^a-z0-9]", "", re.sub(r"^wild ", "", r["label"].lower())),
                               []).append(r)
    unmatched = []
    for key, os_ in orders.items():
        # defName, then defName stem; a label stem only when no defName stem matches (a juvenile
        # labelled "dianoga" is not the Dianoga the order was about).
        st = stem(key)
        targets = [by_def[key]] if key in by_def else \
            [r for r in by_stem.get(st, []) if stem(r["defName"]) == st] or by_stem.get(st, [])
        if not targets:
            unmatched.append(key)
            continue
        for t in {id(t): t for t in targets}.values():
            for o in os_:
                t.setdefault("orders", []).append(dict(o, key=key))
    return unmatched


# ── judging ─────────────────────────────────────────────────────────────────────────────

def _num(tok):
    tok = tok.lower()
    return float(NUMWORDS[tok]) if tok in NUMWORDS else float(tok)


def fiction(r, visible):
    out = []
    text = " ".join([r.get("label") or "", r.get("description") or ""])
    if visible is None:
        return out
    small_cut, big_cut = (2.5, 6.0) if r["kind"] == "plant" and r.get("tree") else (0.6, 2.5)
    b, s = BIG_WORDS.search(text), SMALL_WORDS.search(text)
    if b and not s and visible < small_cut:
        out.append(("MEDIUM", "FICTION", "says '%s' but draws %.2f cells" % (b.group(0), visible)))
    if s and not b and visible > big_cut:
        out.append(("MEDIUM", "FICTION", "says '%s' but draws %.2f cells" % (s.group(0), visible)))
    for m in METRES.finditer(r.get("description") or ""):
        if m.group(2).lower() == "m" and not m.group(3):
            continue      # a bare "m" with no dimension word is too ambiguous
        try:
            metres = _num(m.group(1))
        except ValueError:
            continue
        want = metres / M_PER_CELL
        if want > 0 and (visible < want / 3 or visible > want * 3):
            out.append(("MEDIUM", "FICTION", "'%s' wants ~%.1f cells, draws %.2f" % (
                m.group(0).strip(), want, visible)))
        break
    return out


def judge(rows, fit, env, tiers, vtex=None):
    vanilla_tex = {r.get("texPath") for r in rows if not r["ours"] and r.get("texPath")}
    vanilla_tex |= set(vtex or ())
    for r in rows:
        if not r["ours"]:
            continue
        fl = []
        cells = r.get("cells")
        if cells is not None and cells <= 0:
            fl.append(("HIGH", "BAD_SIZE", "nonpositive drawn size %r" % cells))
            cells = None
            r["badSize"] = True
        fill = r.get("fill")
        f1 = max(fill) if fill else None
        visible = round(cells * (fill[1] if r["kind"] == "plant" else f1), 3) \
            if (cells and fill) else cells
        r["visible"] = visible
        tier = tiers.get(r["defName"]) if r["kind"] == "plant" else None
        r["tier"] = tier
        if tier:
            lo, hi = TIERS[tier]
            if not (lo * 0.95 <= cells <= hi * 1.05):
                fl.append(("HIGH", "TREE_TIER", "owner tier '%s' (%g-%s cells) but mature %.2f" % (
                    tier, lo, "%g" % hi if hi < 1e8 else "+", cells)))
        # newest numeric order, and newest bin rescale
        num = sorted([o for o in r.get("orders", []) if "cells" in o], key=lambda o: o["at"])
        if num and cells:
            o = num[-1]
            ratio = cells / o["cells"] if o["cells"] else None
            older = tier is not None and o["at"][:10] < "2026-10-18"
            off = ratio and (ratio > ORDER_TOL or ratio < 1 / ORDER_TOL)
            if off and not older:
                fl.append(("HIGH", "OWNER_ORDER", "owner '%s' (%s, %s on %s) but %.2f cells now" % (
                    o["note"][:60], o["at"][:10], o["key"], os.path.basename(o["file"]), cells)))
            elif off:
                fl.append(("INFO", "ORDER_SUPERSEDED", "owner '%s' (%s) superseded by tier '%s'" % (
                    o["note"][:40], o["at"][:10], tier)))
            else:
                fl.append(("INFO", "ORDER_MATCHED", "owner '%s' (%s) vs %.2f cells" % (
                    o["note"][:40], o["at"][:10], cells)))
        bins = sorted([o for o in r.get("orders", []) if "bin" in o], key=lambda o: o["at"])
        if bins and cells and not tier and not num:
            lo, hi = BINS[bins[-1]["bin"]]
            if not (lo * 0.9 <= cells <= hi * 1.1):
                fl.append(("MEDIUM", "BIN_RESCALE", "owner moved bin %s->%s (%g-%s) but %.2f cells" % (
                    bins[-1]["from"], bins[-1]["bin"], lo, "%g" % hi if hi < 1e8 else "+", cells)))
        if r["kind"] == "animal":
            if cells is None and not r.get("badSize"):
                fl.append(("HIGH", "NO_SPRITE", "no PawnKindDef lifeStage bodyGraphicData drawSize"))
            elif cells and fit and (r["body"] or 0) > 0:
                pred = math.exp(fit["a"] + fit["b"] * math.log(r["body"]))
                res = math.log(cells) - math.log(pred)
                r["fitCells"] = round(pred, 3)
                r["residual"] = round(res, 3)
                if abs(res) > 1.25 * fit["maxres"] and not num:
                    fl.append(("REVIEW", "ANIMAL_ENVELOPE",
                               "body %.2f draws %.2f cells; vanilla body %.2f draws ~%.2f (x%.2f, "
                               "vanilla never past x%.2f)" % (r["body"], cells, r["body"], pred,
                                                              math.exp(res), math.exp(fit["maxres"]))))
                elif abs(res) > 2 * fit["sd"] and not num:
                    fl.append(("MEDIUM", "ANIMAL_ENVELOPE", "body %.2f draws %.2f cells (vanilla ~%.2f)" % (
                        r["body"], cells, pred)))
        else:
            e = env.get("tree" if r["tree"] else "plant")
            if e and not tier and not num and cells:
                if cells < e["min"] * 0.8 or cells > e["max"] * 1.5:
                    fl.append(("MEDIUM", "PLANT_ENVELOPE", "%s draws %.2f cells; vanilla %ss %g-%g" % (
                        "tree" if r["tree"] else "plant", cells, "tree" if r["tree"] else "plant",
                        e["min"], e["max"])))
        if not r.get("texPath") and not any(c == "NO_SPRITE" for _, c, _ in fl):
            fl.append(("HIGH", "NO_SPRITE", "no texPath"))
        if r.get("texPath"):
            w = r.get("texWhere")
            if w is None and r["texPath"] in vanilla_tex:
                fl.append(("MEDIUM", "VANILLA_TEXTURE", "draws vanilla art %s" % r["texPath"]))
            elif w is None:
                fl.append(("HIGH", "NO_SPRITE", "texPath %s resolves to no loose texture" % r["texPath"]))
            elif w.startswith("donor:"):
                fl.append(("MEDIUM", "DONOR_TEXTURE", "texture only in %s" % w[6:]))
        if fill and fill[0] < 0.55 and fill[1] < 0.55:
            fl.append(("MEDIUM", "SPRITE_PADDED", "subject fills %.0f%% x %.0f%% of its canvas" % (
                fill[0] * 100, fill[1] * 100)))
        fl += fiction(r, visible)
        r["flags"] = fl


def apply_waivers(rows, waivers):
    for r in rows:
        w = waivers.get(r["defName"], {})
        for i, (sev, code, msg) in enumerate(r.get("flags", [])):
            if sev == "HIGH" and isinstance(w.get(code), str) and w[code].strip():
                r["flags"][i] = ("WAIVED", code, msg + " -- waived: " + w[code])


def audit(modlist=PDL.FULL_MODLIST):
    mods, missing, version, active, names = PDL.load_set(modlist)
    root, nfiles = build_doc(mods, active)
    pt = PDL.Patcher(root, active, names)
    npatch = 0
    for m in mods:
        for p in PDL._rel_files(m, "Patches"):
            npatch += 1
            pt.run_file(p)
    rows = extract(root, mods, active)
    vtex = sorted(VANILLA_TEX)
    stats = {"vanillaTex": vtex,
             # an op the runner skips whose text mentions drawSize/visualSizeRange (PDL's watch):
             # gating when it has an xpath not confined to BiomeDefs, or is in one of OUR mods. A
             # foreign mod's custom op class with no xpath (e.g. a robots toggle) only touches
             # its own defs as far as anyone can read; listed as unsupportedWatchedOps, not gated.
             "unsupportedSizeOps": [list(x) for x in pt.unsupported_watched
                                    if (x[2] and not re.search(r"BiomeDef", x[2]))
                                    or os.path.abspath(x[0]).startswith(REPO + os.sep)],
             "unsupportedWatchedOps": [list(x) for x in pt.unsupported_watched],
             "version": version, "mods": len(mods), "missing": missing, "defFiles": nfiles,
             "patchFiles": npatch, "patchOps": pt.ops, "xpathErrors": pt.xpath_errors,
             "unsupportedWatched": len(pt.unsupported_watched)}
    return rows, stats


def finish(rows, stats, tiers=None, orders=None, waivers=None):
    fit, env = animal_fit(rows), plant_env(rows)
    tiers = tree_tiers() if tiers is None else tiers
    if orders is None:
        orders = owner_orders()
        for k, v in table_orders().items():
            orders.setdefault(k, []).extend(v)
    for r in rows:
        r.pop("orders", None)
    unmatched = match_orders(rows, orders)
    judge(rows, fit, env, tiers, stats.get("vanillaTex"))
    if waivers is None:
        try:
            waivers = json.load(open(WAIVERS))
        except (OSError, ValueError):
            waivers = {}
    apply_waivers(rows, {k: v for k, v in waivers.items() if not k.startswith("_")})
    ours = [r for r in rows if r["ours"]]
    stats.update(
        fit=fit, plantEnvelope=env, tiers=len(tiers), orderKeys=len(orders),
        ordersUnmatched=sorted(unmatched),
        tiersMissingDef=sorted(set(tiers) - {r["defName"] for r in ours}),
        counts={"our_plants": sum(r["kind"] == "plant" for r in ours),
                "our_animals": sum(r["kind"] == "animal" for r in ours),
                "ref_plants": sum(r["kind"] == "plant" and not r["ours"] for r in rows),
                "ref_animals": sum(r["kind"] == "animal" and not r["ours"] for r in rows)})
    sev = {}
    for r in ours:
        for f in r["flags"]:
            sev.setdefault(f[0], {}).setdefault(f[1], 0)
            sev[f[0]][f[1]] += 1
    stats["flags"] = sev
    return rows, stats


# ── output ──────────────────────────────────────────────────────────────────────────────

def _cell(x):
    return str(x).replace("|", "/").replace("\n", " ")


def md_report(rows, st):
    ours = sorted((r for r in rows if r["ours"]), key=lambda r: (r["kind"], r["defName"]))
    c = st["counts"]
    fit = st.get("fit") or {}
    out = ["# Art size audit -- every plant and animal we define\n",
           "Item `ART_SIZES_AUDIT_AFTER_DONORS_LEAVE`. Generated by "
           "`src/RimMandrake/Utils/art_size_audit.py` (rules in its docstring) over the owner's full "
           "load set, mandrake.* read from the repo, %d patch operations applied. Every number "
           "below is MEASURED by that run; rerun it rather than editing this file.\n" % st["patchOps"],
           "- subjects: **%d plants, %d animals** of ours; reference: %d vanilla plants, %d vanilla "
           "animals" % (c["our_plants"], c["our_animals"], c["ref_plants"], c["ref_animals"]),
           "- vanilla animal fit: adult cells = %.3f x body^%.3f (n=%s, log sd %.3f, largest "
           "residual x%.2f)" % (math.exp(fit.get("a", 0)), fit.get("b", 0), fit.get("n"),
                                fit.get("sd", 0), math.exp(fit.get("maxres", 0))),
           "- vanilla plant envelope (mature cells): %s" % "; ".join(
               "%s %g-%g (median %g, n=%d)" % (k, v["min"], v["max"], v["median"], v["n"])
               for k, v in st["plantEnvelope"].items()),
           "- owner tree tiers read: %d; owner size orders read: %d keys, %d with no def of ours "
           "(the donor plant or animal was never ported, or was renamed past the stem match)" % (
               st["tiers"], st["orderKeys"], len(st["ordersUnmatched"])),
           "- flags: %s\n" % "; ".join("%s %s" % (s, ", ".join("%s %d" % kv for kv in sorted(v.items())))
                                       for s, v in sorted(st["flags"].items()))]
    for sev in ("HIGH", "WAIVED", "REVIEW", "MEDIUM", "INFO"):
        hit = [(r, f) for r in ours for f in r["flags"] if f[0] == sev]
        out.append("\n## %s (%d)\n" % (sev, len(hit)))
        if not hit:
            out.append("none\n")
            continue
        out.append("| defName | kind | code | finding | cells | fill | package |")
        out.append("|---|---|---|---|---|---|---|")
        for r, f in sorted(hit, key=lambda x: (x[1][1], x[0]["defName"])):
            fill = r.get("fill")
            out.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
                r["defName"], r["kind"], f[1], _cell(f[2]), r.get("cells"),
                "%.2fx%.2f" % tuple(fill) if fill else "-", r["package"]))
    out.append("\n## Owner orders with no def of ours (%d)\n" % len(st["ordersUnmatched"]))
    out.append(", ".join("`%s`" % k for k in st["ordersUnmatched"]) or "none")
    out.append("")
    return "\n".join(out) + "\n"


def check(rows, st):
    bad = []
    for k, floor in SANITY.items():
        if st["counts"][k] < floor:
            bad.append("instrument blind? %s=%d < %d" % (k, st["counts"][k], floor))
    if not st.get("fit"):
        bad.append("no vanilla animal fit")
    if st.get("missing"):
        bad.append("incomplete load set: %d mod(s) missing: %s" % (len(st["missing"]), st["missing"][:5]))
    if st.get("xpathErrors"):
        bad.append("patch run blind in places: %d xpath error(s)" % st["xpathErrors"])
    for x in st.get("unsupportedSizeOps") or []:
        bad.append("a size patch this runner cannot apply: %s %s %s" % tuple(x))
    for r in rows:
        if r["ours"]:
            for f in r["flags"]:
                if f[0] == "HIGH":
                    bad.append("%s %s: %s" % (r["defName"], f[1], f[2]))
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--modlist", default=PDL.FULL_MODLIST)
    ap.add_argument("--json", help="write rows+stats (the raw scan) here")
    ap.add_argument("--from-json", help="re-judge a saved scan instead of rebuilding it")
    ap.add_argument("--md", help="write the markdown report here")
    ap.add_argument("--check", action="store_true", help="exit 1 on any unwaived HIGH or a blind scan")
    a = ap.parse_args(argv)
    if a.from_json:
        j = json.load(open(a.from_json))
        rows, st = j["rows"], j["stats"]
    else:
        rows, st = audit(a.modlist)
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"rows": rows, "stats": st}, f, indent=1, default=str)
    rows, st = finish(rows, st)
    if a.md:
        with open(a.md, "w") as f:
            f.write(md_report(rows, st))
    print("counts=%s flags=%s" % (json.dumps(st["counts"]), json.dumps(st["flags"])))
    bad = check(rows, st)
    for b in bad:
        print("HIGH " + b)
    if a.check:
        print("CHECK %s (%d)" % ("FAIL" if bad else "PASS", len(bad)))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
