#!/usr/bin/env python3
"""chat_review.py — single images for ONE art question at a time, sized for the phone / chat (owner, 2026-10-15).

    python3 chat_review.py <artpipe job id | defName>... [--out DIR]

Owner, 2026-10-15: *"I'll need more than just a picture. I often need a scaled drawing and a full resolution drawing
by itself. Plus facings and variants sometimes. So for whole biome art reviews a sheet makes sense but individual art
questions phone makes sense as long as the raw image is put into context even there."*

One QUESTION is one picture slot: a def's texPath (an artpipe job family's target_texpath, or a bare def's body
texPath). For each, three PNGs land in DIR, sortable and named with the plain subject:

    NN_<subject>_1_full.png     the candidate at its FULL resolution, alone (bytes unchanged)
    NN_<subject>_2_scale.png    true scale beside a vanilla human: cell grid, cell ruler, the def's footprint in cells
                                outlined; the candidate on top, what is installed now below at the same px/cell
    NN_<subject>_3_facings.png  every facing, installed now vs candidate, plus the other variants (texPaths) of the
                                same def asked in this run

A job id joins its siblings (the same family minus the _south/_east/_north suffix) from the artpipe render folder.
A defName with no job shows its artpipe renders from the art ledger (one question per render set).
Sizes come from the live def dump through scale_panel.Resolver, as on the sheets. The absolute paths are printed last,
one per line, for a seat to send with SendUserFile in batches of 6-10.
"""
from __future__ import annotations

import argparse
import re
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402
import art_sheet as AS  # noqa: E402
import scale_panel as SP  # noqa: E402
import scaled_review_gate as SG  # noqa: E402

FACE_ORDER = ("south", "east", "north", "west", "single")
FAM_RE = re.compile(r"_(south|east|north|west)$")
MAX_W = 1500          # px: a phone-legible composite
TILE = 256            # px: one facing in the strip
GAME = Path("/mnt/c/Program Files (x86)/Steam/steamapps")


def slug(s: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", s.lower())).strip("_") or "subject"


# ─────────────────────────────────────────────────────────────── inputs ──

def _src_size(defname: str):
    """Size for a def the live dump does not have (every new RM_/RSW_ port): read it from the def's own XML in src/.
    Plant: drawSize x visualSizeRange MAX (the mature draw). Building/item: size + drawSize. Animal: the PawnKindDef's
    last lifeStage bodyGraphicData drawSize. None when the XML cannot say (the caller keeps the loud FALLBACK)."""
    import subprocess
    import xml.etree.ElementTree as ET
    root = Path(__file__).resolve().parents[4]
    hits = subprocess.run(["grep", "-rlF", f"<defName>{defname}</defName>", str(root / "src"), "--include=*.xml"],
                          capture_output=True, text=True).stdout.split()

    def vec(t, default=None):
        try:
            a = [float(x) for x in re.findall(r"-?\d+\.?\d*", t or "")]
            return [a[0], a[1]] if len(a) >= 2 else default
        except Exception:
            return default
    for h in hits:
        try:
            tree = ET.parse(h)
        except ET.ParseError:
            continue
        for td in tree.getroot().iter("ThingDef"):
            if (td.findtext("defName") or "").strip() != defname:
                continue
            rel = h.split("/rm/foundry/")[-1]
            ds = vec(td.findtext("graphicData/drawSize"))
            if td.find("race") is not None:
                for kd in tree.getroot().iter("PawnKindDef"):
                    if (kd.findtext("race") or "").strip() == defname:
                        for li in reversed(list(kd.find("lifeStages") or [])):
                            d = vec(li.findtext("bodyGraphicData/drawSize"))
                            if d:
                                return {"status": "authored-from-src", "kind": "animal", "def": defname, "drawSize": d,
                                        "bodySize": None, "cells": max(d), "mesh": 1, "quad": max(d), "color": [1, 1, 1],
                                        "source": f"SRC XML {rel} PawnKindDef {kd.findtext('defName')} last lifeStage drawSize (not in the live dump)"}
                return None
            vr = td.findtext("plant/visualSizeRange")
            if td.find("plant") is not None and vr:
                v = [float(x) for x in re.findall(r"\d+\.?\d*", vr)]
                vmax = max(v)
                d = ds or [1.0, 1.0]
                q = d[0] * vmax
                return {"status": "authored-from-src", "kind": "plant", "def": defname, "drawSize": d, "visualMax": vmax,
                        "mesh": 1, "color": [1, 1, 1], "quad": q, "cells": q,
                        "source": f"SRC XML {rel}: drawSize {d[0]:g} x visualSizeRange {vr.strip()} (drawn at the MAX {vmax:g}; "
                                  f"smaller plants draw down to {min(v):g}); not in the live dump"}
            sz = vec(td.findtext("size"), [1, 1])
            d = ds or [1.0, 1.0]
            return {"status": "authored-from-src", "kind": "thing", "category": "Building", "def": defname,
                    "drawSize": d, "footprint": [int(sz[0]), int(sz[1])], "offset": [0.0, 0.0],
                    "graphicClass": (td.findtext("graphicData/graphicClass") or "").rsplit(".", 1)[-1], "color": [1, 1, 1],
                    "quad": d[0], "cells": float(max(sz)), "mesh": 1,
                    "source": f"SRC XML {rel}: size {int(sz[0])}x{int(sz[1])}, drawSize {d[0]:g}x{d[1]:g} (not in the live dump)"}
    return None


def _job_or_none(jid: str):
    try:
        return AS._job(jid)
    except SystemExit:
        return None


def job_family(jid: str) -> tuple[str, dict]:
    """(family, {facing: png bytes}) — every render of the family on disk in the artpipe render folder."""
    fam = FAM_RE.sub("", jid)
    src = SG.artpipe_dir() / "_artsrc"
    faces = {}
    for d in [src / fam] + [src / f"{fam}_{f}" for f in FACE_ORDER[:4]]:
        if not d.is_dir():
            continue
        m = FAM_RE.search(d.name)
        pngs = sorted(p for p in d.glob("*.png") if not p.stem.endswith(("_m", "m_mask")))
        own = [p for p in pngs if p.stem == d.name] or pngs
        if own:
            faces[m.group(1) if m else "single"] = own[0].read_bytes()
    if not faces:
        raise SystemExit(f"{jid}: no render PNG under {src}/{fam}[_facing]/")
    return fam, faces


def _disk_installed(tex: str) -> tuple[str, dict]:
    """Fallback when the ledger holds nothing for a texPath: the files a mod ships for it today (ours, then the game's
    Mods folder, then the workshop), one level of version folder deep."""
    roots = [(L.REPO_ROOT / "src", "*/*/Textures"), (GAME / "common/RimWorld/Mods", "*/Textures"),
             (GAME / "common/RimWorld/Mods", "*/*/Textures"), (GAME / "workshop/content/294100", "*/Textures"),
             (GAME / "workshop/content/294100", "*/*/Textures")]
    for root, pat in roots:
        for tdir in root.glob(pat):
            faces = {}
            if (tdir / tex).is_dir():   # a folder graphic (Graphic_Random / StackCount): every variant in it
                stems = {p.stem for p in (tdir / tex).glob("*.png")}
                faces = {p.stem: p.read_bytes() for p in sorted((tdir / tex).glob("*.png"))
                         if not (p.stem.endswith("_m") or (p.stem.endswith("m") and p.stem[:-1] in stems))}
            for f in FACE_ORDER:
                p = tdir / f"{tex}{'' if f == 'single' else '_' + f}.png"
                if p.is_file():
                    faces[f] = p.read_bytes()
            if faces:
                mod = root / tdir.relative_to(root).parts[0]
                try:
                    import xml.etree.ElementTree as ET
                    name = ET.parse(mod / "About" / "About.xml").getroot().findtext("name") or mod.name
                except (OSError, ET.ParseError):
                    name = mod.name
                return f"installed now — {name} (file on disk)", faces
    return "", {}


def installed(idx, order, slots, tex: str) -> tuple[str, dict]:
    """(label, {facing: bytes}) of the picture the game shows today for this texPath."""
    try:
        row = AS.build_row(idx, tex, order, slots)
        cols = row["cols"]
    except Exception as e:                                  # noqa: BLE001
        print(f"chat_review: ledger row for {tex} failed ({e}); falling back to disk", file=sys.stderr)
        cols = []
    win = next((c for c in cols if c.get("winner")), None) or next((c for c in cols if c["kind"] in ("live", "donor")), None)
    if win:
        faces = {f: L.store_get(s) for f, s in win["faces"].items() if L.store_has(s)}
        if faces:
            return "installed now — " + re.sub(r"^IN GAME — ", "", win.get("label") or win["kind"]), faces
    return _disk_installed(tex)


def questions(args, R, idx, order, slots) -> list[dict]:
    qs, seen = [], set()
    for a in args:
        job = _job_or_none(a)
        if job is None and _job_or_none(FAM_RE.sub("", a) + "_south") is not None:
            job = _job_or_none(FAM_RE.sub("", a) + "_south")
        if job is not None:
            fam, faces = job_family(job["id"])
            if fam in seen:
                continue
            seen.add(fam)
            qs.append({"def": job["target_def"], "tex": job.get("target_texpath") or "", "cand": faces,
                       "candLabel": f"candidate — render {fam}"})
            continue
        row = AS.subject_row(R, a)
        body = next((r["res"] for r in row["art"]["resources"] if r["role"] == "body"), None)
        if not body:
            raise SystemExit(f"{a}: not an artpipe job, and the def has no world texPath")
        cols = [c for c in AS.build_row(idx, body, order, slots)["cols"] if c["kind"] == "artpipe"]
        if not cols:
            raise SystemExit(f"{a}: no artpipe render on record for {body} — pass the job ids")
        for c in cols:
            qs.append({"def": a, "tex": body, "candLabel": "candidate — " + (c.get("label") or "render"),
                       "cand": {f: L.store_get(s) for f, s in c["faces"].items() if L.store_has(s)}})
    for q in qs:
        td = R._def(q["def"], "ThingDef") or {}
        q["label"] = td.get("label") or q["def"]
        q["size"] = R.size(AS.subject_row(R, q["def"]))
        if q["size"].get("status") == "fallback":
            q["size"] = _src_size(q["def"]) or q["size"]
        # installed now: the picture at the job's target texPath, else what the def draws today (its own texPath —
        # a port may have renamed it, so the donor texPath the render replaces has no file of ours)
        own = [r["res"] for r in AS.subject_row(R, q["def"])["art"]["resources"] if r["role"] == "body"]
        q["inst"] = ("", {})
        for tex in [q["tex"]] + [t for t in own if t != q["tex"]]:
            if tex:
                q["inst"] = installed(idx, order, slots, tex)
                if q["inst"][1]:
                    if tex != q["tex"]:
                        q["inst"] = (f"{q['inst'][0]} ({tex})", q["inst"][1])
                    break
    # the plain subject: the def's label, plus the texPath's own word when one def has several pictures asked
    by_def = {}
    for q in qs:
        by_def.setdefault(q["def"], set()).add(q["tex"])
    for q in qs:
        s = slug(q["label"])
        if len(by_def[q["def"]]) > 1:
            stem = slug(re.sub(r"^[A-Z]{2,4}_", "", Path(q["tex"]).name))
            s = stem if slug(q["label"]).replace("_", "") in stem.replace("_", "") else f"{s}_{stem}"
        q["slug"] = s
    return qs


# ─────────────────────────────────────────────────────────────── images ──

def _img(b: bytes):
    from PIL import Image
    return Image.open(BytesIO(b)).convert("RGBA")


def _main_face(faces: dict, size: dict) -> str:
    order = AS.THING_FACE if size.get("kind") == "thing" else AS.SCALE_FACE
    return next(f for f in list(order) + sorted(faces) if f in faces)


def _quad_x(size: dict) -> float:
    if size.get("kind") == "animal" and size.get("drawSize"):
        return size["drawSize"][0]
    return size.get("quad", size.get("cells", 1.0)) or 1.0


def _wrap(t: str, n: int) -> list[str]:
    out, line = [], ""
    for w in t.split(" "):
        if line and len(line) + len(w) + 1 > n:
            out.append(line)
            line = ""
        line = (line + " " + w).strip()
    return out + [line]


def _fmt(x) -> str:
    return "?" if x is None else f"{float(x):.3f}".rstrip("0").rstrip(".")


def _footprint(size: dict) -> tuple[int, int]:
    return tuple(size.get("footprint") or (1, 1)) if size.get("kind") == "thing" else (1, 1)


def ruled_scene(art, size: dict, ppc: int, title: str):
    """human | subject at ppc, on the cell grid, the def's footprint outlined, with a cell ruler on the left and bottom."""
    from PIL import Image, ImageDraw
    SP.FOOTPRINT[:] = list(size.get("footprint") or (0, 0)) if size.get("kind") == "thing" else [0, 0]
    sc = SP._scene(art, size, ppc, SP._font(12), rat_on=False)
    na, nb, sx0, total_w = SP._extent(SP._art_quads(art, size, ppc), ppc, False)
    lab = 13 if ppc < 100 else 18
    base = sc.height - lab if ppc >= 44 else sc.height
    d = ImageDraw.Draw(sc)
    fx, fz = _footprint(size)
    if size.get("kind") != "thing":         # the scene outlines a thing's footprint itself; a pawn/plant holds one cell
        d.rectangle([round(sx0 * ppc), round(base - (fz + nb) * ppc), round((sx0 + fx) * ppc), round(base - nb * ppc)],
                    outline=(232, 182, 76, 255), width=max(2, ppc // 64))
    L_, B_, T_ = 34, 22, 24
    f = SP._font(13)
    out = Image.new("RGBA", (max(sc.width + L_ + 8, L_ + round(f.getlength(title)) + 8), sc.height + B_ + T_), (18, 16, 13, 255))
    out.alpha_composite(sc, (L_, T_))
    d = ImageDraw.Draw(out)
    d.text((L_, 4), title, font=f, fill=(232, 220, 200))
    for i in range(total_w + 1):            # x ruler: cells
        x = L_ + round(i * ppc)
        d.line([(x, T_ + sc.height), (x, T_ + sc.height + 5)], fill=(200, 190, 170))
        d.text((x + 2, T_ + sc.height + 4), str(i), font=f, fill=(200, 190, 170))
    for j in range(-nb, na + 1):            # y ruler: cells above the ground row's bottom edge
        y = T_ + round(base - (j + nb) * ppc)
        d.line([(L_ - 6, y), (L_, y)], fill=(200, 190, 170))
        d.text((4, y - 8), str(j), font=f, fill=(200, 190, 170))
    return out


def scale_image(q: dict, out: Path) -> None:
    from PIL import Image, ImageDraw
    size = q["size"]
    cf = _main_face(q["cand"], size)
    cart = _img(q["cand"][cf])
    native = round(cart.width / _quad_x(size))
    ppc = max(64, min(256, native))
    _na, _nb, _sx, tw = SP._extent(SP._art_quads(cart, size, ppc), ppc, False)
    if tw * ppc > MAX_W:
        ppc = max(32, MAX_W // tw)
    fx, fz = _footprint(size)
    ds = size.get("drawSize") or [size.get("quad") or size.get("cells")] * 2
    head = [f"{q['label']} ({q['def']}) — true scale beside a vanilla human, {ppc} px per cell",
            f"footprint {fx}×{fz} cell{'s' if fx * fz > 1 else ''} (orange box) · drawn {_fmt(ds[0])}×{_fmt(ds[1])} cells · "
            f"grid = 1 cell · rulers in cells · art {cart.width}×{cart.height} px = {native} px/cell native",
            ] + _wrap(f"size: {size.get('status', '?').upper()} · {size.get('source', '')}", 120)
    panels = [ruled_scene(cart, size, ppc, f"{q['candLabel']} · {cf}")]
    lab, faces = q["inst"]
    if faces:
        f2 = cf if cf in faces else _main_face(faces, size)
        panels.append(ruled_scene(_img(faces[f2]), size, ppc, f"{lab} · {f2}"))
    else:
        panels.append(None)
    f = SP._font(14)
    W = max(p.width for p in panels if p) + 16
    H = 16 + 20 * len(head) + sum((p.height if p else 30) + 12 for p in panels)
    img = Image.new("RGBA", (max(W, 900), H), (18, 16, 13, 255))
    d = ImageDraw.Draw(img)
    y = 8
    for i, t in enumerate(head):
        d.text((8, y), t, font=f, fill=(240, 200, 120) if i == 0 else (200, 190, 170))
        y += 20
    y += 4
    for p in panels:
        if p is None:
            d.text((8, y + 6), "installed now: nothing found for " + q["tex"], font=f, fill=(224, 108, 108))
            y += 42
            continue
        img.alpha_composite(p, (8, y))
        y += p.height + 12
    img.convert("RGB").save(out, optimize=True)


def _checker(w, h):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (w, h), (52, 48, 44, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, 16):
        for x in range(0, w, 16):
            if (x // 16 + y // 16) % 2:
                d.rectangle([x, y, x + 15, y + 15], fill=(66, 61, 56, 255))
    return im


def facings_image(rows: list[tuple[str, dict]], title: str, out: Path) -> None:
    """rows: [(label, {facing: bytes})] — one strip row each, facings in FACE_ORDER, each fitted into a TILE box."""
    from PIL import Image, ImageDraw
    cols = ([f for f in FACE_ORDER if any(f in fs for _l, fs in rows)]
            + sorted({k for _l, fs in rows for k in fs} - set(FACE_ORDER))) or ["single"]
    f = SP._font(14)
    LW, HD, RL = 260, 54, 22
    W = LW + len(cols) * (TILE + 10) + 10
    H = HD + len(rows) * (TILE + RL + 12) + 8
    img = Image.new("RGBA", (W, H), (18, 16, 13, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 8), title, font=f, fill=(240, 200, 120))
    for ci, fc in enumerate(cols):
        d.text((LW + ci * (TILE + 10) + 4, 30), fc, font=f, fill=(200, 190, 170))
    for ri, (lab, faces) in enumerate(rows):
        y = HD + ri * (TILE + RL + 12) + RL
        words, line, lines = lab.split(), "", []
        for w in words:
            if len(line) + len(w) > 28:
                lines.append(line)
                line = ""
            line = (line + " " + w).strip()
        lines.append(line)
        for k, t in enumerate(lines[:8]):
            d.text((10, y + k * 18), t, font=f, fill=(232, 220, 200))
        for ci, fc in enumerate(cols):
            x = LW + ci * (TILE + 10)
            tile = _checker(TILE, TILE)
            if fc in faces:
                a = _img(faces[fc])
                sc = min(TILE / a.width, TILE / a.height)
                a2 = a.resize((max(1, round(a.width * sc)), max(1, round(a.height * sc))),
                              Image.NEAREST if sc >= 1 else Image.LANCZOS)
                tile.alpha_composite(a2, ((TILE - a2.width) // 2, (TILE - a2.height) // 2))
                d.text((x, y - RL + 2), f"{a.width}×{a.height}", font=SP._font(12), fill=(150, 140, 125))
            else:
                ImageDraw.Draw(tile).text((TILE // 2 - 30, TILE // 2 - 8), "none", font=f, fill=(150, 140, 125))
            img.alpha_composite(tile, (x, y))
    img.convert("RGB").save(out, optimize=True)


# ───────────────────────────────────────────────────────────────── main ──

def build(args, out_dir: Path) -> list[Path]:
    rgb, _src = AS.measure_terrain(AS.SUBJECT_GROUND)
    SP.set_terrain(rgb or SP.DEFAULT_TERRAIN)
    R = SP.Resolver()
    idx = L.Index()
    order, _fp = AS.load_order()
    slots = L.scan_def_slots()
    qs = questions(args, R, idx, order, slots)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for n, q in enumerate(qs, 1):
        stem = f"{n:02d}_{q['slug']}"
        cf = _main_face(q["cand"], q["size"])
        p1 = out_dir / f"{stem}_1_full.png"
        b = q["cand"][cf]
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            p1.write_bytes(b)
        else:
            _img(b).save(p1, "PNG")
        p2 = out_dir / f"{stem}_2_scale.png"
        scale_image(q, p2)
        rows = [(q["candLabel"], q["cand"])]
        if q["inst"][1]:
            rows.append(q["inst"])
        for o in qs:                       # the other variants (texPaths) of the same def asked in this run
            if o is not q and o["def"] == q["def"] and o["tex"] != q["tex"]:
                rows.append((f"variant {Path(o['tex']).name}: {o['candLabel']}", o["cand"]))
                if o["inst"][1]:
                    rows.append((f"variant {Path(o['tex']).name}: {o['inst'][0]}", o["inst"][1]))
        p3 = out_dir / f"{stem}_3_facings.png"
        facings_image(rows, f"{q['label']} ({q['def']}) — {q['tex']} — facings and variants, candidate vs installed", p3)
        paths += [p1, p2, p3]
    return paths


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="+", metavar="JOB|DEF", help="artpipe job ids (any facing of a family) or defNames")
    ap.add_argument("--out", help="output dir (default Transient/chat_review_<date>/)")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else L.REPO_ROOT / "Transient" / f"chat_review_{L.now()[:10]}"
    if not out.is_absolute():
        out = L.REPO_ROOT / out
    for p in build(a.items, out.resolve()):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
