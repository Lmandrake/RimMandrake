#!/usr/bin/env python3
"""ICE_ART_RESKIN_BORROWED_RUBBLE_AND_SMELTER: crushed ice and the ice melter wear their own art.

Checks, offline:
  * RM_CrushedIce / RM_IceMelter point at FlowWorks-owned texPaths, not vanilla RubbleRock /
    ElectricSmelter, and carry no <color> tint left over from the borrowed art;
  * every PNG the graphic class needs exists in the mod (Graphic_Random folder: >= 2 variants;
    Graphic_Multi: south, north, east), with a real alpha channel, clear corners, and the canvas
    128 px per cell of drawSize asks for (melter 448x192 / 192x448; ice 256x256);
  * the art ledger installed each file at exactly its committed bytes (events/*.jsonl, kind install);
  * the delegated judge verdict file names every picture and calls each KEEP.
"""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "src/RimMandrake/FlowWorks"
DEFS = MOD / "Defs/Pits/ThingDefs/RM_CrushedIce.xml"
TEX = MOD / "Textures"
EVENTS = ROOT / "infrastructure/state/art/events"
VERDICT = ROOT / "infrastructure/state/delegated/2026-11-05/RM_IceMelter_RM_CrushedIce.json"
BORROWED = {"Things/Filth/RubbleRock", "Things/Building/Production/ElectricSmelter"}

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def graphic(defname):
    for td in ET.parse(DEFS).getroot().iter("ThingDef"):
        if td.findtext("defName") == defname:
            return td.find("graphicData")
    raise SystemExit(f"FAIL: {defname} not found in {DEFS}")


def installed_shas():
    out = {}
    for f in sorted(EVENTS.rglob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("kind") == "install" and ev.get("loc"):
                out[ev["loc"]] = ev.get("sha")  # later events win
    return out


def png_ok(p, size):
    rel = p.relative_to(ROOT).as_posix()
    check(p.is_file(), f"missing {rel}")
    if not p.is_file():
        return
    im = Image.open(p)
    check(im.mode == "RGBA", f"{rel}: mode {im.mode}, wants RGBA")
    check(im.size == size, f"{rel}: canvas {im.size}, wants {size}")
    if im.mode == "RGBA":
        a = im.getchannel("A")
        w, h = im.size
        corners = [a.getpixel(c) for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        check(max(corners) == 0, f"{rel}: corners not transparent {corners}")
        solid = sum(a.histogram()[128:])
        check(solid > 0.15 * w * h, f"{rel}: subject covers only {solid} px")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    check(LEDGER.get(rel) == sha, f"{rel}: art ledger install sha {LEDGER.get(rel)} != file {sha}")
    PICTURES.append(p.name)


LEDGER = installed_shas()
PICTURES = []
check(len(LEDGER) > 100, f"art ledger sanity: only {len(LEDGER)} install events seen under {EVENTS}")

ice = graphic("RM_CrushedIce")
tp = ice.findtext("texPath")
check(tp not in BORROWED and tp.startswith("Things/Item/Resource/FlowWorks/"), f"RM_CrushedIce texPath {tp}")
check(ice.findtext("graphicClass") == "Graphic_Random", "RM_CrushedIce is not Graphic_Random")
check(ice.find("color") is None, "RM_CrushedIce still tinted")
variants = sorted((TEX / tp).glob("*.png"))
check(len(variants) >= 2, f"RM_CrushedIce: {len(variants)} variants in {tp}")
for v in variants:
    png_ok(v, (256, 256))

mel = graphic("RM_IceMelter")
tp = mel.findtext("texPath")
check(tp not in BORROWED and tp.startswith("Things/Building/FlowWorks/"), f"RM_IceMelter texPath {tp}")
check(mel.findtext("graphicClass") == "Graphic_Multi", "RM_IceMelter is not Graphic_Multi")
check(mel.find("color") is None, "RM_IceMelter still tinted")
check(mel.findtext("drawSize") == "(3.5,1.5)", f"RM_IceMelter drawSize {mel.findtext('drawSize')}")
for facing, size in (("south", (448, 192)), ("north", (448, 192)), ("east", (192, 448))):
    png_ok(TEX / f"{tp}_{facing}.png", size)

v = json.loads(VERDICT.read_text(encoding="utf-8"))
rows = {r["picture"]: r["verdict"] for r in v["verdicts"]}
for name in PICTURES:
    check(rows.get(name) == "KEEP", f"judge verdict for {name}: {rows.get(name)}")

if fails:
    print("FAIL")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print(f"PASS ice art: {len(PICTURES)} own pictures, ledger-installed, judged KEEP")
