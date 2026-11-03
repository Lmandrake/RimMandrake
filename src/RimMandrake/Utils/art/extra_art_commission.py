#!/usr/bin/env python3
"""extra_art_commission.py — commission the extra herd look and the young look of each biome's creatures, one biome at a
time (item EXTRA_ART_PER_BIOME_COMMISSION_1).

Owner, 2026-10-08 (typed): gender art = "I'm happy with every herd animal"; "After that we should commission this answer
for each biome once it's done. Same for juveniles." Owner by question card 2026-10-08 18:44: "to break up a herd of
identical-looking animals, a COLOUR VARIANT comes first (not a female look)." Guidelines: the 2026-10-08 draft
(`Transient/extra_art_guidelines_2026-10-08.md`, git d92775a94; the Transient copy expired), §1 Gender / Juvenile rows.

Inputs: `design/RimMandrake/biome_group_sizes/biome_group_sizes.csv` (who is in which biome, and the walked group size)
and the race/kind XML under src/ (sex, existing female / variant / young art, pack, tameness, young-stage length) plus the
canon library text for dimorphism and young-differ evidence.

Rules (each row of commission.csv names the rule that produced it):
  HERD   a creature that is a herd in this biome: herdAnimal true, or canon ruling `herd`, its walked max group above 1,
         and not canon `solitary`. It earns ONE extra adult look unless it already has a female look or an
         alternateGraphics variant:
           female   when canon (or its own description) says the sexes look different and the race has sexes; a pack
                    beast also gets a female pack set, because the engine builds the pack path from the female body
           variant  otherwise: a second colour morph (the card above), drawn at the same pose and silhouette
  YOUNG  a young look unless the kind already draws a distinct young texture or the young are a separate race:
           canon    canon (or the description) says the young look different
           kept     a pack beast or an easily-tamed / penned animal (farm tag, roamMtbDays, or wildness <= 0.3), body size
                    >= 0.4, young for >= 15 days ("domesticated beasts", the 2026-10-08 ask)
A creature on several biomes is commissioned once, in the first biome (commission order) that owes it.

Commission order: smallest biome first (fewest owed jobs, then name), so the pipeline is proven on a cheap biome and each
biome's art lands quickly. Every biome's walk is settled (BIOME_GROUP_SIZE_WALK_1 done 2026-11-03), so every biome may be
filed; job priority is 50 + the biome's order, so the daemon still draws the art one biome at a time. delegated: design.

New texture slots (no def draws them until the art lands; the regen_eligibility gate reads commission.csv so they count
as drawn by their def and must still be confirmed NONE):
  female <adult texPath>Female   female pack <adult texPath>FemalePack   variant <adult texPath>Variant
  young  <adult texPath>Young
Wiring each slot into its def once all three facings exist is the follow-on item EXTRA_ART_WIRE_LANDED_LOOKS.

    python3 src/RimMandrake/Utils/art/extra_art_commission.py plan            # rewrite commission.csv from the defs
    python3 src/RimMandrake/Utils/art/extra_art_commission.py check           # plan == commission.csv; filed biomes queued
    python3 src/RimMandrake/Utils/art/extra_art_commission.py submit --next [--dry-run]   # file the next biome's jobs
    python3 src/RimMandrake/Utils/art/extra_art_commission.py submit --biome RM_X [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "src"
CANON = REPO / "design/RimStarWars/canon_references"
GROUPS = REPO / "design/RimMandrake/biome_group_sizes/biome_group_sizes.csv"
OUTDIR = REPO / "design/RimMandrake/extra_art_commission"
TABLE = OUTDIR / "commission.csv"
STATE = OUTDIR / "commission_state.json"
ITEM = "EXTRA_ART_PER_BIOME_COMMISSION_1"
SKIP = {"Utils", "bridgetools", "mapsynth", "rimflow", "RimDefDump"}
FACINGS = ["east", "south", "north"]
COLUMNS = ["biome", "order", "race", "kind", "label", "rule", "look", "slot", "tex_path", "install_mod", "reference",
           "canvas", "facings", "jobs", "evidence", "job_id"]
SUFFIX = {"female": "Female", "female_pack": "FemalePack", "variant": "Variant", "young": "Young"}
YOUNG_MIN_DAYS = 15
YOUNG_MIN_SIZE = 0.4

TRAIT = (r"(larger|smaller|bigger|heavier|horns?|crests?|manes?|tusks?|colou?r\w*|bright\w*|plum\w*|antlers?|frills?"
         r"|sails?|lack\w*|dull\w*|drab|wattles?|spurs?|display)")
DIMORPH = re.compile(r"(sexual(?:ly)? dimorph\w*|\bdimorph\w*|\b(?:fe)?males?\b[^.]{0,80}\b" + TRAIT + r"\b|\b"
                     + TRAIT + r"\b[^.]{0,40}\b(?:than|in) (?:the )?(?:fe)?males?\b|\b(?:bulls?|cows?|stags?|hens?"
                     r"|roosters?|drakes?)\b[^.]{0,40}\b" + TRAIT + r"\b|\bonly (?:the )?(?:fe)?males?\b)", re.I)
YN = (r"(calf|calves|cubs?|pups?|foals?|chicks?|hatchlings?|young|babies|baby|juveniles?|younglings?|whelps?|kits?"
      r"|fledglings?|nymphs?)")
YT = (r"(lack\w*|without|differ\w*|unlike|until|pale\w*|pink|spotted|striped|stripes|mottled|colou?r\w*|downy|down\b"
      r"|fluff\w*|hornless|no horns|translucent|soft-shelled|bright\w*)")
YOUNG = re.compile(r"\b" + YN + r"\b[^.]{0,80}\b" + YT + r"\b|\b" + YT + r"\b[^.]{0,40}\b(?:the |its )?" + YN + r"\b",
                   re.I)
# The regexes only FIND candidates; every hit is read by hand and lands in ACCEPT or REJECT. A hit on neither list is
# UNREAD and makes `check` fail until someone reads it (2026-10-08 guidelines §2, 2026-11-03 for this commission).
# ACCEPT values are the hand-written difference the prompt states (canon wording, read 2026-11-03); "" = already drawn
DIMORPH_ACCEPT = {"RSW_Kybuck": "canon: males carry short horns on top of the head, so the female is hornless",
                  "RSW_IridonianReek": "canon: male horns are larger than female horns, so the female's horns are "
                                       "visibly smaller and shorter",
                  "RSW_Bantha": "", "RSW_Nerf": "", "RSW_Porg": "", "RSW_Scurrier": ""}
DIMORPH_REJECT = {"RSW_Varactyl": "both sexes carry crests", "RSW_Urusai": "canon: dimorphism not stated",
                  "RSW_Runyip": "hit is the antler checklist line, no sex named",
                  "RSW_Corinathoth": "hit is a negative-prompt line about a donor cow, no sex named"}
YOUNG_ACCEPT = {"RSW_Mott": "canon: the young are a uniform brown-tan, without the adults' stripes",
                "RSW_Uvak": "canon: juveniles are small, thin, long-tailed and big-eyed, with big wings for the body",
                "RSW_Woolamander": "canon: the young are small, round and striped",
                "RSW_Clodhopper": "canon: juveniles are smaller, more uniformly brown-olive, and lack the adults' vivid "
                                  "red head colouring",
                "RSW_Neebray": "canon: babies are born with solid skin colours; the wing spots come only with age",
                "RSW_ColoClawFish": "", "RSW_Dianoga": "", "RSW_Hawkbat": ""}
YOUNG_REJECT = {"RSW_Falumpaset": "calf is a smaller version of the same shape", "RSW_TeeMuss": "calf hide, not looks",
                "RSW_Urusai": "chicks duel: behaviour", "RSW_Grank": "identical colouring stated",
                "RSW_Diggerpede": "bears young alive", "RM_Gristle": "bears young alive",
                "RSW_Zakkeg": "about a render, not the young", "RSW_Borcatu": "size only",
                "RSW_Blarth": "same colouring stated", "RSW_OpeeSeaKiller": "mouth-brooding, not looks"}


def num(s, d=None):
    try:
        return float(s)
    except (TypeError, ValueError):
        return d


def _snip(rx, text, w=60):
    m = rx.search(text or "")
    return "" if not m else re.sub(r"\s+", " ", text[max(0, m.start() - w):m.end() + w]).strip()


class Defs:
    """Our race ThingDefs and animal PawnKindDefs, ParentName resolved inside our XML only."""

    def __init__(self, src: Path = SRC):
        self.named, self.things, self.kinds = {}, {}, {}
        for p in sorted(src.rglob("*.xml")):
            parts = set(p.relative_to(src).parts)
            if SKIP & parts or not ({"Defs"} & parts):
                continue
            try:
                r = ET.parse(p).getroot()
            except (ET.ParseError, OSError):
                continue
            if r.tag != "Defs":
                continue
            mod = "/".join(p.relative_to(src).parts[:2])
            for e in r:
                if not isinstance(e.tag, str):
                    continue
                if e.get("Name"):
                    self.named[(e.tag, e.get("Name"))] = e
                dn = (e.findtext("defName") or "").strip()
                if not dn or e.get("Abstract") == "True":
                    continue
                if e.tag == "ThingDef":
                    self.things[dn] = (mod, e)
                elif e.tag == "PawnKindDef":
                    self.kinds[dn] = (mod, e)
        self.tex = {}                                   # lowercased 'rel' (no .png) -> Path, every src Textures dir
        for troot in src.glob("*/*/Textures"):
            for q in troot.rglob("*.png"):
                self.tex.setdefault(q.relative_to(troot).as_posix()[:-4].lower(), q)
        self.canon = {}
        if CANON.is_dir():
            for d in CANON.iterdir():
                if d.is_dir() and not d.name.startswith(("_", ".")):
                    self.canon[d.name] = " ".join(f.read_text(errors="ignore") for f in sorted(d.glob("*.md")))

    def find(self, e, tag, path):
        for _ in range(12):
            if e is None:
                return None
            x = e.find(path)
            if x is not None:
                return x
            pn = e.get("ParentName")
            e = self.named.get((tag, pn)) if pn else None
        return None

    def ft(self, e, tag, path, d=""):
        x = self.find(e, tag, path)
        return (x.text or "").strip() if x is not None and x.text else d

    def png(self, tex: str, facing: str = "east"):
        return self.tex.get(f"{tex}_{facing}".lower()) or self.tex.get(tex.lower())

    def creature(self, kind: str) -> dict | None:
        if kind not in self.kinds:
            return None
        kmod, k = self.kinds[kind]
        race = self.ft(k, "PawnKindDef", "race")
        if race not in self.things:
            return None
        rmod, rd = self.things[race]
        ls = self.find(k, "PawnKindDef", "lifeStages")
        lis = ls.findall("li") if ls is not None else []
        body = [(li.findtext("bodyGraphicData/texPath") or "").strip() for li in lis]
        adult = next((t for t in reversed(body) if t), "")
        label = self.ft(rd, "ThingDef", "label") or race
        desc = self.ft(rd, "ThingDef", "description")
        norm = lambda s: re.sub(r"[^a-z]", "", s.lower())                       # noqa: E731
        slugs = {norm(n): n for n in self.canon}
        slug = next((slugs[s] for s in (norm(re.sub(r"^(RM|RSW|RUT)_", "", race)), norm(label)) if s in slugs), "")
        ctext = self.canon.get(slug, "")
        tt = self.find(rd, "ThingDef", "tradeTags")
        tags = [li.text.strip() for li in (tt if tt is not None else []) if li.text]
        sb = self.find(rd, "ThingDef", "statBases")
        wild = num(sb.findtext("Wildness") if sb is not None else None, num(self.ft(rd, "ThingDef", "race/wildness"), None))
        roam = num(self.ft(rd, "ThingDef", "race/roamMtbDays"), None)
        lsa = self.find(rd, "ThingDef", "race/lifeStageAges")
        stages = [((li.findtext("def") or "").strip(), num(li.findtext("minAge"), 0)) for li in (lsa if lsa is not None else [])]
        adult_age = next((a for d, a in stages if "Adult" in d), None)
        dim_hit = _snip(DIMORPH, ctext) or _snip(DIMORPH, desc)
        yng_hit = _snip(YOUNG, ctext) or _snip(YOUNG, desc)
        unread = [w for w, hit, acc, rej in (("dimorphism", dim_hit, DIMORPH_ACCEPT, DIMORPH_REJECT),
                                             ("young-differ", yng_hit, YOUNG_ACCEPT, YOUNG_REJECT))
                  if hit and race not in acc and race not in rej]
        dim = (DIMORPH_ACCEPT[race] or dim_hit) if dim_hit and race in DIMORPH_ACCEPT else ""
        yng = (YOUNG_ACCEPT[race] or yng_hit) if yng_hit and race in YOUNG_ACCEPT else ""
        pack = self.ft(rd, "ThingDef", "race/packAnimal").lower() == "true"
        return dict(
            race=race, kind=kind, label=label, desc=desc, kmod=kmod, rmod=rmod, adult_tex=adult, canon=slug,
            genders=self.ft(rd, "ThingDef", "race/hasGenders", "true").lower() != "false",
            herd=self.ft(rd, "ThingDef", "race/herdAnimal").lower() == "true",
            pack=pack, size=num(self.ft(rd, "ThingDef", "race/baseBodySize"), 1.0),
            young_days=round(adult_age * 60, 1) if adult_age is not None else None,
            domestic=("AnimalFarm" in tags) or (roam is not None) or (wild is not None and wild <= 0.3),
            has_female=any(li.find("femaleGraphicData") is not None for li in lis),
            has_variant=self.find(k, "PawnKindDef", "alternateGraphics") is not None,
            distinct_young=len({t for t in body if t}) > 1,
            separate_young_race=bool(re.search(r"(Larva|Larvae|Spawn|Hatchling|Grub|Juv|Juvenile)$", race)),
            dimorph=dim, young=yng, unread=unread)


def gmax(s: str) -> int:
    try:
        return int(float(str(s).strip().split("~")[-1]))
    except ValueError:
        return 1


def png_size(p: Path) -> int:
    """Square canvas of an existing sprite (largest side), 256 when unreadable."""
    try:
        with open(p, "rb") as f:
            h = f.read(24)
        w, ht = struct.unpack(">II", h[16:24])
        return max(w, ht) if h[:8] == b"\x89PNG\r\n\x1a\n" else 256
    except (OSError, struct.error):
        return 256


def owed(c: dict, g: dict) -> list[tuple[str, str, str, str]]:
    """-> [(rule, look, slot, evidence)] this creature owes in this biome's walk row G."""
    out = []
    canon = (g.get("canon_ruling") or "").strip()
    herd = (c["herd"] or canon == "herd") and canon != "solitary" and gmax(g.get("set_wildGroupSize")) > 1
    if herd and not (c["has_female"] or c["has_variant"]):
        why = f"herd: group {g.get('set_wildGroupSize')}, herdAnimal {c['herd']}, canon {canon or '-'}"
        if c["dimorph"] and c["genders"]:
            out.append(("HERD", "female", "female", f"{why}; sexes differ: {c['dimorph'][:140]}"))
            if c["pack"]:
                out.append(("HERD", "female", "female_pack", "pack beast: the engine draws the pack on the female body"))
        else:
            out.append(("HERD", "variant", "variant", f"{why}; no canon sex difference: colour variant (card 2026-10-08)"))
    if not (c["distinct_young"] or c["separate_young_race"]):
        yd = c["young_days"] or 0
        if c["young"]:
            out.append(("YOUNG", "young", "young", f"canon young differ: {c['young'][:140]}"))
        elif (c["pack"] or c["domestic"]) and yd >= YOUNG_MIN_DAYS and c["size"] >= YOUNG_MIN_SIZE:
            out.append(("YOUNG", "young", "young", f"kept ({'pack' if c['pack'] else 'tamed/penned'}), young {yd:g} days, "
                                                   f"size {c['size']:g}"))
    return out


def plan(defs: Defs | None = None, groups: Path = GROUPS) -> list[dict]:
    defs = defs or Defs()
    walk = list(csv.DictReader(open(groups, newline="")))
    per_biome = defaultdict(list)
    for g in walk:
        c = defs.creature(g["kind"])
        if c is None or not c["adult_tex"]:
            continue
        for rule, look, slot, ev in owed(c, g):
            per_biome[g["biome"]].append((c, rule, look, slot, ev))
    # commission order: fewest owed jobs first, then name; a race is commissioned in the first biome that owes it
    order = sorted(per_biome, key=lambda b: (len({(c["race"], s) for c, _, _, s, _ in per_biome[b]}), b))
    seen, rows = set(), []
    for i, b in enumerate(order, 1):
        for c, rule, look, slot, ev in sorted(per_biome[b], key=lambda x: (x[0]["race"], x[3])):
            if (c["race"], slot) in seen:
                continue
            seen.add((c["race"], slot))
            tex = c["adult_tex"] + SUFFIX[slot]
            ref_tex = c["adult_tex"] + ("Pack" if slot == "female_pack" else "")
            ref = defs.png(ref_tex)
            mod = _mod_of(ref) if ref else c["rmod"]
            # a Graphic_Single body (one bare PNG, no _east) gets one bare look, not a facing set
            fac = [] if ref and not ref.stem.lower().endswith("_east") else FACINGS
            rows.append(dict(biome=b, order=i, race=c["race"], kind=c["kind"], label=c["label"], rule=rule, look=look,
                             slot=slot, tex_path=tex, install_mod=mod,
                             reference=ref.relative_to(REPO).as_posix() if ref else "",
                             canvas=png_size(ref) if ref else 256, facings=";".join(fac), jobs=max(1, len(fac)),
                             evidence=ev,
                             job_id=f"xart_{c['race']}_{slot}_v1"))
    return rows


def _mod_of(p: Path) -> str:
    rel = p.relative_to(SRC).parts
    return "/".join(rel[:2])


def write_table(rows: list[dict], path: Path = TABLE):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})


def read_table(path: Path = TABLE) -> list[dict]:
    return list(csv.DictReader(open(path, newline=""))) if path.is_file() else []


def read_state(path: Path = STATE) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {"item": ITEM, "biomes": {}}


def _prompt(r: dict, c: dict) -> str:
    who = f"the {c['label']}"
    body = (c["desc"] or "").strip().replace("\n", " ")[:600]
    if r["slot"] == "variant":
        return (f"RimWorld creature sprite of {who}, a second natural colour morph of the same species. Keep the reference "
                f"image's exact body, pose, proportions, silhouette and anatomy; repaint only the hide, coat or shell: a "
                f"clearly different but plausible base tone and marking pattern, so two of them standing in one herd read "
                f"as two individuals. Creature notes: {body}")
    if r["slot"] in ("female", "female_pack"):
        pack = (" carrying the same packs, saddle bags and straps as the reference image, in the same places"
                if r["slot"] == "female_pack" else "")
        return (f"RimWorld creature sprite of {who}: the FEMALE of the species{pack}. Same species, colours and pose as "
                f"the reference image; the visible sex difference follows the species lore ({c['dimorph']}). "
                f"Creature notes: {body}")
    lore = (f" The young look different from the adults: {c['young']}." if c["young"] else
            " A young animal's proportions: a larger head for its body, shorter legs, softer rounder features, and any "
            "horns, tusks, spines or crests small or just budding.")
    return (f"RimWorld creature sprite of a YOUNG {c['label']}, a juvenile of the species, in the same colours and painting "
            f"style as the adult.{lore} Creature notes: {body}")


def fill_rows(rows: list[dict], defs: Defs) -> list[dict]:
    out = []
    for r in rows:
        c = defs.creature(r["kind"])
        mod = r["install_mod"]
        fac = [f for f in r["facings"].split(";") if f]
        row = {"id": r["job_id"][:-len("_v1")] + "_v1", "rimflow_item_id": ITEM, "prompt": _prompt(r, c),
               "canvas_w": int(r["canvas"]), "canvas_h": int(r["canvas"]), "facings": fac,
               "priority": 50 + int(r["order"]),        # the daemon draws them biome by biome, in commission order
               "target_def": r["race"], "target_texpath": r["tex_path"],
               "install_to": f"src/{mod}/Textures/{r['tex_path']}" + ("_{facing}" if fac else "") + ".png",
               "style_notes": f"{ITEM}: {r['look']} look for the {r['biome']} commission ({r['rule']}: {r['evidence'][:160]})"}
        if c["canon"]:
            row["canon"] = c["canon"]
        row["biome_register"] = _register(r["biome"])
        if not (r["reference"] and r["slot"] in ("variant", "female_pack")):
            out.append(row)                       # new shape: east master, north/south derived from it (fill_queue)
            continue
        # same pose as the existing sprite: each facing is a reskin of THAT facing's file (fill_queue takes one
        # reference per row, so one row per facing)
        ref_tex = c["adult_tex"] + ("Pack" if r["slot"] == "female_pack" else "")
        for f in fac or [""]:
            ref = defs.png(ref_tex, f) if f else (REPO / r["reference"])
            one = dict(row, facings=[f] if f else [])
            if ref:
                one["reference"] = str(ref)
            out.append(one)
    return out


def job_ids(rows: list[dict]) -> list[str]:
    """The artpipe job ids a set of commission rows files: <job_id>_<facing>, or the bare id for a single look."""
    out = []
    for r in rows:
        fac = [f for f in str(r["facings"]).split(";") if f]
        out += [f"{r['job_id']}_{f}" for f in fac] if fac else [r["job_id"]]
    return sorted(out)


def unread_hits(defs: Defs | None = None, groups: Path = GROUPS) -> list[str]:
    """Walked creatures whose canon/description regex hit nobody has read by hand yet."""
    defs = defs or Defs()
    out = set()
    for g in csv.DictReader(open(groups, newline="")):
        c = defs.creature(g["kind"])
        if c and c["unread"]:
            out.add(f"{c['race']}: unread {', '.join(c['unread'])} hit")
    return sorted(out)


def _register(biome: str) -> str:
    """The biome's light/palette register for the prompt (placeholder_jobs.REGISTER, its default otherwise)."""
    sys.path.insert(0, str(HERE))
    import placeholder_jobs as PJ                                       # noqa: E402
    return PJ.REGISTER.get(biome, PJ.DEFAULT_REG)


def queued_ids(art_root: Path | None = None) -> set[str]:
    root = art_root or _art_root()
    ids = set()
    reg = root / "registry.jsonl"
    if reg.is_file():
        for line in open(reg, errors="replace"):
            if '"queued"' in line:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("event") == "queued" and e.get("job_id"):
                    ids.add(e["job_id"])
    for d in ("pending", "active", "done", "failed"):
        if (root / d).is_dir():
            ids.update(p.stem for p in (root / d).glob("*.json") if not p.name.endswith(".manifest.json"))
    return ids


def _art_root() -> Path:
    sys.path.insert(0, str(HERE.parent / "artpipe"))
    import state_dir                                                    # noqa: E402
    return Path(state_dir.STATE_ROOT)


def check(rows_now: list[dict], table: list[dict], state: dict, ids: set[str] | None) -> list[str]:
    errs = []
    norm = lambda rs: sorted(tuple(str(r.get(k, "")) for k in COLUMNS) for r in rs)       # noqa: E731
    if norm(rows_now) != norm(table):
        a = {(r["race"], r["slot"]) for r in rows_now}
        b = {(r["race"], r["slot"]) for r in table}
        errs.append(f"commission.csv is stale: {len(a - b)} owed rows missing, {len(b - a)} rows no longer owed, "
                    f"or a field changed; rerun plan (e.g. missing {sorted(a - b)[:3]}, extra {sorted(b - a)[:3]})")
    for r in table:
        if r["rule"] == "HERD" and r["slot"] not in ("female", "female_pack", "variant"):
            errs.append(f"{r['race']}: HERD row with slot {r['slot']}")
        if r["job_id"] != f"xart_{r['race']}_{r['slot']}_v1":
            errs.append(f"{r['race']}: job id {r['job_id']}")
    by_b = defaultdict(list)
    for r in table:
        by_b[r["biome"]].append(r)
    for b, rec in sorted(state.get("biomes", {}).items()):
        if b not in by_b:
            errs.append(f"state names commissioned biome {b}, which owes nothing in commission.csv")
            continue
        want = set(job_ids(by_b[b]))
        if set(rec.get("jobs", [])) != want:
            errs.append(f"{b}: state lists {len(rec.get('jobs', []))} jobs, the table owes {len(want)}")
        if ids is not None:
            miss = sorted(want - ids)
            if miss:
                errs.append(f"{b}: {len(miss)} of {len(want)} jobs not on the artpipe queue/registry (e.g. {miss[:3]})")
    return errs


def submit(biome: str, dry: bool) -> int:
    defs = Defs()
    table = read_table()
    rows = [r for r in table if r["biome"] == biome]
    if not rows:
        print(f"{biome}: owes nothing in {TABLE.relative_to(REPO)}", file=sys.stderr)
        return 2
    jobs = fill_rows(rows, defs)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f, indent=1)
        tmp = f.name
    cmd = [sys.executable, str(HERE.parent / "artpipe/fill_queue.py"), "--input", tmp] + (["--dry-run"] if dry else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(p.stdout[-4000:])
    sys.stderr.write(p.stderr[-4000:])
    os.unlink(tmp)
    if p.returncode != 0 or dry:
        return p.returncode
    st = read_state()
    st["biomes"][biome] = {"filed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           "jobs": job_ids(rows)}
    STATE.write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")
    print(f"{biome}: filed {len(jobs)} looks, {len(job_ids(rows))} jobs; state {STATE.relative_to(REPO)}")
    return 0


def next_biome() -> str | None:
    done = set(read_state().get("biomes", {}))
    for r in sorted(read_table(), key=lambda r: int(r["order"])):
        if r["biome"] not in done:
            return r["biome"]
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    c = sub.add_parser("check")
    c.add_argument("--no-queue", action="store_true", help="skip the artpipe queue/registry lookup")
    s = sub.add_parser("submit")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--biome")
    g.add_argument("--next", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        rows = plan()
        write_table(rows)
        nb = len({r["biome"] for r in rows})
        print(f"commission: {len(rows)} looks, {sum(int(r['jobs']) for r in rows)} jobs over {nb} biomes "
              f"(HERD female {sum(r['slot'] == 'female' for r in rows)}, female pack "
              f"{sum(r['slot'] == 'female_pack' for r in rows)}, variant {sum(r['slot'] == 'variant' for r in rows)}; "
              f"YOUNG {sum(r['slot'] == 'young' for r in rows)}) -> {TABLE.relative_to(REPO)}")
        return 0
    if a.cmd == "check":
        defs = Defs()
        errs = unread_hits(defs) + check(plan(defs), read_table(), read_state(), None if a.no_queue else queued_ids())
        for e in errs:
            print("FAIL", e)
        print("OK" if not errs else f"{len(errs)} failure(s)")
        return 1 if errs else 0
    b = a.biome or next_biome()
    if not b:
        print("every biome is commissioned")
        return 0
    return submit(b, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
