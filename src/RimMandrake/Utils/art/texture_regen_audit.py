#!/usr/bin/env python3
"""texture_regen_audit.py — is each biome's art OUR regenerated art, or donor / placeholder / borrowed?
(owner 2026-10-18: "Ensure the biome textures have been regenerated.")  READ-ONLY: writes only --out JSON.

    python3 src/RimMandrake/Utils/art/texture_regen_audit.py --census <census.json> --out <audit.json> [--md <tables.md>]

Two views, both classified by the SHA-256 of the picture on disk looked up in the art ledger (artledger.Index):
  A. ROSTER view  — every flora/fauna/fish row of every RM_ biome (biome_census.py output, re-run first: dumps decay).
  B. DEF view     — every non-abstract def of every Baroque Biomes compose entry (and the twin mods) that declares a
                    texture path (texPath / texturePath / uiIconPath / wornGraphicPath / flying frame prefixes), including
                    terrain, buildings, items, icons — by parsed XML, not text match.
File classes (first match wins):
  PLACEHOLDER   placeholder_detect: FLAT (<=8 colours, smooth), GEOMETRIC (ellipse/rectangle), or BORROWED (row view)
  DONOR         the exact bytes are a donor/vanilla extract in the ledger (kind donor)
  REGEN         bytes are an artpipe render (kind artpipe) or went in through `art install` / artpipe-collect
  DERIVED       bytes came from one of our scripts (kind derived / live reason script:*) — flips, mirrors, compositing
  UNPROVEN      in the repo, but the ledger holds no artpipe/install/donor record of those bytes (hand-made, legacy, or
                an unregistered copy): provenance UNMEASURED, NOT counted as regenerated
A def with no file in any src/ Textures is EXTERNAL (vanilla Core/DLC or a donor mod's own folder) — counted as
vanilla-or-donor borrowed, never ours. Def class = worst of its files: PLACEHOLDER > DONOR > UNPROVEN > DERIVED > REGEN.
Not measured (named in the output): defs whose texPath is inherited from a ParentName; graphics set in C#.
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A            # noqa: E402
import placeholder_detect as PD  # noqa: E402

REPO = HERE.parents[3]
SRC = REPO / "src"
TAGS = {"texPath", "texturePath", "uiIconPath", "wornGraphicPath", "flyingAnimationFramePathPrefix",
        "flyingAnimationFramePathPrefixFemale", "iconPath", "graphicPath"}
ORDER = ["PLACEHOLDER", "DONOR", "UNPROVEN", "DERIVED", "REGEN"]


def sha_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Classifier:
    def __init__(self):
        self.idx = A.Index()
        self.cache = {}

    def kinds(self, sha):
        return {v.get("kind") for v in self.idx.variants.get(sha, ())}

    def file_class(self, p: Path, mod_rel=None):
        if p in self.cache:
            return self.cache[p]
        sha = sha_of(p)
        try:
            flat = PD.pixel_metrics(p)
            ph = (flat and PD.is_flat(flat)) or PD.is_placeholder(p)
        except Exception:                       # unreadable -> never "real"
            ph = None
        ks = self.kinds(sha)
        live_reason = None
        if mod_rel:
            ev = self.idx.live.get(mod_rel)
            if ev and ev.get("sha") == sha:
                live_reason = ev.get("reason") or ""
        if ph is None:
            c = "UNPROVEN"
        elif ph:
            c = "PLACEHOLDER"
        elif "donor" in ks:
            c = "DONOR"
        elif "artpipe" in ks or "install" in ks or (live_reason or "").startswith(("install", "artpipe-collect")):
            c = "REGEN"
        elif "derived" in ks or (live_reason or "").startswith("script"):
            c = "DERIVED"
        else:
            c = "UNPROVEN"
        sub = ("donor+artpipe" if c == "DONOR" and "artpipe" in ks else "")
        self.cache[p] = (c, sub, sha)
        return self.cache[p]


def is_mask(stem: str) -> bool:
    return stem.endswith("_m") or bool(re.search(r"_(north|east|south|west)m$", stem))


def texture_roots():
    return sorted(p for p in SRC.glob("*/*/Textures") if p.is_dir())


def resolve_files(res: str, own_root: Path | None, roots):
    """PNG files the game could draw for texPath `res` (non-mask). Own mod first, then any other src mod."""
    for r in ([own_root] if own_root else []) + [x for x in roots if x != own_root]:
        base = r / res
        found = []
        if base.is_dir():
            found = [q for q in base.glob("*.png") if not is_mask(q.stem)]
        else:
            for suf in ("", "_north", "_east", "_south", "_west", "_a", "A", "_0"):
                q = Path(str(base) + suf + ".png")
                if q.is_file():
                    found.append(q)
        if found:
            return r, sorted(set(found))
    return None, []


def def_slots(folder: Path):
    """[(defName, [texPaths])] for every non-abstract def under folder's Defs (parsed XML)."""
    out = []
    for f in folder.rglob("*.xml"):
        sp = str(f)
        if "/Defs/" not in sp:
            continue
        try:
            root = ET.parse(f).getroot()
        except (ET.ParseError, OSError):
            continue
        for d in root:
            dn = d.find("defName")
            if dn is None or not (dn.text or "").strip() or d.get("Abstract", "").lower() == "true":
                continue
            tps = []
            for el in d.iter():
                if isinstance(el.tag, str) and el.tag in TAGS and (el.text or "").strip() and not list(el):
                    tps.append(el.text.strip())
            if tps:
                out.append((dn.text.strip(), d.tag, sorted(set(tps)), str(f.relative_to(REPO))))
    return out


def audit_defs(cl: Classifier, folder: Path):
    roots = texture_roots()
    own = folder / "Textures"
    own = own if own.is_dir() else None
    rows = []
    for dn, tag, tps, f in def_slots(folder):
        classes, subs, ext = [], [], 0
        nfiles = 0
        first_tex = None
        for tp in tps:
            r, files = resolve_files(tp, own, roots)
            if not files:
                ext += 1
                continue
            for q in files:
                mod_rel = None
                if r:
                    m = str(r.parent.relative_to(REPO)).replace("\\", "/")
                    mod_rel = (A.mod_key(m), A.rel_key(str(q.relative_to(r))))
                first_tex = first_tex or str(q.relative_to(REPO))
                c, sub, _ = cl.file_class(q, mod_rel)
                classes.append(c)
                subs.append(sub)
                nfiles += 1
        if classes:
            worst = min(classes, key=ORDER.index)
        else:
            worst = "EXTERNAL"
        rows.append({"def": dn, "type": tag, "file": f, "texPaths": tps, "class": worst, "files": nfiles, "tex": first_tex,
                     "file_classes": dict(Counter(classes)), "ext_texpaths": ext,
                     "sub": "donor+artpipe" if "donor+artpipe" in subs else ""})
    return rows


def audit_roster(cl: Classifier, census_path: Path):
    census = json.load(open(census_path))
    shared = PD.shared_map(census)
    donor_pk = {}
    out = {}
    for bd in census["biome_order"]:
        rows = []
        for r in census["biomes"][bd]["rows"]:
            dn = (r.get("defNames") or [r["key"]])[0]
            pc = PD.classify_row(r, shared)
            classes, ext = [], False
            bodies = [x for x in r["art"]["resources"] if x.get("role") == "body"] or r["art"]["resources"]
            for x in bodies:
                lv = x.get("live")
                if not lv:
                    continue
                mod = lv["mod"]
                for face, sha in (lv.get("faces") or {}).items():
                    ks = cl.kinds(sha)
                    # reuse the file-level rule through the sha (placeholder decided at row level below)
                    if "donor" in ks:
                        classes.append("DONOR")
                    elif "artpipe" in ks or "install" in ks:
                        classes.append("REGEN")
                    elif "derived" in ks:
                        classes.append("DERIVED")
                    else:
                        classes.append("UNPROVEN")
            has_art = any(v["kind"] == "artpipe" for x in r["art"]["resources"] for v in x["versions"])
            donor_only = any(v["kind"] == "donor" for x in r["art"]["resources"] for v in x["versions"])
            if pc["verdict"] == "PLACEHOLDER":
                borrowed = any("BORROWED" in z and "vanilla" in z for z in pc["reasons"])
                cls = "VANILLA_BORROWED" if borrowed else "PLACEHOLDER"
            elif classes:
                cls = min(classes, key=ORDER.index)
            else:
                cls = "NO_LIVE_DONOR_ONLY" if donor_only else "NO_LIVE_ART"
            vs = [v for x in r["art"]["resources"] for v in x["versions"] if v["kind"] == "artpipe"]
            gapkind = ("bound-render" if any("not bound" not in v["detail"] for v in vs) else
                       "name-joined-render" if vs else "state-job" if r.get("artpipe_state_jobs") else "none-in-census")
            rows.append({"row": r["key"], "defName": dn, "kind": r["kind"], "class": cls, "gapkind": gapkind,
                         "placeholder_reasons": pc["reasons"] if pc["verdict"] == "PLACEHOLDER" else [],
                         "ledger_artpipe_render": has_art,
                         "artpipe_state_jobs": len(r.get("artpipe_state_jobs") or []),
                         "res": [x["res"] for x in bodies]})
        out[bd] = rows
    return out, census.get("sanity_probe", {})


# ───────────────────────────────────────────────── gap evidence + job filing ──
ART = Path(rm_str("artpipe"))


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


class Evidence:
    """Is there ANY render of ours / owner sheet decision / commit citing an install, for a stem?"""

    def __init__(self):
        self.names = [(d, _norm(n)) for d in ("done", "pending", "active", "failed", "_artsrc")
                      for n in __import__("os").listdir(ART / d)]
        import glob
        self.dec = _norm("".join(open(f, errors="ignore").read() for f in glob.glob(str(REPO / "Transient/**/*.decisions.json"), recursive=True)))
        # sanity probes: the instrument must see known-present stems
        self.probe = {"korrum": self.render_dirs("korrum"), "giantleaf": self.render_dirs("giantleaf")}
        assert all(self.probe.values()), f"evidence instrument blind: {self.probe}"

    def render_dirs(self, stem):
        s = _norm(stem)
        return sorted({d for d, n in self.names if s in n}) if len(s) >= 4 else []

    def in_sheet_decisions(self, stem):
        return len(_norm(stem)) >= 5 and _norm(stem) in self.dec

    @staticmethod
    def commit_cites_install(path):
        import subprocess
        out = subprocess.run(["git", "-C", str(REPO), "log", "-6", "--format=%s", "--", str(path)],
                             capture_output=True, text=True).stdout.lower()
        return any(w in out for w in ("art install", "installed", "regen", "artpipe", "render", "sheet", "redo", "pick"))


def stem_of(defname):
    return re.sub(r"(Juv|Catch)$", "", re.sub(r"^(RM|RSW|RUT)_", "", defname))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cl = Classifier()
    compose = json.load(open(SRC / "RimMandrake/Biomes.compose.json"))
    defs = {}
    for e in compose["entries"]:
        folder = SRC / "RimMandrake" / e["source"]
        if folder.is_dir():
            defs[e["key"]] = {"group": e["group"], "source": e["source"], "rows": audit_defs(cl, folder)}
    for tw in ("RimUtinni/UtinniPatches", "RimStarWars/SWBestiary", "RimStarWars/NunaArtOverride",
               "RimStarWars/AnoobaArtOverride"):
        folder = SRC / tw
        if folder.is_dir():
            defs["TWIN:" + tw] = {"group": "twin", "source": tw, "rows": audit_defs(cl, folder)}
    roster, probe = audit_roster(cl, Path(a.census))
    ev = Evidence()
    for bd, rows in roster.items():
        for r in rows:
            st = stem_of(r["defName"])
            r["render_dirs"] = ev.render_dirs(st)
            r["sheet_decided"] = ev.in_sheet_decisions(st)
    for k, v in defs.items():
        for r in v["rows"]:
            if r["class"] in ("PLACEHOLDER", "DONOR", "UNPROVEN"):
                st = stem_of(r["def"])
                r["render_dirs"] = ev.render_dirs(st)
                r["sheet_decided"] = ev.in_sheet_decisions(st)
                if r["class"] == "UNPROVEN":
                    r["commit_cites_install"] = bool(r["tex"]) and ev.commit_cites_install(REPO / r["tex"])
    json.dump({"generated": A.now(), "git_head": __import__("subprocess").run(
        ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "ledger_variants": len(cl.idx.variants), "census_sanity_probe": probe,
        "evidence_probe": ev.probe, "defs": defs, "roster": roster}, open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
