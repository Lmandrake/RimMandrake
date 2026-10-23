#!/usr/bin/env python3
"""Build the blind art-eval pilot bundle (GPT vs Opus) from ONE owner-ruled biome review sheet.

Reconstructs the sheet the owner actually ruled — the committed sheet HTML that preceded his sitting, corrected
by the art ledger's owner events (which carry the exact shas and letters he ruled) — then writes:

  <out>/bundle/items/<NN>_<defName>/   every candidate picture, every facing, at full resolution where the
                                        artstore still holds it; a composed page; a true-scale panel per
                                        candidate (vanilla human, 32 px/cell play zoom); card.md + card.json
  <out>/bundle/contact/<class>_pN.png  one contact sheet per class group (south/single facing of each candidate)
  <out>/bundle/manifest.json           item list, class, files
  <out>/answer_key.json                the owner's verdicts + notes per item, with provenance (NOT in bundle/)

    python3 src/RimMandrake/Utils/art_eval/build_pilot_bundle.py            # Weeping Stones defaults
    python3 src/RimMandrake/Utils/art_eval/build_pilot_bundle.py --dry-run  # reconstruct + print, no images

Images ≤ 2000 px on the long side (Claude many-image and OpenAI vision both downscale past ~2000).
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))

SHEET = "weepingstones_sheet_2026-10-05"
SHEET_COMMIT = "01b5cdb299"          # last committed build before the owner's 2026-10-10 sitting
OUT = ROOT / "Transient/art_eval_pilot_20261023"
SKIP_GROUP = "Already ruled on another sheet"   # rows he did not rule in this sitting
MAXPX = 2000
FACE_ORDER = ["south", "east", "north", "west", "single"]

# Class per row. Source: the def description shown on the sheet + race flags in
# src/RimMandrake/WeepingStones/Defs (MaxFlightTime/canFly, packAnimal) + the sheet's swimming-graphic lane.
CLASS = {
    # flora
    "RM_Dewblade": "flora/ground_cover", "RM_Verdimoss": "flora/ground_cover", "RM_Weepmat": "flora/ground_cover",
    "Plant_Ambrosia": "flora/bush", "RM_Bladderquill": "flora/bush", "RM_Dewgourd": "flora/bush",
    "RM_Salvecomb": "flora/bush", "RM_Shadefern": "flora/bush", "RM_Steamfrond": "flora/bush",
    "RM_Dewshrooms": "flora/bush", "Plant_Reeds": "flora/bush",
    "RM_Dripfringe": "flora/special", "RM_Rockfinger": "flora/tree",
    # fauna
    "RSW_Boma": "fauna/walker", "RM_Burrak": "fauna/walker", "ColossusToad": "fauna/walker",
    "RM_Gorrask": "fauna/walker", "RM_Sillik": "fauna/walker", "RM_Ssurr": "fauna/walker",
    "RM_Vhakk": "fauna/walker", "RM_Tirbak": "fauna/walker_pack", "RM_Vellak": "fauna/walker_pack",
    "RSW_Dactillion": "fauna/flyer", "RM_Kirruk": "fauna/flyer", "RM_Mirrik": "fauna/flyer",
    "RSW_Fanback": "fauna/amphibious", "RSW_Ollopom": "fauna/amphibious",
    "RM_Huldu": "fauna/swimmer", "RM_Ivvol": "fauna/swimmer", "RM_Karrek": "fauna/swimmer",
    "RM_Loomu": "fauna/swimmer", "RM_Murrin": "fauna/swimmer", "RM_Skarrin": "fauna/swimmer",
    "RM_Vizhik": "fauna/swimmer",
}
DEFAULT_CLASS_BY_KIND = {"fish": "item/catch"}
# Rows whose ledger record contradicts itself — said once, here, so scoring knows.
EXTRA_CAVEATS = {
    "RSW_Dactillion": "his note says 'Old Flyer art must be removed (remove F)' and four shas were purged under it "
                      "(candidates C/D here), yet the ledger also records a keep on the flight-frame column F — "
                      "treat the flight-frame candidate's status as uncertain",
}


def sh(*a, binary=False):
    r = subprocess.run(list(a), cwd=ROOT, capture_output=True, timeout=120)
    if r.returncode:
        return None
    return r.stdout if binary else r.stdout.decode()


def sheet_items():
    h = sh("git", "show", f"{SHEET_COMMIT}:Transient/biome_ffar/{SHEET}.html")
    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', h, re.S)
    return json.loads(m.group(1))


def owner_events():
    ev = []
    for f in sorted(glob.glob(str(ROOT / "infrastructure/state/art/events/*.jsonl"))):
        for line in open(f):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("by") == "owner" and SHEET in json.dumps(e):
                ev.append(e)
    return ev


def decisions():
    return json.load(open(ROOT / f"Transient/biome_ffar/{SHEET}.decisions.json"))["decisions"]


def canon_block(item):
    c = item.get("canon") or {}
    d = c.get("dir")
    if not d:
        return None
    p = ROOT / d / "description.md"
    if not p.is_file():
        return None
    t = p.read_text()

    def sec(name):
        m = re.search(r"^## %s\s*\n(.*?)(?=^## |\Z)" % re.escape(name), t, re.S | re.M)
        return m.group(1).strip() if m else ""
    must = "\n".join(l for l in sec("Must show").splitlines() if l.strip().startswith("- ["))
    return {"entry": str(Path(d) / "description.md"), "must_show": must, "engine_limits": sec("Engine limits")}


def reconstruct(items, ev, dec):
    """Per row: candidates {letter: {faces:{face: sha}, label, kind, src}} as the owner saw them, plus truth."""
    led_cols = defaultdict(dict)   # row -> letter -> set(shas)
    rulings = defaultdict(list)
    for e in ev:
        t = e.get("target") or {}
        row = t.get("row") or e.get("row")
        if not row:
            continue
        rulings[row].append(e)
        col = t.get("column") or e.get("column")
        shas = t.get("shas") or ([e["sha"]] if e.get("sha") else [])
        if col and shas:
            led_cols[row].setdefault(col, set()).update(shas)
    rows = []
    for it in items:
        if it.get("group") == SKIP_GROUP:
            continue
        rid = it["id"]
        cols = []      # list of dicts from the committed sheet
        for g in it["graphics"]:
            flight = "flight" in (g.get("role") or "") or "Flying" in g["key"]
            swim = "swimming" in (g.get("role") or "")
            for c in g["cols"]:
                faces = {}
                for f, s in c["faces"].items():
                    k = ("fly_" + f) if flight else (("swim_" + f) if swim else f)
                    faces[k] = s
                cols.append({"letter": c["letter"], "faces": faces, "label": c.get("short") or c.get("label", ""),
                             "kind": c["kind"], "lane": g.get("role")})
        sha2col = {s: i for i, c in enumerate(cols) for s in c["faces"].values()}
        owner_letter = {}
        for L, shas in led_cols.get(rid, {}).items():
            hits = {sha2col[s] for s in shas if s in sha2col}
            for i in hits:
                owner_letter[i] = L
        cand = {}
        # every letter the owner's sheet used is reserved, mapped onto a committed column or not
        used = set(owner_letter.values()) | set(led_cols.get(rid, {}))
        for i, c in enumerate(cols):
            L = owner_letter.get(i, c["letter"])
            if i not in owner_letter and L in used:
                L = next(x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if x not in used and x not in cand)
            used.add(L)
            if L in cand:   # two committed columns ruled under one owner letter: merge faces
                cand[L]["faces"].update(c["faces"])
                continue
            cand[L] = dict(c, letter=L, src=f"sheet@{SHEET_COMMIT} col {c['letter']}" + ("" if L == c["letter"] else f" (owner's sheet relettered it {L})"))
        # ledger columns whose shas the committed sheet never showed (renders landed between build and sitting)
        for L, shas in led_cols.get(rid, {}).items():
            missing = [s for s in shas if s not in sha2col]
            if missing and L in cand and not (set(cand[L]["faces"].values()) & shas):
                raise SystemExit(f"{rid}: letter {L} collision")
            if missing and L not in cand:
                cand[L] = {"letter": L, "faces": {}, "label": "render landed after the committed build (from art ledger)",
                           "kind": "artpipe", "lane": "body", "src": "art ledger owner ruling (column " + L + ")",
                           "_unfaced": missing}
        relettered = any(not c["src"].endswith(f"col {c['letter']}") for c in cand.values())
        rows.append({"item": it, "cand": dict(sorted(cand.items())), "rulings": rulings.get(rid, []), "relettered": relettered,
                     "dec": dec.get(rid, {})})
    return rows


def face_of(sha, meta):
    m = meta.get(sha) or {}
    f = m.get("facing")
    if f in ("south", "east", "north", "west", "single"):
        return f
    rel = m.get("rel") or m.get("loc") or ""
    mm = re.search(r"_(south|east|north|west)\.png$", rel)
    return mm.group(1) if mm else "single"


def sha_meta():
    meta = {}
    for f in sorted(glob.glob(str(ROOT / "infrastructure/state/art/events/*.jsonl"))):
        for line in open(f):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            s = e.get("sha")
            if s and s not in meta and (e.get("facing") or e.get("rel") or e.get("loc")):
                meta[s] = e
    return meta


def truth(row):
    """Owner's verdict per row and status per candidate, from the decisions file + art ledger."""
    d = row["dec"]
    rid = row["item"]["id"]
    decision = d.get("decision")
    notes = [n["note"] for n in d.get("notes_followed", []) if n.get("note")] + ([d["note"]] if d.get("note") else [])
    verdict = {"redo": "REDO", "hold": "HOLD"}.get(decision, "KEEP")
    if decision == "hold" and any("cut" in n.lower() for n in notes):
        verdict = "CUT"
    purged = set(d.get("purge", []))
    status = {}
    for L, c in row["cand"].items():
        shas = set(c["faces"].values()) | set(c.get("_unfaced", []))
        st = "not_chosen"
        for e in row["rulings"]:
            t = e.get("target") or {}
            es = set(t.get("shas") or ([e["sha"]] if e.get("sha") else []))
            col = t.get("column") or e.get("column")
            if not (es & shas) and col != L:
                continue
            if e["type"] == "rejected":
                st = "rejected"
            elif e["type"] == "ruling" and e.get("verdict") == "keep" and col == L:
                vo = t.get("variant_of")
                if verdict == "KEEP":
                    st = "pick" if L == decision else ("keep_variant" if vo == decision else "keep_other_slot")
                elif st != "rejected":
                    st = "retained_as_reference"
        if shas and shas <= purged:
            st = "purged"
        elif shas & purged:
            st = "partly_purged"
        status[L] = st
    art_judgeable = not (verdict == "CUT" and all("no longer needed" in n for n in notes))
    caveats = []
    if verdict == "KEEP" and status.get(decision) in ("purged", "partly_purged", None):
        caveats.append(f"pick letter {decision} has no surviving picture in the reconstruction (ledger ruling for "
                       f"{decision} carries no shas, or its pictures were purged) — score the row verdict, not the pick")
    if row.get("relettered"):
        caveats.append("renders landed between the committed sheet build and his sitting: candidate letters for this row "
                       "are RECONSTRUCTED from the art ledger's shas — the row verdict is certain, per-candidate status less so")
    if rid in EXTRA_CAVEATS:
        caveats.append(EXTRA_CAVEATS[rid])
    if not art_judgeable:
        caveats.append("CUT for a design reason (roster no longer needs it), not for the art — exclude from art scoring")
    return {"defName": rid, "verdict": verdict, "pick": decision if verdict == "KEEP" else None, "caveats": caveats,
            "candidates": status, "notes_verbatim": notes, "art_judgeable": art_judgeable,
            "ruled_at": d.get("at"),
            "provenance": {"decisions_file": f"Transient/biome_ffar/{SHEET}.decisions.json",
                           "art_ledger_event_ids": sorted({e["id"] for e in row["rulings"]}),
                           "by": "owner (sidecar savedBy/writeCount; per-row `at` stamp)"}}


# ---------------------------------------------------------------- images
def get_bytes(sha, item, store_get, store_has):
    if store_has(sha):
        return store_get(sha), "artstore (full resolution)"
    th = (item.get("thumbs") or {}).get(sha)
    if th:
        full = th.replace(".webp", "_full.png")
        b = sh("git", "show", f"{SHEET_COMMIT}:Transient/biome_ffar/{full}", binary=True)
        if b:
            return b, "sheet full-size copy from git (artstore bytes purged)"
        b = sh("git", "show", f"{SHEET_COMMIT}:Transient/biome_ffar/{th}", binary=True)
        if b:
            return b, "sheet THUMBNAIL from git (full-res purged — reduced resolution)"
    return None, "MISSING"


def checker(w, h, s=12):
    from PIL import Image
    im = Image.new("RGBA", (w, h), (214, 214, 214, 255))
    px = im.load()
    for y in range(h):
        for x in range(w):
            if ((x // s) + (y // s)) % 2:
                px[x, y] = (236, 236, 236, 255)
    return im


def fit(im, box):
    from PIL import Image
    im = im.copy()
    im.thumbnail((box, box), Image.LANCZOS)
    return im


def font(sz):
    from PIL import ImageFont
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"]:
        if Path(p).is_file():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def compose_grid(title, rows_of_cells, cell=240, lab_w=150):
    """rows_of_cells: [(row_label, [(cell_label, PIL.Image|None)])] -> one RGB page ≤ MAXPX."""
    from PIL import Image, ImageDraw
    ncol = max(len(c) for _, c in rows_of_cells)
    cell = min(cell, (MAXPX - lab_w) // max(ncol, 1), (MAXPX - 60) // len(rows_of_cells) - 22)
    W, H = lab_w + ncol * cell, 50 + len(rows_of_cells) * (cell + 22)
    page = Image.new("RGB", (W, H), (40, 34, 28))
    d = ImageDraw.Draw(page)
    d.text((10, 12), title, fill=(240, 230, 210), font=font(20))
    bg = checker(cell - 6, cell - 6)
    for r, (rl, cells) in enumerate(rows_of_cells):
        y = 50 + r * (cell + 22)
        d.text((8, y + cell // 2 - 10), rl, fill=(240, 230, 210), font=font(18))
        for c, (cl, im) in enumerate(cells):
            x = lab_w + c * cell
            d.text((x + 3, y), cl, fill=(220, 200, 160), font=font(14))
            tile = bg.copy()
            if im is not None:
                t = fit(im.convert("RGBA"), cell - 10)
                tile.alpha_composite(t, ((tile.width - t.width) // 2, (tile.height - t.height) // 2))
            else:
                ImageDraw.Draw(tile).text((10, 10), "(no image)", fill=(120, 0, 0), font=font(14))
            page.paste(tile.convert("RGB"), (x + 3, y + 18))
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    t0 = time.time()
    items = sheet_items()
    rows = reconstruct(items, owner_events(), decisions())
    meta = sha_meta()
    for r in rows:   # place ledger-only shas on a facing
        for c in r["cand"].values():
            for s in c.pop("_unfaced", []):
                c["faces"].setdefault(face_of(s, meta), s)
    if a.only:
        rows = [r for r in rows if r["item"]["id"] in a.only]
    key = {}
    for r in rows:
        k = truth(r)
        k["class"] = CLASS.get(r["item"]["id"]) or DEFAULT_CLASS_BY_KIND.get(r["item"]["kind"], "?")
        key[r["item"]["id"]] = k
    if a.dry_run:
        for r in rows:
            k = key[r["item"]["id"]]
            print(r["item"]["id"], k["class"], k["verdict"], k["pick"], k["candidates"],
                  {L: sorted(c["faces"]) for L, c in r["cand"].items()})
        return
    from PIL import Image
    import artledger
    import scale_panel
    bundle = OUT / "bundle"
    (bundle / "items").mkdir(parents=True, exist_ok=True)
    (bundle / "contact").mkdir(parents=True, exist_ok=True)
    biome_intent = re.search(r"<description>(.*?)</description>", (ROOT / "src/RimMandrake/WeepingStones/Defs/BiomeDefs/RM_WeepingStones_Biome.xml").read_text(), re.S).group(1).strip()
    manifest = {"biome": "RM_WeepingStones", "biome_intent": biome_intent, "items": []}
    stats = defaultdict(int)
    contact = defaultdict(list)
    for n, r in enumerate(rows, 1):
        it = r["item"]
        rid = it["id"]
        cls = key[rid]["class"]
        d = bundle / "items" / f"{n:02d}_{rid}"
        d.mkdir(parents=True, exist_ok=True)
        cards = []
        grid_main, grid_fly = [], []
        for L, c in r["cand"].items():
            faces_sorted = sorted(c["faces"].items(), key=lambda kv: (kv[0].startswith(("fly_", "swim_")),
                                  next((i for i, f in enumerate(FACE_ORDER) if kv[0].endswith(f)), 9), kv[0]))
            files, imgs = {}, {}
            for f, s in faces_sorted:
                b, how = get_bytes(s, it, artledger.store_get, artledger.store_has)
                stats[how] += 1
                if not b:
                    files[f] = {"file": None, "how": how}
                    continue
                im = Image.open(io.BytesIO(b)).convert("RGBA")
                fn = f"{L}_{f}.png"
                im.save(d / fn)
                files[f] = {"file": fn, "px": list(im.size), "how": how}
                imgs[f] = im
            main = [(f, imgs.get(f)) for f, _ in faces_sorted if not f.startswith("fly_")]
            fly = [(f[4:], imgs.get(f)) for f, _ in faces_sorted if f.startswith("fly_")]
            if main:
                grid_main.append((f"cand {L}", main))
            if fly:
                for k0 in range(0, len(fly), 4):
                    grid_fly.append((f"cand {L}", fly[k0:k0 + 4]))
            # true-scale panel from the most frontal body facing
            pick_f = next((f for f in ("south", "single", "east", "north") if f in imgs), None)
            scale_file = None
            if pick_f and it.get("scale", {}).get("status") in ("measured", "fallback") or (pick_f and it.get("scale")):
                try:
                    buf = io.BytesIO()
                    imgs[pick_f].save(buf, "PNG")
                    sp = d / f"{L}_scale.png"
                    spf = d / f"{L}_scale_full.png"
                    scale_panel.render_panel(buf.getvalue(), it["scale"], sp, spf)
                    full = Image.open(spf)
                    if max(full.size) > MAXPX:
                        full.thumbnail((MAXPX, MAXPX), Image.LANCZOS)
                        full.save(spf)
                    sp.unlink()
                    scale_file = spf.name
                except Exception as ex:   # noqa: BLE001 — record, never hide
                    scale_file = f"FAILED: {ex}"
            if pick_f:
                contact[cls].append((f"{rid} {L}", imgs[pick_f]))
            cards.append({"letter": L, "provenance_label_shown_to_owner": c["label"], "lane": c.get("lane"),
                          "facings": [f for f, _ in faces_sorted], "files": files, "true_scale_panel": scale_file})
        if grid_main:
            compose_grid(f"{rid} — {it['label']} — candidates x facings (west = mirror of east)", grid_main).save(d / "page_facings.png")
        if grid_fly:
            compose_grid(f"{rid} — flight flip-book frames (frame_direction)", grid_fly).save(d / "page_flight.png")
        sc = it.get("scale") or {}
        canon = canon_block(it)
        card = {"defName": rid, "label": it["label"], "class": cls, "tier": it.get("tierText"),
                "description": (it.get("desc") or {}).get("description", ""),
                "biome": "RM_WeepingStones", "canon": canon,
                "size": {k: sc.get(k) for k in ("kind", "cells", "bodySize", "drawSize", "mesh", "visualMax", "source")},
                "candidates": cards}
        (d / "card.json").write_text(json.dumps(card, indent=1))
        md = [f"# {rid} — {it['label']}", "", f"- **class:** {cls}", f"- **tier:** {it.get('tierText')}",
              f"- **size:** kind {sc.get('kind')}, {sc.get('cells')} cells across, bodySize {sc.get('bodySize')}, drawSize {sc.get('drawSize')}, mesh {sc.get('mesh')}" + (f", visualMax {sc.get('visualMax')}" if sc.get('visualMax') else ""),
              "", "## Intended description (the def text)", "", card["description"], ""]
        if canon:
            md += ["## Canon — Must show (each line is a yes/no check)", "", canon["must_show"], "",
                   "## Canon — Engine limits (never a REDO reason)", "", canon["engine_limits"] or "(none listed)", ""]
        md += ["## Candidates", ""]
        for cd in cards:
            md.append(f"- **{cd['letter']}** — {cd['provenance_label_shown_to_owner']} — lane `{cd['lane']}` — facings: {', '.join(cd['facings'])}"
                      + (f" — true-scale panel `{cd['true_scale_panel']}`" if cd["true_scale_panel"] else ""))
            for f, v in cd["files"].items():
                if v.get("how", "").startswith(("sheet THUMB", "MISSING")):
                    md.append(f"  - {f}: {v['how']}")
        md += ["", "Pages: `page_facings.png`" + (", `page_flight.png`" if grid_fly else "")]
        (d / "card.md").write_text("\n".join(md) + "\n")
        manifest["items"].append({"n": n, "defName": rid, "class": cls, "dir": f"items/{d.name}",
                                  "candidates": list(r["cand"])})
    # contact sheets, ≤ 30 per page
    for cls, cells in contact.items():
        for p, k0 in enumerate(range(0, len(cells), 30), 1):
            chunk = cells[k0:k0 + 30]
            rows_ = [("", chunk[i:i + 6]) for i in range(0, len(chunk), 6)]
            compose_grid(f"RM_WeepingStones — {cls} — contact sheet p{p} (most frontal facing per candidate)",
                         rows_, cell=300, lab_w=10).save(bundle / "contact" / f"{cls.replace('/', '_')}_p{p}.png")
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=1))
    (OUT / "answer_key.json").write_text(json.dumps({
        "_about": "HIDDEN ground truth for the blind race. Owner verdicts from his 2026-10-10 sitting on "
                  f"{SHEET}; never give this file to a reviewer.",
        "_candidate_status": {"pick": "the letter he chose", "keep_variant": "kept as a random-pool variant of the pick",
                              "keep_other_slot": "kept in another slot of the same row", "purged": "he deleted it (✕)",
                              "rejected": "row REDO and this picture dropped", "retained_as_reference": "row REDO; this picture left as the base to redo from",
                              "not_chosen": "shown, neither picked nor deleted", "partly_purged": "some facings deleted"},
        "items": key}, indent=1))
    print("items", len(rows), "images", dict(stats), "secs", round(time.time() - t0))


if __name__ == "__main__":
    main()
