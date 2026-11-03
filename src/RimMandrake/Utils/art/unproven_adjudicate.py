#!/usr/bin/env python3
"""unproven_adjudicate.py — where did live art with NO pipeline record come from?  (TEXREGEN_UNPROVEN_ASK_THE_SHEETS)

texture_regen_audit.py classes a picture UNPROVEN when its exact bytes carry no artpipe / install / donor / derived
record in the art ledger. This tool adjudicates each such picture into one verdict, with the evidence named:

  OURS_RESAVED   a near-duplicate (dhash <= DHASH_MAX) of one of OUR renders or installs: a rescale / re-save of
                 pipeline art whose new bytes were never recorded (the 2026-10-16 facing rescale is the known cause).
  OURS_PRELEDGER our image-model art from before the art ledger tracked bytes (SW_SEA_MONSTERS_ART_1, early render
                 waves): ours and generated, but no render record to bind it to.
  STAND_IN       a near-duplicate of a donor or vanilla extract, or brought in by a commit that says it copied donor /
                 Core art or a placeholder. Not ours.
  OWNER_PICKED   the bytes commit says the owner kept / approved / locked this picture or its mockup, or (weakest,
                 last) the stem was ruled on in a review sheet's *.decisions.json.
  HAND_MADE      drawn or composed by an agent or script (no render, no donor twin).
  UNRESOLVED     none of the above: must go to a sheet.

Provenance = the commit that first brought TODAY'S BYTES into the repo (git blob id, across moves and copies, looking
past mechanical re-saves in PASS_THROUGH); BYTES_RULES records what each such commit's message says, read by hand.

    python3 src/RimMandrake/Utils/art/unproven_adjudicate.py --audit <audit.json>     write the adjudication
    python3 src/RimMandrake/Utils/art/unproven_adjudicate.py --check                  exit 0 iff every UNPROVEN
                                                                                       no-record file, measured now,
                                                                                       has a verdict on record

The def view is re-measured in --check (parsed XML + ledger sha lookup, ~15 s); the census-based roster view
is read from the audit given at write time. A dhash match is a comparison aid, so its threshold is measured each
write (calibrate(): rescaled renders vs chance nearest neighbours) — see DHASH_MAX.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A                 # noqa: E402
import texture_regen_audit as T       # noqa: E402

REPO = HERE.parents[3]
OUT_JSON = REPO / "design/RimMandrake/texregen_unproven_adjudication.json"
OUT_MD = REPO / "design/RimMandrake/texregen_unproven_adjudication.md"
OURS = {"artpipe", "install"}
DONORISH = {"donor", "canon"}
DHASH_MAX = 10          # of 256 bits; calibrate() re-measures each write: LANCZOS resaves of ledger renders sit at p99 ~7-8,
                        # and 40 (tried first) mostly matched chance. A dhash hit is only a candidate: mad() confirms it
VERDICTS = ("OURS_RESAVED", "OURS_PRELEDGER", "STAND_IN", "OWNER_PICKED", "HAND_MADE", "UNRESOLVED")
# The commit that first brought today's bytes into the repo (PngHistory.bytes_commit), read by hand: what that
# commit's own message says the picture IS. Keyed by the first 10 hex of the sha.
S, P, O, H = "STAND_IN", "OURS_PRELEDGER", "OWNER_PICKED", "HAND_MADE"
BYTES_RULES = {
    "891c0c76ee": (S, "BMT_FAUNA_ABSORPTION_1: script port of 68 biomesteam creatures with the donor mods' own art"),
    "b544ff05fb": (S, "BMT_FAUNA_ABSORPTION_1: Rocktooth/Boneblade, 'art copied under swanimals/BiomesTeam/'"),
    "1213bd07b8": (S, "FUNGALFOREST_RAID_MERGE_1: spore kit 'with real art copied from the donor's live Workshop install'"),
    "ae40b6b241": (S, "KOTORCORE_ABSORPTION_MISSING_TEXTURES_1: 'Copied the real PNGs from those donor-adjacent mods'"),
    "e3737f3a9e": (S, "STAT_NORM_WAVE2_RETIRE_1: port of Cephaloids / VE Succulents / VAE Waste content with its art"),
    "589fecf3f2": (S, "POLLUTED_LANDS_FLORA_PORT_1: 'art copied from the live Workshop install'"),
    "58020220bb": (S, "RSW_Maguana port: 'Donor art accepted without review on owner ruling'"),
    "1f993c3fc3": (S, "FILTH_ON_NATURAL_TERRAIN_NOOP_1: 'real Core dung-tinted art, copied under this mod's own Textures/'"),
    "8062d94d32": (S, "SHRUBLAND_SCRAPNEST_BIRDS_1: 'Art/body reuses RSW_Whisperbird's under a new defName and retint'"),
    "60dfa5177c": (S, "FOOTPRINT_TRACK_GRID_1: 'print art is placeholder (artpipe jobs pending)'"),
    "cd06277d89": (S, "Stillsand caves: 'wall and glyph art are placeholders, jobs queued'"),
    "23b12670b3": (P, "SW_SEA_MONSTERS_ART_1: image-model sea-beast art (scavenger swarm, reefback) before the art ledger"),
    "853261aa72": (P, "SW_SEA_MONSTERS_ART_1: image-model scalefish (mee, faa, laa) before the art ledger"),
    "43c20c453e": (P, "SW_SEA_MONSTERS_ART_1: image-model ThornbackColo facings before the art ledger"),
    "fd3439b596": (P, "SeaBeasts: Starmaw and Lanternwhale generated (codex $imagegen) before the art ledger"),
    "4202352cf5": (P, "Opee sprite pilot output (SW_SEA_MONSTERS_ART_1 toolchain) before the art ledger"),
    "040c99f685": (P, "SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1: 'Generated original 512x512 art for both'"),
    "d556f6b757": (P, "ART_PAINTERLY_RESTORATION_1: EmberGrass 'repainted painterly (Codex)'"),
    "9d4ea39838": (P, "'Wire finished renders' (Foundry tower entrance, salvage cache)"),
    "a43c1f0109": (P, "ART_REGEN_WAVE4 renders wired"),
    "a9ad6a949e": (P, "Art-review platform: 'install every gate-passed render awaiting verdict'"),
    "42cd4d2089": (P, "Pyrelands full-review art wave: painterly renders"),
    "f6c01bf661": (P, "art review sheet 2026-09-12: validated creature renders (bytes entered with the sheet)"),
    "cc9c150901": (P, "POISONFOREST_RM_MOD_BUILD_1: DarkCrust 'copied ... from the already-generated rutdarkcrust_v1'"),
    "987e369fb0": (P, "CAVERNS_PARITY_BUILD_1 wall atlases: 'RGB 100% generated', donor alpha as layout only (owner card)"),
    "0d1a84cf57": (P, "DEEP_FLORA_RENAME_1: twitching puffer v2 art wired (renders, purple-tinted)"),
    "57dd8e8879": (O, "SW_SEA_MONSTERS_ART_1: crimson opee, 'west IS the owner's kept mockup'"),
    "ee57eaf398": (O, "SW_SEA_MONSTERS_ART_1: ShaleGorger 'Four facings from the owner's kept mockup'"),
    "b998d027f4": (O, "SW_SEA_MONSTERS_ART_1: ColoClawFish 'Four facings from the owner's kept mockup'"),
    "37a31bab8e": (O, "SW_SEA_MONSTERS_ART_1: abyssal colo + sandos from 'kept mockups'"),
    "de490265d3": (O, "FORSAKEN_CRAGS_PREDATORS_BUILD_1: 'Art is the owner-approved mockup itself'"),
    "02ab863c09": (O, "Lantern Deeps art wired; owner 2026-09-18: 'We approve all of the art review of Lantern deeps!'"),
    "8bc82c5d6d": (O, "Scorch-fruit candidates for owner review; 0da8422dfc ships the four per his sheet ruling"),
    "cec36a2f0b": (O, "Gizka: 'dino_v5 is the locked set (owner, 2026-09-17)'"),
    "f4b6a37918": (O, "Onnik: 'a generated body sprite conformed from the owner's picked mockup'"),
    "fd81873d50": (O, "Moornak, the trio's third entry built the same way as onnik (owner-picked mockup)"),
    "42b40b2ae2": (O, "Long Shade: 'the 7 owner-kept fills'"),
    "79f3454dc5": (H, "GREATBOLE_BARK_EDGE_ART_1: bespoke atlas built cell-for-cell against vanilla Rock_Atlas"),
    "27b87b5608": (H, "faction marks built from the owner's references, then ring-carved by hand"),
    "9cabd9ff93": (H, "Jawa faction icon redrawn (face in shadow) from the owner's reference"),
}
# Pictures whose bytes commit says nothing about the art; judged by looking (contact sheet in the audit scratch).
FILE_RULES = {
    "src/RimMandrake/Abyss/Textures/RM_Abyss/Terrains/EtchHollow.png":
        (H, "script-drawn dark noise, 11 colours: a placeholder in effect (ef61e507f2 names no source)"),
    "src/RimMandrake/TheSump/Textures/Things/Item/Resource/RM_TarGas/RM_TarGas.png":
        (H, "script-drawn green blobs, 6 colours: a placeholder in effect (a86443642b names no source)"),
    "src/RimMandrake/Contagion/Textures/Things/Item/Equipment/RM_Sunbeam.png":
        (P, "image-model style, 12k colours (248f24a28c); no render of it in the artpipe state"),
    "src/RimMandrake/Contagion/Textures/Things/Item/Health/RM_LashItem.png":
        (P, "image-model style; dhash 17 from our RM_LashA_east render, the same lash (e0823872a5)"),
}


def no_record_files(cl):
    """[(group_key, defName, file Path, sha)] for every UNPROVEN file of every def the audit's def view walks."""
    compose = json.load(open(T.SRC / "RimMandrake/Biomes.compose.json"))
    folders = [(e["key"], T.SRC / "RimMandrake" / e["source"]) for e in compose["entries"]]
    folders += [("TWIN:" + tw, T.SRC / tw) for tw in ("RimUtinni/UtinniPatches", "RimStarWars/SWBestiary",
                                                       "RimStarWars/NunaArtOverride", "RimStarWars/AnoobaArtOverride")]
    roots = T.texture_roots()
    out = []
    for key, folder in folders:
        if not folder.is_dir():
            continue
        own = folder / "Textures"
        own = own if own.is_dir() else None
        for dn, _tag, tps, _f in T.def_slots(folder):
            for tp in tps:
                r, files = T.resolve_files(tp, own, roots)
                for q in files:
                    m = str(r.parent.relative_to(REPO)).replace("\\", "/")
                    mod_rel = (A.mod_key(m), A.rel_key(str(q.relative_to(r))))
                    sha = T.sha_of(q)
                    if cl.kinds(sha) & (OURS | DONORISH | {"derived"}):
                        continue        # any record of these bytes: not UNPROVEN, skip the slow pixel read
                    c, _sub, sha = cl.file_class(q, mod_rel)
                    if c == "UNPROVEN":
                        out.append((key, dn, q, sha))
    return out


MAD_MAX = 1.5           # mean |RGB diff| /255 at 32x32 over grey. Measured: a 1/2 LANCZOS rescale p99 0.53, max 0.55;
                        # unrelated ledger renders p01 2.2; the dhash-7 chance hit (a spore item vs RM_Eesh) 6.3


def _vec(png_bytes):
    import io
    import numpy as np
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    bg = Image.new("RGBA", im.size, (128, 128, 128, 255))
    bg.alpha_composite(im)
    return np.asarray(bg.convert("RGB").resize((32, 32), Image.LANCZOS), dtype=float)


def mad(a_bytes, b_bytes):
    return float(abs(_vec(a_bytes) - _vec(b_bytes)).mean())


class Neighbours:
    """dhash near-duplicates in the ledger, each CONFIRMED by pixels (dhash alone collides on small blob-on-alpha
    pictures). `_artsrc/` entries are left out: they are artpipe job INPUTS (often the donor picture itself), not
    renders of ours."""

    def __init__(self, idx):
        self.pool = []          # (int dhash, kind, loc, sha)
        for sha, vs in idx.variants.items():
            for v in vs:
                loc = v.get("loc") or v.get("res") or sha
                if v.get("ph") and v.get("kind") in OURS | DONORISH and "_artsrc/" not in loc:
                    self.pool.append((int(v["ph"], 16), v["kind"], loc, sha))

    def nearest(self, ph_hex, kinds, png_bytes=None):
        """(dhash d, kind, loc, sha, mad) of the closest pixel-confirmed match within DHASH_MAX, else the closest
        dhash candidate with mad None (evidence only, never a match)."""
        x = int(ph_hex, 16)
        cands = sorted((bin(x ^ h).count("1"), k, loc, sha) for h, k, loc, sha in self.pool if k in kinds)
        for d, k, loc, sha in cands:
            if d > DHASH_MAX or png_bytes is None:
                break
            try:
                m = mad(png_bytes, A.store_get(sha))
            except Exception:
                continue
            if m <= MAD_MAX:
                return (d, k, loc, sha, round(m, 2))
        return (cands[0] + (None,)) if cands else None


# Commits that re-saved pictures mechanically (each read by hand): the picture's provenance is the commit before.
PASS_THROUGH = {
    "8615f77098": "art: zero the sub-visible export halo across 241 of our facing sprites",
    "50d116b0d7": "NONDIV4_TEXTURE_FIX_1: pad 87 non-%4 textures (transparent, centered)",
    "3ce74b0946": "CAVERNS_PARITY_BUILD_1: Deep organics hue-tinted +70 deg (same picture, recoloured)",
}


class PngHistory:
    """Where did today's exact bytes first enter the repo? Keyed by git BLOB id, from ONE `git log --raw` over every
    PNG (~10 s): a blob's oldest introduction is its source, across moves AND copies (a retier or an "own it as RM_"
    commit copies RSW_ art under a new name; rename detection alone calls that a fresh add). A per-file --follow
    costs minutes and misses copies; the FIRST add of a path is wrong too — many pictures were replaced later."""

    def __init__(self):
        txt = subprocess.run(["git", "-C", str(REPO), "log", "--raw", "--no-abbrev", "--no-renames",
                              "--format=@@%H %ad %s", "--date=short", "--", "*.png"],
                             capture_output=True, text=True).stdout
        self.first = {}            # blob -> (commit line, status, old blob); oldest wins (log is newest first)
        self.by_path = {}          # path -> [commit lines] newest first
        cur = None
        for line in txt.splitlines():
            if line.startswith("@@"):
                cur = line[2:]
            elif line.startswith(":") and cur:
                meta, path = line.split("\t", 1)
                _m1, _m2, old, new, st = meta[1:].split()
                self.by_path.setdefault(path, []).append(cur)
                if st[:1] in "AM":
                    self.first[new] = (cur, st, old)
        ls = subprocess.run(["git", "-C", str(REPO), "ls-files", "-s", "--", "*.png"], capture_output=True,
                            text=True).stdout
        self.blob = {ln.split("\t", 1)[1]: ln.split()[1] for ln in ls.splitlines() if "\t" in ln}

    def bytes_commit(self, rel: str):
        b = self.blob.get(rel)
        for _ in range(20):
            e = self.first.get(b)
            if not e:
                return ""
            cur, st, old = e
            if cur[:10] in PASS_THROUGH and st == "M" and old.strip("0"):
                b = old                         # a mechanical re-save: provenance is the picture before it
                continue
            return cur
        return ""

    def commits(self, rel):
        return self.by_path.get(rel, [])[:4]


def decision_text():
    return T._norm("".join(open(f, errors="ignore").read()
                           for f in glob.glob(str(REPO / "Transient/**/*.decisions.json"), recursive=True)))


def stems_for(dn, path):
    """Owner-sheet stems: the defName stem and the texture's file stem (>=5 normalised chars, as the audit uses)."""
    s = {T._norm(T.stem_of(dn)), T._norm(re.sub(r"_(north|south|east|west|[a-z]|\d+)$", "", path.stem, flags=re.I))}
    return [x for x in s if len(x) >= 5]


def adjudicate_one(dn, path, sha, nb, dec, hist):
    """Direct evidence about THESE bytes first (the commit that brought them in, then a per-file look), similarity
    second (a pixel-confirmed near-duplicate), the sheet stem last."""
    raw = path.read_bytes()
    ph, w, h = A.dhash(raw)
    ours = nb.nearest(ph, OURS, raw)
    donor = nb.nearest(ph, DONORISH, raw)
    rel = str(path.relative_to(REPO))
    add, commits = hist.bytes_commit(rel), hist.commits(rel)
    sheet = [s for s in stems_for(dn, path) if s in dec]
    ev = {"ph": ph, "size": [w, h], "bytes_commit": add, "commits": commits,
          "nearest_ours": ours and {"d": ours[0], "kind": ours[1], "loc": ours[2], "mad": ours[4]},
          "nearest_donor": donor and {"d": donor[0], "kind": donor[1], "loc": donor[2], "mad": donor[4]},
          "sheet_stems": sheet}
    o_ok = bool(ours and ours[4] is not None)
    d_ok = bool(donor and donor[4] is not None)
    if add[:10] in BYTES_RULES:
        v, why = BYTES_RULES[add[:10]][0], f"bytes from {add[:10]}: {BYTES_RULES[add[:10]][1]}"
    elif rel in FILE_RULES:
        v, why = FILE_RULES[rel]
    elif o_ok and (not d_ok or ours[0] <= donor[0]):
        v, why = "OURS_RESAVED", f"dhash {ours[0]}/256, pixel MAD {ours[4]} from our {ours[1]} {ours[2]}"
    elif d_ok:
        v, why = "STAND_IN", f"dhash {donor[0]}/256, pixel MAD {donor[4]} from {donor[1]} extract {donor[2]}"
    elif sheet:
        v, why = "OWNER_PICKED", f"stem {sheet[0]!r} ruled in a review sheet's decisions.json"
    else:
        v, why = "UNRESOLVED", "no rule for its bytes commit, no confirmed near-duplicate, no sheet ruling"
    return v, why, ev


def calibrate(idx, n=150):
    """Measure DHASH_MAX instead of choosing it: (a) distance between a ledger render and its own LANCZOS rescale
    to 1/2 and 3/4 (the same picture re-saved, what OURS_RESAVED must catch); (b) the nearest-neighbour distance
    from a ledger picture to every OTHER-res picture in the pool (what chance alone reaches)."""
    import io
    import random
    from PIL import Image
    pool = []
    for sha, vs in idx.variants.items():
        v = next((v for v in vs if v.get("ph") and v.get("kind") in OURS | DONORISH), None)
        if v:
            pool.append((int(v["ph"], 16), v.get("res"), sha))
    random.seed(3)
    samp = random.sample(pool, min(n, len(pool)))
    resave, null = [], []
    for h, res, sha in samp:
        null.append(min(bin(h ^ x).count("1") for x, r, s in pool if s != sha and r != res))
        try:
            im = Image.open(io.BytesIO(A.store_get(sha))).convert("RGBA")
        except Exception:
            continue
        for f in (0.5, 0.75):
            o = io.BytesIO()
            im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.LANCZOS).save(o, "PNG")
            resave.append(A.hamming(A.dhash(o.getvalue())[0], f"{h:064x}"))
    q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))] if xs else None  # noqa: E731
    return {"resave": {"n": len(resave), "p50": q(resave, .5), "p99": q(resave, .99), "over_max": sum(x > DHASH_MAX for x in resave)},
            "nearest_other_res": {"n": len(null), "p05": q(null, .05), "p10": q(null, .1), "p50": q(null, .5),
                                  "at_or_under_max": sum(x <= DHASH_MAX for x in null)}}


def write(audit_path):
    idx = A.Index()
    cl = T.Classifier()
    cl.idx = idx
    nb = Neighbours(idx)
    dec = decision_text()
    files = no_record_files(cl)
    audit = json.load(open(audit_path))
    hist = PngHistory()
    rows = []
    for key, dn, q, sha in files:
        v, why, ev = adjudicate_one(dn, q, sha, nb, dec, hist)
        rows.append({"group": key, "def": dn, "file": str(q.relative_to(REPO)), "sha": sha, "verdict": v,
                     "why": why, "evidence": ev})
    by_file = {}
    for r in rows:
        by_file.setdefault(r["file"], r)
    roster = []
    for bd, rr in audit["roster"].items():
        for r in rr:
            if r["class"] == "UNPROVEN" and not r.get("sheet_decided"):
                fs = sorted({f["file"] for f in rows if f["def"] == r["defName"]})
                roster.append({"biome": bd, "def": r["defName"], "files": fs,
                               "verdicts": sorted({by_file[f]["verdict"] for f in fs})})
    vd = {}
    for r in rows:
        vd.setdefault(r["def"], set()).add(r["verdict"])
    rejudge = {"defs": Counter(), "roster": Counter()}
    for v in audit["defs"].values():
        for r in v["rows"]:
            if r["class"] == "UNPROVEN" and r.get("sheet_decided"):
                rejudge["defs"][" + ".join(sorted(vd.get(r["def"], {"not in the def view"})))] += 1
    for rr in audit["roster"].values():
        for r in rr:
            if r["class"] == "UNPROVEN" and r.get("sheet_decided"):
                rejudge["roster"][" + ".join(sorted(vd.get(r["defName"], {"not in the def view"})))] += 1
    doc = {"generated": A.now(), "git_head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                                                            capture_output=True, text=True).stdout.strip(),
           "audit": str(audit_path), "dhash_max": DHASH_MAX, "calibration": calibrate(idx),
           "counts": dict(Counter(r["verdict"] for r in rows)),
           "counts_by_group": {g: dict(Counter(r["verdict"] for r in rows if r["group"] == g))
                               for g in sorted({r["group"] for r in rows})},
           "sheet_decided_rejudged": {k: dict(c) for k, c in rejudge.items()},
           "files": rows, "roster": roster}
    OUT_JSON.write_text(json.dumps(doc, indent=1) + "\n")
    OUT_MD.write_text(render_md(doc))
    print("wrote", OUT_JSON, doc["counts"])
    return doc


def render_md(doc):
    L = ["# Live art with no pipeline record, adjudicated (TEXREGEN_UNPROVEN_ASK_THE_SHEETS)", "",
         f"Generated {doc['generated']} at `{doc['git_head']}` by `src/RimMandrake/Utils/art/unproven_adjudicate.py` "
         f"from `{doc['audit']}`. Data: `design/RimMandrake/texregen_unproven_adjudication.json`. Every picture the "
         "texture audit classes UNPROVEN (no artpipe / install / donor / derived record of its exact bytes) gets one "
         "verdict, keyed on the commit that first brought those bytes into the repo. Verdict meanings: the tool's "
         "docstring.", "",
         f"dhash threshold {doc['dhash_max']}/256, measured: `{json.dumps(doc['calibration'])}`", "",
         "| verdict | pictures |", "|---|---|"]
    L += [f"| {v} | {doc['counts'].get(v, 0)} |" for v in VERDICTS]
    L += ["", "## By mod", "", "| mod | " + " | ".join(VERDICTS) + " |", "|---|" + "---|" * len(VERDICTS)]
    for g, c in doc["counts_by_group"].items():
        L.append(f"| {g} | " + " | ".join(str(c.get(v, 0)) for v in VERDICTS) + " |")
    L += ["", "## Where the bytes came from", "", "| pictures | verdict | evidence |", "|---|---|---|"]
    key = lambda r: ("dhash <= %d/256 from %s" % (DHASH_MAX, "our render" if r["verdict"] == "OURS_RESAVED"  # noqa: E731
                                                   else "a donor/vanilla extract")) if r["why"].startswith("dhash") else r["why"]
    for (v, why), n in Counter((r["verdict"], key(r)) for r in doc["files"]).most_common():
        L.append(f"| {n} | {v} | {why.replace('|', '/')} |")
    L += ["", "## The audit's 'owner sheet decided' class, re-judged", "",
          "texture_regen_audit.py calls an UNPROVEN picture 'sheet decided' when its stem appears anywhere in a "
          "decisions.json. Traced to its bytes, that class is mostly NOT his pick:", ""]
    for k, c in doc["sheet_decided_rejudged"].items():
        L.append(f"- {k}: " + ", ".join(f"{v} {n}" for v, n in sorted(c.items(), key=lambda x: -x[1])))
    L += ["", "## Roster rows with no sheet ruling", ""]
    L += [f"- {r['biome']} `{r['def']}`: {', '.join(r['verdicts']) or 'no file'}" for r in doc["roster"]]
    return "\n".join(L) + "\n"


def check():
    doc = json.load(open(OUT_JSON))
    rec = {(r["file"], r["sha"]): r for r in doc["files"]}
    cl = T.Classifier()
    now = no_record_files(cl)
    missing = [(k, dn, str(q.relative_to(REPO))) for k, dn, q, sha in now if (str(q.relative_to(REPO)), sha) not in rec]
    bad = [r for r in doc["files"] if r["verdict"] not in VERDICTS or not r.get("why")]
    unresolved = [r for r in doc["files"] if r["verdict"] == "UNRESOLVED"]
    print(f"no-record (def, file) pairs now: {len(now)}; distinct (file, sha) on record: {len(rec)}; missing a verdict: {len(missing)}; "
          f"malformed: {len(bad)}; unresolved: {len(unresolved)}")
    # sanity probe: the instrument must see unproven files at all (a 0 here is a blind instrument, not success)
    if not now:
        print("BLIND: measured zero UNPROVEN files; the instrument cannot see"); return 1
    for m in missing[:15]:
        print("  MISSING", *m)
    for r in unresolved[:15]:
        print("  UNRESOLVED", r["def"], r["file"])
    return 0 if not missing and not bad and not unresolved else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if not a.audit:
        ap.error("--audit <audit.json> (from texture_regen_audit.py) or --check")
    write(Path(a.audit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
