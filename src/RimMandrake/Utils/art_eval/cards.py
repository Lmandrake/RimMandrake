#!/usr/bin/env python3
"""Build one evaluation CARD per subject: the panels a reviewer sees, the facts it reads as text, the numeric gates.

A card is a directory:
    card.json        every text fact (subject, template, module, description, departures, notes, sizes, gates,
                     panels, image sha256s) — given to models as TEXT, never only as pixels
    card.md          the same facts as the prompt reads them
    facings.png      south/east/north(/west) side by side on a checkerboard at ONE shared scale, labelled
    south.png …      each facing alone at full resolution;  single.png for plants/items
    scale.png        the true-scale panel (beside a vanilla human) — from scale_panel.py upstream
    living_reference.png  (catch) the living animal's facings;  siblings.png, variants.png, flight.png,
    assembled_N.png  (machines) the in-game capture(s)

Input is a SPEC (JSON) naming files; `pilot_spec()` makes one from the 2026-10-23 pilot bundle
(`Transient/art_eval_pilot_20261023/bundle/items/NN_<def>/`, built by build_pilot_bundle.py).

    python3 cards.py build <spec.json> --out <dir>
    python3 cards.py pilot RM_Huldu:C --out <dir>          # one candidate letter of a pilot subject
    python3 cards.py pilot RM_HulduCatch:C:D --out <dir>   # catch C, living reference = candidate D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "Transient/art_eval_pilot_20261023/bundle"
BRIEFS = ROOT / "infrastructure/state/art_eval/briefs"
FACINGS = ("south", "east", "north", "west")
VISIBLE_ALPHA = 16          # rimworld-sprite-facings: never measure at alpha > 0 (sub-visible export halo)
SPREAD_FLAG = 0.15          # cross-facing height spread that flags F_SIZE_JUMP for a look (sprite-facings audit)
MAXPX = 2000                # both reviewers downscale past ~2000 px on the long side


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pixel_hash(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def visible_bbox(im: Image.Image):
    if im.mode != "RGBA":
        return None
    a = im.getchannel("A").point(lambda v: 255 if v > VISIBLE_ALPHA else 0)
    return a.getbbox()


def checker(w, h, s=16):
    im = Image.new("RGB", (w, h), (200, 200, 200))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range(0, w, s):
            if (x // s + y // s) % 2:
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=(236, 236, 236))
    return im


def _font(sz=20):
    for f in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def shrink(im: Image.Image, maxpx=MAXPX) -> Image.Image:
    if max(im.size) <= maxpx:
        return im
    k = maxpx / max(im.size)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BOX)


def strip(images: list, labels: list, tile=512, title="") -> Image.Image:
    """Images side by side, each scaled by ONE factor (the largest canvas fits the tile), on a checkerboard."""
    ims = [Image.open(p).convert("RGBA") for p in images]
    k = tile / max(max(i.size) for i in ims)
    head = 34 if title else 0
    out = Image.new("RGB", (tile * len(ims), tile + 30 + head), (60, 50, 40))
    d = ImageDraw.Draw(out)
    if title:
        d.text((8, 6), title, fill=(240, 230, 210), font=_font(20))
    for n, (im, lab) in enumerate(zip(ims, labels)):
        r = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BOX)
        bg = checker(tile, tile)
        bg.paste(r, ((tile - r.width) // 2, tile - r.height), r)
        out.paste(bg, (n * tile, head))
        d.text((n * tile + 8, head + tile + 4), lab, fill=(240, 230, 210), font=_font(18))
    return out


def gates(facing_files: dict) -> dict:
    """Numbers code measures (models are told not to re-estimate them)."""
    g = {"alpha": {}, "visible_height_px": {}, "duplicates": []}
    seen = {}
    for f, p in facing_files.items():
        im = Image.open(p)
        g["alpha"][f] = im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 255
        bb = visible_bbox(im.convert("RGBA"))
        g["visible_height_px"][f] = (bb[3] - bb[1]) if bb else 0
        h = pixel_hash(im)
        if h in seen:
            g["duplicates"].append([seen[h], f])
        seen[h] = f
    hs = [v for k, v in g["visible_height_px"].items() if k in FACINGS and v]
    if len(hs) >= 2:
        g["height_spread"] = round(max(hs) / min(hs) - 1, 3)
        g["height_spread_flag"] = g["height_spread"] > SPREAD_FLAG
    return g


def build_card(spec: dict, out: Path) -> dict:
    """Write the card directory for `spec` into `out` and return card.json's content."""
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    imgs = spec.get("images", {})
    panels, shas, src_shas = {}, {}, {}

    def put(name, src):
        src_shas[name] = sha256_file(src)              # the artstore/art-ledger sha of the judged picture
        im = shrink(Image.open(src))
        dst = out / f"{name}.png"
        im.save(dst)
        panels[name] = dst.name
        shas[dst.name] = sha256_file(dst)
        return dst

    facing_src = {f: imgs[f] for f in FACINGS if imgs.get(f)}
    for f, p in facing_src.items():
        put(f, p)
    if imgs.get("single"):
        put("single", imgs["single"])
    if imgs.get("scale"):
        put("scale", imgs["scale"])
    for many in ("assembled", "flight", "variants"):
        for n, p in enumerate(imgs.get(many) or [], 1):
            put(f"{many}_{n}", p)
        if imgs.get(many):
            panels[many] = [k for k in panels if k.startswith(many + "_")]
    if imgs.get("wall_context"):
        put("wall_context", imgs["wall_context"])
    for comp in ("living_reference", "siblings"):
        v = imgs.get(comp)
        if v:
            files = list(v.values()) if isinstance(v, dict) else list(v)
            labs = list(v.keys()) if isinstance(v, dict) else [Path(x).stem for x in files]
            im = strip(files, labs, tile=384, title=f"{comp.replace('_', ' ').upper()} — reference, not a candidate")
            im.save(out / f"{comp}.png")
            panels[comp] = f"{comp}.png"
            shas[f"{comp}.png"] = sha256_file(out / f"{comp}.png")
    if facing_src:
        im = strip([out / f"{f}.png" for f in facing_src], list(facing_src),
                   title=f"{spec['subject']} candidate {spec.get('candidate', '')} — one shared scale")
        im.save(out / "facings.png")
        panels["facings"] = "facings.png"
        shas["facings.png"] = sha256_file(out / "facings.png")
    g = gates({f: out / f"{f}.png" for f in facing_src} or ({"single": out / "single.png"} if "single" in panels else {}))
    card = {k: v for k, v in spec.items() if k != "images"}
    card.update({"panels": panels, "image_sha256": shas, "source_sha256": src_shas, "gates": g,
                 "card_sha": hashlib.sha256(json.dumps([card.get("description"), shas], sort_keys=True).encode()).hexdigest()[:16]})
    (out / "card.json").write_text(json.dumps(card, indent=1))
    (out / "card.md").write_text(card_md(card))
    return card


def card_md(card: dict) -> str:
    L = [f"# {card['subject']} — {card.get('label', '')}", "",
         f"- template: {card['template']} · module: {card.get('module')} · candidate: {card.get('candidate', '-')}",
         f"- tier: {card.get('tier', '-')} · invented: {'yes' if card.get('invented') else 'no'}"
         + (f" · body plan: {card['body_plan']}" if card.get("body_plan") else ""),
         f"- provenance: {card.get('provenance', '-')}"]
    if card.get("size"):
        s = card["size"]
        L.append(f"- size: {json.dumps({k: s[k] for k in s if k != 'source'})}")
    L += ["", "## Intended description (the def text)", "", (card.get("description") or "(none)").strip()]
    if card.get("departures") and card.get("template") == "creature":   # plants use only earth_body_named
        L += ["", "## Required departures from the nearest Earth animal (each must be visible)", ""]
        L += [f"{n}. {d}" for n, d in enumerate(card["departures"], 1)]
    if card.get("canon"):
        L += ["", "## Canon — Must show (yes/no each)", ""] + [f"- {x}" for x in card["canon"].get("must_show", [])]
        if card["canon"].get("engine_limits"):
            L += ["", "Engine limits (never a reason): " + "; ".join(card["canon"]["engine_limits"])]
    if card.get("owner_notes"):
        L += ["", "## Owner notes on this subject (verbatim, each is a requirement)", ""]
        L += [f"- {n}" for n in card["owner_notes"]]
    if card.get("ports"):
        L += ["", "## Code-defined ports (each must have a drawn connector there; no other drawn connectors)", ""]
        L += [f"- {p}" for p in card["ports"]]
    if card.get("depends_on"):
        L += ["", f"This is a catch item of `{card['depends_on']}`; `living_reference.png` shows that living animal."]
    g = card.get("gates", {})
    L += ["", "## Measured by code (do not re-estimate)", "",
          f"- visible-alpha height per facing (px): {g.get('visible_height_px')}"]
    if "height_spread" in g:
        L.append(f"- cross-facing height spread: {g['height_spread']:.0%}"
                 + (" — FLAGGED (> 15 %): judge whether it is real or a pose" if g.get("height_spread_flag") else " (within 15 %)"))
    if g.get("duplicates"):
        L.append(f"- byte-identical pictures: {g['duplicates']}")
    L.append(f"- real alpha present: {g.get('alpha')}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ pilot adapter
def _pilot_dir(defname: str) -> Path:
    hits = [p for p in (PILOT / "items").iterdir() if p.name.split("_", 1)[1] == defname]
    if len(hits) != 1:
        raise SystemExit(f"pilot bundle has {len(hits)} items named {defname}")
    return hits[0]


MODULE_OF_CLASS = {"fauna/walker": "walker", "fauna/walker_pack": "pack", "fauna/swimmer": "swimmer",
                   "fauna/amphibious": "amphibious", "fauna/flyer": "flyer", "item/catch": "catch",
                   "flora/ground_cover": "ground_cover", "flora/bush": "bush", "flora/tree": "tree",
                   "flora/special": "special"}


def pilot_spec(ref: str) -> dict:
    """'DEF:LETTER[:LIVING_LETTER]' -> spec. The owner's verdicts (answer_key.json) are never read here."""
    parts = ref.split(":")
    defname, letter = parts[0], parts[1]
    living = parts[2] if len(parts) > 2 else None
    d = _pilot_dir(defname)
    c = json.loads((d / "card.json").read_text())
    cand = next(x for x in c["candidates"] if x["letter"] == letter)
    module = MODULE_OF_CLASS[c["class"]]
    template = "plant" if c["class"].startswith("flora/") else "creature"
    imgs = {f: str(d / v["file"]) for f, v in cand["files"].items()}
    imgs["scale"] = str(d / cand["true_scale_panel"])
    spec = {"subject": defname, "label": c.get("label"), "template": template, "module": module,
            "candidate": letter, "provenance": cand.get("provenance_label_shown_to_owner"),
            "description": c.get("description"), "tier": c.get("tier"),
            "invented": "our own design" in (c.get("tier") or "") and not c.get("canon"),
            "canon": c.get("canon"), "size": c.get("size"), "source": f"pilot bundle {d.relative_to(ROOT)}"}
    if module == "catch":
        spec["depends_on"] = defname[:-5] if defname.endswith("Catch") else None
        if living:
            lc = next(x for x in c["candidates"] if x["letter"] == living)
            imgs["living_reference"] = {f: str(d / v["file"]) for f, v in lc["files"].items()}
    spec["images"] = imgs
    brief = BRIEFS / f"{defname}.json"
    if brief.is_file():
        b = json.loads(brief.read_text())
        spec["departures"] = b.get("departures") or []
        spec["earth_body_named"] = bool(b.get("earth_body_named"))
        if b.get("body_plan"):
            spec["body_plan"] = b["body_plan"]
    return spec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("spec"); b.add_argument("--out", required=True)
    p = sub.add_parser("pilot"); p.add_argument("ref"); p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    spec = json.loads(Path(a.spec).read_text()) if a.cmd == "build" else pilot_spec(a.ref)
    card = build_card(spec, Path(a.out))
    print(f"card {card['subject']} -> {a.out} panels={sorted(card['panels'])} gates={card['gates'].get('height_spread')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
