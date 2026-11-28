#!/usr/bin/env python3
"""RIMMANDRAKE_DRAW_TALL_CARGO_XTALL_TANKS_IN_HIS_PICKED_DESIGNS: draw the tall, cargo and extra-tall tanks of the Industrial
and Futuristic looks in his picked base-tank designs (2026-11-22: Industrial C gunmetal on cast saddles, Futuristic A
white composite; OWNER.jsonl 2026-11-23T01:31:54Z and 01:34:03Z).

image 1 = the tank's shape master (v3/_master/<Tank>.png: camera, silhouette, canvas, footprint held),
image 2 = his picked base tank (the installed Tank/<Look>/RM_LiquidTank.png: the design language).
Output raw/<Tank>_<Look>.png; fit.py puts each on its master's canvas.

    gen_picked.py [JOB ...]     (no args: every job whose raw PNG is missing; JOB = <Tank>_<Look>)
"""
import concurrent.futures as cf
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
import image_skills  # noqa: E402

MASTER = HERE.parent / "v3" / "_master"
TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank"
RAW = HERE / "raw"

SHAPES = {
    "RM_LiquidTankTall": "an upright cylindrical liquid tank, taller than wide, standing on a low base",
    "RM_UniversalCargoTank": "a short horizontal cargo tank lying left to right on a low skid base, with one outlet at "
                             "the front-centre bottom",
    "RM_UniversalCargoTankXTall": "a very tall upright cylindrical cargo tank, about twice as tall as wide, standing on a "
                                  "low base, with one outlet at the front-centre bottom",
}
LOOKS = {
    "Industrial": (
        "INDUSTRIAL, design C of image 2: heavy painted steel in dark gunmetal and slate grey with the paint mostly whole; "
        "big bolted flanges and welded seams; a raised bolted manway hatch; a short yellow-and-black hazard band as an "
        "accent; a round brass-rimmed ANALOG pressure dial on a short stem and a small red hand-wheel valve; the tank "
        "rests on heavy CAST-STEEL SADDLE supports like image 2's. Honest working wear only: scuffed paint on edges, "
        "grease and dust at the base, a few small rust weeps at a bolt. Maintained, not rusty, not a wreck."
    ),
    "Futuristic": (
        "FUTURISTIC, design A of image 2: a seamless white ceramic-composite shell with flush hairline panel seams and "
        "brushed-titanium end rings or collars; a slim recessed pale-cyan LED level bar showing the liquid level; a small "
        "lit rectangular screen with a glowing graph readout and two tiny status lights; low sleek graphite saddle feet "
        "integrated into the shell like image 2's. Clean, at most faint dust at the base. Absolutely no analog dials, no "
        "rivets, no exposed bolts, no hand wheels, no brass, no exposed pipework, no hazard stripes."
    ),
}

PROMPT = (
    "Use $imagegen to edit. Draw a game sprite for RimWorld. Image 1 fixes the SHAPE ONLY: {shape}. Copy exactly image 1's "
    "camera (RimWorld building camera, orthographic, about 35 degrees above horizontal, the top surface visible and lit, "
    "light from overhead-front), its silhouette, proportions, canvas size and the tank's position on the canvas, so the "
    "new tank covers the same area. Do NOT copy image 1's materials, rust, rivets, patches, wood, colours or its small "
    "fittings. Image 2 is the player's PICKED DESIGN for this family of tanks: redraw image 1's shape as a sibling of "
    "image 2, in the same design language, materials, colours, details and finish, so the two read as one product line "
    "from one maker. STYLE: {look} Painterly-realistic RimWorld mod art, a few bold readable shapes whose silhouette is "
    "carried by value and colour contrast, with NO drawn outline or keyline. Real transparent background (alpha "
    "channel), no ground, no cast shadow, no border, no text or legible letters, no logos. Same canvas aspect as image 1."
)


def job(name):
    tank, look = name.rsplit("_", 1)
    out = RAW / f"{name}.png"
    cmd = [sys.executable, str(image_skills.require(image_skills.CODEX_IMAGE)), "edit", "--out", str(out),
           "--prompt", PROMPT.format(shape=SHAPES[tank], look=LOOKS[look]),
           "--image", str(MASTER / f"{tank}.png"), "--image", str(TEX / look / "RM_LiquidTank.png"),
           "--timeout", "1800", "--force"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return name, r.returncode, out.exists(), (r.stdout + r.stderr)[-600:]


def main(argv):
    RAW.mkdir(parents=True, exist_ok=True)
    names = argv or [f"{t}_{l}" for t in SHAPES for l in LOOKS if not (RAW / f"{t}_{l}.png").exists()]
    rc = 0
    with cf.ThreadPoolExecutor(3) as ex:
        for name, code, ok, tail in ex.map(job, names):
            print(f"== {name} rc={code} exists={ok}\n{tail if code else ''}", flush=True)
            rc = rc or code or (0 if ok else 1)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
