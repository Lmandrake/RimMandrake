#!/usr/bin/env python3
"""Generate NEW FlowWorks liquid-tank designs (not repaints) per look brief, one Codex image job at a time.

Image 1 of each edit is the accepted Scrapper tank: it anchors camera, scale, proportions and the two end pipe ports only.
Looks: design/specs/2026-11-22-flowworks-look-briefs/looks.md.  Item RIMMANDRAKE_GENERATE_FLOWWORKS_TANK_DESIGNS_FIRST_RUN_ONLY_REPAINTED.

    gen_tanks.py [JOB ...]       (no args: every job whose raw PNG is missing)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
import image_skills  # noqa: E402

SCRAPPER = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/Scrapper/RM_LiquidTank.png"
RAW = HERE / "raw"

COMMON = (
    "Use $imagegen to edit. Draw a game sprite for RimWorld: a horizontal liquid storage tank that sits on a 2x2 cell "
    "footprint. Image 1 is the reference for CAMERA, SCALE AND LAYOUT ONLY: copy exactly its camera (RimWorld building "
    "camera, orthographic, about 35 degrees above horizontal, the top surface of the tank visible and lit, light from "
    "overhead-front), its proportions (a horizontal capsule lying left to right that fills the full canvas width and about "
    "the middle 55 percent of the height), and its two pipe connection ports, one centred on the left end cap and one "
    "centred on the right end cap, reaching the left and right edges. Do NOT copy its materials, rivets, colours, rust or "
    "wood skids: this is a completely NEW DESIGN in a different style, described next. Painterly-realistic RimWorld mod "
    "art, a few bold readable shapes whose silhouette is carried by value and colour contrast, with NO drawn outline or keyline. Real transparent background (alpha "
    "channel), no ground, no cast shadow, no border, no text or legible letters, no logos. Every fitting ends flush inside "
    "the tank silhouette; only the two end ports reach the canvas edges. Square 1024x1024 output. "
)

JOBS = {
    "tank_futuristic_A_white_composite": (
        "STYLE: FUTURISTIC, cyberpunk-elegant, computer-managed. A seamless white ceramic-composite capsule shell with "
        "flush, hairline panel seams and brushed-titanium end rings. A slim recessed pale-cyan LED level bar runs along "
        "the side showing the liquid level; a small lit rectangular screen with a glowing graph readout and two tiny "
        "status lights. Two small flush access ports with sliding covers, one cover slid half open showing a lit "
        "connector socket. Low sleek graphite saddle feet integrated into the shell. Clean, at most faint dust at the "
        "base. Absolutely no analog dials, no rivets, no exposed bolts, no hand wheels, no brass, no exposed pipework."
    ),
    "tank_futuristic_B_graphite_neon": (
        "STYLE: FUTURISTIC, cyberpunk. A matte graphite-black composite capsule with smooth chamfered facets and thin "
        "glowing magenta and cyan accent lines inlaid flush in the shell. A long curved glass display window on the side "
        "shows the fluid level as a glowing cyan column with tick marks; a small holographic-style status screen with "
        "digital bars. Small flush control access panels with slide-open covers, one slid open showing a lit port. "
        "Sleek low hover-style mag-lev feet, sculpted, no legs with bolts. Very clean. Absolutely no analog dials, no "
        "rivets, no exposed bolts, no hand wheels, no brass, no steampunk, no exposed pipework."
    ),
    "tank_futuristic_C_titanium_amber": (
        "STYLE: FUTURISTIC, sleek high-tech. A pale grey and brushed titanium capsule made of a few large smooth "
        "segments with precise flush seams, the end caps smooth domes with recessed glowing amber ring ports. A slim "
        "integrated control strip along the top with small amber and white digital readouts and a row of tiny LED "
        "status lights; an amber LED level ladder on the side. Two small slide-open maintenance hatches, flush. "
        "Streamlined integrated cradle base in dark graphite. Clean. Absolutely no analog dials, no rivets, no exposed "
        "bolts, no hand wheels, no brass, no exposed pipework."
    ),
    "tank_industrial_A_gunmetal_saddle": (
        "STYLE: INDUSTRIAL, working heavy industry and the Star Wars used-future standard: maintained, not abandoned. "
        "Heavy painted steel in dark gunmetal and slate grey, the paint mostly whole. Big bolted flanges at the end "
        "caps, welded seams, a raised bolted manway hatch on top, a short yellow-and-black hazard band as an accent, a "
        "round brass-rimmed ANALOG pressure dial gauge on a short stem and a small red hand-wheel valve on top. Sits on "
        "two heavy cast-steel saddle supports. Honest working wear: scuffed paint on edges, grease and dust at the base, "
        "only a few small rust weeps at a bolt or seam. Not rusty, not a wreck."
    ),
    "tank_industrial_B_olive_panelled": (
        "STYLE: INDUSTRIAL, the Star Wars used-future standard: functional, panelled, bolted, kept running. Olive-drab "
        "and dull sand-grey painted steel, the shell wrapped in raised reinforcing panels and two heavy bolted belly "
        "bands, small greeble boxes and a conduit along the side, a stencilled hazard plate (no legible text), an ANALOG "
        "dial gauge in a brass bezel and a vertical sight-glass level tube on the side. Sits on a welded steel skid "
        "frame. Honest working wear: chipped paint at edges, dust and grime at the base, faint grease streaks, only a "
        "touch of rust at a seam. Maintained, not rusty, not abandoned."
    ),
    "tank_modern_A_green_poly_frame": (
        "STYLE: MODERN, real present-day equipment you would see on a farm or behind a store. A UV-faded dark-green "
        "rotomoulded polyethylene horizontal water tank with moulded ribs, held by two galvanised steel straps on a "
        "galvanised steel frame skid. A brass ball valve and PVC outlet at the bottom of one end, a black screw lid on "
        "top, and a small round ANALOG pressure dial gauge on a brass fitting. Realistic normal wear: dust film, dirt "
        "splash on the lower third, water stains streaking down, sun-faded patches, a faded sticker label (no legible "
        "text), scuffs; the frame has mismatched touch-up paint patches. Realistic materials, not cartoonish, not "
        "plastic-toy, no glossy highlight."
    ),
    "tank_modern_B_painted_steel_saddle": (
        "STYLE: MODERN, real present-day commercial equipment. A painted carbon-steel horizontal water tank on two "
        "steel saddle legs, like an agricultural or fire-water tank. Faded off-white paint with a slightly different "
        "shade of repainted panel and a patch of grey primer touch-up; a bolted round manway on top; a black stencilled "
        "band (no legible text); a small round ANALOG dial gauge and blue-handled ball valves. Realistic normal wear: "
        "smudges, handprints, dust, dirt splash at the base, light water staining, a few scuffs. No heavy rust. "
        "Realistic, not cartoonish, not plastic, no glossy highlight."
    ),
}


def main(argv):
    names = argv or [n for n in JOBS if not (RAW / f"{n}.png").exists()]
    RAW.mkdir(parents=True, exist_ok=True)
    script = image_skills.require(image_skills.CODEX_IMAGE)
    rc_all = 0
    for n in names:
        out = RAW / f"{n}.png"
        cmd = [sys.executable, str(script), "edit", "--out", str(out), "--prompt", COMMON + JOBS[n],
               "--image", str(SCRAPPER), "--timeout", "1200", "--force"]
        print(f"== {n}", flush=True)
        rc = subprocess.call(cmd)
        print(f"   rc={rc} exists={out.exists()}", flush=True)
        rc_all = rc_all or rc
    return rc_all




REDO_PROMPT = (
    "Use $imagegen to edit image 1. Keep this exact tank design, camera, size, layout, colours, readouts and the two end "
    "pipe ports, unchanged. Change only this, from the art judge: {brief} The silhouette is carried by value and colour "
    "contrast and shaded bevels, with NO drawn black outline or keyline around the shape. Real transparent background "
    "(alpha channel), no ground, no shadow, no text. Square 1024x1024 output."
)


def redo(name, brief):
    """One redo of a judged flaw: edit the candidate's own raw drawing, written as raw/<name>_r2.png."""
    script = image_skills.require(image_skills.CODEX_IMAGE)
    out = RAW / f"{name}_r2.png"
    cmd = [sys.executable, str(script), "edit", "--out", str(out), "--prompt", REDO_PROMPT.format(brief=brief),
           "--image", str(RAW / f"{name}.png"), "--timeout", "1200", "--force"]
    print(f"== redo {name}", flush=True)
    return subprocess.call(cmd)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--redo"]:
        sys.exit(redo(sys.argv[2], sys.argv[3]))
    sys.exit(main(sys.argv[1:]))
