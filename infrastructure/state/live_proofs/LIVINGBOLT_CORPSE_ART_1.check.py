#!/usr/bin/env python3
"""Offline proof for LIVINGBOLT_CORPSE_ART_1: RM_LivingBolt's corpse render is wired and installed.

Exits 0 when (1) the RM_LivingBolt PawnKindDef's life stage carries corpseGraphicData -> RM_LivingBoltCorpse,
Graphic_Multi, drawSize 0.1; (2) RM_LivingBoltCorpse_{east,north,south}.png exist as 256x256 RGBA with real alpha;
(3) the art ledger's live picture at each slot is the file on disk (installed through `art install`). Else exit 1.
Run from the repo root."""
import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "src/RimMandrake/RustCathedral"
TEX = "Things/Pawn/Animal/RM_LivingBolt/RM_LivingBoltCorpse"
bad = []

kind = next((k for k in ET.parse(MOD / "Defs/ThingDefs_Races/RM_LivingBolt.xml").getroot().iter("PawnKindDef")
             if k.findtext("defName") == "RM_LivingBolt"), None)
cg = kind.find("lifeStages/li/corpseGraphicData") if kind is not None else None
if cg is None:
    bad.append("no corpseGraphicData on PawnKindDef RM_LivingBolt")
else:
    for tag, want in (("texPath", TEX), ("graphicClass", "Graphic_Multi"), ("drawSize", "0.1")):
        if (cg.findtext(tag) or "").strip() != want:
            bad.append(f"corpseGraphicData/{tag} = {cg.findtext(tag)!r}, want {want!r}")

sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402
from PIL import Image  # noqa: E402

live = L.Index().live                   # (mod key or mod path, rel_key) -> live event
for f in ("east", "north", "south"):
    p = MOD / "Textures" / f"{TEX}_{f}.png"
    if not p.is_file():
        bad.append(f"missing {p}")
        continue
    im = Image.open(p)
    if im.size != (256, 256) or im.mode != "RGBA" or im.split()[3].getextrema()[0] != 0:
        bad.append(f"{p.name}: {im.size} {im.mode}, want 256x256 RGBA with transparent pixels")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    rel = L.rel_key(f"{TEX}_{f}.png")
    ev = live.get(("src/RimMandrake/RustCathedral", rel)) or live.get((L.mod_key("RustCathedral"), rel)) or {}
    led = ev.get("sha")
    if led != sha:
        bad.append(f"{p.name}: ledger live sha {str(led)[:12]} != file {sha[:12]}")

for b in bad:
    print("FAIL", b)
print("PASS" if not bad else f"{len(bad)} failure(s)")
sys.exit(1 if bad else 0)
