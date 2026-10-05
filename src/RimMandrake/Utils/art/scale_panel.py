#!/usr/bin/env python3
"""scale_panel.py — in-game size (cells) + true-scale panel for a biome art-sheet row.

Owner, 2026-10-04: "I also need to know the cell size for each of these flora and fauna too, with a
realistic game human for scale. It's the only way I can judge the art quality/resolution."

SIZE IS A MEASUREMENT (review-sheets §1). Every value is read from the LIVE def dump (defs.sqlite,
captured out of the running game, so post-inheritance and post-patch — exactly what the engine
reads), then cross-checked against the raw XML the game loaded (the deployed mod's Defs file named by
the dump's own `fileName`), following ParentName, and against every <Operation> in the declaring mod's
and our mods' Patches that names the def and a size field. The row prints the source of each value;
a value not measured says FALLBACK.

  animals  cells = max(adult lifeStage bodyGraphicData.drawSize)           (PawnRenderNode_AnimalPart)
  plants   quad  = graphicData.drawSize.x × plant.visualSizeRange.max, a SQUARE   (Plant.Print,
           read via RimSage 2026-10-04); maxMeshCount n>1 prints n quads on a √n sub-grid of ONE
           cell; a single-mesh plant is centred on its cell but lifted so its bottom never drops below
           the cell's bottom edge.

RENDERING follows the image_scaling skill: the FULL texture canvas maps onto the draw quad (that is
what the engine does — margins included), downscaled BOX in premultiplied alpha (≈ GPU mipmap),
composited over the biome's ground colour. The PRIMARY view is a max-zoom scene at 128–256 px per cell
(the art near its native resolution) with the vanilla human beside it at the same scale: the owner plays
with enhanced-zoom mods, so vanilla's 96 px/cell ceiling does not hold (owner, 2026-10-04: "Please don't
down-resolve the imagery so badly"). Normal play (32 px/cell) is a small secondary; 18 lives only in the
click-to-enlarge strip.

The human is a vanilla colonist composed as the engine does it (body, T-shirt in Cloth, head, Mop hair): Naked_Male_south and
Male_Average_Normal_south (both 128² on the 1.5-cell humanlike mesh), the head raised by BodyTypeDef
Male headOffset.y = 0.34 (live dump). The vanilla control is Core's Rat (drawSize 1.25, 128²).

    python3 scale_panel.py --biome RM_LongShade      # print the size table (no rendering)
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from functools import lru_cache
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import game_paths as GP  # noqa: E402
from art_zoom_sim import BG as TERRAIN  # noqa: E402   (Ash'karr desert brown, the zoom-sim's own)


def set_terrain(rgb):
    """Per-biome ground colour for the panel backdrop (module global read at render time)."""
    global TERRAIN
    TERRAIN = tuple(int(c) for c in rgb)

DB = Path(GP.DUMP_ROOT) / "defs.sqlite"
VANILLA_TEX = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core")
TIERS = [(32, "normal play"), (18, "zoomed out")]   # secondary tiers (full strip only)
ZOOM_MIN, ZOOM_MAX = 128, 256   # primary scene px/cell: the art near native, clamped
SCENE_PPC = 64            # the human-for-scale scene: RimWorld's own 64 px per cell texture ratio
OWNER_PPC = 128           # owner ruling (image_scaling skill): canvas = drawSize×128 → next pow2
LOW_PPC = 64              # below this, detail is lost at max zoom-in
HUMAN_MESH = 1.5
HEAD_OFFSET_Y = 0.34      # BodyTypeDef Male headOffset.y, live dump 2026-10-04
RAT_DRAW = 1.25           # Core Rat adult drawSize, live dump (Races_Animal_SquirrelGroup.xml)
SIZE_FIELDS = ("drawSize", "visualSizeRange", "maxMeshCount", "bodyGraphicData", "graphicData", "lifeStages")


def _win2wsl(p: str) -> Path:
    m = re.match(r"^([A-Za-z]):\\(.*)$", p or "")
    return Path(f"/mnt/{m.group(1).lower()}/" + m.group(2).replace("\\", "/")) if m else Path(p)


def _vec(v):
    if isinstance(v, dict):
        return [v.get("x"), v.get("y")]
    if isinstance(v, str):
        m = re.findall(r"-?\d+(?:\.\d+)?", v)
        if len(m) >= 2:
            return [float(m[0]), float(m[1])]
        if len(m) == 1:
            return [float(m[0]), float(m[0])]
    return [None, None]


def _fr(v):  # FloatRange max
    if isinstance(v, dict):
        return v.get("max")
    if isinstance(v, str):
        m = re.findall(r"-?\d+(?:\.\d+)?", v)
        return float(m[-1]) if m else None
    return None


def _fmt(x):
    return ("%g" % x) if isinstance(x, (int, float)) else str(x)


class Resolver:
    def __init__(self, db_path: Path = DB):
        self.db = sqlite3.connect(str(db_path))
        prov = dict(self.db.execute("select key, value from provenance"))
        self.captured = prov.get("captured_utc", "?")
        self.fingerprint = prov.get("modlist_fingerprint", "?")
        self.mods = {pid: (name, _win2wsl(root)) for _lo, name, pid, root in
                     self.db.execute("select load_order, name, package_id, root_dir from mods")}

    # ── dump ──
    def _def(self, name: str, typ: str):
        r = self.db.execute("select json from defs where def_name=? and def_type=?", (name, typ)).fetchone()
        return json.loads(r[0])["fields"] if r else None

    def _kind_for(self, race: str):
        k = self._def(race, "PawnKindDef")
        if k and k.get("race") == race:
            return race, k
        for n, js in self.db.execute("select def_name, json from defs where def_type='PawnKindDef' and json like ?",
                                     (f'%"race": "{race}"%',)):
            f = json.loads(js)["fields"]
            if f.get("race") == race:
                return n, f
        return None, None

    # ── XML the game loaded ──
    @lru_cache(maxsize=None)
    def _mod_files(self, pid: str) -> tuple:
        root = self.mods.get(pid, (None, None))[1]
        if not root or not root.is_dir():
            return ()
        out = []
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in ("Textures", "Sounds", "Assemblies", "Source", ".git", "About", "Languages")]
            out += [Path(dp) / f for f in fns if f.endswith(".xml")]
        return tuple(out)

    @lru_cache(maxsize=None)
    def _parse(self, p: Path):
        try:
            return ET.parse(p).getroot()
        except Exception:                                   # noqa: BLE001
            return None

    def _find_def(self, pid: str, file_name: str, def_name: str, typ: str):
        for p in self._mod_files(pid):
            if p.name != file_name:
                continue
            root = self._parse(p)
            if root is None:
                continue
            for el in root:
                if el.tag == typ and (el.findtext("defName") or "").strip() == def_name:
                    return p, el
        return None, None

    def _find_parent(self, pid: str, name: str, typ: str):
        for scope in [pid] + [x for x in self.mods if x.startswith("ludeon.")]:
            for p in self._mod_files(scope):
                if "Patches" in p.parts:
                    continue
                root = self._parse(p)
                if root is None:
                    continue
                for el in root:
                    if el.tag == typ and el.get("Name") == name:
                        return p, el
        return None, None

    def _xml_value(self, pid, file_name, def_name, typ, getter):
        """(value, how) from the raw XML, following ParentName. how names file + declared/inherited."""
        p, el = self._find_def(pid, file_name, def_name, typ)
        if el is None:
            return None, f"XML: {def_name} not found in {file_name}"
        chain = []
        while el is not None:
            v = getter(el)
            if v is not None:
                where = f"{p.name}" + (f" (inherited via {' → '.join(chain)})" if chain else " (declared)")
                return v, where
            parent = el.get("ParentName")
            if not parent:
                break
            chain.append(parent)
            p, el = self._find_parent(pid, parent, typ)
            if el is None:
                return None, f"{file_name}: not declared; parent {parent} NOT FOUND (chain {' → '.join(chain)})"
        return None, f"{file_name}: declared nowhere in the chain" + (f" {' → '.join(chain)}" if chain else "")

    @lru_cache(maxsize=None)
    def _patch_ops(self) -> tuple:
        ops = []
        pids = [x for x in self.mods if x.startswith("mandrake.")]
        for pid in pids:
            for p in self._mod_files(pid):
                if "Patches" not in p.parts:
                    continue
                root = self._parse(p)
                if root is None:
                    continue
                for op in root.iter():
                    xp = op.findtext("xpath")
                    if xp and any(f in (xp + ET.tostring(op, encoding="unicode")) for f in SIZE_FIELDS):
                        ops.append((pid, p.name, xp))
        return tuple(ops)

    def _patches_for(self, *names):
        hits = []
        for pid, fn, xp in self._patch_ops():
            if any(f'"{n}"' in xp or f"'{n}'" in xp for n in names if n) and any(f in xp for f in SIZE_FIELDS):
                hits.append(f"{fn}")
        return sorted(set(hits))

    # ── public ──
    def describe(self, row: dict) -> dict:
        """The in-game label + description the player reads: ThingDef label/description from the LIVE dump
        (post-inheritance, post-patch). {} when no def of the row is in the dump."""
        for n in [row["key"]] + [x for x in (row.get("defNames") or []) if x != row["key"]]:
            td = self._def(n, "ThingDef")
            if td:
                return {"def": n, "label": td.get("label") or "", "description": (td.get("description") or "").strip(),
                        "source": f"live def dump {self.captured[:10]} · ThingDef {n}"}
        return {}

    def size(self, row: dict) -> dict:
        names = [row["key"]] + [n for n in (row.get("defNames") or []) if n != row["key"]]
        for n in names:
            td = self._def(n, "ThingDef")
            if td:
                break
        else:
            return {"status": "fallback", "cells": 1.0, "source": "FALLBACK 1 cell — no ThingDef in the live dump",
                    "kind": row.get("kind")}
        tmod = (td.get("modContentPack") or {}).get("packageId", "")
        dump_src = f"live def dump {self.captured[:16].replace('T', ' ')}Z"
        if td.get("race"):
            kname, kd = self._kind_for(n)
            body = (td.get("race") or {}).get("baseBodySize")
            ds, color = [None, None], None
            if kd:
                for st in reversed(kd.get("lifeStages") or []):
                    bg = (st or {}).get("bodyGraphicData") or {}
                    if bg.get("drawSize") is not None:
                        ds = _vec(bg["drawSize"])
                        col = bg.get("color") or {}
                        color = [col.get("r", 1), col.get("g", 1), col.get("b", 1)]
                        break
            stats = td.get("statBases")
            if body is None and isinstance(stats, list):
                pass
            if ds[0] is None:
                return {"status": "fallback", "kind": "animal", "def": n, "cells": 1.0, "bodySize": body,
                        "source": f"FALLBACK 1 cell — PawnKindDef {kname or '?'} has no adult drawSize in the dump"}
            kmod = (kd.get("modContentPack") or {}).get("packageId", "")

            def g(el):
                ls = el.find("lifeStages")
                if ls is None:
                    return None
                lis = list(ls)
                for li in reversed(lis):
                    d = li.find("bodyGraphicData/drawSize")
                    if d is not None and d.text:
                        return _vec(d.text.strip())
                return None
            xv, xhow = self._xml_value(kmod, kd.get("fileName", ""), kname, "PawnKindDef", g)
            pat = self._patches_for(kname, n)
            cells = max(x for x in ds if x is not None)
            check = self._agree(ds, xv, xhow, pat)
            return {"status": "measured", "kind": "animal", "def": n, "kindDef": kname, "drawSize": ds,
                    "bodySize": body, "cells": cells, "mesh": 1, "quad": cells, "color": color,
                    "source": f"{dump_src} · PawnKindDef {kname}, last lifeStage bodyGraphicData · {check}",
                    "xml": {"value": xv, "how": xhow, "patches": pat, "mod": kmod, "file": kd.get("fileName")}}
        gd = td.get("graphicData") or {}
        pl = td.get("plant") or {}
        ds = _vec(gd.get("drawSize"))
        vmax = _fr(pl.get("visualSizeRange"))
        mesh = int(pl.get("maxMeshCount") or 1)
        if ds[0] is None:
            return {"status": "fallback", "kind": "plant", "def": n, "cells": 1.0,
                    "source": "FALLBACK 1 cell — graphicData.drawSize absent in the dump"}
        quad = ds[0] * (vmax if vmax else 1.0)

        def gds(el):
            d = el.find("graphicData/drawSize")
            return _vec(d.text.strip()) if d is not None and d.text else None

        def gvs(el):
            d = el.find("plant/visualSizeRange")
            return _fr(d.text.strip()) if d is not None and d.text else None

        def gmm(el):
            d = el.find("plant/maxMeshCount")
            return int(d.text.strip()) if d is not None and d.text else None
        fn = td.get("fileName", "")
        xds, hds = self._xml_value(tmod, fn, n, "ThingDef", gds)
        xvs, hvs = self._xml_value(tmod, fn, n, "ThingDef", gvs)
        xmm, hmm = self._xml_value(tmod, fn, n, "ThingDef", gmm)
        pat = self._patches_for(n)
        checks = [self._agree(ds, xds, hds, pat, "drawSize", engine_default=[1.0, 1.0]),
                  self._agree(vmax, xvs, hvs, pat, "visualSizeRange.max", engine_default=None),
                  self._agree(mesh, xmm, hmm, pat, "maxMeshCount", engine_default=1)]
        col = gd.get("color") or {}
        return {"status": "measured", "kind": "plant", "def": n, "drawSize": ds, "visualMax": vmax, "mesh": mesh,
                "color": [col.get("r", 1), col.get("g", 1), col.get("b", 1)],
                "quad": quad, "cells": quad if mesh == 1 else 1.0,
                "source": f"{dump_src} · ThingDef {n} · " + " · ".join(checks),
                "xml": {"drawSize": [xds, hds], "visualMax": [xvs, hvs], "mesh": [xmm, hmm], "patches": pat,
                        "mod": tmod, "file": fn}}

    @staticmethod
    def _agree(dump, xv, xhow, patches, label="drawSize", engine_default="_none"):
        pat = f"; patched by {', '.join(patches)}" if patches else ""
        if xv is None:
            if engine_default != "_none" and engine_default is not None and dump == engine_default:
                return f"{label}: XML {xhow} → engine default{pat}"
            return f"{label}: XML {xhow}{pat}"
        same = (xv == dump) if not isinstance(xv, list) else all(
            a is not None and b is not None and abs(a - b) < 1e-4 for a, b in zip(xv, dump))
        if same:
            return f"{label}: XML agrees, {xhow}{pat}"
        return f"⚠ {label}: XML {xhow} says {xv}{pat or ' and NO patch found to explain it'}"


# ═════════════════════════════════════════════════════════════ rendering
def _premul_resize(im, w, h):
    from PIL import Image
    im = im.convert("RGBA")
    # zero RGB of fully transparent texels (image_scaling skill: the halo trap)
    a = im.getchannel("A")
    rgb = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rgb.paste(im, mask=a.point(lambda v: 255 if v else 0))
    filt = Image.BOX if (w < im.width or h < im.height) else Image.BILINEAR
    return rgb.convert("RGBa").resize((max(1, w), max(1, h)), filt).convert("RGBA")


SKIN = (0.9490196, 0.78039217, 0.549019635)   # GeneDef Skin_Melanin6 skinColorBase, live dump
RAT_COLOR = (0.431372553, 0.372549027, 0.321568638)   # Rat adult bodyGraphicData.color, live dump


def _tint(im, rgb):
    """The engine multiplies a Cutout graphic by its colour (vanilla body/head/rat art is greyscale)."""
    if not rgb or all(abs(c - 1) < 1e-3 for c in rgb[:3]):
        return im
    r, g, b, a = im.split()
    r, g, b = (ch.point(lambda v, k=k: round(v * k)) for ch, k in zip((r, g, b), rgb))
    from PIL import Image
    return Image.merge("RGBA", (r, g, b, a))


@lru_cache(maxsize=None)
def _vanilla(name):
    from PIL import Image
    return Image.open(VANILLA_TEX / f"{name}.png").convert("RGBA")


CLOTH = (0.635294139, 0.6156863, 0.596078455)   # ThingDef Cloth stuffProps.color, live dump — the shirt's stuff
HAIR_COLOR = (0.32, 0.22, 0.13)                 # an ordinary dark-brown hair colour
HUMAN_LAYERS = "Naked_Male_south + ShirtBasic_Male_south (Cloth) + Male_Average_Normal_south + Mop_south"


def human_sprite(ppc: int):
    """A vanilla colonist as seen in play, south facing, in the engine's draw order: naked body, OnSkin
    apparel (T-shirt, Apparel_BasicShirt in Cloth — vanilla pants have no worn graphic), head, hair. Body and
    apparel on the 1.5-cell body mesh; head and hair on the 1.5-cell head mesh raised by headOffset.y.
    Returns (img, mesh_px, head_px) where the BODY mesh is the bottom mesh_px×mesh_px square of img."""
    from PIL import Image
    m = round(HUMAN_MESH * ppc)
    hoff = round(HEAD_OFFSET_Y * ppc)
    body = _tint(_premul_resize(_vanilla("Naked_Male_south"), m, m), SKIN)
    shirt = _tint(_premul_resize(_vanilla("ShirtBasic_Male_south"), m, m), CLOTH)
    head = _tint(_premul_resize(_vanilla("Male_Average_Normal_south"), m, m), SKIN)
    hair = _tint(_premul_resize(_vanilla("Mop_south"), m, m), HAIR_COLOR)
    img = Image.new("RGBA", (m, m + hoff), (0, 0, 0, 0))
    img.alpha_composite(body, (0, hoff))
    img.alpha_composite(shirt, (0, hoff))
    img.alpha_composite(head, (0, 0))
    img.alpha_composite(hair, (0, 0))
    return img, m, hoff


def _font(sz):
    from PIL import ImageFont
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _art_quads(art, size, ppc):
    """[(img, x_cells, y_cells_top)] relative to the subject cell's bottom-left, y up in cells."""
    art = _tint(art, size.get("color"))
    if size["kind"] == "plant":
        q = size["quad"]
        mesh = size.get("mesh") or 1
        if mesh > 1:
            side = int(round(mesh ** 0.5)) or 1
            step = 1.0 / side
            spr = _premul_resize(art, max(1, round(q * ppc)), max(1, round(q * ppc)))
            out = []
            for i in range(side * side):
                cx, cz = (i // side + 0.5) * step, (i % side + 0.5) * step
                out.append((spr, cx - q / 2, cz + q / 2))
            out.sort(key=lambda t: -t[2])      # back rows first (higher z drawn first)
            return out
        spr = _premul_resize(art, max(1, round(q * ppc)), max(1, round(q * ppc)))
        cz = 0.5
        vis = size.get("visualMax") or 1.0
        if cz - vis / 2 < 0:   # Plant.Print: `if (z - num2/2 < Position.z) z = Position.z + num2/2` —
            cz = vis / 2       # num2 is visualSize, NOT the quad, so a drawSize>1 plant still overhangs
        return [(spr, 0.5 - q / 2, cz + q / 2)]
    dx, dy = size["drawSize"]
    w, h = max(1, round(dx * ppc)), max(1, round(dy * ppc))
    spr = _premul_resize(art, w, h)
    return [(spr, 0.5 - dx / 2, 0.5 + dy / 2)]


def _extent(quads, ppc, rat_on):
    """(cells above row 0, cells below row 0, subject x origin, total cells wide) — a drawSize larger than one cell
    overhangs its cell on every side (it is centred on it), so the scene grows DOWN and right as well as up."""
    import math
    above = max(0.5 + HUMAN_MESH / 2 + HEAD_OFFSET_Y, 0.5 + RAT_DRAW / 2, max(t for _, _, t in quads), 1.0)
    below = max(0.0, -min(t - im.height / ppc for im, _, t in quads))
    left = max(0.0, -min(x for _, x, _ in quads))
    sx0 = (2.0 if rat_on else 1.0) + left
    right = max(sx0 + 1.0, max(sx0 + x + im.width / ppc for im, x, _ in quads))
    return math.ceil(above - 1e-6), math.ceil(below - 1e-6), sx0, math.ceil(right - 1e-6)


def _scene(art, size, ppc, f, rat_on=True):
    """human | rat | subject on the cell grid, all at ppc px per cell, over terrain (rat_on=False: human | subject)."""
    from PIL import Image, ImageDraw
    hum, hm, hoff = human_sprite(ppc)
    rat = _tint(_premul_resize(_vanilla("Rat_east"), round(RAT_DRAW * ppc), round(RAT_DRAW * ppc)), RAT_COLOR)
    quads = _art_quads(art, size, ppc)
    na, nb, sx0, total_w = _extent(quads, ppc, rat_on)
    lab = 13 if ppc < 100 else 18
    W, H = round(total_w * ppc), round((na + nb) * ppc) + lab
    sc = Image.new("RGBA", (W, H), TERRAIN + (255,))
    d = ImageDraw.Draw(sc)
    base = H - lab

    def Y(c):                       # c in cells above row 0's bottom edge
        return round(base - (c + nb) * ppc)
    line = tuple(max(0, c - 26) for c in TERRAIN) + (255,)
    for i in range(total_w + 1):
        d.line([(round(i * ppc), 0), (round(i * ppc), base)], fill=line)
    for j in range(-nb, na + 1):
        d.line([(0, Y(j)), (W, Y(j))], fill=line)
    sc.alpha_composite(hum, (round((0.5 - HUMAN_MESH / 2) * ppc), Y(0.5 + HUMAN_MESH / 2) - hoff))
    if rat_on:
        sc.alpha_composite(rat, (round((1.5 - RAT_DRAW / 2) * ppc), Y(0.5 + RAT_DRAW / 2)))
    for im, x, t in quads:
        sc.alpha_composite(im, (round((sx0 + x) * ppc), Y(t)))
    d.rectangle([0, base, W, H], fill=(18, 16, 13, 255))
    if ppc >= 44:
        lf = _font(14) if ppc >= 100 else f
        d.text((2, base), "human", font=lf, fill=(200, 190, 170))
        if rat_on:
            d.text((round(1.0 * ppc) + 2, base), "rat", font=lf, fill=(200, 190, 170))
        d.text((round(max(sx0 - 0.0, 1.0 if not rat_on else 2.0) * ppc) + 2, base), "this", font=lf, fill=(232, 182, 76))
        return sc
    return sc.crop((0, 0, W, base))


def _tier_tile(art, size, t_ppc):
    import math
    from PIL import Image
    qs = _art_quads(art, size, t_ppc)
    ox = -min(0.0, min(x for _, x, _ in qs))
    wc = max(1.0, max(x + im.width / t_ppc for im, x, _ in qs) + ox)
    tc = max(1.0, max(t for _, _, t in qs))
    tw, th = max(1, math.ceil(wc * t_ppc)), max(1, math.ceil(tc * t_ppc))
    tile = Image.new("RGBA", (tw, th), TERRAIN + (255,))
    for im, x, top in qs:
        tile.alpha_composite(im, (round((ox + x) * t_ppc), round((tc - top) * t_ppc)))
    return tile


def _crop_centre(im, w, h):
    if im.width <= w and im.height <= h:
        return im, False
    cx, cy = im.width // 2, im.height // 2
    x0, y0 = max(0, min(im.width - w, cx - w // 2)), max(0, min(im.height - h, cy - h // 2))
    return im.crop((x0, y0, x0 + min(w, im.width), y0 + min(h, im.height))), True


def _strip(parts, f, bg=(18, 16, 13, 255), gap=10, lab=13):
    from PIL import Image, ImageDraw
    H = max(p.height for _, p in parts) + lab
    ws = [max(p.width, round(f.getlength(n)) + 2) for n, p in parts]
    W = sum(ws) + gap * (len(parts) - 1)
    out = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(out)
    x = 0
    for (name, p), w in zip(parts, ws):
        out.alpha_composite(p, (x, H - lab - p.height))
        d.text((x, H - lab), name, font=f, fill=(200, 190, 170))
        x += w + gap
    return out


ZOOM_W, ZOOM_H = 640, 440     # px: the in-row max-zoom scene's budget (human | subject)
NORMAL_PPC = 32               # the small secondary scene: normal play


def _cells(art, size, rat_on):
    """(cells tall, cells wide) of a scene, independent of ppc."""
    na, nb, _sx0, w = _extent(_art_quads(art, size, 64), 64, rat_on)
    return na + nb, w


def zoom_ppc(native, top_cells, w_cells, wmax=ZOOM_W, hmax=ZOOM_H):
    """(ppc, fitted): the art near native, clamped 128–256; shrunk only when the scene cannot fit the budget."""
    want = int(min(ZOOM_MAX, max(ZOOM_MIN, native or ZOOM_MIN)))
    fit = int(min((hmax - 18) / top_cells, wmax / w_cells))
    return (want, False) if want <= fit else (max(24, fit), True)


def _crop_scene(sc, art, size, ppc):
    """The max-zoom scene cut to the row budget: from the left edge (the human stays in view), vertically centred
    on row 1 (the human's middle and the subject's cell); the label strip is kept."""
    from PIL import Image
    na, nb, _sx0, _w = _extent(_art_quads(art, size, ppc), ppc, False)
    lab = 13 if ppc < 100 else 18
    base = sc.height - lab
    w, hwin = min(sc.width, ZOOM_W), min(base, ZOOM_H - lab)
    yc = base - (1.0 + nb) * ppc
    y0 = int(max(0, min(base - hwin, yc - hwin / 2)))
    out = Image.new("RGBA", (w, hwin + lab))
    out.paste(sc.crop((0, y0, w, y0 + hwin)), (0, 0))
    out.paste(sc.crop((0, base, w, sc.height)), (0, hwin))
    return out


def render_panel(art_bytes: bytes, size: dict, out_png: Path, full_png: Path) -> dict:
    """Two PNGs. COMPACT (in the row): human | subject at MAX ZOOM — the art near native resolution,
    128–256 px per cell (shrunk only if the subject is too big for the row, and then labelled) — plus a
    small normal-play scene (human · rat · subject at 32 px/cell). FULL (click-to-enlarge): the max-zoom
    scene never shrunk, then normal play 32 and zoomed-out 18, each also ×4 nearest."""
    from PIL import Image
    art = Image.open(BytesIO(art_bytes)).convert("RGBA")
    f = _font(11)
    quad_x = size["drawSize"][0] if size["kind"] == "animal" else size["quad"]
    native = round(art.width / quad_x) if quad_x else None
    top, w = _cells(art, size, False)
    zfull, _ = zoom_ppc(native, top, w, 10 ** 6, 10 ** 6)
    zppc, fitted = zoom_ppc(native, top, w)
    parts = [(f"max zoom {zfull} px/cell — human | this", _scene(art, size, zfull, f, rat_on=False))]
    for t_, lab in TIERS:
        tile = _scene(art, size, t_, f) if t_ == NORMAL_PPC else _tier_tile(art, size, t_)
        parts.append((f"{t_}/cell {lab}", tile))
        parts.append((f"{t_} ×4 nearest", tile.resize((tile.width * 4, tile.height * 4), Image.NEAREST)))
    full = _strip(parts, _font(13), gap=16, lab=18)
    full_png.parent.mkdir(parents=True, exist_ok=True)
    full.convert("RGB").save(full_png, optimize=True)
    # never down-resolve below the art's own px/cell (or 128): a subject too big for the row at that scale is
    # CROPPED around the human and the subject's base, not shrunk — the whole of it is the normal-play scene
    floor_ppc = min(native or ZOOM_MIN, ZOOM_MIN)
    cropped = fitted and zppc < floor_ppc
    if cropped:
        zppc, fitted = floor_ppc, False
    zoom = _scene(art, size, zppc, f, rat_on=False)
    if cropped:
        zoom = _crop_scene(zoom, art, size, zppc)
    normal = _scene(art, size, NORMAL_PPC, f)
    note = " (cropped, not shrunk — click for whole)" if cropped else ""
    if fitted:
        note = (f" (art's native is {native} — no detail lost)" if native and zppc >= native
                else " (shrunk to fit the row — click for full)")
    comp = _strip([((f"max zoom · {zppc} px/cell" + note), zoom),
                   ("normal play · 32/cell", normal)], f, gap=10, lab=15)
    comp.convert("RGB").save(out_png, optimize=True)
    return {"srcPx": list(art.size), "pxPerCell": native, "zoomPpc": zppc, "zoomFitted": bool(fitted and not (native and zppc >= native)), "zoomCropped": bool(cropped),
            "zoomFullPpc": zfull, "compactPx": list(comp.size), "fullPx": list(full.size)}


def ppc_verdict(ppc):
    """Against the enhanced-zoom range (owner, 2026-10-04): 128–256 px/cell is what max zoom resolves."""
    if ppc is None:
        return ""
    if ppc > ZOOM_MAX:
        return "above 256/cell — beyond even enhanced max zoom"
    if ppc >= OWNER_PPC * 0.95:
        return "in the 128–256/cell range enhanced zoom resolves"
    if ppc >= LOW_PPC:
        return "below 128/cell — soft at enhanced max zoom"
    return "BELOW 64/cell — detail lost when zoomed in"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--biome", default="RM_LongShade")
    ap.add_argument("--census", default=str(HERE.parents[2].parent / "Transient" / "biome_ffar" / "census.json"))
    a = ap.parse_args()
    rows = json.loads(Path(a.census).read_text())["biomes"][a.biome]["rows"]
    R = Resolver()
    for r in rows:
        s = R.size(r)
        print(f"{r['key']:34s} {s['status']:9s} cells={_fmt(round(s['cells'], 3)):6s} | {s['source']}")
