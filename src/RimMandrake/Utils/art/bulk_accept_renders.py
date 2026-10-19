#!/usr/bin/env python3
"""bulk_accept_renders.py — install every finished artpipe render that is still waiting, onto the texture our defs
draw, where that texture is today a donor copy, a stand-in, a placeholder, or missing.

Owner, 2026-10-18 (relayed by the FOUNDRY coordinator): "Yes. Simply accept all art as currently rendered to get this
done. We will re review at a later time. No more art blockers."  Item: TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING.

    RIMFLOW_SEAT=FOUNDRY python3 src/RimMandrake/Utils/art/bulk_accept_renders.py plan  --out <plan.json>
    RIMFLOW_SEAT=FOUNDRY python3 src/RimMandrake/Utils/art/bulk_accept_renders.py apply --plan <plan.json> [--only <mod substr>]

Destination of a done job (PNG in _artsrc/<id>/<id>.png, done/<id>.manifest.json present), first that applies:
  1. its `install_to`;  2. `target_texpath` (+ _north/_south/_east/_west from `facing`) found under one src mod's
  Textures (the mod defining `target_def` breaks a tie; a StandIn/<path> copy counts, see below);  3. `target_def`'s own
  texPath (+ facing);  4. no binding: the job id names exactly one def stem of ours and that def draws exactly one file
  for the job's facing (name-joined; only used where no bound job reaches the file).
A destination is REPLACED only when the file there is donor bytes, a geometric placeholder, missing while some XML of
ours draws it, or the XML draws StandIn/<path> (then the render goes in at <path> and the XML is pointed back; the
stand-in file stays as past art). REGEN bytes (an artpipe render / art install / collect), UNPROVEN and DERIVED bytes
are left alone. Several jobs on one destination: bound beats name-joined, then the newest PNG wins. `_var<x>_` job ids
on a Graphic_Random folder go in as the extra variant file <stem>_<x>.png. src/RimMandrake/FlowWorks is never touched.
Installs go through artledger.install (mechanical reason script:<this file>; his words only where the ledger refuses
over an owner keep or a rejection/redo), and each is appended to <artpipe>/collected.jsonl as collect_one does.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "src"
ART = Path(os.environ.get("ARTPIPE_STATE") or "/mnt/d/Luke/dev/_artpipe")
sys.path.insert(0, str(HERE))
import artledger as A            # noqa: E402
import placeholder_detect as PD  # noqa: E402

OWNER_SAID = ("Yes. Simply accept all art as currently rendered to get this done. "
              "We will re review at a later time. No more art blockers.")
REASON = "script:src/RimMandrake/Utils/art/bulk_accept_renders.py bulk accept (TEXREGEN_STANDINS_INSTALL_RENDERS_WAITING)"
EXCLUDE = ("src/RimMandrake/FlowWorks/",)
NO_XML_EDIT = ("src/RimUtinni/UtinniPatches/Defs/BiomeDefs/", "src/RimMandrake/FlowWorks/")
FACINGS = ("north", "south", "east", "west")
TEXTAGS = {"texPath", "texturePath", "uiIconPath", "wornGraphicPath", "flyingAnimationFramePathPrefix",
           "flyingAnimationFramePathPrefixFemale", "iconPath", "graphicPath"}


def sha_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def excluded(rel: str) -> bool:
    return any(rel.startswith(e) for e in EXCLUDE)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ─────────────────────────────────────────────────────────────── the repo view ──

class Repo:
    def __init__(self):
        self.tex = defaultdict(list)       # texrel (no .png) -> [mod dir rel 'src/T/M']
        self.mods = sorted(str(p.parent.relative_to(REPO)) for p in SRC.glob("*/*/Textures") if p.is_dir())
        for m in self.mods:
            if excluded(m + "/"):
                continue
            root = REPO / m / "Textures"
            for p in root.rglob("*.png"):
                self.tex[str(p.relative_to(root))[:-4]].append(m)
        self.defs = defaultdict(list)      # defName -> [(mod, xmlfile, {tag: [texts]}, graphicClass)]
        self.drawn = defaultdict(set)      # texPath text -> {xml files (repo-rel)}
        self.gclass = {}                   # (defName, texture text) -> graphicClass of its element ('' = inherited)
        seen = set()
        for x in SRC.rglob("*.xml"):
            r = str(x.relative_to(REPO))
            if excluded(r) or "/Textures/" in r or r in seen:
                continue
            seen.add(r)
            parts = r.split("/")
            mod = "/".join(parts[:3])
            try:
                root = ET.parse(x).getroot()
            except (ET.ParseError, OSError):
                continue
            for el in root.iter():
                if isinstance(el.tag, str) and el.tag in TEXTAGS and (el.text or "").strip() and not list(el):
                    self.drawn[el.text.strip()].add(r)
            if "/Defs/" not in r:
                continue
            for d in root:
                dn = d.find("defName")
                if dn is None or not (dn.text or "").strip():
                    continue
                tps = defaultdict(list)
                for el in d.iter():
                    if isinstance(el.tag, str) and el.tag in TEXTAGS and (el.text or "").strip() and not list(el):
                        tps[el.tag].append(el.text.strip())
                gd = d.find("graphicData")
                gc = (gd.findtext("graphicClass") or "").strip() if gd is not None else ""
                gtp = (gd.findtext("texPath") or "").strip() if gd is not None else ""
                self.defs[dn.text.strip()].append((mod, r, dict(tps), gc, gtp))
                for par in d.iter():                      # graphicClass of the element each texture text sits in
                    for c in par:
                        if isinstance(c.tag, str) and c.tag in TEXTAGS and (c.text or "").strip():
                            self.gclass[(dn.text.strip(), c.text.strip())] = (par.findtext("graphicClass") or "").strip()

    def mods_with(self, texrel: str) -> list[str]:
        return sorted(set(self.tex.get(texrel, [])))

    def mods_with_dir(self, tp: str) -> list[str]:
        return sorted({m for k, ms in self.tex.items() if k.startswith(tp + "/") for m in ms})

    def def_mods(self, dn: str) -> list[str]:
        return sorted({d[0] for d in self.defs.get(dn, [])})


def strip_facing(stem: str) -> str:
    return re.sub(r"_(north|south|east|west)$", "", stem)


def is_drawn(repo: Repo, texrel: str) -> list[str]:
    """XML files whose texture text draws texrel (exact, base without facing, or its folder for Graphic_Random)."""
    cands = {texrel, strip_facing(texrel), texrel.rsplit("/", 1)[0]}
    out = set()
    for c in cands:
        out |= repo.drawn.get(c, set())
    return sorted(out)


# ───────────────────────────────────────────────────────────────── the jobs ──

def load_jobs():
    jobs = []
    for f in sorted((ART / "done").glob("*.json")):
        if f.name.endswith(".manifest.json"):
            continue
        try:
            j = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        jid = j.get("id") or f.stem
        png = ART / "_artsrc" / jid / f"{jid}.png"
        if not png.is_file() or not (ART / "done" / f"{jid}.manifest.json").is_file():
            continue
        j["_png"] = str(png)
        j["_mtime"] = png.stat().st_mtime
        jobs.append(j)
    return jobs


def facing_suffix(j) -> str:
    f = (j.get("facing") or "").lower()
    return f"_{f}" if f in FACINGS else ""


def variant_letter(jid: str) -> str | None:
    m = re.search(r"_var([b-z])(?:_|$)", jid)
    return m.group(1) if m else None


OUR_TOKEN = re.compile(r"(^|/)(RM|RSW|RUT)_|^(RimMandrake|RimStarWars|RimUtinni)/", re.I)
JUV = re.compile(r"(_j|juv|juvenile|baby|young|calf|pup|chick|larva)$", re.I)


def subject_in_path(subject: str, path: str) -> bool:
    s = norm(re.sub(r"^(RM|RSW|RUT)_", "", subject))
    return len(s) >= 4 and s in norm(path)


def ours_for(repo: "Repo", tp: str, subj: str) -> bool:
    """True when the texture path belongs to this subject in OUR namespace: an RM_/RSW_/RUT_ component, or a def of
    ours whose stem is in the path (swanimals/Bantha for RSW_Bantha). A vanilla Core path is not in the gametex index,
    so 'not ours' is decided by this, never by an index miss (Meat_Small for a Catch item, 2026-10-18)."""
    if OUR_TOKEN.search(tp):
        return True
    return bool(subj and repo.def_mods(subj) and subject_in_path(subj, tp))


def def_texpaths(repo: "Repo", dn: str, jid: str = "") -> list[str]:
    """The texPath(s) def `dn` draws for its body: graphicData first, else every texPath it names (a PawnKind's life
    stages). Juvenile stages are dropped unless the job id says juvenile; dessicated and pack overlays always."""
    ents = repo.defs.get(dn, [])
    g = sorted({e[4] for e in ents if e[4]})
    if g:
        return g
    tps = sorted({t for e in ents for t in e[2].get("texPath", [])
                  if "essicated" not in t and not t.lower().endswith("pack")})
    if len(tps) > 1:
        # alternate skins (BanthaV_G, EopieA) and swim/flight frames are not the body the job drew, unless it says so
        swim = bool(re.search(r"swim", jid.lower()))
        fly = bool(re.search(r"fly|flight", jid.lower()))
        alt = {t for t in tps if re.search(r"V_[A-Z]\d?$", t) or (re.fullmatch(r".*[a-z][A-Z]", t) and t[:-1] in tps)}
        keep = [t for t in tps if t not in alt and bool(re.search(r"_Swimming$", t)) == swim
                and bool(re.search(r"_Flying", t)) == fly]
        if keep:
            tps = keep
    if len(tps) > 1:
        juv = bool(re.search(r"(^|_)(j|juv|juvenile|baby|young|calf|pup|chick)(_|$)", jid.lower()))
        keep = [t for t in tps if bool(JUV.search(t)) == juv]
        if keep:
            tps = keep
    return tps


def editable_blocks(repo: "Repo", dn: str, text: str) -> list[str]:
    """Defs XML files (editable) where def `dn` carries `text` as a texture element."""
    return sorted({e[1] for e in repo.defs.get(dn, []) if not any(e[1].startswith(n) for n in NO_XML_EDIT)
                   and any(text in v for v in e[2].values())})


def def_is_random(repo: "Repo", dn: str, tp: str) -> bool:
    return repo.gclass.get((dn, tp)) == "Graphic_Random"


def own_path(ext_tp: str, dn: str) -> str:
    parts = ext_tp.strip("/").split("/")
    if len(parts) >= 2 and parts[-1].lower().startswith(parts[-2].lower()):
        parts[-2] = parts[-1] = dn                      # Dromedary/Dromedary, Echeveria/EcheveriaA
    else:
        parts[-1] = dn + "/" + dn                       # Things/Plant/Grass -> Things/Plant/RM_X/RM_X
    return "/".join(parts)


LETTER = re.compile(r"(?:_var([a-z])|_([a-h]))(?:_v\d+|_redo|_tint|_|$)")


def job_letter(jid: str) -> str | None:
    m = LETTER.search(re.sub(r"_(north|south|east|west|single)$", "", jid))
    return (m.group(1) or m.group(2)) if m else None


def random_dest(repo: "Repo", mod: str, folder: str, jid: str) -> tuple[str | None, str]:
    """A file inside a Graphic_Random folder for this job: <base><sep><letter>.png in the naming the folder already
    uses (RM_X_a / RM_X_b, or A / B / C)."""
    d = REPO / mod / "Textures" / folder
    files = sorted(q.stem for q in d.glob("*.png") if not q.stem.endswith("_m")) if d.is_dir() else []
    letter = job_letter(jid) or "a"
    if not files:
        return f"{mod}/Textures/{folder}/{folder.rsplit('/', 1)[-1]}_{letter}.png", f"random_{letter}"
    if len(files) == 1:
        m = re.fullmatch(r"(.*?)(_?)([a-zA-Z])", files[0]) if (re.search(r"_[a-z]$", files[0]) or len(files[0]) == 1) else None
        pre, sep, last = (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)
    else:
        pre = os.path.commonprefix(files)
        rems = [f[len(pre):] for f in files]
        if not all(re.fullmatch(r"_?[a-zA-Z]", r) for r in rems):
            pre = pre[:-1] if pre else pre
            rems = [f[len(pre):] for f in files]
        if not all(re.fullmatch(r"_?[a-zA-Z]", r) for r in rems):
            return None, "Graphic_Random folder naming not <base><letter>"
        sep = "_" if rems[0].startswith("_") else ""
        last = rems[0][-1]
    if pre is None:
        return None, "Graphic_Random folder naming not <base><letter>"
    if pre.endswith("_") and not sep:
        pre, sep = pre[:-1], "_"
    lt = letter.upper() if last.isupper() else letter
    return f"{mod}/Textures/{folder}/{pre}{sep}{lt}.png", f"random_{letter}"


def resolve_texpath(repo: "Repo", tp: str, j) -> tuple[str | None, str, dict | None]:
    """-> (dest 'src/T/M/Textures/<rel>.png' | None, how, fix | None). fix = {'kind': 'standin'|'external', ...}:
    an XML texture element that must be pointed at the destination for the render to be drawn."""
    suf = facing_suffix(j)
    tp = tp.strip().strip("/")
    if tp.startswith("StandIn/"):
        tp = tp[len("StandIn/"):]
    rel = tp + suf
    subj = j.get("target_def") or ""
    dmods = repo.def_mods(subj)
    mine = ours_for(repo, tp, subj)
    mods = repo.mods_with(rel)
    if not mods and not suf and repo.mods_with(rel + "_south"):
        return None, "texpath is Graphic_Multi but the job has no facing", None
    if len(mods) > 1:
        pick = [m for m in mods if m in dmods]
        if len(pick) != 1:
            return None, f"texpath in {len(mods)} mods", None
        mods = pick
    if mods and mine:
        return f"{mods[0]}/Textures/{rel}.png", "texpath", None
    if not mods and mine:
        smods = repo.mods_with("StandIn/" + rel)
        if smods:
            if len(smods) > 1:
                pick = [m for m in smods if m in dmods]
                if len(pick) != 1:
                    return None, f"standin in {len(smods)} mods", None
                smods = pick
            return f"{smods[0]}/Textures/{rel}.png", "standin", {"kind": "standin", "from": "StandIn/" + tp, "to": tp}
        fm = [m for m in (dmods or repo.mods_with_dir(tp)) if (REPO / m / "Textures" / tp).is_dir()]
        if fm and is_drawn(repo, tp + "/x"):
            d, how = random_dest(repo, fm[0], tp, j["id"])
            return d, how, None
        if len(dmods) == 1 and is_drawn(repo, rel):
            return f"{dmods[0]}/Textures/{rel}.png", "missing-drawn", None
        return None, "texpath resolves to no file of ours", None
    # the def draws a vanilla/donor path (or a donor copy / a stand-in of one): our render goes in at a path of its
    # own and the def is pointed there; never at the shared path, which every other def drawing it would pick up
    if not subj or len(dmods) != 1:
        return None, "vanilla/donor texpath, no single def of ours to repoint", None
    frm = next((t for t in (tp, "StandIn/" + tp) if editable_blocks(repo, subj, t)), None)
    if not frm:
        return None, "vanilla/donor texpath not set in an editable Defs file of the def", None
    xmls = editable_blocks(repo, subj, frm)
    gc = repo.gclass.get((subj, frm), "")
    new = own_path(tp, subj)
    if gc == "Graphic_Random":
        new = new.rsplit("/", 1)[0]
        dest = f"{dmods[0]}/Textures/{new}/{subj}_{job_letter(j['id']) or 'a'}.png"
    elif (gc == "Graphic_Single" and not suf) or (gc in ("Graphic_Multi", "") and suf):
        # '' with facings: a PawnKind life stage's bodyGraphicData, which the engine defaults to Graphic_Multi
        dest = f"{dmods[0]}/Textures/{new}{suf}.png"
    else:
        return None, f"vanilla/donor texpath, graphicClass {gc or 'inherited'} with facing '{suf}': not repointed", None
    return dest, "external-repoint", {"kind": "external", "def": subj, "from": frm, "to": new, "xml": xmls}


def resolve_def(repo: "Repo", j, dn: str):
    tps = def_texpaths(repo, dn, j["id"])
    if len(tps) != 1:
        return None, f"target_def draws {min(len(tps), 2)}{'+' if len(tps) > 1 else ''} texPaths", None
    d, how, s = resolve_texpath(repo, tps[0], dict(j, target_def=dn))
    return d, "def:" + how, s


def resolve_job(repo: Repo, j):
    """-> (dest | None, how, fix | None, bound: bool)."""
    if j.get("install_to"):
        d = j["install_to"].lstrip("/")
        if not d.startswith("src/") or "/Textures/" not in d:
            return None, "install_to not under src Textures", None, True
        rel = d.split("/Textures/", 1)[1][:-4]
        mod = d.split("/Textures/", 1)[0]
        if not (REPO / d).is_file() and mod in repo.mods_with("StandIn/" + rel):
            b = strip_facing(rel)
            return d, "install_to-standin", {"kind": "standin", "from": "StandIn/" + b, "to": b}, True
        subj = j.get("target_def") or ""
        if not ours_for(repo, rel, subj):
            return None, "install_to is a vanilla/donor path not of this subject", None, True
        return d, "install_to", None, True
    if j.get("target_texpath"):
        d, how, s = resolve_texpath(repo, j["target_texpath"], j)
        if d or not j.get("target_def"):
            return d, how, s, True
        # the job's texpath is stale (the def has since moved): the def's own texPath decides
        d2, how2, s2 = resolve_def(repo, j, j["target_def"])
        return (d2, how2, s2, True) if d2 else (None, how, None, True)
    if j.get("target_def"):
        d, how, s = resolve_def(repo, j, j["target_def"])
        return d, how, s, True
    return None, "unbound", None, False


def name_join(repo: Repo, j, stems: dict):
    """Unbound job -> a single plausible destination, else (None, why). The job id, stripped of version, facing and
    a biome/regen prefix, must EQUAL one def stem of ours (substring joins put a door's Top layer on the door)."""
    jid = re.sub(r"_v\d+.*$", "", j["id"])
    jid = re.sub(r"_(north|south|east|west|single)$", "", jid)
    toks = jid.split("_")
    cands = set()
    for i in range(len(toks)):
        cands.add(norm("".join(toks[i:])))
    hits = [(s, stems[s]) for s in cands if len(s) >= 5 and s in stems]
    if not hits:
        return None, "unbound, no def stem"
    best = max(len(s) for s, _ in hits)
    top = [(s, dns) for s, dns in hits if len(s) == best]
    if len(top) != 1 or len(top[0][1]) != 1:
        return None, "unbound, several defs match"
    dn = next(iter(top[0][1]))
    d, how, s = resolve_def(repo, j, dn)
    if not d:
        return None, f"unbound -> {dn}: {how}"
    return (d, "name-joined:" + dn + ":" + how, s), ""


# ──────────────────────────────────────────────────────────────── classify ──

class Cls:
    def __init__(self):
        self.idx = A.Index()

    def of(self, dest: str) -> str:
        p = REPO / dest
        if not p.is_file():
            return "MISSING"
        sha = sha_of(p)
        ks = {v.get("kind") for v in self.idx.variants.get(sha, ())}
        mod, rel = dest.split("/Textures/", 1)
        ev = self.idx.live.get((A.mod_key(mod), A.rel_key(rel)))
        live_reason = (ev.get("reason") or "") if ev and ev.get("sha") == sha else ""
        try:
            if PD.placeholder_reason(p.read_bytes()):
                return "PLACEHOLDER"
        except Exception:                                  # noqa: BLE001
            pass
        if "donor" in ks:
            return "DONOR"
        if "artpipe" in ks or "install" in ks or live_reason.startswith(("install", "artpipe-collect")):
            return "REGEN"
        if "derived" in ks or live_reason.startswith("script"):
            return "DERIVED"
        return "UNPROVEN"


REPLACE = {"DONOR", "PLACEHOLDER", "MISSING"}


def plan(out: Path):
    repo = Repo()
    cls = Cls()
    stems = defaultdict(set)
    for dn, ents in repo.defs.items():
        if any(e[2] for e in ents):
            stems[norm(re.sub(r"^(RM|RSW|RUT)_", "", dn))].add(dn)
    jobs = load_jobs()
    by_dest = defaultdict(list)
    unresolved = defaultdict(list)
    for j in jobs:
        dest, how, fix, bound = resolve_job(repo, j)
        if not bound:
            r, why = name_join(repo, j, stems)
            if r is None:
                unresolved[why if why.startswith("unbound,") else "unbound, name-joined def unresolvable"].append(
                    {"job": j["id"], "why": why})
                continue
            dest, how, fix = r
        if not dest:
            unresolved[how].append({"job": j["id"]})
            continue
        if excluded(dest):
            unresolved["flowworks"].append({"job": j["id"]})
            continue
        mdir = REPO / dest.split("/Textures/", 1)[0]
        if not ((mdir / "About").is_dir() or (mdir / "Defs").is_dir() or (mdir / "Patches").is_dir()):
            unresolved["destination mod folder is not a mod (no About/Defs/Patches)"].append({"job": j["id"], "dest": dest})
            continue
        letter = variant_letter(j["id"])
        if letter:
            stem = dest[:-4]
            folder_drawn = repo.drawn.get(stem.split("/Textures/", 1)[1].rsplit("/", 1)[0])
            if re.search(r"_[a-z]$", stem) and folder_drawn:
                dest = re.sub(r"_[a-z]$", f"_{letter}", stem) + ".png"
                how += f"+variant_{letter}"
        by_dest[dest].append({"job": j["id"], "how": how, "fix": fix, "bound": bound,
                              "mtime": j["_mtime"], "png": j["_png"]})
    rows, skipped = [], defaultdict(list)
    for dest, cands in sorted(by_dest.items()):
        c = cls.of(dest)
        cands.sort(key=lambda x: (x["bound"], x["mtime"]), reverse=True)
        ok = [x for x in cands if not cls.idx.is_purged(sha_of(Path(x["png"])))]   # purged bytes never go back
        if not ok:
            skipped["every render for it was purged by the owner"].append({"dest": dest, "jobs": [x["job"] for x in cands]})
            continue
        win, rest = ok[0], [x for x in cands if x is not ok[0]]
        fix = win["fix"] or next((x["fix"] for x in cands if x["fix"]), None)
        if c == "MISSING" and not fix and not is_drawn(repo, dest.split("/Textures/", 1)[1][:-4]):
            skipped["missing and drawn by no XML of ours"].append({"dest": dest, "job": win["job"]})
            continue
        if fix and fix["kind"] == "external":
            sm = re.search(r"(_(north|south|east|west))?$", dest[:-4]).group(0)
            orig = f"{dest.split('/Textures/', 1)[0]}/Textures/{fix['from']}{sm}.png"
            oc = cls.of(orig)
            if oc not in REPLACE:
                skipped[f"live is {oc} (at the path the def draws now)"].append(
                    {"dest": orig, "jobs": [x["job"] for x in cands]})
                continue
        if c not in REPLACE and not (fix and c == "REGEN"):
            skipped[f"live is {c}"].append({"dest": dest, "jobs": [x["job"] for x in cands]})
            continue
        if (REPO / dest).is_file() and sha_of(Path(win["png"])) == sha_of(REPO / dest):
            skipped["already live"].append({"dest": dest, "job": win["job"]})
            continue
        rows.append({"dest": dest, "class": c, "job": win["job"], "how": win["how"], "png": win["png"],
                     "fix": fix, "others": [x["job"] for x in rest]})
    # a repoint goes in only when every facing the XML will now draw exists or is planned: for a stand-in, every
    # StandIn file under the path has its <orig> twin; for an external path, the rendered facing set is complete
    planned = {r["dest"] for r in rows}
    groups = defaultdict(list)
    for r in rows:
        if r["fix"]:
            groups[(r["dest"].split("/Textures/", 1)[0], r["fix"]["from"], r["fix"]["to"])].append(r)
    repoint, drop = [], set()
    for (mod, frm, to), rs in groups.items():
        fx = rs[0]["fix"]
        if fx["kind"] == "standin":
            sfiles = [k for k in repo.tex if k.startswith(frm) and mod in repo.tex[k]
                      and (k == frm or k[len(frm):][:1] in ("_", "/"))]
            need = [f"{mod}/Textures/{to}{k[len(frm):]}.png" for k in sfiles]
            xmls = sorted(f for f in repo.drawn.get(frm, set()) if not any(f.startswith(n) for n in NO_XML_EDIT))
        else:
            sufs = {re.search(r"(_(north|south|east|west))?$", r["dest"][:-4]).group(0) for r in rs}
            if any("/Textures/" + to + "/" in r["dest"] for r in rs):
                need = []                                # a Random folder: the planned variant(s) are enough
            elif sufs - {""}:
                need = [f"{mod}/Textures/{to}{x}.png" for x in ("_north", "_south", "_east")]
            else:
                need = [f"{mod}/Textures/{to}.png"]
            xmls = fx["xml"]
        missing = [n for n in need if not (REPO / n).is_file() and n not in planned]
        if missing or not xmls:
            why = (f"repoint {frm} -> {to} withheld: {len(missing)} facing/file(s) would be missing"
                   if missing else "no editable XML draws it")
            for r in rs:
                drop.add(r["dest"])
                skipped["repoint incomplete"].append({"dest": r["dest"], "job": r["job"], "why": why})
            continue
        repoint.append({"mod": mod, "kind": fx["kind"], "def": fx.get("def"), "from": frm, "to": to, "xml": xmls})
    rows = [r for r in rows if r["dest"] not in drop]
    # a Graphic_Random folder that gets renders of ours: its remaining donor / placeholder variants are retired
    # (archived in the art store, removed from the folder) so the def no longer rolls a donor picture
    planned = {r["dest"] for r in rows}
    retire = []
    for folder in sorted({r["dest"].rsplit("/", 1)[0] for r in rows if "random_" in r["how"]}):
        left = [q for q in sorted((REPO / folder).glob("*.png")) if str(q.relative_to(REPO)) not in planned]
        for q in left:
            if cls.of(str(q.relative_to(REPO))) in ("DONOR", "PLACEHOLDER"):
                retire.append(str(q.relative_to(REPO)))
    json.dump({"generated": A.now(), "rows": rows, "repoint": repoint, "retire": retire,
               "skipped": {k: v for k, v in skipped.items()},
               "unresolved": {k: v for k, v in unresolved.items()}}, open(out, "w"), indent=1)
    print(f"plan: {len(rows)} installs, {len(repoint)} repoints, {len(retire)} random-folder donor retires; skipped "
          + ", ".join(f"{k}={len(v)}" for k, v in skipped.items())
          + "; unresolved " + ", ".join(f"{k}={len(v)}" for k, v in sorted(unresolved.items(), key=lambda x: -len(x[1]))[:10]))


# ─────────────────────────────────────────────────────────────────── apply ──

def repoint_text(t: str, rp: dict) -> str:
    """Point >from< at >to<: everywhere in the file for a stand-in; inside def rp['def']'s own blocks for an
    external path (a vanilla path other defs of the same file keep drawing)."""
    pat = re.compile(r">\s*" + re.escape(rp["from"]) + r"\s*<")
    if rp["kind"] == "standin":
        return pat.sub(">" + rp["to"] + "<", t)
    out, pos = [], 0
    for m in re.finditer(r"<defName>\s*" + re.escape(rp["def"]) + r"\s*</defName>", t):
        # the enclosing def: the last top-level open tag before the defName, to its matching close
        opens = [o for o in re.finditer(r"^(\s{0,4})<([A-Za-z_.]+)(\s[^>]*)?>\s*$", t[:m.start()], re.M)]
        if not opens:
            continue
        o = opens[-1]
        end = t.find("</" + o.group(2) + ">", m.end())
        if end < 0:
            continue
        out.append(t[pos:o.start()])
        out.append(pat.sub(">" + rp["to"] + "<", t[o.start():end]))
        pos = end
    out.append(t[pos:])
    return "".join(out)


def apply(plan_path: Path, only: str | None, dry: bool):
    P = json.load(open(plan_path))
    log = {"installed": [], "refused": [], "already": [], "owner_words": []}
    for r in P["rows"]:
        if only and only not in r["dest"]:
            continue
        data = Path(r["png"]).read_bytes()
        prov = {"kind": "artpipe", "job": r["job"], "accepted_for_now": True, "owner_said": OWNER_SAID,
                "relayed_by": "FOUNDRY coordinator"}
        mod, rel = A.locate(REPO / r["dest"])
        if dry:
            continue
        sha = A.store_put_bytes(data)
        try:
            res = A.install(mod, rel, sha, reason=REASON, provenance=prov)
        except A.Refused as e:
            msg = str(e)
            if any(w in msg for w in ("owner-KEPT", "REJECTED", "redo", "purged by the owner (since unpurged")):
                try:
                    res = A.install(mod, rel, sha, owner_said=OWNER_SAID, provenance=prov)
                    log["owner_words"].append(r["dest"])
                except A.Refused as e2:
                    log["refused"].append({"dest": r["dest"], "job": r["job"], "why": str(e2)})
                    continue
            else:
                log["refused"].append({"dest": r["dest"], "job": r["job"], "why": msg})
                continue
        if res.get("status") == "already-live":
            log["already"].append(r["dest"])
            continue
        log["installed"].append(r["dest"])
        rec = {"job_id": r["job"], "dest": r["dest"], "sha256": sha_of(REPO / r["dest"]),
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "clone": str(REPO), "host": socket.gethostname(),
               "via": "bulk_accept_renders.py", "accepted_for_now": True, "owner_said": OWNER_SAID,
               "relayed_by": "FOUNDRY coordinator"}
        with (ART / "collected.jsonl").open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    if not dry:
        done = set(log["installed"]) | set(log["already"])
        for x in P.get("retire", []):
            if only and only not in x:
                continue
            folder = x.rsplit("/", 1)[0]
            if not any(d.startswith(folder + "/") for d in done):
                continue                                 # nothing of ours went into that folder after all
            try:
                A.retire(REPO / x, reason=REASON)
                log.setdefault("retired", []).append(x)
            except A.Refused as e:
                log["refused"].append({"dest": x, "job": None, "why": "retire: " + str(e)})
        for rp in P["repoint"]:
            if only and only not in rp["mod"]:
                continue
            for x in rp["xml"]:
                p = REPO / x
                t = p.read_text(encoding="utf-8")
                n = repoint_text(t, rp)
                if n != t:
                    p.write_text(n, encoding="utf-8")
                    log.setdefault("repointed", []).append(x)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in log.items()}))
    out = plan_path.with_suffix(f".applied{('.' + re.sub(r'[^A-Za-z0-9]', '_', only)) if only else ''}.json")
    json.dump(log, open(out, "w"), indent=1)
    print("log:", out)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("plan")
    a.add_argument("--out", required=True, type=Path)
    b = sp.add_parser("apply")
    b.add_argument("--plan", required=True, type=Path)
    b.add_argument("--only")
    b.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "plan":
        plan(args.out)
    else:
        apply(args.plan, args.only, args.dry_run)


if __name__ == "__main__":
    main()
