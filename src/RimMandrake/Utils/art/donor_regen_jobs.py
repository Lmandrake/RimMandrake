#!/usr/bin/env python3
"""donor_regen_jobs.py — artpipe regeneration jobs for every art-bearing def of ours that still WEARS borrowed art:
a donor copy, a StandIn/ stand-in, a geometric placeholder, a vanilla/donor texPath, or nothing. Then feeds them to
the artpipe pending queue in capped batches, so the Artist daemon (artpiped.py) drains them in the background.

Owner, 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!! Just get it done."
then "Yes. Simply accept all art as currently rendered to get this done. We will re review at a later time. No more
art blockers."  Stand-ins were installed so the donor mods could retire; every one still owes a render of ours
(no-donor-art ruling 2026-10-05; vanilla counts as donor). Item: DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO.

    # 1. measure (background, ~5 + ~3 min)
    python3 src/RimMandrake/Utils/art/biome_census.py --no-wookiee --out <dir>
    python3 src/RimMandrake/Utils/art/texture_regen_audit.py --census <dir>/census.json --out <audit.json>
    # 2. build the ordered job list (writes nothing to the queue)
    python3 src/RimMandrake/Utils/art/donor_regen_jobs.py build --audit <audit.json> --census <dir>/census.json \
        --out design/RimMandrake/donor_regen_jobs_2026-10-18.json
    # 3. feed: file the next rows until pending+active reaches --cap (default 40). Safe to re-run any time.
    #    Every row passes regen_eligibility.Gate first (owner 2026-10-19: only confirmed NONE / PLACEHOLDER / DONOR
    #    art is queued; owner-kept, regenerated or renamed destinations are refused and logged; gate error = no filing).
    python3 src/RimMandrake/Utils/art/donor_regen_jobs.py submit --jobs design/RimMandrake/donor_regen_jobs_2026-10-18.json
    # 4. later, install what finished (accept-for-now):  src/RimMandrake/Utils/art/art_accept_finished.py

Targets (a def is a target when the picture it draws today is not ours):
  roster rows of texture_regen_audit (DONOR, PLACEHOLDER, NO_LIVE_DONOR_ONLY, NO_LIVE_ART) whose defName is a def
  of ours; def-view rows of the biome/engine/kit mods (DONOR, PLACEHOLDER, EXTERNAL); SWBestiary/UtinniPatches twin
  rows only when a biome roster casts that def; every def whose XML draws a StandIn/ path.
Never targeted: REGEN, DERIVED, UNPROVEN (owner-sheet picks), src/RimMandrake/FlowWorks, donor defNames cast on a
roster with no def of ours (a port is owed first; listed under `gaps`).
Binding: a file that exists in src/ gets an exact `install_to` (a StandIn/<p> file -> <p>, so the stand-in stays as
past art); a vanilla/donor texPath gets target_def + target_texpath (bulk_accept_renders repoints it to a path of
our own). Dedupe: a target whose def already has a pending/active job, or a done job the installer can still place,
is skipped; job ids are `dregen_<def>[_<file>]_v1` so a re-run never re-files (fill_queue/registry dedupe too).
Order (lower priority claims sooner): creatures of the arid start region (the Utinni lands on RUT_ExtremeDesert,
tile 17007), other creatures, plants, terrain, buildings, items, icons.
Never runs image generation itself.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bulk_accept_renders as BA  # noqa: E402
import regen_eligibility as RE  # noqa: E402

REPO = BA.REPO
ART = BA.ART
CANON = REPO / "design/RimStarWars/canon_references"
ITEM = "DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO"
SW_ITEM = "TEXREGEN_SWBESTIARY_DECIDE_NO_ROSTER_OWNS_IT"
HOUSE = ("Painterly vanilla-RimWorld house style, matte, no outlines, never cute; one centred subject on a "
         "transparent background, no ground, no props, no baked shadow.")
# The arid region the colony starts in (canonical start tile 17007 is RUT_ExtremeDesert, region The Breaks) and the
# desert biomes of ours that share its register. A judgment for ORDERING only, never a tile count.
START = ["RUT_ExtremeDesert", "RM_Stillsand", "RM_LeaningScrub", "RM_LongShade", "RM_Wasteland", "RM_BlueDesert",
         "RM_FloodedCanyon", "RM_Pyrelands"]
KIND_PRIO = {"creature_start": 20, "creature": 30, "plant_start": 40, "plant": 45, "terrain": 55, "building": 65,
             "item": 75, "icon": 85}
BAD = {"DONOR", "PLACEHOLDER", "MISSING"}


def pow2(px: float, lo=128, hi=1024) -> int:
    n = lo
    while n < px and n < hi:
        n *= 2
    return n


def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\\n", " ")).strip()


def load_xml_defs():
    """defName -> (element, deftype, repo-rel file); race -> PawnKindDef element. Defs folders only, no FlowWorks."""
    defs, kinds = {}, {}
    for x in (REPO / "src").rglob("*.xml"):
        r = str(x.relative_to(REPO))
        if "/Defs/" not in r or BA.excluded(r):
            continue
        try:
            root = ET.parse(x).getroot()
        except (ET.ParseError, OSError):
            continue
        for d in root:
            if not isinstance(d.tag, str):
                continue
            dn = (d.findtext("defName") or "").strip()
            if not dn:
                continue
            defs.setdefault(dn, (d, d.tag, r))
            if d.tag == "PawnKindDef" and (d.findtext("race") or "").strip():
                kinds.setdefault(d.findtext("race").strip(), d)
    return defs, kinds


def kind_of(el, tag, kinds, dn):
    if tag == "TerrainDef":
        return "terrain"
    if tag == "PawnKindDef" or (el is not None and el.find("race") is not None) or dn in kinds:
        return "creature"
    if el is not None and el.find("plant") is not None:
        return "plant"
    if el is not None:
        cat = (el.findtext("category") or "").strip()
        tc = (el.findtext("thingClass") or "")
        if cat == "Building" or "Building" in tc or el.find("building") is not None:
            return "building"
        if el.find("graphicData") is None and el.find("uiIconPath") is not None:
            return "icon"
        if tag not in ("ThingDef",):
            return "icon"
    return "item"


def draw_size(*els) -> float:
    for e in els:
        if e is None:
            continue
        for ds in e.iter("drawSize"):
            m = re.findall(r"[\d.]+", ds.text or "")
            if m:
                return max(float(v) for v in m)
    return 1.0


def canon_slug(dn: str) -> str | None:
    if not dn.startswith("RSW_"):
        return None
    s = dn[4:].lower()
    p = CANON / s / "description.md"
    if p.is_file() and "## Must show" in p.read_text(errors="replace"):
        return s
    return None


# ───────────────────────────────────────────────────────────── the queue view ──

def queue_view():
    """target_def -> set of states ('pending','active','done-installable') and every id ever filed."""
    by_def = defaultdict(set)
    ids = set()
    for st in ("pending", "active", "done", "failed"):
        d = ART / st
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if not f.name.endswith(".json") or f.name.endswith(".manifest.json"):
                continue
            ids.add(f.stem)
            if st in ("pending", "active"):
                try:
                    j = json.loads(f.read_text())
                except (OSError, ValueError):
                    continue
                if j.get("target_def"):
                    by_def[j["target_def"]].add(st)
    return by_def, ids


def installable_defs(plan_path: Path | None) -> set:
    """Defs a finished render can already be installed on (a bulk_accept_renders plan's rows)."""
    if not plan_path or not plan_path.is_file():
        return set()
    P = json.loads(plan_path.read_text())
    return {r["dest"] for r in P.get("rows", [])}


# ──────────────────────────────────────────────────────────────── targets ──

def files_for(repo: BA.Repo, tp: str):
    """(mod, texrel-without-.png) files under src Textures that the texPath text `tp` draws: single, facings, or a
    Graphic_Random folder. StandIn/ copies are returned at their StandIn path."""
    out = []
    for k in (tp, tp + "_east", tp + "_south", tp + "_north", tp + "_west"):
        for m in repo.mods_with(k):
            out.append((m, k))
    if not out:
        for k, ms in repo.tex.items():
            if k.startswith(tp + "/") and "/" not in k[len(tp) + 1:] and not k.endswith("_m"):
                for m in ms:
                    out.append((m, k))
    return sorted(set(out))


def textures_of(repo, dn, el, ke):
    """Every texture text def `dn` (and its PawnKindDef) names: (tag, text, drawSize of the element holding it).
    Mask paths and duplicate texts are dropped."""
    out, seen = [], set()
    for node in [x for x in (el, ke) if x is not None]:
        for par in node.iter():
            for c in par:
                if isinstance(c.tag, str) and c.tag in BA.TEXTAGS and (c.text or "").strip() and not list(c):
                    t = c.text.strip()
                    if t in seen or t.endswith("_m") or "maskPath" in c.tag:
                        continue
                    seen.add(t)
                    ds = None
                    m = re.findall(r"[\d.]+", par.findtext("drawSize") or "")
                    if m:
                        ds = max(float(v) for v in m)
                    out.append((c.tag, t, ds, par.tag))
    return out


def dest(m, k):
    return f"{m}/Textures/{k.removeprefix('StandIn/')}.png"


def build(audit_p: Path, census_p: Path, plan_p: Path | None, out: Path, sw_only: bool = False,
          exclude_jobs: Path | None = None):
    audit = json.loads(audit_p.read_text())
    census = json.loads(census_p.read_text())
    repo = BA.Repo()
    cls = BA.Cls()
    defs, kinds = load_xml_defs()
    by_def, filed_ids = queue_view()
    inst = installable_defs(plan_p)

    roster_biomes = defaultdict(set)              # def -> biomes casting it
    labels = {}
    for bd in census["biome_order"]:
        for r in census["biomes"][bd]["rows"]:
            for dn in (r.get("defNames") or [r["key"]]):
                roster_biomes[dn].add(bd)
                labels.setdefault(dn, r.get("label"))

    targets, gaps = {}, defaultdict(list)       # def -> {why:set, src}
    skip_defs = set()
    if exclude_jobs and exclude_jobs.is_file():
        skip_defs = {r["target_def"] for r in json.loads(exclude_jobs.read_text())["rows"]}

    def add(dn, why):
        targets.setdefault(dn, set()).add(why)

    for bd, rows in ([] if sw_only else audit["roster"].items()):
        for r in rows:
            if r["class"] in ("DONOR", "PLACEHOLDER", "NO_LIVE_DONOR_ONLY", "NO_LIVE_ART", "VANILLA_BORROWED"):
                dn = r["defName"]
                if dn not in defs:
                    gaps["roster casts a donor/vanilla def with no def of ours (port owed first)"].append(f"{bd}:{dn}")
                    continue
                add(dn, f"roster {bd}: {r['class']}")
    for key, v in audit["defs"].items():
        twin = v["group"] == "twin"
        if sw_only and "SWBestiary" not in key:
            continue
        for r in v["rows"]:
            if r["class"] not in ("DONOR", "PLACEHOLDER", "EXTERNAL"):
                continue
            dn = r["def"]
            if twin and (dn in roster_biomes) == sw_only:   # sw_only: the no-roster twin defs; else: roster-cast only
                continue
            if dn in skip_defs:
                continue
            if dn not in defs:
                continue
            add(dn, f"{key}: {r['class']}")
    for dn, ents in ([] if sw_only else repo.defs.items()):
        if any(t.startswith("StandIn/") for e in ents for vs in e[2].values() for t in vs):
            add(dn, "draws a StandIn/ copy")

    rows, skipped = [], defaultdict(list)
    for dn in sorted(targets):
        el, tag, xfile = defs.get(dn, (None, "", ""))
        if xfile and BA.excluded(xfile):
            continue
        if by_def.get(dn):
            skipped["a pending/active job already targets it"].append(dn)
            continue
        ke = kinds.get(dn)
        kind = kind_of(el, tag, kinds, dn)
        biomes = sorted(roster_biomes.get(dn, ()))
        start = any(b in START for b in biomes)
        texs = textures_of(repo, dn, el, ke)            # [(tag, text, drawSize or None, parent tag)]
        if not texs:
            skipped["names no texture (inherited or set in C#): UNMEASURED"].append(dn)
            continue
        label = clean((el.findtext("label") if el is not None else None) or labels.get(dn) or dn)
        desc = clean(el.findtext("description") if el is not None else "")
        if not desc and ke is not None:
            desc = clean(ke.findtext("description"))
        ds_def = draw_size(ke, el)
        base = {"rimflow_item_id": SW_ITEM if sw_only else ITEM, "target_def": dn, "channel": "codex", "style_notes": HOUSE,
                "biome_register": BA_REG(biomes), "ask": "new", "why": "; ".join(sorted(targets[dn])),
                "kind": kind, "biomes": biomes}
        any_row = False
        for ttag, t, ds_t, ptag in texs:
            if "flyingAnimationFramePath" in ttag:
                gaps["flight flip-book frames (flight.md; never commissioned blind)"].append(f"{dn}:{t}")
                continue
            files = [(m, k) for m, k in files_for(repo, t)]
            orig = t.removeprefix("StandIn/")
            bad = [(m, k) for m, k in files if t.startswith("StandIn/") or cls.of(f"{m}/Textures/{k}.png") in BAD]
            ext = not files
            if not ext and not bad:
                continue
            if bad and all(dest(m, k) in inst for m, k in bad):
                skipped["a finished render is installable now (run the installer)"].append(f"{dn}:{t}")
                continue
            role = ("desiccated" if "essicated" in t else "juvenile" if BA.JUV.search(t) or re.search(r"(^|_)j$", t)
                    else "swimming" if "Swim" in t else "icon" if ttag in ("uiIconPath", "iconPath")
                    else "alt" if ptag == "li" and kind == "creature" else "body")
            k2 = "icon" if role == "icon" else kind
            ds = ds_t or ds_def
            slug = re.sub(r"[^A-Za-z0-9]", "", orig.rsplit("/", 1)[-1])
            rid = f"dregen_{dn}_{slug}_v1"
            prio = KIND_PRIO.get(k2 + ("_start" if start and k2 in ("creature", "plant") else ""), 80)
            if role in ("juvenile", "swimming"):
                prio += 5
            elif role == "desiccated":
                prio += 8
            elif role == "alt":
                prio += 10
            row0 = dict(base, priority=prio, kind=k2)
            if k2 == "creature":
                canon = canon_slug(dn)
                px = pow2(ds * 128, 256, 1024)
                what = {"juvenile": f"a juvenile {label}, young proportions",
                        "desiccated": f"the desiccated corpse of a {label}: dried, shrunken hide over the skeleton, "
                                      f"lying on its side, muted dusty colours",
                        "swimming": f"the {label} swimming, body low and stretched",
                        "alt": f"the {label} in an alternate natural coat colouring (a colour variant of the same "
                               f"animal, same anatomy)",
                        "body": f"the {label}"}[role]
                scale = (f"In game it is drawn {ds:g} cells wide against a vanilla human's 1 cell; the body fills "
                         f"most of the canvas, whole, never shrunk inside the frame.")
                if canon:
                    prompt = (f"RimWorld creature sprite, side view (east): the Star Wars canon creature {dn}, shown as "
                              f"{what}. Highly realistic painted natural-history illustration in the painterly "
                              f"vanilla-RimWorld house style, matte, no outlines. Follow canon anatomy, colouring and "
                              f"proportions precisely: satisfy every item of the Must show list below. Single creature, "
                              f"centred, transparent background, no ground shadow, no scenery. {scale}")
                else:
                    prompt = (f"RimWorld creature sprite, side view (east), painterly: {what}. {desc} Our own original "
                              f"design, drawn fresh; no recognisable Earth animal. One animal, whole body, centred. {scale}")
                row = dict(row0, prompt=prompt, canvas_w=px, canvas_h=px, drawsize=ds, background="transparent")
                if canon:
                    row["canon"] = canon
                fac = [f for f in ("east", "south", "north") if any(k.endswith("_" + f) for _, k in bad)]
                if ext:
                    fac = ["east", "south", "north"]
                if fac:
                    row["facings"] = fac
                    if not ext:
                        m, k = next((m, k) for m, k in bad if re.search(r"_(east|south|north)$", k))
                        row["install_to"] = dest(m, BA.strip_facing(k) + "_{facing}")
                else:
                    row["facings"] = []
                    row["prompt"] = prompt.replace("side view (east)", "three-quarter view")
                if ext:
                    row["target_texpath"] = orig
                if not ext and not fac:
                    m, k = bad[0]
                    row["install_to"] = dest(m, k)
                rows.append(dict(row, id=rid))
                any_row = True
                continue
            if k2 == "terrain":
                px, bg = 1024, "opaque"
                prompt = (f"A seamless square terrain texture seen straight down from above: {label}. {desc} Even, "
                          f"flat lighting, no single dominant feature.")
                notes = ("Ground texture for a RimWorld floor: fully opaque, tiles seamlessly in both directions, no "
                         "vignette and no edge darkening; mid-value overall so the game's tint and rough edge blend.")
            elif k2 == "plant":
                tree = el is not None and el.find("plant/treeCategory") is not None
                px, bg = (512 if tree or ds >= 1.9 else 256), "transparent"
                prompt = (f"RimWorld {'tree' if tree else 'plant'} sprite, painterly: the {label}. {desc} Our own "
                          f"original design, drawn fresh; not a recognisable Earth plant. One plant, centred, base at "
                          f"bottom centre.")
                notes = HOUSE
            elif k2 == "building":
                px, bg = pow2(ds * 128, 128, 1024), "transparent"
                prompt = (f"RimWorld building sprite, seen from above in the vanilla three-quarter view: the {label}. "
                          f"{desc} Our own original design, drawn fresh. One object, centred, silhouette inside its "
                          f"footprint.")
                notes = HOUSE
            elif k2 == "icon":
                px, bg = 128, "transparent"
                prompt = f"RimWorld UI icon, painterly: the {label}. {desc} One clear symbol, centred, readable small."
                notes = HOUSE
            else:
                px, bg = pow2(ds * 128, 128, 512), "transparent"
                prompt = (f"RimWorld item sprite, painterly: the {label}. {desc} Our own original design, drawn fresh. "
                          f"One subject, centred.")
                notes = HOUSE
            common = dict(row0, canvas_w=px, canvas_h=px, background=bg, style_notes=notes, facings=[])
            if ext:
                rows.append(dict(common, id=rid, prompt=prompt, target_texpath=orig))
                any_row = True
                continue
            multi = [(m, k) for m, k in bad if re.search(r"_(east|south|north)$", k)]
            if multi:
                m, k = multi[0]
                fac = [f for f in ("south", "east", "north") if any(kk.endswith("_" + f) for _, kk in bad)]
                rows.append(dict(common, id=rid, prompt=prompt, facings=fac,
                                 install_to=dest(m, BA.strip_facing(k) + "_{facing}")))
                any_row = True
                continue
            many = len(bad) > 1
            for i, (m, k) in enumerate(bad):
                vs = re.sub(r"[^A-Za-z0-9]", "", k.rsplit("/", 1)[-1])
                p = prompt + (f" Variant {i + 1} of {len(bad)}: a clearly different silhouette from the others."
                              if many else "")
                rows.append(dict(common, id=f"dregen_{dn}_{vs}_v1", prompt=p, install_to=dest(m, k),
                                 slot=k.removeprefix("StandIn/")))
                any_row = True
        if not any_row:
            skipped["every file it draws is already ours (REGEN/UNPROVEN/DERIVED)"].append(dn)
    seen_dest, uniq = set(), []
    for r in rows:                                   # one shared texture is one job (FeralNerfDessicated)
        d = r.get("install_to") or ("ext:" + r["target_def"] + ":" + r.get("target_texpath", ""))
        if d in seen_dest:
            skipped["shares a destination with another row"].append(r["id"])
            continue
        seen_dest.add(d)
        uniq.append(r)
    rows = uniq
    for r in rows:
        ids = [r["id"]] if not r["facings"] else [f"{r['id']}_{f}" for f in r["facings"]]
        if any(i in filed_ids for i in ids):
            r["_already_filed"] = True
    rows.sort(key=lambda r: (r["priority"], r["id"]))
    out.write_text(json.dumps({"generated": BA.A.now(), "git_head": subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "item": SW_ITEM if sw_only else ITEM, "audit": str(audit_p), "rows": rows, "skipped": skipped, "gaps": gaps}, indent=1))
    kc = Counter((r["kind"], r["priority"]) for r in rows)
    nj = sum(max(1, len(r["facings"])) for r in rows)
    print(f"targets {len(targets)}; rows {len(rows)} ({nj} job files); by kind/prio {sorted(kc.items())}")
    print("skipped: " + ", ".join(f"{k}={len(v)}" for k, v in skipped.items()))
    print("gaps: " + ", ".join(f"{k}={len(v)}" for k, v in gaps.items()))


def BA_REG(biomes):
    try:
        import placeholder_jobs as PJ
    except Exception:                                     # noqa: BLE001
        return "the subject keeps its own colours in the biome's natural light; muted, matte, painterly"
    for b in biomes:
        if b in PJ.REGISTER:
            return PJ.REGISTER[b]
    return PJ.DEFAULT_REG


# ──────────────────────────────────────────────────────────────── submit ──

def in_flight() -> int:
    return sum(1 for st in ("pending", "active") for f in (ART / st).iterdir()
               if f.name.endswith(".json") and not f.name.endswith(".manifest.json"))


def submit(jobs_ps, cap: int, dry: bool, gate=None):
    """Feed the job files in order (earlier files claim the room first); one shared cap. Every row passes the
    eligibility gate (regen_eligibility.py, owner 2026-10-19: only confirmed NONE / PLACEHOLDER / DONOR art is
    queued). Fail closed: a gate that cannot be built files nothing."""
    try:
        gate = gate or RE.Gate()
    except RE.GateError as e:
        print(f"ELIGIBILITY GATE FAILED — filing nothing: {e}", file=sys.stderr)
        return 2
    rc = 0
    for jp in jobs_ps:
        if cap - in_flight() <= 0:
            print(f"queue at cap before {jp.name}")
            break
        rc = submit_one(jp, cap, dry, gate) or rc
    return rc


def submit_one(jobs_p: Path, cap: int, dry: bool, gate=None):
    if gate is None:
        try:
            gate = RE.Gate()
        except RE.GateError as e:
            print(f"ELIGIBILITY GATE FAILED — filing nothing: {e}", file=sys.stderr)
            return 2
    J = json.loads(jobs_p.read_text())
    _, filed = queue_view()
    room = cap - in_flight()
    print(f"in flight {cap - room} / cap {cap}")
    batch, refused = [], []
    for r in J["rows"]:
        if room <= 0:
            break
        n = max(1, len(r["facings"]))
        ids = [r["id"]] if not r["facings"] else [f"{r['id']}_{f}" for f in r["facings"]]
        if any(i in filed for i in ids):
            continue
        v = gate.classify(r)
        if not v["eligible"]:
            refused.append(v)
            continue
        if n > room and batch:
            break
        batch.append({k: v for k, v in r.items() if not k.startswith("_") and k not in ("kind", "biomes", "why")})
        room -= n
    if refused:
        print(f"eligibility gate refused {len(refused)} rows: "
              + ", ".join(f"{k}={n}" for k, n in Counter(v["verdict"] for v in refused).most_common()))
        for v in refused[:20]:
            print(f"  REFUSED {v['id']}: {v['verdict']} — {v['reason'][:160]}")
        if not dry:
            with (ART / "_refs" / (jobs_p.stem + ".refused.log")).open("a") as fh:
                for v in refused:
                    fh.write(json.dumps({"ts": BA.A.now(), "id": v["id"], "verdict": v["verdict"],
                                         "reason": v["reason"]}) + "\n")
    if not batch:
        print("nothing to file (queue at cap, every row already filed, or every remaining row refused)")
        return 0
    tmp = ART / "_refs" / f"donor_regen_batch_{BA.A.now().replace(':', '')}.json"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(json.dumps(batch, indent=1))
    cmd = [sys.executable, str(REPO / "src/RimMandrake/Utils/artpipe/fill_queue.py"), "--input", str(tmp)]
    if dry:
        cmd.append("--dry-run")
    print(f"filing {len(batch)} rows from {jobs_p.name}: {batch[0]['id']} .. {batch[-1]['id']}  (batch file {tmp})")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("\n".join((res.stdout + res.stderr).strip().splitlines()[-(40 if dry else 6):]))
    if dry:
        tmp.unlink()
        return res.returncode
    with (ART / "_refs" / (jobs_p.stem + ".submitted.log")).open("a") as fh:
        fh.write(json.dumps({"ts": BA.A.now(), "dry": dry, "rows": [b["id"] for b in batch], "rc": res.returncode,
                             "batch_file": str(tmp)}) + "\n")
    return res.returncode


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build")
    b.add_argument("--audit", required=True, type=Path)
    b.add_argument("--census", required=True, type=Path)
    b.add_argument("--plan", type=Path, help="a bulk_accept_renders plan: defs it can install now are skipped")
    b.add_argument("--out", required=True, type=Path)
    b.add_argument("--sw-only", action="store_true", help="only SWBestiary twin defs in NO biome roster "
                   "(owner 2026-10-18: redraw all)")
    b.add_argument("--exclude-jobs", type=Path, help="skip defs already in this job file")
    s = sp.add_parser("submit")
    s.add_argument("--jobs", required=True, type=Path, nargs="+", help="fed in order, one shared cap")
    s.add_argument("--cap", type=int, default=40, help="max job files pending+active after filing")
    s.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.audit, a.census, a.plan, a.out, a.sw_only, a.exclude_jobs)
    else:
        sys.exit(submit(a.jobs, a.cap, a.dry_run))


if __name__ == "__main__":
    main()
