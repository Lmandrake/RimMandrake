#!/usr/bin/env python3
"""selftest_firewasp_flight.py - the Fire Wasp flies on a still-torso flip-book baked from its kept brown art
(FIREWASP_FLIGHT_BUILD_AFTER_BROWN_REGEN).

Offline, read-only. Checks:
  1. RM_FireWasp (ThingDef) carries MaxFlightTime 10, FlightCooldown 5, flightStartChanceOnJobStart 0.1,
     flightSpeedFactor 2.5, canFlyIntoMap true; the PawnKindDef names an 8-frame flip-book whose 24 PNGs exist.
  2. Every installed frame is byte-identical to flyer_cutout's bake of the static FireWasp_<facing>.png (padded to
     the frame canvas), so the frames are the kept art and nothing else.
  3. Still torso: the body plate is pixel-identical in every frame (plate_identical 1.0), and the flyer_cutout
     drift/margin gate passes per facing.
  4. The wings visibly move in every facing (flyer_cutout motion).
  5. No frame is a banned picture (the yellow-black wasp set was purged and banned 2026-10-31).
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

DEF = REPO / "src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsPortedFauna.xml"
CFG = HERE / "flyer_cutout_sets/FireWasp.json"
TEX = REPO / "src/RimMandrake/Pyrelands/Textures"
FACINGS = ("south", "east", "north")
FRAMES = 8

fails: list[str] = []


def want(ok: bool, what: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'} {what}")
    if not ok:
        fails.append(what)


def defs() -> tuple[ET.Element, ET.Element]:
    root = ET.parse(DEF).getroot()
    td = [e for e in root.findall("ThingDef") if e.findtext("defName") == "RM_FireWasp"]
    pk = [e for e in root.findall("PawnKindDef") if e.findtext("defName") == "RM_FireWasp"]
    if len(td) != 1 or len(pk) != 1:
        print(f"FAIL RM_FireWasp ThingDef x{len(td)}, PawnKindDef x{len(pk)} in {DEF}")
        sys.exit(1)
    return td[0], pk[0]


def main() -> int:
    td, pk = defs()
    for path, val in (("statBases/MaxFlightTime", 10.0), ("statBases/FlightCooldown", 5.0),
                      ("race/flightStartChanceOnJobStart", 0.1), ("race/flightSpeedFactor", 2.5)):
        got = td.findtext(path)
        want(got is not None and abs(float(got) - val) < 1e-9, f"ThingDef {path} = {val} (got {got})")
    want((td.findtext("race/canFlyIntoMap") or "").strip() == "true", "ThingDef race/canFlyIntoMap = true")

    cfg = json.loads(CFG.read_text())
    prefix = pk.findtext("flyingAnimationFramePathPrefix") or ""
    want(prefix == "Things/Pawn/Animal/Pyrelands/FireWasp/" + cfg["prefix"], f"flip-book prefix {prefix!r}")
    want(pk.findtext("flyingAnimationFrameCount") == str(FRAMES), f"flyingAnimationFrameCount = {FRAMES}")
    folder = REPO / cfg["folder"]
    want(folder == (TEX / prefix).parent, "config folder is the def's texture folder")

    paths = {f: [TEX / f"{prefix}{k}_{f}.png" for k in range(1, FRAMES + 1)] for f in FACINGS}
    missing = [str(p) for ps in paths.values() for p in ps if not p.is_file()]
    want(not missing, f"{FRAMES * len(FACINGS)} frame PNGs exist ({len(missing)} missing)")
    if missing:
        print("\n".join(missing[:5]))
        return 1

    for f in FACINGS:
        frames = [np.asarray(Image.open(p).convert("RGBA")) for p in paths[f]]
        size = frames[0].shape[0]
        static = Image.open(folder / f"FireWasp_{f}.png").convert("RGBA")
        pad = (size - static.width) // 2
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(static, (pad, pad))
        master = np.asarray(canvas)
        baked, plate, covers = FC.compose_facing(master, cfg["facings"][f], FRAMES)
        same = all(np.array_equal(a, b) for a, b in zip(frames, baked))
        want(same, f"{f}: installed frames == flyer_cutout bake of FireWasp_{f}.png padded {pad} px")
        ident = FC.plate_identical(frames, plate, covers)
        want(ident == 1.0, f"{f}: body plate pixel-identical in every frame (plate_identical {ident:.4f})")
        m = FC.measure(frames)
        ok = FC.drift_ok(m, ident) and m["margin"] >= FC.MARGIN
        want(ok, f"{f}: flyer_cutout drift/margin gate (body_px {m['body_px']}, colour_px {m['colour_px']}, "
                 f"margin {m['margin']})")

    r = subprocess.run([sys.executable, str(HERE / "flyer_cutout.py"), "motion", str(folder), "--prefix", cfg["prefix"]],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    want(r.returncode == 0, "flyer_cutout motion: the wings move in every facing")

    idx = L.Index()
    hits = [str(p.name) for ps in paths.values() for p in ps if L.ban_match(idx, data=p.read_bytes())]
    want(not hits, f"no frame is a banned picture ({len(idx.bans)} bans checked; hits {hits})")

    print(f"{'OK' if not fails else 'FAILED'}: {len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
