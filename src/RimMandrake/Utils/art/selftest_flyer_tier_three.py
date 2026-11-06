#!/usr/bin/env python3
"""selftest_flyer_tier_three.py - the tier-3 flyers fly on still-body flip-books cut from their kept statics
(FLYER_TIER_THREE_REBUILD_EASY_WINGS_ONLY; recipe: design/RimMandrake/flyer_stable_body_study.md 3.1, 3.2).

Offline, read-only. Per def (RM_Dwommo, RM_FeverSwarm, RM_Skellick, RM_Skinflap, RM_Skiralim):
  1. the ThingDef can fly (statBases/MaxFlightTime > 0: Pawn_FlightTracker.CanEverFly reads that stat);
     the PawnKindDef names the set's 8-frame flip-book (prefix = config folder + prefix, DrawSize 1.25 multiplier)
     and all 24 PNGs exist;
  2. every installed frame is byte-identical to flyer_cutout's bake of the static <tex>_<facing>.png padded to the
     frame canvas, so the frames are the kept art and nothing else;
  3. still body: plate_identical 1.0 and the flyer_cutout drift/margin gate pass per facing;
  4. flyer_gate.DEF_SETS maps the def to its set, and the committed plan calls the def locked (tier 0);
  5. the wings move in every facing (flyer_cutout motion; MOTION_WAIVED names a facing excused, and why); no frame
     is a banned picture.
RSW_Porg is not here: its flight frames are owner-KEPT, so replacing them is his call (the Porg.json set is staged).
Exit 0 = all pass, 1 = a check failed.
"""
from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import flyer_cutout as FC  # noqa: E402
import flyer_gate as G  # noqa: E402

FACINGS = ("south", "east", "north")
FRAMES = 8
# def -> (defs file, set, static texture base relative to the mod's Textures)
SETS = {
    "RM_Dwommo": ("src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Races/Dwommo.xml", "Dwommo",
                  "Things/Pawn/Animal/Dwommo/RM_Dwommo"),
    "RM_FeverSwarm": ("src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_Miasma_FeverSwarmKarrobel.xml", "FeverSwarm",
                      "Things/Pawn/Animal/RM_FeverSwarm/RM_FeverSwarm"),
    "RM_Skellick": ("src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_FeverWoodBirds.xml", "Skellick",
                    "Things/Pawn/Animal/RM_FeverWoodBirds/RM_Skellick"),
    "RM_Skinflap": ("src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml", "Skinflap",
                    "Things/Pawn/Animal/RM_Skinflap/RM_Skinflap"),
    "RM_Skiralim": ("src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fills.xml", "Skiralim",
                    "Things/Pawn/Animal/RM_Skarrok/RM_Skarrok"),
}

# A facing excused from flyer_cutout motion's "40% of the east facing" floor, with the reason. Only a static whose view
# draws almost no wing belongs here; each entry names the item that owes the drawn wing layer.
MOTION_WAIVED = {"RM_Skellick": {"north": "back-view static draws slivers of folded wing (G2 0.348): 9% of east; "
                                          "a drawn wing layer is owed by SKELLICK_BACKWING_REDRAW_SLIVER_VIEW"}}

fails: list[str] = []


def want(ok: bool, what: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'} {what}")
    if not ok:
        fails.append(what)


def one(d: str, plan: dict, idx) -> None:
    deffile, name, tex = SETS[d]
    root = ET.parse(REPO / deffile).getroot()
    td = [e for e in root.findall("ThingDef") if e.findtext("defName") == d]
    pk = [e for e in root.findall("PawnKindDef") if e.findtext("defName") == d]
    if len(td) != 1 or len(pk) != 1:
        want(False, f"{d}: ThingDef x{len(td)}, PawnKindDef x{len(pk)} in {deffile}")
        return
    td, pk = td[0], pk[0]
    mft = td.findtext("statBases/MaxFlightTime")
    want(mft is not None and float(mft) > 0, f"{d}: statBases/MaxFlightTime > 0 (got {mft})")
    cfg = json.loads((G.SETS / f"{name}.json").read_text())
    folder = REPO / cfg["folder"]
    texroot = REPO / deffile.split("/Defs/")[0] / "Textures"
    prefix = pk.findtext("flyingAnimationFramePathPrefix") or ""
    want(texroot / prefix == folder / cfg["prefix"], f"{d}: flip-book prefix {prefix!r} is the {name} set's")
    want(pk.findtext("flyingAnimationFrameCount") == str(FRAMES), f"{d}: flyingAnimationFrameCount = {FRAMES}")
    want(pk.findtext("flyingAnimationDrawSize") == "1.25"
         and pk.findtext("flyingAnimationDrawSizeIsMultiplier") == "true",
         f"{d}: flyingAnimationDrawSize 1.25 as a multiplier (320 frame over the 256 static)")
    want(texroot / tex == folder / Path(tex).name, f"{d}: static {tex} lives in the set folder")
    want(G.DEF_SETS.get(d) == [name], f"{d}: flyer_gate.DEF_SETS maps it to [{name!r}]")
    row = plan.get(d) or {}
    want(row.get("flipbook") == "locked" and row.get("tier") == 0, f"{d}: the committed plan calls it locked, tier 0")

    paths = {f: [folder / f"{cfg['prefix']}{k}_{f}.png" for k in range(1, FRAMES + 1)] for f in FACINGS}
    missing = [str(p) for ps in paths.values() for p in ps if not p.is_file()]
    want(not missing, f"{d}: {FRAMES * len(FACINGS)} frame PNGs exist ({len(missing)} missing)")
    if missing:
        return
    for f in FACINGS:
        frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths[f]]
        size = frames[0].shape[0]
        static = Image.open(folder / f"{Path(tex).name}_{f}.png").convert("RGBA")
        pad = (size - static.width) // 2
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(static, (pad, pad))
        baked, plate, covers = FC.compose_facing(np.asarray(canvas), cfg["facings"][f], FRAMES)
        want(all(np.array_equal(a, b) for a, b in zip(frames, baked)),
             f"{d} {f}: installed frames == flyer_cutout bake of the static padded {pad} px")
        ident = FC.plate_identical(frames, plate, covers)
        want(ident == 1.0, f"{d} {f}: body plate pixel-identical in every frame (plate_identical {ident:.4f})")
        m = FC.measure(frames)
        want(FC.drift_ok(m, ident) and m["margin"] >= min(FC.MARGIN, pad),
             f"{d} {f}: drift/margin gate (body_px {m['body_px']}, margin {m['margin']})")
    waived = MOTION_WAIVED.get(d, {})
    for f, why in waived.items():
        print(f"WAIVED {d} {f}: motion floor ({why})")
    keep = ",".join(f for f in ("east", "north", "south") if f not in waived)
    r = subprocess.run([sys.executable, str(HERE / "flyer_cutout.py"), "motion", str(folder), "--prefix", cfg["prefix"],
                        "--facings", keep], capture_output=True, text=True)
    want(r.returncode == 0, f"{d}: flyer_cutout motion, the wings move in facings {keep}")
    hits = [p.name for ps in paths.values() for p in ps if L.ban_match(idx, data=p.read_bytes())]
    want(not hits, f"{d}: no frame is a banned picture (hits {hits})")


def main() -> int:
    plan = G.plan_rows()
    idx = L.Index()
    for d in SETS:
        one(d, plan, idx)
    print(f"{'OK' if not fails else 'FAILED'}: {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
